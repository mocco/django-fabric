# -*- coding: utf-8 -*-
import time

from fabric.api import local, run, cd
from fabric import colors
from fabric.context_managers import settings
from fabric.contrib.console import confirm
from fabric.contrib import django
from fabric.utils import abort
from fabric.operations import get


class App(object):
    project_paths = {}
    project_package = None
    test_settings = None
    strict = False
    restart_command = None
    loaddata_command = None
    dumpdata_command = None
    local_tables_to_flush = []
    requirements = {
        'dev': 'requirements.txt',
        'prod': 'requirements.txt',
    }

    def __init__(self, project_paths, project_package, test_settings=None,
                 strict=False, restart_command=None,
                 loaddata_command='loaddata', dumpdata_command='dumpdata',
                 requirements=None, local_tables_to_flush=[]):
        self.project_paths = project_paths
        self.project_package = project_package
        self.test_settings = test_settings
        self.strict = strict
        self.restart_command = restart_command
        self.loaddata_command = loaddata_command
        self.dumpdata_command = dumpdata_command
        self.local_tables_to_flush = local_tables_to_flush
        self.requirements = requirements or self.requirements
        django.project(project_package)

    def run(self, command):
        return run(command)

    def local_management_command(self, command, *args, **kwargs):
        return local("venv/bin/python manage.py %s" % command, *args, **kwargs)

    def run_management_command(self, instance, command):
        if instance == 'local':
            return self.local_management_command(command)

        code_dir = self.project_paths[instance]
        with cd(code_dir):
            return self.run("venv/bin/python manage.py %s" % command)

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
                if self.strict:
                    abort('')
                if not confirm('Do you really want to deploy?'):
                    abort('')
        else:
            print(colors.green("All tests ok"))

    def syncdb(self, instance):
        from django.conf import settings

        if 'south' in settings.INSTALLED_APPS:
            self.run_management_command(instance,
                                        "syncdb --noinput --migrate")
        else:
            self.run_management_command(instance, "syncdb --noinput")

    def run_server_updates(self, instance):
        code_dir = self.project_paths[instance]
        with cd(code_dir):
            self.run("git fetch")
            self.run("git reset --hard origin/master")

            self.run("venv/bin/pip install -r%s" % self.requirements[instance])

            self.syncdb(instance)

            from django.conf import settings

            if 'djangobower' in settings.INSTALLED_APPS:
                self.run_management_command(instance, "bower_install")

            if 'django.contrib.staticfiles' in settings.INSTALLED_APPS:
                self.run_management_command(instance,
                                            "collectstatic --noinput")

    def restart_app(self, instance):
        if self.restart_command is None:
            # If restart command is not used this method should have been
            # overrided
            raise NotImplementedError
        else:
            self.run(self.restart_command)

    def deploy(self, instance=None, run_tests=True):
        if instance is None:
            abort(colors.red("You need to provide instance on the form "
                             "deploy:instance"))
        if bool(run_tests) or \
           confirm("Do you want to run tests before deploying?"):
                self.test(is_deploying=True)

        self.run_server_updates(instance)
        self.restart_app(instance)

    def translate(self):
        self.local_management_command('makemessages --all')
        if confirm('Compile messages?'):
            self.local_management_command('compilemessages')

    def clone_data(self, instance):
        if not confirm("All local data will be replaced with "
                       "data from %s, OK?" % instance):
            abort()

        dump_file = "%s.json" % str(int(time.time()))

        # Ignore errors on these next steps, so that we are sure we clean up
        # no matter what
        with settings(warn_only=True) and cd(self.project_paths[instance]):
            # Dump the database to a file...
            self.run_management_command(
                instance,
                '%s --all > %s' % (self.dumpdata_command, dump_file)
            )

            # The download that file, all uploaded files and rm the dump file
            get("%s%s" % (self.project_paths[instance], dump_file), dump_file)
            self.run('rm %s' % dump_file)

            self.syncdb('local')
            self.local_management_command('flush --noinput')

            from django.db import connection, transaction

            cursor = connection.cursor()
            cursor.execute("DELETE FROM django_content_type;")

            for table in self.local_tables_to_flush:
                cursor.execute("DELETE FROM %s;" % table)

            transaction.commit_unless_managed()
            self.local_management_command('%s %s' % (self.loaddata_command,
                                                     dump_file))

        # ... then cleanup the dump file
        local('rm %s' % dump_file)
