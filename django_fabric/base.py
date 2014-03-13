# -*- coding: utf-8 -*-
import time

from fabric.context_managers import settings, quiet
from fabric.contrib.console import confirm
from fabric.contrib.files import exists
from fabric.api import local, run, cd
from fabric.operations import get
from fabric.contrib import django
from fabric.utils import abort
from fabric import colors

import requests


class App(object):
    project_paths = {}
    project_package = None
    test_settings = None
    strict = False
    restart_command = None
    loaddata_command = None
    dumpdata_command = None
    urls = None
    local_tables_to_flush = []
    requirements = {
        'dev': 'requirements.txt',
        'prod': 'requirements.txt',
    }

    def __init__(self, project_paths, project_package, test_settings=None,
                 strict=False, restart_command=None,
                 loaddata_command='loaddata', dumpdata_command='dumpdata',
                 requirements=None, local_tables_to_flush=[], urls=None):
        self.project_paths = project_paths
        self.project_package = project_package
        self.test_settings = test_settings
        self.strict = strict
        self.restart_command = restart_command
        self.loaddata_command = loaddata_command
        self.dumpdata_command = dumpdata_command
        self.local_tables_to_flush = local_tables_to_flush
        self.requirements = requirements or self.requirements
        self.urls = urls
        django.project(project_package)

    def run(self, command):
        with quiet():
            return run(command)

    def local(self, command, *args, **kwargs):
        with quiet():
            return local(command, *args, **kwargs)

    def local_management_command(self, command, *args, **kwargs):
        return self.local('venv/bin/python manage.py %s' % command, *args,
                          **kwargs)

    def run_management_command(self, instance, command):
        if instance == 'local':
            return self.local_management_command(command)

        code_dir = self.project_paths[instance]
        with cd(code_dir):
            return self.run('venv/bin/python manage.py %s' % command)

    def get_head_hash(self):
        return self.run('git rev-parse HEAD')

    def test(self, is_deploying=True):
        with settings(warn_only=True):
            print(colors.yellow('Running tests, please wait!'))
            if settings is None:
                command = 'test --settings=%s' % \
                          self.test_settings
            else:
                command = 'test'
            result = self.local_management_command(command, capture=True)

        if result.failed:
            print(colors.red('Tests failed'))
            if is_deploying:
                if self.strict:
                    abort(colors.red('You are not allowed to deploy with '
                                     'broken tests'))
                if not confirm('Do you really want to deploy?'):
                    abort('Ok!')
        else:
            print(colors.green('All tests ok'))

    def lock_value(self):
        return ''

    def lock(self, instance):
        with cd(self.project_paths[instance]):
            if exists('.deploying'):
                abort(colors.red('Deployment is locked!'))

            self.run('echo %s > .deploying' % self.lock_value())

    def unlock(self, instance):
        with cd(self.project_paths[instance]):
            self.run('rm .deploying')

    def syncdb(self, instance):
        from django.conf import settings

        if 'south' in settings.INSTALLED_APPS:
            self.run_management_command(instance,
                                        'syncdb --noinput --migrate')
        else:
            self.run_management_command(instance, 'syncdb --noinput')

        print(colors.green('Synced/Migrated the database'))

    def run_server_updates(self, instance):
        code_dir = self.project_paths[instance]
        with cd(code_dir):
            self.run('git fetch')
            self.run('git reset --hard origin/master')
            print(colors.green('HEAD is now at %s' % self.get_head_hash()[:6]))

            self.run('venv/bin/pip install -r%s' % self.requirements[instance])
            print(colors.green('Updated requirements'))

            self.syncdb(instance)

            from django.conf import settings

            if 'djangobower' in settings.INSTALLED_APPS:
                self.run_management_command(instance, 'bower_install')
                print(colors.green('Ran bower install'))

            if 'django.contrib.staticfiles' in settings.INSTALLED_APPS and \
               not settings.STATIC_ROOT is None:
                self.run_management_command(instance,
                                            'collectstatic --noinput')
                print(colors.green('Collected static files'))

    def restart_app(self, instance):
        if self.restart_command is None:
            # If restart command is not used this method should have been
            # overrided
            raise NotImplementedError
        else:
            self.run(self.restart_command[instance])

    def check_status(self, instance):
        if self.urls is not None:
            if instance in self.urls:
                print(colors.yellow('Checking if %s is alive...' % instance))
                response = requests.get(self.urls[instance]).status_code
                if response != 200:
                    print(colors.red('Sound the alarm, %s did noe respond '
                                     'correctly(%s)' % (instance, response)))

                print(colors.green('Relax already, %s returned 200' %
                                   instance))
                return response == 200
            else:
                print(colors.yellow('I have no url for %s' % instance))
                return False

    def deploy(self, instance=None, run_tests=True):
        if instance is None:
            abort(colors.red('You need to provide instance on the form '
                             'deploy:instance'))
        if bool(run_tests) or \
           confirm('Do you want to run tests before deploying?'):
                self.test(is_deploying=True)

        self.lock(instance)
        self.run_server_updates(instance)
        self.restart_app(instance)
        self.check_status(instance)
        self.unlock(instance)

    def translate(self):
        self.local_management_command('makemessages --all')
        print(colors.green('Made translation files'))

        if confirm('Compile messages?'):
            self.local_management_command('compilemessages')
            print(colors.green('Compiled translation files'))

    def clone_data(self, instance):
        if not confirm('All local data will be replaced with '
                       'data from %s, OK?' % instance):
            abort('Ok!')

        dump_file = '%s.json' % str(int(time.time()))

        # Ignore errors on these next steps, so that we are sure we clean up
        # no matter what
        with settings(warn_only=True) and cd(self.project_paths[instance]):
            # Dump the database to a file...
            self.run_management_command(
                instance,
                '%s --all > %s' % (self.dumpdata_command, dump_file)
            )

            # The download that file, all uploaded files and rm the dump file
            get('%s%s' % (self.project_paths[instance], dump_file), dump_file)
            self.run('rm %s' % dump_file)

            self.syncdb('local')
            self.local_management_command('flush --noinput')

            from django.db import connection, transaction

            cursor = connection.cursor()
            cursor.execute('DELETE FROM django_content_type;')

            for table in self.local_tables_to_flush:
                cursor.execute('DELETE FROM %s;' % table)

            transaction.commit_unless_managed()
            self.local_management_command('%s %s' % (self.loaddata_command,
                                                     dump_file))

            print(colors.green('Cloned data from %s into the local '
                               'database' % instance))

        # ... then cleanup the dump file
        self.local('rm %s' % dump_file)
