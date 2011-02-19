#!/usr/bin/env python
# Parchment-proxy - A proxy for fetching web data for Parchment
# Copyright 2008-2011 The Parchment-proxy contributors (see CONTRIBUTORS)
# Released under a BSD-like licence, see LICENCE

# main.py: Main server and response handler

import base64
import hashlib
import logging
import sys
import traceback

from django.utils import simplejson
from google.appengine.api import memcache
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
		url = self.request.get('url').replace(' ', '%20')
		callback = self.request.get('callback')
		encode = self.request.get('encode')
		ifnonematch = self.request.headers.get('If-None-Match') or ''
		
		if not url:
			# Show the home page
			self.redirect('/')
			return
		
		# Set headers for allowing cross domain XHR and content type
		self.response.headers['Access-Control-Allow-Origin'] = '*'
		self.response.headers['Content-Type'] = 'text/plain; charset=ISO-8859-1'
		
		# Check for a cached hash
		hash = memcache.get(url + '_hash')
		if hash == ifnonematch:
			self.response.set_status(304)
			self.response.headers['ETag'] = hash
			return
		
		# Get this URL
		data = mirror.get(url)
		
		# Generate the hash if needed
		if not hash:
			hash = '"' + hashlib.md5(data).hexdigest() + '"'
			if not memcache.add(url + '_hash', hash, 86400):
				logging.error('Memcache set failed for hash of url ' + url)
		
		# Base64 encode the data if required
		if encode == 'base64':
			data = base64.b64encode(data)
		
		# Handle a callback function
		if callback:
			# Warning, data must be escaped too
			data = callback + '("' + data + '")'
		
		# Sent the data
		self.response.headers['ETag'] = hash
		self.response.out.write(data)
		
	def options(self):
		# Send Access-Control headers for preflighted requests
		
		self.response.headers['Access-Control-Allow-Origin'] = '*'
		self.response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
		self.response.headers['Access-Control-Allow-Headers'] = self.request.headers['Access-Control-Request-Headers']
	
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
				# Show the home page
				self.print_home()
				return

			url = url.replace(" ", "%20")
			data = mirror.get(url)
			response = {'data': base64.b64encode(data)}
		  
		except Exception, e:
			response = {"error" : repr(e)}

		self.response.headers["Content-Type"] = "text/javascript"
		self.response.out.write("%s(%s);" % (jsonp, simplejson.dumps(response)))
	
	def print_home(self):
		# Print a home page
		self.response.headers["Content-Type"] = "text/html"
		self.response.out.write('''
<!doctype html>
<title>Parchment-proxy</title>
<h1>Parchment-proxy</h1>
<p>This is the proxy for Parchment the web IF interpreter.
<p>If you want to read a story with Parchment go to <a href="http://parchment.toolness.com/">http://parchment.toolness.com/</a>
<p>If you want to know more about Parchment-proxy go to <a href="http://github.com/curiousdannii/parchment-proxy">http://github.com/curiousdannii/parchment-proxy</a>
		''')

def main():
	application = webapp.WSGIApplication([
		('/proxy/?', ProxyHandler),
		('/', LegacyHandler),
	], debug=True)
	run_wsgi_app(application)

if __name__ == '__main__':
	main()
