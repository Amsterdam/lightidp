#!/usr/bin/env python

import sys

from codecs import open

from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    """ Custom class to avoid depending on pytest-runner.
    """
    user_options = [('pytest-args=', 'a', "Arguments to pass into py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest

        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

version = '0.1.1rc1'

packages = ['auth']

# Why are you so precise about the versions here? --PvB
requires = [
    'datapunt-accounts~=1.0',
    'Flask==1.0',
    'graypy',
    'jsonschema==2.6.0',
    'PyJWT==1.5.2',
    'pyyaml==5.4',
    'requests==2.20.0',
    'uwsgi',
]
requires_test = ['responses==0.5.1', 'pytest==3.0.5', 'pytest-cov==2.4.0',
                 'pytest-capturelog==0.7']
requires_extras = {
    'docs': [
        'sphinx',
        'sphinx-autobuild',
        'sphinx-rtd-theme',
    ],
    'dev': requires_test + [ 'pylint' ],
}

setup(
    name='datapunt-auth',
    version=version,
    description='Datapunt Amsterdam authn & authz service',
    long_description=long_description,
    url='https://github.com/DatapuntAmsterdam/auth',
    author='Amsterdam Datapunt',
    author_email='datapunt.ois@amsterdam.nl',
    license='Mozilla Public License Version 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Topic :: System :: Systems Administration :: Authentication/Directory',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    cmdclass={'test': PyTest},
    packages=packages,
    install_requires=requires,
    tests_require=requires_test,
    extras_require=requires_extras,
)
