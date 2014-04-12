Quickstart
==========
django-fabric is written to make writing fabfiles for django projects easier and faster.
It contains the basic stuff one would expect from a django setup with git and virtualenv. The code
expects the project to have a certain structure as seen below. It is possible to customize the
activation of the virtualenvironment.::
    project-dir/
      venv/ # virtualenv
      project-package/
      manage.py
      fabfile.py

Installation
------------
Run :code:`pip install django-fabric`


Usage
-----
There is two options to get get a basic setup, both will make you able to run :code:`fab deploy:prod` and :code:`fab test`.

Init script
~~~~~~~~~~~
There is a init script that will guide you through the generation of a basic fabfile
that utilises django-fabric. Run it with the command
::
    django-fabric-init

Basic manual setup
~~~~~~~~~~~~~~~~~~
Create a :code:`fabfile.py` in your project directory. You can see example of a fabfile below. If you
run into problems with settings where fabric cannot locate settings add
:code:`sys.path.append(os.path.dirname(__file__))` to your fabfile.


Here is an example of an fabfile
::
    from fabric.decorators import task
    from fabric.state import env
    from django_fabric import App

    env.user = 'web'
    env.hosts = ['server1.example.com']

    site = App(
        project_paths={
            'prod': '/var/www/example_site',
        },
        urls={
            'prod': 'http://example.com'
        },
        restart_command={
            'prod': 'restart prod'
        },
        project_package='example',
        test_settings='example.settings.test',
    )

    deploy = task(site.deploy)
    test = task(site.test)
