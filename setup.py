from setuptools import find_packages, setup

try:
    with open('docs/quickstart.rst', 'r') as f:
            QUICKSTART = f.read()
except IOError:
    QUICKSTART = ''


setup(
    name='django-fabric',
    version='2.0.1',
    author='Rolf Erik Lekang',
    author_email='rolf@mocco.no',
    url='https://github.com/mocco/django-fabric',
    packages=find_packages(),
    description='a generic fabric utility class for django projects',
    long_description=QUICKSTART,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Environment :: Web Environment",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
    include_package_data=True,
    test_suite='tests.run',
    zip_safe=False,
    install_requires=['fabric', 'django', 'requests'],
    test_requires=['fabric', 'django', 'requests'],
    entry_points={
        'console_scripts': [
            'django-fabric-init = django_fabric.commands:init',
        ]
    }
)
