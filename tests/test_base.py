import unittest
import os

from .helpers import TestApp


class TestBaseClass(unittest.TestCase):
    def setUp(self):
        self.log_file_name = 'testlogfile'
        self.fab = TestApp(self.log_file_name)

    def tearDown(self):
        os.remove(self.log_file_name)

    def test_deploy(self):
        self.fab.deploy('prod')
        with open(self.log_file_name, 'r') as output:
            with open('tests/expected/deploy', 'r') as expected:
                self.assertEqual(output.readlines(), expected.readlines())
