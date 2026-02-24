#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 29 11:52:03 2025

@author: u1301408
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.ticker as ticker
import numpy as np
import os
import sys

sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/tool_belt/')
from file_traversing import read_file

# read in PC data from tabular format in Savanna's .csv file
df = pd.read_csv('/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/climate_analysis/pca/PCs_zscore_column.csv')
scatter_framework = read_file('dictionary_structure.txt', '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/JJA_climate_change/')

# _ refers to the rows while rows really refers to the columns
for row, col in df.iterrows():
    model = col['Model']
    exp = col['Exp']
    
    record = {
        'delta_temp' : 0,
        'precip_ratio' : 0,
        'PC1' : float(col['PC1']),
        'PC2' : float(col['PC2'])}
    
    # input PC data into the dictionary framework foound in reference_data.py (use this dictionary to compile more data with the calculations below)
    scatter_framework.setdefault(model, {})[exp] = record


# Open and read the file
data_dict = read_file('oct_19.txt', '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/JJA_climate_change/')

# establish figure for subplots
fig, axs = plt.subplots(1, 2, figsize = (13.5, 6))

# loop through dictionary to pull out necessary data for scatter
for model in data_dict:
    for scenario in data_dict[model]:
        if data_dict[model][scenario]['delta_temp'] == 'File Not Found' or data_dict[model][scenario]['precip_ratio'] == 'File Not Found':
            continue
        # adjust color of data point relative to PC value
        PC1_scatter = axs[0].scatter(data_dict[model][scenario]['delta_temp'], 
                              data_dict[model][scenario]['precip_ratio'], 
                              c = data_dict[model][scenario]['PC1'], 
                              cmap = plt.get_cmap('viridis', 9), 
                              s = 100, 
                              norm = mcolors.Normalize(vmin = -10, vmax = 18))
        PC2_scatter = axs[1].scatter(data_dict[model][scenario]['delta_temp'], 
                              data_dict[model][scenario]['precip_ratio'], 
                              c = data_dict[model][scenario]['PC2'], 
                              cmap = plt.get_cmap('viridis', 9), 
                              s = 100, 
                              norm = mcolors.Normalize(vmin = -5, vmax = 6))
        
# loop through both subplots to add visual features        
for ax in [0, 1]:        
    # axis ticks and labels
    axs[ax].set_yticks([50, 100, 150, 200])
    axs[ax].set_yticklabels([0.5, 1, 1.5, 2])
    axs[ax].set_xticks([0, 5, 10])
    axs[ax].tick_params(axis = 'x', labelsize=12)
    axs[ax].tick_params(axis = 'y', labelsize=12)

    # set horizontal and vertical lines
    axs[ax].axhline(y = 50, color = 'lightgray', linewidth = 0.7)
    axs[ax].axhline(y = 100, color = 'lightgray', linewidth = 0.7)
    axs[ax].axhline(y = 150, color = 'lightgray', linewidth = 0.7)
    axs[ax].axhline(y = 200, color = 'lightgray', linewidth = 0.7)
    axs[ax].axvline(x = 0, color = 'lightgray', linewidth = 0.7)
    axs[ax].axvline(x = 5, color = 'lightgray', linewidth = 0.7)
    axs[ax].axvline(x = 10, color = 'lightgray', linewidth = 1.15)

    # remove the black outlines around the graph
    for spine in axs[ax].spines.values():
        spine.set_visible(False)
    axs[ax].tick_params(axis='both', which='both', length=0)

    # labels for the graph
    axs[ax].set_xlabel('Temperature Change (K)', fontsize = 16)
    axs[ax].set_ylabel('Precipitation Ratio', fontsize = 16)

# define norm and levels for PC1
PC1_levels = np.linspace(-10, 18, 9)
# PC1_norm = mcolors.BoundaryNorm(PC1_levels, ncolors = plt.get_cmap(cmap.cmap('MPL_BrBG'), 9).N)

# creating a color bar and legend for PC1 and PC2 data
PC1_cbar = plt.colorbar(PC1_scatter, 
                           orientation = 'horizontal', 
                           ticks = PC1_levels, 
                           shrink = 0.5, 
                           pad = 0.05,
                           extend = 'both',
                           boundaries = PC1_levels)
PC1_cbar.ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))

# define norm and levels for PC2
PC2_levels = np.linspace(-5, 6, num = 9)
# PC2_norm = mcolors.BoundaryNorm(PC1_levels, ncolors = plt.get_cmap(cmap.cmap('MPL_BrBG'), 9).N)

PC2_cbar = plt.colorbar(PC2_scatter, 
                           orientation = 'horizontal', 
                           ticks = PC2_levels, 
                           shrink = 0.5, 
                           pad = 0.05,
                           extend = 'both', 
                           boundaries = PC2_levels)
PC2_cbar.ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))

# add labels to each subplot
axs[0].text(0.05, 0.85, 'a.', fontsize = 20, transform = axs[0].transAxes)
axs[1].text(0.05, 0.85, 'b.', fontsize = 20, transform = axs[1].transAxes)

# save figure
# save_name = 'figure4.png'
# save_path = os.path.join(f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/JJA_climate_change/PC/{save_name}.png')
# fig.savefig(save_path, dpi = 400, bbox_inches = 'tight', pad_inches = 0.1)

plt.show()


#%%
# search for mins and maxs in PC data
PC1_dat = []
PC2_dat = []
for model in data_dict:
    for scenario in data_dict[model]:
        PC1_dat.append(data_dict[model][scenario]['PC1'])
        PC2_dat.append(data_dict[model][scenario]['PC2'])
        
print('PC1 max:', max(PC1_dat))
print('PC1 min:', min(PC1_dat))
print('PC2 max:', max(PC2_dat))
print('PC2 min:', min(PC2_dat))


# PC1 max: 18.84070707094948
# PC1 min: -10.9383515120254
# PC2 max: 6.043028766206847
# PC2 min: -5.961574675200636


