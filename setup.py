from setuptools import find_packages, setup

setup(
    name='django-fabric',
    version='1.0',
    author='Rolf Erik Lekang',
    author_email='rolf@mocco.no',
    packages=find_packages(),

    include_package_data=True,
    zip_safe=False,
    install_requires=['fabric']
)
