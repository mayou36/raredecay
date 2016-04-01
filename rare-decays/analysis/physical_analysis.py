# -*- coding: utf-8 -*-
"""
Created on Sat Mar 26 16:49:45 2016

@author: mayou

Contains the different run-modes for the machine-learning algorithms.
"""
import ml_analysis
import config as cfg

def run(runmode):
    """select the right runmode from the parameter and run it"""
    print "1,2,3..."
    _test1()




def _test1():
    print "starting physical module test"
    ml_ana = ml_analysis.MachineLearningAnalysis()
    gb_reweighter = ml_ana.reweight_mc_real(meta_cfg=cfg.reweight_meta_cfg, **cfg.reweight_cfg)
    gb_weights = ml_ana.reweight_weights(cfg.reweight_cfg.get('reweight_data_mc'), gb_reweighter)
    bins_reweighter = ml_ana.reweight_mc_real(meta_cfg=cfg.reweight_meta_cfg_bins, **cfg.reweight_cfg_bins)
    bins_weights = ml_ana.reweight_weights(cfg.reweight_cfg.get('reweight_data_mc'), bins_reweighter)
    #new_weights = ml_ana.reweight_weights(cfg.reweight_cfg.get('reweight_data_mc'), "reweighter1.pickl.pickle")

    ml_ana.draw_distributions([cfg.reweight_cfg.get('reweight_data_mc'),
                              cfg.reweight_cfg.get('reweight_data_real')],
                              labels=['mc', 'real'])
    ml_ana.draw_distributions([cfg.reweight_cfg.get('reweight_data_mc'),
                              cfg.reweight_cfg.get('reweight_data_real')],
                              weights=gb_weights,
                              labels=['mc gb_reweighter', 'real'])
    ml_ana.draw_distributions([cfg.reweight_cfg.get('reweight_data_mc'),
                              cfg.reweight_cfg.get('reweight_data_real')],
                              weights=bins_weights,
                              labels=['mc bins_reweighter', 'real'])


def _test2():
    pass
# temporary:
if __name__ == '__main__':
    run(1)
