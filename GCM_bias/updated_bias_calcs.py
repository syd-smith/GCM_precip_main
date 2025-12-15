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
# read out dictionaries from the .txt file
import ast

# Open and read the file
bp.os.chdir('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/GCM_bias/')
with open('gcm_dict_dec_15.txt', 'r') as f: # saved before MIROC6
    contents = f.read()

# Convert from string representation to actual dictionary
gcm_dict = ast.literal_eval(contents)


#%%
yearly_results = []
for model in MACA_models:
    for variable in variables:
        yearly_results.append(gcm_dict[model]['yearly_avg'][1980][variable])
        #%%
print(list(gcm_dict[model]['yearly_avg'].keys())[:])
print(type(next(iter(gcm_dict[model]['yearly_avg'].keys()))))        
#%%
with open('gmet_dict_nov_26.txt', 'r') as f: # saved before MIROC6
    contents = f.read()

# Convert from string representation to actual dictionary
gmet_dict = ast.literal_eval(contents)

#%%
with open('gmet_JJA_dict.txt', 'r') as f: # saved before MIROC6
    contents = f.read()

# Convert from string representation to actual dictionary
gmet_JJA_dict = ast.literal_eval(contents)


#%%
# create the framework for a gcm dictionary
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
# create framework for gridmet dictionary
gmet_dict = {}

for year in range(1979, 2015):
    gmet_dict[year] = {}
    for variable in variables:
        gmet_dict[year][variable] = 'x'
        
#%%
# create framework for gcm dictionary
gcm_JJA_dict = {}

for model in MACA_models:
    gcm_JJA_dict[model] = {}
    for year in range(1979, 2015):
        gcm_JJA_dict[model][year] = {}
        for variable in variables:
            gcm_JJA_dict[model][year][variable] = 'x'
            
#%%
# create updated gcm_dict framework
updated_gcm_dict = {}

for model in MACA_models:
    updated_gcm_dict[model] = {}
    for calc in ('JJA_future_stdev', 'yearly_future_stdev', 'pr_ratio', 'tasmin_change', 'tasmax_change', 'yearly_avg', 'JJA_avg', 'yearly_bias', 'summer_bias', 'JJA_stdev_ratio', 'stdev_ratio'):
        if calc in ('pr_ratio', 'tasmin_change', 'tasmax_change'):
            updated_gcm_dict[model][calc] = gcm_dict[model][calc]
        elif calc == 'yearly_avg':
            updated_gcm_dict[model][calc] = {}
            for year in range(1979, 2100):
                updated_gcm_dict[model][calc][year] = {}
                for variable in variables:
                    if year in range(1979, 2015):
                        updated_gcm_dict[model][calc][year][variable] = gcm_dict[model][calc][year][variable]
                    elif year in range(2015, 2100):
                        updated_gcm_dict[model][calc][year][variable] = 'x'
        elif calc == 'JJA_stdev_ratio':
            updated_gcm_dict[model][calc] = {}
            for variable in variables:
                updated_gcm_dict[model][calc][variable] = gcm_dict[model][calc][variable]
        elif calc == 'JJA_future_stdev' or calc == 'yearly_future_stdev':
            updated_gcm_dict[model][calc] = {}
            for variable in variables:
                updated_gcm_dict[model][calc][variable] = 'x'
        elif calc == 'JJA_avg':
            updated_gcm_dict[model][calc] = {}
            for year in range(1979, 2100):
                updated_gcm_dict[model][calc][year] = {}
                for variable in variables:
                    if year in range(1979, 2015):
                        updated_gcm_dict[model][calc][year][variable] = gcm_dict[model][calc][year][variable]
                    elif year in range(2015, 2100):
                        updated_gcm_dict[model][calc][year][variable] = 'x'
        else: 
            updated_gcm_dict[model][calc] = {}
            for variable in variables:
                updated_gcm_dict[model][calc][variable] = gcm_dict[model][calc][variable]
        
#%%
# save dictionary containing data to a specified file (after running it through the functions below)
printer = bp.pprint.PrettyPrinter(indent = 3, width = 100, sort_dicts = True)
bp.os.chdir('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/GCM_bias/')

with open('gcm_dict_dec_15.txt', 'w') as f:
    f.write(printer.pformat(updated_gcm_dict))
    
    
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
        gcm_yearly_avg(updated_gcm_dict, model, variable)
        
#%%

def gcm_future_yearly_avg(save_variable, model, variable, save = False):
    
    file_path = f'/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/coarse_grid/{model}_ssp585_{variable}.mat'
    
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
        for year, (position, value) in zip(range(2015, 2100), enumerate(var_bar)):
            save_variable[model]['yearly_avg'][year][variable] = float(var_bar[position])
            print(f'{value} saved to {variable} in {year} for {model}.')
   
    return var_bar

