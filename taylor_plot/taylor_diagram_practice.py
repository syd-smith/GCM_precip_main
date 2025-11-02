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


# list of all models used in the MACA downscaling process
MACA_models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5', 'EC-Earth3-AerChem', 'EC-Earth3-CC',
 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'IITM-ESM', 'INM-CM4-8', 'INM-CM5-0',
 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC-ES2L', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']
    
# list of models that we currently have pr GCM data downloaded for
GCM_models = ['KACE-1-0-G', 'CanESM5', 'UKESM1-0-LL', 'ACCESS-CM2', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'MPI-ESM1-2-LR']


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

# lat      (lat) float32 672B 36.03 36.07 36.11 36.15 ... 42.9 42.94 42.98
# * lon      (lon) float32 684B -115.1 -115.1 -115.0 ... -108.1 -108.1 -108.0