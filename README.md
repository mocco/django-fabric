# django-fabric

a generic fabric utility class for django projects

## Usage

Create a `fabfile.py` in your project directory. You can see example of a fabfile below. If you 
run into problems with settings where fabric cannot locate settings add 
`sys.path.append(os.path.dirname(__file__))` to your fabfile.

```python
from fabric.decorators import task
from fabric.state import env
from django_fabric.fabfile import App

env.user = 'web'
env.hosts = ['server1.example.com']

site = App(
    project_paths={
        'prod': '/var/www/example_site',
    },
    project_package='example',
    test_settings='example.settings.test'
)

deploy_dev = task(site.deploy_dev)
deploy_prod = task(site.deploy_prod)
test = task(site.test)
```
