#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from setuptools import setup


required = [line for line in open('requirements.txt').read().split("\n")]

mfinit = open('misfit/__init__.py').read()
refind = lambda varname: re.search("%s = '([^']+)'" % varname, mfinit).group(1)

setup(
    name='misfit',
    version=refind('__version__'),
    description='Misfit API client implementation',
    long_description=open('README.rst').read(),
    author=refind('__author__'),
    author_email=refind('__author_email__'),
    url='https://github.com/orcasgit/python-misfit',
    packages=['misfit'],
    package_data={'': ['LICENSE']},
    include_package_data=True,
    install_requires=["setuptools"] + required,
    license=refind('__license__'),
    entry_points={
        'console_scripts': ['misfit=misfit.cli:main'],
    },
    classifiers=(
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: PyPy'
    ),
)
