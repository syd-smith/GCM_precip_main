#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 23 15:13:41 2026

@author: u1301408
"""

import numpy as np
import matplotlib.pyplot as plt
import statsmodels as sm

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/tool_belt/')
from file_traversing import write2file, read_file


models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5',
          'EC-Earth3-AerChem', 'EC-Earth3-CC', 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4',
          'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'IITM-ESM', 'INM-CM4-8', 'INM-CM5-0', 'KACE-1-0-G', 'KIOST-ESM', 
          'MIROC-ES2H', 'MIROC-ES2L', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']


gcm_dict =  read_file('gcm_feb19.txt')
gmet_dict = read_file('obs_feb3.txt')
lag_one  = read_file('lag_one_feb23.txt')

averages = []
for year in range(1979, 2015):
    averages.append(gmet_dict['JJA'][year]['tasmin'])
    
lag_one_calc, CI = sm.tsa.stattools.acf(averages, nlags = 1, alpha = 0.05)
magnitude = float(lag_one_calc[-1])
CI_lower = float(CI[-1, 0])
CI_upper = float(CI[-1, 1])

estimates = np.array([magnitude])
upper  =  np.array([CI_upper])
lower = np.array([CI_lower])

for model in models:
    estimates = np.append(estimates, lag_one[model]['JJA']['tasmin']['lag_one'])
    upper  = np.append(upper, lag_one[model]['JJA']['tasmin']['CI_upper'])
    lower = np.append(lower, lag_one[model]['JJA']['tasmin']['CI_lower'])

yerr = [estimates - lower,
        upper - estimates]


model_names = ["Model A", "Model B", "Model C", "Model D", "Model E"]

plt.figure()
plt.errorbar(estimates,
             np.arange(len(estimates)),
             xerr=[estimates - lower, upper - estimates],
             fmt='o',
             capsize=4)

models.insert(0, 'Observations')
plt.yticks(np.arange(len(estimates)), models)
plt.axvline(0, linestyle='--')
plt.title("Horizontal Confidence Interval Plot")
plt.show()