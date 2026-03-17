#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 10:33:53 2026

@author: u1301408
"""

import numpy as np
from pathlib import Path
from scipy.stats import pearsonr
import sys 


# ==================================
# - Establish Relative File Path - 
# ==================================

current_file_directory = Path(__file__).resolve().parent
print(f'CURRENT FILE DIRECTORY: {current_file_directory}')
parent_directory = current_file_directory.parent
sys.path.append(str(parent_directory))

from tool_belt.file_traversing import read_file


# ===============
#  - Constants - 
# ===============

models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5',
          'EC-Earth3-AerChem', 'EC-Earth3-CC', 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4',
          'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'IITM-ESM', 'INM-CM4-8', 'INM-CM5-0', 'KACE-1-0-G', 'KIOST-ESM', 
          'MIROC-ES2H', 'MIROC-ES2L', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']

ssp585_models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1',
                 'CanESM5', 'EC-Earth3-CC', 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL',
                  'HadGEM3-GC31-MM', 'INM-CM4-8', 'INM-CM5-0', 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC6',
                   'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']

MACA_data = read_file('gcm_feb19.txt')

GSLB_data = read_file('oct_19.txt', parent_directory.join_path('JJA_climate_change'))



# Pearson R and P values of correlation between pr bias and var

GSLB = np.array([GSLB_data[model]['JJA']['bias']['pr'] for model in ssp585_models])
MACA =  np.array([MACA_data[model]['JJA']['var_ratio']['pr'] for model in ssp585_models])
values = pearsonr(bias, var)



# Pearson R and P values of correlation between pr bias and var
check = read_file('gcm_feb9.txt')
bias = np.array([check[model]['JJA']['bias']['pr'] for model in ssp585_models])
var =  np.array([check[model]['JJA']['var_ratio']['pr'] for model in ssp585_models])
values = pearsonr(bias, var)