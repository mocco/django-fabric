---
title: django-fabric 
layout: base
description: a generic fabric utility class for django projects
github: django-fabric
---

# django-fabric
django-fabric is written to make writing fabfiles for django projects easier and faster.
It contains the basic stuff one would expect from a django setup with git and virtualenv. The code
expects the project to have a certain structure as seen below.

    project-dir/
      venv/ # virtualenv
      project-package/
      manage.py
      fabfile.py

## Usage

Create a `fabfile.py` in your project directory. You can see example of a fabfile below. If you 
run into problems with settings where fabric cannot locate settings add 
`sys.path.append(os.path.dirname(__file__))` to your fabfile.

### Basic setup

    from fabric.decorators import task
    from fabric.state import env
    from django_fabric import App

    env.user = 'web'
    env.hosts = ['server1.example.com']

    site = App(
        project_paths={
            'prod': '/var/www/example_site',
        },
        project_package='example',
        test_settings='example.settings.test',
        restart_command='project restart'
    )

    deploy_dev = task(site.deploy_dev)
    deploy_prod = task(site.deploy_prod)
    test = task(site.test)

### App-server spesific usage
There are some, or at least one at this moment, classes that have spesific restart routines. They
are listed below:

* `django_fabric.uwsgi.UwsgiApp`
