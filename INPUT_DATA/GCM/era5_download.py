#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  1 09:20:07 2025

@author: u1301408
"""
# code from ECMWF climate data store to download netcdf files

# list of variables and models studied for Wilkes Summer Research 2025
variables_25 = ['precipitation', 'northward_near_surface_wind', 'easthward_near_surface_wind', 'geopotential_height', 'sea_level_pressure', 'near_surface_air_temperature']
models_25 = ['UKESM1-0-LL', 'ACCESS-CM2', 'CanESM5', 'KACE-1-0-G', 'MPI-ESM1-2-LR', 'CNRM-ESM2-1', 'CNRM-CM6-1-HR', 'INM-CM4-8']

# data download for continued analysis 7/29/2025
variables = ['surface_temperature', 'near_surface_specific_humidity'] # note: suraface temperature and near surface air temp are not the same
models = ['UKESM1-0-LL', 'ACCESS-CM2', 'CanESM5', 'KACE-1-0-G', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'MPI-ESM1-2-LR'] # sorted as wet, moderate, dry

# more monsoonal variables to look at 500 hPa level 9/2025
variables_huss = ['specific_humidity', 'eastward_wind', 'northward_wind']

# needed models for analysis of historical accuracy for precip (based on what models were downscaled for MACA)
MACA_models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5', 'EC-Earth3-AerChem', 'EC-Earth3-CC',
 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'IITM-ESM', 'INM-CM4-8', 'INM-CM5-0',
 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC-ES2L', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']

# not found
not_found = ['CNRM-CM6-1', 'EC-Earth3-AerChem', 'EC-Earth3-CC', 'EC-Earth3-Veg-LR', 'EC-Earth3', 'HadGEM3-GC31-LL', 'IITM-ESM', 
             'MIROC-ES2H', 'MIROC-ES2L', 'MPI-ESM1-2-HR']

import cdsapi

def download_hist(model, variable):
    dataset = "projections-cmip6"
    request = {
        "temporal_resolution": "monthly",
        "experiment": "historical",
        "variable": variable, 
        "level": [
            "500",
            "600",
            "700",
            "800",
            "900",
            "1000"],
        "model": model, 
        "month": [
            "01", "02", "03",
            "04", "05", "06",
            "07", "08", "09",
            "10", "11", "12"
        ],
        "year": [
            "2000", "2001", "2002",
            "2003", "2004", "2005",
            "2006", "2007", "2008",
            "2009", "2010", "2011",
            "2012", "2013", "2014",
            "1950", "1951", "1952",
            "1953", "1954", "1955",
            "1956", "1957", "1958",
            "1959", "1960", "1961",
            "1962", "1963", "1964",
            "1965", "1966", "1967",
            "1968", "1969", "1970",
            "1971", "1972", "1973",
            "1974", "1975", "1976",
            "1977", "1978", "1979",
            "1980", "1981", "1982",
            "1983", "1984", "1985",
            "1986", "1987", "1988",
            "1989", "1990", "1991",
            "1992", "1993", "1994",
            "1995", "1996", "1997",
            "1998", "1999"
        ]
    }

    client = cdsapi.Client()
    client.retrieve(dataset, request).download(f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/ERA5/hist_{model}_{variable}.zip')


for model in not_found:
    download_hist(model, 'tas')

# download precip data for all models downscaled to MACA
# 10, 11, -8 failed (doownload these with ESGF)
# for model in MACA_models[-7:]:
#     download_hist(model, variables_25[0])

# hus wont download for last 2
# download_hist(models[-1], 'hus')

# for model in models[-2]:
#     for variable in variables_huss[-2:]:
#         download_hist(model, variable)
        
# Had-LL through specific humidity

# no wind components for CanESM5
# download_hist(models[2], variables_huss[2])

# job failed -> check esgf
# download_hist(models[5], variables_25[3])
#%%

def download_fut(model, variable):
    dataset = "projections-cmip6"
    request = {
        "temporal_resolution": "monthly",
        "experiment": "ssp5_8_5",
        "variable": variable,
        "model": model,
        "year": [
            "2050", "2051", "2052",
            "2053", "2054", "2055",
            "2056", "2057", "2058",
            "2059", "2060", "2061",
            "2062", "2063", "2064",
            "2065", "2066", "2067",
            "2068", "2069", "2070",
            "2071", "2072", "2073",
            "2074", "2075", "2076",
            "2077", "2078", "2079",
            "2080", "2081", "2082",
            "2083", "2084", "2085",
            "2086", "2087", "2088",
            "2089", "2090", "2091",
            "2092", "2093", "2094",
            "2095", "2096", "2097",
            "2098", "2099"
        ],
        "month": [
            "01", "02", "03",
            "04", "05", "06",
            "07", "08", "09",
            "10", "11", "12"
        ]
    }

    client = cdsapi.Client()
    client.retrieve(dataset, request).download(f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/ERA5/fut_{model}_{variable}.zip')

# for model in models[3:]:
#     download_fut(model, variables[1])

# for variable in variables_25[3:]:
#     download_fut(models[5], variable)
    
# two caused issues -> try independently (needs to be run on esgf not working here)
# download_fut(models[2], variables[1])

# deleted file needs redownloaded
# multiple .nc files -> issues unzipping
# download_fut(models[5], variables_25[3])

# for model in models[6:]:
#     for variable in variables_huss:
#         download_fut(model, variable)

download_fut(models[-2], 'hus')
# download_fut(models[-2], 'ua')
# download_fut(models[-1], 'ua')
