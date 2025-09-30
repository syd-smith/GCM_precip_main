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
# bias : GCM

# all data is only evaluated over the Great Salt Lake Basin (GSLB)


def mask_gridmet(start_month, stop_month, save = False):
    
    # Load in the shape file that contains the boundaries for the GSLB
    TOPO_DIR = "/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/gridmet/"
    gslb = bp.gpd.read_file(TOPO_DIR + "WBD_16_HU2_Shape/Shape/WBDHU4.shp")
    gslb = gslb[gslb["huc4"] == "1602"]

    # decodes time information follownig the Climate and Weather metadata connvention
    time_coder = bp.xr.coders.CFDatetimeCoder(use_cftime = True)

    fpath = '/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/gridmet/gsl_region_pr_1979-2014.nc'
    ds_open = bp.xr.open_dataset(fpath, engine = "netcdf4", decode_times = time_coder)
    ds_years = ds_open['precipitation_amount'].sel(day = ds_open.day.dt.year.isin(range(1979, 2015)))
    ds_slice = ds_years.sel(day = ds_years.day.dt.month.isin(range(start_month, stop_month + 1)))

    ds = ds_slice.rio.write_crs("EPSG:4326")

    # Clips out the GSLB
    ds = ds.rio.clip(gslb.geometry.apply(bp.mapping), gslb.crs, drop=False)
    
    if save == True:
        output_path = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/taylor_plot/masked/st_dev_gridmet_{start_month}-{stop_month}_masked.nc'
        ds.to_netcdf(output_path)
        
    return ds


def mask_MACA(model_name, start_month, stop_month, save = False):
    
    # Load in the shape file that contains the boundaries for the GSLB
    TOPO_DIR = "/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/gridmet/"
    gslb = bp.gpd.read_file(TOPO_DIR + "WBD_16_HU2_Shape/Shape/WBDHU4.shp")
    gslb = gslb[gslb["huc4"] == "1602"]

    # load file path for data
    fpath = '/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/output/netcdf/macav2metdata_GSLBIP_'
    
    # decodes time information follownig the Climate and Weather metadata connvention
    time_coder = bp.xr.coders.CFDatetimeCoder(use_cftime = True)

    # open data for specifiedd model and slice to focus on specified months in the historical period
    ds_open = bp.xr.open_mfdataset(fpath + model_name + '*ssp585_pr.nc', engine = "netcdf4", decode_times = time_coder)
    ds_years = ds_open['pr'].sel(time = ds_open.time.dt.year.isin(range(1979, 2015)))
    ds_slice = ds_years.sel(time = ds_years.time.dt.month.isin(range(start_month, stop_month + 1)))

    # applied data to standard coordinate system (not regridding)
    ds = ds_slice.rio.write_crs("EPSG:4326")

    # Clips out the GSLB
    ds = ds.rio.clip(gslb.geometry.apply(bp.mapping), gslb.crs, drop=False)
    
    # saved masked dataset to directory
    if save == True:
        output_dir = '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/taylor_plot/masked/'
        output_name = f'st_dev_{model_name}_MACA_{start_month}-{stop_month}_masked.nc'
        output_path = f'{output_dir}/{output_name}'
        
        ds.to_netcdf(output_path)
    
    return ds


def mask_GCM(model_name, start_month, stop_month, save = False):

    # Load in the shape file that contains the boundaries for the GSLB
    TOPO_DIR = "/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/gridmet/"
    gslb = bp.gpd.read_file(TOPO_DIR + "WBD_16_HU2_Shape/Shape/WBDHU4.shp")
    gslb = gslb[gslb["huc4"] == "1602"]

    # load file path for data
    fpath = '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/ERA5/pr/pr_Amon_'
    
    # decodes time information follownig the Climate and Weather metadata connvention
    time_coder = bp.xr.coders.CFDatetimeCoder(use_cftime = True)

    # open data for specifiedd model and slice to focus on specified months in the historical period
    ds_open = bp.xr.open_mfdataset(fpath + model_name + '*.nc', engine = "netcdf4", decode_times = time_coder)
    ds_years = ds_open['pr'].sel(time = ds_open.time.dt.year.isin(range(1979, 2015)))
    ds_slice = ds_years.sel(time = ds_years.time.dt.month.isin(range(start_month, stop_month + 1)))

    # regrid the GCM data to ennsure that at least a few gridpoints land within the mask boundaries
    # look at where these points land and how central they are to the region
    ds_regrid = bp.xr.Dataset(
            {
                "lat": (["lat"], bp.np.arange(36, 43, 1)),
                "lon": (["lon"], bp.np.arange(245, 251, 1)), #115, 109
            }
        )

    regridder = bp.xe.Regridder(ds_slice, ds_regrid, 'bilinear')
    ds_regridded = regridder(ds_slice)

    # redefine longitude values to be -180 to 180 not 0 to 360
    ds_regridded.coords['lon'] = ((ds_regridded.coords['lon'] + 180) % 360) - 180
    ds_regridded = ds_regridded.sortby('lon')
    
    # applied data to standard coordinate system (not regridding)
    ds = ds_regridded.rio.write_crs("EPSG:4326")

    # Clips out the GSLB
    ds = ds.rio.clip(gslb.geometry.apply(bp.mapping), gslb.crs, drop=False)
    
    # saved masked dataset to directory
    if save == True:
        output_dir = '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/taylor_plot/masked/'
        output_name = f'st_dev_{model_name}_GCM_{start_month}-{stop_month}_masked.nc'
        output_path = f'{output_dir}/{output_name}'
        
        ds.to_netcdf(output_path)
    
    return ds

# all masked data needing to be saved
gridmet = mask_gridmet(8, 9, save = True)

# list of all models used in the MACA downscaling process
MACA_models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5', 'EC-Earth3-AerChem', 'EC-Earth3-CC',
 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'IITM-ESM', 'INM-CM4-8', 'INM-CM5-0',
 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC-ES2L', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']
for model in MACA_models:
    mask_MACA(model, 8, 9, save = True)
    
# list of models that we currently have pr GCM data downloaded for
GCM_models = ['KACE-1-0-G', 'CanESM5', 'UKESM1-0-LL', 'ACCESS-CM2', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'MPI-ESM1-2-LR']
for model in GCM_models:
    mask_GCM(model, 8, 9, save = True)


def st_dev_MACA(dataset):
    
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
