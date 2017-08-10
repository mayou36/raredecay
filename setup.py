# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 16:26:12 2016

@author: Jonas Eschle "Mayou36"
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from builtins import (ascii, bytes, chr, dict, filter, hex, input,
                      int, map, next, oct, open, pow, range, round,
                      str, super, zip)

from setuptools import setup
import subprocess

import io
import os

here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, 'requirements.txt')) as f:
    requirements = f.read().split('\n')


def readme():
    with open('README.rst') as f:
        return f.read()

git_version = '1.4.0'

extras_require = {'all': []}
extras_require_tmp = {
                  'root': ['root_numpy',
                           'rootpy'],
                 'reweight': ['hep_ml>= 0.4'],
                  'ml': [
                        'rep>=0.6.6',
                         'scikit-learn>=0.18.1']

      		     }
for val in extras_require_tmp.values():
    extras_require['all'] += val

setup(name='raredecay',
      version=git_version,
      description='A package for analysis of rare particle decays with machine-learning algorithms',
      long_description=readme(),
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: MacOS',
		'Operating System :: MacOS :: MacOS X',
		'Operating System :: POSIX :: Linux',
		'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: Implementation :: CPython',
		'Topic :: Scientific/Engineering :: Physics',
		'Topic :: Scientific/Engineering :: Information Analysis',
      ],
      keywords='particle physics, analysis, machine learning, reweight, high energy physics',
      url='https://github.com/mayou36/raredecay',
      author='Jonas Eschle',
      author_email='mayou36@jonas.eschle.com',
      license='Apache-2.0 License',
#      dependency_links=['https://github.com/yandex/rep/archive/stratifiedkfold.zip'],
      install_requires=requirements,
      extras_require=extras_require,
      packages=['raredecay',
                'raredecay.analysis',
                'raredecay.tools',
                ],
      include_package_data=True,
      zip_safe=False
      )
