#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 22 21:32:55 2025

@author: u1301408
"""

def delta_temp(save_variable, start_month = 6, stop_month = 8):
    
    # loop through all listed models and emission scenarios to open all available data
    for model in models:
        for emission_scenario in emission_scenarios:
            fpath = '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/scatter_plot/masked_MACA/'
            hist_min_path = f'{fpath}MACA_{model}_{emission_scenario}_{start_month}-{stop_month}_1979-2014_tasmin_masked.nc'
            hist_max_path = f'{fpath}MACA_{model}_{emission_scenario}_{start_month}-{stop_month}_1979-2014_tasmax_masked.nc'
            fut_min_path = f'{fpath}MACA_{model}_{emission_scenario}_{start_month}-{stop_month}_2070-2099_tasmin_masked.nc'
            fut_max_path = f'{fpath}MACA_{model}_{emission_scenario}_{start_month}-{stop_month}_2070-2099_tasmax_masked.nc'
            
            try:
                # find the mean for the historical period
                hist_ds_min = bp.xr.open_dataset(hist_min_path)
                hist_means_min = []
                for year in range(1979, 2015):
                    data_hist_min = hist_ds_min['tasmin'].sel(time = hist_ds_min.time.dt.year == year)
                    hist_mean_min = data_hist_min.mean(skipna= True).item()
                    hist_means_min.append(hist_mean_min)
                    
                hist_ds_max = bp.xr.open_dataset(hist_max_path)
                hist_means_max = []
                for year in range(1979, 2015):
                    data_hist_max = hist_ds_max['tasmax'].sel(time = hist_ds_max.time.dt.year == year)
                    hist_mean_max = data_hist_max.mean(skipna = True).item()
                    hist_means_max.append(hist_mean_max)    
                
                # finds the mean between average min and max values
                avg_hist = [(min + max)/2 for min, max in zip(hist_means_min, hist_means_max)]
                hist_val = float(bp.np.mean(avg_hist))
                
                # finds the mean for the future period
                fut_ds_min = bp.xr.open_dataset(fut_min_path)
                fut_means_min = []
                for year in range(2070, 2099):
                    data_fut_min = fut_ds_min['tasmin'].sel(time = fut_ds_min.time.dt.year == year)
                    fut_mean_min = data_fut_min.mean(skipna= True).item()
                    fut_means_min.append(fut_mean_min)
                    
                fut_ds_max = bp.xr.open_dataset(fut_max_path)
                fut_means_max = []
                for year in range(2070, 2099):
                    data_fut_max = fut_ds_max['tasmax'].sel(time = fut_ds_max.time.dt.year == year)
                    fut_mean_max = data_fut_max.mean(skipna = True).item()
                    fut_means_max.append(fut_mean_max)    
                
                # finds the mean between average min and max values
                avg_fut = [(min + max)/2 for min, max in zip(fut_means_min, fut_means_max)]
                fut_val = float(bp.np.mean(avg_fut))    
                    
                # calulate change in temperature and save data to dictionary
                grand_temp = fut_val - hist_val
                save_variable[model][emission_scenario]['delta_temp'] = grand_temp
                
            # skip over model and emission scenario combos that don't exist in the dataset
            except OSError:
                save_variable[model][emission_scenario]['delta_temp'] = 'File Not Found'
                
    return save_variable   