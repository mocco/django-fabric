import unittest
import os
import django
from django.test.utils import override_settings

from .helpers import TestApp


class TestBaseClass(unittest.TestCase):
    def setUp(self):
        self.log_file_name = 'testlogfile'
        self.fab = TestApp(self.log_file_name)

    def tearDown(self):
        os.remove(self.log_file_name)

    def assertOutput(self, expected_filename):
        if django.VERSION >= (1, 7):
            expected_filename += '1.7'

        with open(self.log_file_name, 'r') as output:
            with open(expected_filename, 'r') as expected:
                self.assertEqual(output.readlines(), expected.readlines())

    def test_deploy(self):
        self.fab.deploy('prod')
        self.assertOutput('tests/expected/deploy')

    @override_settings(STATIC_ROOT=None)
    def test_empty_static_root(self):
        self.fab.deploy('prod')
        self.assertOutput('tests/expected/no_static_root')
