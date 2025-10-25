#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 23 17:44:03 2025

@author: u1301408
"""

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/packages')
import base_packages as bp

sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/anomaly_maps/')
from gcm_var_mapping import region_mean, anomaly

models = ['UKESM1-0-LL', 'HadGEM3-GC31-MM', 'MPI-ESM1-2-LR']

def temp_precip_fig(save = False):
    fig, axs = bp.plt.subplots(nrows = 2, ncols = 3, subplot_kw={'projection': bp.ccrs.PlateCarree()}, figsize = (35, 10))
    
    # loop for pecip anomalies on the top row
    for i, model in enumerate(models):
        precip_data = anomaly(model, 'pr', 6, 8)
        temp_data = anomaly(model, 'ts', 6, 8)
        precip_maps = axs[0][i].contourf(precip_data['lon'], precip_data['lat'], precip_data.values, cmap = bp.cmap.cmap('MPL_BrBG'), extend = 'both', transform = bp.ccrs.PlateCarree(),)
        temp_maps = axs[1][i].contourf(temp_data['lon'], temp_data['lat'], temp_data.values, cmap = bp.cmap.cmap('MPL_YlOrRd'), extend = 'both', transform = bp.ccrs.PlateCarree(),)
        
        for ax in [axs[0, i], axs[1, i]]:
            ax.set_extent([-143, -67.5, 20, 45])
            
            # add features to each map
            ax.coastlines(linewidth=0.5,color = 'k')

            states = bp.cfeature.NaturalEarthFeature(category = 'cultural', name = 'admin_1_states_provinces_lines', scale = '50m', facecolor = 'none', edgecolor = 'k')
            countries = bp.cfeature.NaturalEarthFeature(category = 'cultural', name = 'admin_0_boundary_lines_land', scale = '50m', facecolor = 'none', edgecolor = 'k')
            ax.add_feature(states, linewidth = 0.5)
            ax.add_feature(countries, linewidth = 0.5)
      
    bp.plt.show()
      
temp_precip_fig()