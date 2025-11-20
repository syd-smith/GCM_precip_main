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
    """
    Function to simply create a colorbar for maps. Note that this colorbar
    won't be standardized using a scalar mappable to apply to multiple maps. 
    """
    
    ticks = bp.np.linspace(var_min, var_max, num = 10)
    norm = bp.mcolors.TwoSlopeNorm(vmin = var_min, vcenter = var_center, vmax = var_max)

    # create a scalar mappable as a standin for contour so the colorbar remains standardized across different maps
    sm = bp.mpl.cm.ScalarMappable(norm = norm, cmap = color)
    sm.set_array([]) # makes sure no data is attached to the colorbar
    
    # specify the layout of the colorbar
    cbar = bp.plt.colorbar(sm, ax = axs, orientation = 'vertical', pad = 0.015, aspect = 50, extend = 'both', ticks = ticks, location = location)
    cbar.ax.yaxis.set_major_formatter(bp.ticker.FormatStrFormatter('%.0f'))
    cbar.ax.tick_params(labelsize = 30)
    
    return cbar


#%%
def future_change_fig(start_month, stop_month, save_name = 'test', save = False):
    """
    Function used to create the final maps displaying the expected future change
    in precipitation across the continential US. Note that the selected models
    range from high precipitation outputs on the left (UKESM1-0-LL) with no 
    precipiation change in the center (HadGEM3-GC31-MM) and low precipitation
    outputs on the right (MPI-ESM1-2-LR). 
    """
 
    fig, axs = bp.plt.subplots(nrows = 3, ncols = 3, subplot_kw = {'projection': bp.ccrs.PlateCarree()}, figsize = (40, 17.5))
    
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
        pr_levels = bp.np.linspace(-150, 150, 15) # 15 bins means 14 edges
        ts_levels = bp.np.linspace(0, 15, 15)
        huss_levels = bp.np.linspace(0, 7, 15)
        
        # define norm values to standardize colorbar to map colors
        pr_norm = bp.mcolors.BoundaryNorm(pr_levels, ncolors = bp.plt.get_cmap(bp.cmap.cmap('MPL_BrBG'), 14).N) # 15 bins means 14 edges
        ts_norm = bp.mcolors.BoundaryNorm(ts_levels, ncolors = bp.plt.get_cmap(bp.cmap.cmap('MPL_YlOrRd'), 14).N) # 15 bins means 14 edges
        huss_norm = bp.mcolors.BoundaryNorm(huss_levels, ncolors = bp.plt.get_cmap(bp.cmap.cmap('MPL_BuGn'), 14).N) # 15 bins means 14 edges

        # call contour function in specified ax location      
        precip_maps = axs[0][i].contourf(pr_data['lon'], pr_data['lat'], pr_data.values, levels = pr_levels, norm = pr_norm, cmap = bp.cmap.cmap('MPL_BrBG'), extend = 'both', transform = bp.ccrs.PlateCarree())
        temp_maps = axs[1][i].contourf(ts_data['lon'], ts_data['lat'], ts_data.values, levels = ts_levels, norm = ts_norm, cmap = bp.cmap.cmap('MPL_YlOrRd'), extend = 'both', transform = bp.ccrs.PlateCarree())
        huss_maps = axs[2][i].contourf(huss_data['lon'], huss_data['lat'], huss_data.values, levels = huss_levels, norm = huss_norm, cmap = bp.cmap.cmap('MPL_BuGn'), extend = 'both', transform = bp.ccrs.PlateCarree())
        
        for ax in [axs[0, i], axs[1, i], axs[2, i]]:
            ax.set_extent([-143, -67.5, 20, 44.5])
            
            # add features to each map
            ax.coastlines(linewidth = 1.5,color = 'k')
            
            states = bp.cfeature.NaturalEarthFeature(category = 'cultural', name = 'admin_1_states_provinces_lines', scale = '50m', facecolor = 'none', edgecolor = 'k')
            countries = bp.cfeature.NaturalEarthFeature(category = 'cultural', name = 'admin_0_boundary_lines_land', scale = '50m', facecolor = 'none', edgecolor = 'k')
            lakes = bp.cfeature.NaturalEarthFeature(category = 'physical', name = 'lakes', scale = '50m', facecolor = 'none', edgecolor = 'k')
            
            ax.add_feature(states, linewidth = 1.5)
            ax.add_feature(countries, linewidth = 1.5)
            ax.add_feature(lakes, linewidth = 1.5)
            
        axs[0][i].text(0.02, 0.89, labels_one[i], fontsize = 30, fontweight = 'bold', transform = axs[0][i].transAxes)
        axs[1][i].text(0.02, 0.89, labels_two[i], fontsize = 30, fontweight = 'bold', transform = axs[1][i].transAxes)
        axs[2][i].text(0.02, 0.89, labels_three[i], fontsize = 30, fontweight = 'bold', transform = axs[2][i].transAxes)
    
    # PRECIPITATION COLORBAR
    # fine tuning control of colorbar size and placement
    pr_axins = bp.inset_axes(ax, width = '10%', height = '20%', loc='center right', bbox_to_anchor = (0.98, 0.08, 0.05, 1.5), bbox_transform = fig.transFigure, borderpad = 0)

    # create a scalar mappable as a standin for contour so the colorbar remains standardized across different maps
    pr_sm = bp.mpl.cm.ScalarMappable(norm = pr_norm, cmap =  bp.cmap.cmap('MPL_BrBG'))
    pr_sm.set_array([])
    
    #  colorbar function passed using the scalar mappable 
    pr_cbar = fig.colorbar(pr_sm, cax = pr_axins, orientation = 'vertical', extend = 'both', ticks = pr_levels, boundaries = pr_levels, aspect = 50)
    pr_cbar.ax.tick_params(labelsize = 20)
    pr_cbar.ax.yaxis.set_major_formatter(bp.ticker.FormatStrFormatter('%.0f'))
    
    # TEMPERATURE COLORBAR
    # fine tuning control of colorbar size and placement
    ts_axins = bp.inset_axes(ax, width = '10%', height = '20%', loc='center right', bbox_to_anchor = (0.98, -0.25, 0.05, 1.5), bbox_transform = fig.transFigure, borderpad = 0)

    # create a scalar mappable as a standin for contour so the colorbar remains standardized across different maps
    ts_sm = bp.mpl.cm.ScalarMappable(norm = ts_norm, cmap =  bp.cmap.cmap('MPL_YlOrRd'))
    ts_sm.set_array([])
    
    #  colorbar function passed using the scalar mappable 
    ts_cbar = fig.colorbar(ts_sm, cax = ts_axins, orientation = 'vertical', extend = 'both', ticks = ts_levels, boundaries = ts_levels, aspect = 50)
    ts_cbar.ax.tick_params(labelsize = 20)
    ts_cbar.ax.yaxis.set_major_formatter(bp.ticker.FormatStrFormatter('%.0f'))
    
    # HUMIDITY COLORBAR
    # fine tuning control of colorbar size and placement
    huss_axins = bp.inset_axes(ax, width = '10%', height = '20%', loc='center right', bbox_to_anchor = (0.98, -0.585, 0.05, 1.5), bbox_transform = fig.transFigure, borderpad = 0)

    # create a scalar mappable as a standin for contour so the colorbar remains standardized across different maps
    huss_sm = bp.mpl.cm.ScalarMappable(norm = huss_norm, cmap =  bp.cmap.cmap('MPL_BuGn'))
    huss_sm.set_array([])
    
    # colorbar function passed using the scalar mappable 
    huss_cbar = fig.colorbar(huss_sm, cax = huss_axins, orientation = 'vertical', extend = 'both', ticks = huss_levels, boundaries = huss_levels, aspect = 50)
    huss_cbar.ax.tick_params(labelsize = 20)
    huss_cbar.ax.yaxis.set_major_formatter(bp.ticker.FormatStrFormatter('%.0f'))
      
    if save:
        # all PNGs stored to anomaly_maps directory but ignored in Git
        save_path = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/anomaly_maps/paper_figs/'
        save_path = bp.os.path.join(save_path + save_name + '.png')
        bp.plt.savefig(save_path, dpi = 400)
        
    bp.plt.show()
    
