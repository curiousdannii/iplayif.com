# Parchment-proxy - A proxy for fetching web data for Parchment
# Copyright 2008-2010 The Parchment-proxy contributors (see CONTRIBUTORS)
# Released under a BSD-like licence, see LICENCE

# mirror.py: File download/retrieval functions
# Will eventually form a mirror of the IF Archive

import logging

from google.appengine.api import memcache
from google.appengine.api import urlfetch

# Maximum size of a story file we'll download, in bytes.
MAX_FILE_SIZE = 1024 * 1024

def get(url):
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
		if len(result.content) > MAX_FILE_SIZE:
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
