# Pocket.py
A python wrapper for [Pocket API v3](http://getpocket.com/developer/docs/overview) 

===

## OAuth 2

	import sys, json
	from flask import Flask
	from flask import url_for,redirect, session
	from pocket import Pocket, APIError

	app = Flask(__name__)
	app.debug = True
	app.secret_key = 'your secret key'

	POCKET_CONSUMER_KEY = 'pocket api key'
	WEB_APP_BASE_URL = 'your web app base url'

	@app.route('/auth')
	def auth():
		pocket = Pocket(POCKET_CONSUMER_KEY, WEB_APP_BASE_URL + url_for('auth_callback'))
		try:
			code = pocket.get_request_token()
			url = pocket.get_authorize_url(code)
		except APIError as apie:
			return str(apie)
		session.pop('code', None)
		session['code'] = code # store request token (code) for getting access token
		return redirect(url)

	@app.route('/auth_callback')
	def auth_callback():
		pocket = Pocket(POCKET_CONSUMER_KEY)
		code = session['code']
		try:
			resp = pocket.get_access_token(code)
			session.pop('access_token', None)
			session['access_token'] = resp['access_token'] #store access token in session for api call
		except APIError as apie:
			return str(apie)

## Api

First, 

	pocket = Pocket(POCKET_CONSUMER_KEY)
	pocket.set_access_token(session['access_token'])

For example, retrieving first five favorited and archived items from Pocket list.
	
	items = pocket.get(count=5, favorite=1, state='archive')
	return json.dumps(items)
	
adding a url item to Pocket list.

	item = pocket.add(url='http://getpocket.com/developer/docs/authentication')
	return json.dumps(item)

## requirements

[requests](https://github.com/kennethreitz/requests)
