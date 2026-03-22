#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  3 14:00:23 2026

@author: u1301408
"""

from pathlib import Path
import sys

current_file_directory = Path(__file__).resolve().parent
parent_directory = current_file_directory.parent
sys.path.append(str(parent_directory))

from tool_belt.file_traversing import read_file

seasons = ['DJF', 'MAM', 'JJA', 'SON', 'yearly']
data = read_file('gcm_feb19.txt')

def model_review(model):
    """
    Easily print all data for a specific model.
    """
    
    for season in seasons:
        print(season)
        print(f'Precip bias for {season}: {data[model][season]['bias']['pr']}')
        print(f'Precip variance ratio for {season}: {data[model][season]['var_ratio']['pr']}')
        print(f'Tasmin bias for {season}: {data[model][season]['bias']['tasmin']}')
        print(f'Tasmin variance ratio for {season}: {data[model][season]['var_ratio']['tasmin']}')
        print(f'Tasmax bias for {season}: {data[model][season]['bias']['tasmax']}')
        print(f'Tasmax variance ratio for {season}: {data[model][season]['var_ratio']['tasmax']}')
        print('--------------------')
        
    return model

model_review('CNRM-ESM2-1')