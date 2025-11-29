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


#%%
gcm_dict = {}

for model in MACA_models:
    gcm_dict[model] = {}
    for calc in ('pr_ratio', 'tasmin_change', 'tasmax_change', 'yearly_avg', 'yearly_bias', 'summer_bias', 'stdev_ratio'):
        if calc in ('pr_ratio', 'tasmin_change', 'tasmax_change'):
            gcm_dict[model][calc] = 'x'
        elif calc == 'yearly_avg':
            gcm_dict[model][calc] = {}
            for year in range(1979, 2015):
                gcm_dict[model][calc][year] = {}
                for variable in variables:
                    gcm_dict[model][calc][year][variable] = 'x'
        else: 
            gcm_dict[model][calc] = {}
            for variable in variables:
                gcm_dict[model][calc][variable] = 'x'
                
bp.pprint.pprint(gcm_dict)

#%%
def gcm_yearly_avg(save_variable, model, variable, save = False):
    
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
    
    if save == True:
        # save data to dictionary
        for year, (position, value) in zip(range(1979, 2015), enumerate(var_bar)):
            save_variable[model]['yearly_avg'][year][variable] = float(var_bar[position])
            print(f'{value} saved to {variable} in {year} or {model}.')
   
    return var_bar

for model in MACA_models:
    for variable in variables:
        gcm_yearly_avg(gcm_dict, model, variable)
        
#%%   
# save dictionary containing data to a specified file (after running it through the functions below)
printer = bp.pprint.PrettyPrinter(indent = 3, width = 100, sort_dicts = True)
bp.os.chdir('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/GCM_bias/')

with open('gcm_dict_nov_26.txt', 'w') as f:
    f.write(printer.pformat(gcm_dict))

#%%
gmet_dict = {}

for year in range(1979, 2015):
    gmet_dict[year] = {}
    for variable in variables:
        gmet_dict[year][variable] = 'x'

#%%
def gmet_yearly_avg(save_variable, variable, save = False):
    
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
    
    if  save == True:
        # save data to dictionary
        for year, (position, value) in zip(range(1979, 2015), enumerate(ds_var.values)):
            save_variable[year][variable] = float(ds_var.values[position])
            print(f'{value} saved to {variable} in {year}.')
    
    return ds_var.values

# for variable in variables:
#     gmet_yearly_avg(gmet_dict, variable)
    

#%%
# save dictionary containing data to a specified file (after running it through the functions below)
printer = bp.pprint.PrettyPrinter(indent = 3, width = 100, sort_dicts = True)
bp.os.chdir('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/GCM_bias/')

with open('gmet_dict_nov_26.txt', 'w') as f:
    f.write(printer.pformat(gmet_dict))
    
    
#%%
# read out the dictionary from the .txt file
import ast

# Open and read the file
bp.os.chdir('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/GCM_bias/')
with open('gcm_dict_nov_26.txt', 'r') as f: # saved before MIROC6
    contents = f.read()

# Convert from string representation to actual dictionary
gcm_dict = ast.literal_eval(contents)

with open('gmet_dict_nov_26.txt', 'r') as f: # saved before MIROC6
    contents = f.read()

# Convert from string representation to actual dictionary
gmet_dict = ast.literal_eval(contents)


#%%
def bias(save_variable,  model, variable):
    
    # call GCM data from saved dictionary and take the average
    retrived_gcm_data =  []
    for year in range(1979, 2015):
        gcm_dat_point = gcm_dict[model]['yearly_avg'][year][variable]
        retrived_gcm_data.append(gcm_dat_point)
    gcm_avg = float(bp.np.mean(retrived_gcm_data))

    # call gmet data from function and take the average
    retrived_gmet_data = []
    for year in range(1979, 2015):
        gmet_dat_point = gmet_dict[year][variable]
        retrived_gmet_data.append(gmet_dat_point)
    gmet_avg = float(bp.np.mean(retrived_gmet_data))
    
    # calculate bias
    bias = gcm_avg - gmet_avg
    
    # save data to dictionary
    save_variable[model]['yearly_bias'][variable]  = bias
    
    return  bias
    
# bias_test = bias(MACA_models[0], variables[0])
for model in MACA_models:
    for variable in variables:
        bias(gcm_dict, model, variable)


def stdev_ratio(save_variable, model, variable):
    
    # call GCM data from saved dictionary and take the average
    retrived_gcm_data =  []
    for year in range(1979, 2015):
        gcm_dat_point = gcm_dict[model]['yearly_avg'][year][variable]
        retrived_gcm_data.append(gcm_dat_point)
    gcm_stdev = float(bp.np.std(retrived_gcm_data))

    # call gmet data from function and take the average
    retrived_gmet_data = []
    for year in range(1979, 2015):
        gmet_dat_point = gmet_dict[year][variable]
        retrived_gmet_data.append(gmet_dat_point)
    gmet_stdev = float(bp.np.std(retrived_gmet_data))
    
    stdev_ratio = gcm_stdev / gmet_stdev
    
    # save data to dictionary
    save_variable[model]['stdev_ratio'][variable] = stdev_ratio
    
    return stdev_ratio

# test_stdev = stdev_ratio(MACA_models[0], variables[0])
for model in MACA_models:
    for variable in variables:
        stdev_ratio(gcm_dict, model, variable)
    
                
#%%
model = MACA_models[0]
variable = variables[0]

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

#%%
gmet_JJA_dict = {}

for year in range(1979, 2015):
    gmet_JJA_dict[year] = {}
    for variable in variables:
        gmet_JJA_dict[year][variable] = 'x'
        
# save dictionary containing data to a specified file (after running it through the functions below)
printer = bp.pprint.PrettyPrinter(indent = 3, width = 100, sort_dicts = True)
bp.os.chdir('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/GCM_bias/')

with open('gmet_JJA_dict.txt', 'w') as f:
    f.write(printer.pformat(gmet_JJA_dict))

#%%
        
def gmet_JJA_avg(variable):
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
     
    da  = ds_open[obs_variable]   
     
    year = da['day'].dt.year.values
    month = da['day'].dt.month.values
    da = da.assign_coords(year=('day', year), month=('day', month))

    # now group by both at once using a tuple key
    ds_var = da.groupby(['year', 'month'])
    ds_mean = ds_var.mean('day')

    for year in range(1979, 2015):
        june_mean = ds_mean.sel(year = year, month = 6)
        july_mean = ds_mean.sel(year = year, month = 7)
        august_mean = ds_mean.sel(year = year, month = 8)
        combine = bp.xr.concat([june_mean, july_mean, august_mean], dim = 'monthly_JJA')
        dat_point = float(bp.np.mean(combine))
        gmet_JJA_dict[year][variable] = dat_point
    
    return gmet_JJA_dict

for variable in variables:
    gmet_JJA_avg(variable)
    print(f'{variable} saved!')
    
    
    
    


# ds_year = ds_open[obs_variable].groupby('day.year')
# ds_month = ds_year[obs_variable].groupby('day.month')
# ds_JJA_mean = bp.np.mean(ds_var[6], ds_var[7], ds_var[8])