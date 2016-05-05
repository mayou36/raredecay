# -*- coding: utf-8 -*-
"""
Created on Sat Mar 26 16:49:45 2016

@author: mayou

Contains the different run-modes for the machine-learning algorithms.
"""
from __future__ import division, absolute_import

import importlib

import raredecay.meta_config


DEFAULT_CFG_FILE = dict(
    reweightCV='raredecay.run_config.reweight_cfg',
    simple_plot=None,
    test='raredecay.run_config.reweight1_comparison_cfg',
    reweight_comparison='raredecay.run_config.reweight1_comparison_cfg'
)


def run(run_mode, cfg_file=None):
    """select the right runmode from the parameter and run it"""

    if cfg_file is None:
        cfg_file = DEFAULT_CFG_FILE.get(run_mode, None)
        assert cfg_file is not None, "No (default) cfg-file found."
    raredecay.meta_config.run_config = cfg_file

    # import configuration-file
    cfg = importlib.import_module(raredecay.meta_config.run_config)

    # initialize
    from raredecay.globals_ import out
    out.initialize(logger_cfg=cfg.logger_cfg, **cfg.OUTPUT_CFG)
    out.add_output(["config file used", str(raredecay.meta_config.run_config)],
                    section="Configuration", obj_separator=" : ", to_end=True)

    # create logger
    from raredecay.tools import dev_tool
    logger = dev_tool.make_logger(__name__, **cfg.logger_cfg)

    out.make_me_a_logger()  # creates a logger inside of "out"
    out.add_output(cfg.run_message, title="Run: "+cfg.RUN_NAME, do_print=False,
                   subtitle="Comments about the run")

#==============================================================================
# Run initialized, start physical analysis
#==============================================================================

    if run_mode == "test":
        test(cfg, logger)
    if run_mode == "reweight_comparison":
        reweight_comparison(cfg, logger)
    if run_mode == "simple_plot":
        simple_plot(cfg, logger)
    if run_mode == "reweightCV":
        reweightCV(cfg, logger)
    else:
        raise ValueError("Runmode " + str(run_mode) + " not a valid choice")

#==============================================================================
# Run finished, finalize it
#==============================================================================
    out.finalize()

def test(cfg):
    """just a test-function"""
    print "empty"


def add_branch_to_rootfile(cfg, logger, root_data=None, new_branch=None,
                           branch_name=None):
    """Add a branch to a given rootfile"""

    from raredecay.tools import data_tools

    data_tools.add_to_rootfile(root_data, new_branch=new_branch,
                               branch_name=branch_name)


def reweightCV(cfg, logger, n_folds=2, n_checks=1):

    import raredecay.analysis.ml_analysis as ml_ana
    from raredecay.tools import data_tools, data_storage
    from raredecay.globals_ import out
    import matplotlib.pyplot as plt

    out.add_output("Starting the run 'reweightCV'", title="Reweighting Cross-Validated")
    # initialize variables
    n_checks = min([n_folds, n_checks])

    # initialize data
    reweight_real = data_storage.HEPDataStorage(**cfg.data.get('reweight_real'))
    reweight_mc = data_storage.HEPDataStorage(**cfg.data.get('reweight_mc'))
    reweight_real.make_folds(n_folds=n_folds)
    reweight_mc.make_folds(n_folds=n_folds)
    logger.info("Data created, starting folding")
    out.add_output(["Start reweighting cross-validated with", n_folds,
                    "split up the data and do", n_checks, "checks on it."],
                    subtitle="cross-validation", obj_separator=" ")
    for fold in range(n_checks):

        train_real, test_real = reweight_real.get_fold(fold)
        train_mc, test_mc = reweight_mc.get_fold(fold)
        print "lenght of train_mc", len(train_mc)
        train_real.plot(figure="Reweighter trainer, fold " + str(fold))
        train_mc.plot(figure="Reweighter trainer, fold " + str(fold))
        reweighter = ml_ana.reweight_mc_real(meta_cfg=cfg.reweight_meta_cfg,
                                             reweight_data_mc=train_mc,
                                             reweight_data_real=train_real,
                                             branches=cfg.branches, reweighter='gb')
        # TODO: attention, completely wrong redefinition for test purposes
#        test_mc, temp = reweight_mc.get_fold(fold+1)
#        test_real, temp = reweight_real.get_fold(fold+1)
        print "reweighting finished"
        # reweighter = ''  # load from pickle file
        plot1 = test_mc.plot(figure="Bevor reweighting, fold " + str(fold))
        out.save_fig(plot1)
        test_real.plot(figure="Bevor reweighting, fold " + str(fold))
        new_weights = ml_ana.reweight_weights(test_mc, reweighter,
                                              branches=cfg.branches)
        plt.figure("new weights")
        plt.hist(new_weights,bins=40, log=True)
        ml_ana.data_ROC(test_real, test_mc)
        test_mc.plot(figure="After reweighting, fold " + str(fold))
        test_real.plot(figure="After reweighting, fold " + str(fold))

        logger.info("fold " + str(fold) + "finished")


