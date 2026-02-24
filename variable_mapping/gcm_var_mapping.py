#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 13:05:53 2025

@author: u1301408
"""

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import geopandas as gpd
import glob
import matplotlib as mpl
import matplotlib.colors as mcolors
from matplotlib.patches import FancyBboxPatch
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import os
import sys
import xarray as xr
import xesmf as xe

sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/variable_mapping/')
from map_formatting import variable_dict


# Define the shapefile path (where to find coordinates used by VIC from Maribeth at USBR)
bdir = '/uufs/chpc.utah.edu/common/home/u0660911/Documents/projects/gslbip/'
shapefile_path = os.path.join(bdir,'GSLBIP_shpfiles/MF6_VIC_bounding_box/MF6_VIC_bounding_box.shp')

# Load the shapefile for VIC boundaries of Great Salt Lake Basin (not applied for larger maps)
gdf = gpd.read_file(shapefile_path)
gdf = gdf.to_crs("EPSG:4326")
min_lon, min_lat, max_lon, max_lat = gdf.total_bounds

# output of values in VIC shapefile
# min_lon = -113.69354024533703
# max_lon = -110.59375
# min_lat = 39.553038338687124
# max_lat = 42.84375

time_dict = {
    range(5, 6) :'May',
    range(6, 7) : 'June', 
    range(7, 8) : 'July',
    range(8, 9) : 'August',
    range(9, 10) : 'September', 
    range(5, 7) : 'MJ',
    range(5, 8) : 'MJJ',
    range(6, 8) : 'JJ',
    range(6, 9) : 'JJA',
    range(7, 9) : 'JA',
    range(7, 10) : 'JAS',
    range(8, 10): 'AS'
    }


# MODELS USED FOR LATEST GROUPING -> WET, MODERATE, DRY
# listed in order from highest to lowest
W_models = ['KACE-1-0-G', 'CanESM5', 'UKESM1-0-LL', 'ACCESS-CM2', 'HadGEM3-GC31-LL']
M_models = ['HadGEM3-GC31-MM']
D_models = ['MPI-ESM1-2-LR']
models = ['KACE-1-0-G', 'CanESM5', 'UKESM1-0-LL', 'ACCESS-CM2', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'MPI-ESM1-2-LR']

# MODELS USED FOR INITIAL GROUPING OF HIGH AND LOW
# wet models from figure2.py (high precip ratio)
# H_models = ['UKESM1-0-LL', 'ACCESS-CM2', 'CanESM5', 'KACE-1-0-G']

# dry models from figure2.py (low precip ratio)
# L_models = ['MPI-ESM1-2-LR', 'CNRM-ESM2-1', 'CNRM-CM6-1-HR', 'INM-CM4-8']


def region_mean(model_name, variable, start_month, stop_month, level = None, start_year = 1979, stop_year = 2014, zoom_out = False, *kwargs): 
    
    """
    Function to calculate the mean for each gridpoint across the historical period 
    (1979-2014). Intended to run for the summer months. Zoom out expands the region 
    to have a broader view of the Pacific Ocean. Returns an xarray.DataArray.
    
    Note that the level (plev) is selected in Pa not hPa so 500 hPa = 50000.
    """
    
    fpath = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/ERA5/{variable}/{variable}_Amon_'
    
    # lets the function know what file to open for the given model and variable based on date range
    if 1970 <= start_year <= 2014:
        date = '_hist*.nc'
    else:
        date = '_ssp585*.nc'
    
    fname = fpath + model_name + date
    ds = xr.open_mfdataset(glob.glob(fname), decode_times = True)
    # print('Files Found:', glob.glob(fname))
    
    # variables that have an extra dimension for what pressure level you want to look at needs to be selected
    # geopotential height should be at the  500 hPa level
    if not level:
        print('No level to select for this variable')
    else:
        ds = ds.sel(plev = level, method = 'nearest')
    
    if zoom_out:
        location = ds[variable].sel(lat = slice(0, 65), lon = slice(200, 300))
    else: 
        location = ds[variable].sel(lat = slice(15, 53), lon = slice(215, 295))
        
    years = range(start_year, stop_year + 1)
    JJA = location.sel(time = location.time.dt.month.isin(range(start_month, stop_month + 1)))
    means = []
    for year in years:
        year = JJA.sel(time = JJA.time.dt.year == year)
        
        # GCM pr data is in precipitation flux so the time unit has to be taken out
        if variable == 'pr':
            days_in_month = year.time.dt.days_in_month
            seconds_per_month = days_in_month * 24 * 60 * 60
            mean = (year * seconds_per_month).mean(dim = 'time', skipna = True)
        else:
            mean = year.mean(dim = 'time', skipna = True)
            
        means.append(mean)        
    combine_means = xr.concat(means, dim = 'year')
    overall_mean = combine_means.mean(dim = 'year')
    
    if variable == 'psl':
        overall_mean *= 0.01 # convert from Pa to hPa
    elif variable == 'huss' or variable == 'hus':
        overall_mean *= 1000 # convert from kg/kg to g/kg

    return overall_mean


def anomaly(model_name, variable, start_month, stop_month, level = None, zoom_out = False, *kwargs):
    
    """
    Function to calculate the change in a variable from 1979-2014 to 2070-2099 as a 
    difference (precipitation is calculated as a percent change) by passing the mean
    calculation from the above function. Note that date ranges need to manually be 
    changed if they vary from those in this study. Returns an xarray.DataArray.
    
    Note that the level (plev) is selected in Pa not hPa so 500 hPa = 50000.
    """
    
    overall_mean_hist = region_mean(model_name, variable, start_month, stop_month, level, start_year = 1979, stop_year = 2014, zoom_out = zoom_out)
    overall_mean_fut = region_mean(model_name, variable, start_month, stop_month, level, start_year = 2070, stop_year = 2099, zoom_out = zoom_out)
        
    # Sets up all variables as a difference between time periods except for precipitation as a percent change
    if variable == 'pr':
        anomaly = ((overall_mean_fut - overall_mean_hist) / overall_mean_hist) * 100
    else:
        anomaly = overall_mean_fut - overall_mean_hist

    return anomaly

# example of the anomaly function being used to return a lat and lon xarray.DataArray for the specified variable
# vas = anomaly('ACCESS-CM2', 'vas')


def quiver(u, v, ax, anomaly_ref, model_name, start_month, stop_month, level, start_year = 1979, stop_year = 2014, zoom_out = False, step = 1, *kwargs):
    
    """
    Adds an overlay of wind vectors as arrows. Made to integrate with map_anomalies 
    function. Make sure to call the same level that coordinates with the contour
    variable.
    
    The only arguements that should be adjusted are which u and v values should 
    be selected. It is optional to adjust the step  size (spacing of the arrows).
    All other arguements will be pulled from the map_anomaly function.
    
    Note that the level (plev) is selected in Pa not hPa so 500 hPa = 50000.
    """
    
    # call wind data
    u = anomaly_ref(model_name, u, start_month, stop_month, level, zoom_out = zoom_out)
    v = anomaly_ref(model_name, v, start_month, stop_month, level, zoom_out = zoom_out)
            
    # set scale to adjust based on being an anomaly or fut/hist mean
    if anomaly_ref.__name__ == 'anomaly':
        scale = 75
        U = 1
        label = '1 m/s'
    else: 
        scale = 250
        U = 5
        label = '5 m/s'
        
    # interpolate data to fit same grid
    if zoom_out:
        ds_out = xr.Dataset(
            {
                "lat": (["lat"], np.arange(1.25, 63, 3)),
                "lon": (["lon"], np.arange(200, 300, 3)),
            }
        )
        
        # patch size for key
        width = 0.13
        height = 0.035
        
    else:
        ds_out = xr.Dataset(
            {
                "lat": (["lat"], np.arange(15.625, 51.88, 2.75)),
                "lon": (["lon"], np.arange(216.5625, 295.275, 2.75)),
            }
        )
        
        # patch size for key
        width = 0.1
        height = 0.035
    
    regridder_u = xe.Regridder(u, ds_out, 'bilinear')
    regridder_v = xe.Regridder(v, ds_out, 'bilinear')
    u = regridder_u(u)
    v = regridder_v(v)

    # allow to skip values
    lat = u['lat'][::step]
    lon = u['lon'][::step]
    X, Y = np.meshgrid(lon, lat)
    uu = np.array(u[::step, ::step])
    vv = np.array(v[::step, ::step])
    
    # setup quiver
    quiv = ax.quiver(X, Y, uu, vv,
                pivot = 'tail',
                width = 0.0015,
                scale = scale, 
                headwidth = 6,
                color = 'k',
                transform = ccrs.PlateCarree())
    
    
    bbox = FancyBboxPatch((0.03, 0.04), width, height,
                      transform=ax.transAxes,
                      fc='white', ec='black', boxstyle='round,pad=0.02', zorder=1)
    
    ax.add_patch(bbox)
    
    key = ax.quiverkey(quiv, 
                       X = 0.05, 
                       Y = 0.05, 
                       U = U, 
                       label = label, 
                       labelpos = 'E',
                       fontproperties = {'size' : 20})
        
    return quiv, key


def map_anomalies(anomaly_ref, model_name, variable, start_month, stop_month, level = None, start_year = 1979, stop_year = 2014, add_quiver = None, u = 'uas', v = 'vas', save = False, zoom_out = False):
    
    """
    Maps xarray.DataArray from specified function. Can use contourfill to visualize a 
    single variable and also overlay wind vectors (quiver). Mapping dictionary contains
    data for each variable to set associated titles, colors, and standardization of the 
    scale for the color bar. 
    
    Note that the level (plev) is selected in Pa not hPa so 500 hPa = 50000.
    """
    
    # specified what function to use and calls it to get xarray.DataArray
    if zoom_out:
        shrink = 0.6
        if anomaly_ref.__name__ == 'anomaly':
            save_name = f'/ZOOOMED_{variable}_{anomaly_ref.__name__}_{start_month}-{stop_month}_{model_name}.png'
            data = anomaly_ref(model_name, variable, start_month, stop_month, level, zoom_out = True)
        else:
            save_name = f'/ZOOOMED_{variable}_{anomaly_ref.__name__}_{start_month}-{stop_month}_{start_year}-{stop_year}_{model_name}.png'
            data = anomaly_ref(model_name, variable, start_month, stop_month, level, start_year, stop_year, zoom_out = True)
        
    else:
        shrink = 0.85
        if anomaly_ref.__name__ == 'anomaly':
            save_name = f'/{variable}_{anomaly_ref.__name__}_{start_month}-{stop_month}_{model_name}.png'
            data = anomaly_ref(model_name, variable, start_month, stop_month, level)
        else:
            save_name = f'/{variable}_{anomaly_ref.__name__}_{start_month}-{stop_month}_{start_year}-{stop_year}_{model_name}.png'
            data = anomaly_ref(model_name, variable, start_month, stop_month, level, start_year, stop_year)
        
    # setup map
    fig = plt.figure()
    ax = plt.axes(projection  = ccrs.PlateCarree())
    
    # set the color transition to happen at 0
    variable_min = variable_dict[variable][anomaly_ref.__name__]['min']
    variable_max = variable_dict[variable][anomaly_ref.__name__]['max']
    ticks = np.linspace(variable_min, variable_max, num = 9)

    # defualts norm if 0 can't be at the center
    if variable_min < 0.00 < variable_max:
        norm = mcolors.TwoSlopeNorm(vmin = variable_min, vcenter = 0.00, vmax = variable_max)
    else:
        norm = mcolors.Normalize(vmin = variable_min, vmax = variable_max)

    # create outline of map based on mean values or anomalies
    contour = ax.contourf(data['lon'], data['lat'], data.values, cmap = variable_dict[variable][anomaly_ref.__name__]['cmap'], transform = ccrs.PlateCarree(), levels = 20, norm = norm)
    
    # create a scalar mappable as a standin for contour so the colorbar remains standardized across different maps
    sm = mpl.cm.ScalarMappable(norm = norm, cmap = variable_dict[variable][anomaly_ref.__name__]['cmap'])
    sm.set_array([]) # makes sure no data is attached to the colorbar
    
    # specify the layout of the colorbar
    cbar = plt.colorbar(sm, ax = ax, orientation = 'horizontal', pad = 0.03, aspect = 50, shrink = shrink, extend = 'both', ticks = ticks)
    cbar.set_label(variable_dict[variable][anomaly_ref.__name__]['cbar'], fontsize = 10)
    
    if variable == 'ts' or variable == 'zg' or variable == 'pr' or variable == 'huss' or variable == 'psl':
        cbar.ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
    else:
        cbar.ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))
        
    if anomaly_ref.__name__ == 'region_mean':
        ax.set_title(f'{model_name} ssp585\nMean {variable_dict[variable][anomaly_ref.__name__]['title']}\n{time_dict[range(start_month, stop_month +1)]} {start_year}-{stop_year}', fontsize = 18)
        
    else:
        ax.set_title(f'{model_name} ssp585\n{variable_dict[variable][anomaly_ref.__name__]['title']} Anomaly\n{time_dict[range(start_month, stop_month +1)]} 2070-2099 vs 1985-2014', fontsize = 18)
        
    if zoom_out:
        ax.set_ylim(1.25, 63)
        ax.set_xlim(-157.75, -61.5)
    else:
        ax.set_ylim(20, 51.25)
        ax.set_xlim(-143, -67.5)
    
    # add features to the map
    ax.coastlines(linewidth=0.5,color = 'k')
    # ax.add_feature(cfeature.LAND, color=land_color,zorder=2)
    states = cfeature.NaturalEarthFeature(category = 'cultural', name = 'admin_1_states_provinces_lines', scale = '50m', facecolor = 'none', edgecolor = 'k')
    ax.add_feature(states, linewidth = 0.5)
    countries = cfeature.NaturalEarthFeature(category = 'cultural', name = 'admin_0_boundary_lines_land', scale = '50m', facecolor = 'none', edgecolor = 'k')
    ax.add_feature(countries, linewidth = 0.5)
    # ax.add_feature(cfeature.LAKES, zorder = 1)
    # ax.add_feature(cfeature.RIVERS)
    
    # add arrows to show wind vectors
    if add_quiver:
        quiver_obj, quiver_key = quiver(u, v, ax, anomaly_ref, model_name, start_month, stop_month, level, start_year, stop_year, zoom_out, step = 1)
            
    # save path for files
    if save:
        # all PNGs stored to anomaly_maps directory but ignored in Git
        save_path = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/anomaly_maps/{model_name}/'
        
        # refers to time_dict for the naming files based on the given months
        save_path = os.path.join(save_path, time_dict[range(start_month, stop_month +1)] + save_name)
        plt.savefig(save_path, dpi = 400)
        
    plt.show()   
    
    return fig, ax

test = map_anomalies(anomaly, models[2], 'ts', 6, 8)

# for variable in variables:
#     for model in models:
#         map_anomalies(region_mean, model, variable, 9, 9, start_year = 1979, stop_year = 2014, save = True)
#         map_anomalies(region_mean, model, variable, 9, 9, start_year = 2070, stop_year = 2099, save = True)
#         map_anomalies(anomaly, model, variable, 9, 9, save = True)

# for variable in H_variables:
#     for model in models:
#         map_anomalies(region_mean, model, variable, 9, 9, level = 50000, start_year = 1979, stop_year = 2014, save = True)
#         map_anomalies(region_mean, model, variable, 9, 9, level = 50000, start_year = 2070, stop_year = 2099, save = True)
#         map_anomalies(anomaly, model, variable, 9, 9, level = 50000, save = True)
        