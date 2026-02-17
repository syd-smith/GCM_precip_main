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

sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/GCM_bias/sanity_check/correlation_matrix/')
from seasonal_matrix import mk_df

test = mk_df(['pr', 'tasmin', 'tasmax'], 'JJA', 'ssp585')

x1 = 'pr bias'
x2 = 'pr stdev'
y = 'projected precip'

fig, axs = plt.subplots(1, 2, figsize = (12, 5))

m1, b1 = np.polyfit(test[x1], test[y]/100, 1)
axs[0].plot(test[x1], m1*test[x1]+b1, '-', color  = 'red')
axs[0].scatter(test[x1], test[y]/100)
axs[0].set_xlabel('Precipitation Bias')
axs[0].set_ylabel('Projected Precipitation')
axs[0].text(0.03, 0.92, 'a.', transform = axs[0].transAxes, fontsize = 20)

m2, b2 = np.polyfit(test[x2], test[y]/100, 1)
axs[1].plot(test[x2], m1*test[x2]+b2, '-', color  = 'red')
axs[1].scatter(test[x2], test[y]/100)
axs[1].set_xlabel('Precipitation Standard Deviation Ratio')
axs[1].set_ylabel('Projected Precipitation')
axs[1].text(0.03, 0.92, 'b.', transform = axs[1].transAxes, fontsize = 20)

#%%
ssp585_models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1',
                 'CanESM5', 'EC-Earth3-CC', 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL',
                  'HadGEM3-GC31-MM', 'INM-CM4-8', 'INM-CM5-0', 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC6',
                   'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']

JJA_data = read_file('gcm_dict_dec_19.txt', '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/GCM_bias/')
study_region = []
for model in  ssp585_models:
    study_region.append(JJA_data[model]['pr_ratio'])
    
values = pearsonr(study_region, test['projected precip'])
print(values)

X = sm.add_constant(test['projected precip'])  # adds intercept
y = study_region

results = sm.OLS(y, X).fit()
print(results.pvalues)

#%%
plt.scatter(test['tasmax bias'], test['pr bias'])

#%%
bias = sm.add_constant(test['pr stdev'])
results = sm.OLS(test['projected precip'], bias).fit()
# print(results.summary())

residuals = results.resid
exog = results.model.exog

# Return order: LM value, LM p-value, F value,  F p-value
bp_test = het_breuschpagan(residuals, exog)
white_test = het_white(residuals, exog)


#%%
# model = sm.OLS(test['projected precip'], bias).fit(cov_type = 'HC3')
# model.get_robustcov_results(cov_type = 'HC3')
