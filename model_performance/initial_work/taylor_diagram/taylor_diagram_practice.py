#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 10 12:59:57 2025

@author: u1301408
"""

import geopandas as gpd
import numpy as np
import os
import sys
import xarray as xr
import xesmf as xe
from shapely.geometry import mapping

# evaluation of historical efficieny from 1979-2014 using an adpated version of a taylor diagram

# standard deviation : MACA
# correlation : MACA
# bias : GCM

# all data is only evaluated over the Great Salt Lake Basin (GSLB)


def mask_gridmet(start_month, stop_month, save = False):
    
    # Load in the shape file that contains the boundaries for the GSLB
    TOPO_DIR = "/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/gridmet/"
    gslb = gpd.read_file(TOPO_DIR + "WBD_16_HU2_Shape/Shape/WBDHU4.shp")
    gslb = gslb[gslb["huc4"] == "1602"]

    # decodes time information follownig the Climate and Weather metadata connvention
    time_coder = xr.coders.CFDatetimeCoder(use_cftime = True)

    fpath = '/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/gridmet/gsl_region_pr_1979-2014.nc'
    ds_open = xr.open_dataset(fpath, engine = "netcdf4", decode_times = time_coder)
    ds_years = ds_open['precipitation_amount'].sel(day = ds_open.day.dt.year.isin(range(1979, 2015)))
    ds_slice = ds_years.sel(day = ds_years.day.dt.month.isin(range(start_month, stop_month + 1)))

    ds = ds_slice.rio.write_crs("EPSG:4326")

    # Clips out the GSLB
    ds = ds.rio.clip(gslb.geometry.apply(mapping), gslb.crs, drop=False)
    
    if save == True:
        output_path = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/taylor_plot/masked/gridmet_{start_month}-{stop_month}_masked.nc'
        ds.to_netcdf(output_path)
        
    return ds


def mask_MACA(model_name, start_month, stop_month, save = False):
    
    # Load in the shape file that contains the boundaries for the GSLB
    TOPO_DIR = "/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/gridmet/"
    gslb = gpd.read_file(TOPO_DIR + "WBD_16_HU2_Shape/Shape/WBDHU4.shp")
    gslb = gslb[gslb["huc4"] == "1602"]

    # load file path for data
    fpath = '/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/output/netcdf/macav2metdata_GSLBIP_'
    
    # decodes time information follownig the Climate and Weather metadata connvention
    time_coder = xr.coders.CFDatetimeCoder(use_cftime = True)

    # open data for specifiedd model and slice to focus on specified months in the historical period
    ds_open = xr.open_dataset(fpath + model_name + '_ssp585_pr.nc', engine = "netcdf4", decode_times = time_coder)
    ds_years = ds_open['pr'].sel(time = ds_open.time.dt.year.isin(range(1979, 2015)))
    ds_slice = ds_years.sel(time = ds_years.time.dt.month.isin(range(start_month, stop_month + 1)))

    # applied data to standard coordinate system (not regridding)
    ds = ds_slice.rio.write_crs("EPSG:4326")

    # Clips out the GSLB
    ds = ds.rio.clip(gslb.geometry.apply(mapping), gslb.crs, drop=False)
    
    # saved masked dataset to directory
    if save == True:
        output_dir = '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/taylor_plot/masked/'
        output_name = f'MACA_{model_name}_{start_month}-{stop_month}_masked.nc'
        output_path = f'{output_dir}/{output_name}'
        
        ds.to_netcdf(output_path)
    
    return ds


def mask_GCM(model_name, start_month, stop_month, save = False):

    # Load in the shape file that contains the boundaries for the GSLB
    TOPO_DIR = "/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/gridmet/"
    gslb = gpd.read_file(TOPO_DIR + "WBD_16_HU2_Shape/Shape/WBDHU4.shp")
    gslb = gslb[gslb["huc4"] == "1602"]

    # load file path for data
    fpath = '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/ERA5/pr/pr_Amon_'
    
    # decodes time information follownig the Climate and Weather metadata connvention
    time_coder = xr.coders.CFDatetimeCoder(use_cftime = True)

    # open data for specifiedd model and slice to focus on specified months in the historical period
    ds_open = xr.open_mfdataset(fpath + model_name + '*.nc', engine = "netcdf4", decode_times = time_coder)
    ds_open = ds_open.sel(time=~ds_open.indexes['time'].duplicated())
    ds_years = ds_open['pr'].sel(time = ds_open.time.dt.year.isin(range(1979, 2015)))
    ds_slice = ds_years.sel(time = ds_years.time.dt.month.isin(range(start_month, stop_month + 1)))

    # regrid the GCM data to ennsure that at least a few gridpoints land within the mask boundaries
    ds_regrid = xr.Dataset(
            {
                "lat": (["lat"], np.arange(36, 43, 1)),
                "lon": (["lon"], np.arange(245, 251, 1)), #115, 109
            }
        )

    regridder = xe.Regridder(ds_slice, ds_regrid, 'bilinear')
    ds_regridded = regridder(ds_slice)

    # redefine longitude values to be -180 to 180 not 0 to 360
    ds_regridded.coords['lon'] = ((ds_regridded.coords['lon'] + 180) % 360) - 180
    ds_regridded = ds_regridded.sortby('lon')
    
    # applied data to standard coordinate system (not regridding)
    ds = ds_regridded.rio.write_crs("EPSG:4326")
    
    # note that GCM data required that the variable you wish to look at is specified
    ds = ds.rio.set_spatial_dims(x_dim = 'lon', y_dim = 'lat', inplace = False)

    # Clips out the GSLB
    ds = ds.rio.clip(gslb.geometry.apply(mapping), gslb.crs, drop=False)
    
    # saved masked dataset to directory
    if save == True:
        output_dir = '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/taylor_plot/masked/'
        output_name = f'GCM_{model_name}_{start_month}-{stop_month}_masked.nc'
        output_path = f'{output_dir}/{output_name}'
        
        ds.to_netcdf(output_path)
    
    return ds

# all masked data needing to be saved
# gridmet = mask_gridmet(8, 9, save = True)

# list of all models used in the MACA downscaling process
models_ssp585 = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5', 'EC-Earth3-CC',
 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'INM-CM4-8', 'INM-CM5-0',
 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']

# some models don't have ssp585 and therefore aren't relevant for skill analysis
# models_removed = ['EC-Earth3-AerChem', 'IITM-ESM', 'MIROC-ES2L']

# for model in models_ssp585[-5:]:
#     mask_MACA(model, 8, 9, save = True)

# files with duplicates: 9
for model in models_ssp585[10]:
    mask_GCM(model, 8, 9, save = True)


#%%
def st_dev_MACA(model_name, start_month, stop_month):
    
    # opens saved xarray from masking functions above
    fpath = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/taylor_plot/masked/GCM_{model_name}_{start_month}-{stop_month}_masked.nc'
    ds = xr.open_dataset(fpath)
    
    # raises error if specified file wasn't created above using masking functions
    if not os.path.isfile(ds):
        raise FileNotFoundError(f'File {ds} has not been saved for {model_name} for the months {start_month}-{stop_month}. Review functions above to create and save masked netcdf for MACA data over the GSLB.')  
   
    # make a list of yearly averages
    averages= []
    years = range(1979, 2015)
    for year in years:
        ds_year = ds.sel(time = ds.time.dt.year == year)
        ds_avg = ds_year.mean(skipna = True)
        averages.append(ds_avg.values)
     
    averages = np.array(averages)
    st_dev = np.std(averages)
    
    return st_dev

    
def st_dev_obs(start_month, stop_month):
    
    # open observational data and model dataset
    ds = xr.open_dataset(f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/taylor_plot/masked/st_dev_gridmet_{start_month}-{stop_month}_masked.nc')
   
    # raises error if specified file wasn't created above using masking functions
    if not os.path.isfile(ds):
        raise FileNotFoundError(f'File {ds} has not been saved for the months {start_month}-{stop_month}. Review functions above to create and save masked netcdf for observational data over the GSLB.')  
   
    # make a list of yearly averages
    averages= []
    years = range(1979, 2015)
    for year in years:
        ds_year = ds.sel(days = ds.days.dt.year == year)
        ds_avg = ds_year.mean(skipna = True)
        averages.append(ds_avg.values)
     
    averages = np.array(averages)
    st_dev = np.std(averages)
    
    return st_dev


def corcoef(model_name, start_month, stop_month):
    
    # open observational data and model dataset
    ds_gridmet = xr.open_dataset(f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/taylor_plot/masked/st_dev_gridmet_{start_month}-{stop_month}_masked.nc')
   
    # raises error if specified file wasn't created above using masking functions
    if not os.path.isfile(ds_gridmet):
        raise FileNotFoundError(f'File {ds_gridmet} has not been saved for the months {start_month}-{stop_month}. Review functions above to create and save masked netcdf for observational data over the GSLB.')  
   
    # opens saved xarray from masking functions above
    fpath = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/taylor_plot/masked/GCM_{model_name}_{start_month}-{stop_month}_masked.nc'
    ds_MACA = xr.open_dataset(fpath)
    
    # raises error if specified file wasn't created above using masking functions
    if not os.path.isfile(ds_MACA):
        raise FileNotFoundError(f'File {ds_MACA} has not been saved for {model_name} for the months {start_month}-{stop_month}. Review functions above to create and save masked netcdf for MACA data over the GSLB.')  
   
    # find correlation coefficient
    corcoef = xr.corr(ds_gridmet, ds_MACA, dim = 'time')
    
    return corcoef

def bias(model_name, start_month, stop_month):
    
    # open observational data
    ds_gridmet = xr.open_dataset(f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/taylor_plot/masked/st_dev_gridmet_{start_month}-{stop_month}_masked.nc')
    
    # raises error if specified file wasn't created above using masking functions
    if not os.path.isfile(ds_gridmet):
        raise FileNotFoundError(f'File {ds_gridmet} has not been saved for the months {start_month}-{stop_month}. Review functions above to create and save masked netcdf for observational data over the GSLB.')  
   
    # opens saved xarray from masking functions above
    fpath = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/taylor_plot/masked/GCM_{model_name}_{start_month}-{stop_month}_masked.nc'
    ds_model = xr.open_dataset(fpath)
    
    # raises error if specified file wasn't created above using masking functions
    if not os.path.isfile(ds_model):
        raise FileNotFoundError(f'File {ds_model} has not been saved for {model_name} for the months {start_month}-{stop_month}. Review functions above to create and save masked netcdf for GCM data over the GSLB.')  
   
    
    # find total mean of observational data to use for bias calculation
    obs_mean = ds_gridmet.mean(skipna = True)
    model_mean = ds_model.mean(skipna = True)
    
    # bias calculation
    bias = model_mean / obs_mean
    
    return [model, bias]
    
    
    