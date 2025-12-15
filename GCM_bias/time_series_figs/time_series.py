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

# models with highest and lowest precipitation ratios showing change from the historical to the future period
H_models = ['UKESM1-0-LL', 'ACCESS-CM2', 'CanESM5', 'KACE-1-0-G']
L_models = ['MPI-ESM1-2-LR', 'CNRM-ESM2-1', 'CNRM-CM6-1-HR']

# read out the dictionary from the .txt file
import ast

# Open and read the file
bp.os.chdir('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/GCM_bias/')
with open('gcm_dict_dec_15.txt', 'r') as f: # saved before MIROC6
    contents = f.read()

# Convert from string representation to actual dictionary
gcm_dict = ast.literal_eval(contents)

with open('gmet_JJA_dict.txt', 'r') as f: # saved before MIROC6
    contents = f.read()

# Convert from string representation to actual dictionary
gmet_dict = ast.literal_eval(contents)


#%%
precip_bias = []
for model in MACA_models:
    precip_bias.append([model, gcm_dict[model]['summer_bias']['pr']])

# largest precip bias
 # ['INM-CM4-8', 1.9595805448057724],
 # ['INM-CM5-0', 2.2968416184085014],
 # ['MRI-ESM2-0', 1.9422929778067248]
 
# smallest precip bias
 # ['KACE-1-0-G', 0.4614887857109568],
 # ['MPI-ESM1-2-HR', 0.40737524414524856],
 # ['MPI-ESM1-2-LR', 0.3398679961281793],
 
 
#%%
# models with the smallest precipitation bias
x_obs = list(range(1979, 2015))
x_model = list(range(1979, 2100))
variable = 'pr'

y = [gmet_dict[year][variable] for year in range(1979, 2015)]
bp.plt.plot(x_obs, y, color = 'red', label = 'Observation')

for model, color in zip(('KACE-1-0-G', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR'), ('blue', 'green', 'orange')):
    y = [gcm_dict[model]['JJA_avg'][year][variable] for year in range(1979, 2100)]
    bp.plt.plot(x_model, y, color = color, label = model)
    
bp.plt.xlabel('Year')
bp.plt.ylabel('Precipitation (mm)')
bp.plt.legend()


#%%
# models with the largest precipitation bias
x_obs = list(range(1979, 2015))
x_model = list(range(1979, 2100))
variable = 'pr'

y = [gmet_dict[year][variable] for year in range(1979, 2015)]
bp.plt.plot(x_obs, y, color = 'red', label = 'Observation')

for model, color in zip(['INM-CM4-8', 'INM-CM5-0', 'MRI-ESM2-0'], ('blue', 'green', 'orange')):
    y = [gcm_dict[model]['JJA_avg'][year][variable] for year in range(1979, 2100)]
    bp.plt.plot(x_model, y, color = color, label = model)
    
bp.plt.xlabel('Year')
bp.plt.ylabel('Precipitation (mm)')
bp.plt.legend()

#%%
# models with the smallest precipitation ratio
x_obs = list(range(1979, 2015))
x_model = list(range(1979, 2100))
variable = 'pr'

y = [gmet_dict[year][variable] for year in range(1979, 2015)]
bp.plt.plot(x_obs, y, color = 'red', label = 'Observation')

for model, color in zip(L_models, ('blue', 'green', 'orange')):
    y = [gcm_dict[model]['JJA_avg'][year][variable] for year in range(1979, 2100)]
    bp.plt.plot(x_model, y, color = color, label = model)
    
bp.plt.xlabel('Year')
bp.plt.ylabel('Precipitation (mm)')
bp.plt.legend()


#%%
# models with the largest precipitation ratio
x_obs = list(range(1979, 2015))
x_model = list(range(1979, 2100))
variable = 'pr'

y = [gmet_dict[year][variable] for year in range(1979, 2015)]
bp.plt.plot(x_obs, y, color = 'red', label = 'Observation')

for model, color in zip(H_models, ('blue', 'green', 'orange')):
    y = [gcm_dict[model]['JJA_avg'][year][variable] for year in range(1979, 2100)]
    bp.plt.plot(x_model, y, color = color, label = model)
    
bp.plt.xlabel('Year')
bp.plt.ylabel('Precipitation (mm)')
bp.plt.legend()

    