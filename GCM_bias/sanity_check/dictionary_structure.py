#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 29 12:24:19 2026

@author: u1301408
"""

import pprint

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/tool_belt/')
from file_traversing import write2file, read_file


models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5',
          'EC-Earth3-AerChem', 'EC-Earth3-CC', 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4',
          'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'IITM-ESM', 'INM-CM4-8', 'INM-CM5-0', 'KACE-1-0-G', 'KIOST-ESM', 
          'MIROC-ES2H', 'MIROC-ES2L', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']

ssp585_models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1',
                 'CanESM5', 'EC-Earth3-CC', 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL',
                  'HadGEM3-GC31-MM', 'INM-CM4-8', 'INM-CM5-0', 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC6',
                   'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']

ssp370_models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5', 'EC-Earth3-AerChem',
                 'EC-Earth3-Veg-LR', 'GFDL-ESM4', 'INM-CM4-8', 'INM-CM5-0', 'KACE-1-0-G', 'MIROC-ES2H', 'MIROC-ES2L',
                  'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']

ssp245_models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5', 'EC-Earth3-CC',
                 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL', 'INM-CM4-8', 'INM-CM5-0',
                  'KACE-1-0-G', 'MIROC-ES2H', 'MIROC-ES2L', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']

ssp126_models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1',
                 'CanESM5', 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-ESM4', 'HadGEM3-GC31-LL', 'IITM-ESM',
                 'INM-CM4-8', 'INM-CM5-0', 'KACE-1-0-G', 'MIROC-ES2H', 'MIROC-ES2L', 'MIROC6', 'MPI-ESM1-2-HR',
                 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']


# variables used in MACA downscaling process 
variables = ['pr', 'huss', 'tasmin', 'tasmax', 'rsds', 'uas', 'vas']

# seasons to break out calculations into
seasons = ['DJF', 'MAM', 'JJA', 'SON', 'yearly']

ssps = ['ssp126', 'ssp245', 'ssp370', 'ssp585']

#%%
# create the framework for a gcm dictionary to evaluate model performance in historical period
gcm_dict = read_file('gcm_feb9.txt')


gcm_hist_dict = {}
for model in models:
    gcm_hist_dict[model] = {}
    for season in seasons:
        gcm_hist_dict[model][season] = {}
        gcm_hist_dict[model][season]['bias'] = {}
        gcm_hist_dict[model][season]['var_ratio'] = {}
        for variable in variables:
            gcm_hist_dict[model][season]['bias'][variable] = gcm_dict[model][season]['bias'][variable]
            print(f'{model}-{season}-bias-{variable}')
            gcm_hist_dict[model][season]['var_ratio'][variable] = 'x'
        for year in range(1979, 2015):
            gcm_hist_dict[model][season][year] = {}
            for variable in variables:
                gcm_hist_dict[model][season][year][variable] = gcm_dict[model][season][year][variable]

write2file(gcm_hist_dict, 'gcm_feb19.txt')

#%%
# create a dictionary framework for future projections of GCM data (change in variables from historical to future period)                
projections_dict = {}    
     
for ssp, list_name in zip(ssps, [ssp126_models, ssp245_models, ssp370_models, ssp585_models]):
    projections_dict[ssp] = {}
    for model in list_name:
        projections_dict[ssp][model] = {}
        for season in seasons:
            projections_dict[ssp][model][season] = {}
            for calc in ['precip_ratio', 'delta_tasmin', 'delta_tasmax']:
                projections_dict[ssp][model][season][calc] = 'x'

write2file(projections_dict, 'projections_feb3.txt')

#%%
gmet_dict = {}

for season in seasons:
    gmet_dict[season] = {}
    for year in range(1979, 2015):
        gmet_dict[season][year] = {}
        for variable in variables:
            gmet_dict[season][year][variable] = 'x'
            
            
#%%
lag_one_dict = {}

for model in models:
    lag_one_dict[model] = {}
    for season in seasons:
        lag_one_dict[model][season] = {}
        for variable in variables:
            lag_one_dict[model][season][variable] = {}
            lag_one_dict[model][season][variable]['lag_one'] = 'x'
            lag_one_dict[model][season][variable]['pvalue'] = 'x'
            
write2file(lag_one_dict, 'lag_one_feb22.txt')
            
pprint.pprint(lag_one_dict)


