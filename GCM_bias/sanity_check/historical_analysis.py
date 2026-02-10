#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  9 17:14:03 2026

@author: u1301408
"""


import matplotlib.colors as mcolors 
from matplotlib.colors import Normalize
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/tool_belt/')
from file_traversing import write2file, read_file

sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/GCM_bias/sanity_check/')
from taylor_per_season import data_build


models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5',
          'EC-Earth3-AerChem', 'EC-Earth3-CC', 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4',
          'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'IITM-ESM', 'INM-CM4-8', 'INM-CM5-0', 'KACE-1-0-G', 'KIOST-ESM', 
          'MIROC-ES2H', 'MIROC-ES2L', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']



def model_performance(variable, season, models, add_box = True, percentile = 50, model_to_label = 'SKIP'):
    
    bias, stdev = data_build(variable, season, models)
    
    fig, axs = plt.subplots(figsize =  (5, 5))
    axs.scatter(bias, stdev)
    
    if variable == 'pr' or variable == 'huss':
        ref_bias = 1
    else:
        ref_bias = 0
        
    axs.plot(ref_bias, 1, marker =  '*', markeredgecolor = 'black', markersize = 25, markerfacecolor  = 'none')
    
    if add_box == True:
        adjusted_bias = []
        adjusted_stdev = []
        for b, s in zip(bias, stdev):
            bias_distance = b - ref_bias
            stdev_distance = s - 1
            adjusted_bias.append(float(bias_distance))
            adjusted_stdev.append(float(stdev_distance))
    
        bias_percentile = np.percentile(adjusted_bias, percentile)
        stdev_percentile = np.percentile(adjusted_stdev, percentile)
        
        focus_area = Rectangle((ref_bias-bias_percentile, 1-stdev_percentile), bias_percentile*2, stdev_percentile*2, edgecolor = 'red', facecolor = 'none')
        axs.add_patch(focus_area)
    
    if model_to_label != 'SKIP':
        for model, color in zip(model_to_label, ['green', 'yellow', 'red']):
            index = models.index(model)
            axs.plot(float(bias[index]), float(stdev[index]), marker = 'o', markeredgecolor = 'black', 
                     markerfacecolor  = color, markersize = 10, label = model)
        fig.legend(loc = 'upper right', bbox_to_anchor = (1.3, 0.9))

    axs.set_yticks([0.5, 1, 1.5, 2, 2.5])
    axs.axvline(x = ref_bias, color = 'black', linewidth = 0.75, linestyle = ':', zorder = 0)
    axs.axhline(y = 1, color = 'black', linewidth = 0.75, linestyle = ':', zorder = 0)
    
    return fig, axs

face, bones = model_performance('huss', 'yearly', models, add_box = False)




