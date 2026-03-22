#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 10 12:26:44 2026

@author: u1301408
"""

from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.colors as mcolors 
import numpy as np
from pathlib import Path
import sys

# ==================================
# - Establish Relative File Path - 
# ==================================

current_file_directory = Path(__file__).resolve().parent
parent_directory = current_file_directory.parent
sys.path.append(str(parent_directory))

import from_savanna.nclcmaps as cmap
from model_performance.seasonal_taylor_diagram import data_build
from tool_belt.file_traversing import read_file


# ===============
#  - Constants - 
# ===============

models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5',
          'EC-Earth3-AerChem', 'EC-Earth3-CC', 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4',
          'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'IITM-ESM', 'INM-CM4-8', 'INM-CM5-0', 'KACE-1-0-G', 'KIOST-ESM', 
          'MIROC-ES2H', 'MIROC-ES2L', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']

ssp585_models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1',
                 'CanESM5', 'EC-Earth3-CC', 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL',
                  'HadGEM3-GC31-MM', 'INM-CM4-8', 'INM-CM5-0', 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC6',
                   'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']


# ==============
# - Functions - 
# ==============

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
        projection = np.array([data['ssp585'][model][season]['pr'] for model in ssp585_models])
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

def mixed_model_performance(season, models, coloring = False, box = False, percentile = 50, model_to_label = 'SKIP'):
    """
    Multi-pannel figure calling model_performance to display multiple variables at once.
    """
    
    # initialize figure with three subplots
    fig, axs  = plt.subplots(1, 3, figsize = (20, 5))
    
    # coloring refers to the color bar to show projected precipitation
    if coloring == True:
        # read out data and create structure for colorbar
        data = read_file('projections_feb10.txt')
        # create structure to color each points
        projection = np.array([data['ssp585'][model][season]['pr'] for model in ssp585_models])
        levels = np.array([50, 65, 80, 95, 100, 105, 150, 190, 220])
        norm = mcolors.BoundaryNorm(levels, ncolors = plt.get_cmap(cmap.cmap('MPL_BrBG'), 8).N)
        
    # call each individual plot from the model_performance function
    b, points = model_performance('pr', season, models, axs = axs[0], add_box = box, coloring = coloring, percentile = percentile, model_to_label = model_to_label)
    axs[0].set_ylabel('Precipitation Variance Ratio')
    axs[0].set_xlabel('Precipitation Bias Ratio')
    axs[0].text(0.05, 0.92, 'a.', transform = axs[0].transAxes, fontsize = 15)
    
    d, points = model_performance('tasmin', season, models, axs = axs[1], add_box = box, coloring = coloring, percentile = percentile, model_to_label = model_to_label)
    axs[1].set_ylabel('Minimum Temperature Variance Ratio')
    axs[1].set_xlabel('Minimum Temperature Bias (K)')
    axs[1].text(0.05, 0.92, 'b.', transform = axs[1].transAxes, fontsize = 15)
    
    f, points = model_performance('tasmax', season, models, axs = axs[2], add_box = box, coloring = coloring, percentile = percentile, model_to_label = model_to_label)
    axs[2].set_ylabel('Maximum Temperature Variance Ratio')
    axs[2].set_xlabel('Maximum Temperature Bias (K)')
    axs[2].text(0.05, 0.92, 'c.', transform = axs[2].transAxes, fontsize = 15)
    
    # actually adding the color bar based on structure from 
    if coloring == True:
        # create colorbar with shading to indicate percent change in projected precipitation 
        cbar = fig.colorbar(points, ax = axs, orientation = 'vertical', ticks = levels, pad = 0.02,extend = 'both', boundaries = levels)
        cbar.ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
    
    # add a single legend for all three subplots
    if model_to_label != 'SKIP':
        for ax in axs:
            if ax.get_legend() is not None:
                ax.get_legend().remove()
        
        # collect handles and labels from all subplots
        all_handles = []
        all_labels = []
        
        for ax in axs:
            handles, labels = ax.get_legend_handles_labels()
            all_handles.extend(handles)
            all_labels.extend(labels)
        
        # remove duplicates while preserving order
        from collections import OrderedDict
        by_label = OrderedDict(zip(all_labels, all_handles))
        
        # create shared legend
        fig.legend(
            by_label.values(),
            by_label.keys(),
            loc = 'upper center',
            bbox_to_anchor = (0.95, 0.88)
        )
    
    return fig, axs


# ================
# - Entry Point - 
# ================

def main():
    
    # shows the historical performance of CMIP6 models to gridMET (obs) for pr, tmin, tmax
    paper_fig = mixed_model_performance('JJA', ssp585_models, coloring = True)
    
    # example of model performance plot with box to show 50th percentile
    # for season in ['yearly', 'DJF', 'MAM', 'JJA', 'SON']:
    #     mixed_model_performance(season, models, box = True, model_to_label = ['UKESM1-0-LL', 'HadGEM3-GC31-LL', 'KACE-1-0-G'])
    
if __name__ == '__main__':
    main()







