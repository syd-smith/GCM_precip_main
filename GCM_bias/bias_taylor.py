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
            
    else:
        # linearly scale raw values into 0 to 1 range for arccos function  (returns np.array)
        scaled_bias = (values - a) / (b - a)
        
    return a, b, scaled_bias

# low, high, adjusted = scaled_data('pr')
    

def bias_taylor(variable_list):
    
    # manually set obs data point
    obs_bias = 0
    obs_stdev_ratio = 1

    # Setup polar plot: angle = arccos(correlation coefficient), radius = standard deviation
    fig, axs = bp.plt.subplots(1, 2, subplot_kw={'projection': 'polar'}, figsize = (10, 8))
    
    one, two = axs
    
    for index, diagram in enumerate([one, two]):
        diagram.set_theta_zero_location('W')
        diagram.set_theta_direction(-1)
        diagram.set_thetamax(180)
        diagram.set_xticklabels([])
        diagram.spines['polar'].set_linewidth(0.5)
        diagram.spines['polar'].set_edgecolor('black')
            
        diagram.xaxis.grid(False)

        # Plot the reference (observation) point 
        diagram.plot(bp.np.pi - bp.np.arccos(obs_bias), obs_stdev_ratio, 'ko', label = "Reference", markersize = 10)

        min_value, max_value, data = scaled_data(variable_list[index])
        
        if min_value < 0:
            diagram.set_thetamin(0)
            
            # Draw lines for various correlation coefficients as grid
            bias_lines = bp.np.array([-1.0, -0.8, -0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1.0])
            min_label = bp.np.linspace(min_value, 0,  6)
            max_label = bp.np.linspace(0, max_value, 6)
            bias_labels = bp.np.concatenate([min_label[:-1], max_label])

        else:
            diagram.set_thetamin(90)
            
            # Draw lines for various correlation coefficients as grid
            bias_lines = bp.np.array([0, 0.2, 0.4, 0.6, 0.8, 1.0])
            bias_labels = bp.np.linspace(min_value, max_value, 6)
    
        # Plot all models
        for model, value in zip(MACA_models, data):
            theta = bp.np.pi - bp.np.arccos(value)  # angle for bias
            diagram.plot(theta, gcm_dict[model]['JJA_stdev_ratio'][variable_list[index]], 'o', label = model, markersize = 10)

        for lin, label in zip(bias_lines, bias_labels):
            angle = bp.np.pi - bp.np.arccos(lin)
            diagram.plot([angle, angle], [0, 2.62], '-.', color = 'black', lw = 0.25)
            diagram.text(angle, 2.74, f"{label:.2f}", ha = 'center', va = 'center', fontsize = 12)

        # Set axis limits and labels
        diagram.set_ylim(0, 1.6)
        diagram.set_yticks([0.5, 1.0, 1.5, 2.0, 2.5])
        diagram.yaxis.grid(True, color = 'black', linewidth = 0.25, linestyle = '-.')
        diagram.set_yticklabels([0.5, 1.0, 1.5, 2.0, 2.5], fontsize  = 50)

    bp.plt.show()
    
    return fig, axs

precip = bias_taylor(['pr', 'pr'])
temp = bias_taylor(['tasmax', 'tasmax'])
    
#%%
variable_list =  ['pr', 'pr']

# manually set obs data point
obs_bias = 0
obs_stdev_ratio = 1

# Setup polar plot: angle = arccos(correlation coefficient), radius = standard deviation
fig, axs = bp.plt.subplots(1, 2, subplot_kw={'projection': 'polar'}, figsize = (10, 8))

one, two = axs

