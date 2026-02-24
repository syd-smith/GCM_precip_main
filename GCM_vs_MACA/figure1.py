#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 17 08:17:43 2025

@author: u1301408
"""

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import geopandas as gpd
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import sys
import xarray as xr

sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/tool_belt/')
from lon_conversion import convert_lon_to_0_360

sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/from_savanna/')
import nclcmaps as cmap


# Load in the shape file that contains the new boundaries for the GSLB
TOPO_DIR = "/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/gridmet/"
shp  = gpd.read_file(TOPO_DIR + "WBD_16_HU2_Shape/Shape/WBDHU4.shp")
gsl  = shp[shp["huc4"] == "1602"]
br   = shp[shp["huc4"] == "1601"]
gslb = gpd.GeoDataFrame(geometry=[gsl.geometry.unary_union.union(br.geometry.unary_union)], crs=shp.crs)


# open MACA dataset and pullout sum of monthly values for JJA to get JJA averages for season as input for pcolormesh
MACA_fpath = '/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/output/netcdf/macav2metdata_GSLBIP_KACE-1-0-G_ssp585_pr.nc'
MACA_open = xr.open_dataset(MACA_fpath)

# mean calculation for MACA using same method as GCM data
MACA_data = []
for year in range(1979, 2015):
    # Select all JJA months for this year
    MACA_dat = MACA_open['pr'].sel(time=(MACA_open.time.dt.month.isin([6, 7, 8])) & (MACA_open.time.dt.year == year), drop=True)
    MACA_summer_precip = MACA_dat.mean(dim = 'time')
    MACA_data.append(MACA_summer_precip)

MACA_combine = xr.concat(MACA_data, dim = 'year')

# calculates daily mean so have to *30 for days in month to get monthly mean
MACA_mean = MACA_combine.mean(skipna = True, dim = 'year') * 30


# open GCM dataset and take mean of summer months
GCM_fpath = '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/ERA5/pr/pr_Amon_KACE-1-0-G_historical_r1i1p1f1_gr_19500116-20141216.nc'
GCM_open = xr.open_dataset(GCM_fpath)

# GCM data is pr flux -> needs conversion
GCM_boundary = GCM_open['pr'].sel(lat = slice(35.5, 43.5), lon = slice(convert_lon_to_0_360(-116), convert_lon_to_0_360(-107)))

GCM_data = []
for year in range(1979, 2015):
    # Select all JJA months for this year
    GCM_dat = GCM_boundary.sel(time=(GCM_boundary.time.dt.month.isin([6, 7, 8])) & (GCM_boundary.time.dt.year == year), drop=True)

    days_in_month = GCM_dat.time.dt.days_in_month
    seconds_per_month = days_in_month * 24 * 60 * 60
    summer_precip = (GCM_dat * seconds_per_month).mean(dim = 'time')
    
    GCM_data.append(summer_precip)

combine = xr.concat(GCM_data, dim = 'year')
GCM_mean = combine.mean(skipna = True, dim = 'year')


# setup pcolormesh
fig, axs = plt.subplots(1, 2, figsize = (7, 4), subplot_kw = {'projection' : ccrs.PlateCarree()}, constrained_layout = True)

# define levels for both maps
GCM_levels = np.linspace(0, 30, 8)
MACA_levels = np.linspace(0, 85, 8)

# define norms for both maps
GCM_norm = mcolors.BoundaryNorm(GCM_levels, ncolors = plt.get_cmap(cmap.cmap('MPL_GnBu'), 7).N) # 15 bins means 14 edges
MACA_norm = mcolors.BoundaryNorm(MACA_levels, ncolors = plt.get_cmap(cmap.cmap('MPL_GnBu'), 7).N)

# setup first map with GCM_mean data
m1 = axs[0].pcolormesh(GCM_mean['lon'].values, GCM_mean['lat'].values, GCM_mean.values, norm = GCM_norm, cmap = cmap.cmap('MPL_GnBu'))
axs[0].set_ylim(36.5, 43)
axs[0].set_xlim(-115, -108.5)
GCM_cbar = fig.colorbar(m1, ax = axs[0], orientation = 'horizontal', label = 'mm month\u207B\u00B9', shrink = 0.65, ticks = GCM_levels, boundaries = GCM_levels)
GCM_cbar.ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))

# setup second map with MACA_mean data
m2 = axs[1].pcolormesh(MACA_mean['lon'].values, MACA_mean['lat'].values, MACA_mean.values, norm = MACA_norm, cmap = cmap.cmap('MPL_GnBu'))
axs[1].set_ylim(36.5, 43)
axs[1].set_xlim(-115, -108.5)
MACA_cbar = fig.colorbar(m2, ax = axs[1], orientation = 'horizontal', label = 'mm month\u207B\u00B9', shrink = 0.65, ticks = MACA_levels, boundaries = MACA_levels)
MACA_cbar.ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))

labels = ['a.', 'b.']
for ax, label in zip(axs, labels):
    ax.text(0.01, 0.01, label,
            transform = ax.transAxes,
            fontsize = 14,
            va = 'bottom', ha = 'left')
    
    # add features to the map
    states = cfeature.NaturalEarthFeature(category = 'cultural', name = 'admin_1_states_provinces_lines', scale = '50m', facecolor = 'none', edgecolor = 'k', zorder = 4)
    ax.add_feature(states, linewidth = 1.3)
    ax.add_feature(cfeature.LAKES, zorder = 2, linewidth = 1)
    ax.add_feature(cfeature.RIVERS, linewidth = 1, zorder = 1)
    
    # add GSLB boundaries to map
    gslb.boundary.plot(ax = ax, color = 'red', linewidth = 3)

# set save path for image
# save_path = '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSLBIP/GCM_vs_MACA/'
# bp.plt.savefig(save_path + 'figure_1.png', dpi = 400)

plt.show()




