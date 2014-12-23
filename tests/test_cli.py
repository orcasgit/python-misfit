import json
import os
import unittest
import sys

from docopt import DocoptExit
from httmock import HTTMock
from mock import patch
from nose.tools import eq_
from requests import Request
from six import BytesIO

from misfit.cli import main, MisfitCli

from .mocks import MisfitHttMock


class TestMisfitCli(unittest.TestCase):
    def setUp(self):
        self.default_arguments = {
            '--client_id': None,
            '--client_secret': None,
            '--config': './misfit.cfg',
            '--detail': False,
            '--object_id': None,
            '--start_date': None,
            '--end_date': None,
            '--user_id': None,
            '--version': False,
            'authorize': False,
            'device': False,
            'goal': False,
            'profile': False,
            'session': False,
            'sleep': False,
            'summary': False
        }

    @patch('misfit.cli.MisfitCli')
    @patch('sys.exit')
    def test_main(self, exit_mock, cli_mock):
        # Docopt raises an error when no arguments are passed
        self.assertRaises(DocoptExit, main)
        self.assertEqual(exit_mock.call_count, 0)
        self.assertEqual(cli_mock.call_count, 0)

        # Docopt raises an error (and exits) when the argument is --help
        sys.argv = ['misfit', '--help']
        self.assertRaises(DocoptExit, main)
        self.assertEqual(exit_mock.call_count, 1)
        self.assertEqual(cli_mock.call_count, 0)
        exit_mock.reset_mock()

        # Docopt doesn't raise an error when the argument is --version
        # The MisfitCli object gets created in this case
        sys.argv = ['misfit', '--version']
        main()
        self.assertEqual(exit_mock.call_count, 1)
        version_arguments = self.default_arguments.copy()
        version_arguments['--version'] = True
        cli_mock.assert_called_once_with(version_arguments)

    @patch('webbrowser.open')
    @patch('cherrypy.quickstart')
    @patch('requests_oauthlib.OAuth2Session.new_state')
    @patch('requests_oauthlib.OAuth2Session.fetch_token')
    def test_authorize(self, fetch_token_mock, new_state_mock, quickstart_mock,
                       open_mock):
        """
        Test that the authorize CLI command authorizes the user correctly
        """
        # Mock the state generation function so we know what it returns
        state = 'FAKE_STATE'
        new_state_mock.return_value = state
        stdout_backup = sys.stdout
        sys.stdout = BytesIO()

        # Try without mocking token receipt
        auth_arguments = self.default_arguments.copy()
        auth_arguments.update({
            'authorize': True,
            '--client_id': 'FAKE_CLIENT_ID',
            '--client_secret': 'FAKE_CLIENT_SECRET'
        })
        MisfitCli(auth_arguments)
        auth_url = 'https://api.misfitwearables.com/auth/dialog/authorize?response_type=code&client_id=FAKE_CLIENT_ID&redirect_uri=http%3A%2F%2F127.0.0.1%3A8080%2F&scope=public+birthday+email&state=FAKE_STATE'
        open_mock.assert_called_once_with(auth_url)
        eq_(sys.stdout.getvalue(),
            'ERROR: We were unable to authorize to use the Misfit API.\n')

        # This time, make sure we have a token
        fetch_token_mock.return_value = {'access_token': 'FAKE_TOKEN'}
        quickstart_mock.side_effect = lambda auth: auth.fetch_token(0, state)
        auth_arguments['--config'] = './misfit-test.cfg'
        MisfitCli(auth_arguments)
        with open(auth_arguments['--config']) as config_file:
            eq_(config_file.read(),
                '[misfit]\n'
                'client_id = FAKE_CLIENT_ID\n'
                'client_secret = FAKE_CLIENT_SECRET\n'
                'access_token = FAKE_TOKEN\n\n')
        os.remove(auth_arguments['--config'])

        sys.stdout = stdout_backup


    @patch('pprint.PrettyPrinter.pprint')
    def test_summary(self, pprint_mock):
        """ Check that we can get the summary with the API """
        # TODO: Try summary without detail
        summary_json = MisfitHttMock('summary_detail').json_http
        with HTTMock(summary_json):
            # Fake authorization
            version_arguments = self.default_arguments.copy()
            version_arguments['--version'] = True
            cli = MisfitCli(version_arguments)
            cli.client_id = 'FAKE_ID'
            cli.client_secret = 'FAKE_SECRET'
            cli.access_token = 'FAKE_TOKEN'

            # Get summary detail
            summary_arguments = self.default_arguments.copy()
            summary_arguments.update({
                '--start_date': "2014-10-05",
                '--end_date': "2014-10-08",
                '--detail': True,
                'summary': True
            })
            cli.get_resource(summary_arguments)
            eq_(pprint_mock.call_count, 1)
            pp_summaries = pprint_mock.call_args[0][0]
            eq_(len(pp_summaries), 3)
            eq_(pp_summaries[0]['date'], '2014-10-05')
            eq_(pp_summaries[2]['date'], '2014-10-07')
