#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 24 08:07:37 2025

@author: u1301408
"""

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/packages')
import base_packages as bp

# list of all models used in the MACA downscaling process that have ssp585
MACA_models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5', 'EC-Earth3-CC',
 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'INM-CM4-8', 'INM-CM5-0',
 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']

# variables used in MACA downscaling process 
variables = ['pr', 'huss', 'tasmin', 'tasmax', 'rsds', 'uas', 'vas']

# read out the dictionary from the .txt file
import ast

# Open and read the file
bp.os.chdir('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/GCM_bias/')
with open('gcm_JJA_dict.txt', 'r') as f: # saved before MIROC6
    contents = f.read()

# Convert from string representation to actual dictionary
gcm_dict = ast.literal_eval(contents)

with open('gmet_JJA_dict.txt', 'r') as f: # saved before MIROC6
    contents = f.read()

# Convert from string representation to actual dictionary
gmet_dict = ast.literal_eval(contents)


#%%
x = list(range(1979, 2015))
variable = 'pr'

y = [gmet_dict[year][variable] for year in range(1979, 2015)]
bp.plt.plot(x, y, color = 'red', label = 'Observation')

for model, color in zip((MACA_models[-1], MACA_models[16], MACA_models[12]), ('blue', 'green', 'orange')):
    y = [gcm_dict[model][year][variable] for year in range(1979, 2015)]
    bp.plt.plot(x, y, color = color, label = model)
    
bp.plt.xlabel('Year')
bp.plt.ylabel('Precipitation (mm)')
bp.plt.legend()

#%%
x = list(range(1979, 2015))
variable = 'pr'

y = [gmet_dict[year][variable] for year in range(1979, 2015)]
bp.plt.plot(x, y, color = 'red', label = 'Observation')

for model, color in zip(['MPI-ESM1-2-LR', 'CNRM-ESM2-1', 'CNRM-CM6-1-HR'], ('blue', 'green', 'orange')):
    y = [gcm_dict[model][year][variable] for year in range(1979, 2015)]
    bp.plt.plot(x, y, color = color, label = model)
    
bp.plt.xlabel('Year')
bp.plt.ylabel('Precipitation (mm)')
bp.plt.legend()


    