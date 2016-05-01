# -*- coding: utf-8 -*-
"""
Created on Thu Apr  7 22:10:29 2016

@author: mayou
"""
# debug
from __future__ import division, absolute_import

import copy
import warnings

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

from root_numpy import root2rec

try:
    from rep.data.storage import LabeledDataStorage
except ImportError:
    warnings.warn("Could not import parts from the REP repository. \
                  Some functions will be unavailable and raise errors")

from raredecay.tools import data_tools, dev_tool

import importlib
from raredecay import meta_config
cfg = importlib.import_module(meta_config.run_config)
modul_logger = dev_tool.make_logger(__name__, **cfg.logger_cfg)



class HEPDataStorage(object):
    """ A wrapper around pandas.DataFrame and an extension to the
    LabeledDataStorage.



    """
    __HIST_SETTINGS_DEFAULT = dict(
        bins=40,
        normed=True,
        alpha=0.5  # transparency [0.0, 1.0]
        )
    __figure_number = 0
    __figure_dic = {}

    def __init__(self, data, target=None, sample_weights=None, data_name=None,
                 data_name_addition=None, data_labels=None, add_label=False,
                 hist_settings=None, supertitle_fontsize=18, logger=None):
        """Initialize instance and load data

        Parameters
        ----------
        data : root-tree dict
            Dictionary which specifies all the information to convert a root-
            tree to an array. Directly given to :func:`~root_numpy.root2rec`
        .. note:: Will be also arrays or pandas DataFrame in the future
        target : list or 1-D array or int {0, 1}
            Labels the data for the machine learning. Usually the y.
        sample_weights : 1-D array
            Contains the weights of the samples
        .. note:: If None specified, 1 will be assumed for all.
        data_name : str
            | Name of the data, human-readable. Displayed in the title of \
            plots.
            | *Example: 'Bu2K1piee_mc', 'beta-decay_realData' etc.*
        data_name_addition : str
            | Additional remarks to the data, human readable. Displayed in \
            the title of plots.
            | *Example: 'reweighted', 'shuffled', '5 GeV cut applied' etc.*
        data_labels : dict with strings {column name: human readable name}
            | Human-readable names for the columns, displayed in the plot.
            | Dictionary has to contain the exact column (=branch) name of \
            the data
            | All not specified labels will be auto-labeled by the branch \
            name itself.
        add_label : boolean
            If true, the human-readable labels will be added to the branch name
            shows in the plot instead of replaced.
        hist_settings : dict
            Dictionary with the settings for the histogram plot function
            :func:`~matplotlip.pyplot.hist`
        supertitle_fontsize : int
            The size of the title of several subplots (data_name, _addition)
        """
        # initialize logger
        self.logger = modul_logger if logger is None else logger

        # initialize data
        self._data_pandas = None
        self._root_dict = data

        # data name
        self._name = (data_name, data_name_addition)

        # initialize targets
        self._target_label = target

        # data-labels human readable
        data_labels = {} if data_labels is None else data_labels
        self.add_label = add_label
        self._label_dic = {col: col for col in self._root_dict.get('branches')}
        self._label_dic.update(data_labels)

        # TODO: removeLine: self.data_name = data_name
        # define length of object
        temp_root_dict = copy.deepcopy(self._root_dict)
        temp_branch = temp_root_dict.pop('branches')  # remove to only use one branch
        temp_branch = dev_tool.make_list_fill_var(temp_branch)
        self._length = len(root2rec(branches=temp_branch[0], **temp_root_dict))

        # initialize weights
        if not dev_tool.is_in_primitive(sample_weights, None):
            assert len(sample_weights) == self._length
        self.weights = sample_weights

        # plot settings
        if dev_tool.is_in_primitive(hist_settings, None):
            hist_settings = self.__HIST_SETTINGS_DEFAULT
        self.hist_settings = hist_settings
        self.supertitle_fontsize = supertitle_fontsize

    def __len__(self):
        return self._length

