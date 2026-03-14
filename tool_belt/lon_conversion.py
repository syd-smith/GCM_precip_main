#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 24 09:47:11 2026

@author: u1301408
"""

import numpy as np


def convert_lon_to_0_360(lon):
    # Convert longitude from -180-180 to 0-360
    lon = np.array(lon)
    lon_360 = (lon + 360) % 360
    return lon_360

def convert_lon_360_to_180(lon):
    #Convert longitude from 0360 range to -180 to 180 range
    lon = np.array(lon)  # Ensures input works for lists or arrays
    lon_180 = ((lon + 180) % 360) - 180
    return lon_180