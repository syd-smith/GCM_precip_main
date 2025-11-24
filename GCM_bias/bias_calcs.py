#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 22 21:32:55 2025

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
# read out the dictionary from the .txt file
import ast

# Open and read the file
bp.os.chdir('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/GCM_bias/')
with open('nov_23.txt', 'r') as f: # saved before MIROC6
    contents = f.read()

# Convert from string representation to actual dictionary
base_dict = ast.literal_eval(contents)

#%%

def delta_temp(save_variable, start_month = 6, stop_month = 8):
    
    # loop through all listed models and emission scenarios to open all available data
    for model in MACA_models:
        fpath = '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/scatter_plot/masked_MACA/'
        hist_min_path = f'{fpath}MACA_{model}_ssp585_{start_month}-{stop_month}_1979-2014_tasmin_masked.nc'
        hist_max_path = f'{fpath}MACA_{model}_ssp585_{start_month}-{stop_month}_1979-2014_tasmax_masked.nc'
        fut_min_path = f'{fpath}MACA_{model}_ssp585_{start_month}-{stop_month}_2070-2099_tasmin_masked.nc'
        fut_max_path = f'{fpath}MACA_{model}_ssp585_{start_month}-{stop_month}_2070-2099_tasmax_masked.nc'
            
        if model in MACA_models:
            # find the mean for the historical period
            hist_ds_min = bp.xr.open_dataset(hist_min_path)
            hist_means_min = []
            for year in range(1979, 2015):
                data_hist_min = hist_ds_min['tasmin'].sel(time = hist_ds_min.time.dt.year == year)
                hist_mean_min = data_hist_min.mean(skipna= True).item()
                hist_means_min.append(hist_mean_min)
            hist_min_mean = bp.np.mean(hist_means_min)
                
            hist_ds_max = bp.xr.open_dataset(hist_max_path)
            hist_means_max = []
            for year in range(1979, 2015):
                data_hist_max = hist_ds_max['tasmax'].sel(time = hist_ds_max.time.dt.year == year)
                hist_mean_max = data_hist_max.mean(skipna = True).item()
                hist_means_max.append(hist_mean_max) 
            hist_max_mean = bp.np.mean(hist_means_max)

            # finds the mean for the future period
            fut_ds_min = bp.xr.open_dataset(fut_min_path)
            fut_means_min = []
            for year in range(2070, 2099):
                data_fut_min = fut_ds_min['tasmin'].sel(time = fut_ds_min.time.dt.year == year)
                fut_mean_min = data_fut_min.mean(skipna = True).item()
                fut_means_min.append(fut_mean_min)
            fut_min_mean = bp.np.mean(fut_means_min)
                
            fut_ds_max = bp.xr.open_dataset(fut_max_path)
            fut_means_max = []
            for year in range(2070, 2099):
                data_fut_max = fut_ds_max['tasmax'].sel(time = fut_ds_max.time.dt.year == year)
                fut_mean_max = data_fut_max.mean(skipna = True).item()
                fut_means_max.append(fut_mean_max)  
            fut_max_mean = bp.np.mean(fut_means_max)   
                
            # calulate change in temperature and save data to dictionary
            min_temp = fut_min_mean - hist_min_mean
            max_temp = fut_max_mean - hist_max_mean
            
            # save to dictionary
            save_variable[model]['tasmin_change'] = float(min_temp)
            save_variable[model]['tasmax_change'] = float(max_temp)
            
            # print model as a check
            print(f'{model} saved!')
            
        # skip over model and emission scenario combos that don't exist in the dataset
        else:
            print(f'{model} not found')
            
    return save_variable   

temp_test = delta_temp(base_dict)
    
#%%
# CALCULATE PERCENT CHANGE IN PRECIPITATION AND CHANGE IN TEMPERATURE
def precip_ratio(save_variable, start_month = 6, stop_month = 8):
    
    """
    Returns the percent change in precitation to a nested dictionary under the model 
    name and emission scenario. The average precip value is across the historical 
    period and all grid points.Save_variable should be the framework dictionary imported 
    from reference_data.py.
    """
    
    # loop through all listed models and emission scenarios to open all available data
    for model in MACA_models:
        fpath = '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/scatter_plot/masked_MACA/'
        hist_path = f'{fpath}MACA_{model}_ssp585_{start_month}-{stop_month}_1979-2014_pr_masked.nc'
        fut_path = f'{fpath}MACA_{model}_ssp585_{start_month}-{stop_month}_2070-2099_pr_masked.nc'
        
        # calculate precipitation ratio for found data
        ds_hist = bp.xr.open_dataset(hist_path)
        ds_fut = bp.xr.open_dataset(fut_path)
        
        years_means_hist = []
        for year in range(1979, 2015):
            year_dat_hist = ds_hist['pr'].sel(time = ds_hist.time.dt.year == year)
            mean_hist = year_dat_hist.mean(skipna = True).item() # <- make sure to skip all NAN values outside the boundary
            years_means_hist.append(mean_hist)
        grand_mean_hist = float(bp.np.mean(years_means_hist))
        
        years_means_fut = []
        for year in range(2070, 2100):
            year_dat_fut = ds_fut['pr'].sel(time = ds_fut.time.dt.year == year)
            mean_fut = year_dat_fut.mean(skipna = True).item() # <- make sure to skip all NAN values outside the boundary
            years_means_fut.append(mean_fut)
        grand_mean_fut = float(bp.np.mean(years_means_fut))
        
        grand_precip = (grand_mean_fut/ grand_mean_hist) *100
        
        save_variable[model]['pr_ratio'] = grand_precip
        
        # print model name as a check
        print(f'{model} saved!')
                
    return save_variable 

