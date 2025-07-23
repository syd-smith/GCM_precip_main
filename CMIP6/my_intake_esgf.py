#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 15:56:52 2025

@author: u1301408
"""
# inntake_esgf was used to suplement ECMWF to download needed datasets when unavailable elsewhere
# built following documentation for intake_esgf -> doesn't perform complete download functions

import intake_esgf
from intake_esgf import ESGFCatalog

cat = ESGFCatalog()
looking = cat.search(
    variable_id = 'pr', 
    experiment_id = 'historical', 
    table_id = 'Amon', 
    mip_era = 'CMIP6', 
    source_id = 'UKESM1-0-LL', 
    # member_id = 'r1i1p1f1', 
    activity_drs = ['CMIP', 'ScenarioMIP']
    )

dsd = cat.to_dataset_dict()
