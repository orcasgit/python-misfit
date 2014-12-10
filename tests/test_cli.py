from docopt import DocoptExit
import unittest

from misfit.cli import main


class TestMisfitCli(unittest.TestCase):
    def test_main(self):
        self.assertRaises(DocoptExit, main)
