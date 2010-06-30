# Parchment-proxy - A proxy for fetching web data for Parchment
# Copyright 2008-2010 The Parchment-proxy contributors (see CONTRIBUTORS)
# Released under a BSD-like licence, see LICENCE

# mirror.py: File download/retrieval functions
# Will eventually form a mirror of the IF Archive

import logging

from google.appengine.api import memcache
from google.appengine.api import urlfetch

# Maximum size of a story file we'll download, in bytes.
MAX_FILE_SIZE = 1024 * 1000

def get(url):
	'''Get a file, using memcache if possible'''
	
	# Check memcache for this url
	data = memcache.get(url)
	if data is not None:
		return data
	
	# Missed! Attempt to download it now
	else:
		result = urlfetch.fetch(url, allow_truncated=True)
		
		# HTTP Status code
		if result.status_code != 200:
			raise Exception('got status code %d for url %s' % (result.status_code, url))
		
		# Check for oversized requests
		data = result.content
		if result.content_was_truncated:
			data += fetch_big(url, int(result.headers['Content-Length']), len(data) - 1)
		
		# Check it's a valid glulx/zcode story file
		if data.startswith('FORM') or data.startswith('Glul') or ord(data[0]) < 9:
			pass
		else:
			raise Exception('url does not contain a story file')
		
		# All good... cache it and return (don't cache big files for now)
		if len(data) <= MAX_FILE_SIZE:
			if not memcache.add(url, data, 3600):
				logging.error('Memcache set failed for url ' + url)
		
		return data

def fetch_big(url, size, last):
	'''Get the rest of a big file'''
	# Consider changing later to request the parts async
		
	# Range for the next request
	minrange = last + 1
	maxrange = (last + MAX_FILE_SIZE)
	# Can we trust the Content-Length header? What if it's gzipped?
	if maxrange >= size:
		maxrange = size - 1
	headers = {'Range': 'bytes=%d-%d' % (minrange, maxrange)}
	
	# Make each URL unique, otherwise the cache will only return the first part (What about the headers?!?)
	tempurl = url + '#' + str(minrange)
	
	# Request the next part of the file
	request = urlfetch.fetch(tempurl, headers=headers, allow_truncated=True)
	data = request.content
	
	# If that's not all, recursively fetch the next part
	if maxrange < size - 1:
		data += fetch_big(url, size, maxrange)
	
	return data