def simple_plot(cfg, logger):

    import raredecay.analysis.ml_analysis as ml_ana
    from raredecay.tools import data_storage
    real_no_sweights = data_storage.HEPDataStorage(**cfg.data.get('reweight_real_no_sweights'))
    reweight_real = data_storage.HEPDataStorage(**cfg.data.get('reweight_real'))
    reweight_mc = data_storage.HEPDataStorage(**cfg.data.get('reweight_mc'))



    reweight_real.plot(figure='sweights_vs_no_sweights')
    real_no_sweights.plot(figure='sweights_vs_no_sweights', plots_name='sweights versus no sweights')
    reweight_mc.plot(figure='mc_vs_real_no_sweights', plots_name='monte-carlo versus real no sweights')
    real_no_sweights.plot(figure='mc_vs_real_no_sweights', plots_name='monte-carlo versus real no sweights')


def reweight_comparison(cfg, logger):
    """

    """
    import matplotlib.pyplot as plt

    import raredecay.analysis.ml_analysis as ml_ana
    from raredecay.tools import data_storage
    from raredecay.globals_ import out

    # make data
    logger.info("Start with gb reweighter")
    reweight_mc = data_storage.HEPDataStorage(**cfg.data.get('reweight_mc'))
    reweight_real = data_storage.HEPDataStorage(**cfg.data.get('reweight_real'))
    # TODO: remove
    gb_reweighter = ml_ana.reweight_mc_real(reweight_data_mc=reweight_mc,
                                            reweight_data_real=reweight_real,
                                            #branches=['B_PT', 'nTracks', 'nSPDHits'
                                            #, 'h1_TRACK_TCHI2NDOF','B_ENDVERTEX_CHI2'
                                            #],
                                            reweighter='gb',
                                            meta_cfg=cfg.reweight_meta_cfg)
    #gb_reweighter = 'gb_reweighter1.pickle'
    ml_ana.reweight_weights(reweight_mc, #branches=['B_PT', 'nTracks', 'nSPDHits'
                                          #  , 'h1_TRACK_TCHI2NDOF','B_ENDVERTEX_CHI2'
                                           # ],
                            reweighter_trained=gb_reweighter)
    reweight_mc.plot2Dscatter('B_PT', 'nTracks', figure=2)
    reweight_real.plot2Dscatter('B_PT', 'nTracks', figure=2, color='r')
    gb_roc_auc = ml_ana.data_ROC(original_data=reweight_mc,
                                 target_data=reweight_real, curve_name="GB reweighted")
    plot1 = reweight_mc.plot(figure="gradient boosted reweighting",
                     plots_name="comparison real-target", hist_settings={'bins':20})
    reweight_real.plot(figure="gradient boosted reweighting", hist_settings={'bins':20})
    out.save_fig(plot1, file_format=['png', 'svg'], to_pickle=False)
    out.save_fig(plt.figure("Weights bg reweighter"))
    plt.hist(reweight_mc.get_weights(), bins=20)
    plt.figure("Big weights (>4) bg reweighter")
    plt.hist([i for i in reweight_mc.get_weights() if i > 4], bins=200)
    print "mc weights sum", str(reweight_mc.get_weights().sum())
    print "real weights sum", str(reweight_real.get_weights().sum())
    #plt.show()


#    logger.info("Start with bins reweighter")
#    reweight_mc = data_storage.HEPDataStorage(**cfg.data.get('reweight_mc'))
#    reweight_real = data_storage.HEPDataStorage(**cfg.data.get('reweight_real'))
#    logger.debug("plotted figure 2")
#    bins_reweighter = ml_ana.reweight_mc_real(reweight_data_mc=reweight_mc,
#                                            reweight_data_real=reweight_real,
#                                            reweighter='bins',
#                                            branches=['B_PT', 'nTracks', 'nSPDHits'
#                                            #, 'h1_TRACK_TCHI2NDOF'
#                                            ],
#                                            meta_cfg=cfg.reweight_meta_cfg_bins)
#    #bins_reweighter = 'bins_reweighter1.pickle'
#    ml_ana.reweight_weights(reweight_mc, bins_reweighter, branches=['B_PT', 'nTracks', 'nSPDHits'
#                                            #, 'h1_TRACK_TCHI2NDOF'
#                                            ],)
#    reweight_mc.plot(figure="binned reweighting",
#                     plots_name="comparison real-target")
#    reweight_real.plot(figure="binned reweighting")
#    bins_roc_auc = ml_ana.data_ROC(original_data=reweight_mc,
#                                   target_data=reweight_real, curve_name="Bins reweighted")
#    # plt.show()
#
#
#    logger.debug("starting with original")
#    reweight_mc = data_storage.HEPDataStorage(**cfg.data.get('reweight_mc'))
#    reweight_real = data_storage.HEPDataStorage(**cfg.data.get('reweight_real'))
#    original_roc_auc = ml_ana.data_ROC(original_data=reweight_mc,
#                                       target_data=reweight_real, curve_name="Original weights")
#    reweight_mc.plot(figure="no reweighting",
#                     plots_name="comparison real-target")
#    reweight_real.plot(figure="no reweighting")



# temporary:
if __name__ == '__main__':
    run(1)
