Parchment IF Proxy
==================

Parchment-proxy is a simple Google App Engine server for proxying Interactive Fiction files for web interpreters like Parchment.

You may install your own, or use ours at <https://proxy.iplayif.com/>

Parchment-proxy is MIT licensed.

How to use
----------

Examples:

-	<https://proxy.iplayif.com/proxy/?url=http://mirror.ifarchive.org/if-archive/games/springthing/2007/Fate.z8>
-	<https://proxy.iplayif.com/proxy/?callback=processBase64Zcode&encode=base64&url=http://mirror.ifarchive.org/if-archive/games/springthing/2007/Fate.z8>

Access the proxy by the `/proxy/` URL. `/` still works, but has a depreciated API.

Parameters:

-	`url`: required, the URL of the story to access
   
-	`encode`: set `encode=base64` to base64 encode the story file
   
-	`callback`: a callback function for JSONP
	
	If you're using jQuery and you set the `dataType` to `'jsonp'`, it will automatically create the callback function and add this parameter for you. Other libraries may do the same. However, as the parameter jQuery choses for you will be unique, the results won't be cached, and so it's recommended that you manually specify the callback function. See <http://api.jquery.com/jQuery.ajax/> for more information.
	
	If you use a callback, also set `encode=base64`.

Parchment-proxy will send the data with a `Content-Type` header of `'text/plain; charset=ISO-8859-1'` and an `Access-Control-Allow-Origin` header of `'*'` for cross-site AJAX requests. Similarly, it will handle an `OPTIONS` request if you need to preflight your cross-site requests.

Parchment-proxy uses `ETag` and `If-None-Match` headers to manage caching. In most situations you shouldn't need to manually use the headers.