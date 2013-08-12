# -*- coding: utf8 -*-
from fabric.operations import sudo

from django_fabric.base import App


class UwsgiApp(App):
    ini_files = {}

    def __init__(self, ini_files, *args, **kwargs):
        super(UwsgiApp, self).__init__(*args, **kwargs)
        self.ini_files = ini_files

    def restart_app(self, instance):
        sudo("touch %s" % self.ini_files[instance])
