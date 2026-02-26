#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 18 11:43:39 2025

@author: u1301408
"""


import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/packages')
import base_packages as bp
import ast

MACA_models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5', 'EC-Earth3-CC',
 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'INM-CM4-8', 'INM-CM5-0',
 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']

# Open and read the file
bp.os.chdir('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/GCM_bias')
with open('gcm_dict_dec_15.txt', 'r') as f:
    contents = f.read()

# Convert from string representation to actual dictionary
gcm_dict = ast.literal_eval(contents)


# not the best fit to the regression line, larger cluster around 100 for precip ratio and fewer models out to to the right
# most notable outliers: KACE_1-0-G, GFDL-ESM4

x = bp.np.array([])
y = bp.np.array([])

for model in MACA_models:
    x = bp.np.append(x, gcm_dict[model]['pr_ratio'])
    y  = bp.np.append(y, gcm_dict[model]['tasmin_change'])
    bp.plt.scatter(gcm_dict[model]['pr_ratio'], gcm_dict[model]['tasmin_change'])
    bp.plt.text(gcm_dict[model]['pr_ratio'], gcm_dict[model]['tasmin_change'], s = model)

m, b = bp.np.polyfit(x,  y, 1)
bp.plt.plot(x, m*x+b, '-', color  = 'red')

bp.plt.xlabel('Precip Ratio')
bp.plt.ylabel('Change in Minimium Temperature')


#%%

# loose fit to the regression line, generally has even spread minus an outlier of the left hand side
# most notable outlier: GFDL-ESM4

x = bp.np.array([])
y = bp.np.array([])

for model in MACA_models:
    x = bp.np.append(x, gcm_dict[model]['tasmax_change'])
    y  = bp.np.append(y, gcm_dict[model]['summer_bias']['tasmin'])
    bp.plt.scatter(gcm_dict[model]['tasmax_change'], gcm_dict[model]['summer_bias']['tasmin'])
    bp.plt.text(gcm_dict[model]['tasmin_change'], gcm_dict[model]['summer_bias']['tasmin'], s = model)

m, b = bp.np.polyfit(x,  y, 1)
bp.plt.plot(x, m*x+b, '-', color  = 'red')

bp.plt.xlabel('Change in Max Temperature')
bp.plt.ylabel('Bias in Minimium Temperature')


#%%

# loose fit to the regression line, almost funnel shaped with a wider mouth  on the  left and narrowing to the right

x = bp.np.array([])
y = bp.np.array([])

for model in MACA_models:
    x = bp.np.append(x, gcm_dict[model]['tasmin_change'])
    y  = bp.np.append(y, gcm_dict[model]['summer_bias']['tasmin'])
    bp.plt.scatter(gcm_dict[model]['tasmin_change'], gcm_dict[model]['summer_bias']['tasmin'])
    bp.plt.text(gcm_dict[model]['tasmin_change'], gcm_dict[model]['summer_bias']['tasmin'], s = model)

m, b = bp.np.polyfit(x,  y, 1)
bp.plt.plot(x, m*x+b, '-', color  = 'red')
    
bp.plt.xlabel('Change in Minimium Temperature')
bp.plt.ylabel('Bias in Minimium Temperature')

#%%

# nice, tight-fit linear regression with no notable outliers

x = bp.np.array([])
y = bp.np.array([])

for model in MACA_models:
    x = bp.np.append(x, gcm_dict[model]['tasmin_change'])
    y  = bp.np.append(y, gcm_dict[model]['tasmax_change'])
    bp.plt.scatter(gcm_dict[model]['tasmin_change'], gcm_dict[model]['tasmax_change'])
    bp.plt.text(gcm_dict[model]['tasmin_change'], gcm_dict[model]['tasmax_change'], s = model)

m, b = bp.np.polyfit(x,  y, 1)
bp.plt.plot(x, m*x+b, '-', color  = 'red')
    
bp.plt.xlabel('Change in Minimium Temperature')
bp.plt.ylabel('Change in Maximium Temperature')

#%%

# cluster of models with semi-linear regression however several outliers are pulling the data more positive than it should be
#  most notable outlier: KIOST_ESM

x = bp.np.array([])
y = bp.np.array([])

for model in MACA_models:
    x = bp.np.append(x, gcm_dict[model]['summer_bias']['tasmin'])
    y  = bp.np.append(y, gcm_dict[model]['summer_bias']['tasmax'])
    bp.plt.scatter(gcm_dict[model]['summer_bias']['tasmin'], gcm_dict[model]['summer_bias']['tasmax'])
    bp.plt.text(gcm_dict[model]['summer_bias']['tasmin'], gcm_dict[model]['summer_bias']['tasmax'], s = model)

m, b = bp.np.polyfit(x,  y, 1)
bp.plt.plot(x, m*x+b, '-', color  = 'red')
    
bp.plt.xlabel('Bias in Minimium Temperature')
bp.plt.ylabel('Bias in Maximium Temperature')


