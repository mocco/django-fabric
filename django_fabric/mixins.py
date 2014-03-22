# -*- coding: utf-8 -*-
import os

from fabric.api import cd
from fabric import colors
from fabric.contrib.console import confirm


class VirtualenvMixin(object):
    """
    A mixin that will check for a virtual environment at <project_path>/venv
    before deployment.
    """

    def run_server_updates(self, instance):
        code_dir = self.project_paths[instance]
        self.check_virtualenv(code_dir)
        super(VirtualenvMixin, self).run_server_updates(instance)

    def check_virtualenv(self, path):
        venv_path = os.path.join(path, 'venv')
        if not self.exists(venv_path):
            if confirm('virtualenv not found. Do you want to create one'):
                print(colors.yellow('Creating virtualenv'))
                with cd(path):
                    self.run('virtualenv venv')
