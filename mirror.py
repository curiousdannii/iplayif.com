# Parchment-proxy - A proxy for fetching web data for Parchment
# Copyright 2008-2012 The Parchment-proxy contributors (see CONTRIBUTORS)
# Released under a BSD-like licence, see LICENCE

# mirror.py: File download/retrieval functions
# Will eventually form a mirror of the IF Archive

import logging

from google.appengine.api import memcache
from google.appengine.api import urlfetch

from errors import *

# Maximum size of a story file we'll download, in bytes.
MAX_FILE_SIZE = 1000000

def get(url):
	'''Get a file, using memcache if possible'''

	# Check memcache for this url
	data = memcache.get(url)
	if data is not None:
		return data

	# Missed! Attempt to download it now
	else:
		try:
			result = urlfetch.fetch(url, deadline=60)
		except urlfetch.DownloadError, e:
			raise ProxyError('could not contact server, or server too slow', e)
		except urlfetch.ResponseTooLargeError, e:
			raise ProxyError('file is too big', e)

		data = result.content

		# HTTP Status code
		if result.status_code != 200:
			raise ProxyError('got status code %d for url %s' % (result.status_code, url))

		# Check it's a valid glulx/zcode story file, before downloading the rest
		#if data.startswith('FORM') or data.startswith('Glul') or ord(data[0]) < 9:
		#	pass
		#else:
		#	raise ProxyError('url does not contain a story file')

		# All good... cache it and return (don't cache big files for now)
		if len(data) <= MAX_FILE_SIZE:
			if not memcache.add(url, data, 3600):
				logging.error('Memcache set failed for url ' + url)

		return data
