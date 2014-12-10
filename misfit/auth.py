from __future__ import absolute_import

import cherrypy
import os
import threading
import webbrowser

from oauthlib.oauth2 import Client
from oauthlib.oauth2.rfc6749.errors import MismatchingStateError
from requests_oauthlib import OAuth2Session

from .misfit import API_URL


class MisfitAuth:
    def __init__(self, client_id, client_secret,
                 redirect_uri='http://127.0.0.1:8080/', state=None,
                 scope=['public', 'birthday', 'email'], html=None):
        """ Initialize the OAuth2Session """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.html = html if html else """
            <h1>You are now authorized to access the Misfit API!</h1>
            <br/><h3>You can close this window</h3>"""
        # Ignore when the Misfit API doesn't return the actual scope granted,
        # even though this goes against rfc6749:
        #     https://github.com/idan/oauthlib/blob/master/oauthlib/oauth2/rfc6749/parameters.py#L392
        os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = 'true'
        self.token = None
        self.state = state
        self.oauth = OAuth2Session(
            self.client_id, scope=self.scope, redirect_uri=self.redirect_uri,
            state=self.state)

    def authorize_url(self):
        """
        Build the authorization url and save the state. Return the
        authorization url
        """
        url, self.state = self.oauth.authorization_url(
            '%sauth/dialog/authorize' % API_URL)
        return url

    def fetch_token(self, code, state):
        """
        Fetch the token, using the verification code. Also, make sure the state
        received in the response matches the one in the request. Returns the
        access_token.
        """
        if self.state != state:
            raise MismatchingStateError()
        self.token = self.oauth.fetch_token(
            '%sauth/tokens/exchange/' % API_URL, code=code,
            client_secret=self.client_secret)
        return self.token['access_token']

    def browser_authorize(self):
        """
        Open a browser to the authorization url and spool up a CherryPy
        server to accept the response
        """
        webbrowser.open(self.authorize_url())
        cherrypy.quickstart(self)

    @cherrypy.expose
    def index(self, code, state):
        """
        Receive a Misfit response containing a verification code. Use the code
        to fetch the access_token.
        """
        self.fetch_token(code, state)
        threading.Timer(1, lambda: cherrypy.engine.exit()).start()
        return self.html
