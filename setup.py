# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 16:26:12 2016

@author: Jonas Eschle "Mayou36"
"""

from setuptools import setup
import subprocess


def readme():
    with open('README.md') as f:
        return f.read()
try:
    git_version = subprocess.check_output(["git", "-C",
                        "/home/mayou/Documents/uniphysik/Bachelor_thesis/python_workspace/raredecay/raredecay",
                        "describe"])
    git_version = git_version.partition('-')
    git_version = str(git_version[0])
except:
    git_version = 'unknown'
#git_version = '0.9.5'


setup(name='raredecay',
      version=git_version,
      description='A package for analysis of rare particle decays with machine-learning algorithms',
      long_description=readme(),
      classifiers=[
        'Development Status :: 10 - Alpha',
        'Programming Language :: Python :: 2.7',
      ],
      keywords='particle physics analysis machine learning reweight',
      url='https://github.com/mayou36/raredecay',
      author='Jonas Eschle',
      author_email='mayou36@jonas.eschle.com',
      license='None',
      install_requires=[
          'hep_ml',
          'rep>=0.6.6',
          #'https://github.com/yandex/rep/archive/stratifiedkfold.zip',
          'sklearn>=0.17.1'
          'nose_parameterized'
          'root_numpy'
	  #'rootpy'
          'seaborn'
	#'memory_profiler'  # for developement, can be removed later
      ],
      packages=['raredecay',
                'raredecay.analysis',
                'raredecay.run_config',
                'raredecay.tools',
      ],
      include_package_data=True,
      zip_safe=False
      )
