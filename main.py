#!/usr/bin/env python
# Parchment-proxy - A proxy for fetching web data for Parchment
# Copyright (c) 2008-2009 The Parchment-proxy (see CONTRIBUTORS)
# Released under a BSD-like licence, see LICENCE

import wsgiref.handlers
import base64
import logging

from django.utils import simplejson
from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.api import urlfetch

# Maximum size of a story file we'll JSONify, in bytes.
MAX_STORY_SIZE = 1024 * 1024

class MainHandler(webapp.RequestHandler):
  def get(self):
    url = self.request.get("url")
    jsonp = self.request.get("jsonp")

    try:
      if not url:
        raise Exception("no url provided")
        
      url = url.replace(" ", "%20")
      data = get_file(url)
      response = {'data': base64.b64encode(data)}
      
    except Exception, e:
      response = {"error" : repr(e)}
    
    self.response.headers["Content-Type"] = "text/javascript"
    self.response.out.write("%s(%s);" % (jsonp, simplejson.dumps(response)))

def get_file(url):
	'''Get a file, using memcache if possible'''
	
	# Check memcache for this url
	data = memcache.get(url)
	if data is not None:
		return data
	
	# Missed! Attempt to download it now
	else:
		result = urlfetch.fetch(url)
		data = result.content
		
		# HTTP Status code
		if result.status_code != 200:
			raise Exception('got status code %d for url %s' % (result.status_code, url))
		
		# Check if it's too big (but won't urlfetch complain first?)
		if len(result.content) > MAX_STORY_SIZE:
			raise Exception('file too large')
		
		# Check it's a valid zcode story file
		if data.startswith('FORM') or ord(data[0]) < 9:
			pass
		else:
			raise Exception('url does not contain a zcode story file')
		
		# All good... cache it and return
		if not memcache.add(url, data, 3600):
			logging.error('Memcache set failed for url ' + url)
		
		return data

def main():
  application = webapp.WSGIApplication([('/', MainHandler)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