future_change_fig(6, 8)
      

#%%
def height_wind_fig(start_month, stop_month, save_name = 'test', save = False):
    """
    Geopotential height at 500 hPa with the average over the historical period
    displayed on the top row and anomaly from the historical to the future 
    period on the bottom row. 
    """
    
    fig, axs = bp.plt.subplots(nrows = 2, ncols = 3, subplot_kw = {'projection': bp.ccrs.PlateCarree()}, figsize = (33, 13.5))
    
    labels_one = ['a.', 'b.', 'c.']
    labels_two = ['d.', 'e.', 'f.']
    
    # loop for pecip anomalies on the top row
    for i, model in enumerate(models):
        mean_data = region_mean(model, 'zg', start_month, stop_month, level = 50000, zoom_out = True)
        anom_data = anomaly(model, 'zg', start_month, stop_month, level = 50000, zoom_out = True)
        
        # define levels
        mean_levels = bp.np.linspace(5675, 5975, 15)
        anom_levels = bp.np.linspace(75, 200, 15)
        
        # define norms
        mean_norm = bp.mcolors.BoundaryNorm(mean_levels, ncolors = bp.plt.get_cmap(bp.cmap.cmap('MPL_coolwarm'), 14).N) # 15 bins means 14 edges
        anom_norm = bp.mcolors.BoundaryNorm(anom_levels, ncolors = bp.plt.get_cmap(bp.cmap.cmap('NCV_bright'), 14).N)
        
        # add mean geopotential height and wind data for the historical period to the top row
        mean_maps = axs[0][i].contourf(mean_data['lon'], mean_data['lat'], mean_data.values, levels = mean_levels, norm = mean_norm, cmap = bp.cmap.cmap('MPL_coolwarm'), extend = 'both', transform = bp.ccrs.PlateCarree())
        mean_quiver, mean_key = quiver('ua', 'va', axs[0][i], region_mean, model, start_month, stop_month, level = 50000, zoom_out = True)
        
        # add anomaly data to the bottom row
        anom_maps = axs[1][i].contourf(anom_data['lon'], anom_data['lat'], anom_data.values, levels = anom_levels, norm = anom_norm, cmap = bp.cmap.cmap('NCV_bright'), extend = 'both', transform = bp.ccrs.PlateCarree())
        anom_quiver, anom_key = quiver('ua', 'va', axs[1][i], anomaly, model, start_month, stop_month, level = 50000, zoom_out = True)
        
        for ax in [axs[0, i], axs[1, i]]:
            ax.set_extent([-157.75, -61.5, 1.25, 55])
 
            # add features to each map
            ax.coastlines(linewidth = 1.5,color = 'k')

            states = bp.cfeature.NaturalEarthFeature(category = 'cultural', name = 'admin_1_states_provinces_lines', scale = '50m', facecolor = 'none', edgecolor = 'k')
            countries = bp.cfeature.NaturalEarthFeature(category = 'cultural', name = 'admin_0_boundary_lines_land', scale = '50m', facecolor = 'none', edgecolor = 'k')
            lakes = bp.cfeature.NaturalEarthFeature(category = 'physical', name = 'lakes', scale = '50m', facecolor = 'none', edgecolor = 'k')
            
            ax.add_feature(states, linewidth = 1.5)
            ax.add_feature(countries, linewidth = 1.5)
            ax.add_feature(lakes, linewidth = 1.5)
            
        axs[0][i].text(0.02, 0.88, labels_one[i], fontsize = 60, transform = axs[0][i].transAxes)
        axs[1][i].text(0.02, 0.88, labels_two[i], fontsize = 60, transform = axs[1][i].transAxes)
            
    # create a scalar mappable as a standin for contour so the colorbar remains standardized across different maps
    mean_sm = bp.mpl.cm.ScalarMappable(norm = mean_norm, cmap =  bp.cmap.cmap('MPL_coolwarm'))
    mean_sm.set_array([])
    
    # colorbar function passed using the scalar mappable 
    mean_cbar = fig.colorbar(mean_sm, ax = axs, orientation = 'vertical', extend = 'both', ticks = mean_levels, boundaries = mean_levels, aspect = 50, location = 'left', pad = 0.015)
    mean_cbar.ax.tick_params(labelsize = 20)
    mean_cbar.ax.yaxis.set_major_formatter(bp.ticker.FormatStrFormatter('%.0f'))
    
    # create a scalar mappable as a standin for contour so the colorbar remains standardized across different maps
    anom_sm = bp.mpl.cm.ScalarMappable(norm = anom_norm, cmap =  bp.cmap.cmap('NCV_bright'))
    anom_sm.set_array([])
    
    # colorbar function passed using the scalar mappable 
    anom_cbar = fig.colorbar(anom_sm, ax = axs, orientation = 'vertical', extend = 'both', ticks = anom_levels, boundaries = anom_levels, aspect = 50, location = 'right', pad = 0.015)
    anom_cbar.ax.tick_params(labelsize = 20)
    anom_cbar.ax.yaxis.set_major_formatter(bp.ticker.FormatStrFormatter('%.0f'))
    
    if save:
        # all PNGs stored to anomaly_maps directory but ignored in Git
        save_path = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/anomaly_maps/paper_figs/'
        save_path = bp.os.path.join(save_path + save_name + '.png')
        bp.plt.savefig(save_path, dpi = 400)
      
    bp.plt.show()

