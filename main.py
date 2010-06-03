#!/usr/bin/env python
# Parchment-proxy - A proxy for fetching web data for Parchment
# Copyright 2008-2010 The Parchment-proxy contributors (see CONTRIBUTORS)
# Released under a BSD-like licence, see LICENCE

# main.py: Main server and response handler

import base64

from django.utils import simplejson
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import mirror

class ProxyHandler(webapp.RequestHandler):
	'''The parchment-proxy server itself'''
	
	def get(self):
		code = 200
		data = ''
		
		# Parameters
		url = self.request.get('url')
		callback = self.request.get('callback')
		encode = self.request.get('encode')
		
		try:
			if not url:
				code = 400
				raise Exception('no url provided')
			
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
			
		except Exception, e:
			# Set the HTTP status code
			if code == 200:
				code = 500
			self.response.set_status(code)
			
			# Write out the error message
			data = e
		
		# Set a header for allowing cross domain XHR and send the data
		self.response.headers['Access-Control-Allow-Origin'] = '*'
		self.response.headers['Content-Type'] = 'text/plain; charset=ISO-8859-1'
		self.response.out.write(data)

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
