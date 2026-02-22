#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 22 09:16:21 2026

@author: u1301408
"""
import numpy as np
import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/tool_belt/')
from file_traversing import write2file, read_file

models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5',
          'EC-Earth3-AerChem', 'EC-Earth3-CC', 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4',
          'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'IITM-ESM', 'INM-CM4-8', 'INM-CM5-0', 'KACE-1-0-G', 'KIOST-ESM', 
          'MIROC-ES2H', 'MIROC-ES2L', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']

seasons = ['DJF', 'MAM', 'JJA', 'SON']
variables = ['pr', 'tasmin', 'tasmax']

def ranking_system(models):
    # golf scoring
    data = read_file('gcm_feb19.txt')
    for variable in variables:
        for season in seasons:
            bias = np.array([[name, data[name][season]['bias'][variable]] for name in models])
            var = np.array([[name, data[name][season]['var_ratio'][variable]] for name in models])
            
            # returns position of that data's percentile
            bias_percentile = np.array([[name, abs(float(value) - 1)] for name, value in bias])
            var_percentile = np.array([[name, abs(float(value) - 1)] for name, value in var])

            
            bias_order = bias_percentile[:, 1].astype(float).argsort()
            sorted_bias = bias_percentile[bias_order]
            var_order = var_percentile[:, 1].astype(float).argsort()
            sorted_var = var_percentile[var_order]
            
            value = int(np.where(sorted_bias[:, 0] == model)[0][0])
