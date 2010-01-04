#!/usr/bin/env python
# Parchment-proxy - A proxy for fetching web data for Parchment
# Copyright 2008-2010 The Parchment-proxy contributors (see CONTRIBUTORS)
# Released under a BSD-like licence, see LICENCE

# main.py: Main server and response handler

import wsgiref.handlers
import base64

from django.utils import simplejson
from google.appengine.ext import webapp

import mirror

class MainHandler(webapp.RequestHandler):
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
  application = webapp.WSGIApplication([('/', MainHandler)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
