#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 22 13:24:14 2026

@author: u1301408
"""

import ast
import pprint
import os
import scipy.io
import numpy as np

MACA_models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5', 'EC-Earth3-CC',
 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'INM-CM4-8', 'INM-CM5-0',
 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']

# variables used in MACA downscaling process 
variables = ['pr', 'huss', 'tasmin', 'tasmax', 'rsds', 'uas', 'vas']

seasons = {'DJF':(11, 0, 1), 'MAM':(2, 3, 4), 'JJA':(5, 6, 7), 'SON':(8, 9, 10), 'yearly':tuple(range(0, 12))}

# # Open and read the file
# os.chdir('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/GCM_bias/sanity_check/ssp370')
# with open('ssp370_dict_jan_24.txt', 'r') as f:
#     contents = f.read()

# # Convert from string representation to actual dictionary
# gcm_dict = ast.literal_eval(contents)

#%%
# create the framework for a gcm dictionary
gcm_dict = {}

for model in MACA_models:
    gcm_dict[model] = {}
    for season in ['DJF', 'MAM', 'JJA', 'SON', 'yearly']:
        gcm_dict[model][season] = {}
        for calc in ('pr_ratio', 'tasmin_change', 'tasmax_change', 'avg', 'bias', 'stdev_ratio'):
            if calc in ('pr_ratio', 'tasmin_change', 'tasmax_change'):
                gcm_dict[model][season][calc] = 'x'
            elif calc == 'avg':
                gcm_dict[model][season][calc] = {}
                for year in range(1979, 2100):
                    gcm_dict[model][season][calc][year] = {}
                    for variable in variables:
                        gcm_dict[model][season][calc][year][variable] = 'x'
            else: 
                gcm_dict[model][season][calc] = {}
                for variable in variables:
                    gcm_dict[model][season][calc][variable] = 'x'
                
pprint.pprint(gcm_dict)
#%%  
def temporal_avg(save_variable, model, variable, season_name, season, hist_vs_fut, save = False):

    if hist_vs_fut ==  'historical':
        file_path = f'/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/coarse_grid/{model}_historical_{variable}.mat'
        time_period  = range(1979, 2015)
        num_o_years = range(0, 36)
    elif hist_vs_fut == 'future':
        file_path = f'/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/coarse_grid/{model}_ssp245_{variable}.mat'
        time_period = range(2015, 2100)
        num_o_years  =  range(0, 86)
    else:
        print('Time period not found.')
        
    # min and max latitudes and longitudes used in the MACA process
    lat_min, lat_max = 36.03, 42.98
    lon_min, lon_max = -115.1, -108.0

    # Load the .mat file
    mat_contents = scipy.io.loadmat(file_path)  

    # Print the contents of the .mat file
    # print("Contents of the .mat file:")

    # for key, value in mat_contents.items():
    #     if not key.startswith('__'):  # Skip metadata entries
    #         print(f"{key}")

    var = mat_contents['interpolated_data']  

    # convert precipitation from kg m-2 s-1 to mm
    if variable == 'pr':
       var *= 86400
       
    lat = np.squeeze(mat_contents['lat'])
    lon = np.squeeze(mat_contents['lon'])

    lat_mask = (lat >= lat_min) & (lat <= lat_max)
    lon_mask = (lon >= lon_min) & (lon <= lon_max)

    # output of (6, 8, 366, 36) -> (lat, lon, days in year, year)
    trimmed_var = var[np.ix_(lat_mask, lon_mask)]

    # number of days in each month based on the number of days in the year for that model
    ndays = trimmed_var.shape[2]
    if ndays == 366:
        days_in_month = np.array([31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
    elif ndays == 365:
        days_in_month = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
    elif ndays == 360:
        days_in_month = np.array([30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30])
    else:
        print(model)
        raise ValueError(f"Number of days in the year not found: ndays = {ndays}")

    # repeat the month number for the number of days in that month
    month_index = np.repeat(np.arange(1, 13), days_in_month)

    # define the shape of monthly_mean to be (12, 36) -> (month, year)
    nmonths = 12
    nyears = trimmed_var.shape[3]
    monthly_mean = np.empty((nmonths, nyears))

    # loop over months and give an average for each month across all of the lat, lon, and years
    for m in range(1, nmonths + 1):
        mask = (month_index == m)          # True for days in month m
        data_m = trimmed_var[:, :, mask, :]
        monthly_mean[m-1, :] = np.nanmean(data_m, axis = (0, 1, 2))

    # find the average for the summer months
    means = []
    for year, position in zip(time_period, num_o_years):  
        temporal_mean  = float(np.mean([monthly_mean[x, position] for x in season]))
        means.append(temporal_mean)
        if save == True:
            save_variable[model][season_name]['avg'][year][variable] = temporal_mean
            print(f"{temporal_mean} successfully saved to {model}, {variable}, {season_name}!")
            
    return means

temporal_avg(gcm_dict, MACA_models[0], variables[0], 'DJF', seasons['DJF'], 'historical')

# for model in MACA_models:
#     for variable in variables:
#         for season_name, season in seasons.items():
#             historical_avg(gcm_dict, model, variable, season_name, season,save = True)
            
#%%
# save dictionary containing data to a specified file (after running it through the functions below)
printer = pprint.PrettyPrinter(indent = 3, width = 100, sort_dicts = True)
os.chdir('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/GCM_bias/sanity_check/ssp370')

with open('ssp370_dict_jan_24.txt', 'w') as f:
    f.write(printer.pformat(gcm_dict))
        
        
        
        