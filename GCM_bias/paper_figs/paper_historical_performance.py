#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 10 12:26:44 2026

@author: u1301408
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.colors as mcolors 
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
import numpy as np
from scipy.stats import pearsonr
import xarray as xr

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/tool_belt/')
from file_traversing import write2file, read_file

sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/GCM_bias/sanity_check/')
from historical_analysis import model_performance

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
        projection = np.array([data['ssp585'][model][season]['precip_ratio'] for model in ssp585_models])
        levels = np.array([50, 65, 80, 95, 100, 105, 150, 190, 220])
        norm = mcolors.BoundaryNorm(levels, ncolors = plt.get_cmap(cmap.cmap('MPL_BrBG'), 8).N)
        
    # call each individual plot from the model_performance function
    b, points = model_performance('pr', season, models, axs = axs[0], add_box = box, coloring = coloring, percentile = percentile, model_to_label = model_to_label)
    axs[0].set_ylabel('Precipitation Standard Deviation Ratio')
    axs[0].set_xlabel('Precipitation Bias Ratio')
    axs[0].text(0.05, 0.92, 'a.', transform = axs[0].transAxes, fontsize = 20)
    
    d, points = model_performance('tasmin', season, models, axs = axs[1], add_box = box, coloring = coloring, percentile = percentile, model_to_label = model_to_label)
    axs[1].set_ylabel('Minimum Temperature Standard Deviation Ratio')
    axs[1].set_xlabel('Minimum Temperature Bias (K)')
    axs[1].text(0.05, 0.92, 'b.', transform = axs[1].transAxes, fontsize = 20)
    
    f, points = model_performance('tasmax', season, models, axs = axs[2], add_box = box, coloring = coloring, percentile = percentile, model_to_label = model_to_label)
    axs[2].set_ylabel('Maximum Temperature Standard Deviation Ratio')
    axs[2].set_xlabel('Maximum Temperature Bias (K)')
    axs[2].text(0.05, 0.92, 'c.', transform = axs[2].transAxes, fontsize = 20)
    
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


# paper_fig = mixed_model_performance('JJA', ssp585_models, coloring = True)

for season in ['yearly', 'DJF', 'MAM', 'JJA', 'SON']:
    mixed_model_performance(season, models, box = True, model_to_label = ['UKESM1-0-LL', 'HadGEM3-GC31-LL', 'KACE-1-0-G'])

# winter = mixed_model_performance('DJF', models, box = True)
    


#%%

# Pearson R and P values of correlation between pr bias and stdev
check = read_file('gcm_feb9.txt')
bias = np.array([check[model]['JJA']['bias']['pr'] for model in ssp585_models])
stdev =  np.array([check[model]['JJA']['stdev_ratio']['pr'] for model in ssp585_models])
values = pearsonr(bias, stdev)

#%%

def fut_value(model, emission_scenario, variable, season_name, season):
    
    """
    Returns the change in a variable from the historical to future period to a nested 
    dictionary under the model name and emission scenario. 
    The average for the variable calculated is across all grid points in the given period.
    Save_variable should be the framework dictionary imported from dictionary_structure.py.
    """

    fpath = f'/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/output/netcdf/macav2metdata_GSLBIP_{model}_{emission_scenario}_{variable}.nc'
    open_ds = xr.open_dataset(fpath)
    
    # finds the mean for the future period
    fut_ds = open_ds[variable].sel(time = open_ds[variable].time.dt.month.isin(season))
    fut_means = []
    for year in range(2070, 2099):
        data_fut = fut_ds.sel(time = fut_ds.time.dt.year == year)
        fut_mean = data_fut.mean(skipna= True).item()
        fut_means.append(fut_mean)
    
    fut_val = float(np.mean(fut_means))    
        
    return fut_val


# pr units in mm

# Group 7 
print(f'UKESM1-0-LL, ssp370: {fut_value('UKESM1-0-LL', 'ssp370', 'pr', 'JJA', [5, 6, 7])}')
print(f'HadGEM3-GC31-LL, ssp585: {fut_value('HadGEM3-GC31-LL', 'ssp585', 'pr', 'JJA', [5, 6, 7])}')
print(f'KACE-1-0-G, ssp585: {fut_value('KACE-1-0-G', 'ssp585', 'pr', 'JJA', [5, 6, 7])}')

# Group 6
# print(f'EC-Earth3-AerChem, ssp370: {fut_value('EC-Earth3-AerChem', 'ssp370', 'pr', 'JJA', [5, 6, 7])}')
# print(f'EC-Earth3, ssp585: {fut_value('EC-Earth3', 'ssp585', 'pr', 'JJA', [5, 6, 7])}')
# print(f'EC-Earth3-CC, ssp585: {fut_value('EC-Earth3-CC', 'ssp585', 'pr', 'JJA', [5, 6, 7])}')

# Group 5
# print(f'KACE-1-0-G, ssp126: {fut_value('KACE-1-0-G', 'ssp126', 'pr', 'JJA', [5, 6, 7])}')
# print(f'KACE-1-0-G, ssp245: {fut_value('KACE-1-0-G', 'ssp245', 'pr', 'JJA', [5, 6, 7])}')
# print(f'MIROC-ES2L, ssp126: {fut_value('MIROC-ES2L', 'ssp126', 'pr', 'JJA', [5, 6, 7])}')

# print(f'CNRM-ESM2-1, ssp370: {fut_value('CNRM-ESM2-1', 'ssp370', 'tasmax', 'JJA', [5, 6, 7])}')
# print(f'HadGEM3-GC31-LL, ssp126: {fut_value('HadGEM3-GC31-LL', 'ssp126', 'tasmax', 'JJA', [5, 6, 7])}')