pr_test = precip_ratio(base_dict)

#%%

def avg_hist_gcm(model, variable):
    
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

    var_bar = bp.np.nanmean(var, axis = (2,3))  # average over years
   
    trimmed_var_bar = var_bar[bp.np.ix_(lat_mask, lon_mask)]
    trimmed_lat = lat[lat_mask]
    trimmed_lon = lon[lon_mask]

    # print(var.shape)
    # print(len(lat))
    # print(len(lon))

    # so data are lat x lon x doy x year
   
    return trimmed_var_bar, trimmed_lat, trimmed_lon


def bias_calc(save_variable, model, variable):
    
    # call GCM data for the bias comparison
    GCM_data, lat, lon = avg_hist_gcm(model, variable)
    GCM_mean = float(GCM_data.mean())
    
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
        
    # open gridmet files
    # gridmet is already restricted to the MACA region
    gridmet_path = f'/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/gridmet/gsl_region_{open_variable}_1979-2014.nc'
    ds_open = bp.xr.open_dataset(gridmet_path) 
    
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
    
    # average over all of the regions and days to get a single number
    gridmet_mean = float(ds_open[obs_variable].mean(skipna = True))
    
    # bias calculation
    if open_variable == 'precipitation_amount':
        bias = GCM_mean / gridmet_mean
    else:
        bias = GCM_mean - gridmet_mean
    
    # save to dictionary
    save_variable[model]['region_bias'][variable] = bias
    
    # print as a check
    print(f'{model} {variable} saved!')
    
    return bias

for model in MACA_models:
    for variable in variables:
        bias_calc(base_dict, model, variable)

#%%
def stdev_ratio(save_variable, model, variable):
    
    # call GCM data for the bias comparison
    GCM_data, lat, lon = avg_hist_gcm(model, variable)
    GCM_stdev = float(GCM_data.std())
    
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
        
    # open gridmet files
    # gridmet is already restricted to the MACA region
    gridmet_path = f'/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/gridmet/gsl_region_{open_variable}_1979-2014.nc'
    ds_open = bp.xr.open_dataset(gridmet_path) 
    
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
    
    gridmet_stdev = float(ds_open[obs_variable].std())
    
    # ratio calculation
    stdev_ratio = GCM_stdev / gridmet_stdev
    
    # save to dictionary
    save_variable[model]['stdev_ratio'][variable] = stdev_ratio
    
    # print as a check
    print(f'{model} saved!')
    
    return stdev_ratio

# test = stdev_ratio(base_dict, MACA_models[0], variables[0])

for model in MACA_models:
    for variable in variables:
        stdev_ratio(base_dict, model, variable)
    

#%%

save_variable = base_dict

# def stdev_time(save_variable, model, variable):
model = MACA_models[0]
variable = variables[0]

# call GCM data for the bias comparison
GCM_data, lat, lon = avg_hist_gcm(model, variable)
GCM_stdev = GCM_data.std()
 
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
     
# open gridmet files
# gridmet is already restricted to the MACA region
gridmet_path = f'/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/gridmet/gsl_region_{open_variable}_1979-2014.nc'
ds_open = bp.xr.open_dataset(gridmet_path) 
 
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
 
gridmet_stdev = ds_open[obs_variable].std()
 
# ratio calculation
stdev_ratio = GCM_stdev / gridmet_stdev
 
# save to dictionary
save_variable[model]['stdev_ratio_time'][year][variable] = stdev_ratio


#%%
for year in range(1979, 2015):
    base_dict[model]['stdev_ratio_time'][year] = {}
    for variable in variables:
        base_dict[model]['stdev_ratio_time'][year][variable] = 'x'

#%%
printed = bp.pprint.pprint(base_dict)