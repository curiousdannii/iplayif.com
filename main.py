#!/usr/bin/env python
# Parchment-proxy - A proxy for fetching web data for Parchment
# Copyright (c) 2008-2009 The Parchment-proxy (see CONTRIBUTORS)
# Released under a BSD-like licence, see LICENCE

import wsgiref.handlers
import base64

from django.utils import simplejson
from google.appengine.ext import webapp
from google.appengine.api import urlfetch

# Maximum size of a story file we'll JSONify, in bytes.
MAX_STORY_SIZE = 1024 * 1024

class MainHandler(webapp.RequestHandler):
  def get(self):
    url = self.request.get("url")
    jsonp = self.request.get("jsonp")
    if not url:
      raise Exception("no url provided")
    try:
      url = url.replace(" ", "%20")
      result = urlfetch.fetch(url)
      if result.status_code == 200:
        if len(result.content) > MAX_STORY_SIZE:
          raise Exception("file too large")
        if result.content.startswith("FORM"):
          # It's an IFF file.
          pass
        elif ord(result.content[0]) < 9:
          # It's a naked Infocom file.
          pass
        else:
          raise Exception("url does not contain a story file")

        response = {"data" : base64.b64encode(result.content)}
      else:
        raise Exception("got status code %d for url %s" % (result.status_code,
                                                           url))
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
