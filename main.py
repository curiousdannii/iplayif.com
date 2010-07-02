#!/usr/bin/env python
# Parchment-proxy - A proxy for fetching web data for Parchment
# Copyright 2008-2010 The Parchment-proxy contributors (see CONTRIBUTORS)
# Released under a BSD-like licence, see LICENCE

# main.py: Main server and response handler

import base64
import logging
import sys
import traceback

from django.utils import simplejson
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from errors import *
import mirror

class ProxyHandler(webapp.RequestHandler):
	'''The parchment-proxy server itself'''
	
	def initialize(self, request, response):
		webapp.RequestHandler.initialize(self, request, response)
		
		# Add our code var
		self.code = 200
	
	def get(self):
		# Parameters
		url = self.request.get('url')
		callback = self.request.get('callback')
		encode = self.request.get('encode')
		
		if not url:
			self.code = 400
			raise ProxyError('no url provided')
		
		# Get this URL
		url = url.replace(' ', '%20')
		data = mirror.get(url)
		
		# Base64 encode the data if required
		if encode == 'base64':
			data = base64.b64encode(data)
		
		# Handle a callback function
		if callback:
			# Warning, data must be escaped too
			data = callback + '("' + data + '")'
		
		# Set a header for allowing cross domain XHR and send the data
		self.response.headers['Access-Control-Allow-Origin'] = '*'
		self.response.headers['Content-Type'] = 'text/plain; charset=ISO-8859-1'
		self.response.out.write(data)
		
	def options(self):
		# Send Access-Control headers for preflighted requests
		
		self.response.headers['Access-Control-Allow-Origin'] = '*'
		self.response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
		# Why must Prototype add these?
		self.response.headers['Access-Control-Allow-Headers'] = 'x-prototype-version, x-requested-with'
	
	def handle_exception(self, e, debug):
		# Handle exceptions
		self.response.clear()
		
		# Set the HTTP status code
		if self.code == 200:
			self.code = 500
		self.response.set_status(self.code)
		
		# Write out the error message
		self.response.out.write(e)
		
		# Log this error too
		logging.error(repr(e))
		logging.error(''.join(traceback.format_tb(sys.exc_info()[2])))
		

class LegacyHandler(webapp.RequestHandler):
  '''The original jsonp proxy server'''
  def get(self):
    url = self.request.get("url")
    jsonp = self.request.get("jsonp")

    try:
      if not url:
        raise Exception("no url provided")
        
      url = url.replace(" ", "%20")
      data = mirror.get(url)
      response = {'data': base64.b64encode(data)}
      
    except Exception, e:
      response = {"error" : repr(e)}
    
    self.response.headers["Content-Type"] = "text/javascript"
    self.response.out.write("%s(%s);" % (jsonp, simplejson.dumps(response)))

def main():
	application = webapp.WSGIApplication([
	                                      ('/proxy/?', ProxyHandler),
	                                      ('/', LegacyHandler),
	                                     ], debug=True)
	run_wsgi_app(application)

if __name__ == '__main__':
  main()
