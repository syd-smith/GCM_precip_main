#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 24 14:17:20 2026

@author: u1301408
"""

from pathlib import Path
import sys
import xarray as xr

# ==================================
# - Establish Relative File Path - 
# ==================================

current_file_directory = Path(__file__).resolve().parent
parent_directory = current_file_directory.parent
sys.path.append(str(parent_directory))

import from_savanna.nclcmaps as cmap


# ===============
#  - Constants - 
# ===============

# finding min and max across datasets for each variable to infor variable_dict
models = ['KACE-1-0-G', 'CanESM5', 'UKESM1-0-LL', 'ACCESS-CM2', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'MPI-ESM1-2-LR']

# defines a dictionary that stores formatting information for each variable -> see else: for more information
variable_dict = {'psl' : {
                 'anomaly' : {
                      'cmap' : cmap.cmap('MPL_coolwarm'),
                       'cbar' : 'Change in Sea Level Pressure (hPa)',
                       'min' : -2.1117968559265137,
                       'max' : 3.2,
                       'title': 'Sea Level Pressure'
                  },
                  'region_mean' : 
                      {'cmap' : cmap.cmap('MPL_coolwarm'),
                       'cbar' : 'Mean Sea Level Pressure (hPa)',
                       'min' : 1002.8295312500001,
                       'max' : 1027.75984375,
                       'title': 'Sea Level Pressure'
                    }
                },
                'pr': {
                    'anomaly': {
                        'cmap': cmap.cmap('MPL_BrBG'),
                        'cbar': 'Change in Precipitation (%)',
                        'min': -75,
                        'max': 300,
                        'title': 'Precipitation'
                    },
                    'region_mean': {
                        'cmap': cmap.cmap('cmocean_haline', revBool=True),
                        'cbar': 'Mean Precipitation (mm)',
                        'min': 0.21196805760707713,
                        'max': 360,
                        'title': 'Precipitation'
                    }
                },
                'zg': {
                    'anomaly': {
                        'cmap': cmap.cmap('BlAqGrYeOrReVi200'),
                        'cbar': 'Change in 500-hPa Geopotential Height (m)',
                        'min': 75,
                        'max': 200,
                        'title': 'Geopotential Height'
                    },
                    'region_mean': {
                        'cmap': cmap.cmap('MPL_coolwarm'),
                        'cbar': 'Mean 500-hPa Geopotential Height (m)',
                        'min': 5676.18017578125,
                        'max': 5978.65869140625,
                        'title': 'Geopotential Height'
                    }
                },
                'vas': {
                    'anomaly': {
                        'cmap': cmap.cmap('CBR_wet'),
                        'cbar': 'Change in Northward Near Surface Wind (m s\u207B\u00B9)',
                        'min': -1.862033486366272,
                        'max': 3.81015682220459,
                        'title': 'Northward Near Surface Wind'
                    },
                    'region_mean': {
                        'cmap': cmap.cmap('MPL_coolwarm'),
                        'cbar': 'Mean Northward Near Surface Wind (m s\u207B\u00B9)',
                        'min': -9.491390228271484,
                        'max': 6.107685565948486,
                        'title': 'Northward Near Surface Wind'
                    }
                },
                'uas': {
                    'anomaly': {
                        'cmap': cmap.cmap('CBR_wet'),
                        'cbar': 'Change in Eastward Near Surface Wind (m s\u207B\u00B9)',
                        'min': -3.5138015747070312,
                        'max': 2.595974922180176,
                        'title': 'Eastward Near Surface Wind'
                    },
                    'region_mean': {
                        'cmap': cmap.cmap('MPL_coolwarm'),
                        'cbar': 'Mean Eastward Near Surface Wind (m s\u207B\u00B9)',
                        'min': -11.079482078552246,
                        'max': 5.9408488273620605,
                        'title': 'Eastward Near Surface Wind'
                    }
                },
                'ts': {
                    'anomaly': {
                        'cmap': cmap.cmap('MPL_YlOrRd'),
                        'cbar': 'Change in Surface Temperature (K)',
                        'min': 0.475433349609375,
                        'max': 15.549346923828125,
                        'title': 'Surface Temperature'
                    },
                    'region_mean': {
                        'cmap': cmap.cmap('MPL_YlOrRd'),
                        'cbar': 'Mean Surface Temperature (K)',
                        'min': 281.8443298339844,
                        'max': 318.0555114746094,
                        'title': 'Surface Temperature'
                    }
                },
                'huss': {
                    'anomaly': {
                        'cmap': cmap.cmap('MPL_YlGnBu'),
                        'cbar': 'Change in Near Surface Specific Humidity (g/kg)',
                        'min': 0,
                        'max': 7.801617622375488,
                        'title': 'Near Surface Specific Humidity'
                    },
                    'region_mean': {
                        'cmap': cmap.cmap('cmocean_haline', revBool=True),
                        'cbar': 'Mean Near Surface Specific Humidity (g/kg)',
                        'min': 4.40641213208437,
                        'max': 27.03595533967018,
                        'title': 'Near Surface Specific Humidity'
                    }
                },
                'hus': {
                    'anomaly': {
                        'cmap': cmap.cmap('MPL_YlGnBu'),
                        # 'cbar': f'Change in Specific Humidity (g/kg) at {level} Pa',
                        'min': 0,
                        'max': 3.5, #7801.617622375488,
                        'title': 'Specific Humidity'
                    },
                    'region_mean': {
                        'cmap': cmap.cmap('cmocean_haline', revBool=True),
                        # 'cbar': f'Mean Specific Humidity (g/kg) at {level} Pa',
                        'min': 0.9462222806178033,
                        'max': 6, #4.642414394766092,
                        'title': 'Specific Humidity'
                    }
                },
                'ua': {
                    'anomaly': {
                        'cmap': cmap.cmap('MPL_YlGnBu'),
                        'cbar': 'Change in Near Surface Specific Humidity (g/kg)',
                        'min': 0,
                        'max': 7.801617622375488,
                        'title': 'Near Surface Specific Humidity'
                    },
                    'region_mean': {
                        'cmap': cmap.cmap('cmocean_haline', revBool=True),
                        'cbar': 'Mean Near Surface Specific Humidity (g/kg)',
                        'min': 4.40641213208437,
                        'max': 27.03595533967018,
                        'title': 'Near Surface Specific Humidity'
                    }
                },
                'va': {
                    'anomaly': {
                        'cmap': cmap.cmap('MPL_YlGnBu'),
                        'cbar': 'Change in Near Surface Specific Humidity (g/kg)',
                        'min': 0,
                        'max': 7.801617622375488,
                        'title': 'Near Surface Specific Humidity'
                    },
                    'region_mean': {
                        'cmap': cmap.cmap('cmocean_haline', revBool=True),
                        'cbar': 'Mean Near Surface Specific Humidity (g/kg)',
                        'min': 4.40641213208437,
                        'max': 27.03595533967018,
                        'title': 'Near Surface Specific Humidity'
                    }
                }
            }
    
    
# ==============
# - Functions - 
# ==============    

def min_max(variable):
    """
    Used to define region_mean min and max values in variable_dict by finding 
    the min and max values out of all models for the given variable.
    """
    
    all_mins = []
    all_maxs = []
    for model in models:
        fpath = parent_directory.joinpath('INPUT_DATA', variable, f'{variable}_Amon_{model}*.nc')
        ds = xr.open_mfdataset(fpath)
        ds = ds[variable].sel(lat = slice(15, 53), lon = slice(215, 295))
        ds = ds.sel(time = ds.time.dt.month.isin([6, 7, 8]))
        years = range(1985, 2099)
        if variable == 'zg' or variable == 'hus':
            ds = ds.sel(plev = 50000, method = 'nearest')
        means = []
        for year in years:
            one_year = ds.sel(time = ds.time.dt.year == year)
            # GCM pr data is in precipitation flux so the time unit has to be taken out
            if variable == 'pr':
                days_in_month = ds.time.dt.days_in_month
                seconds_per_month = days_in_month * 24 * 60 * 60
                mean = (one_year * seconds_per_month).mean(dim = 'time')
            else:
                mean = one_year.mean(dim = 'time')
            means.append(mean)
        combine = xr.concat(means, dim = 'year')
        total_mean = combine.mean(dim = 'year')
        data_min = float(total_mean.min())
        data_max = float(total_mean.max())
            
        if variable == 'psl':
            data_min *= 0.01 # convert from Pa to hPa
            data_max *= 0.01
        elif variable == 'huss':
            data_min *= 1000 # convert from kg/kg to g/kg
            data_max *= 1000
                
        all_mins.append(data_min)
        all_maxs.append(data_max)
            
    final_min = min(all_mins)
    final_max = max(all_maxs)
    
    result = f'Min for {variable}: {final_min}\nMax for {variable}: {final_max}'
    return result

def anom_min_max(variable):
    """
    Used to define anomaly min and max values in variable_dict by first calculating
    each models anomaly and then finding the min and max values out of all models 
    for the given variable.
    """
    
    all_mins = []
    all_maxs = []
    for model in models:
        hist_fpath = parent_directory.joinpath('INPUT_DATA', variable, f'{variable}_Amon_{model}_hist*.nc')
        open_hist = xr.open_mfdataset(hist_fpath)
        fut_fpath = parent_directory.joinpath('INPUT_DATA', variable, f'{variable}_Amon_{model}_ssp*.nc')
        open_fut = xr.open_mfdataset(fut_fpath)
     
        open_hist = open_hist[variable].sel(lat = slice(15, 53), lon = slice(215, 295))
        open_hist = open_hist.sel(time = open_hist.time.dt.month.isin([6, 7, 8]))
        
        open_fut = open_fut[variable].sel(lat = slice(15, 53), lon = slice(215, 295))
        open_fut = open_fut.sel(time = open_fut.time.dt.month.isin([6, 7, 8]))
    
        # geopotential height has an extra dimension for what pressure level you want to look at (we chose 500 hPa)
        if variable == 'zg' or variable == 'hus':
            open_hist = open_hist.sel(plev = 50000, method = 'nearest')
            open_fut = open_fut.sel(plev = 50000, method = 'nearest')
            
        years_hist = range(1985, 2015)
        means_hist = []
        for year in years_hist:
            year_hist = open_hist.sel(time = open_hist.time.dt.year == year)
            mean_hist = year_hist.mean(dim = 'time')
            means_hist.append(mean_hist)        
        combine_means_hist = xr.concat(means_hist, dim = 'year')
        overall_mean_hist = combine_means_hist.mean(dim = 'year')

        years_fut = range(2070, 2100)
        means_fut = []
        for year in years_fut:
            year_fut = open_fut.sel(time = open_fut.time.dt.year == year)
            mean_fut = year_fut.mean(dim = 'time', skipna = True)
            means_fut.append(mean_fut)
        combine_means_fut = xr.concat(means_fut, dim = 'year')
        overall_mean_fut = combine_means_fut.mean(dim = 'year')
       
        # Sets up all variables as a difference between time periods except for precipitation as a percent change
        if variable == 'pr':
            anomaly = ((overall_mean_fut - overall_mean_hist) / overall_mean_hist) * 100
        else:
            anomaly = overall_mean_fut - overall_mean_hist
        
        # conversions for some variables
        if variable == 'psl':
            anomaly *= 0.01 # convert from Pa to hPa
        elif variable == 'huss':
            anomaly *= 1000 # convert from kg/kg to g/kg
            
        # find min and max of all returned anomalies
        data_max = float(anomaly.max())
        data_min = float(anomaly.min())
        
        all_mins.append(data_min)
        all_maxs.append(data_max)
    
    total_min = min(all_mins)
    total_max = max(all_maxs)
    result = f'Anom min for {variable}: {total_min}\nAnom max for {variable}: {total_max}'
        
    return result


    