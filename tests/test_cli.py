import unittest
import sys

from docopt import DocoptExit
from mock import patch

from misfit.cli import main


class TestMisfitCli(unittest.TestCase):
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
        cli_mock.assert_called_once_with({
            '--client_id': None,
            '--client_secret': None,
            '--config': './misfit.cfg',
            '--detail': False,
            '--end_date': None,
            '--object_id': None,
            '--start_date': None,
            '--user_id': None,
            '--version': True,
            'authorize': False,
            'device': False,
            'goal': False,
            'profile': False,
            'session': False,
            'sleep': False,
            'summary': False
        })
