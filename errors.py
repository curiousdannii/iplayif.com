# Parchment-proxy - A proxy for fetching web data for Parchment
# Copyright 2008-2010 The Parchment-proxy contributors (see CONTRIBUTORS)
# Released under a BSD-like licence, see LICENCE

# errors.py: Error classes

class ProxyError(Exception):
	'''Basic Parchment-proxy error'''
	
	def __init__(self, message, original=None):
		self.message = message
		self.original = original
	
	def __str__(self):
		# Return only the message
		return self.message
	
	def __repr__(self):
		# Return this error and the original error, if one was provided
		return '''ProxyError('%s'%s)''' % (self.message, self.original and (', ' + repr(self.original)) or '')
