from fabric.contrib import django

from django_fabric import App
from django_fabric.test_helpers import TestMixin


class TestApp(TestMixin, App):
    project_package = 'package'
    project_paths = {
        'prod': 'path-to-prod'
    }
    restart_command = {
        'prod': 'restart prod'
    }

    def __init__(self, test_log, *args, **kwargs):
        django.settings_module('tests.django_settings')
        self.test_log = test_log

    def notify(self, message):
        with open(self.test_log, 'a') as log_file:
            log_file.write(message + '\n')

    def lock_value(self):
        """
        Override this to make the expected fixtures work for several people
        """
        return ''
