#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 21 12:57:27 2025

@author: u1301408
"""

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/packages')
import base_packages as bp

# dimensions for MACA region
# lat      (lat) float32 672B 36.03 36.07 36.11 36.15 ... 42.9 42.94 42.98
# * lon      (lon) float32 684B -115.1 -115.1 -115.0 ... -108.1 -108.1 -108.0

#%%
def avg_hist_gcm(file_path):
   # min and max latitudes and longitudes
   lat_min, lat_max = 36.03, 42.98
   lon_min, lon_max = -115.1, -108.0
    
   # Load the .mat file
   mat_contents = bp.scipy.io.loadmat(file_path)  

   # Print the contents of the .mat file
   print("Contents of the .mat file:")

   for key, value in mat_contents.items():
        if not key.startswith('__'):  # Skip metadata entries
            print(f"{key}")

   var = mat_contents['interpolated_data']  # Adjust 'pr' to the actual variable name in your .mat file
   lat = bp.np.squeeze(mat_contents['lat'])
   lon = bp.np.squeeze(mat_contents['lon'])
   
   lat_mask = (lat >= lat_min) & (lat <= lat_max)
   lon_mask = (lon >= lon_min) & (lon <= lon_max)

   var_bar = bp.np.nanmean(var, axis = (2,3))  # average over years
   
   trimmed_var_bar = var_bar[bp.np.ix_(lat_mask, lon_mask)]
   trimmed_lat = lat[lat_mask]
   trimmed_lon = lon[lon_mask]

   print(var.shape)
   print(len(lat))
   print(len(lon))

   # so data are lat x lon x doy x year
   
   return trimmed_var_bar, trimmed_lat, trimmed_lon

#%%
file_path = '/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/coarse_grid/ACCESS-CM2_historical_pr.mat'

pr_bar, lat, lon = avg_hist_gcm(file_path)

#%%
# Create a figure and axis with PlateCarree projection
fig, ax = bp.plt.subplots(subplot_kw={"projection": bp.ccrs.PlateCarree()})

# Plot the pr_bar data as a heatmap
mesh = ax.pcolormesh(lon, lat, pr_bar, transform = bp.ccrs.PlateCarree(), cmap="viridis")

# Add a colorbar
cbar = bp.plt.colorbar(mesh, ax = ax, orientation = "vertical", shrink = 0.7, pad = 0.05)

# Add US state boundaries
ax.add_feature(bp.cfeature.STATES, edgecolor = "black", linewidth = 0.5)

# Set map extent (optional, adjust as needed)
ax.set_extent([-130, -60, 20, 55], crs = bp.ccrs.PlateCarree())

# Add gridlines and remove labels from the top and right
gridlines = ax.gridlines(draw_labels = True, dms = True, x_inline = False, y_inline = False, color = "gray", alpha = 0.5, linestyle = "--")
gridlines.top_labels = False  # Disable labels on the top
gridlines.right_labels = False  # Disable labels on the right

# Show the plot
bp.plt.show()
