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
with open('gcm_dict_dec_1.txt', 'r') as f:
    contents = f.read()

# Convert from string representation to actual dictionary
gcm_dict = ast.literal_eval(contents)

variable = 'pr'
obs_bias = 0
obs_stdev_ratio = 1


values = bp.np.array([])
for model in  MACA_models:
    values = bp.np.append(values, gcm_dict[model]['summer_bias']['pr'])
    
a = values.min()
b = values.max()

# linearly scale into [0, 1]
precip_bias = (values - a) / (b - a)


# Setup polar plot: angle = arccos(correlation coefficient), radius = standard deviation
fig = bp.plt.figure(figsize = (10, 10))
ax = fig.add_subplot(111, polar = True)

# Style: theta=0 at left (correlation 1)
ax.set_theta_zero_location('W')
ax.set_theta_direction(-1)
ax.set_thetamin(90)
ax.set_thetamax(180)
ax.set_xticklabels([])
ax.spines['polar'].set_linewidth(0.5)
ax.spines['polar'].set_edgecolor('black')

ax.xaxis.grid(False)


# Plot the reference (observation) point 
ax.plot(bp.np.pi - bp.np.arccos(obs_bias), obs_stdev_ratio, 'ko', label = "Reference", markersize = 18)

# Plot all models
for model, value in zip(MACA_models, precip_bias):
    theta = bp.np.pi - bp.np.arccos(value)  # angle for bias
    ax.plot(theta, gcm_dict[model]['JJA_stdev_ratio'][variable], 'o', label = model, markersize = 18)

# Draw lines for various correlation coefficients as grid
bias_lines = bp.np.array([0, 0.2, 0.4, 0.6, 0.8, 1.0])
bias_labels = bp.np.linspace(a, b, 6)
for lin, label in zip(bias_lines, bias_labels):
    angle = bp.np.pi - bp.np.arccos(lin)
    ax.plot([angle, angle], [0, 2.62], '-.', color = 'black', lw = 0.25)
    ax.text(angle, 2.64, f"{label:.2f}", ha = 'center', va = 'center', fontsize = 12)

# Set axis limits and labels
ax.set_ylim(0, 1.6)
ax.set_yticks([0.5, 1.0, 1.5, 2.0, 2.5])
ax.yaxis.grid(True, color = 'black', linewidth = 0.25, linestyle = '-.')
ax.set_yticklabels([0.5, 1.0, 1.5, 2.0, 2.5], fontsize  = 50)
ax.legend(loc = 'upper right', bbox_to_anchor = (1.1, 1.1))

# r_ticks = [0.5, 1.0, 1.5]
# for r in r_ticks:
#     # Default side (right/top, angle ~22.5° or wherever your main labels are)
#     # Add labels on the left (angle = À radians)
#     ax.text(bp.np.pi, r, f"{r}", ha='center', va='center', fontsize=10)
    
# ax.legend(loc="upper right")
bp.plt.show()




# learn how to read GCM data out of matlab files
# make taylor plot repeatable for different variables


# dimensions for MACA region
# lat      (lat) float32 672B 36.03 36.07 36.11 36.15 ... 42.9 42.94 42.98
# * lon      (lon) float32 684B -115.1 -115.1 -115.0 ... -108.1 -108.1 -108.0

# PolarAxes.PolarTransform() # this tells plot to set std for radius and cor for angle
# diagram = TaylorDiagram(reference.std(ddof=1), fig=myfig)
# diagram.add_sample(stddev2, corrcoef2, label = 'Model 2', marker = 'o')





# min(values)
# Out[33]: 1.0309136727222494

# max(values)
# Out[34]: 2.2048123705718075