# -*- coding: utf-8 -*-
import time

import django
import requests
from fabric import colors
from fabric.api import cd, local, run
from fabric.context_managers import quiet, settings
from fabric.contrib import django as fab_django
from fabric.contrib.console import confirm
from fabric.contrib.files import exists
from fabric.operations import get
from fabric.utils import abort

STATIC_FILES = 'django.contrib.staticfiles'


class App(object):
    project_paths = {}
    project_package = None
    test_settings = None
    strict = False
    restart_command = None
    loaddata_command = 'loaddata'
    dumpdata_command = 'dumpdata'
    urls = None
    local_tables_to_flush = []
    requirements = {
        'dev': 'requirements.txt',
        'prod': 'requirements.txt',
    }
    status_code = 200
    virtualenv_activate = 'source venv/bin/activate'

    def __init__(self, project_paths=None, project_package=None, test_settings=None, strict=False,
                 restart_command=None, loaddata_command=None, dumpdata_command=None,
                 requirements=None, local_tables_to_flush=[], urls=None, virtualenv_activate=None):
        self.project_paths = project_paths or self.project_paths
        self.project_package = project_package or self.project_package
        self.test_settings = test_settings or self.test_settings
        self.restart_command = restart_command or self.restart_command
        self.loaddata_command = loaddata_command or self.loaddata_command
        self.dumpdata_command = dumpdata_command or self.dumpdata_command
        self.local_tables_to_flush = local_tables_to_flush or self.local_tables_to_flush
        self.requirements = requirements or self.requirements
        self.strict = strict or self.strict
        self.urls = urls or self.urls
        self.virtualenv_activate = virtualenv_activate or self.virtualenv_activate
        fab_django.project(self.project_package)

    def notify(self, message):
        print(message)

    def run(self, command):
        with quiet():
            return run(command)

    def local(self, command, *args, **kwargs):
        with quiet():
            return local(command, *args, **kwargs)

    def exists(self, *args, **kwargs):
        return exists(*args, **kwargs)

    def get(self, *args, **kwargs):
        return get(*args, **kwargs)

    def local_management_command(self, command, *args, **kwargs):
        return self.local('python manage.py %s' % command, *args, **kwargs)

    def run_management_command(self, instance, command):
        if instance == 'local':
            return self.local_management_command(command)

        code_dir = self.project_paths[instance]
        with cd(code_dir):
            return self.run('%s && python manage.py %s' % (self.virtualenv_activate, command))

    def get_head_hash(self):
        return self.run('git rev-parse HEAD')

    def test(self, is_deploying=True):
        with settings(warn_only=True):
            self.notify(colors.yellow('Running tests, please wait!'))
            if settings is None:
                command = 'test --settings=%s' % \
                          self.test_settings
            else:
                command = 'test'
            result = self.local_management_command(command, capture=True)

        if result.failed:
            self.notify(colors.red('Tests failed'))
            if is_deploying:
                if self.strict:
                    abort(colors.red('You are not allowed to deploy with '
                                     'broken tests'))
                if not confirm('Do you really want to deploy?'):
                    abort('Ok!')
        else:
            self.notify(colors.green('All tests ok'))

    def lock_value(self):
        return self.local('git config user.name', capture=True)

    def lock(self, instance):
        with cd(self.project_paths[instance]):
            if self.exists('.deploying'):
                locker = self.run('cat .deploying')
                if self.lock_value() != '' and locker == self.lock_value():
                    if not confirm(colors.red('Deployment is locked by yourself! '
                                              'Do you want to continue?')):
                        abort(colors.red('Deployment is locked!'))
                else:
                    abort(colors.red('Deployment is locked by %s!' % locker))

            self.run('echo %s > .deploying' % self.lock_value())

    def unlock(self, instance):
        with cd(self.project_paths[instance]):
            self.run('rm .deploying')

    def syncdb(self, instance):
        from django.conf import settings
        if django.VERSION >= (1, 7):
            self.run_management_command(instance, 'migrate --noinput')
        elif 'south' in settings.INSTALLED_APPS:
            self.run_management_command(instance, 'syncdb --noinput --migrate')
        else:
            self.run_management_command(instance, 'syncdb --noinput')

        self.notify(colors.green('Synced/Migrated the database'))

    def run_server_updates(self, instance):
        code_dir = self.project_paths[instance]
        with cd(code_dir):
            self.run('git fetch')
            self.run('git reset --hard origin/master')
            self.notify(colors.green('HEAD is now at %s' % self.get_head_hash()[:6]))

            self.run('%s && pip install -r%s' % (self.virtualenv_activate,
                                                 self.requirements[instance]))
            self.notify(colors.green('Updated requirements'))

            self.syncdb(instance)

            from django.conf import settings

            if 'djangobower' in settings.INSTALLED_APPS:
                self.run_management_command(instance, 'bower_install')
                self.notify(colors.green('Ran bower install'))

            if STATIC_FILES in settings.INSTALLED_APPS and settings.STATIC_ROOT is not None:
                self.run_management_command(instance, 'collectstatic --noinput')
                self.notify(colors.green('Collected static files'))

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
                self.notify(colors.yellow('Checking if %s is alive...' % instance))
                response = requests.get(self.urls[instance]).status_code
                if response != self.status_code:
                    self.notify(colors.red('Sound the alarm, %s did noe respond correctly(%s)' % (
                        instance,
                        response
                    )))

                self.notify(colors.green('Relax already, %s returned %s' % (instance, response)))
                return response == self.status_code
            else:
                self.notify(colors.yellow('I have no url for %s' % instance))
                return False

    def deploy(self, instance=None, run_tests=True):
        if instance is None:
            abort(colors.red('You need to provide instance on the form deploy:instance'))
        if bool(run_tests) or confirm('Do you want to run tests before deploying?'):
            self.test(is_deploying=True)

        self.lock(instance)
        if hasattr(self, 'pre_deploy_notify'):
            self.pre_deploy_notify(instance)
        self.run_server_updates(instance)
        self.restart_app(instance)
        self.check_status(instance)
        self.unlock(instance)
        if hasattr(self, 'post_deploy_notify'):
            self.post_deploy_notify(instance)

    def translate(self):
        self.local_management_command('makemessages --all')
        self.notify(colors.green('Made translation files'))

        if confirm('Compile messages?'):
            self.local_management_command('compilemessages')
            self.notify(colors.green('Compiled translation files'))

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

            with transaction.atomic():
                cursor = connection.cursor()
                cursor.execute('DELETE FROM django_content_type;')
                cursor.execute('DELETE FROM auth_permission;')

                for table in self.local_tables_to_flush:
                    cursor.execute('DELETE FROM %s;' % table)

            self.local_management_command('%s %s' % (self.loaddata_command, dump_file))

            self.notify(colors.green('Cloned data from %s into the local database' % instance))

        # ... then cleanup the dump file
        self.local('rm %s' % dump_file)
