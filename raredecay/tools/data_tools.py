# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 17:53:18 2016

@author: mayou

Contains several tools to convert, load, save and plot data
"""
from __future__ import division, absolute_import

import pandas as pd
import numpy as np
import cPickle as pickle

from root_numpy import root2array, array2tree
from ROOT import TObject
from rootpy.io import root_open

from raredecay.tools import dev_tool
from raredecay import meta_config

module_logger = dev_tool.make_logger(__name__, **meta_config.DEFAULT_LOGGER_CFG)


def add_to_rootfile(rootfile, new_branch, branch_name=None):
    """Adds a new branch to a given root file, overwrites.


    Parameters
    ----------
    rootfile : root-dict
        The ROOT-file where the data should be added
    new_branch : numpy.array 1-D, list, root-dict
        A one-dimensional numpy array that contains the data.
    branch_name : str
        The name of the branche resp. the name in the dtype of the array.
    """
    # get the right parameters
    # TODO: what does that if there? an assertion maybe?
    if isinstance(rootfile, dict):
        filename = rootfile.get('filenames')
    treename = rootfile.get('treename')
    new_branch = to_ndarray(new_branch)
    new_branch.dtype =[(branch_name, 'f8')]

    # write to ROOT-file
    with root_open(filename, mode='a') as f:
        array2tree(new_branch, tree=getattr(f, treename))
        f.write("", TObject.kOverwrite)  # overwrite, does not create friends


def format_data_weights(data_to_shape, weights, logger):
    """Format the data and the weights perfectly. Same length and more.

    Change the data to pandas.DataFrame and fill the weights with ones where
    nothing or None is specified. Returns both in lists.
    Very useful to loop over several data and weights.

    Parameters
    ----------
    data_to_shape : (root_dict, numpy.array, pandas.DataFrame)
        The data for which we apply the weights. Usual 2-D shape.
    weights : (list, numpy.array, pandas.DataFrame, None)
        The weights to be reshaped

        *Best format* :

        [array(weights),array(weights), None, array(weights),...]

        *None* can be used if no special weights are specified.
        If weights contains less "weight-containing array-like objects" then
        data_to_shape does, the difference will be filled with *1*

    Return
    ------
    out : list(pandas.DataFrame(data), pandas.DataFrame(data),...)
        Return a list containing data
    out : list(numpy.array(weight), numpy.array(weight),...)
        Return a list with the weights, converted and filled.
    """
    # conver the data
    if not isinstance(data_to_shape, list):
        data_to_shape = [data_to_shape]
    data_to_shape = map(to_pandas, data_to_shape)
    # convert the weights
    if not isinstance(weights, list):
        weights = [weights]
    if weights[0] is not None:
        if len(weights[0]) == 1:
            weights = [weights]
    # convert to pandas
    assert isinstance(weights, list), "weights could not be converted to list"
    for data_id, data in enumerate(data_to_shape):
        if data_id >= len(weights):
            weights.append(None)
        if weights[data_id] is None:
            weights[data_id] = np.array([1] * len(data))
        weights[data_id] = to_pandas(weights[data_id]).squeeze().values
    return data_to_shape, weights


def obj_to_string(objects, separator=None):
    """Return a string containing all objects as strings, separated by the separator.

    Useful for automatic conversion for different types. The following objects
    will automatically be converted:

    - None will be omitted

    Parameters
    ----------
    objects : any object or list(obj, obj, ...) with a string representation
        The objects will be converted to a string and concatenated, separated
        by the separator.
    separator : str
        The separator between the objects. Default is " - ".
    """
    if isinstance(objects, str):  # no need to change things
        return objects
    separator = " - " if separator is None else separator
    assert isinstance(separator, str), "Separator not a string"

    objects = to_list(objects)
    objects = [str(obj) for obj in objects if obj is not None]  # remove Nones
    string_out = ""
    for word in objects:
        string_out += word + separator if word != objects[-1] else word

    return string_out


def is_root(data_to_check):
    """Check whether a given data is a root file. Needs dicts to be True!
    """
    flag = False
    if isinstance(data_to_check, dict):
        path_name = data_to_check.get('filenames')
        assert isinstance(path_name, str), ("'filenames' of the dictionary " +
                                        str(data_to_check) + "is not a string")
        if path_name.endswith(meta_config.ROOT_DATATYPE):
            flag = True
    return flag


def is_list(data_to_check):
    """ Check whether the given data is a list
    """
    flag = False
    if isinstance(data_to_check, list):
        flag = True
    return flag


def is_ndarray(data_to_check):
    """Check whether a given data is an ndarray.
    """
    flag = False
    if isinstance(data_to_check, np.ndarray):
        flag = True
    return flag


def is_pickle(data_to_check):
    flag = False
    if isinstance(data_to_check, str):
        if data_to_check.endswith(meta_config.PICKLE_DATATYPE):
            flag = True
    return flag


def to_list(data_in):
    """Convert the data into a list. Does not pack objects into a new one.

    If your input is, for example, a string or a list of strings, or a
    tuple filled with strings, you have, in general, a problem:

    - just iterate through the object will fail because it iterates through the
      characters of the string.
    - using list(obj) converts the tuple, leaves the list but splits the strings
      characters into single elements of a new list.
    - using [obj] creates a list containing a string, but also a list containing
      a list or a tuple, which you did not want to.

    Solution: use to_list(obj), which creates a new list in case the object is
    a single object (a string is a single object in this sence) or converts
    to a list if the object is already a container for several objects.

    Parameters
    ----------
    data_in : any obj
        So far, any object can be entered.

    Returns
    -------
    out : list
        Return a list containing the object or the object converted to a list.
    """
    if isinstance(data_in, str):
        data_in = [data_in]
    data_in = list(data_in)
    return data_in


def to_ndarray(data_in, logger=None, dtype=None, float_array=True):
    """Convert data to numpy array (containing only floats)

    """
    if logger is None:
        logger = module_logger
    if is_root(data_in):
        data_in = root2array(**data_in)  # why **? it's a root dict
    # change numpy.void to normal floats
    if isinstance(data_in, (pd.Series, pd.DataFrame)):
        test_sample = data_in.iloc[0]
    else:
        test_sample = data_in[0]
    if isinstance(test_sample, np.void):
        data_in = np.array([val[0] for val in data_in])
    if isinstance(data_in, (np.recarray, np.ndarray)):
        data_in = data_in.tolist()
    if is_list(data_in) or isinstance(data_in, pd.Series):
        data_in = np.array(data_in)
    if float_array:
        data_in = np.asfarray(data_in)
    assert is_ndarray(data_in), "Error, could not convert data to numpy array"
    return data_in


def to_pandas(data_in, logger=None, indices=None, columns=None, dtype=None):
    """Convert data from numpy or root to pandas dataframe.

    Convert data safely to pandas, whatever the format is.
    """
    if logger is None:
        logger = module_logger
    if is_root(data_in):
        data_in = root2array(**data_in)  # why **? it's a root dict
    if is_list(data_in):
        data_in = np.array(data_in)
    if is_ndarray(data_in):
        data_in = pd.DataFrame(data_in)
    elif type(data_in) is pd.core.frame.DataFrame:
        pass
    else:
        raise TypeError("Could not convert data to pandas. Data: " + data_in)
    return data_in


def adv_return(return_value, save_name=None, logger=None):
    """Save the value if save_name specified, otherwise just return input

    Can be wrapped around the return value. Without any arguments, the return
    of your function will be exactly the same. With arguments, the value can
    be saved (**pickled**) before it is returned.

    Parameters
    ----------
    return_value : any python object
        The python object which should be pickled.
    save_name : str, None
        | The (file-)name for the pickled file. File-extension will be added
        automatically if specified in *raredecay.meta_config*.
        | If *None* is passed, the object won't be pickled.
    logger : python-logger
        Can be passed to avoid using the module_logger but to use another one.

    Return
    ------
    out : python object
        Return return_value without changes.

    **Usage**:
     Instead of a simple return statement

     >>> return my_variable/my_object

     one can use the **completely equivalent** statement

     >>> return adv_return(my_variable/my_object)

     If the return value should be saved in addition to be returned, use

     >>> return adv_return(my_variable/my_object, save_name='my_object.pickle')

      (*the .pickle ending is not required but added automatically if omitted*)
     which returns the value and saves it.
    """
    if logger is None:
        logger = module_logger
    if save_name not in (None, False):
        if isinstance(save_name, str):
            save_name = meta_config.PICKLE_PATH + save_name
            if not is_pickle(save_name):
                save_name += "." + meta_config.PICKLE_DATATYPE
            with open(str(save_name), 'wb') as f:
                pickle.dump(return_value, f, meta_config.PICKLE_PROTOCOL)
                logger.info(str(return_value) + " pickled to " + save_name)
        else:
            logger.error("Could not pickle data, name for file (" +
                         str(save_name) + ") is not a string!" +
                         "\n Therefore, the following data was only returned" +
                         " but not saved! \n Data:" + str(return_value))
    return return_value


def try_unpickle(file_to_unpickle):
    """Try to unpickle a file and return, otherwise just return input"""
    if is_pickle(file_to_unpickle):
        with open(meta_config.PICKLE_PATH + file_to_unpickle, 'rb') as f:
            file_to_unpickle = pickle.load(f)
    return file_to_unpickle


if __name__ == '__main__':
    print "running selftest"

    print "selftest completed!"
