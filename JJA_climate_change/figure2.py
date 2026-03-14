#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 23 18:06:49 2025

@author: Sydney Smith
"""

import geopandas as gpd
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path
from shapely.geometry import mapping
import  sys
import xarray as xr

# ==================================
# - Establish Relative File Path - 
# ==================================

current_file_directory = Path(__file__).resolve().parent
print(f'CURRENT FILE DIRECTORY: {current_file_directory}')
parent_directory = current_file_directory.parent
sys.path.append(str(parent_directory))

from tool_belt.file_traversing import read_file, write2file


# ===============
#  - Constants - 
# ===============

# all possible emission scenarios found in downscaled models
emission_scenarios = ['ssp119', 'ssp126', 'ssp245', 'ssp370', 'ssp434', 'ssp585']

models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5',
          'EC-Earth3-AerChem', 'EC-Earth3-CC', 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4',
          'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'IITM-ESM', 'INM-CM4-8', 'INM-CM5-0', 'KACE-1-0-G', 'KIOST-ESM', 
          'MIROC-ES2H', 'MIROC-ES2L', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']

# Load in the shape file that contains the new boundaries for the GSLB
shp  = gpd.read_file(parent_directory.joinpath('from_savanna/WBD_16_HU2_Shape/Shape/WBDHU4.shp'))
gsl  = shp[shp["huc4"] == "1602"]
br   = shp[shp["huc4"] == "1601"]
gslb = gpd.GeoDataFrame(geometry=[gsl.geometry.unary_union.union(br.geometry.unary_union)], crs=shp.crs)


# ==============
# - Functions - 
# ==============

def mask_MACA(model_name, variable, emission_scenario, start_month = 6, stop_month = 8, start_year = 1979, stop_year = 2014, save = False):
    
    """
    This function applies the boundaries of the GSLB to a given dataset through setting everything
    outside the boundaries to NAN. Default values return a NETCDF file with data for JJA over the 
    historical period. 
    
    Note: For this research, the historical period is defined as 1979 - 2014 and the future period 
          as 2070 - 2099.
    """

    # decodes time information follownig the Climate and Weather metadata connvention
    time_coder = xr.coders.CFDatetimeCoder(use_cftime = True)
    
    # load file path for data
    # TODO: change file path once data is published
    fpath = f'/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/output/netcdf/macav2metdata_GSLBIP_{model_name}_{emission_scenario}_{variable}.nc'
    if not os.path.exists(fpath):
        raise OSError(f'{fpath} was not downscaled in the MACA process.')
        
    # open data for specified model and raise error for requests that are not within the scope of the dataset
    ds_open = xr.open_mfdataset(fpath, engine = "netcdf4", decode_times = time_coder)
    
    # slice to focus on specified months and years
    ds_years = ds_open[variable].sel(time = ds_open.time.dt.year.isin(range(start_year, stop_year + 1)))
    ds_slice = ds_years.sel(time = ds_years.time.dt.month.isin(range(start_month, stop_month + 1)))

    # applied data to standard coordinate system (not regridding)
    ds = ds_slice.rio.write_crs("EPSG:4326")

    # clips out the GSLB
    ds = ds.rio.clip(gslb.geometry.apply(mapping), gslb.crs, drop=False)
    
    # saved masked dataset to directory
    if save:
        output_path = parent_directory.joinpath('JJA_climate_change', 'masked_MACA')
        output_name = f'MACA_{model_name}_{emission_scenario}_{start_month}-{stop_month}_{start_year}-{stop_year}_{variable}_masked.nc'
        
        ds.to_netcdf(output_path / output_name)
        print(f'Saved: {output_path}')
        return ds    
    
    return ds

def test_mask_function():
    """
    Apply the model to one test then open and map it to see if boundary application was successful.
    """
    
    # mask application
    mask_MACA(models[0], 'pr', emission_scenarios[1], save = True)
    
    # open newly created dataset
    fpath = parent_directory.joinpath('JJA_climate_change', 'masked_MACA', 'MACA_ACCESS-CM2_ssp126_6-8_1979-2014_pr_masked.nc')
    ds = xr.open_dataset(fpath)
    
    # plot data
    ds['pr'].isel(time=0).plot()
    plt.title("Precipitation for First Time Slice")
    plt.show()

def precip_ratio(save_variable, start_month = 6, stop_month = 8):
    
    """
    Returns the  change in precitation (future/historical) to a nested dictionary under the model 
    name and emission scenario. Precipitation is averaged across the historical (1979-2014) and
    future (2070-2099) periods respectively and all grid points. Save_variable should be the 
    framework dictionary as seen in reference_data.txt.
    """
    # loop through all listed models and emission scenarios to open all available data
    for model in models:
        for emission_scenario in emission_scenarios:
            
            fpath = parent_directory.joinpath('JJA_climate_change', 'masked_MACA/') # data is masked using mask_MACA
            
            hist_path = fpath / f'MACA_{model}_{emission_scenario}_{start_month}-{stop_month}_1979-2014_pr_masked.nc'
            fut_path = fpath / f'MACA_{model}_{emission_scenario}_{start_month}-{stop_month}_2070-2099_pr_masked.nc'
            
            try:
                # calculate precipitation ratio for data
                ds_hist = xr.open_dataset(hist_path)
                ds_fut = xr.open_dataset(fut_path)
                
                # create a list of the summer means for each year in the historical period
                years_means_hist = []
                for year in range(1979, 2015):
                    year_dat_hist = ds_hist['pr'].sel(time = ds_hist.time.dt.year == year)
                    mean_hist = year_dat_hist.mean(skipna = True).item() # <- make sure to skip all NAN values outside the boundary
                    years_means_hist.append(mean_hist)
                # take the overall historical mean
                grand_mean_hist = float(np.mean(years_means_hist))
                
                # create a list of the summer means for each year in the future periood 
                years_means_fut = []
                for year in range(2070, 2100):
                    year_dat_fut = ds_fut['pr'].sel(time = ds_fut.time.dt.year == year)
                    mean_fut = year_dat_fut.mean(skipna = True).item() # <- make sure to skip all NAN values outside the boundary
                    years_means_fut.append(mean_fut)
                # take the overalll future mean
                grand_mean_fut = float(np.mean(years_means_fut))
                
                # calculate the precipitation ratio
                grand_precip = (grand_mean_fut/ grand_mean_hist) 
                
                save_variable[model][emission_scenario]['precip_ratio'] = grand_precip
                print(f'{model}/{emission_scenario} saved!')
            
            # skip over model and emission scenario combos that don't exist in the dataset
            except OSError:
                save_variable[model][emission_scenario]['precip_ratio'] = 'File Not Found'
            
    return save_variable   

def delta_temp(save_variable, start_month = 6, stop_month = 8):
    
    """
    Returns the change in temperature from the historical to future period to a nested 
    dictionary under the model name and emission scenario. 
    The average temperature calculated is across all grid points in the given period.
    Save_variable should be the framework dictionary imported from reference_data.py.
    """
    
    # loop through all listed models and emission scenarios to open all available data
    for model in models:
        for emission_scenario in emission_scenarios:
            fpath = parent_directory.joinpath('JJA_climate_change', 'masked_MACA/')
            hist_min_path = fpath / f'MACA_{model}_{emission_scenario}_{start_month}-{stop_month}_1979-2014_tasmin_masked.nc'
            hist_max_path = fpath / f'MACA_{model}_{emission_scenario}_{start_month}-{stop_month}_1979-2014_tasmax_masked.nc'
            fut_min_path = fpath / f'MACA_{model}_{emission_scenario}_{start_month}-{stop_month}_2070-2099_tasmin_masked.nc'
            fut_max_path = fpath / f'MACA_{model}_{emission_scenario}_{start_month}-{stop_month}_2070-2099_tasmax_masked.nc'
            
            try:
                # find the mean for the historical period
                hist_ds_min = xr.open_dataset(hist_min_path)
                
                # calculate the average min temp for each year in the historical period
                hist_means_min = []
                for year in range(1979, 2015):
                    data_hist_min = hist_ds_min['tasmin'].sel(time = hist_ds_min.time.dt.year == year)
                    hist_mean_min = data_hist_min.mean(skipna= True).item()
                    hist_means_min.append(hist_mean_min)
                    
                # calculate the averagge max temp for each year in the historical period
                hist_ds_max = xr.open_dataset(hist_max_path)
                hist_means_max = []
                for year in range(1979, 2015):
                    data_hist_max = hist_ds_max['tasmax'].sel(time = hist_ds_max.time.dt.year == year)
                    hist_mean_max = data_hist_max.mean(skipna = True).item()
                    hist_means_max.append(hist_mean_max)    
                
                # finds the mean between average min and max values to get the overall historoical mean
                avg_hist = [(min + max)/2 for min, max in zip(hist_means_min, hist_means_max)]
                hist_val = float(np.mean(avg_hist))
                
                # finds the mean for the future period
                fut_ds_min = xr.open_dataset(fut_min_path)
                # calculate the yearly mean min temp for the future perriod
                fut_means_min = []
                for year in range(2070, 2099):
                    data_fut_min = fut_ds_min['tasmin'].sel(time = fut_ds_min.time.dt.year == year)
                    fut_mean_min = data_fut_min.mean(skipna= True).item()
                    fut_means_min.append(fut_mean_min)
                    
                fut_ds_max = xr.open_dataset(fut_max_path)
                # calculate the yearly mean max for the future period
                fut_means_max = []
                for year in range(2070, 2099):
                    data_fut_max = fut_ds_max['tasmax'].sel(time = fut_ds_max.time.dt.year == year)
                    fut_mean_max = data_fut_max.mean(skipna = True).item()
                    fut_means_max.append(fut_mean_max)    
                
                # finds the mean between average min and max values to get the overall future mean
                avg_fut = [(min + max)/2 for min, max in zip(fut_means_min, fut_means_max)]
                fut_val = float(np.mean(avg_fut))    
                    
                # calulate change in temperature and save data to dictionary
                grand_temp = fut_val - hist_val
                save_variable[model][emission_scenario]['delta_temp'] = grand_temp
                print(f'{model}/{emission_scenario} saved!')
                
            # skip over model and emission scenario combos that don't exist in the dataset
            except OSError:
                save_variable[model][emission_scenario]['delta_temp'] = 'File Not Found'
                
    return save_variable   

def scatter_plot(data_dict, save_name, save = False):
    
    """
    This function graphs data points stored in a nested dictionary (data_dict) by the functions above. 
    PC = True changes the size and colors of each point to reflect the respective PC scores assigned in 
    the climate analysis process. Note that PC1 and PC2 data was read in from a .csv file. See above 
    .csv data readin for more information. 
    """
    
    fig, ax = plt.subplots()
    marker_colors = ['purple', 'indigo', 'steelblue', 'darkcyan', 'seagreen', 'gold']
    
    for model in data_dict:
        for scenario in data_dict[model]:
            if data_dict[model][scenario]['delta_temp'] == 'File Not Found' or data_dict[model][scenario]['precip_ratio'] == 'File Not Found':
                continue

            marker = marker_colors[emission_scenarios.index(scenario)]
            scatter = ax.scatter(data_dict[model][scenario]['delta_temp'], data_dict[model][scenario]['precip_ratio'], c = marker, s = 25)
            
    # axis ticks and labels
    ax.set_yticks([0.5, 1.0, 1.5, 2.0])
    ax.set_yticklabels([0.5, 1, 1.5, 2])
    ax.set_xticks([0, 5, 10])

    # set horizontal and vertical lines
    ax.axhline(y = 0.5, color = 'lightgray', linewidth = 0.7)
    ax.axhline(y = 1.0, color = 'lightgray', linewidth = 0.7)
    ax.axhline(y = 1.5, color = 'lightgray', linewidth = 0.7)
    ax.axhline(y = 2.0, color = 'lightgray', linewidth = 0.7)
    ax.axvline(x = 0, color = 'lightgray', linewidth = 0.7)
    ax.axvline(x = 5, color = 'lightgray', linewidth = 0.7)
    ax.axvline(x = 10, color = 'lightgray', linewidth = 1.15)

    # remove the black outlines around the graph
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis='both', which='both', length=0)

    # labels for the graph
    ax.set_xlabel('Temperature Change (K)')
    ax.set_ylabel('Precipitation Ratio')

    # subtitle
    # ax.set_title('1979-2014 vs. 2070-2099', fontsize = 10, pad = 7)

    # creating a custom legend for emission scenarios
    my_legend = [Line2D([0], [0], marker = 'o', color = 'w', markersize = 8, 
              markerfacecolor = marker_colors[i], label = emission_scenarios[i])
     for i in range(len(emission_scenarios))]  
    ax.legend(handles = my_legend, loc = 'center left', bbox_to_anchor = (1.02, 0.5))
    
    # title
    # fig.suptitle("Climate Change's Impact on Summer Precipitation", fontsize = 20, y = 1.08)

    ax.text(8.4, 1.82, 'Wet Case', fontsize = 7, bbox = dict(edgecolor = 'white', facecolor = 'white'))
    ax.text(8.85, 0.97, 'Moderate Case', fontsize = 7, bbox = dict(edgecolor = 'white', facecolor = 'white'))
    ax.text(7.1, 0.55, 'Dry Case', fontsize = 7, bbox = dict(edgecolor = 'white', facecolor = 'white'))

    if save:
        save_path = current_file_directory.joinpath(f'JJA_climate_change', f'{save_name}.png')
        fig.savefig(save_path, dpi = 400, bbox_inches = 'tight', pad_inches = 0.1)
    else: 
        plt.show()
        
    return fig


# ================
# - Entry Point - 
# ================

def main(mask_data = False, calculate_precip_ratio = False, calculate_delta_temp = False):
    
    if mask_data:
        for model in models:
            for emission_scenario in emission_scenarios:
                try: 
                    mask_MACA(model, 'tasmax', emission_scenario, start_year = 2070, stop_year = 2099, save = True)
                    mask_MACA(model, 'tasmax', emission_scenario, start_year = 1979, stop_year = 2014, save = True)
                except OSError:
                    print(f'{model}_{emission_scenario} has not been downscaled using MACA.')   
                    continue
    
    # read saved data out of dictionary
    read_data = read_file('oct_19.txt', 'JJA_climate_change/')
    
    if calculate_precip_ratio:
        # calculate precip ratio and save data to dictionary
        save_pr = precip_ratio(read_data)
        write2file(save_pr, 'oct_19.txt', 'JJA_climate_change/')
    
    if calculate_delta_temp:
        # calculate the change in temperature and save data to a dictionary
        save_temp = delta_temp(read_data)
        write2file(save_temp, 'oct_19.txt', 'JJA_climate_change/')
         
    # read saved data from dictionary
    base_dict = read_file('oct_19.txt', 'JJA_climate_change/')
    # create scatter plot
    scatter_plot(base_dict, 'figure2')

if __name__ == '__main__':
    main()