for model in MACA_models:
    for variable in variables:
        gcm_future_yearly_avg(updated_gcm_dict, model, variable, save = True)
        

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

for variable in variables:
    gmet_yearly_avg(gmet_dict, variable)


#%%
def bias(save_variable, model, variable):
    
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
    if variable == 'pr':
        bias = gcm_avg / gmet_avg
    else:
        bias = gcm_avg - gmet_avg
    
    # save data to dictionary
    save_variable[model]['yearly_bias'][variable]  = bias
    
    return bias
    
for model in MACA_models:
    bias(gcm_dict, model, 'pr')
    
# for model in MACA_models:
#     for variable in variables:
#         bias(gcm_dict, model, variable)
#%%
new_dict = gcm_dict

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
        gmet_dat_point = gmet_JJA_dict[year][variable]
        retrived_gmet_data.append(gmet_dat_point)
    gmet_stdev = float(bp.np.std(retrived_gmet_data))
    
    stdev_ratio = gcm_stdev / gmet_stdev
    
    # save data to dictionary
    save_variable[model]['stdev_ratio'][variable] = stdev_ratio
    
    return stdev_ratio

# test_stdev = stdev_ratio(MACA_models[0], variables[0])
for model in MACA_models:
    for variable in variables:
        stdev_ratio(new_dict, model, variable)
        
#%%

def JJA_future_stdev(save_variable, model, variable):
    
    gcm_data  = []
    for year in range(2015, 2100):
        gcm_dat_point = updated_gcm_dict[model]['JJA_avg'][year][variable]
        gcm_data.append(gcm_dat_point)
    gcm_stdev = float(bp.np.std(gcm_data))

    # save data to dictionary
    save_variable[model]['JJA_future_stdev'][variable] = gcm_stdev
    print(f'{gcm_stdev} saved to {variable} for {model}.')
    
    return gcm_stdev
    
for model in MACA_models:
    for variable in variables:
        JJA_future_stdev(updated_gcm_dict, model, variable)


def yearly_future_stdev(save_variable, model, variable):
    
    gcm_data  = []
    for year in range(2015, 2100):
        gcm_dat_point = updated_gcm_dict[model]['yearly_avg'][year][variable]
        gcm_data.append(gcm_dat_point)
    gcm_stdev = float(bp.np.std(gcm_data))
    
    # save data to dictionary
    save_variable[model]['yearly_future_stdev'][variable] = gcm_stdev
    print(f'{gcm_stdev} saved to {variable} for {model}.')
    
    return gcm_stdev

for model in MACA_models:
    for variable in variables:
        yearly_future_stdev(updated_gcm_dict, model, variable)
                
