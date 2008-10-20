#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#




import wsgiref.handlers
import base64

import json
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
    self.response.out.write("%s(%s);" % (jsonp, json.write(response)))

def main():
  application = webapp.WSGIApplication([('/', MainHandler)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
