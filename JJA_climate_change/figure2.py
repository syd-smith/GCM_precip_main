#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 23 18:06:49 2025

@author: Sydney Smith
"""

import matplotlib.colors as mcolors
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import os
import pandas as pd
import pprint
import  sys
import xarray as xr

sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/tool_belt/')
from file_traversing import read_file, write2file


# Future Period: 2070-2099
# Historical Period: 1979-2014
# Temp Change: future - historical (C)
# Precip Ratio: future / historical 


# all possible emission scenarios found in downscaled models
emission_scenarios = ['ssp119', 'ssp126', 'ssp245', 'ssp370', 'ssp434', 'ssp585']

models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5',
          'EC-Earth3-AerChem', 'EC-Earth3-CC', 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4',
          'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'IITM-ESM', 'INM-CM4-8', 'INM-CM5-0', 'KACE-1-0-G', 'KIOST-ESM', 
          'MIROC-ES2H', 'MIROC-ES2L', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']
    
data_save = read_file('oct_19.txt', '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/JJA_climate_change/')

def precip_ratio(save_variable, start_month = 6, stop_month = 8):
    
    """
    Returns the percent change in precitation to a nested dictionary under the model 
    name and emission scenario. The average precip value is across the historical 
    period and all grid points.Save_variable should be the framework dictionary imported 
    from reference_data.py.
    """
    # loop through all listed models and emission scenarios to open all available data
    for model in models:
        for emission_scenario in emission_scenarios:
            
            fpath = '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/JJA_climate_change/masked_MACA/'
            hist_path = f'{fpath}MACA_{model}_{emission_scenario}_{start_month}-{stop_month}_1979-2014_pr_masked.nc'
            fut_path = f'{fpath}MACA_{model}_{emission_scenario}_{start_month}-{stop_month}_2070-2099_pr_masked.nc'
            
            try:
                # calculate precipitation ratio for data
                ds_hist = xr.open_dataset(hist_path)
                ds_fut = xr.open_dataset(fut_path)
                
                years_means_hist = []
                for year in range(1979, 2015):
                    year_dat_hist = ds_hist['pr'].sel(time = ds_hist.time.dt.year == year)
                    mean_hist = year_dat_hist.mean(skipna = True).item() # <- make sure to skip all NAN values outside the boundary
                    years_means_hist.append(mean_hist)
                grand_mean_hist = float(np.mean(years_means_hist))
                
                years_means_fut = []
                for year in range(2070, 2100):
                    year_dat_fut = ds_fut['pr'].sel(time = ds_fut.time.dt.year == year)
                    mean_fut = year_dat_fut.mean(skipna = True).item() # <- make sure to skip all NAN values outside the boundary
                    years_means_fut.append(mean_fut)
                grand_mean_fut = float(np.mean(years_means_fut))
                
                grand_precip = (grand_mean_fut/ grand_mean_hist) *100
                
                save_variable[model][emission_scenario]['precip_ratio'] = grand_precip
                print(f'{model}/{emission_scenario} saved!')
            
            # skip over model and emission scenario combos that don't exist in the dataset
            except OSError:
                save_variable[model][emission_scenario]['precip_ratio'] = 'File Not Found'
            
    return save_variable   

data_save = precip_ratio(data_save)


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
            fpath = '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/JJA_climate_change/masked_MACA/'
            hist_min_path = f'{fpath}MACA_{model}_{emission_scenario}_{start_month}-{stop_month}_1979-2014_tasmin_masked.nc'
            hist_max_path = f'{fpath}MACA_{model}_{emission_scenario}_{start_month}-{stop_month}_1979-2014_tasmax_masked.nc'
            fut_min_path = f'{fpath}MACA_{model}_{emission_scenario}_{start_month}-{stop_month}_2070-2099_tasmin_masked.nc'
            fut_max_path = f'{fpath}MACA_{model}_{emission_scenario}_{start_month}-{stop_month}_2070-2099_tasmax_masked.nc'
            
            try:
                # find the mean for the historical period
                hist_ds_min = xr.open_dataset(hist_min_path)
                hist_means_min = []
                for year in range(1979, 2015):
                    data_hist_min = hist_ds_min['tasmin'].sel(time = hist_ds_min.time.dt.year == year)
                    hist_mean_min = data_hist_min.mean(skipna= True).item()
                    hist_means_min.append(hist_mean_min)
                    
                hist_ds_max = xr.open_dataset(hist_max_path)
                hist_means_max = []
                for year in range(1979, 2015):
                    data_hist_max = hist_ds_max['tasmax'].sel(time = hist_ds_max.time.dt.year == year)
                    hist_mean_max = data_hist_max.mean(skipna = True).item()
                    hist_means_max.append(hist_mean_max)    
                
                # finds the mean between average min and max values
                avg_hist = [(min + max)/2 for min, max in zip(hist_means_min, hist_means_max)]
                hist_val = float(np.mean(avg_hist))
                
                # finds the mean for the future period
                fut_ds_min = xr.open_dataset(fut_min_path)
                fut_means_min = []
                for year in range(2070, 2099):
                    data_fut_min = fut_ds_min['tasmin'].sel(time = fut_ds_min.time.dt.year == year)
                    fut_mean_min = data_fut_min.mean(skipna= True).item()
                    fut_means_min.append(fut_mean_min)
                    
                fut_ds_max = xr.open_dataset(fut_max_path)
                fut_means_max = []
                for year in range(2070, 2099):
                    data_fut_max = fut_ds_max['tasmax'].sel(time = fut_ds_max.time.dt.year == year)
                    fut_mean_max = data_fut_max.mean(skipna = True).item()
                    fut_means_max.append(fut_mean_max)    
                
                # finds the mean between average min and max values
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

data_save = delta_temp(data_save)

# oct_19 = write2file(data_save, 'oct_19.txt', '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/JJA_climate_change/')
       

#%%
# read data from dictionary
base_dict = read_file('oct_19.txt', '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/JJA_climate_change/')


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
    ax.set_yticks([50, 100, 150, 200])
    ax.set_yticklabels([0.5, 1, 1.5, 2])
    ax.set_xticks([0, 5, 10])

    # set horizontal and vertical lines
    ax.axhline(y = 50, color = 'lightgray', linewidth = 0.7)
    ax.axhline(y = 100, color = 'lightgray', linewidth = 0.7)
    ax.axhline(y = 150, color = 'lightgray', linewidth = 0.7)
    ax.axhline(y = 200, color = 'lightgray', linewidth = 0.7)
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

    ax.text(9.2, 167.5, 'Wet Case', fontsize = 7, bbox = dict(edgecolor = 'white', facecolor = 'white'))
    ax.text(9, 100.6, 'Moderate Case', fontsize = 7, bbox = dict(edgecolor = 'white', facecolor = 'white'))
    ax.text(7.2, 54.75, 'Dry Case', fontsize = 7, bbox = dict(edgecolor = 'white', facecolor = 'white'))

    if save == True:
        save_path = os.path.join(f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/JJA_climate_change/{save_name}.png')
        fig.savefig(save_path, dpi = 400, bbox_inches = 'tight', pad_inches = 0.1)
    else: 
        plt.show()
        
    return fig

scatter_plot(base_dict, 'figure2')



