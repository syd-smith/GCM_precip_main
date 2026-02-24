#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 24 12:28:31 2026

@author: u1301408
"""
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import rioxarray 
import xarray as xr

# all possible emission scenarios found in downscaled models
emission_scenarios = ['ssp119', 'ssp126', 'ssp245', 'ssp370', 'ssp434', 'ssp585']

# all possible models included in downscaling
models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1',
                 'CanESM5', 'EC-Earth3-CC', 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL',
                  'HadGEM3-GC31-MM', 'INM-CM4-8', 'INM-CM5-0', 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC6',
                   'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']

# APPLY MASK TO MACA DATA
def mask_MACA(model_name, variable, emission_scenario, start_month = 6, stop_month = 8, start_year = 1979, stop_year = 2014, save = False):
    
    """
    This function applies the boundaries of the GSLB to a given dataset through setting everything
    outside the boundaries to NAN. Default values return a NETCDF file with data for JJA over the 
    historical period. 
    
    Note: For this research, the historical period is defined as 1979 - 2014 and the future period 
          as 2070 - 2099.
    """
    
    # Load in the shape file that contains the boundaries for the GSLB
    TOPO_DIR = "/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/gridmet/"
    shp  = gpd.read_file(TOPO_DIR + "WBD_16_HU2_Shape/Shape/WBDHU4.shp")
    gsl  = shp[shp["huc4"] == "1602"]
    br   = shp[shp["huc4"] == "1601"]
    gslb = gpd.GeoDataFrame(geometry=[gsl.geometry.union_all().union(br.geometry.union_all())], crs=shp.crs)
    
    # decodes time information follownig the Climate and Weather metadata connvention
    time_coder = xr.coders.CFDatetimeCoder(use_cftime = True)
    
    # load file path for data
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
    # ds = rio.clip(gslb.geometry.apply(mapping), gslb.crs, drop=False)
    
    # saved masked dataset to directory
    if save == True:
        output_dir = '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/scatter_plot/masked_MACA/'
        output_name = f'MACA_{model_name}_{emission_scenario}_{start_month}-{stop_month}_{start_year}-{stop_year}_{variable}_masked.nc'
        output_path = f'{output_dir}{output_name}'
        
        ds.to_netcdf(output_path)
        print(f'Saved: {output_path}')
        return ds    
    
    return ds


for model in models:
    for emission_scenario in emission_scenarios:
        try: 
            mask_MACA(model, 'tasmax', emission_scenario, start_year = 2070, stop_year = 2099, save = True)
            mask_MACA(model, 'tasmax', emission_scenario, start_year = 1979, stop_year = 2014, save = True)
        except OSError:
            print(f'{model}_{emission_scenario} has not been downscaled using MACA.')   
            continue


    
# apply the model to one test then open and map it to see if boundary application was successful
mask_MACA(models[0], 'pr', emission_scenarios[1], save = True)

# open newly created dataset
fpath = '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/scatter_plot/masked_MACA/MACA_ACCESS-CM2_ssp126_6-8_1979-2014_pr_masked.nc'
ds = xr.open_dataset(fpath)

# plot data
ds['pr'].isel(time=0).plot()
plt.title("Precipitation for First Time Slice")
plt.show()