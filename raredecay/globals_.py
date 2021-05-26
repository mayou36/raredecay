"""
Created on Thu Apr 14 14:34:21 2016

@author: Jonas Eschle "Mayou36"

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

Variables
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

# Python 2 backwards compatibility overhead START
import sys  # noqa
import warnings  # noqa
from . import meta_config  # noqa

try:  # noqa
    from future.builtins.disabled import (
        apply,
        cmp,
        coerce,
        execfile,
        file,
        long,
        raw_input,  # noqa
        reduce,
        reload,
        unicode,
        xrange,
        StandardError,
    )  # noqa
    from future.standard_library import install_aliases  # noqa

    install_aliases()  # noqa
except ImportError as err:  # noqa
    if sys.version_info[0] < 3:  # noqa
        if meta_config.SUPPRESS_FUTURE_IMPORT_ERROR:  # noqa
            meta_config.warning_occured()  # noqa
            warnings.warn(
                "Module future is not imported, error is suppressed. This means "  # noqa
                "Python 3 code is run under 2.7, which can cause unpredictable"  # noqa
                "errors. Best install the future package.",
                RuntimeWarning,
            )  # noqa
        else:  # noqa
            raise err  # noqa
    else:  # noqa
        basestring = str  # noqa

# Python 2 backwards compatibility overhead END

from . import meta_config as meta_cfg
from . import config as cfg
from .tools import output

__all__ = ["out", "logger_cfg", "n_cpu_used", "free_cpus"]

# ==============================================================================
# Output handler. Contains methods "initialize" and "finalize"
# ==============================================================================

out = output.OutputHandler()

logger_cfg = cfg.logger_cfg  # only if not save_output

# def set_output_handler(internal=True):
#   global out
#   if internal:
#     out = output.OutputHandlerInt()
#   else:
#     out = output.OutputHandlerExt()


# ==============================================================================
# parallel profile
# ==============================================================================

n_cpu_used = 0


def free_cpus():
    """Return the number of free cpus, 1 if no or one are free"""
    n_out = max([meta_cfg.n_cpu_max - n_cpu_used, 1])
    return n_out
