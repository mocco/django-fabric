from setuptools import find_packages, setup

setup(
    name='django-fabric',
    version='1.3',
    author='Rolf Erik Lekang',
    author_email='rolf@mocco.no',
    url='http://mocco.no/django-fabric/',
    packages=find_packages(),
    description='a generic fabric utility class for django projects',
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Environment :: Web Environment",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=['fabric', 'django']
)
