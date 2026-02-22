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

sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/from_savanna/')
import nclcmaps as cmap

sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/GCM_bias/sanity_check/')
from taylor_per_season import data_build



models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5',
          'EC-Earth3-AerChem', 'EC-Earth3-CC', 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4',
          'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'IITM-ESM', 'INM-CM4-8', 'INM-CM5-0', 'KACE-1-0-G', 'KIOST-ESM', 
          'MIROC-ES2H', 'MIROC-ES2L', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']

ssp585_models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1',
                 'CanESM5', 'EC-Earth3-CC', 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL',
                  'HadGEM3-GC31-MM', 'INM-CM4-8', 'INM-CM5-0', 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC6',
                   'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']


def model_performance(variable, season, models, axs = None, add_box = True, percentile = 50, model_to_label = 'SKIP', coloring = False):
    """
    Uses bias and temporal variance data to build a Cartesian Taylor Diagram
    with bias on the x axis and the temporal variance ratio 
    (GCM variance/Obs variance) on the y axis. Each point on the plot represents
    a different model. A box can be added to represent the bounds of the 50th 
    percentile for both axes. Plot points can also be shaded by a model's
    projected increase in summer precipitation.
    """
    
    # extract data from dictionary
    bias, var = data_build(variable, season, models)
    
    # allow an axs to be passed to the function to integrate this into building subplots
    if axs == None:
        fig, axs = plt.subplots(figsize = (5, 5))
    else:
        fig = axs.figure
        
    # plot bias and standard deviation data on figure
    if coloring == False:
        axs.scatter(bias, var)
        points = 'No coloring shading specified.'
    else:
        data = read_file('projections_feb10.txt')
        projection = np.array([data['ssp585'][model][season]['precip_ratio'] for model in ssp585_models])
        levels = np.array([50, 65, 80, 95, 100, 105, 150, 190, 220])
        norm = mcolors.BoundaryNorm(levels, ncolors = plt.get_cmap(cmap.cmap('MPL_BrBG'), 8).N) 
        points = axs.scatter(bias, var, norm = norm, cmap = cmap.cmap('MPL_BrBG'), c = projection, edgecolor = 'k')

    # set bias of reference data based on variable
    if variable == 'pr' or variable == 'huss':
        ref_bias = 1
    else:
        ref_bias = 0
    
    # plot reference point as a black star
    axs.plot(ref_bias, 1, marker =  '*', markeredgecolor = 'black', markersize = 25, markerfacecolor  = 'none')
    
    # if selected, as a box to show what models perform at the defined percentile
    if add_box == True:
        # returns position of that dadta's percentile
        bias_percentile = np.percentile(abs(bias - ref_bias), percentile)
        var_percentile = np.percentile(abs(var - 1), percentile)
        
        # creates a box aroound models that perform at the percentile or higher in both datasets
        focus_area = Rectangle((ref_bias-bias_percentile, 1-var_percentile), bias_percentile*2, var_percentile*2, edgecolor = 'red', facecolor = 'none')
        axs.add_patch(focus_area)
    
    # highlights specific models on the plot
    if model_to_label != 'SKIP':
        for model, color in zip(model_to_label, ['green', 'yellow', 'red']):
            index = models.index(model)
            axs.plot(float(bias[index]), float(var[index]), marker = 'o', markeredgecolor = 'black', 
                     markerfacecolor  = color, markersize = 10, label = model)
        axs.legend(loc = 'upper left', bbox_to_anchor = (0.01, 0.99))

    # axs.set_yticks([0.5, 1, 1.5, 2, 2.5, 3, 3.5])
    # add line to show zero bias
    axs.axvline(x = ref_bias, color = 'black', linewidth = 0.75, linestyle = ':', zorder = 0)
    # add line to show where standard deviation is equal to reference data
    axs.axhline(y = 1, color = 'black', linewidth = 0.75, linestyle = ':', zorder = 0)
    
    return axs, points


bones, points = model_performance('pr', 'JJA', models)



