# -*- coding: utf-8 -*-
from fabric.contrib.console import confirm


TEMPLATE = """
from fabric.decorators import task
from fabric.state import env
from django_fabric import App

env.user = '%(server_user)s'
env.hosts = ['%(server)s']

site = App(
    project_paths={
        %(project_paths)s
    },
    %(urls)s
    restart_command={
        %(restart_commands)s
    },
    project_package='%(project_package)s',
    %(test_settings)s
)

deploy = task(site.deploy)
test = task(site.test)
"""


def render_template(settings):
    return TEMPLATE % settings


def init():
    settings = {
        'project_package': raw_input('What is your project package called? '),
        'server_user': raw_input('What is the server user? '),
        'server': raw_input('What is the server host? '),
        'test_settings': '',
        'urls': '',
        '_project_paths': {},
        '_restart_commands': {},
        '_urls': {}
    }

    if confirm('Do you have a test configuration file?', default=False):
        test_settings = raw_input('What is the python path to your test '
                                  'settings(my_app.settings.test)? ')
        settings['test_settings'] = "test_settings='%s'" % test_settings

    instances = raw_input('What is the name of your instances'
                          '(use a commaseperated list)? ').split(',')

    for instance in instances:
        instance = instance.strip()
        settings['_project_paths'][instance] = raw_input(
            'What is the full path of %s instance on the server? ' % instance
        )

        settings['_restart_commands'][instance] = raw_input(
            'What is the restart command for %s '
            'instance on the server? ' % instance
        )

    if confirm('Do you want to check if the site is up after deployment?'):
        for instance in instances:
            instance = instance.strip()
            settings['_urls'][instance] = raw_input(
                'What is the full url of %s instance? ' % instance
            )

        urls = ',\n    '.join(
            ["\'%s\': \'%s\'" % (key, path)
             for key, path in settings['_urls'].items()]
        )

        settings['urls'] = "urls={\n        %s\n    }," % urls

    settings['project_paths'] = ',\n    '.join(
        ["\'%s\': \'%s\'" % (key, path)
         for key, path in settings['_project_paths'].items()]
    )

    settings['restart_commands'] = ',\n    '.join(
        ["\'%s\': \'%s\'" % (key, cmd)
         for key, cmd in settings['_restart_commands'].items()]
    )

    with open('fabfile.py', 'w') as f:
        f.write(render_template(settings))

if __name__ == '__main__':
    init()
