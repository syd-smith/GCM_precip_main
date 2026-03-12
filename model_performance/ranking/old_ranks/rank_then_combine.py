#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 22 09:16:21 2026

@author: u1301408
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
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


def rank_data(data, dict_name, dict_path, save = False):
    
    storage_dict = read_file(dict_name, dict_path)
    
    for variable in variables:
        for season in seasons:
            if variable == 'pr':
                obs = 1
            else:
                obs = 0
    
            bias = np.array([[name, data[name][season]['bias'][variable]] for name in models])
            var = np.array([[name, data[name][season]['var_ratio'][variable]] for name in models])
            
            # returns position of that data's percentile
            bias_percentile = np.array([[name, abs(float(value) - obs)] for name, value in bias])
            var_percentile = np.array([[name, abs(float(value) - 1)] for name, value in var])
            
            bias_order = bias_percentile[:, 1].astype(float).argsort()
            sorted_bias = bias_percentile[bias_order]
            
            var_order = var_percentile[:, 1].astype(float).argsort()
            sorted_var = var_percentile[var_order]

            for model in models:
                bias_val = int(np.where(sorted_bias[:, 0] == model)[0][0])
                var_val = int(np.where(sorted_var[:, 0] == model)[0][0])
                # lag_val = int(np.where(sorted_lag[:, 0] == model)[0][0])
                storage_dict[model][variable][season] = int(np.sum([bias_val, var_val]))
        
        if save == True:
            write2file(storage_dict, dict_name, dict_path)
                
    return storage_dict
               
# save_data = rank_data(data, 'rank_mar3.txt', '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/model_performance/ranking/', save = True)


def rank_calcs(dict_name, dict_path, variable = 'all'):
    
    dictionary = read_file(dict_name, dict_path)
                
    final = []
    if variable == 'all':
        for model in models:
            pr_total = [] 
            tasmin_total = []
            tasmax_total = []
            
            for season in seasons:
                pr_total.append(int(dictionary[model]['pr'][season]))
                tasmin_total.append(int(dictionary[model]['tasmin'][season]))
                tasmax_total.append(int(dictionary[model]['tasmax'][season]))
            
            pr_total = int(np.sum(pr_total))
            tasmin_total = int(np.sum(tasmin_total))
            tasmax_total = int(np.sum(tasmax_total))
            
            # weight the rankings so averagge temp is the same as precip
            final.append([model, float(np.average([pr_total, tasmin_total, tasmax_total], weights = [0.5, 0.25, 0.25]))])
                                
    else:
        for model in models:
            var_total = []
            for season in seasons:
                var_total.append(dictionary[model][variable][season])
            var_total = int(np.sum(var_total))
            final.append([model, float(var_total)])
                
    final_arr  = np.array(final)
    final_order = final_arr[:, 1].astype(float).argsort()
    sorted_final = final_arr[final_order]
        
    return sorted_final

grand_total = rank_calcs('rank_mar3.txt', '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/model_performance/ranking/')
pr = rank_calcs('rank_mar3.txt', '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/model_performance/ranking/', variable = 'pr')
tasmin = rank_calcs('rank_mar3.txt', '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/model_performance/ranking/', variable = 'tasmin')
tasmax = rank_calcs('rank_mar3.txt', '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/model_performance/ranking/', variable = 'tasmax')

df = pd.DataFrame([pr[:, 0], tasmin[:, 0], tasmax[:, 0], grand_total[:, 0]]).T
df.columns = ['Precipitation', 'Minimum Temperature', 'Maximum Temperature', 'Grand Total']

fig, ax = plt.subplots(figsize = (6, 2)) # Adjust size as needed
ax.axis('off') # Hide the axes

# Create the table and add it to the plot
table = ax.table(cellText = df.values, colLabels = df.columns, loc = 'center', cellLoc = 'center')
for (row, col), cell in table.get_celld().items():
    if row == 0: # This targets the header row
        cell.set_text_props(weight = 'bold', fontsize = 16)
