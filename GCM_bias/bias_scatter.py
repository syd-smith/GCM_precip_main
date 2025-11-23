#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 22 21:02:16 2025

@author: u1301408
"""

# first graph  x: precip change over time y: precip bias
# second graph x: temp change over time y: temp bias

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/packages')
import base_packages as bp

# list of all models used in the MACA downscaling process that have ssp585
MACA_models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5', 'EC-Earth3-CC',
 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'INM-CM4-8', 'INM-CM5-0',
 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']
    
# variables used in MACA downscaling process 
variables = ['pr', 'huss', 'tasmin', 'tasmax', 'rsds', 'uas', 'vas']
gridmet_variables = ['pr', 'rmax', 'rmin', 'sph', 'srad', 'tmmn', 'tmmx', 'uas', 'vas']

# read out the dictionary from the .txt file
import ast

# Open and read the file with temporal change information
bp.os.chdir('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/scatter_plot/')
with open('oct_19.txt', 'r') as f: # saved before MIROC6
    contents = f.read()

# Convert from string representation to actual dictionary
scatter_dict = ast.literal_eval(contents)

# Open and read the file with bias data
bp.os.chdir('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/GCM_bias/')
with open('nov_22.txt', 'r') as f: # saved before MIROC6
    contents = f.read()

# Convert from string representation to actual dictionary
bias_dict = ast.literal_eval(contents)


fig, axs = bp.plot.subplots(2, 2, figsize = (2, 2))

# loop through dictionary to pull out necessary data for scatter
for model in MACA_models:
    
    # adjust color of data point relative to PC value
    first = axs[0][0].scatter(scatter_dict[model]['ssp585']['precip_ratio'], 
                          bias_dict[model]['bias']['pr'], 
                          c = data_dict[model][scenario]['PC1'], 
                          cmap = bp.plt.get_cmap('viridis', 9), 
                          s = 100, 
                          norm = bp.mcolors.Normalize(vmin = -10, vmax = 18))
    second = axs[1][0].scatter(scatter_dict[model]['ssp585']['delta_temp'], 
                          bias_dict[model]['bias']['pr'], 
                          c = data_dict[model][scenario]['PC2'], 
                          cmap = bp.plt.get_cmap('viridis', 9), 
                          s = 100, 
                          norm = bp.mcolors.Normalize(vmin = -5, vmax = 6))
    third = axs[0][1].scatter(data_dict[model][scenario]['delta_temp'], 
                          data_dict[model][scenario]['precip_ratio'], 
                          c = data_dict[model][scenario]['PC1'], 
                          cmap = bp.plt.get_cmap('viridis', 9), 
                          s = 100, 
                          norm = bp.mcolors.Normalize(vmin = -10, vmax = 18))
    fourth = axs[1][1].scatter(data_dict[model][scenario]['delta_temp'], 
                          data_dict[model][scenario]['precip_ratio'], 
                          c = data_dict[model][scenario]['PC2'], 
                          cmap = bp.plt.get_cmap('viridis', 9), 
                          s = 100, 
                          norm = bp.mcolors.Normalize(vmin = -5, vmax = 6))