height_wind_fig(6, 8)


#%%

def humidity_fig(start_month, stop_month, save_name = 'test', save = False):
    fig, axs = bp.plt.subplots(nrows = 2, ncols = 3, subplot_kw = {'projection': bp.ccrs.PlateCarree()}, figsize = (42, 11.5))
    
    labels_one = ['a.', 'b.', 'c.']
    labels_two = ['d.', 'e.', 'f.']
    
    # loop for pecip anomalies on the top row
    for i, model in enumerate(models):
        mean_data = region_mean(model, 'huss', start_month, stop_month)
        anom_data = anomaly(model, 'huss', start_month, stop_month)
        mean_maps = axs[0][i].contourf(mean_data['lon'], mean_data['lat'], mean_data.values, levels = bp.np.linspace(4, 27, 15), norm = bp.mcolors.TwoSlopeNorm(vmin = 4, vcenter = 15, vmax = 27), cmap = bp.cmap.cmap('MPL_YlGnBu',), extend = 'both', transform = bp.ccrs.PlateCarree(),)
        anom_maps = axs[1][i].contourf(anom_data['lon'], anom_data['lat'], anom_data.values, levels = bp.np.linspace(0, 7, 15), norm = bp.mcolors.TwoSlopeNorm(vmin = 0, vcenter = 3.5, vmax = 7), cmap = bp.cmap.cmap('MPL_BuGn'), extend = 'both', transform = bp.ccrs.PlateCarree(),)
        
        for ax in [axs[0, i], axs[1, i]]:
            ax.set_extent([-143, -67.5, 20, 44.8])
            
            # add features to each map
            ax.coastlines(linewidth = 1,color = 'k')

            states = bp.cfeature.NaturalEarthFeature(category = 'cultural', name = 'admin_1_states_provinces_lines', scale = '50m', facecolor = 'none', edgecolor = 'k')
            countries = bp.cfeature.NaturalEarthFeature(category = 'cultural', name = 'admin_0_boundary_lines_land', scale = '50m', facecolor = 'none', edgecolor = 'k')
            lakes = bp.cfeature.NaturalEarthFeature(category = 'physical', name = 'lakes', scale = '50m', facecolor = 'none', edgecolor = 'k')
            
            ax.add_feature(states, linewidth = 1)
            ax.add_feature(countries, linewidth = 1)
            ax.add_feature(lakes, linewidth = 1)
            
        axs[0][i].text(0.02, 0.89, labels_one[i], fontsize = 30, fontweight = 'bold', transform = axs[0][i].transAxes)
        axs[1][i].text(0.02, 0.89, labels_two[i], fontsize = 30, fontweight = 'bold', transform = axs[1][i].transAxes)
            
    mean_cbar = color_bar(4, 15, 27, bp.cmap.cmap('MPL_YlGnBu'), 'left', axs)
    anom_cbar = color_bar(0, 3.5, 7, bp.cmap.cmap('MPL_BuGn'), 'right', axs)
    
    if save:
        # all PNGs stored to anomaly_maps directory but ignored in Git
        save_path = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/anomaly_maps/paper_figs/'
        save_path = bp.os.path.join(save_path + save_name + '.png')
        bp.plt.savefig(save_path, dpi = 400)
      
    bp.plt.show()
    
humidity_fig(6, 8)