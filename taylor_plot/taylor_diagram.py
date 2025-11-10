#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  9 21:32:43 2025

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
bp.os.chdir('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/taylor_plot/')
with open('nov_9.txt', 'r') as f:
    contents = f.read()

# Convert from string representation to actual dictionary
base_dict = ast.literal_eval(contents)

# Example Taylor statistics
std_obs = 1.0  # standard deviation of reference (observation)
models = [
    {'std': 1.2, 'corr': 0.8, 'label': "Model A"},
    {'std': 0.9, 'corr': 0.95, 'label': "Model B"}
]

# Setup polar plot: angle = arccos(correlation coefficient), radius = standard deviation
fig = bp.plt.figure(figsize = (5, 5))
ax = fig.add_subplot(111, polar = True)

# Style: theta=0 at left (correlation 1)
ax.set_theta_zero_location('W')
ax.set_theta_direction(-1)
ax.set_thetamin(0)
ax.set_thetamax(180)
ax.set_xticklabels([])
ax.spines['polar'].set_linewidth(0.75)
ax.spines['polar'].set_edgecolor('grey')

# Plot the reference (observation) point always at correlation=1, std=std_obs
ax.plot(0, std_obs, 'ko', label = "Reference", markersize = 10)

# Plot all models
for m in models:
    theta = bp.np.arccos(m['corr'])  # angle for correlation
    ax.plot(theta, m['std'], 'o', label=m['label'], markersize=9)

# Draw lines for various correlation coefficients as grid
corrs = bp.np.linspace(-1, 1, 6)
for c in corrs:
    angle = bp.np.arccos(c)
    ax.plot([angle, angle], [0, 1.5], '--', color='gray', lw=0.5)
    ax.text(angle, 1.55, f"{c:.2f}", ha='center', va='center', fontsize=9)

# Set axis limits and labels
ax.set_ylim(0, 1.6)
ax.set_yticks([0.5, 1.0, 1.5])
ax.set_yticklabels(['0.5', '1.0', '1.5'])
ax.set_title("Simple Taylor Diagram", y=1.08)
ax.legend(loc="upper right")
bp.plt.show()




# learn how to read GCM data out of matlab files
# make taylor plot repeatable for different variables


# dimensions for MACA region
# lat      (lat) float32 672B 36.03 36.07 36.11 36.15 ... 42.9 42.94 42.98
# * lon      (lon) float32 684B -115.1 -115.1 -115.0 ... -108.1 -108.1 -108.0

# PolarAxes.PolarTransform() # this tells plot to set std for radius and cor for angle
# diagram = TaylorDiagram(reference.std(ddof=1), fig=myfig)
# diagram.add_sample(stddev2, corrcoef2, label = 'Model 2', marker = 'o')