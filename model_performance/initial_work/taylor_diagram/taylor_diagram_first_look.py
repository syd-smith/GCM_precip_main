#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  9 21:32:43 2025

@author: u1301408
"""

import matplotlib.pyplot as plt
import numpy as np
import sys

sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/tool_belt/')
from file_traversing import write2file, read_file

MACA_models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5', 'EC-Earth3-CC',
 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'INM-CM4-8', 'INM-CM5-0',
 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']

# Convert from string representation to actual dictionary
base_dict = read_file('nov_17.txt', '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/model_performance/taylor_diagram')

variable =  'pr'
obs_data = {'pr': 0.46832597244903795,
            'huss': 0.0003445885315470638,
            'rsds': 9.423356161495821,
            'tasmin': 3.6344803010020477,
            'tasmax': 3.778675424194867,
            'uas': 0.7591268756780736,
            'vas': 0.3952614372625724
            }


# Setup polar plot: angle = arccos(correlation coefficient), radius = standard deviation
fig = plt.figure(figsize = (5, 5))
ax = fig.add_subplot(111, polar = True)

# Style: theta=0 at left (correlation 1)
ax.set_theta_zero_location('W')
ax.set_theta_direction(-1)
ax.set_thetamin(0)
ax.set_thetamax(180)
ax.set_xticklabels([])
ax.spines['polar'].set_linewidth(0.5)
ax.spines['polar'].set_edgecolor('black')

ax.xaxis.grid(False)


# Plot the reference (observation) point 
ax.plot(np.pi - np.arccos(1), obs_data[variable], 'ko', label = "Reference", markersize = 10)

# Plot all models
for model in MACA_models:
    theta = np.pi - np.arccos(base_dict[model]['corrcoef'][variable])  # angle for correlation
    ax.plot(theta, base_dict[model]['std'][variable], 'o', label = model, markersize = 9)

# Draw lines for various correlation coefficients as grid
corr_lines = np.array([-1.00, -0.93, -0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75, 0.93, 1.00])
for lin in corr_lines:
    angle = np.pi - np.arccos(lin)
    ax.plot([angle, angle], [0, 1.62], '-.', color = 'black', lw = 0.25)
    ax.text(angle, 1.74, f"{lin:.2f}", ha = 'center', va = 'center', fontsize = 9)

# Set axis limits and labels
ax.set_ylim(0, 1.6)
ax.set_yticks([0.5, 1.0, 1.5])
ax.yaxis.grid(True, color = 'black', linewidth = 0.25, linestyle = '-.')
ax.set_yticklabels(['0.5', '1.0', '1.5'])

# r_ticks = [0.5, 1.0, 1.5]
# for r in r_ticks:
#     # Default side (right/top, angle ~22.5° or wherever your main labels are)
#     # Add labels on the left (angle = À radians)
#     ax.text(bp.np.pi, r, f"{r}", ha='center', va='center', fontsize=10)
    
# ax.legend(loc="upper right")
plt.show()




# learn how to read GCM data out of matlab files
# make taylor plot repeatable for different variables


# dimensions for MACA region
# lat      (lat) float32 672B 36.03 36.07 36.11 36.15 ... 42.9 42.94 42.98
# * lon      (lon) float32 684B -115.1 -115.1 -115.0 ... -108.1 -108.1 -108.0

# PolarAxes.PolarTransform() # this tells plot to set std for radius and cor for angle
# diagram = TaylorDiagram(reference.std(ddof=1), fig=myfig)
# diagram.add_sample(stddev2, corrcoef2, label = 'Model 2', marker = 'o')