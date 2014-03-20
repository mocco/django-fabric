import unittest
import os
import django

from .helpers import TestApp


class TestBaseClass(unittest.TestCase):
    def setUp(self):
        self.log_file_name = 'testlogfile'
        self.fab = TestApp(self.log_file_name)

    def tearDown(self):
        os.remove(self.log_file_name)

    def test_deploy(self):
        expected_filename = 'tests/expected/deploy'
        if django.VERSION >= (1, 7):
            expected_filename += '1.7'
        self.fab.deploy('prod')
        with open(self.log_file_name, 'r') as output:
            with open(expected_filename, 'r') as expected:
                self.assertEqual(output.readlines(), expected.readlines())
