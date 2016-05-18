# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 16:26:12 2016

@author: mayou
"""

from setuptools import setup
import subprocess


def readme():
    with open('README.md') as f:
        return f.read()
git_version = subprocess.check_output(["git", "-C",
            "/home/mayou/Documents/uniphysik/Bachelor_thesis/python_workspace/HEP-decay-analysis/raredecay",
            "describe"])
git_version = git_version.partition('-')


setup(name='raredecay',
      version=git_version,  # '0.8.5',
      description='A package for analysis of rare particle decays with ml',
      long_description=readme(),
      classifiers=[
        'Development Status :: 8 - Alpha',
        'Programming Language :: Python :: 2.7',
      ],
      keywords='particle physics analysis machine learning reweight',
      url='https://bitbucket.org/mayou36/hep-ml-analysis',
      author='Jonas Eschle',
      author_email='mayou36@jonas.eschle.com',
      license='None',
      install_requires=[
          #'hep_ml',
          #'rep',
      ],
      packages=['raredecay',
                'raredecay.analysis',
                'raredecay.run_config',
                'raredecay.tools',
      ],
      include_package_data=True,
      zip_safe=False)