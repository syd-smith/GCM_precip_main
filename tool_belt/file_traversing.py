#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 29 13:02:07 2026

@author: u1301408
"""

import glob
import os
import ast
from pathlib import Path
import pprint

# ==================================
# - Establish Relative File Path - 
# ==================================

current_file_directory = Path(__file__).resolve().parent
print(f'CURRENT FILE DIRECTORY: {current_file_directory}')
parent_directory = current_file_directory.parent


# ==============
# - Functions - 
# ==============

def read_file(file_name, file_dir = 'model_performance'):
    
    """
    Read data out of .txt files.
    """
    # Open and read the file
    os.chdir(parent_directory.joinpath(file_dir))
    with open(file_name, 'r') as f:
        contents = f.read()

    # Convert from string representation to actual dictionary
    return_variable = ast.literal_eval(contents)
    
    return return_variable

def write2file(data, file_name, file_dir = 'model_performance'):
    
    """
    Write data into .txt files.
    """
    
    # save dictionary containing data to a specified file (after running it through the functions below)
    printer = pprint.PrettyPrinter(indent = 3, width = 100, sort_dicts = True)
    os.chdir(parent_directory.joinpath(file_dir))

    with open(file_name, 'w') as f:
        f.write(printer.pformat(data))
        
    return print(f'Success! {data} has been saved to {file_name}.')

def model_list(emission_scenario = '', delimiter = '_ssp'): 
    
    """
    Used to create list of models for each emission scenario by reading titles 
    of netcdf files.
    """
    
    # path to access netcdf files containing the data
    # TODO: change path to read data from where it is published
    strong_group_path = '/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/output/netcdf/macav2metdata_GSLBIP_'
    find_files = sorted(glob.glob(strong_group_path + '*{emission_scenario}.nc'))
    prefix = strong_group_path

    # makes list of all model names by editing file paths
    models = []
    for file in find_files:
        no_prefix = file.replace(prefix, '')
        model = no_prefix.split(delimiter)[0]
        if model not in models:
            models.append(model)
    
    return models