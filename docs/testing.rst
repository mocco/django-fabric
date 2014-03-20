Testing
=======
We all get a little nervous the first time we run a deploy script on production.
Well, don't do it without proper testing first. django-fabric is used as deployment
tool in several organisations. However, you should feel a lot more safe that you
configured it correctly if you test it first.

One way to test it is to run a deployment of a staging environment before you deploy
to your production environment.

The testing mixin
-----------------
There is one way to do a no-operation run of the deployment, wich mean that
every command that will be ran on your servers will be printed instead.
This will give you a way to visually confirm the shell commands before running
them on a server. The example below shows how to use the mixin.
::
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
