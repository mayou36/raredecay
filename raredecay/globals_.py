# -*- coding: utf-8 -*-
"""
Created on Thu Apr 14 14:34:21 2016

@author: mayou

This module contains all (package-)global variables and methods.

Instances
---------
out : object of class :class:`~raredecay.tools.output.OutputHandler`
    An instance which is initiated once for the whole package and handles
    all the output and metastructure of the code:

    * initialization:

      - create and set run-dependant variables
      - create folders to save the collected output
      - create loggers

    * collection of output:

      - collect figures and save them later on
      - concatenate every string output and format it

    * finalization:

      - add general information to the output
      - save all the figures and outputs
      - collect run information like errors occured

    It is important to use the same instance (of course) for the same run.
    Everything else would be very special case.

    .. note:: To ensure that you import the instance and to not make a copy,
      always import with an alias

Variables:
---------
randint : int
    Many methods need random integers for their pseudo-random generator.
    To keep them all the same (or intentionally not), use the randint.

methods
-------
free_cpus
    Return the number of available cores. Currently not sophisticated, but
    can be extended if wanted
"""

from __future__ import division, absolute_import

import random

from raredecay.tools import output
from raredecay import meta_config

#==============================================================================
# Output handler. Contains methods "initialize" and "finalize"
#==============================================================================

out = None


def set_output_handler(internal=True):
  global out
  if internal:
    out = output.OutputHandlerInt()
  else:
    out = output.OutputHandlerExt()

#==============================================================================
# Random integer generator for pseudo random generator (or other things)
#==============================================================================

randint = random.randint(123, 1512412)  # 357422 or 566575

#==============================================================================
# parallel profile
#==============================================================================

n_cpu_used = 0
def free_cpus():
    n_out = max([meta_config.n_cpu_max - n_cpu_used, 1])
    return n_out




if __name__=='__main__':
    print "Selftest start"
    print "Selftest completed"