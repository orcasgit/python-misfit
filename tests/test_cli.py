import json
import unittest
import sys

from docopt import DocoptExit
from httmock import HTTMock
from mock import patch
from nose.tools import eq_
from requests import Request

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
