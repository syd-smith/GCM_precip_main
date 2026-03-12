#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 09:45:29 2026

@author: u1301408
"""

import matplotlib.patches as mpatches
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


def rank_data(data, dict_name, dict_path, variable, calc = 'both'):
    
    if calc == 'both':

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
    
    else:
        totals = []

        for name in models:
            if calc == 'bias':
                if variable == 'pr':
                    obs = 1
                else:
                    obs = 0
            else:
                obs = 1
                
            annual = []
            
            for season in seasons:

                season_calc = float(data[name][season][calc][variable])
                # print(bias, abs(float(bias) - obs))
                
                # returns position of that data's percentile
                annual.append(abs(float(season_calc) - obs))
                
            totals.append([name, float(np.sum(annual))])
            
        sorted_data = sorted(totals, key = lambda x: float(x[1]))
        
        return np.array(sorted_data)
               
# bias, var = rank_data(data, 'rank_mar3.txt', '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/model_performance/ranking/', variable = 'pr', calc = 'both')


def rmse(actual, predicted):
    return np.sqrt(np.mean((predicted - actual) ** 2))

def sort_data(variable, calc = 'both'):
    if calc == 'both':
        bias, var = rank_data(data, 'rank_mar3.txt', '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/model_performance/ranking/', variable = variable, calc = calc)
        values = []
        for model in models:
            bias_val = int(np.where(bias[:, 0] == model)[0][0])
            var_val = int(np.where(var[:, 0] == model)[0][0])
            values.append([model, int(np.sum([bias_val, var_val]))])
            
    else:
        sorted_data = rank_data(data, 'rank_mar3.txt', '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/model_performance/ranking/', variable = variable, calc = calc)
        values = []
        for model in models:
            val = int(np.where(sorted_data[:, 0] == model)[0][0])
            values.append([model, int(np.sum(val))])
            
    values = np.array(values)
    idx = np.argsort(values[:, 1].astype(float))
    sorted_values = np.array(values[idx])
    
    return sorted_values, idx

sorted_pr, pr_idx = sort_data('pr', calc = 'both')
sorted_tasmin, tasmin_idx = sort_data('tasmin', calc = 'both')
sorted_tasmax, tasmax_idx = sort_data('tasmax', calc = 'both')

def combine_variables(pr_data, tasmin_data, tasmax_data):
    grand_total = []
    for model in models:
        pr_val = int(np.where(pr_data[:, 0] == model)[0][0])
        tasmin_val = int(np.where(tasmin_data[:, 0] == model)[0][0])
        tasmax_val = int(np.where(tasmax_data[:, 0] == model)[0][0])
        grand_total.append([model, int(np.sum([pr_val, tasmin_val, tasmax_val]))])
        
    grand_total = np.array(grand_total)
    total_idx = np.argsort(grand_total[:, 1].astype(float))
    sorted_total = grand_total[total_idx]
    
    return sorted_total

sorted_total = combine_variables(sorted_pr, sorted_tasmin, sorted_tasmax)
    

def sorted_RMSE(comparison_data, actual_data, idx_order = None):
    error = []
    
    for model in models:
        val = float(np.where(comparison_data[:, 0] == model)[0][0])
        total_val = float(np.where(actual_data[:, 0] == model)[0][0])
        RMSE = rmse(float(val), float(total_val))
        error.append([str(model), int(RMSE)])
    error = np.array(error)  
    
    if idx_order is None:
        return error
    else: 
        sorted_error = error[idx_order]
        return sorted_error


pr_error = sorted_RMSE(sorted_pr, sorted_total, pr_idx)
tasmin_error = sorted_RMSE(sorted_tasmin, sorted_total, tasmin_idx)
tasmax_error = sorted_RMSE(sorted_tasmax, sorted_total, tasmax_idx)


df = pd.DataFrame([sorted_pr[:, 0], pr_error[:, 1], sorted_tasmin[:, 0], tasmin_error[:, 1], sorted_tasmax[:, 0], tasmax_error[:, 1], sorted_total[:, 0]]).T
df.columns = ['Pr', 'Pr RMSE', 'Tasmin', 'Tasmin RMSE', 'Tasmax', 'Tasmax RMSE', 'Grand Total']


### Create table to display dataframe ###
fig, ax = plt.subplots(figsize = (6, 2)) # Adjust size as needed
ax.axis('off') # Hide the axes

# Create the table and add it to the plot
table = ax.table(cellText = df.values, colLabels = df.columns, loc = 'center', cellLoc = 'center')

table.auto_set_font_size(False)
table.set_fontsize(4.5)

for (row, col), cell in table.get_celld().items():
    if row == 0: # This targets the header row
        cell.set_text_props(weight = 'bold', fontsize = 5)
        
        
#%%

### RMSE of individual calcs from combined ranking ###
bias_pr, bias_pr_idx = sort_data('pr', calc = 'bias')
pr_bias_error = sorted_RMSE(bias_pr, sorted_pr)
bias_tasmin, bias_tasmin_idx = sort_data('tasmin', calc = 'bias')
tasmin_bias_error = sorted_RMSE(bias_tasmin, sorted_tasmin)
bias_tasmax, bias_tasmax_idx = sort_data('tasmax', calc = 'bias')
tasmax_bias_error = sorted_RMSE(bias_tasmax, sorted_tasmax)

var_pr, var_pr_idx = sort_data('pr', calc = 'var_ratio')
pr_var_error = sorted_RMSE(var_pr, sorted_pr)
var_tasmin, var_tasmin_idx = sort_data('tasmin', calc = 'var_ratio')
tasmin_var_error = sorted_RMSE(var_tasmin, sorted_tasmin)
var_tasmax, var_tasmax_idx = sort_data('tasmax', calc = 'var_ratio')
tasmax_var_error = sorted_RMSE(var_tasmax, sorted_tasmax)


RMSE_df = pd.DataFrame([models, pr_bias_error[:, 1], pr_var_error[:, 1], tasmin_bias_error[:, 1], tasmin_var_error[:, 1], tasmax_bias_error[:, 1], tasmax_var_error[:, 1]]).T
RMSE_df.columns = ['Models', 'PR Bias', 'PR Var Ratio', 'TMIN Bias', 'TMIN Var Ratio', 'TMAX Bias', 'TMAX Var Ratio']


### Create table to display dataframe ###
fig, ax = plt.subplots(figsize = (6, 2)) # Adjust size as needed
ax.axis('off') # Hide the axes

# Create the table and add it to the plot
table = ax.table(cellText = RMSE_df.values, colLabels = RMSE_df.columns, loc = 'center', cellLoc = 'center')

table.auto_set_font_size(False)
table.set_fontsize(4.5)

for (row, col), cell in table.get_celld().items():
    if row == 0: # This targets the header row
        cell.set_text_props(weight = 'bold', fontsize = 5)

#%%

def model_search_table(model):
    search_df = pd.DataFrame([range(1, 28), bias_pr[:, 0], var_pr[:, 0], sorted_pr[:, 0], bias_tasmin[:, 0], var_tasmin[:, 0], sorted_tasmin[:, 0], bias_tasmax[:, 0], var_tasmax[:, 0], sorted_tasmax[:, 0], sorted_total[:, 0]]).T
    search_df.columns = ['', 'PR Bias', 'PR Var Ratio', 'PR Combined', 'TMIN Bias', 'TMIN Var Ratio', 'TMIN Combined', 'TMAX Bias', 'TMAX Var Ratio', 'TMAX Combined', 'Grand Total']
    
    fig, ax = plt.subplots(figsize = (6, 2)) # Adjust size as needed
    ax.axis('off') # Hide the axes
    
    # Create the table and add it to the plot
    table = ax.table(cellText = search_df.values, colLabels = search_df.columns, loc = 'center', cellLoc = 'center')
    
    table.auto_set_font_size(False)
    table.set_fontsize(3.2)
    
    for (row, col), cell in table.get_celld().items():
        if row == 0: # This targets the header row
            cell.set_text_props(weight = 'bold', fontsize = 3.2)
    
    for (i,j), cell in table.get_celld().items():
        text = str(cell.get_text().get_text()).strip()
    
        # Only highlight exact matches
        if text == model:
            cell.set_facecolor("#ffeb99")
        
    return fig


first = model_search_table('CNRM-ESM2-1')
# second = model_search_table('MRI-ESM2-0')
third = model_search_table('EC-Earth3')


# ranking is a bit arbitray but the grand total seems to be more representative of the center of the spread of uncertainty produced by the individual rankings

