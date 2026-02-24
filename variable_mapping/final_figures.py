#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 23 17:44:03 2025

@author: u1301408
"""

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib as mpl
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import numpy as np
import os
import sys

sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/anomaly_maps/')
from gcm_var_mapping import region_mean, anomaly, quiver

sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/from_savanna/')
import nclcmaps as cmap

# representatives of wet/moderate/dry scenarios
models = ['UKESM1-0-LL', 'HadGEM3-GC31-MM', 'MPI-ESM1-2-LR']


def color_bar(var_min, var_center, var_max, color, location, axs):
    """
    Function to simply create a colorbar for maps. Note that this colorbar
    won't be standardized using a scalar mappable to apply to multiple maps. 
    """
    
    ticks = np.linspace(var_min, var_max, num = 10)
    norm = mcolors.TwoSlopeNorm(vmin = var_min, vcenter = var_center, vmax = var_max)

    # create a scalar mappable as a standin for contour so the colorbar remains standardized across different maps
    sm = mpl.cm.ScalarMappable(norm = norm, cmap = color)
    sm.set_array([]) # makes sure no data is attached to the colorbar
    
    # specify the layout of the colorbar
    cbar = plt.colorbar(sm, ax = axs, orientation = 'vertical', pad = 0.015, aspect = 50, extend = 'both', ticks = ticks, location = location)
    cbar.ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
    cbar.ax.tick_params(labelsize = 30)
    
    return cbar


def future_change_fig(start_month, stop_month, save_name = 'test', save = False):
    """
    Function used to create the final maps displaying the expected future change
    in precipitation across the continential US. Note that the selected models
    range from high precipitation outputs on the left (UKESM1-0-LL) with no 
    precipiation change in the center (HadGEM3-GC31-MM) and low precipitation
    outputs on the right (MPI-ESM1-2-LR). 
    """
 
    fig, axs = plt.subplots(nrows = 3, ncols = 3, subplot_kw = {'projection': ccrs.PlateCarree()}, figsize = (40, 17.5))
    
    labels_one = ['a.', 'b.', 'c.']
    labels_two = ['d.', 'e.', 'f.']
    labels_three = ['g.', 'h.', 'i.']
    
    # loop for pecip anomalies on the top row
    for i, model in enumerate(models):
        # call data
        pr_data = anomaly(model, 'pr', start_month, stop_month)
        ts_data = anomaly(model, 'ts', start_month, stop_month)
        huss_data = anomaly(model, 'huss', start_month, stop_month)
        
        # define levels
        pr_levels  = np.array([-75, -60, -45, -30, -15, 0, 50, 100, 150, 200, 250])
        # pr_levels = bp.np.linspace(-150, 150, 15) # 15 bins means 14 edges
        ts_levels = np.linspace(0, 15, 15)
        huss_levels = np.linspace(0, 7, 8)
        
        # define norm values to standardize colorbar to map colors
        pr_norm = mcolors.BoundaryNorm(pr_levels, ncolors = plt.get_cmap(cmap.cmap('MPL_BrBG'), 14).N) # 15 bins means 14 edges
        ts_norm = mcolors.BoundaryNorm(ts_levels, ncolors = plt.get_cmap(cmap.cmap('MPL_YlOrRd'), 14).N) # 15 bins means 14 edges
        huss_norm = mcolors.BoundaryNorm(huss_levels, ncolors = plt.get_cmap(cmap.cmap('MPL_BuGn'), 7).N) # 8 bins means 7 edges

        # call contour function in specified ax location      
        precip_maps = axs[0][i].contourf(pr_data['lon'], pr_data['lat'], pr_data.values, levels = pr_levels, norm = pr_norm, cmap = cmap.cmap('MPL_BrBG'), extend = 'both', transform = ccrs.PlateCarree())
        temp_maps = axs[1][i].contourf(ts_data['lon'], ts_data['lat'], ts_data.values, levels = ts_levels, norm = ts_norm, cmap = cmap.cmap('MPL_YlOrRd'), extend = 'both', transform = ccrs.PlateCarree())
        huss_maps = axs[2][i].contourf(huss_data['lon'], huss_data['lat'], huss_data.values, levels = huss_levels, norm = huss_norm, cmap = cmap.cmap('MPL_BuGn'), extend = 'both', transform = ccrs.PlateCarree())
        
        for ax in [axs[0, i], axs[1, i], axs[2, i]]:
            ax.set_extent([-143, -67.5, 20, 44.5])
            
            # add features to each map
            ax.coastlines(linewidth = 1.5,color = 'k')
            
            states = cfeature.NaturalEarthFeature(category = 'cultural', name = 'admin_1_states_provinces_lines', scale = '50m', facecolor = 'none', edgecolor = 'k')
            countries = cfeature.NaturalEarthFeature(category = 'cultural', name = 'admin_0_boundary_lines_land', scale = '50m', facecolor = 'none', edgecolor = 'k')
            lakes = cfeature.NaturalEarthFeature(category = 'physical', name = 'lakes', scale = '50m', facecolor = 'none', edgecolor = 'k')
            
            ax.add_feature(states, linewidth = 1.5)
            ax.add_feature(countries, linewidth = 1.5)
            ax.add_feature(lakes, linewidth = 1.5)
            
        axs[0][i].text(0.02, 0.89, labels_one[i], fontsize = 30, fontweight = 'bold', transform = axs[0][i].transAxes)
        axs[1][i].text(0.02, 0.89, labels_two[i], fontsize = 30, fontweight = 'bold', transform = axs[1][i].transAxes)
        axs[2][i].text(0.02, 0.89, labels_three[i], fontsize = 30, fontweight = 'bold', transform = axs[2][i].transAxes)
    
    # PRECIPITATION COLORBAR
    # fine tuning control of colorbar size and placement
    pr_axins = inset_axes(ax, width = '10%', height = '20%', loc='center right', bbox_to_anchor = (0.935, 0.08, 0.08, 1.5), bbox_transform = fig.transFigure, borderpad = 0)

    # create a scalar mappable as a standin for contour so the colorbar remains standardized across different maps
    pr_sm = mpl.cm.ScalarMappable(norm = pr_norm, cmap =  cmap.cmap('MPL_BrBG'))
    pr_sm.set_array([])
    
    #  colorbar function passed using the scalar mappable 
    pr_cbar = fig.colorbar(pr_sm, cax = pr_axins, orientation = 'vertical', extend = 'both', ticks = pr_levels, boundaries = pr_levels, aspect = 50)
    pr_cbar.ax.tick_params(labelsize = 20)
    pr_cbar.ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
    
    # TEMPERATURE COLORBAR
    # fine tuning control of colorbar size and placement
    ts_axins = inset_axes(ax, width = '10%', height = '20%', loc='center right', bbox_to_anchor = (0.935, -0.25, 0.08, 1.5), bbox_transform = fig.transFigure, borderpad = 0)

    # create a scalar mappable as a standin for contour so the colorbar remains standardized across different maps
    ts_sm = mpl.cm.ScalarMappable(norm = ts_norm, cmap =  cmap.cmap('MPL_YlOrRd'))
    ts_sm.set_array([])
    
    #  colorbar function passed using the scalar mappable 
    ts_cbar = fig.colorbar(ts_sm, cax = ts_axins, orientation = 'vertical', extend = 'both', ticks = [0, 2.5, 5, 7.5, 10, 12.5, 15], boundaries = ts_levels, aspect = 50)
    ts_cbar.ax.tick_params(labelsize = 20)
    ts_cbar.ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
    
    # HUMIDITY COLORBAR
    # fine tuning control of colorbar size and placement
    huss_axins = inset_axes(ax, width = '10%', height = '20%', loc = 'center right', bbox_to_anchor = (0.935, -0.585, 0.08, 1.5), bbox_transform = fig.transFigure, borderpad = 0)

    # create a scalar mappable as a standin for contour so the colorbar remains standardized across different maps
    huss_sm = mpl.cm.ScalarMappable(norm = huss_norm, cmap = cmap.cmap('MPL_BuGn'))
    huss_sm.set_array([])
    
    # colorbar function passed using the scalar mappable 
    huss_cbar = fig.colorbar(huss_sm, cax = huss_axins, orientation = 'vertical', extend = 'both', ticks = huss_levels, boundaries = huss_levels, aspect = 50)
    huss_cbar.ax.tick_params(labelsize = 20)
    huss_cbar.ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
     
    fig.text(-1.7, 3.35, 'Wet Case', transform = ax.transAxes, fontsize = 60, va = 'top', ha = 'left', bbox = dict(facecolor = 'white', pad  = 1, edgecolor = 'white'))
    fig.text(-0.78, 3.35, 'Moderate Case', transform = ax.transAxes, fontsize = 60, va = 'top', ha = 'left', bbox = dict(facecolor = 'white', pad  = 1, edgecolor = 'white'))
    fig.text(0.4, 3.35, 'Dry Case', transform = ax.transAxes, fontsize = 60, va = 'top', ha = 'left', bbox = dict(facecolor = 'white', pad  = 1, edgecolor = 'white'))
    
    if save:
        # all PNGs stored to anomaly_maps directory but ignored in Git
        save_path = '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/variable_mapping/'
        save_path = os.path.join(save_path + save_name + '.png')
        plt.savefig(save_path, dpi = 400)
        
    plt.show()
    
figure5 = future_change_fig(6, 8, save_name = 'figure5')
      

def height_wind_fig(start_month, stop_month, save_name = 'test', save = False):
    """
    Geopotential height at 500 hPa with the average over the historical period
    displayed on the top row and anomaly from the historical to the future 
    period on the bottom row. 
    """
    
    fig, axs = plt.subplots(nrows = 2, ncols = 3, subplot_kw = {'projection': ccrs.PlateCarree()}, figsize = (33, 13.5))
    
    labels_one = ['a.', 'b.', 'c.']
    labels_two = ['d.', 'e.', 'f.']
    
    # loop for pecip anomalies on the top row
    for i, model in enumerate(models):
        mean_data = region_mean(model, 'zg', start_month, stop_month, level = 50000, zoom_out = True)
        anom_data = anomaly(model, 'zg', start_month, stop_month, level = 50000, zoom_out = True)
        
        # define levels
        mean_levels = np.array([5580, 5640, 5700, 5760, 5820, 5880, 5940, 6000])
        anom_levels = np.array([75, 85, 95, 105, 115, 125, 135, 145, 155, 165, 175, 185, 195])
        
        # define norms
        mean_norm = mcolors.BoundaryNorm(mean_levels, ncolors = plt.get_cmap(cmap.cmap('MPL_coolwarm'), 7).N) # 15 bins means 14 edges
        anom_norm = mcolors.BoundaryNorm(anom_levels, ncolors = plt.get_cmap(cmap.cmap('NCV_bright'), 12).N)
        
        # add mean geopotential height and wind data for the historical period to the top row
        mean_maps = axs[0][i].contourf(mean_data['lon'], mean_data['lat'], mean_data.values, levels = mean_levels, norm = mean_norm, cmap = cmap.cmap('MPL_coolwarm'), extend = 'both', transform = ccrs.PlateCarree())
        mean_quiver, mean_key = quiver('ua', 'va', axs[0][i], region_mean, model, start_month, stop_month, level = 50000, zoom_out = True)
        
        # add anomaly data to the bottom row
        anom_maps = axs[1][i].contourf(anom_data['lon'], anom_data['lat'], anom_data.values, levels = anom_levels, norm = anom_norm, cmap = cmap.cmap('NCV_bright'), extend = 'both', transform = ccrs.PlateCarree())
        anom_quiver, anom_key = quiver('ua', 'va', axs[1][i], anomaly, model, start_month, stop_month, level = 50000, zoom_out = True)
        
        for ax in [axs[0, i], axs[1, i]]:
            ax.set_extent([-157.75, -61.5, 1.25, 55])
 
            # add features to each map
            ax.coastlines(linewidth = 1.5,color = 'k')

            states = cfeature.NaturalEarthFeature(category = 'cultural', name = 'admin_1_states_provinces_lines', scale = '50m', facecolor = 'none', edgecolor = 'k')
            countries = cfeature.NaturalEarthFeature(category = 'cultural', name = 'admin_0_boundary_lines_land', scale = '50m', facecolor = 'none', edgecolor = 'k')
            lakes = cfeature.NaturalEarthFeature(category = 'physical', name = 'lakes', scale = '50m', facecolor = 'none', edgecolor = 'k')
            
            ax.add_feature(states, linewidth = 1.5)
            ax.add_feature(countries, linewidth = 1.5)
            ax.add_feature(lakes, linewidth = 1.5)
            
        axs[0][i].text(0.02, 0.88, labels_one[i], fontsize = 60, transform = axs[0][i].transAxes)
        axs[1][i].text(0.02, 0.88, labels_two[i], fontsize = 60, transform = axs[1][i].transAxes)
            
    # create a scalar mappable as a standin for contour so the colorbar remains standardized across different maps
    mean_sm = mpl.cm.ScalarMappable(norm = mean_norm, cmap = cmap.cmap('MPL_coolwarm'))
    mean_sm.set_array([])
    
    # colorbar function passed using the scalar mappable 
    mean_cbar = fig.colorbar(mean_sm, ax = axs, orientation = 'vertical', extend = 'both', ticks = mean_levels, boundaries = mean_levels, aspect = 30, location = 'left', pad = 0.015)
    mean_cbar.ax.tick_params(labelsize = 20)
    mean_cbar.ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
    
    # create a scalar mappable as a standin for contour so the colorbar remains standardized across different maps
    anom_sm = mpl.cm.ScalarMappable(norm = anom_norm, cmap =  cmap.cmap('NCV_bright'))
    anom_sm.set_array([])
    
    # colorbar function passed using the scalar mappable 
    anom_cbar = fig.colorbar(anom_sm, ax = axs, orientation = 'vertical', extend = 'both', ticks = anom_levels, boundaries = [75, 95, 115, 135, 155, 175, 195], aspect = 30, location = 'right', pad = 0.015)
    anom_cbar.ax.tick_params(labelsize = 20)
    anom_cbar.ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
    
    fig.text(-1.75, 2.2, 'Wet Case', transform = ax.transAxes, fontsize = 50, va = 'top', ha = 'left', bbox = dict(facecolor = 'white', pad  = 1, edgecolor = 'white'))
    fig.text(-0.82, 2.2, 'Moderate Case', transform = ax.transAxes, fontsize = 50, va = 'top', ha = 'left', bbox = dict(facecolor = 'white', pad  = 1, edgecolor = 'white'))
    fig.text(0.34, 2.2, 'Dry Case', transform = ax.transAxes, fontsize = 50, va = 'top', ha = 'left', bbox = dict(facecolor = 'white', pad  = 1, edgecolor = 'white'))
    
    if save:
        # all PNGs stored to anomaly_maps directory but ignored in Git
        save_path = '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/variable_mapping/'
        save_path = os.path.join(save_path + save_name + '.png')
        plt.savefig(save_path, dpi = 400)
      
    plt.show()

figure_S4 = height_wind_fig(6, 8, save_name = 'figure_S4')


def humidity_fig(start_month, stop_month, save_name = 'test', save = False):
    fig, axs = plt.subplots(nrows = 2, ncols = 3, subplot_kw = {'projection': ccrs.PlateCarree()}, figsize = (42, 11.5))
    
    labels_one = ['a.', 'b.', 'c.']
    labels_two = ['d.', 'e.', 'f.']
    
    # loop for pecip anomalies on the top row
    for i, model in enumerate(models):
        mean_data = region_mean(model, 'huss', start_month, stop_month)
        anom_data = anomaly(model, 'huss', start_month, stop_month)
        mean_maps = axs[0][i].contourf(mean_data['lon'], mean_data['lat'], mean_data.values, 
                                       levels = np.linspace(4, 27, 15), 
                                       norm = mcolors.TwoSlopeNorm(vmin = 4, vcenter = 15, vmax = 27), 
                                       cmap = cmap.cmap('MPL_YlGnBu',), 
                                       extend = 'both', 
                                       transform = ccrs.PlateCarree())
        
        anom_maps = axs[1][i].contourf(anom_data['lon'], anom_data['lat'], anom_data.values, 
                                       levels = np.linspace(0, 7, 15), 
                                       norm = mcolors.TwoSlopeNorm(vmin = 0, vcenter = 3.5, vmax = 7), 
                                       cmap = cmap.cmap('MPL_BuGn'), 
                                       extend = 'both', 
                                       transform = ccrs.PlateCarree())
        
        for ax in [axs[0, i], axs[1, i]]:
            ax.set_extent([-143, -67.5, 20, 44.8])
            
            # add features to each map
            ax.coastlines(linewidth = 1,color = 'k')

            states = cfeature.NaturalEarthFeature(category = 'cultural', name = 'admin_1_states_provinces_lines', scale = '50m', facecolor = 'none', edgecolor = 'k')
            countries = cfeature.NaturalEarthFeature(category = 'cultural', name = 'admin_0_boundary_lines_land', scale = '50m', facecolor = 'none', edgecolor = 'k')
            lakes = cfeature.NaturalEarthFeature(category = 'physical', name = 'lakes', scale = '50m', facecolor = 'none', edgecolor = 'k')
            
            ax.add_feature(states, linewidth = 1)
            ax.add_feature(countries, linewidth = 1)
            ax.add_feature(lakes, linewidth = 1)
            
        axs[0][i].text(0.02, 0.89, labels_one[i], fontsize = 30, fontweight = 'bold', transform = axs[0][i].transAxes)
        axs[1][i].text(0.02, 0.89, labels_two[i], fontsize = 30, fontweight = 'bold', transform = axs[1][i].transAxes)
            
    mean_cbar = color_bar(4, 15, 27, cmap.cmap('MPL_YlGnBu'), 'left', axs)
    anom_cbar = color_bar(0, 3.5, 7, cmap.cmap('MPL_BuGn'), 'right', axs)
    
    if save:
        # all PNGs stored to anomaly_maps directory but ignored in Git
        save_path = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/variable_mapping/test_maps'
        save_path = os.path.join(save_path + save_name + '.png')
        plt.savefig(save_path, dpi = 400)
      
    plt.show()
    
humidity_fig(6, 8)