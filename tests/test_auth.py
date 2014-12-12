from __future__ import unicode_literals

import cherrypy
import json
import os
import unittest

from mock import patch
from oauthlib.oauth2.rfc6749.errors import MismatchingStateError
from requests_oauthlib import OAuth2Session

from misfit.auth import MisfitAuth
from misfit.misfit import API_URL


class TestMisfitAuth(unittest.TestCase):
    def setUp(self):
        self.client_id = 'FAKE_CLIENT_ID'
        self.client_secret = 'FAKE_CLIENT_SECRET'
        self.state = 'FAKE_STATE'
        self.code = 'FAKE_CODE'
        self.access_token = 'FAKE_ACCESS_TOKEN'
        self.token = {
            'access_token': self.access_token,
            'token_type': 'Bearer'
        }
        self.kwargs = {
            'redirect_uri': 'http://www.example.com/misfit-auth/',
            'scope': ['public'],
            'success_html': 'My customized success HTML',
            'failure_html': 'My customized failure HTML',
            'state': self.state
        }
        cherrypy.engine.state = cherrypy.engine.states.STOPPED

    def test_init(self):
        """ Test all the ways we can create a MisfitAuth object """
        # Only mandatory args
        auth = MisfitAuth(self.client_id, self.client_secret)
        self._verify_member_vars(auth)

        # Override args
        auth = MisfitAuth(self.client_id, self.client_secret, **self.kwargs)
        self._verify_member_vars(auth, **self.kwargs)
        # Check that a new state doesn't get generated to override the value
        # passed
        auth.authorize_url()
        self.assertEqual(auth.state, self.state)

    @patch('requests_oauthlib.OAuth2Session.new_state')
    def test_authorize_url(self, new_state_mock):
        """
        Test that the authorize_url method sets the state and returns the right
        url
        """
        auth = MisfitAuth(self.client_id, self.client_secret, **self.kwargs)
        # Mock the state generation function so we know what it returns
        new_state_mock.return_value = self.state
        self.assertEqual(auth.authorize_url(), API_URL + (
            r'auth/dialog/authorize?response_type=code&'
            'client_id=FAKE_CLIENT_ID&'
            'redirect_uri=http%3A%2F%2Fwww.example.com%2Fmisfit-auth%2F&'
            'scope=public&state=FAKE_STATE'))
        self.assertEqual(auth.state, self.state)

    @patch('requests_oauthlib.OAuth2Session.new_state')
    @patch('requests_oauthlib.OAuth2Session.fetch_token')
    def test_fetch_token(self, fetch_token_mock, new_state_mock):
        """
        Test that the fetch_token method gets the access_token and checks for
        mismatching state
        """
        auth = MisfitAuth(self.client_id, self.client_secret, **self.kwargs)
        # Mock the fetch_token function so we don't actually hit the API
        fetch_token_mock.return_value = self.token
        # Mock the state generation function so we know what it returns
        new_state_mock.return_value = self.state
        auth.authorize_url()
        self.assertEqual(auth.fetch_token(self.code, self.state),
                         self.access_token)
        self.assertEqual(auth.token, self.token)
        fetch_token_mock.assert_called_once_with(
            '%sauth/tokens/exchange/' % API_URL,
            client_secret='FAKE_CLIENT_SECRET', code=self.code)

        # Try with a bad state
        self.assertRaises(MismatchingStateError,
                          auth.fetch_token, self.code, 'BAD_STATE')

    @patch('webbrowser.open')
    @patch('cherrypy.quickstart')
    @patch('requests_oauthlib.OAuth2Session.new_state')
    def test_browser_authorize(self, new_state_mock, quickstart_mock,
                               open_mock):
        """
        Test that the browser_authorize method opens a browser to the right
        URL and starts the CherryPy server to listen for a redirect
        """
        # Mock the state generation function so we know what it returns
        new_state_mock.return_value = self.state
        auth = MisfitAuth(self.client_id, self.client_secret, **self.kwargs)
        auth.browser_authorize()
        open_mock.assert_called_once_with(auth.authorize_url())
        quickstart_mock.assert_called_once_with(auth)

    @patch('threading.Timer')
    @patch('requests_oauthlib.OAuth2Session.fetch_token')
    @patch('requests_oauthlib.OAuth2Session.new_state')
    def test_index(self, new_state_mock, fetch_token_mock, timer_mock):
        """
        Test that the index CherryPy endpoint fetches the access_token and then
        shuts down the CherryPy server
        """
        auth = MisfitAuth(self.client_id, self.client_secret, **self.kwargs)
        # Mock the fetch_token function so we don't actually hit the API
        fetch_token_mock.return_value = self.token
        # Mock the state generation function so we know what it returns
        new_state_mock.return_value = self.state
        auth.authorize_url()
        cherrypy.engine.state = cherrypy.engine.states.STARTED
        self.assertEqual(auth.index(self.state, code=self.code),
                         self.kwargs['success_html'])
        self.assertEqual(auth.token, self.token)
        fetch_token_mock.assert_called_once_with(
            '%sauth/tokens/exchange/' % API_URL,
            client_secret='FAKE_CLIENT_SECRET', code=self.code)
        timer_mock().start.assert_called_once_with()

        # Try with an error
        timer_mock.reset_mock()
        fetch_token_mock.reset_mock()
        auth = MisfitAuth(self.client_id, self.client_secret, **self.kwargs)
        auth.authorize_url()
        self.assertEqual(auth.index(self.state, error='access_denied'),
                         self.kwargs['failure_html'])
        assert auth.token is None
        self.assertEqual(fetch_token_mock.call_count, 0)
        timer_mock().start.assert_called_once_with()

        # Also try with an invalid state
        timer_mock.reset_mock()
        fetch_token_mock.reset_mock()
        auth = MisfitAuth(self.client_id, self.client_secret, **self.kwargs)
        auth.authorize_url()
        self.assertRaises(MismatchingStateError,
                          auth.index, 'BAD_STATE', code=self.code)
        assert auth.token is None
        self.assertEqual(fetch_token_mock.call_count, 0)
        timer_mock().start.assert_called_once_with()

    @patch('threading.Timer')
    def test_shutdown_cherrypy(self, timer_mock):
        """
        Test that the _shutdown_cherrypy method shuts down the cherrypy server
        if it's running.
        """
        # No shutdown if the server isn't running
        auth = MisfitAuth(self.client_id, self.client_secret, **self.kwargs)
        auth._shutdown_cherrypy()
        self.assertEqual(timer_mock().start.call_count, 0)

        # Make sure the server shuts down, if it is running
        auth = MisfitAuth(self.client_id, self.client_secret, **self.kwargs)
        cherrypy.engine.state = cherrypy.engine.states.STARTED
        auth._shutdown_cherrypy()
        timer_mock().start.assert_called_once_with()

    def _verify_member_vars(
            self, auth, redirect_uri='http://127.0.0.1:8080/',
            scope=['public', 'birthday', 'email'], success_html="""
            <h1>You are now authorized to access the Misfit API!</h1>
            <br/><h3>You can close this window</h3>""", failure_html="""
            <h1>ERROR: We were unable to authorize to use the Misfit API.</h1>
            <br/><h3>You can close this window</h3>""", state=None):
        """
        Verify all the MisfitAuth member variables are as they should be
        """
        self.assertEqual(auth.client_id, self.client_id)
        self.assertEqual(auth.client_secret, self.client_secret)
        self.assertEqual(auth.redirect_uri, redirect_uri)
        self.assertEqual(auth.scope, scope)
        self.assertEqual(auth.success_html, success_html)
        self.assertEqual(auth.failure_html, failure_html)
        self.assertEqual(os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'], 'true')
        self.assertEqual(auth.state, state)
        self.assertTrue(auth.token is None)
        self.assertEqual(type(auth.oauth), OAuth2Session)
