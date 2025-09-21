#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 17 08:17:43 2025

@author: u1301408
"""

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/packages/')
import base_packages as bp

# set boundaries to run as old or new
old_boundary = True
if old_boundary == True:
    save_name = 'study_region_OLD.png'
else: 
    save_name = 'study_region.png'

# OLD BOUNDARY
# Define the shapefile path (where to find coordinates used by VIC from Maribeth)
bdir = '/uufs/chpc.utah.edu/common/home/u0660911/Documents/projects/gslbip/'
shapefile_path = bp.os.path.join(bdir,'GSLBIP_shpfiles/MF6_VIC_bounding_box/MF6_VIC_bounding_box.shp')

# VIC boundary coordinates to overlay red box on map to show study region
gdf = bp.gpd.read_file(shapefile_path)
gdf = gdf.to_crs("EPSG:4326")
min_lon, min_lat, max_lon, max_lat = gdf.total_bounds 

# Load in the shape file that contains the new boundaries for the GSLB
TOPO_DIR = "/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/gridmet/"
gslb = bp.gpd.read_file(TOPO_DIR + "WBD_16_HU2_Shape/Shape/WBDHU4.shp")
gslb = gslb[gslb["huc4"] == "1602"]

def convert_lon_to_0_360(lon):
    # Convert longitude from -180-180 to 0-360
    lon = bp.np.array(lon)
    lon_360 = (lon + 360) % 360
    return lon_360

#open MACA dataset and pullout sum of monthly values for JJA to get JJA averages for season as input for pcolormesh
MACA_fpath = '/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/output/netcdf/macav2metdata_GSLBIP_KACE-1-0-G_ssp585_pr.nc'
MACA_open = bp.xr.open_dataset(MACA_fpath)

# old mean calculation
# years = []
# for year in range(1979, 2015):
#     months = []
#     for month in range(6, 9):
#         data = MACA_open['pr'].sel(time = (MACA_open.time.dt.month == month) & (MACA_open.time.dt.year == year))
#         data_mean = data.mean(dim = 'time', skipna = True)
#         months.append(data_mean)
#     combine_months = bp.xr.concat(months, dim = 'month')
#     average_month = combine_months.mean(skipna = True, dim = 'month')
#     years.append(average_month)
    
# combine_year = bp.xr.concat(years, dim = 'year')
# # multiply by days of month to get monthly average
# MACA_mean = combine_year.mean(skipna = True, dim = 'year') * 30

# mean calculation using same method as GCM data
MACA_data = []
for year in range(1979, 2015):
    # Select all JJA months for this year
    # check if this is monthly average
    MACA_dat = MACA_open['pr'].sel(time=(MACA_open.time.dt.month.isin([6, 7, 8])) & (MACA_open.time.dt.year == year), drop=True)
    MACA_summer_precip = MACA_dat.mean(dim = 'time')

    MACA_data.append(MACA_summer_precip)

MACA_combine = bp.xr.concat(MACA_data, dim = 'year')

# calculates daily mean so have to *30 for days in month to get monthly mean
MACA_mean = MACA_combine.mean(skipna = True, dim = 'year') * 30


#open GCM dataset and take mean of summer months
GCM_fpath = '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/ERA5/pr/pr_Amon_KACE-1-0-G_historical_r1i1p1f1_gr_19500116-20141216.nc'
GCM_open = bp.xr.open_dataset(GCM_fpath)

#data still in pr flux -> needs conversion
GCM_boundary = GCM_open['pr'].sel(lat = slice(35.5, 43.5), lon = slice(convert_lon_to_0_360(-116), convert_lon_to_0_360(-107)))

GCM_data = []
for year in range(1979, 2015):
    # Select all JJA months for this year
    GCM_dat = GCM_boundary.sel(time=(GCM_boundary.time.dt.month.isin([6, 7, 8])) & (GCM_boundary.time.dt.year == year), drop=True)

    # currently shows total precip but if /30 then is monthly average?
    days_in_month = GCM_dat.time.dt.days_in_month
    seconds_per_month = days_in_month * 24 * 60 * 60
    # precip_months_avg = 24 * 60 * 60
    summer_precip = (GCM_dat * seconds_per_month).mean(dim = 'time')
    # summer_precip = (GCM_dat * precip_months_avg).mean(dim = 'time')

    GCM_data.append(summer_precip)

combine = bp.xr.concat(GCM_data, dim = 'year')
GCM_mean = combine.mean(skipna = True, dim = 'year')



# setup pcolormesh
fig, axs = bp.plt.subplots(1, 2, figsize = (7, 4), subplot_kw = {'projection' : bp.ccrs.PlateCarree()}, constrained_layout = True)

# setup first map with GCM_mean data
m1 = axs[0].pcolormesh(GCM_mean['lon'].values, GCM_mean['lat'].values, GCM_mean.values, cmap = bp.cmap.cmap('MPL_GnBu'))
axs[0].set_title('GCM Data - Coarse Resolution')
axs[0].set_ylim(36.5, 43)
axs[0].set_xlim(-115, -108.5)
fig.colorbar(m1, ax = axs[0], orientation = 'horizontal', label = 'mm month\u207B\u00B9', shrink = 0.65)

# setup second map with MACA_mean data
m2 = axs[1].pcolormesh(MACA_mean['lon'].values, MACA_mean['lat'].values, MACA_mean.values, cmap = bp.cmap.cmap('MPL_GnBu'))
axs[1].set_title('MACA Data - Fine Resolution')
axs[1].set_ylim(36.5, 43)
axs[1].set_xlim(-115, -108.5)
fig.colorbar(m2, ax = axs[1], orientation = 'horizontal', label = 'mm month\u207B\u00B9', shrink = 0.65)

for ax in axs:
    ax.set_xlabel('lat')
    ax.set_ylabel('lon')
    
    #add features to the map
    states = bp.cfeature.NaturalEarthFeature(category = 'cultural', name = 'admin_1_states_provinces_lines', scale = '50m', facecolor = 'none', edgecolor = 'k', zorder = 4)
    ax.add_feature(states, linewidth = 1.3)
    ax.add_feature(bp.cfeature.LAKES, zorder = 2, linewidth = 1)
    ax.add_feature(bp.cfeature.RIVERS, linewidth = 1, zorder = 1)
    
    #add VIC boundaries
    if old_boundary ==  True:
        box = bp.mpatches.Rectangle((min_lon, min_lat), (max_lon - min_lon), (max_lat - min_lat), linewidth = 2.5, edgecolor = 'red', facecolor = 'none', zorder = 5)
        ax.add_patch(box)
    else:
        gslb.boundary.plot(ax = ax, color = 'red', linewidth = 3)


#set title for entire figure
# fig.suptitle('KACE-1-0-G Mean Precipitation Over Study Region', fontsize = 20)

#set save path for image
save_path = '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/anomaly_maps/location_figs/'
bp.plt.savefig(save_path + save_name, dpi = 400)

bp.plt.show()





