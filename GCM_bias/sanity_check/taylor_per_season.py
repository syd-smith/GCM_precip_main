#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 30 18:29:48 2026

@author: u1301408
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.colors as mcolors 
from matplotlib.colors import Normalize
import numpy as np

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/tool_belt/')
from file_traversing import write2file, read_file


models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5',
          'EC-Earth3-AerChem', 'EC-Earth3-CC', 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4',
          'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'IITM-ESM', 'INM-CM4-8', 'INM-CM5-0', 'KACE-1-0-G', 'KIOST-ESM', 
          'MIROC-ES2H', 'MIROC-ES2L', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']

ssp585_models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1',
                 'CanESM5', 'EC-Earth3-CC', 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL',
                  'HadGEM3-GC31-MM', 'INM-CM4-8', 'INM-CM5-0', 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC6',
                   'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']


data = read_file('gcm_jan_29.txt')

bias = np.array([])
st_dev = np.array([])
for model in models:
    bias = np.append(bias, data[model]['DJF']['bias']['pr'])
    st_dev = np.append(st_dev, data[model]['DJF']['stdev_ratio']['pr'])

# read out data and format it in an array
# how can the data be plotted with the grid being equal distance on the radial axis
# no scaling of data
# functionality to add colorbars for specific projections
# base taylor diagram
# change it to be a quadrant or semi circle (maybe assumed by data points)
# have subplots or not
#%%

def bias_taylor_sans_projections(bias, stdev):
    
    # manually set obs data point
    obs_bias = 0
    obs_stdev_ratio = 1

    # Setup polar plot: angle = arccos(correlation coefficient), radius = standard deviation
    fig, axs = plt.subplots(subplot_kw={'projection': 'polar'})
    
    axs.set_theta_zero_location('W')
    axs.set_theta_direction(-1)
    axs.set_thetamax(180)
    axs.set_xticklabels([])
    axs.spines['polar'].set_linewidth(0.5)
    axs.spines['polar'].set_edgecolor('black')
        
    axs.xaxis.grid(False)

    # Plot the reference (observation) point 
    axs.plot(np.pi - np.arccos(obs_bias), obs_stdev_ratio, marker = 'o', markerfacecolor =  'none', markeredgecolor = 'k', label = "Reference", markersize = 12)

    min_value = min(data)
    max_value = max(data)
    
    axs.set_thetamin(0)
    pad = -0.08
    
    # Draw lines for various correlation coefficients as grid
    bias_lines = np.array([-1.0, -0.8, -0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1.0])
    min_label = np.linspace(min_value, 0,  6)
    max_label = np.linspace(0, max_value, 6)
    bias_labels = np.concatenate([min_label[:-1], max_label])
    
    # add more stdev labels
    r_ticks = [0.5, 1.0, 1.5, 2.0, 2.5]
    
    for r, move_it in zip(r_ticks, [0.05, 0.09, 0.13, 0.17, 0.21]):
        # Default side (right/top, angle ~22.5° or wherever your main labels are)
        # Add labels on the left (angle = À radians)
        fig.text(0.24 + move_it, 0.119, f"{r}", ha = 'center', va = 'center', fontsize = 9.75, color =  'k')
        fig.text(0.74 + move_it, 0.119, f"{r}", ha = 'center', va = 'center', fontsize = 9.75, color =  'k')

    theta = np.pi - np.arccos(value)  # angle for bias
    pr = one.scatter(theta, gcm_dict[model]['JJA_stdev_ratio'][variable_list[index]], marker = 'o', edgecolors = 'k', linewidths = 0.25, norm = pr_norm, cmap = cmap.cmap('MPL_BrBG'), c = gcm_dict[model]['pr_ratio'], s = 25)
    ts = two.scatter(theta, gcm_dict[model]['JJA_stdev_ratio'][variable_list[index]], marker = 'o', edgecolors = 'k', linewidths = 0.25, norm = ts_norm, cmap = cmap.cmap('BlRe'), c = gcm_dict[model]['tasmax_change'], s = 25)

    angle = np.pi - np.arccos(lin)
    axs.plot([angle, angle], [0, 2.62], '-.', color = 'black', lw = 0.25)
    axs.text(angle, 2.8, f"{label:.2f}", ha = 'center', va = 'center', fontsize = 12)

    # Set axis limits and labels
    axs.set_ylim(0, 1.6)
    axs.set_yticks([0.5, 1.0, 1.5, 2.0, 2.5])
    axs.yaxis.grid(True, color = 'black', linewidth = 0.25, linestyle = '-.')
    axs.set_yticklabels([0.5, 1.0, 1.5, 2.0, 2.5], fontsize  = 50)

    plt.show()
    
    return fig, axs, raw_data



#%%
print(bias.min())
print(bias.max())
# if bias.min() > 0: 
#     norm =  Normalize(vmin = 0, vmax = bias.max())
if abs(bias.min()) > abs(bias.max()):
    vmin = bias.min()
    vmax = abs(bias.min())
elif abs(bias.min()) < abs(bias.max()):
    vmin = -(bias.max())
    vmax = bias.max()
norm =  Normalize(vmin = vmin, vmax = vmax)


bias_norm =  norm(bias) * np.pi
# manually set obs data point
obs_bias = 0
obs_stdev_ratio = 1

# Setup polar plot: angle = arccos(correlation coefficient), radius = standard deviation
fig, axs = plt.subplots(subplot_kw={'projection': 'polar'}, figsize = (11, 8))

axs.set_thetamin(0)
axs.set_theta_zero_location('W')
axs.set_theta_direction(-1)
axs.set_thetamax(180)
axs.set_xticklabels([])
axs.spines['polar'].set_linewidth(0.5)
axs.spines['polar'].set_edgecolor('black')
    
