#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  5 13:42:47 2026

@author: u1301408
"""

import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan, het_white
from scipy.stats import pearsonr

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/tool_belt/')
from file_traversing import write2file, read_file

sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/model_performance/correlation_matrix')
from seasonal_matrix import mk_df

# creates dataframe with summer data from ssp585  models
data = mk_df(['pr', 'tasmin', 'tasmax'], 'JJA', 'ssp585')

# defines the axes for each plot
x1 = 'pr bias'
x2 = 'pr var'
y = 'projected precip'

# initializes the ploting function outlining that there are two subplots
fig, axs = plt.subplots(1, 2, figsize = (12, 5))

###  plot #1 - pr bias vs. projected pr ###
m1, b1 = np.polyfit(data[x1], data[y]/100, 1) 
axs[0].plot(data[x1], m1*data[x1]+b1, '-', color  = 'red') # plot a regression  line
axs[0].scatter(data[x1], data[y]/100) # display both axes as a ratio
axs[0].set_xlabel('Precipitation Bias')
axs[0].set_ylabel('Projected Precipitation')
axs[0].text(0.03, 0.92, 'a.', transform = axs[0].transAxes, fontsize = 15)

### plot #2 - pr varriance ratio vs. projected pr ###
m2, b2 = np.polyfit(data[x2], data[y]/100, 1)
axs[1].plot(data[x2], m1*data[x2]+b2, '-', color  = 'red')
axs[1].scatter(data[x2], data[y]/100)
axs[1].set_xlabel('Precipitation Variance Ratio')
axs[1].set_ylabel('Projected Precipitation')
axs[1].text(0.03, 0.92, 'b.', transform = axs[1].transAxes, fontsize = 15)

#%%
ssp585_models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1',
                 'CanESM5', 'EC-Earth3-CC', 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL',
                  'HadGEM3-GC31-MM', 'INM-CM4-8', 'INM-CM5-0', 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC6',
                   'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']

# pull projected precipitation ratios for the GSL Basin from a dictionary
JJA_data = read_file('gcm_dict_dec_19.txt', '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/GCM_bias/')
study_region = []
for model in  ssp585_models:
    study_region.append(JJA_data[model]['pr_ratio'])
    
# find the corrrelation between projected prrecip over the GSL Basin vs. MACA region using pearsonr
values = pearsonr(study_region, data['projected precip'])
print(values)

# find the corrrelation between projected prrecip over the GSL Basin vs. MACA region using OLS
X = sm.add_constant(data['projected precip'])  # adds intercept
y = study_region

results = sm.OLS(y, X).fit()
print(results.summary())

#%%
# Breusch-Pagan test for heteroskedasticity on pr bias vs. projected pr
bias = sm.add_constant(data['pr bias'])
results = sm.OLS(data['projected precip'], bias).fit()
# print(results.summary())

residuals = results.resid
exog = results.model.exog

# Return order: LM value, LM p-value, F value,  F p-value
bp_test = het_breuschpagan(residuals, exog) 
white_test = het_white(residuals, exog)
# all findings were staatistically significant


