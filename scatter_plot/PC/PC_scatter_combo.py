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
bp.os.chdir('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/scatter_plot/')
with open("oct_19.txt", "r") as f:
    contents = f.read()

# Convert from string representation to actual dictionary
data_dict = ast.literal_eval(contents)

# establish figure for subplots
fig, axs = bp.plt.subplots(1, 2, figsize = (18, 8))

# loop through dictionary to pull out necessary data for scatter
for model in data_dict:
    for scenario in data_dict[model]:
        if data_dict[model][scenario]['delta_temp'] == 'File Not Found' or data_dict[model][scenario]['precip_ratio'] == 'File Not Found':
            continue
        # adjust color of data point relative to PC value
        PC1_scatter = axs[0].scatter(data_dict[model][scenario]['delta_temp'], 
                              data_dict[model][scenario]['precip_ratio'], 
                              c = data_dict[model][scenario]['PC1'], 
                              cmap = 'viridis', 
                              s = 50, 
                              norm = bp.mcolors.Normalize(vmin = -10, vmax = 18))
        PC2_scatter = axs[1].scatter(data_dict[model][scenario]['delta_temp'], 
                              data_dict[model][scenario]['precip_ratio'], 
                              c = data_dict[model][scenario]['PC2'], 
                              cmap = 'viridis', 
                              s = 50, 
                              norm = bp.mcolors.Normalize(vmin = -5, vmax = 6))
        
# loop through both subplots to add visual features        
for ax in [0, 1]:        
    # axis ticks and labels
    axs[ax].set_yticks([50, 100, 150, 200])
    axs[ax].set_yticklabels([0.5, 1, 1.5, 2])
    axs[ax].set_xticks([0, 5, 10])

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
    axs[ax].set_xlabel('Temperature Change (K)')
    axs[ax].set_ylabel('Precipitation Ratio')


# creating a color bar and legend for PC1 and PC2 data
PC1_cbar = bp.plt.colorbar(PC1_scatter, 
                           orientation = 'horizontal', 
                           ticks = bp.np.linspace(-10, 18, num = 9), 
                           shrink = 0.5, 
                           pad = 0.05,
                           extend = 'both')
PC1_cbar.ax.xaxis.set_major_formatter(bp.ticker.FormatStrFormatter('%.0f'))

PC2_cbar = bp.plt.colorbar(PC2_scatter, 
                           orientation = 'horizontal', 
                           ticks = bp.np.linspace(-5, 6, num = 9), 
                           shrink = 0.5, 
                           pad = 0.05,
                           extend = 'both')
PC2_cbar.ax.xaxis.set_major_formatter(bp.ticker.FormatStrFormatter('%.0f'))

# add labels to each subplot
axs[0].text(0.05, 0.85, 'a.', fontsize = 15, fontweight = 'bold', transform = axs[0].transAxes)
axs[1].text(0.05, 0.85, 'b.', fontsize = 15, fontweight = 'bold', transform = axs[1].transAxes)

# save figure
save_name = 'PC_scatter_combo_take_one'
save_path = bp.os.path.join(f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/scatter_plot/PC/{save_name}.png')
fig.savefig(save_path, dpi = 400, bbox_inches = 'tight', pad_inches = 0.1)

bp.plt.show()


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
