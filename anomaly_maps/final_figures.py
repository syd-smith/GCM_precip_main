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

#%%
def color_bar(var_min, var_center, var_max, color, location, axs):
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


def future_change_fig(start_month, stop_month, save_name = 'test', save = False):
 
    fig, axs = bp.plt.subplots(nrows = 3, ncols = 3, subplot_kw = {'projection': bp.ccrs.PlateCarree()}, figsize = (40, 17.5))
    
    labels_one = ['a.', 'b.', 'c.']
    labels_two = ['d.', 'e.', 'f.']
    labels_three = ['g.', 'h.', 'i.']
    
    # loop for pecip anomalies on the top row
    for i, model in enumerate(models):
        precip_data = anomaly(model, 'pr', start_month, stop_month)
        temp_data = anomaly(model, 'ts', start_month, stop_month)
        huss_data = anomaly(model, 'huss', start_month, stop_month)
        precip_maps = axs[0][i].contourf(precip_data['lon'], precip_data['lat'], precip_data.values, levels = bp.np.linspace(-150, 150, 15), norm = bp.mcolors.TwoSlopeNorm(vmin = -150, vcenter = 0, vmax = 150), cmap = bp.cmap.cmap('MPL_BrBG'), extend = 'both', transform = bp.ccrs.PlateCarree())
        temp_maps = axs[1][i].contourf(temp_data['lon'], temp_data['lat'], temp_data.values, levels = bp.np.linspace(0, 15, 15), norm = bp.mcolors.TwoSlopeNorm(vmin = 0, vcenter = 7.5, vmax = 15),cmap = bp.cmap.cmap('MPL_YlOrRd'), extend = 'both', transform = bp.ccrs.PlateCarree())
        huss_maps = axs[2][i].contourf(huss_data['lon'], huss_data['lat'], huss_data.values, levels = bp.np.linspace(0, 7, 15), norm = bp.mcolors.TwoSlopeNorm(vmin = 0, vcenter = 3.5, vmax = 7), cmap = bp.cmap.cmap('MPL_BuGn'), extend = 'both', transform = bp.ccrs.PlateCarree())
        
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
    
    # norm and tick parameters to standardize colorbar to map color
    pr_norm = bp.mcolors.TwoSlopeNorm(vmin = -150, vcenter = 0, vmax = 150)
    pr_ticks = bp.np.linspace(-150, 150, num = 15)

    # create a scalar mappable as a standin for contour so the colorbar remains standardized across different maps
    pr_sm = bp.mpl.cm.ScalarMappable(norm = pr_norm, cmap =  bp.cmap.cmap('MPL_BrBG'))
    pr_sm.set_array([])
    
    #  colorbar function passed using the scalar mappable 
    pr_cbar = fig.colorbar(pr_sm, cax = pr_axins, orientation = 'vertical', extend = 'both', ticks = pr_ticks, aspect = 50)
    pr_cbar.ax.tick_params(labelsize = 20)
    pr_cbar.ax.yaxis.set_major_formatter(bp.ticker.FormatStrFormatter('%.0f'))
    
    # TEMPERATURE COLORBAR
    # fine tuning control of colorbar size and placement
    ts_axins = bp.inset_axes(ax, width = '10%', height = '20%', loc='center right', bbox_to_anchor = (0.98, -0.25, 0.05, 1.5), bbox_transform = fig.transFigure, borderpad = 0)
    
    # norm and tick parameters to standardize colorbar to map color
    ts_norm = bp.mcolors.TwoSlopeNorm(vmin = 0, vcenter = 7.5, vmax = 15)
    ts_ticks = bp.np.linspace(0, 15, num = 15)

    # create a scalar mappable as a standin for contour so the colorbar remains standardized across different maps
    ts_sm = bp.mpl.cm.ScalarMappable(norm = ts_norm, cmap =  bp.cmap.cmap('MPL_YlOrRd'))
    ts_sm.set_array([])
    
    #  colorbar function passed using the scalar mappable 
    ts_cbar = fig.colorbar(ts_sm, cax = ts_axins, orientation = 'vertical', extend = 'both', ticks = ts_ticks, aspect = 50)
    ts_cbar.ax.tick_params(labelsize = 20)
    ts_cbar.ax.yaxis.set_major_formatter(bp.ticker.FormatStrFormatter('%.0f'))
    
    # HUMIDITY COLORBAR
    # fine tuning control of colorbar size and placement
    huss_axins = bp.inset_axes(ax, width = '10%', height = '20%', loc='center right', bbox_to_anchor = (0.98, -0.585, 0.05, 1.5), bbox_transform = fig.transFigure, borderpad = 0)
    
    # norm and tick parameters to standardize colorbar to map color
    huss_norm = bp.mcolors.TwoSlopeNorm(vmin = 0, vcenter = 3.5, vmax = 7)
    huss_ticks = bp.np.linspace(0, 7, num = 15)

    # create a scalar mappable as a standin for contour so the colorbar remains standardized across different maps
    huss_sm = bp.mpl.cm.ScalarMappable(norm = huss_norm, cmap =  bp.cmap.cmap('MPL_BuGn'))
    huss_sm.set_array([])
    
    # colorbar function passed using the scalar mappable 
    huss_cbar = fig.colorbar(huss_sm, cax = huss_axins, orientation = 'vertical', extend = 'both', ticks = huss_ticks, aspect = 50)
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
    fig, axs = bp.plt.subplots(nrows = 2, ncols = 3, subplot_kw = {'projection': bp.ccrs.PlateCarree()}, figsize = (33, 13.5))
    
    labels_one = ['a.', 'b.', 'c.']
    labels_two = ['d.', 'e.', 'f.']
    
    # loop for pecip anomalies on the top row
    for i, model in enumerate(models):
        mean_data = region_mean(model, 'zg', start_month, stop_month, level = 50000, zoom_out = True)
        anom_data = anomaly(model, 'zg', start_month, stop_month, level = 50000, zoom_out = True)
        
        # add mean geopotential height and wind data for the historical period to the top row
        mean_maps = axs[0][i].contourf(mean_data['lon'], mean_data['lat'], mean_data.values, levels = bp.np.linspace(5675, 5975, 15), norm = bp.mcolors.TwoSlopeNorm(vmin = 5675, vcenter = 5825, vmax = 5975), cmap = bp.cmap.cmap('MPL_coolwarm'), extend = 'both', transform = bp.ccrs.PlateCarree())
        mean_quiver, mean_key = quiver('ua', 'va', axs[0][i], region_mean, model, start_month, stop_month, level = 50000, zoom_out = True)
        
        # add anomaly data to the bottom row
        anom_maps = axs[1][i].contourf(anom_data['lon'], anom_data['lat'], anom_data.values, levels = bp.np.linspace(75, 200, 15), norm = bp.mcolors.TwoSlopeNorm(vmin = 75, vcenter = 138, vmax = 200), cmap = bp.cmap.cmap('NCV_bright'), extend = 'both', transform = bp.ccrs.PlateCarree())
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
            
    mean_cbar = color_bar(5675, 5825, 5975, bp.cmap.cmap('MPL_coolwarm'), 'left', axs)
    anom_cbar = color_bar(75, 138, 200, bp.cmap.cmap('NCV_bright'), 'right', axs)
    
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