for index, diagram in enumerate([one, two]):
    diagram.set_theta_zero_location('W')
    diagram.set_theta_direction(-1)
    diagram.set_thetamax(180)
    diagram.set_xticklabels([])
    diagram.spines['polar'].set_linewidth(0.5)
    diagram.spines['polar'].set_edgecolor('black')
        
    diagram.xaxis.grid(False)

    # Plot the reference (observation) point 
    diagram.plot(bp.np.pi - bp.np.arccos(obs_bias), obs_stdev_ratio, 'ko', label = "Reference", markersize = 10)

    min_value, max_value, data = scaled_data(variable_list[index])
    
    if min_value < 0:
        diagram.set_thetamin(0)
        
        # Draw lines for various correlation coefficients as grid
        bias_lines = bp.np.array([-1.0, -0.8, -0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1.0])
        min_label = bp.np.linspace(min_value, 0,  6)
        max_label = bp.np.linspace(0, max_value, 6)
        bias_labels = bp.np.concatenate([min_label[:-1], max_label])

    else:
        diagram.set_thetamin(90)
        
        # Draw lines for various correlation coefficients as grid
        bias_lines = bp.np.array([0, 0.2, 0.4, 0.6, 0.8, 1.0])
        bias_labels = bp.np.linspace(min_value, max_value, 6)

    # Plot all models
    for model, value in zip(MACA_models, data):
        theta = bp.np.pi - bp.np.arccos(value)  # angle for bias
        diagram.plot(theta, gcm_dict[model]['JJA_stdev_ratio'][variable_list[index]], 'o', label = model, markersize = 10)

    for lin, label in zip(bias_lines, bias_labels):
        angle = bp.np.pi - bp.np.arccos(lin)
        diagram.plot([angle, angle], [0, 2.62], '-.', color = 'black', lw = 0.25)
        diagram.text(angle, 2.74, f"{label:.2f}", ha = 'center', va = 'center', fontsize = 12)

    # Set axis limits and labels
    diagram.set_ylim(0, 1.6)
    diagram.set_yticks([0.5, 1.0, 1.5, 2.0, 2.5])
    diagram.yaxis.grid(True, color = 'black', linewidth = 0.25, linestyle = '-.')
    diagram.set_yticklabels([0.5, 1.0, 1.5, 2.0, 2.5], fontsize  = 50)
    
    
# add colorbar
precip_ratio = bp.np.array([])
delta_temp = bp.np.array([])

for model in MACA_models:
    precip_ratio = bp.np.append(precip_ratio, gcm_dict[model]['pr_ratio'])
    delta_temp = bp.np.append(delta_temp, gcm_dict[model]['tasmax_change'])
    
pr_levels = bp.np.linspace(min(precip_ratio), max(precip_ratio), 8)

cmap = bp.plt.get_cmap(bp.cmap.cmap('MPL_BrBG'), 7)
pr_norm = bp.mcolors.BoundaryNorm(pr_levels, ncolors = cmap.N)

pr_sm = bp.mpl.cm.ScalarMappable(norm = pr_norm, cmap = cmap)
pr_sm.set_array([])

# shared colorbar for both Taylor diagrams
pr_cbar = fig.colorbar(
    pr_sm,
    ax = one,                
    orientation='horizontal',
    extend='both',
    ticks = pr_levels,
    boundaries = pr_levels,
    aspect = 50,
)

pr_cbar.ax.tick_params(labelsize=20)
pr_cbar.ax.yaxis.set_major_formatter(bp.ticker.FormatStrFormatter('%.0f'))


temp_levels = bp.np.linspace(min(delta_temp), max(delta_temp), 8)

temp_norm = bp.mcolors.BoundaryNorm(temp_levels, ncolors = cmap.N)
temp_sm = bp.mpl.cm.ScalarMappable(norm = temp_norm, cmap = cmap)
temp_sm.set_array([])

# shared colorbar for both Taylor diagrams
temp_cbar = fig.colorbar(
    temp_sm,
    ax = two,                
    orientation = 'horizontal',
    extend = 'both',
    ticks = temp_levels,
    boundaries = temp_levels,
    aspect = 50,
)

temp_cbar.ax.tick_params(labelsize=20)
temp_cbar.ax.yaxis.set_major_formatter(bp.ticker.FormatStrFormatter('%.0f'))

bp.plt.show()
