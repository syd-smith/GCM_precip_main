#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 09:07:53 2026

@author: u1301408
"""

import sys

sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/tool_belt/')
from file_traversing import write2file, read_file

models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5',
          'EC-Earth3-AerChem', 'EC-Earth3-CC', 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4',
          'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'IITM-ESM', 'INM-CM4-8', 'INM-CM5-0', 'KACE-1-0-G', 'KIOST-ESM', 
          'MIROC-ES2H', 'MIROC-ES2L', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']

seasons = ['DJF', 'MAM', 'JJA', 'SON']
variables = ['pr', 'tasmin', 'tasmax']

ranking = {}

for model in models:
    ranking[model] = {}
    for variable in variables:
        ranking[model][variable] = {}
        for season in seasons:
            ranking[model][variable][season] = 'x'
            
write2file(ranking, 'rank_mar3.txt', '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/model_performance/ranking/')
