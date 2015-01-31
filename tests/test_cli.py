import json
import os
import unittest
import sys

from docopt import DocoptExit
from httmock import HTTMock
from imp import load_source
from mock import patch
from nose.tools import eq_, ok_
from requests import Request
from six import StringIO
from six.moves import configparser

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
            '--help': False,
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
        """ Test the main() function and running cli as a module """

        # Docopt raises an error when no arguments are passed
        self.assertRaises(DocoptExit, main)
        self.assertEqual(exit_mock.call_count, 0)
        self.assertEqual(cli_mock.call_count, 0)

        # Test running: python -m misfit.cli
        cli_path = os.path.abspath(os.path.join('misfit', 'cli.py'))
        self.assertRaises(DocoptExit, load_source, '__main__', cli_path)
        self.assertEqual(exit_mock.call_count, 0)
        self.assertEqual(cli_mock.call_count, 0)

        # Test the --help argument
        sys.argv = ['misfit', '--help']
        main()
        self.assertEqual(exit_mock.call_count, 1)
        version_arguments = self.default_arguments.copy()
        version_arguments['--help'] = True
        cli_mock.assert_called_once_with(version_arguments)

        # Test the --version argument
        cli_mock.reset_mock()
        exit_mock.reset_mock()
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
        sys.stdout = StringIO()

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
        token = {'access_token': 'FAKE_TOKEN'}
        fetch_token_mock.return_value = token
        quickstart_mock.side_effect = lambda auth: auth.fetch_token(0, state)
        auth_arguments['--config'] = './misfit-test.cfg'
        # Remove the cfg file if it exists
        if os.path.isfile(auth_arguments['--config']):
            os.remove(auth_arguments['--config'])
        cli = MisfitCli(auth_arguments)
        eq_(cli.client_id, auth_arguments['--client_id'])
        eq_(cli.client_secret, auth_arguments['--client_secret'])
        os.remove(auth_arguments['--config'])

        sys.stdout = stdout_backup

    def test_write_config(self):
        """
        Test that the write_config method works as expected
        """
        config_arguments = self.default_arguments.copy()
        config_arguments['--config'] = './misfit-test.cfg'
        # Remove the cfg file if it exists
        if os.path.isfile(config_arguments['--config']):
            os.remove(config_arguments['--config'])
        # Create an empty MisfitCli
        cli = MisfitCli(config_arguments)
        ok_(cli.client_id is None)
        ok_(cli.client_secret is None)
        ok_(cli.access_token is None)

        # Manually create the config file
        test_args = ['FAKE_ID', 'FAKE_SECRET', 'FAKE_TOKEN']
        cli.client_id = test_args[0]
        cli.client_secret = test_args[1]
        # Write the config file
        cli.write_config(test_args[2])
        config = configparser.ConfigParser()
        with open(config_arguments['--config']) as cfg:
            config.readfp(cfg)
        ok_(config.has_section('misfit'))
        eq_(config.get('misfit', 'client_id'), test_args[0])
        eq_(config.get('misfit', 'client_secret'), test_args[1])
        eq_(config.get('misfit', 'access_token'), test_args[2])
        # Remove the test config we created
        os.remove(config_arguments['--config'])

    def test_read_config(self):
        """
        Test that the read_config method pulls values from config
        """
        config_arguments = self.default_arguments.copy()
        config_arguments['--config'] = './misfit-test.cfg'
        # Remove the cfg file if it exists
        if os.path.isfile(config_arguments['--config']):
            os.remove(config_arguments['--config'])
        # Create an empty MisfitCli
        cli = MisfitCli(config_arguments)
        ok_(cli.client_id is None)
        ok_(cli.client_secret is None)
        ok_(cli.access_token is None)
        # Manually create the config file
        lines = ['[misfit]', 'access_token = FAKE_TOKEN',
                 'client_secret = FAKE_SECRET', 'client_id = FAKE_ID']
        with open(config_arguments['--config'], 'w') as cfg:
            cfg.write('\n'.join(lines))
        # Readi it in
        cli.read_config()
        # Check that the values match the ones we entered
        eq_(cli.access_token, lines[1].split(' = ')[1])
        eq_(cli.client_secret, lines[2].split(' = ')[1])
        eq_(cli.client_id, lines[3].split(' = ')[1])
        # Remove the test config we created
        os.remove(config_arguments['--config'])



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
