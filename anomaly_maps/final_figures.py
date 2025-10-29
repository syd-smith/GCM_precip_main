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
from gcm_var_mapping import region_mean, anomaly, quiver

models = ['UKESM1-0-LL', 'HadGEM3-GC31-MM', 'MPI-ESM1-2-LR']


def color_bar(var_min, var_center, var_max, color, location, axs):
    ticks = bp.np.linspace(var_min, var_max, num = 10)
    norm = bp.mcolors.TwoSlopeNorm(vmin = var_min, vcenter = var_center, vmax = var_max)

    # create a scalar mappable as a standin for contour so the colorbar remains standardized across different maps
    sm = bp.mpl.cm.ScalarMappable(norm = norm, cmap = color)
    sm.set_array([]) # makes sure no data is attached to the colorbar
    
    # specify the layout of the colorbar
    cbar = bp.plt.colorbar(sm, ax = axs, orientation = 'vertical', pad = 0.025, aspect = 50, extend = 'both', ticks = ticks, location = location)
    cbar.ax.yaxis.set_major_formatter(bp.ticker.FormatStrFormatter('%.0f'))
    cbar.ax.tick_params(labelsize = 30)
    
    return cbar

# zoom out for zg
fig = bp.plt.figure()
ax = bp.plt.axes(projection  = bp.ccrs.PlateCarree())

ds = anomaly(models[2], 'ts', 6, 8)

ax.contourf(ds['lon'], ds['lat'], ds.values, cmap = bp.cmap.cmap('MPL_YlOrRd'), transform = bp.ccrs.PlateCarree(), levels = 20)
color_bar(0, 7.5, 15, bp.cmap.cmap('MPL_YlOrRd'), 'right', ax)


def temp_precip_fig(start_month, stop_month, save_name = 'test', save = False):
 
    fig, axs = bp.plt.subplots(nrows = 2, ncols = 3, subplot_kw = {'projection': bp.ccrs.PlateCarree()}, figsize = (40, 11))
    
    labels_one = ['a.', 'b.', 'c.']
    labels_two = ['d.', 'e.', 'f.']
    
    # loop for pecip anomalies on the top row
    for i, model in enumerate(models):
        precip_data = anomaly(model, 'pr', start_month, stop_month)
        temp_data = anomaly(model, 'ts', start_month, stop_month)
        precip_maps = axs[0][i].contourf(precip_data['lon'], precip_data['lat'], precip_data.values, levels = bp.np.linspace(-75, 300, 10), norm = bp.mcolors.TwoSlopeNorm(vmin = -75, vcenter = 0, vmax = 300), cmap = bp.cmap.cmap('MPL_BrBG'), extend = 'both', transform = bp.ccrs.PlateCarree())
        temp_maps = axs[1][i].contourf(temp_data['lon'], temp_data['lat'], temp_data.values, levels = bp.np.linspace(0, 15, 10), norm = bp.mcolors.TwoSlopeNorm(vmin = 0, vcenter = 7.5, vmax = 15),cmap = bp.cmap.cmap('MPL_YlOrRd'), extend = 'both', transform = bp.ccrs.PlateCarree())
        
        for ax in [axs[0, i], axs[1, i]]:
            ax.set_extent([-143, -67.5, 20, 44.8])
            
            # add features to each map
            ax.coastlines(linewidth = 1,color = 'k')

            states = bp.cfeature.NaturalEarthFeature(category = 'cultural', name = 'admin_1_states_provinces_lines', scale = '50m', facecolor = 'none', edgecolor = 'k')
            countries = bp.cfeature.NaturalEarthFeature(category = 'cultural', name = 'admin_0_boundary_lines_land', scale = '50m', facecolor = 'none', edgecolor = 'k')
            ax.add_feature(states, linewidth = 1)
            ax.add_feature(countries, linewidth = 1)
            
        axs[0][i].text(0.02, 0.89, labels_one[i], fontsize = 30, fontweight = 'bold', transform = axs[0][i].transAxes)
        axs[1][i].text(0.02, 0.89, labels_two[i], fontsize = 30, fontweight = 'bold', transform = axs[1][i].transAxes)
            
    ts_cbar = color_bar(0, 7.5, 15, bp.cmap.cmap('MPL_YlOrRd'), 'right', axs)
    pr_cbar = color_bar(-75, 0, 300, bp.cmap.cmap('MPL_BrBG'), 'left', axs)
      
    if save:
        # all PNGs stored to anomaly_maps directory but ignored in Git
        save_path = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/anomaly_maps/paper_figs/'
        save_path = bp.os.path.join(save_path + save_name + '.png')
        bp.plt.savefig(save_path, dpi = 400)
        
    bp.plt.show()
    
temp_precip_fig(6, 8)
      

