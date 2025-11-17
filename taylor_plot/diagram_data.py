#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 10 12:59:57 2025

@author: u1301408
"""

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/packages')
import base_packages as bp

# evaluation of historical efficieny from 1979-2014 using a taylor diagram with optional basis display

# standard deviation : MACA
# correlation : MACA
# bias : GCM (shown on colorscale)

# list of all models used in the MACA downscaling process that have ssp585
MACA_models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5', 'EC-Earth3-CC',
 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'INM-CM4-8', 'INM-CM5-0',
 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']
    
# variables used in MACA downscaling process 
MACA_variables = ['pr', 'huss', 'tasmin', 'tasmax', 'rsds', 'uas', 'vas']
gridmet_variables = ['pr', 'rmax', 'rmin', 'sph', 'srad', 'tmmn', 'tmmx', 'uas', 'vas']


#%%
# loop through model dictionary framework variable to add all models and variables with a placeholder for each value
model_dict = {
    model: {
        'std': {var: 'x' for var in MACA_variables},
        'corrcoef':  {var: 'x' for var in MACA_variables},
        'bias': {var: 'x' for var in MACA_variables}
    }
    for model in MACA_models
}

# save the dictionary to a specified file for later use
printer = bp.pprint.PrettyPrinter(indent = 3, width = 100, sort_dicts = True)
bp.os.chdir('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/taylor_plot/')

with open('taylor_dict_framework.txt', 'w') as f:
    f.write(printer.pformat(model_dict))

# bp.pprint.pprint(model_dict)


#%%
# read out the dictionary from the .txt file
import ast

# Open and read the file
bp.os.chdir('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/taylor_plot/')
with open('nov_9.txt', 'r') as f: # saved before MIROC6
    contents = f.read()

# Convert from string representation to actual dictionary
base_dict = ast.literal_eval(contents)


#%%
# save dictionary containing data to a specified file (after running it through the functions below)
printer = bp.pprint.PrettyPrinter(indent = 3, width = 100, sort_dicts = True)
bp.os.chdir('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/taylor_plot/')

with open('nov_17.txt', 'w') as f:
    f.write(printer.pformat(base_dict))
    

#%%
def st_dev_MACA(model, variable, dictionary):
    """
    First average data across the time dimension and then
    calculate the spatial standard deviaton.
    Dictionary should follow structure outlined above. 
    """
    
    ds = bp.xr.open_dataset(f'/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/output/netcdf/macav2metdata_GSLBIP_{model}_ssp585_{variable}.nc')
    # restrict to histrocial time period
    time_average = ds[variable].mean(skipna = True, dim = 'time')
    
    st_dev = time_average.std(dim = ['lat', 'lon'])
    
    # add calculation to dictionary
    dictionary[model]['std'][variable] = float(st_dev)
    
    return f'Standard Deviation for {model}: {float(st_dev)}'

# for model in MACA_models[20]:
#     for var in MACA_variables:
#         st_dev_MACA(model, var, base_dict)
#         print(model, var)


def st_dev_obs(variable):
    """
    Averages observational data over the time dimension and then 
    calculates thee spatial standard deviation. 
    Note that gridmet variables are named differently. 
    tasmin : tmmn 
    tasmax : tmmx 
    rsds : srad
    huss : sph
    min rh : rmin
    max rh : rmax
    """
    
    # open dataset stored in Savanna's folder of strong-group7
    ds = bp.xr.open_dataset(f'/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/gridmet/gsl_region_{variable}_1979-2014.nc')
   
    # change the variable name from abreviation used in file name to variable name in the dataset
    if variable == 'pr':
        variable = 'precipitation_amount'
    elif variable == 'rmax' or variable == 'rmin':
        variable = 'relative_humidity'
    elif variable == 'sph':
        variable = 'specific_humidity'
    elif variable == 'srad':
        variable = 'surface_downwelling_shortwave_flux_in_air'
    elif variable == 'tmmn' or variable == 'tmmx':
        variable = 'air_temperature'
        
    # average selected variable over the time dimension
    time_average = ds[variable].mean(skipna = True, dim = 'day')
    
    # calculate spatial standard deviation
    st_dev = time_average.std(dim = ['lat', 'lon'])
    
    return float(st_dev)

# for var in gridmet_variables[3:]:
#     output = st_dev_obs(var)
#     print(f'{var} : {output}')
    
# standard deviations for observational data
# pr : 0.46832597244903795
# rmax : 10.24461758012446
# rmin : 4.791940955646766
# sph : 0.0003445885315470638
# srad : 9.423356161495821
# tmmn : 3.6344803010020477
# tmmx : 3.778675424194867
# uas : 0.7591268756780736
# vas : 0.3952614372625724

#%%
def corr_coef(model, variable, dictionary):
    # make sure the same grid is being used for the model and gridmet (boundaries and gridpoint locations are the same)
    # make a map plt.imshow() of both dataset next to each other and make sure they match (of collapsed time dataset)
    # collapse time average to a single array and plot on a scatter plot
    
    
    """
    Calulate the spatial correlation coefficient using the model
    and observational data. 
    Dictionary structure should match framework above. 
    """
    
    # dataset
    # open dataset and average model data across time
    ds_MACA = bp.xr.open_dataset(f'/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/output/netcdf/macav2metdata_GSLBIP_{model}_ssp585_{variable}.nc')
    time_average_MACA = ds_MACA[variable].mean(skipna = True, dim = 'time')
    time_average_MACA_flipped = time_average_MACA.isel(lat = slice(None, None, -1))
    print(time_average_MACA.size)
    MACA_data = time_average_MACA.values.flatten()

    # average observational data across time
    time_average_obs = ds_obs[obs_variable].mean(skipna = True, dim = 'day')
    print(time_average_obs.size)
    obs_data = time_average_obs.values.flatten()
    obs_data_flipped = bp.np.flip(obs_data)
    
    
    # open dataset and average model data across time
    ds_MACA = bp.xr.open_dataset(f'/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/output/netcdf/macav2metdata_GSLBIP_{model}_ssp585_{variable}.nc')
    time_average_MACA = ds_MACA[variable].mean(skipna = True, dim = 'time')
    time_average_MACA_flipped = time_average_MACA.isel(lat = slice(None, None, -1))
    MACA_data = time_average_MACA_flipped.values.flatten()
    
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
        
    # open observational data
    ds_obs = bp.xr.open_dataset(f'/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/gridmet/gsl_region_{open_variable}_1979-2014.nc')
    
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
        
    # average observational data across time
    time_average_obs = ds_obs[obs_variable].mean(skipna = True, dim = 'day')
    obs_data = time_average_obs.values.flatten()
    obs_data_flipped = bp.np.flip(obs_data)
    
    # correlation coefficient calculation
    corr_coef = bp.np.corrcoef(MACA_data, obs_data_flipped)[0,1] # selects the right correlation coefficient out of an array
    
    # save data point to dictionary
    # dictionary[model]['corrcoef'][variable] = float(corr_coef)
    
    return float(corr_coef)


test = corr_coef(MACA_models[0], MACA_variables[0], base_dict)
# for model in MACA_models:
#     for var in MACA_variables:
#         corr_coef(model, var, base_dict)
#         print(model, var)


#%%
def matlab_to_netcdf(model, variable):
    
    # convert matlab file to netcdf
    matlab_file = bp.scipy.io.loadmat(f'/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/coarse_grid/{model}_historical_{variable}.mat')
    
    # Suppose you have lat, lon, time, and var in your file:
    lat = bp.np.squeeze(matlab_file['lat'])
    lon = bp.np.squeeze(matlab_file['lon'])
    var = bp.np.squeeze(matlab_file['interpolated_data'])  # shape: (time, lat, lon), check and reshape if necessary

    years = bp.np.arange(1979, 2015)                 # 36 years
    # days_per_year = 365                           # change to 366 if all leap years
    year_full = []
    day_full = []
    for year in years:
        max_day = 366 if bp.calendar.isleap(year) else 365
        for day in range(1, max_day + 1):
            year_full.append(year)
            day_full.append(day)
    year_full = bp.np.array(year_full)
    day_full = bp.np.array(day_full)

    time = bp.pd.to_datetime({'year' : year_full, 'month' : 1, 'day' : 1}) + bp.pd.to_timedelta(day_full - 1, unit = 'D')
    
    # Create an xarray DataArray (or Dataset for multiple variables)
    ds = bp.xr.DataArray(
        var,
        coords = {'time': time, 'lat': lat, 'lon': lon},
        dims = (variable, 'time', 'lat', 'lon'),
        name = variable
    )
    
    # Save to NetCDF
    ds.to_netcdf(f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/taylor_plot/GCM_data/{model}_historical_{variable}.nc')
    
    return ds

#%%
ds = bp.scipy.io.loadmat('/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/coarse_grid/ACCESS-CM2_historical_pr.mat')

var = bp.np.squeeze(ds['interpolated_data'])
# year = bp.np.squeeze(ds['year'])

print(var.shape)
# print(day_of_year.shape)


#%%
model = MACA_models[0]
variable = MACA_variables[0]

# dataset
# open dataset and average model data across time
ds_MACA = bp.xr.open_dataset(f'/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/output/netcdf/macav2metdata_GSLBIP_{model}_ssp585_{variable}.nc')
time_average_MACA = ds_MACA[variable].mean(skipna = True, dim = 'time')
time_average_MACA_flipped = time_average_MACA.isel(lat = slice(None, None, -1))
print(time_average_MACA.size)
MACA_data = time_average_MACA.values.flatten()

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
    
# open observational data
ds_obs = bp.xr.open_dataset(f'/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/gridmet/gsl_region_{open_variable}_1979-2014.nc')

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
    
# average observational data across time
time_average_obs = ds_obs[obs_variable].mean(skipna = True, dim = 'day')
print(time_average_obs.size)
obs_data = time_average_obs.values.flatten()
obs_data_flipped = bp.np.flip(obs_data)

# correlation coefficient calculation
# corr_coef = bp.np.corrcoef(MACA_data, obs_data_flipped)[0,1] # selects the right correlation coefficient out of an array

#%%
bp.plt.imshow(time_average_MACA_flipped)

#%%
bp.plt.imshow(time_average_obs)

#%%
# maca as x
bp.plt.scatter(time_average_MACA_flipped, time_average_obs, s = 1)