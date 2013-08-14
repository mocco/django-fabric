# -*- coding: utf8 -*-
import os
from fabric.api import local, run, cd
from fabric import colors
from fabric.context_managers import settings
from fabric.contrib.console import confirm
from fabric.contrib import django
from fabric.contrib.files import exists
from fabric.utils import abort


class App(object):
    project_paths = {}
    project_package = None
    test_settings = None

    def __init__(self, project_paths, project_package, test_settings=None):
        self.project_paths = project_paths
        self.project_package = project_package
        self.test_settings = test_settings 
        django.project(project_package)

    def local_management_command(self, command, *args, **kwargs):
        return local("venv/bin/python manage.py %s" % command, *args, **kwargs)

    def run_management_command(self, instance, command):
        code_dir = self.project_paths[instance]
        with cd(code_dir):
            return run("venv/bin/python manage.py %s" % command)

    def test(self, is_deploying=True):
        with settings(warn_only=True):
            print(colors.yellow("Running tests, please wait!"))
            if settings is None:
                command = "test --settings=%s" % \
                    self.test_settings
            else:
                command = "test"
            result = self.local_management_command(command, capture=True)

        if result.failed:
            print(colors.red("Tests failed"))
            if is_deploying:
                if not confirm('Do you really want to deploy?'):
                    abort('')
        else:
            print(colors.green("All tests ok"))

    def check_virtualenv(self, path):
        venv_path = os.path.join(path, "venv")
        if not exists(venv_path):
            if confirm("virtualenv not found. Do you want to create one"):
                print(colors.yellow("Creating virtualenv"))
                with cd(path):
                    run("virtualenv venv")

    def run_server_updates(self, instance):
        code_dir = self.project_paths[instance]
        self.check_virtualenv(code_dir)
        with cd(code_dir):
            run("git fetch")
            run("git reset --hard origin/master")

            run("venv/bin/pip install -r requirements.txt")

            from django.conf import settings
            if 'south' in settings.INSTALLED_APPS:
                self.run_management_command(instance,
                                            "syncdb --noinput --migrate")
            else:
                self.run_management_command(instance, "syncdb --noinput")

            if 'djangobower' in settings.INSTALLED_APPS:
                self.run_management_command(instance, "bower_install")

            self.run_management_command(instance, "collectstatic --noinput")

    def restart_app(self, instance):
        raise NotImplementedError

    def deploy(self, instance):
        self.run_server_updates(instance)
        self.restart_app(instance)

    def deploy_dev(self):
        if confirm("Do you want to run tests before deploying?"):
            self.test(is_deploying=True)

        self.deploy('dev')

    def deploy_prod(self, run_test=True):
        if run_test:
            self.test(is_deploying=True)

        self.deploy('prod')
