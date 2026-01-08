#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  1 08:18:25 2025

@author: u1301408
"""

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/packages')
import base_packages as bp
import ast

MACA_models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5', 'EC-Earth3-CC',
 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'INM-CM4-8', 'INM-CM5-0',
 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']

# Open and read the file
bp.os.chdir('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/GCM_bias')
with open('gcm_dict_dec_3.txt', 'r') as f:
    contents = f.read()

# Convert from string representation to actual dictionary
gcm_dict = ast.literal_eval(contents)

pr_levels = bp.np.array([])
temp_levels = bp.np.array([])
for model in MACA_models:
    pr_levels = bp.np.append(pr_levels, gcm_dict[model]['pr_ratio'])
    temp_levels = bp.np.append(temp_levels, gcm_dict[model]['tasmax_change'])
    
pr_min = float(pr_levels.min())
pr_max = float(pr_levels.max())
temp_min = float(temp_levels.min())
temp_max = float(temp_levels.max())

#%%

def scaled_data(variable):
    
    # add all data points for the called variable to a numpy array to determine max and min
    values = bp.np.array([])
    for model in  MACA_models:
        values = bp.np.append(values, gcm_dict[model]['summer_bias'][variable])

    a = values.min()
    b = values.max()

    if a < 0:
        scaled_bias = bp.np.zeros_like(values, dtype=float)

        neg_mask = values < 0
        pos_mask = values > 0

        if neg_mask.any() and a < 0:
            neg_vals = values[neg_mask]
            scaled_bias[neg_mask] = neg_vals / abs(a)

        if pos_mask.any() and b > 0:
            pos_vals = values[pos_mask]
            scaled_bias[pos_mask] = pos_vals / b
            
    elif variable == 'pr':
        # Map values so that:
         # - 1 in the original data maps to 0
         # - extremes map to -1 and 1
         a = values.min()
         b = values.max()

         # max distance from 1 on either side
         scale = max(1 - a, b - 1)

         scaled_bias = (values - 1.0) / scale
            
    else:
        # linearly scale raw values into 0 to 1 range for arccos function  (returns np.array)
        scaled_bias = (values - a) / (b - a)
        
    return a, b, scaled_bias, values

# low, high, adjusted, raw = scaled_data('pr')
    

def bias_taylor(variable_list):
    
    # manually set obs data point
    obs_bias = 0
    obs_stdev_ratio = 1

    # Setup polar plot: angle = arccos(correlation coefficient), radius = standard deviation
    fig, axs = bp.plt.subplots(1, 2, subplot_kw={'projection': 'polar'}, figsize = (11, 8))
    
    one, two = axs
    
    pr_levels = bp.np.array([50, 65, 80, 95, 100, 105, 150, 190, 220])
    temp_levels = bp.np.array([3, 4, 5, 6, 7, 8, 9])
    
    pr_norm = bp.mcolors.BoundaryNorm(pr_levels, ncolors = bp.plt.get_cmap(bp.cmap.cmap('MPL_BrBG'), 10).N) # 15 bins means 14 edges
    ts_norm = bp.mcolors.BoundaryNorm(temp_levels, ncolors = bp.plt.get_cmap(bp.cmap.cmap('BlRe'), 6).N) # 15 bins means 14 edges
    
    for index, diagram in enumerate([one, two]):
        diagram.set_theta_zero_location('W')
        diagram.set_theta_direction(-1)
        diagram.set_thetamax(180)
        diagram.set_xticklabels([])
        diagram.spines['polar'].set_linewidth(0.5)
        diagram.spines['polar'].set_edgecolor('black')
            
        diagram.xaxis.grid(False)

        # Plot the reference (observation) point 
        diagram.plot(bp.np.pi - bp.np.arccos(obs_bias), obs_stdev_ratio, marker = 'o', markerfacecolor =  'none', markeredgecolor = 'k', label = "Reference", markersize = 12)

        min_value, max_value, data, raw_data = scaled_data(variable_list[index])
        
        if min_value < 0:
            diagram.set_thetamin(0)
            pad = -0.08
            
            # Draw lines for various correlation coefficients as grid
            bias_lines = bp.np.array([-1.0, -0.8, -0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1.0])
            min_label = bp.np.linspace(min_value, 0,  6)
            max_label = bp.np.linspace(0, max_value, 6)
            bias_labels = bp.np.concatenate([min_label[:-1], max_label])
            
            # add more stdev labels
            r_ticks = [0.5, 1.0, 1.5, 2.0, 2.5]
            
            for r, move_it in zip(r_ticks, [0.05, 0.09, 0.13, 0.17, 0.21]):
                # Default side (right/top, angle ~22.5° or wherever your main labels are)
                # Add labels on the left (angle = À radians)
                fig.text(0.24 + move_it, 0.119, f"{r}", ha = 'center', va = 'center', fontsize = 9.75, color =  'k')
                fig.text(0.74 + move_it, 0.119, f"{r}", ha = 'center', va = 'center', fontsize = 9.75, color =  'k')

        elif 'pr' in variable_list:
            diagram.set_thetamin(0)
            pad = -0.08
            
            # Draw lines for various correlation coefficients as grid
            bias_lines = bp.np.array([-1.0, -0.8, -0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1.0])
            min_label = bp.np.linspace(min_value, 1,  6)
            max_label = bp.np.linspace(1, max_value, 6)
            bias_labels = bp.np.concatenate([min_label[:-1], max_label])
            
            # add more stdev labels
            r_ticks = [0.5, 1.0, 1.5, 2.0, 2.5]
            
            for r, move_it in zip(r_ticks, [0.05, 0.09, 0.13, 0.17, 0.21]):
                # Default side (right/top, angle ~22.5° or wherever your main labels are)
                # Add labels on the left (angle = À radians)
                fig.text(0.24 + move_it, 0.119, f"{r}", ha = 'center', va = 'center', fontsize = 9.75, color =  'k')
                fig.text(0.74 + move_it, 0.119, f"{r}", ha = 'center', va = 'center', fontsize = 9.75, color =  'k')

        else:
            diagram.set_thetamin(90)
            pad = 0.01
            
            # Draw lines for various correlation coefficients as grid
            bias_lines = bp.np.array([0, 0.2, 0.4, 0.6, 0.8, 1.0])
            bias_labels = bp.np.linspace(min_value, max_value, 6)
    
        # Plot all models
        for model, value in zip(MACA_models, data):
            theta = bp.np.pi - bp.np.arccos(value)  # angle for bias
            pr = one.scatter(theta, gcm_dict[model]['JJA_stdev_ratio'][variable_list[index]], marker = 'o', edgecolors = 'k', linewidths = 0.25, norm = pr_norm, cmap = bp.cmap.cmap('MPL_BrBG'), c = gcm_dict[model]['pr_ratio'], s = 25)
            ts = two.scatter(theta, gcm_dict[model]['JJA_stdev_ratio'][variable_list[index]], marker = 'o', edgecolors = 'k', linewidths = 0.25, norm = ts_norm, cmap = bp.cmap.cmap('BlRe'), c = gcm_dict[model]['tasmax_change'], s = 25)

        for lin, label in zip(bias_lines, bias_labels):
            angle = bp.np.pi - bp.np.arccos(lin)
            diagram.plot([angle, angle], [0, 2.62], '-.', color = 'black', lw = 0.25)
            diagram.text(angle, 2.8, f"{label:.2f}", ha = 'center', va = 'center', fontsize = 12)

        # Set axis limits and labels
        diagram.set_ylim(0, 1.6)
        diagram.set_yticks([0.5, 1.0, 1.5, 2.0, 2.5])
        diagram.yaxis.grid(True, color = 'black', linewidth = 0.25, linestyle = '-.')
        diagram.set_yticklabels([0.5, 1.0, 1.5, 2.0, 2.5], fontsize  = 50)
        
    pr_cbar = bp.plt.colorbar(pr, 
                               orientation = 'horizontal', 
                               ticks = pr_levels, 
                               shrink = 0.75, 
                               pad = pad,
                               extend = 'both',
                               boundaries = pr_levels)
    pr_cbar.ax.xaxis.set_major_formatter(bp.ticker.FormatStrFormatter('%.0f'))
    
    temp_cbar = bp.plt.colorbar(ts, 
                               orientation = 'horizontal', 
                               ticks = temp_levels, 
                               shrink = 0.75, 
                               pad = pad,
                               extend = 'both',
                               boundaries = temp_levels)
    temp_cbar.ax.xaxis.set_major_formatter(bp.ticker.FormatStrFormatter('%.0f'))

    bp.plt.show()
    
    return fig, axs, raw_data

# precip = bias_taylor(['pr', 'pr'])
temp = bias_taylor(['tasmin', 'tasmin'])
