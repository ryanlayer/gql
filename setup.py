import ez_setup
ez_setup.use_setuptools()

import glob
import os
import sys
import distutils
from setuptools import setup
from distutils.extension import Extension

if 'setuptools.extension' in sys.modules:
    m = sys.modules['setuptools.extension']
    m.Extension.__dict__ = m._Extension.__dict__

version_py = os.path.join(os.path.dirname(__file__), 'gql', 'version.py')
version = open(version_py).read().strip().split('=')[-1].replace('"','')
long_description = """
``gql`` is a genome query language'
"""

setup(
        name="gql",
        version=version,
        install_requires=['ply>=3.4', 
                          'pybedtools>=0.6.2',],
        dependency_links = [],
        requires = ['python (>=2.5, <3.0)'],
        packages=['gql',
                  'gql.scripts'],
        author="Ryan Layer",
        description='A langauge for genome exploration and comparison',
        long_description=long_description,
        url="none",
        package_dir = {'gql': "gql"},
		data_files = [ ('gql/config',['gql/config/gql.conf']) ],
        zip_safe = False,
        scripts = ['gql/scripts/gql'],
        author_email="rl6sf@virginia.edu",
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Topic :: Scientific/Engineering :: Bio-Informatics']
    )