#%%
def gcm_JJA_avg(save_variable, model, variable, save = False):
    
    file_path = f'/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/coarse_grid/{model}_historical_{variable}.mat'

    # min and max latitudes and longitudes used in the MACA process
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

    # output of (6, 8, 366, 36) -> (lat, lon, days in year, year)
    trimmed_var = var[bp.np.ix_(lat_mask, lon_mask)]

    # number of days in each month based on the number of days in the year for that model
    ndays = trimmed_var.shape[2]
    if ndays == 366:
        days_in_month = bp.np.array([31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
    elif ndays == 365:
        days_in_month = bp.np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
    elif ndays == 360:
        days_in_month = bp.np.array([30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30])
    else:
        print(model)
        raise ValueError(f"Number of days in the year not found: ndays = {ndays}")

    # repeat the month number for the number of days in that month
    month_index = bp.np.repeat(bp.np.arange(1, 13), days_in_month)

    # define the shape of monthly_mean to be (12, 36) -> (month, year)
    nmonths = 12
    nyears = trimmed_var.shape[3]
    monthly_mean = bp.np.empty((nmonths, nyears))

    # loop over months and give an average for each month across all of the lat, lon, and years
    for m in range(1, nmonths + 1):
        mask = (month_index == m)          # True for days in month m
        data_m = trimmed_var[:, :, mask, :]
        monthly_mean[m-1, :] = bp.np.nanmean(data_m, axis = (0, 1, 2))

    # find the average for the summer months
    means = []
    for year, position in zip(range(1979, 2100), range(0, 36)):
        JJA_mean  = float(bp.np.mean([monthly_mean[5, position], monthly_mean[6, position], monthly_mean[7, position]]))
        means.append(JJA_mean)
        if save == True:
            save_variable[model]['JJA_avg'][year][variable] = JJA_mean

    return means
    
for model in MACA_models:
    for variable in variables:
        gcm_JJA_avg(updated_gcm_dict, model, variable, save = True)
        
#%%
def gcm_future_JJA_avg(save_variable, model, variable, save = False):
    
    file_path = f'/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/coarse_grid/{model}_ssp585_{variable}.mat'
    
    # min and max latitudes and longitudes used in the MACA process
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

    # output of (6, 8, 366, 36) -> (lat, lon, days in year, year)
    trimmed_var = var[bp.np.ix_(lat_mask, lon_mask)]

    # number of days in each month based on the number of days in the year for that model
    ndays = trimmed_var.shape[2]
    if ndays == 366:
        days_in_month = bp.np.array([31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
    elif ndays == 365:
        days_in_month = bp.np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
    elif ndays == 360:
        days_in_month = bp.np.array([30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30])
    else:
        print(model)
        raise ValueError(f"Number of days in the year not found: ndays = {ndays}")

    # repeat the month number for the number of days in that month
    month_index = bp.np.repeat(bp.np.arange(1, 13), days_in_month)

    # define the shape of monthly_mean to be (12, 36) -> (month, year)
    nmonths = 12
    nyears = trimmed_var.shape[3]
    monthly_mean = bp.np.empty((nmonths, nyears))

    # loop over months and give an average for each month across all of the lat, lon, and years
    for m in range(1, nmonths + 1):
        mask = (month_index == m)          # True for days in month m
        data_m = trimmed_var[:, :, mask, :]
        monthly_mean[m-1, :] = bp.np.nanmean(data_m, axis = (0, 1, 2))

    # find the average for the summer months
    means = []
    for year, position in zip(range(2015, 2100), range(0, 85)):
        JJA_mean  = float(bp.np.mean([monthly_mean[5, position], monthly_mean[6, position], monthly_mean[7, position]]))
        means.append(JJA_mean)
        if save == True:
            save_variable[model]['JJA_avg'][year][variable] = JJA_mean
            print(f'{JJA_mean} saved to {variable} in {year} for {model}.')
        else:
            print('Not saving data.')

    return means

for model in MACA_models:
    for variable in variables:
        gcm_future_JJA_avg(updated_gcm_dict, model, variable, save = True)


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
    
#%%
def JJA_bias(save_variable, model, variable):
    
    # call GCM data from saved dictionary and take the average
    retrived_gcm_data =  []
    for year in range(1979, 2015):
        gcm_dat_point = gcm_dict[model]['JJA_avg'][year][variable]
        retrived_gcm_data.append(gcm_dat_point)
    gcm_avg = float(bp.np.mean(retrived_gcm_data))

    # call gmet data from function and take the average
    retrived_gmet_data = []
    for year in range(1979, 2015):
        gmet_dat_point = gmet_JJA_dict[year][variable]
        retrived_gmet_data.append(gmet_dat_point)
    gmet_avg = float(bp.np.mean(retrived_gmet_data))
    
    # calculate bias
    if variable == 'pr':
        JJA_bias = gcm_avg / gmet_avg
    else:
        JJA_bias = gcm_avg - gmet_avg
    
    # save data to dictionary
    save_variable[model]['summer_bias'][variable]  = JJA_bias
    
    return JJA_bias
    
# bias_test = bias(MACA_models[0], variables[0])
for model in MACA_models:
    for variable in variables:
        JJA_bias(gcm_dict, model, variable)

#%%
def JJA_stdev_ratio(save_variable, model, variable):
    
    # call GCM data from saved dictionary and take the average
    retrived_gcm_data =  []
    for year in range(1979, 2015):
        gcm_dat_point = updated_gcm_dict[model]['JJA_avg'][year][variable]
        retrived_gcm_data.append(gcm_dat_point)
    gcm_stdev = float(bp.np.std(retrived_gcm_data))

    # call gmet data from function and take the average
    retrived_gmet_data = []
    for year in range(1979, 2015):
        gmet_dat_point = gmet_JJA_dict[year][variable]
        retrived_gmet_data.append(gmet_dat_point)
    gmet_stdev = float(bp.np.std(retrived_gmet_data))
    
    JJA_stdev_ratio = gcm_stdev / gmet_stdev
    
    # save data to dictionary
    save_variable[model]['JJA_stdev_ratio'][variable] = JJA_stdev_ratio
    
    return stdev_ratio

# test_stdev = stdev_ratio(MACA_models[0], variables[0])
for model in MACA_models:
    for variable in variables:
        JJA_stdev_ratio(updated_gcm_dict, model, variable)
        
#%%
# read out dictionaries from the .txt file
import ast

# Open and read the file
bp.os.chdir('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/GCM_bias/old_bias_calcs')
with open('nov_23.txt', 'r') as f: # saved before MIROC6
    contents = f.read()

# Convert from string representation to actual dictionary
old_gcm = ast.literal_eval(contents)

#%%
for model in MACA_models:
    updated_gcm_dict[model]['pr_ratio'] = old_gcm[model]['pr_ratio']
    updated_gcm_dict[model]['tasmin_change'] = old_gcm[model]['tasmin_change']
    updated_gcm_dict[model]['tasmax_change'] = old_gcm[model]['tasmax_change']

        
                 
    