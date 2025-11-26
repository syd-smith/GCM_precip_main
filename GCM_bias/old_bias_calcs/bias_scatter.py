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

# Open and read the file with bias data
bp.os.chdir('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/GCM_bias/')
with open('nov_23.txt', 'r') as f: # saved before MIROC6
    contents = f.read()

# Convert from string representation to actual dictionary
bias_dict = ast.literal_eval(contents)


fig, axs = bp.plt.subplots(3, 3, figsize = (10, 10))

# loop through dictionary to pull out necessary data for scatter
for model in MACA_models:
    
    # adjust color of data point relative to PC value
    # row one
    row_one_first = axs[0][0].scatter(bias_dict[model]['pr_ratio'], 
                          bias_dict[model]['region_bias']['pr'], 
                          c = 'blue', 
                          s = 10)
    row_one_second = axs[0][1].scatter(bias_dict[model]['tasmin_change'], 
                          bias_dict[model]['region_bias']['pr'], 
                          c = 'blue', 
                          s = 10)
    row_one_third = axs[0][2].scatter(bias_dict[model]['tasmax_change'], 
                          bias_dict[model]['region_bias']['pr'], 
                          c = 'blue', 
                          s = 10)
    
    # row two
    row_two_first = axs[1][0].scatter(bias_dict[model]['pr_ratio'], 
                          bias_dict[model]['region_bias']['tasmin'], 
                          c = 'blue', 
                          s = 10)
    row_two_second = axs[1][1].scatter(bias_dict[model]['tasmin_change'], 
                          bias_dict[model]['region_bias']['tasmin'], 
                          c = 'blue', 
                          s = 10)
    row_two_third = axs[1][2].scatter(bias_dict[model]['tasmax_change'], 
                          bias_dict[model]['region_bias']['tasmin'], 
                          c = 'blue', 
                          s = 10)
    
    # row three
    row_three_first = axs[2][0].scatter(bias_dict[model]['pr_ratio'], 
                          bias_dict[model]['region_bias']['tasmax'], 
                          c = 'blue', 
                          s = 10)
    row_three_second = axs[2][1].scatter(bias_dict[model]['tasmin_change'], 
                          bias_dict[model]['region_bias']['tasmax'], 
                          c = 'blue', 
                          s = 10)
    row_three_third = axs[2][2].scatter(bias_dict[model]['tasmax_change'], 
                          bias_dict[model]['region_bias']['tasmax'], 
                          c = 'blue', 
                          s = 10)
