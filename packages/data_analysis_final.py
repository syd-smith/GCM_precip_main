#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 10 13:01:47 2025

@author: u1301408
"""

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/packages')
import base_packages as bp
import csv
from datetime import datetime, timedelta
import matplotlib.dates as mdates

input_file = '/uufs/chpc.utah.edu/common/home/u1301408/Downloads/trout_2906331_189211775_CR1000XSeries_LAB4_hourly.csv'

with open(input_file, mode = 'r') as file:
    header = next(file).strip().split(",")
    reader = list(csv.reader(file))
    
    # print(reader[26829][0]) #26109 - 26829
  
    timestamps = []
    battery_voltage = []
    temperature = []
    RH = []
    wind_speed = []
    peak_wind_speed = []
    wind_direction = []
    pressure = []
    solar_radiation = []
    
    for i, row in enumerate(reader[26109:26830]):
        ts = row[header.index('Hour')]
        dt = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
        timestamps.append(dt)
        
        battery_voltage.append(float(row[header.index('BattV')]))
        temperature.append(float(row[header.index('AirTC_Avg')]))
        RH.append(float(row[header.index('RH')]))
        wind_speed.append(float(row[header.index('WS_ms_Avg')]))
        peak_wind_speed.append(float(row[header.index('WS_ms_Max')]))
        wind_direction.append(float(row[header.index('WindDir')]))
        pressure.append(float(row[header.index('BP_hPa')]))
        solar_radiation.append(float(row[header.index('SlrW_Avg')]))













