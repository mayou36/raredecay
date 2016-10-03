# -*- coding: utf-8 -*-
"""
Created on Wed Jul 13 14:21:16 2016

@author: mayou
"""
from __future__ import division, absolute_import

import math as mt
import numpy as np

from raredecay.tools import data_storage
import raredecay.analysis.ml_analysis as ml_ana
from raredecay.globals_ import out



def rnd_dist():
    """Test reweighting by classify several random distributions. Not yet
    known how to interpret outcome correctly"""
    pass


def train_similar(mc_data, real_data, n_checks=10, n_folds=10, clf='xgb',
                  test_max=True, old_mc_weights=1, test_predictions=False,
                  clf_pred='rdf', make_plots=True):
    """Score for reweighting. Train clf on mc reweighted/real, test on real.
    Minimize score.

    Enter two datasets and evaluate the score described below. Return a
    dictionary containing the different scores. The test_predictions is
    another scoring, which is built upon the train_similar method.

    Scoring method description
    --------------------------

    **Idea**:
    A clf is trained on the reweighted mc as well as on the real data of a
    certain decay. Therefore, the classifier learns to distinguish between
    Monte-Carlo data and real data. Then we let the classifier predict some
    real data (an unbiased test set) and see, how many he is able to classify
    as real events. The lower the score, the less differences he was able to
    learn from the train data therefore the more similar the train data
    therefore the better the reweighting.

    **Advandages**: It is quite difficult to cheat on this method. Most of all
    it is robust to single high-weight events (which mcreweighted_as_real is
    not) and, in general, seems to be the best scoring so far.

    **Disadvantages**: If you insert a gaussian shaped 1.0 as mc and a gaussian
    shaped 1.1 as real, the score will be badly (around 0.33). So far, this was
    only observed for "artificial" distributions (even dough, of course, we
    do not know if it affects real distributions aswell partly)

    Output explanation
    ------------------
    The return is a dictionary containing several values. Of course, only the
    values, which are set to be evaluated, are contained. The keys are:

    - '**score**' : The average of all train_similar scores (as we use KFolding,
      there will be n_folds scores). *The* score.
    - '**score_std**' : The std of a single score, just for curiosity
    - '**score_max**' : The (average of all) "maximum" score. Actually the
      train_similar score but
      with mc instead of *reweighted* mc. Should be higher then the
      reweighted score.
    - '**score_max_std**' : The std of a single score, just for curiosity
    - '**score_pred**' : The score of the test_predictions method.
    - '**score_mc_pred**' : The score of the test_predictions method but on the
      predictions of the mc instead of the *reweighted* mc.

    Parameters
    ----------
    mc_data : HEPDataStorage
        The reweighted Monte-Carlo data, assuming the new weights are applied
        already.
    real_data : HEPDataStorage
        The real data
    n_checks : int >= 1
        Number of checks to perform. Has to be <= n_folds
    n_folds : int > 1
        Number of folds the data will be split into
    clf : str
        The name of a classifier to be used in
        :py:func:`~raredecay.analysis.ml_analysis.classify`.
    test_max : boolean
        If true, test for the "maximum value" by training also on mc/real
        (instead of *reweighted* mc/real)
        and test on real. The score for only mc should be higher than for
        reweighted mc/real. It *should* most probably but does not have to
        be!
    old_mc_weights : array-like or 1
        If *test_max* is True, the weights for mc before reweighting will be
        taken to be *old_mc_weights*, the weights the mc distribution had
        before the reweighting. The default is 1.
    test_predictions : boolean
        If true, try to distinguish the predictions. Advanced feature and not
        yet really discoverd how to interpret. Gives very high ROC somehow.
    clf_pred : str
        The classifier to be used to distinguish the predictions. Required for
        the *test_predictions*.

    Return
    ------
    out : dict
        A dictionary conaining the different scores. Description see above.

    """
    # initialize variables
    assert 1 <= n_checks <= n_folds and n_folds > 1, "wrong n_checks/n_folds. Check the docs"
    assert isinstance(mc_data, data_storage.HEPDataStorage), "mc_data wrong type:" + str(type(mc_data)) + ", has to be HEPDataStorage"
    assert isinstance(real_data, data_storage.HEPDataStorage), "real_data wrong type:" + str(type(real_data)) + ", has to be HEPDataStorage"
    assert isinstance(clf, str), "clf has to be a string, the name of a valid classifier. Check the docs!"

    output = {}

    scores = np.ones(n_checks)
    scores_max = np.ones(n_checks)  # required due to output of loop
    probas_mc = []
    probas_reweighted = []
    weights_mc = []
    weights_reweighted = []


    real_pred = []
    real_test_index = []
    real_mc_pred = []



    # initialize data
    real_data.make_folds(n_folds=n_folds)
    for fold in range(n_folds):
        real_train, real_test = real_data.get_fold(fold)
        real_test.set_targets(1)

        tmp_, scores[fold], pred_reweighted = ml_ana.classify(mc_data, real_train,
                                            validation=real_test, clf=clf, make_plots=make_plots,
                                            plot_title="train on mc reweighted/real, test on real",
                                            weights_ratio=1, get_predictions=True)
        probas_reweighted.append(pred_reweighted['y_proba'])
        weights_reweighted.append(pred_reweighted['weights'])

        real_pred.extend(pred_reweighted['y_pred'])
        real_test_index.extend(real_test.get_index())

        if test_max:
            temp_weights = mc_data.get_weights()
            mc_data.set_weights(1)
            tmp_, scores_max[fold], pred_mc = ml_ana.classify(mc_data, real_train, validation=real_test,
                                           plot_title="real/mc NOT reweight trained, validate on real",
                                           weights_ratio=1, get_predictions=True, clf=clf,
                                           make_plots=make_plots)
            mc_data.set_weights(temp_weights)
            probas_mc.append(pred_mc['y_proba'])
            weights_mc.append(pred_mc['weights'])

            real_mc_pred.extend(pred_mc['y_pred'])


    output['score'] = np.round(scores.mean(), 4)
    output['score_std'] = np.round(scores.std(), 4)

    out.add_output(["Score train_similar (recall, lower means better): ",
                    str(round(output['score'], 4)) + " +- " + str(round(output['score_std'], 4))],
                    # TODO: remove? not required actually: "Scores:", [round(i, 4) for i in scores]],
                    subtitle="Clf trained on real/mc reweight, tested on real")
    if test_max:
        output['score_max'] = np.round(scores_max.mean(), 4)
        output['score_max_std'] = np.round(scores_max.std(), 4)
        out.add_output(["No reweighting score: ", round(output['score_max'], 4),])

    if test_predictions:
        # test on the reweighted/real predictions
        real_data.set_targets(targets=real_pred, index=real_test_index)
        tmp_, score_pred = ml_ana.classify(real_data, target_from_data=True, clf=clf_pred,
                                           plot_title="train on predictions reweighted/real, real as target",
                                           weights_ratio=1, validation=n_checks, make_plots=make_plots)
        output['score_pred'] = round(score_pred, 4)

    if test_predictions and test_max:
        # test on the mc/real predictions
        real_data.set_targets(targets=real_mc_pred, index=real_test_index)
        tmp_, score_mc_pred = ml_ana.classify(real_data, target_from_data=True, clf=clf_pred,
                                              validation=n_checks,
                                              plot_title="mc not rew/real pred, real as target",
                                              weights_ratio=1, make_plots=make_plots)
        output['score_mc_pred'] = np.round(score_mc_pred, 4)

    return output


def punzi_fom(n_signal, n_background, n_sigma=5):
    """Return the Punzi Figure of Merit metric: S / (sqrt(B) + n_sigma/2)

    The Punzi FoM is mostly used for the detection of rare decays to prevent
    the metric of cutting off all the background and leaving us with only a
    very few signals.

    Parameters
    ----------
    n_signal : int
        Number of signals observed (= tpr; true positiv rate)
    n_background : int
        Number of background observed as signal (= fpr; false positiv rate)
    n_sigma : int or float

    """
    length = 1 if not hasattr(n_signal, "__len__") else len(n_signal)
    if length > 1:
        sqrt = np.sqrt(np.array(n_background))
        term1 = np.full(length, n_sigma/2)
    else:
        sqrt = mt.sqrt(n_background)
        term1 = n_sigma/2
    output = n_signal / (sqrt + term1)
    return output


def precision_measure(n_signal, n_background):
    """Return the precision measure: s / sqrt(s + b)"""
    length = 1 if not hasattr(n_signal, "__len__") else len(n_signal)
    if length > 1:
        sqrt = np.sqrt(np.array(n_signal + n_background))
    else:
        sqrt = mt.sqrt(n_signal + n_background)
    output = n_signal / sqrt
    return output