# TODO: required to have them? data should not be an available attribute...
#    @property
#    def data(self):
#        raise IOError("Don't access data with my_data = HEPDataStorageInstance\
#                      .data. Use one of the built-in methods.")
#
#    @data.setter
#    def data(self):
#        raise IOError("You cannot set the data atribute manualy. Use a method\
#                      or the constructor")

    def get_rootdict(self):
        """Return the root-dictionary if available, else None"""
        return self._root_dict

    def get_weights(self, index=None, normalize=True):
        """Return the weights of the specified indeces or, if None, return all.

        Parameters
        ----------
        index: NotImplemented
            not yet implemented
        Return
        ------
        out: 1-D numpy array
            Return the weights in an array
        """
        if dev_tool.is_in_primitive(self.weights, (None, 1)):
            self.weights = dev_tool.fill_list_var([], len(self), 1)
        weights_out = data_tools.to_ndarray(self.weights)
        assert len(weights_out) == len(self), str("data and weights differ in lenght")
        if normalize:
            weights_out *= weights_out.size/weights_out.sum()
        return weights_out

    def set_weights(self, sample_weights):
        """Set the weights of the sample.

        Parameters
        ----------
        sample_weights : 1-D array or list or int {1}
            The new weights for the dataset.
        """
        assert (len(sample_weights) == len(self) or dev_tool.is_in_primitive(
                sample_weights, (None, 1)), "Invalid weights")
        self.weights = sample_weights

    def extend(self, branches, treename=None, filenames=None, selection=None):
        """Add the branches as columns to the data

        """
        warnings.warn("Function 'extend' not yet implemented")

    def pandasDF(self, branches=None, treename=None, filenames=None,
                 selection=None, index=None):
        """Convert the data to pandas or cut an already existing data frame and
        return

        Return a pandas DataFrame
        """
        if isinstance(branches, str):
            branches = [branches]
        temp_root_dict = {'branches': branches, 'treename': treename,
                          'filenames': filenames, 'selection': selection}
        for key, val in temp_root_dict.iteritems():
            if dev_tool.is_in_primitive(val, None):
                temp_root_dict[key] = self._root_dict.get(key)
        data_out = data_tools.to_pandas(temp_root_dict)
        if len(temp_root_dict['branches']) == 1:
            data_out.columns = temp_root_dict['branches']
        return data_out

    def get_labels(self, branches=None, as_list=False):
        """Return the labels of the data

        Parameters
        ----------
        branches : list with str or str
            The labels of the branches to return
        as_list : boolean
            If true, the labels will be returned as a list instead of a dict.
        Return
        ------
        out : list or dict
            Return a list or dict containing the labels.
        """
        if branches is None:
            branches = self._root_dict.get('branches')
        branches = dev_tool.make_list_fill_var(branches)
        if as_list:
            labels_out = [self._label_dic.get(col, col) for col in branches]
        else:
            labels_out = {key: self._label_dic.get(key) for key in branches}
        return dev_tool.make_list_fill_var(labels_out)

    def get_name(self):
        """Return the human-readable name of the data as a string"""
        # TODO: change into real name
        return "only test-string"

    def get_targets(self):

        if dev_tool.is_in_primitive(self._target_label, (0, 1, None)):
            # complicated? No! target_label could be array -> use any, all etc.
            if self._target_label is None:
                self.logger.warning("Target list consists of None")
            self._target_label = dev_tool.make_list_fill_var([], len(self),
                                                             self._target_label)
        if isinstance(self._target_label, list):
            self._target_label = np.array(self._target_label)
        assert len(self._target_label) == len(self), "Target has wrong lengths"
        return self._target_label

    def remove_data(self):
        """Remove data (columns, indices, labels etc.) from itself. Use only \
        if low on memory, otherwise use copy_data_partial

        """

    def copy_storage(self, branches=None):
        """Return a copy of self with only some of the columns (and therefore \
        labels etc).

        """
        branches = dev_tool.make_list_fill_var(branches)
        new_labels = {}
        if self._data_pandas is not None:
            return None
        else:
            new_root_dic = copy.deepcopy(self._root_dict)
            new_root_dic['branches'] = branches
            for column in branches:
                new_labels[column] = self._label_dic.get(column)
            new_storage = HEPDataStorage(new_root_dic, target=self.get_targets,
                                         sample_weights=self.get_weights(),
                                         data_labels=new_labels,
                                         add_label=self.add_label)
        return new_storage

    def get_LabeledDataStorage(self, random_state=None, shuffle=False):
        """Create and return an instance of class "LabeledDataStorage" from
        the REP repository

        Return
        ------
        out: LabeledDataStorage instance
            Return a Labeled Data Storage instance created with the data
        """
        new_lds = LabeledDataStorage(self.pandasDF(), target=self.get_targets(),
                                     sample_weight=self.get_weights(),
                                     random_state=random_state, shuffle=shuffle)
        return new_lds

    def plot(self, figure=None, branches=None, index=None, sample_weights=None,
             hist_settings=None, data_labels=None, log_y_axes=False,
             plots_name=None):
        """Draw histograms of the data.


        Parameters
        ----------
        figure : str or int
            The name of the figure. If the figure already exists, the plots
            will be plotted in the same window (can be intentional, for
            example to compare data)
        log_y_axes : boolean
            If True, the y-axes will be scaled logarithmically.
        plots_name:
            Additional, (to the *data_name* and *data_name_addition*), human-
            readable name for the plot.
        data_labels : dict
            Contain the column as key and the value as label

        """
        # update labels
        if dev_tool.is_in_primitive(data_labels, None):
            data_labels = {}
        data_labels = dict(self._label_dic, **data_labels)
        # update weights
        if dev_tool.is_in_primitive(sample_weights, None):
            sample_weights = self.get_weights()
        assert len(sample_weights) == len(self.get_weights()), str(
                "sample_weights is not the right lengths")
        # update hist_settings
        if dev_tool.is_in_primitive(hist_settings, None):
            hist_settings = {}
        if isinstance(hist_settings, dict):
            hist_settings = dict(self.__HIST_SETTINGS_DEFAULT, **hist_settings)
        data_plot = self.pandasDF(branches=branches, index=index)
        columns = data_plot.columns.values
        self.logger.debug("plot columns from pandasDataFrame: " + str(columns))
        # set the right number of rows and columns for the subplot
        subplot_col = int(math.ceil(math.sqrt(len(columns))))
        subplot_row = int(math.ceil(float(len(columns))/subplot_col))
        # assign a free figure if argument is None
        if dev_tool.is_in_primitive(figure, None):
            while True:
                safety = 0
                figure = self.__figure_number + 1
                self.__figure_number += 1
                assert safety < 5000, "stuck in an endless while loop"
                if figure not in self.__figure_dic.keys():
                    x_limits_col = {}
                    self.__figure_dic.update({figure: x_limits_col})
                    break
        elif figure not in self.__figure_dic.keys():
            x_limits_col = {}
            self.__figure_dic.update({figure: x_limits_col})
        out_figure = plt.figure(figure, figsize=(20, 30))
        # naming the plot. Ugly!
        temp_name = ""
        temp_first = False
        temp_second = False

    # TODO: change the ugly part to a nice method which takes all the strings
        if self._name[0] is not None:
            temp_name = str(self._name[0])
            temp_first = True
        if self._name[1] is not None:
            temp_name += " - " if temp_first else ""
            temp_name += str(self._name[1])
            temp_second = True
            label_name = copy.copy(temp_name)
        if plots_name is not None:
            temp_name += " - " if temp_first or temp_second else ""
            temp_name += str(plots_name)
        plt.suptitle(temp_name, fontsize=self.supertitle_fontsize)
        # plot the distribution column by column
        for col_id, column in enumerate(columns, 1):
            # only plot in range x_limits, otherwise the plot is too big
            x_limits = self.__figure_dic.get(figure).get(column, None)
            if dev_tool.is_in_primitive(x_limits, None):
                x_limits = np.percentile(np.hstack(data_plot[column]),
                                         [0.01, 99.99])
                self.__figure_dic[figure].update({column: x_limits})
            plt.subplot(subplot_row, subplot_col, col_id)
            temp1, temp2, patches = plt.hist(data_plot[column], weights=sample_weights, log=log_y_axes,
                     range=x_limits, label=label_name,#data_labels.get(column),
                     **hist_settings)
            plt.title(column)
        plt.legend()

        return out_figure

    def plot2Dscatter(self, x_branch, y_branch, dot_size=20, color='b', weights=None, figure=0):
        """Plots two branches against each other to see the distribution.

        """
        out_figure = plt.figure(figure)
        if isinstance(weights, (int, long, float)):
            weights = dev_tool.make_list_fill_var(weights, length=len(self),
                                                  var=weights)
        else:
            weights = self.get_weights()
        assert len(weights) == len(self), "Wrong length of weigths"
        size = [dot_size*weight for weight in weights]
        plt.scatter(self.pandasDF(branches=x_branch),
                    self.pandasDF(branches=y_branch), s=size, c=color,
                    alpha=0.5, label=self._name[0])
        plt.xlabel(self.get_labels(branches=x_branch, as_list=True))
        plt.ylabel(self.get_labels(branches=y_branch, as_list=True))
        plt.legend()

        return out_figure

# TODO: add correlation matrix










