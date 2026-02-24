#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 15:56:52 2025

@author: u1301408
"""
# intake_esgf was used to suplement ECMWF to download needed datasets when unavailable elsewhere
# built following documentation for intake_esgf -> doesn't perform complete download functions

import intake_esgf
from intake_esgf import ESGFCatalog

# surface_air_pressure
# variables_to_check  = ['ps']

# list of models used in MACA process
ssp119_models = ['CNRM-ESM2-1', 'CanESM5', 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-ESM4', 'MIROC-ES2H',
                 'MIROC-ES2L', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']
ssp126_models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2',
                 'CanESM5', 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-ESM4', 'HadGEM3-GC31-LL', 'IITM-ESM',
                 'INM-CM4-8', 'INM-CM5-0', 'KACE-1-0-G', 'MIROC-ES2H', 'MIROC-ES2L', 'MIROC6', 'MPI-ESM1-2-HR',
                 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']
ssp126_not_found = ['CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-CM6-1', 'CNRM-ESM2-1']

# used to look at multiple emission scenarios
# set ssp = ssps
ssps = ['ssp119', 'ssp126', 'ssp245', 'ssp434', 'ssp370', 'ssp585']

for model in ssp126_models[-5]:
    cat = ESGFCatalog()
    looking = cat.search(
        variable_id = 'ps', 
        experiment_id = 'ssp126', 
        table_id = 'Amon', 
        mip_era = 'CMIP6', 
        source_id = model, 
        # member_id = 'r1i1p1f1', 
        activity_drs = ['ScenarioMIP'],
        grid_label =  'gn'
        )
    print(f'{model} downloaded!')



ds_dict = cat.to_dataset_dict()


# https://aims2.llnl.gov/search 
# used this website for download when downloads took too long
# website downloads wget -> follow commands below for .nc
# chmod 744 wget***.sh
# ./wget***.sh
