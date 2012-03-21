/*

Parchment-proxy - A proxy for fetching web data for Parchment
=============================================================

Copyright (c) 2008-2012 The Parchment-proxy contributors (see CONTRIBUTORS)
BSD licenced
http://code.google.com/p/parchment

*/

/*

TODO:
	ETag
	Error handling

*/

var connect = require( 'connect' ),
express = require( 'express' ),
request = require( 'request' );

var app = express.createServer( express.logger() );
app.use( connect.compress() );

// Our informative front page
app.get( '/' , function( req, res )
{
	res.send( '<!doctype html><title>Parchment-proxy</title><h1>Parchment-proxy</h1><p>This is the proxy for Parchment the web IF interpreter.<p>If you want to read a story with Parchment go to <a href="http://iplayif.com/">http://iplayif.com/</a><p>If you want to know more about Parchment-proxy go to <a href="https://github.com/curiousdannii/parchment-proxy">https://github.com/curiousdannii/parchment-proxy</a>' );
});

// The main proxy itself
app.get( '/proxy/?', function( req, res )
{
	// Request parameters
	var url = req.query.url,
	callback = req.query.callback,
	encode = req.query.encode;
	
	// Show the home page
	if ( !url )
	{
		return res.redirect( '/' );
	}
	
	// Get this URL
	request( {
		uri: url,
		encoding: null
	}, function( error, response, body )
	{
		// Set headers for allowing cross domain XHR and content type
		res.header( 'Access-Control-Allow-Origin', '*' );
		res.charset = 'ISO-8859-1';
		res.header( 'Content-Type', 'text/plain' );
	
		// Base64 encode the data if required
		var data = body.toString( callback || encode == 'base64' ? 'base64' : 'binary' );
		
		// Handle a callback function
		if ( callback )
		{
			data = callback + '("' + data + '")';
			res.header( 'Content-Type', 'text/javascript' );
		}
		
		// Sent the data
		res.send( data );
	});
});

// Send Access-Control headers for preflighted requests
app.options( '/proxy/?', function( req, res )
{
	res.header( 'Access-Control-Allow-Origin', '*' );
	res.header( 'Access-Control-Allow-Methods', 'GET, OPTIONS' );
	res.header( 'Access-Control-Allow-Headers', req.header( 'Access-Control-Request-Headers', '' ) );
	res.end();
});

// Start us up
var port = process.env.PORT || 3000;
app.listen( port, function()
{
  console.log( 'Listening on ' + port );
});