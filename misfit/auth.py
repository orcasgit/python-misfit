from __future__ import absolute_import

import cherrypy
import slumber
import threading
import webbrowser

from .misfit import API_URL


class AuthServer:
    def __init__(self, client_id, client_secret, html=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_url = '%sauth/dialog/authorize' % API_URL
        self.redirect_uri = 'http://127.0.0.1:8080/'
        self.html = html
        if not self.html:
            self.html = """
                <h1>You are now authenticated to the Misfit API!</h1>
                <br/><h3>You can close this window</h3>"""

    def authenticate(self):
        webbrowser.open('%s?client_id=%s&redirect_uri=%s&'
                        'scope=public,birthday,email&response_type=code' %
                        (self.auth_url, self.client_id, self.redirect_uri))

    @cherrypy.expose
    def index(self, code):
        res = slumber.API('%sauth/tokens/' % API_URL).exchange.post({
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        })
        self.access_token = res['access_token']
        threading.Timer(1, lambda: cherrypy.engine.exit()).start()
        return self.html
