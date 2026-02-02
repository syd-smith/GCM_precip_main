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
import glob
import xarray as xr

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


# variables used in MACA downscaling process 
variables = ['pr', 'huss', 'tasmin', 'tasmax', 'rsds', 'uas', 'vas']

seasons = {'DJF':[11, 0, 1], 'MAM':[2, 3, 4], 'JJA':[5, 6, 7], 'SON':[8, 9, 10], 'yearly':list(range(0, 12))}
obs_seasons = {'DJF':[12, 1,2], 'MAM':[3, 4, 5], 'JJA':[6, 7, 8], 'SON':[9, 10, 11], 'yearly':list(range(1, 13))}


#%%
gcm_dict =  read_file('gcm_hist_jan_27.txt')
def model_avg(save_variable, model, variable, season_name, season, save = False, future = False):

    if future == True:
        file_path = f'/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/coarse_grid/{model}_ssp245_{variable}.mat'
        time_period = range(2015, 2100)
        
    else:
        file_path = f'/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/coarse_grid/{model}_historical_{variable}.mat'
        time_period  = range(1979, 2015)
        
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
    for position, year in enumerate(time_period):  
        temporal_mean  = float(np.mean([monthly_mean[x, position] for x in season]))
        means.append(temporal_mean)
        if save == True:
            save_variable[model][season_name][year][variable] = temporal_mean
            print(f"{temporal_mean} successfully saved to {model}, {variable}, {season_name}!")
            
    return means

for model in models:
    for variable in variables:
        for season_name, season in seasons.items():
            model_avg(gcm_dict, model, variable, season_name, season, save = True)
    
# save point
write2file(gcm_dict, 'gcm_hist_jan_27.txt')
             

#%%
gmet_dict = read_file('obs_jan_28.txt')

def obs_avg(save_variable, variable, season_name, season, save = True):
    
    # convert varibale name for observational data file names
    if variable == 'tasmin':
         open_variable = 'tmmn'
         
    elif variable == 'tasmax':
         open_variable = 'tmmx'
         
    elif variable == 'huss':
         open_variable = 'sph'
         
    elif variable == 'rsds':
         open_variable = 'srad'
         
    else:
         open_variable = variable

    fpath = f'/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/gridmet/gsl_region_{open_variable}_1979-2014.nc'
    ds_open = xr.open_dataset(fpath)

    # convert variable name again for variables saved in the dataset
    if open_variable == 'pr':
         obs_variable ='precipitation_amount'
         
    elif open_variable == 'rmax' or variable == 'rmin':
         obs_variable = 'relative_humidity'
         
    elif open_variable == 'sph':
         obs_variable = 'specific_humidity'
         
    elif open_variable == 'srad':
         obs_variable = 'surface_downwelling_shortwave_flux_in_air'
         
    elif open_variable == 'tmmn' or open_variable == 'tmmx':
         obs_variable = 'air_temperature'
    else: 
         obs_variable = open_variable
         
         
    ds_season = ds_open[obs_variable].sel(day = ds_open[obs_variable].day.dt.month.isin(season))
    ds_year = ds_season.resample(day = 'YS').mean(dim = 'day', skipna = True)
    annual_means = ds_year.mean(dim = ('lat', 'lon'), skipna = True)
    values = annual_means.values
    
    # annual_means = annual_means_calc.values
    # da  = ds_open[obs_variable]   
     
    # year = da['day'].dt.year.values
    # month = da['day'].dt.month.values
    # da = da.assign_coords(year=('day', year), month=('day', month))

    # # now group by both at once using a tuple key
    # ds_var = da.groupby(['year', 'month'])
    # ds_mean = ds_var.mean('day')

    # means = []
    # for year in range(1979, 2015):
    #     monthly_means = []
    #     for month in season:
    #         monthly_mean = ds_mean.sel(year = year, month = month)
    #         monthly_means.append(monthly_mean)
    #     combine = xr.concat(monthly_means, dim = 'season')
    #     dat_point = float(np.mean(combine))
    #     means.append(dat_point)
        
    #     if save == True:
    #         save_variable[season_name][year][variable] = dat_point
     
    # ds_month = ds_open[obs_variable].sel(day = ds_open[obs_variable].day.dt.month.isin(season))
    # # ds_year = ds_month.resample(day='YS').mean(skipna=True)
    # ds_year = ds_month.groupby('day.year').mean(skipna = True, dim = ('day', 'lat', 'lon'))

    if save == True:
        # save data to dictionary
        for year, value in zip(range(1979, 2015), values):
            save_variable[season_name][year][variable] = float(value)
            print(f'{value} saved to {variable} in {year}.')

    return values

test = obs_avg(gmet_dict, 'pr', 'DJF', [12, 1, 2], save =  False)


#%%

# remaining_variables = ['huss', 'rsds', 'uas', 'vas']
# gmet_dict = read_file('obs_jan_28.txt')

