#!/bin/env python

from setuptools import setup
from subprocess import check_output, DEVNULL
from os.path import join, dirname

version = '0.0.0'
version_py = join( dirname(__file__), 'mconv', 'version.py')

try:
   version_git = check_output( ["git", "describe"], encoding='utf-8', stderr=DEVNULL ).rstrip().split('-')
   version_git[0] = version_git[0][1:]
   version = '.'.join( version_git[:2] )
except:
   print( 'INFO: No git tag found. Setup will use "%s" instead.' % version )
   pass

with open(version_py, 'w') as fh:
   fh.write( "__version__='%s'" % version )
with open("README.md", "r", encoding="utf-8") as fh:
   long_description = fh.read()

setup(
    name="mconv",
    version=version,
    author="Gabriel Llera",
    author_email="g113r4@gmail.com",
    description="Multimedia library maintainer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gllera/mconv",
    packages=['mconv'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
