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

data = read_file('gcm_feb19.txt')
lag_data = read_file('lag_one_feb23.txt')


ranking = {}

for model in models:
    ranking[model] = {}
    for variable in variables:
        ranking[model][variable] = {}
        for season in seasons:
            ranking[model][variable][season] = 'x'
#%%

for variable in variables:
    for season in seasons:

        bias = np.array([[name, data[name][season]['bias'][variable]] for name in models])
        var = np.array([[name, data[name][season]['var_ratio'][variable]] for name in models])
        # lag = np.array([[name, lag_data[name][season][variable]['lag_one_ratio']] for name in models])
        
        # returns position of that data's percentile
        bias_percentile = np.array([[name, abs(float(value) - 1)] for name, value in bias])
        var_percentile = np.array([[name, abs(float(value) - 1)] for name, value in var])
        # lag_percentile  = np.array([[name, abs(float(value) - 1)] for name, value in lag])
        
        
        bias_order = bias_percentile[:, 1].astype(float).argsort()
        sorted_bias = bias_percentile[bias_order]
        
        var_order = var_percentile[:, 1].astype(float).argsort()
        sorted_var = var_percentile[var_order]
        
        # lag_order = lag_percentile[:, 1].astype(float).argsort()
        # sorted_lag = lag_percentile[lag_order]
        
        seasonal_total = np.array([])
        for model in models:
            bias_val = int(np.where(sorted_bias[:, 0] == model)[0][0])
            var_val = int(np.where(sorted_var[:, 0] == model)[0][0])
            # lag_val = int(np.where(sorted_lag[:, 0] == model)[0][0])
            ranking[model][variable][season] = int(np.sum([bias_val, var_val]))
           
final = []            
for model in models:
    pr_total = [] 
    tasmin_total = []
    tasmax_total = []
    
    for season in seasons:
        pr_total.append(ranking[model]['pr'][season])
        tasmin_total.append(ranking[model]['tasmin'][season])
        tasmax_total.append(ranking[model]['tasmax'][season])
    
    pr_total = int(np.sum(pr_total))
    tasmin_total = int(np.sum(tasmin_total))
    tasmax_total = int(np.sum(tasmax_total))
    
    final.append([model, float(np.average([pr_total, tasmin_total, tasmax_total], weights = [0.5, 0.25, 0.25]))])
                        
final_arr  = np.array(final)
final_order = final_arr[:, 1].astype(float).argsort()
sorted_final = final_arr[final_order]


# with lag one
# array([['ACCESS-ESM1-5', '116.5'],
#        ['INM-CM4-8', '117.0'],
#        ['KACE-1-0-G', '132.0'],
#        ['MPI-ESM1-2-HR', '135.0'],
#        ['MPI-ESM1-2-LR', '138.25'],
#        ['MIROC-ES2L', '140.25'],
#        ['HadGEM3-GC31-LL', '143.0'],
#        ['EC-Earth3', '145.0'],
#        ['HadGEM3-GC31-MM', '148.25'],
#        ['EC-Earth3-CC', '148.5'],
#        ['GFDL-ESM4', '150.25'],
#        ['ACCESS-CM2', '152.0'],
#        ['CanESM5', '153.25'],
#        ['UKESM1-0-LL', '156.5'],
#        ['CNRM-CM6-1', '157.25'],
#        ['INM-CM5-0', '158.25'],
#        ['CNRM-CM6-1-HR', '160.75'],
#        ['CNRM-ESM2-1', '161.75'],
#        ['EC-Earth3-Veg-LR', '163.5'],
#        ['EC-Earth3-AerChem', '165.25'],
#        ['GFDL-CM4', '166.0'],
#        ['CMCC-ESM2', '170.25'],
#        ['KIOST-ESM', '181.5'],
#        ['MIROC6', '184.25'],
#        ['IITM-ESM', '185.75'],
#        ['MRI-ESM2-0', '189.75'],
#        ['MIROC-ES2H', '192.0']], dtype='<U32')


cs1 = ['EC-Earth3', '145.0']
cs2 = ['HadGEM3-GC31-LL', '143.0']
cs3 = ['KACE-1-0-G', '132.0']
cs4 = ['EC-Earth3', '145.0']
cs5 = ['KACE-1-0-G', '132.0']



# without lag one
# array([['INM-CM4-8', '66.25'],
#        ['HadGEM3-GC31-MM', '68.5'],
#        ['ACCESS-ESM1-5', '69.25'],
#        ['HadGEM3-GC31-LL', '84.0'],
#        ['MIROC-ES2L', '84.25'],
#        ['KACE-1-0-G', '87.25'],
#        ['UKESM1-0-LL', '88.25'],
#        ['CanESM5', '90.75'],
#        ['ACCESS-CM2', '92.75'],
#        ['EC-Earth3', '96.0'],
#        ['EC-Earth3-AerChem', '98.75'],
#        ['MPI-ESM1-2-LR', '102.5'],
#        ['GFDL-ESM4', '102.5'],
#        ['EC-Earth3-CC', '105.5'],
#        ['EC-Earth3-Veg-LR', '105.75'],
#        ['MPI-ESM1-2-HR', '108.25'],
#        ['INM-CM5-0', '113.25'],
#        ['CMCC-ESM2', '114.25'],
#        ['MIROC-ES2H', '115.75'],
#        ['GFDL-CM4', '117.5'],
#        ['CNRM-ESM2-1', '119.0'],
#        ['IITM-ESM', '120.25'],
#        ['CNRM-CM6-1', '121.0'],
#        ['MIROC6', '125.5'],
#        ['CNRM-CM6-1-HR', '129.0'],
#        ['KIOST-ESM', '138.5'],
#        ['MRI-ESM2-0', '143.5']], dtype='<U32')

cs1 = ['EC-Earth3', '96.0']
cs2 = ['HadGEM3-GC31-LL', '84.0']
cs3 = ['MIROC-ES2L', '84.25']
cs4 = ['EC-Earth3', '96.0']
cs5 = ['HadGEM3-GC31-LL', '84.0'] 