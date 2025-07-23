#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  1 09:20:07 2025

@author: u1301408
"""
# code from ECMWF climate data store to download netcdf files
# variables = ['precipitation', 'northward_near_surface_wind', 'easthward_near_surface_wind', 'geopotential_height', 'sea_level_pressure', 'near_surface_air_temperature']
# models = ['UKESM1-0-LL', 'ACCESS-CM2', 'CanESM5', 'KACE-1-0-G', 'MPI-ESM1-2-LR', 'CNRM-ESM2-1', 'CNRM-CM6-1-HR', 'INM-CM4-8']

import cdsapi

dataset = "projections-cmip6"
request = {
    "temporal_resolution": "monthly",
    "experiment": "historical",
    "variable": "precipitation", 
    "model": "CNRM-CM6-1-HR", 
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
client.retrieve(dataset, request).download()

#%%
import cdsapi

dataset = "projections-cmip6"
request = {
    "temporal_resolution": "monthly",
    "experiment": "ssp5_8_5",
    "variable": "near_surface_air_temperature",
    "model": "INM-CM4-8",
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
client.retrieve(dataset, request).download()


