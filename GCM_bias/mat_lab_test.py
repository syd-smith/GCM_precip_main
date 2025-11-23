#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 21 12:57:27 2025

@author: u1301408
"""

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/packages')
import base_packages as bp

# dimensions for MACA region
# lat      (lat) float32 672B 36.03 36.07 36.11 36.15 ... 42.9 42.94 42.98
# * lon      (lon) float32 684B -115.1 -115.1 -115.0 ... -108.1 -108.1 -108.0

# list of all models used in the MACA downscaling process that have ssp585
MACA_models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5', 'EC-Earth3-CC',
 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'INM-CM4-8', 'INM-CM5-0',
 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']
    
# variables used in MACA downscaling process 
variables = ['pr', 'huss', 'tasmin', 'tasmax', 'rsds', 'uas', 'vas']
gridmet_variables = ['pr', 'rmax', 'rmin', 'sph', 'srad', 'tmmn', 'tmmx', 'uas', 'vas']


#%%
base_dict = {}
for model in MACA_models:
    base_dict[model] = {}
    for calc in ['stdev', 'r_cor', 'p_cor', 'region_bias']:
        base_dict[model][calc] = {}
        for variable in variables:
            base_dict[model][calc][variable] = 'x'
            

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


def bias_calc(model, variable):
    
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
    
    return bias
    

#%%
for model in MACA_models:
    for variable in variables:
        bias = bias_calc(model, variable)
        base_dict[model]['bias'][variable] = bias
        print(f'{variable} in {model} has a bias of {bias}.')
        
#%%
# read out the dictionary from the .txt file
import ast

# Open and read the file
bp.os.chdir('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/taylor_plot/')
with open('nov_17.txt', 'r') as f: # saved before MIROC6
    contents = f.read()

# Convert from string representation to actual dictionary
base_dict = ast.literal_eval(contents)

#%%
# save dictionary containing data to a specified file (after running it through the functions below)
printer = bp.pprint.PrettyPrinter(indent = 3, width = 100, sort_dicts = True)
bp.os.chdir('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/GCM_bias/')

with open('nov_22.txt', 'w') as f:
    f.write(printer.pformat(base_dict))
        

#%%
# Create a figure and axis with PlateCarree projection
fig, ax = bp.plt.subplots(subplot_kw={"projection": bp.ccrs.PlateCarree()})

# Plot the pr_bar data as a heatmap
mesh = ax.pcolormesh(lon, lat, pr_bar, transform = bp.ccrs.PlateCarree(), cmap="viridis")

# Add a colorbar
cbar = bp.plt.colorbar(mesh, ax = ax, orientation = "vertical", shrink = 0.7, pad = 0.05)

# Add US state boundaries
ax.add_feature(bp.cfeature.STATES, edgecolor = "black", linewidth = 0.5)

# Set map extent (optional, adjust as needed)
ax.set_extent([-130, -60, 20, 55], crs = bp.ccrs.PlateCarree())

# Add gridlines and remove labels from the top and right
gridlines = ax.gridlines(draw_labels = True, dms = True, x_inline = False, y_inline = False, color = "gray", alpha = 0.5, linestyle = "--")
gridlines.top_labels = False  # Disable labels on the top
gridlines.right_labels = False  # Disable labels on the right

# Show the plot
bp.plt.show()







