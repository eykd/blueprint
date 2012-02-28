#!/usr/bin/env python

# Bootstrap installation of Distribute
import distribute_setup
distribute_setup.use_setuptools()

import os

from setuptools import setup


PROJECT = 'python-blueprint'
VERSION = '0.3.2'
URL = 'https://github.com/eykd/blueprint'
AUTHOR = 'David Eyk'
AUTHOR_EMAIL = 'david.eyk@gmail.com'
DESC = "Magical blueprints for procedural generation of content."


def read_file(file_name):
    file_path = os.path.join(
        os.path.dirname(__file__),
        file_name
        )
    return open(file_path).read()

setup(
    name=PROJECT,
    version=VERSION,
    description=DESC,
    long_description=read_file('README.rst'),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=read_file('LICENSE'),
    packages=[u'blueprint'],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # see http://pypi.python.org/pypi?:action=list_classifiers
        # -*- Classifiers -*- 
        "Programming Language :: Python",
        "Topic :: Games/Entertainment",
        "Topic :: Artistic Software",
        "License :: OSI Approved :: MIT License",
    ],
)
