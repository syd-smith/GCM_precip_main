#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  6 12:36:15 2026

@author: u1301408
"""

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/packages')
import base_packages as bp


# list of all models used in the MACA downscaling process that have ssp585
MACA_models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5', 'EC-Earth3-CC',
 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'INM-CM4-8', 'INM-CM5-0',
 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']

extreme_value_dict  = {}
for model in MACA_models:
    extreme_value_dict[model] = {}
    for time_period in ['Historical', 'Future', 'Ratio']:
        extreme_value_dict[model][time_period] = {}
        for keyz in ['10 year', '50 year', '100 year']:
            extreme_value_dict[model][time_period][keyz] = 'x'

#%%
fpath = '/uufs/chpc.utah.edu/common/home/u0660911/github/gslbip/return_levels.pkl'

with open(fpath, 'rb') as f:
    pickle_data = bp.pickle.load(f)
    
bp.pprint.pprint(pickle_data[0])

#%%
def return_levels(data):
    unused_data = []
    for position in range(0, 128):
        if data[position][1].endswith('ssp585_pr.nc'):
            no_prefix = data[position][1].replace('/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/output/netcdf/macav2metdata_GSLBIP_', '')
            model = no_prefix.split('_ssp')[0]
            
            extreme_value_dict[model][data[position][0]]['10 year'] = float(data[position][2])
            extreme_value_dict[model][data[position][0]]['50 year'] = float(data[position][3])
            extreme_value_dict[model][data[position][0]]['100 year'] = float(data[position][4])
        else:
            unused_data.append(data[position][1])
                
    return extreme_value_dict

test = return_levels(pickle_data)

#%%
def return_levels_ratio(dictionary):
    for model in MACA_models:
        for keyz in ['10 year', '50 year', '100 year']:
            dictionary[model]['Ratio'][keyz] = dictionary[model]['Future'][keyz] /  dictionary[model]['Historical'][keyz]

    return dictionary

dict_test = return_levels_ratio(extreme_value_dict)


#%%
# save dictionary containing data to a specified file (after running it through the functions below)
printer = bp.pprint.PrettyPrinter(indent = 3, width = 100, sort_dicts = True)
bp.os.chdir('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/GCM_bias/cor_matrix')

with open('pickle_dict_jan_6.txt', 'w') as f:
    f.write(printer.pformat(dict_test))
