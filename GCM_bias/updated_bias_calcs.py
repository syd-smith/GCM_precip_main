#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 25 20:28:47 2025

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


def gcm_yearly_avg(model, variable):
    
    file_path = f'/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/coarse_grid/{model}_historical_{variable}.mat'
    
    # min and max latitudes and longitudes
    lat_min, lat_max = 36.03, 42.98
    lon_min, lon_max = -115.1, -108.0
    
    # Load the .mat file
    mat_contents = bp.scipy.io.loadmat(file_path)  

    # Print the contents of the .mat file
    # print("Contents of the .mat file:")

    # for key, value in mat_contents.items():
    #     if not key.startswith('__'):  # Skip metadata entries
    #         print(f"{key}")

    var = mat_contents['interpolated_data']  
   
    # convert precipitation from kg m-2 s-1 to mm
    if variable == 'pr':
       var *= 86400
       
    lat = bp.np.squeeze(mat_contents['lat'])
    lon = bp.np.squeeze(mat_contents['lon'])
   
    lat_mask = (lat >= lat_min) & (lat <= lat_max)
    lon_mask = (lon >= lon_min) & (lon <= lon_max)

    trimmed_var = var[bp.np.ix_(lat_mask, lon_mask)]
    trimmed_lat = lat[lat_mask]
    trimmed_lon = lon[lon_mask]
    
    var_bar = bp.np.nanmean(trimmed_var, axis = (0, 1, 2))  # get single value average for each year
   
    # print(var.shape)
    # print(len(lat))
    # print(len(lon))

    # so data are lat x lon x doy x year
   
    return var_bar

# test = gcm_yearly_avg(MACA_models[0], variables[0])


def gmet_yearly_avg(variable):
    
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
    ds_open = bp.xr.open_dataset(fpath)
    
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
     
    ds_var = ds_open[obs_variable].groupby('day.year').mean(skipna  = True, dim = ('day', 'lat', 'lon'))
    
    return ds_var.values

# test = gmet_yearly_avg(variables[0])


def bias(model, variable):
    
    # call GCM data from function and take the average
    gcm_data = gcm_yearly_avg(model, variable)
    gcm_avg = float(gcm_data.mean())
    
    # call gmet data from function and take the average
    gmet_data = gmet_yearly_avg(variable)
    gmet_avg = float(gmet_data.mean())
    
    # calculate bias
    bias = gcm_avg - gmet_avg
    
    return  bias
    
# bias_test = bias(MACA_models[0], variables[0])

def stdev_ratio(model, variable):
    
    # call GCM data from function and take standard devitation
    gcm_data = gcm_yearly_avg(model, variable)
    gcm_stdev = float(gcm_data.std())
    
    # call gridmet data from function and take standard deviation
    gmet_data = gmet_yearly_avg(variable)
    gmet_stdev = float(gmet_data.std())
    
    stdev_ratio = gcm_stdev / gmet_stdev
    
    return stdev_ratio

# test_stdev = stdev_ratio(MACA_models[0], variables[0])
    
#%%

base_dict = {}

for model in MACA_models:
    base_dict[model] = {}
    for calc in ('pr_ratio', 'tasmin_change', 'tasmax_change', 'yearly_avg', 'yearly_bias', 'summer_bias', 'stdev_ratio'):
        if calc in ('pr_ratio', 'tasmin_change', 'tasmax_change'):
            base_dict[model][calc] = 'x'
        elif calc == 'yearly_avg':
            base_dict[model][calc] = {}
            for year in range(1979, 2015):
                base_dict[model][calc][year] = {}
                for variable in variables:
                    base_dict[model][calc][year][variable] = 'x'
        else: 
            base_dict[model][calc] = {}
            for variable in variables:
                base_dict[model][calc][variable] = 'x'
                
bp.pprint.pprint(base_dict)
                
#%%

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
ds_open = bp.xr.open_dataset(fpath)

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
 
ds_var = ds_open[obs_variable].groupby('day.month')