#!/usr/bin/env python
# Parchment-proxy - A proxy for fetching web data for Parchment
# Copyright 2008-2010 The Parchment-proxy contributors (see CONTRIBUTORS)
# Released under a BSD-like licence, see LICENCE

# main.py: Main server and response handler

import base64

from django.utils import simplejson
from google.appengine.ext import webapp

import mirror

class ProxyHandler(webapp.RequestHandler):
	'''The parchment-proxy server itself'''
	
	def get(self):
		url = self.request.get('url')
		encode = self.request.get('base64')
		
		try:
			if not url:
				raise Exception('no url provided')
			
			# Get this URL
			url = url.replace(' ', '%20')
			data = mirror.get(url)
			
			# Base64 encode the data if required, and set the content type
			if encode:
				data = base64.b64encode(data)
				self.response.headers['Content-Type'] = 'text/plain'
			else:
				self.response.headers['Content-Type'] = 'application/octet-stream'
			
		except:
			pass
		
		# Set a header for allowing cross domain XHR and send the data
		self.response.headers['Access-Control-Allow-Origin'] = '*'
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
	                                      ('/proxy', ProxyHandler),
	                                      ('/', LegacyHandler),
	                                     ], debug=True)
	webapp.util.run_wsgi_app(application)

if __name__ == '__main__':
  main()
