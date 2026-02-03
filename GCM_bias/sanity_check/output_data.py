#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  3 14:00:23 2026

@author: u1301408
"""

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/tool_belt/')
from file_traversing import write2file, read_file

seasons = ['DJF', 'MAM', 'JJA', 'SON', 'yearly']

data = read_file('gcm_feb3.txt')

def model_review(model):

    for season in seasons:
        print(season)
        print(f'Precip bias for {season}: {data[model][season]['bias']['pr']}')
        print(f'Precip stdev ratio for {season}: {data[model][season]['stdev_ratio']['pr']}')
        print(f'Tasmin bias for {season}: {data[model][season]['bias']['tasmin']}')
        print(f'Tasmin stdev ratio for {season}: {data[model][season]['stdev_ratio']['tasmin']}')
        print(f'Tasmax bias for {season}: {data[model][season]['bias']['tasmax']}')
        print(f'Tasmax stdev ratio for {season}: {data[model][season]['stdev_ratio']['tasmax']}')
        print('--------------------')
        
    return model

model_review('CNRM-ESM2-1')