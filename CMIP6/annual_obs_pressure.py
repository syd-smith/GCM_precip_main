#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 27 12:56:06 2026

@author: u1301408
"""
import csv
from itertools import islice
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates


fpath_2025 = '/uufs/chpc.utah.edu/common/home/u1301408/Downloads/KSLC.2025-12-31.csv'
fpath_lt  = ''

def open_CSV(f_path, header_line, delimiter):
    with open(f_path, mode = 'r') as file:
        list(islice(file, header_line -1)) # skip all lines before the header 

        header = next(file).strip().split(delimiter)
        units   = next(file).strip().split(delimiter) 

        reader = list(csv.reader(file))
        
    return reader, header, units


def time_conversion(reader, column_number):
    time = []
    for row in reader:
        dt = datetime.strptime(
            row[column_number], '%Y-%m-%dT%H:%M:%SZ')
        time.append(dt)

    return time

# test, header, units = open_CSV(fpath_2025, 11, ',')
# time = time_conversion(test, 1)

long_term_data, header, units = open_CSV(fpath_lt, 5, ',')
time = time_conversion(long_term_data, 1)


#%%

empty_rows = [i for i, row in enumerate(test) if len(row) > 2 and row[5] == '']
print("Rows with empty row[2]:", empty_rows)

#%%
x_vals = [time[i] for i, holder in enumerate(time)
          if i not in empty_rows]
y_vals = [float(row[5]) / 100 
          for i, row in enumerate(test)
          if i not in empty_rows]

plt.plot(x_vals, y_vals)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
plt.xticks(rotation = 45, ha = 'right')
plt.title('Annual Surface Pressure Variation - 2025')
plt.ylabel('Pressure (hPa)')

    
    