#%%
def height_wind_fig(start_month, stop_month, save_name = 'test', save = False):
    fig, axs = bp.plt.subplots(nrows = 2, ncols = 3, subplot_kw = {'projection': bp.ccrs.PlateCarree()}, figsize = (40, 11))
    
    labels_one = ['a.', 'b.', 'c.']
    labels_two = ['d.', 'e.', 'f.']
    
    # loop for pecip anomalies on the top row
    for i, model in enumerate(models):
        mean_data = region_mean(model, 'zg', start_month, stop_month, level = 5000)
        anom_data = anomaly(model, 'zg', start_month, stop_month, level = 50000)
        
        # add mean geopotential height and wind data for the historical period to the top row
        mean_maps = axs[0][i].contourf(mean_data['lon'], mean_data['lat'], mean_data.values, levels = bp.np.linspace(5675, 5975, 10), norm = bp.mcolors.TwoSlopeNorm(vmin = 5675, vcenter = 5825, vmax = 5975), cmap = bp.cmap.cmap('MPL_coolwarm'), extend = 'both', transform = bp.ccrs.PlateCarree())
        mean_quiver, mean_key = quiver('ua', 'va', axs[0][i], region_mean, model, start_month, stop_month, level = 50000)
        
        # add anomaly data to the bottom row
        anom_maps = axs[1][i].contourf(anom_data['lon'], anom_data['lat'], anom_data.values, levels = bp.np.linspace(75, 200, 10), norm = bp.mcolors.TwoSlopeNorm(vmin = 75, vcenter = 138, vmax = 200), cmap = bp.cmap.cmap('BlAqGrYeOrReVi200'), extend = 'both', transform = bp.ccrs.PlateCarree())
        anom_quiver, anom_key = quiver('ua', 'va', axs[1][i], anomaly, model, start_month, stop_month, level = 50000)
        
        for ax in [axs[0, i], axs[1, i]]:
            ax.set_extent([-143, -67.5, 20, 44.8])
            
            # add features to each map
            ax.coastlines(linewidth = 1,color = 'k')

            states = bp.cfeature.NaturalEarthFeature(category = 'cultural', name = 'admin_1_states_provinces_lines', scale = '50m', facecolor = 'none', edgecolor = 'k')
            countries = bp.cfeature.NaturalEarthFeature(category = 'cultural', name = 'admin_0_boundary_lines_land', scale = '50m', facecolor = 'none', edgecolor = 'k')
            ax.add_feature(states, linewidth = 1)
            ax.add_feature(countries, linewidth = 1)
            
        axs[0][i].text(0.02, 0.89, labels_one[i], fontsize = 30, fontweight = 'bold', transform = axs[0][i].transAxes)
        axs[1][i].text(0.02, 0.89, labels_two[i], fontsize = 30, fontweight = 'bold', transform = axs[1][i].transAxes)
            
    mean_cbar = color_bar(5675, 5825, 5975, bp.cmap.cmap('MPL_coolwarm'), 'left', axs)
    anom_cbar = color_bar(75, 138, 200, bp.cmap.cmap('BlAqGrYeOrReVi200'), 'right', axs)
    
    if save:
        # all PNGs stored to anomaly_maps directory but ignored in Git
        save_path = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/anomaly_maps/paper_figs/'
        save_path = bp.os.path.join(save_path + save_name + '.png')
        bp.plt.savefig(save_path, dpi = 400)
      
    bp.plt.show()

height_wind_fig(6, 8)

#%%

def humidity_fig(start_month, stop_month, save_name = 'test', save = False):
    fig, axs = bp.plt.subplots(nrows = 2, ncols = 3, subplot_kw = {'projection': bp.ccrs.PlateCarree()}, figsize = (40, 11))
    
    labels_one = ['a.', 'b.', 'c.']
    labels_two = ['d.', 'e.', 'f.']
    
    # loop for pecip anomalies on the top row
    for i, model in enumerate(models):
        mean_data = region_mean(model, 'huss', start_month, stop_month)
        anom_data = anomaly(model, 'huss', start_month, stop_month)
        mean_maps = axs[0][i].contourf(mean_data['lon'], mean_data['lat'], mean_data.values, cmap = bp.cmap.cmap('cmocean_haline', revBool=True), extend = 'both', transform = bp.ccrs.PlateCarree(),)
        anom_maps = axs[1][i].contourf(anom_data['lon'], anom_data['lat'], anom_data.values, cmap = bp.cmap.cmap('MPL_YlGnBu'), extend = 'both', transform = bp.ccrs.PlateCarree(),)
        
        for ax in [axs[0, i], axs[1, i]]:
            ax.set_extent([-143, -67.5, 20, 44.8])
            
            # add features to each map
            ax.coastlines(linewidth = 1,color = 'k')

            states = bp.cfeature.NaturalEarthFeature(category = 'cultural', name = 'admin_1_states_provinces_lines', scale = '50m', facecolor = 'none', edgecolor = 'k')
            countries = bp.cfeature.NaturalEarthFeature(category = 'cultural', name = 'admin_0_boundary_lines_land', scale = '50m', facecolor = 'none', edgecolor = 'k')
            ax.add_feature(states, linewidth = 1)
            ax.add_feature(countries, linewidth = 1)
            
        axs[0][i].text(0.02, 0.89, labels_one[i], fontsize = 30, fontweight = 'bold', transform = axs[0][i].transAxes)
        axs[1][i].text(0.02, 0.89, labels_two[i], fontsize = 30, fontweight = 'bold', transform = axs[1][i].transAxes)
            
    mean_cbar = color_bar(4, 15, 27, bp.cmap.cmap('cmocean_haline', revBool=True), 'left', axs)
    anom_cbar = color_bar(0, 3.5, 7, bp.cmap.cmap('MPL_YlGnBu'), 'right', axs)
    
    if save:
        # all PNGs stored to anomaly_maps directory but ignored in Git
        save_path = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/anomaly_maps/paper_figs/'
        save_path = bp.os.path.join(save_path + save_name + '.png')
        bp.plt.savefig(save_path, dpi = 400)
      
    bp.plt.show()
    
humidity_fig(6, 8)