for variable in variables:
    for season_name, season in obs_seasons.items():
        obs_avg(gmet_dict, variable, season_name, season, save = True)
        print(f'{season_name}, {variable} done!')
        
# save point        
write2file(gmet_dict, 'obs_jan_29.txt')

#%%
gcm_dict = read_file('gcm_jan_29.txt')
gmet_dict = read_file('obs_jan_28.txt')

def bias(save_variable, model, variable, season, save = True):
    
    # call GCM data from saved dictionary and take the average
    retrived_gcm_data =  []
    for year in range(1979, 2015):
        gcm_dat_point = gcm_dict[model][season][year][variable]
        retrived_gcm_data.append(int(gcm_dat_point))    
    gcm_avg = float(np.mean(retrived_gcm_data))

    # call gmet data from function and take the average
    retrived_gmet_data = []
    for year in range(1979, 2015):
        gmet_dat_point = gmet_dict[season][year][variable]
        retrived_gmet_data.append(int(gmet_dat_point))
    # print(set(type(x) for x in retrived_gmet_data))
    gmet_avg = float(np.mean(retrived_gmet_data))
    
    # calculate bias
    if variable == 'pr':
        bias = gcm_avg / gmet_avg
    else:
        bias = gcm_avg - gmet_avg
    
    if save == True:
        # save data to dictionary
        save_variable[model][season]['bias'][variable] = bias
    
    return bias
    
for model in models:
    for season in seasons.keys():
        for variable in ['pr', 'tasmin', 'tasmax']:
            bias(gcm_dict, model, variable, season)
            
# save point            
write2file(gcm_dict, 'gcm_jan_29.txt')

#%%
def stdev_ratio(save_variable, model, variable, season, save = True):
    
    # call GCM data from saved dictionary and take the average
    retrived_gcm_data =  []
    for year in range(1979, 2015):
        gcm_dat_point = gcm_dict[model][season][year][variable]
        retrived_gcm_data.append(int(gcm_dat_point))
    gcm_stdev = float(np.std(retrived_gcm_data))

    # call gmet data from function and take the average
    retrived_gmet_data = []
    for year in range(1979, 2015):
        gmet_dat_point = gmet_dict[season][year][variable]
        retrived_gmet_data.append(int(gmet_dat_point))
    gmet_stdev = float(np.std(retrived_gmet_data))
    
    stdev_ratio = gcm_stdev / gmet_stdev
    
    if save == True:
        # save data to dictionary
        save_variable[model][season]['stdev_ratio'][variable] = stdev_ratio
    
    return stdev_ratio

# test_stdev = stdev_ratio(MACA_models[0], variables[0])
for model in models:
    for season in seasons.keys():
        for variable in remaining_variables:
            stdev_ratio(gcm_dict, model, variable, season)  
            
# save point            
write2file(gcm_dict, 'gcm_jan_29.txt')


#%%
projections_dict = read_file('projections_jan_29.txt')
def fut_projection(model, emission_scenario, variable, save_variable, season_name, season, save = True):
    
    """
    Returns the change in a variable from the historical to future period to a nested 
    dictionary under the model name and emission scenario. 
    The average for the variable calculated is across all grid points in the given period.
    Save_variable should be the framework dictionary imported from dictionary_structure.py.
    """

    fpath = f'/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/output/netcdf/macav2metdata_GSLBIP_{model}_{emission_scenario}_{variable}.nc'
    open_ds = xr.open_dataset(fpath)
    
    # find the mean for the historical period
    hist_ds = open_ds[variable].sel(time = open_ds[variable].time.dt.month.isin(season))
    hist_means = []
    for year in range(1979, 2015):
        data_hist = hist_ds.sel(time = hist_ds.time.dt.year == year)
        hist_mean = data_hist.mean(skipna= True).item()
        hist_means.append(hist_mean)
        
    hist_val = float(np.mean(hist_means))
    
    # finds the mean for the future period
    fut_ds = open_ds[variable].sel(time = open_ds[variable].time.dt.month.isin(season))
    fut_means = []
    for year in range(2070, 2099):
        data_fut = fut_ds.sel(time = fut_ds.time.dt.year == year)
        fut_mean = data_fut.mean(skipna= True).item()
        fut_means.append(fut_mean)
    
    fut_val = float(np.mean(fut_means))    
        
    if variable == 'pr':
        projection = (fut_val/ hist_val) *100
        calculation = 'precip_ratio'
    else:
        # calulate change in temperature
        projection = fut_val - hist_val
        calculation = f'delta_{variable}'
    
    if save == True:
        save_variable[emission_scenario][model][season_name][calculation] = projection
        print(f'{projection} saved to {model}/{variable}/{season_name}!')
        
    return save_variable 

for model in ssp245_models:
    for variable in variables:
        for season_name, season in seasons.items():
            fut_projection(model, 'ssp245', variable, projections_dict, season_name, season)
        
write2file(projections_dict, 'projections_jan_29.txt')




