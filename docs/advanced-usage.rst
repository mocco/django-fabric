Advanced usage
==============
To be able to use different mixins or override som methods in the App class it is necessary to subclass it.
If you use this approach in your fabfile it is possible to move your values out of the
init call as seen in the example below, if you want to.::
    from fabric.decorators import task
    from fabric.state import env
    from django_fabric import App

    env.user = 'web'
    env.hosts = ['server1.example.com']

    class Site(App):
        project_package = 'package'
        project_paths = {
            'prod': 'path-to-prod'
        }
        restart_command = {
            'prod': 'restart prod'
        }

    site = Site()

    deploy = task(site.deploy)
    test = task(site.test)

Need to use custom commands on the server?
------------------------------------------
Need to :code:`su` to a specific user or something similar. No problem! Just override the
method :code:`App.run(command)`, but there are a few things to remember.

- Add :code:`with quiet():` context manager around your code if you want to hide the output from fabric and only show the output from django-fabric.
- Return the fabric run command. This is used to determine the output of the command several places.
