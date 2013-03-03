#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '0.1.0'
__author__ = 'Gong Zibin (gzb1985@gmail.com)'

'''
Python client SDK for Pocket V3 API using OAuth 2.
'''

try:
    import json
except ImportError:
    import simplejson as json

import requests


class APIError(StandardError):
    def __init__(self, status_code, x_error_code, x_error, request):
        self.status_code = status_code
        self.x_error_code = x_error_code
        self.x_error = x_error
        self.request = request
        StandardError.__init__(self, x_error)

    def __str__(self):
        '''
        like:
        APIError: HTTP Status:403, X-Error-Code:158, X-Error:"User rejected code.", request: Get access token
        '''
        return 'APIError: HTTP Status:%d, X-Error-Code:%s, X-Error:"%s", request: %s' \
            % (self.status_code, self.x_error_code, self.x_error, self.request)

POCKET_URLs = {
    'request_token': 'https://getpocket.com/v3/oauth/request',
    'authorize_token': 'https://getpocket.com/auth/authorize?request_token=%(request_token)s&redirect_uri=%(redirect_uri)s',
    'access_token': 'https://getpocket.com/v3/oauth/authorize'
}
POCKET_HEADERS = {
    'Content-Type': 'application/json; charset=UTF-8',
    'X-Accept': 'application/json'
}

class Pocket(object):
    '''
    API client using synchronized invocation.
    '''
    def __init__(self, consumer_key, redirect_uri=None):
        self.consumer_key = str(consumer_key)
        self.redirect_uri = redirect_uri
        self.access_token = None

    def _post(self, method_url, **kw):
        '''
        make a http post.
        '''
        resp = requests.post(method_url, data=json.dumps(kw), headers=POCKET_HEADERS)
        if resp.status_code != 200:
            raise APIError(resp.status_code, resp.headers['X-Error-Code'], resp.headers['X-Error'], 'Get access token')
        return json.loads(resp.content)

    def _authenticated_post(self, method_url, **kw):
        '''
        make a authenticated http post.
        '''
        kw['consumer_key'] = self.consumer_key
        kw['access_token'] = self.access_token
        return self._post(method_url,**kw)

    def get_request_token(self):
        '''
        return request token (the "code" in the response). 
        This request token must be stored for use in request access token step. 
        For web applications, it should be associated with the user's session or other persistent state.
        '''
        resp = self._post(POCKET_URLs['request_token'], consumer_key=self.consumer_key, 
            redirect_uri='is-this-even-used', state='foo')
        return resp['code']

    def get_authorize_url(self, code):
        '''
        return the authorization url that the user should be redirected to.
        '''
        if not self.redirect_uri:
            raise APIError(400, '140', 'Missing redirect url.', 'Get access token')
        url = POCKET_URLs['authorize_token'] % {
            'request_token': code,
            'redirect_uri': self.redirect_uri
        }
        return url

    def get_access_token(self, code):
        '''
        return access token as a dict: {"access_token":"5678defg-5678-defg-5678-defg56","username":"pocketuser"}.
        '''
        resp = self._post(POCKET_URLs['access_token'], consumer_key=self.consumer_key, code=code)
        self.access_token = resp['access_token']
        return resp

    def set_access_token(self, access_token):
        '''
        set the access token if already authenticated.
        '''
        self.access_token = str(access_token)

    def add(self, **kw):
        '''
        add a single item to Pocket list.
        '''
        return self._authenticated_post('https://getpocket.com/v3/add', **kw)

    def get(self, **kw):
        '''
        retrieve item(s) from Pocket list.
        '''
        return self._authenticated_post('https://getpocket.com/v3/get', **kw)

    def modify(self, **kw):
        '''
        '''
        pass


