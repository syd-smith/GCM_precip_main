#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 10 12:59:57 2025

@author: u1301408
"""

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/packages')
import base_packages as bp

# evaluation of historical efficieny from 1979-2014 using an adpated version of a taylor diagram

# standard deviation : MACA
# correlation : MACA
# bias : GCM (shown on colorscale)


# list of all models used in the MACA downscaling process
MACA_models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5', 'EC-Earth3-AerChem', 'EC-Earth3-CC',
 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'IITM-ESM', 'INM-CM4-8', 'INM-CM5-0',
 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC-ES2L', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']
    
# list of models that we currently have pr GCM data downloaded for
GCM_models = ['KACE-1-0-G', 'CanESM5', 'UKESM1-0-LL', 'ACCESS-CM2', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'MPI-ESM1-2-LR']

# find the variable average for every grid point across the historical period before doing calculations
# same averaging can be used for standard deviation and correlation
# learn how to read GCM data out of matlab files
# make taylor plot repeatable for different variables



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

def maca_time_avg(model, variable):
    ds = bp.xr.open_dataset(f'/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/output/netcdf/macav2metdata_GSLBIP_{model}_ssp585_{variable}.nc')
    time_average = ds.mean(skipna = True, dims = 'time')
    return time_average

test = maca_time_avg(MACA_models[0], 'pr')
#%%
def st_dev_MACA(dataset):
    # THIS IS CURRENTLY SETUP TO CALCULATE TEMPORAL STANDARD DEVIATION
    
    # calls data from a specified file path (meant to call saved masked data to prevent masking everytime)
    ds = bp.xr.open_dataset(dataset)
    
    # make a list of yearly averages
    averages= []
    years = range(1979, 2015)
    for year in years:
        ds_year = ds.sel(time = ds.time.dt.year == year)
        ds_avg = ds_year.mean(skipna = True)
        averages.append(ds_avg.values)
     
    averages = bp.np.array(averages)
    st_dev = bp.np.std(averages)
    
    return st_dev

    
def st_dev_obs(dataset):
    
    # calls gridmet data from a specified file path (meant to call saved masked data to prevent masking everytime)
    ds = bp.xr.open_dataset(dataset)
    
    # make a list of yearly averages
    averages= []
    years = range(1979, 2015)
    for year in years:
        ds_year = ds.sel(days = ds.days.dt.year == year)
        ds_avg = ds_year.mean(skipna = True)
        averages.append(ds_avg.values)
     
    averages = bp.np.array(averages)
    st_dev = bp.np.std(averages)
    
    return st_dev

# lat      (lat) float32 672B 36.03 36.07 36.11 36.15 ... 42.9 42.94 42.98
# * lon      (lon) float32 684B -115.1 -115.1 -115.0 ... -108.1 -108.1 -108.0

# PolarAxes.PolarTransform() # this tells plot to set std for radius and cor for angle
# diagram = TaylorDiagram(reference.std(ddof=1), fig=myfig)
# diagram.add_sample(stddev2, corrcoef2, label = 'Model 2', marker = 'o')

#%%

ds = bp.scipy.io.loadmat('/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/coarse_grid/ACCESS-CM2_historical_pr.mat')

var = bp.np.squeeze(ds['interpolated_data'])
# year = bp.np.squeeze(ds['year'])

print(var.shape)
# print(day_of_year.shape)


#%%
ds_maca = bp.xr.open_dataset('/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/output/netcdf/macav2metdata_GSLBIP_ACCESS-CM2_ssp126_pr.nc')










