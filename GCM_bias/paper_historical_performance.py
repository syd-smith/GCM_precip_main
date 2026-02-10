#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 10 12:26:44 2026

@author: u1301408
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.colors as mcolors 
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
import numpy as np

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/tool_belt/')
from file_traversing import write2file, read_file

sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/GCM_bias/sanity_check/')
from historical_analysis import model_performance

sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/from_savanna/')
import nclcmaps as cmap

sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/GCM_bias/sanity_check/')
from taylor_per_season import data_build


ssp585_models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1',
                 'CanESM5', 'EC-Earth3-CC', 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL',
                  'HadGEM3-GC31-MM', 'INM-CM4-8', 'INM-CM5-0', 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC6',
                   'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']

# initialize figure with three subplots
fig, axs  = plt.subplots(1, 3, figsize = (20, 5))

# read out data and create structure for colorbar
data = read_file('projections_feb10.txt')
projection = np.array([data['ssp585'][model]['JJA']['precip_ratio'] for model in ssp585_models])
levels = np.array([50, 65, 80, 95, 100, 105, 150, 190, 220])
norm = mcolors.BoundaryNorm(levels, ncolors = plt.get_cmap(cmap.cmap('MPL_BrBG'), 8).N)

# call each individual plot from the model_performance function
a, b, points = model_performance('pr', 'JJA', ssp585_models, axs = axs[0], add_box = False, coloring = True)
axs[0].set_ylabel('Precipitation Standard Deviation Ratio')
axs[0].set_xlabel('Precipitation Bias Ratio')

c, d, points = model_performance('tasmin', 'JJA', ssp585_models, axs = axs[1], add_box = False, coloring = True)
axs[1].set_ylabel('Minimum Temperature Standard Deviation Ratio')
axs[1].set_xlabel('Minimum Temperature Bias (K)')

e, f, points = model_performance('tasmax', 'JJA', ssp585_models, axs = axs[2], add_box = False, coloring = True)
axs[2].set_ylabel('Maximum Temperature Standard Deviation Ratio')
axs[2].set_xlabel('Maximum Temperature Bias (K)')

# create colorbar with shading to indicate percent change in projected precipitation 
cbar = fig.colorbar(points, ax = axs,corientation = 'vertical', ticks = levels, pad = 0.02,extend = 'both', boundaries = levels)
cbar.ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))




