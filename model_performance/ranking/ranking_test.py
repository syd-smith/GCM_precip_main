#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 09:45:29 2026

@author: u1301408
"""

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

dict_name = 'rank_mar3.txt'
dict_path = '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/model_performance/ranking/' 
variable = 'tasmin'


storage_dict = read_file(dict_name, dict_path)

bias_totals = []
var_totals = []

for name in models:
    # print(name)
    if variable == 'pr':
        obs = 1
    else:
        obs = 0
        
    annual_bias = []
    annual_var = []
    
    for season in seasons:

        bias = float(data[name][season]['bias'][variable])
        # print(bias, abs(float(bias) - obs))
        var = float(data[name][season]['var_ratio'][variable])
        # print(var, abs(float(var) - 1))
        
        # returns position of that data's percentile
        annual_bias.append(abs(float(bias) - obs))
        annual_var.append(abs(float(var) - 1))
        
    bias_totals.append([name, float(np.sum(annual_bias))])
    var_totals.append([name, float(np.sum(annual_var))])
    
sorted_bias = sorted(bias_totals, key = lambda x: float(x[1]))
sorted_var = sorted(var_totals, key = lambda x: float(x[1]))




#%%
def rank_data(data, dict_name, dict_path, variable):
    
    storage_dict = read_file(dict_name, dict_path)

    bias_totals = []
    var_totals = []

    for name in models:
        # print(name)
        if variable == 'pr':
            obs = 1
        else:
            obs = 0
            
        annual_bias = []
        annual_var = []
        
        for season in seasons:

            bias = float(data[name][season]['bias'][variable])
            # print(bias, abs(float(bias) - obs))
            var = float(data[name][season]['var_ratio'][variable])
            # print(var, abs(float(var) - 1))
            
            # returns position of that data's percentile
            annual_bias.append(abs(float(bias) - obs))
            annual_var.append(abs(float(var) - 1))
            
        bias_totals.append([name, float(np.sum(annual_bias))])
        var_totals.append([name, float(np.sum(annual_var))])
        
    sorted_bias = sorted(bias_totals, key = lambda x: float(x[1]))
    sorted_var = sorted(var_totals, key = lambda x: float(x[1]))

    return np.array(sorted_bias), np.array(sorted_var)
               
bias, var = rank_data(data, 'rank_mar3.txt', '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/model_performance/ranking/', variable = 'pr')
#%%
    
pr_bias, pr_var = rank_data(data, 'rank_mar3.txt', '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/model_performance/ranking/', variable = 'pr')
pr = []
for model in models:
    bias_val = int(np.where(pr_bias[:, 0] == model)[0][0])
    var_val = int(np.where(pr_var[:, 0] == model)[0][0])
    pr.append([model, int(np.sum([bias_val, var_val]))])
pr = np.array(pr)
    
tasmin_bias, tasmin_var = rank_data(data, 'rank_mar3.txt', '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/model_performance/ranking/', variable = 'tasmin')
tasmin = []
for model in models:
    bias_val = int(np.where(tasmin_bias[:, 0] == model)[0][0])
    var_val = int(np.where(tasmin_var[:, 0] == model)[0][0])
    tasmin.append([model, int(np.sum([bias_val, var_val]))])
tasmin = np.array(tasmin)

tasmax_bias, tasmax_var = rank_data(data, 'rank_mar3.txt', '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/model_performance/ranking/', variable = 'tasmax')
tasmax = []
for model in models:
    bias_val = int(np.where(tasmax_bias[:, 0] == model)[0][0])
    var_val = int(np.where(tasmax_var[:, 0] == model)[0][0])
    tasmax.append([model, int(np.sum([bias_val, var_val]))])
tasmax = np.array(tasmax)

grand_total = []
for model in models:
    pr_val = int(np.where(pr[:, 0] == model)[0][0])
    tasmin_val = int(np.where(tasmin[:, 0] == model)[0][0])
    tasmax_val = int(np.where(tasmax[:, 0] == model)[0][0])
    grand_total.append([model, int(np.sum([pr_val, tasmin_val, tasmax_val]))])
grand_total = np.array(grand_total)

df = pd.DataFrame([pr[:, 0], tasmin[:, 0], tasmax[:, 0], grand_total[:, 0]]).T