axs.xaxis.grid(False)

# Plot the reference (observation) point 
axs.plot(np.pi - np.arccos(obs_bias), obs_stdev_ratio, marker = 'o', markerfacecolor =  'none', markeredgecolor = 'k', label = "Reference", markersize = 12)

# Set axis limits and labels
axs.set_ylim(0, 1.6)
axs.set_yticks([0.5, 1.0, 1.5, 2.0, 2.5])
axs.yaxis.grid(True, color = 'black', linewidth = 0.25, linestyle = '-.')
axs.set_yticklabels([0.5, 1.0, 1.5, 2.0, 2.5], fontsize  = 50)

axs.scatter(bias_norm, st_dev, marker = 'o', edgecolors = 'k', linewidths = 0.25, s = 25)

min_value = min(bias)
max_value = max(bias)
bias_lines = np.linspace(0, np.pi, 10)
bias_labels = vmin + (bias_lines / np.pi) * (vmax - vmin)

axs.set_xticks(bias_lines)
for line in bias_lines:
    angle = np.pi - np.arccos(line)
    axs.plot([angle, angle], [0, 2.62], '-.', color='black', lw=0.5)
# axs.plot([np.pi - np.arccos(line) for line in bias_lines, np.pi - np.arccos(line) for line in bias_lines], [0, 2.62], '-.', color = 'black')
axs.set_xticklabels([f"{b:.2f}" for b in bias_labels], fontsize=12)

# for lin, label in zip(bias_lines, bias_labels):
#     angle = np.pi - np.arccos(lin)
#     axs.plot([angle, angle], [0, 2.62], '-.', color = 'black', lw = 0.25)
#     axs.text(angle, 2.8, f"{label:.2f}", ha = 'center', va = 'center', fontsize = 12)



#%%
min_value, max_value, data, raw_data = scaled_data(variable_list[index])

if min_value < 0:
    axs.set_thetamin(0)
    pad = -0.08
    
    # Draw lines for various correlation coefficients as grid
    bias_lines = np.array([-1.0, -0.8, -0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1.0])
    min_label = np.linspace(min_value, 0,  6)
    max_label = np.linspace(0, max_value, 6)
    bias_labels = np.concatenate([min_label[:-1], max_label])
    
    # add more stdev labels
    r_ticks = [0.5, 1.0, 1.5, 2.0, 2.5]
    
    for r, move_it in zip(r_ticks, [0.05, 0.09, 0.13, 0.17, 0.21]):
        # Default side (right/top, angle ~22.5° or wherever your main labels are)
        # Add labels on the left (angle = À radians)
        fig.text(0.24 + move_it, 0.119, f"{r}", ha = 'center', va = 'center', fontsize = 9.75, color =  'k')
        fig.text(0.74 + move_it, 0.119, f"{r}", ha = 'center', va = 'center', fontsize = 9.75, color =  'k')

    elif 'pr' in variable_list:
        axs.set_thetamin(0)
        pad = -0.08
        
        # Draw lines for various correlation coefficients as grid
        bias_lines = np.array([-1.0, -0.8, -0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1.0])
        min_label = np.linspace(min_value, 1,  6)
        max_label = np.linspace(1, max_value, 6)
        bias_labels = np.concatenate([min_label[:-1], max_label])
        
        # add more stdev labels
        r_ticks = [0.5, 1.0, 1.5, 2.0, 2.5]
        
        for r, move_it in zip(r_ticks, [0.05, 0.09, 0.13, 0.17, 0.21]):
            # Default side (right/top, angle ~22.5° or wherever your main labels are)
            # Add labels on the left (angle = À radians)
            fig.text(0.24 + move_it, 0.119, f"{r}", ha = 'center', va = 'center', fontsize = 9.75, color =  'k')
            fig.text(0.74 + move_it, 0.119, f"{r}", ha = 'center', va = 'center', fontsize = 9.75, color =  'k')

    else:
        axs.set_thetamin(90)
        pad = 0.01
        
        # Draw lines for various correlation coefficients as grid
        bias_lines = np.array([0, 0.2, 0.4, 0.6, 0.8, 1.0])
        bias_labels = np.linspace(min_value, max_value, 6)

    # Plot all models
    for model, value in zip(MACA_models, data):
        theta = np.pi - np.arccos(value)  # angle for bias
        pr = one.scatter(theta, gcm_dict[model]['JJA_stdev_ratio'][variable_list[index]], marker = 'o', edgecolors = 'k', linewidths = 0.25, norm = pr_norm, cmap = cmap.cmap('MPL_BrBG'), c = gcm_dict[model]['pr_ratio'], s = 25)
        ts = two.scatter(theta, gcm_dict[model]['JJA_stdev_ratio'][variable_list[index]], marker = 'o', edgecolors = 'k', linewidths = 0.25, norm = ts_norm, cmap = cmap.cmap('BlRe'), c = gcm_dict[model]['tasmax_change'], s = 25)

    for lin, label in zip(bias_lines, bias_labels):
        angle = np.pi - np.arccos(lin)
        axs.plot([angle, angle], [0, 2.62], '-.', color = 'black', lw = 0.25)
        axs.text(angle, 2.8, f"{label:.2f}", ha = 'center', va = 'center', fontsize = 12)

    # Set axis limits and labels
    axs.set_ylim(0, 1.6)
    axs.set_yticks([0.5, 1.0, 1.5, 2.0, 2.5])
    axs.yaxis.grid(True, color = 'black', linewidth = 0.25, linestyle = '-.')
    axs.set_yticklabels([0.5, 1.0, 1.5, 2.0, 2.5], fontsize  = 50)
    

plt.show()
