#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 29 11:52:03 2025

@author: u1301408
"""

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/packages/')
import base_packages as bp

# read out the dictionary from the .txt file
import ast

# Open and read the file
with open("oct_19.txt", "r") as f:
    contents = f.read()

# Convert from string representation to actual dictionary
base_dict = ast.literal_eval(contents)