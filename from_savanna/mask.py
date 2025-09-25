#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  9 12:36:24 2025

@author: u1301408
"""

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/packages')
import base_packages as bp

# APPLY MASK TO GCM DATA
fGCM = '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/ERA5/pr/pr_Amon_ACCESS-CM2_historical_r1i1p1f1_gn_19500116-20141216.nc'
# decodes time information follownig the Climate and Weather metadata connvention
time_coder = bp.xr.coders.CFDatetimeCoder(use_cftime = True)

# Load in the shape file that contains the boundaries for the GSLB
TOPO_DIR = "/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/gridmet/"
shp  = bp.gpd.read_file(TOPO_DIR + "WBD_16_HU2_Shape/Shape/WBDHU4.shp")
gsl  = shp[shp["huc4"] == "1602"]
br   = shp[shp["huc4"] == "1601"]
gslb = bp.gpd.GeoDataFrame(geometry=[gsl.geometry.unary_union.union(br.geometry.unary_union)], crs=shp.crs)
# gslb = gslb.to_crs("EPSG:4326")

# Then I'll load in the file I want and set its mapping projection
ds = bp.xr.open_dataset(fGCM, engine = "netcdf4", decode_times = time_coder)

# regrid the GCM data to ennsure that at least a few gridpoints land within the mask boundaries
ds_regrid = bp.xr.Dataset(
        {
            "lat": (["lat"], bp.np.arange(36, 43, 1)),
            "lon": (["lon"], bp.np.arange(245, 251, 1)), #115, 109
        }
    )

regridder = bp.xe.Regridder(ds, ds_regrid, 'bilinear')
ds_regridded = regridder(ds)

# redefine longitude values to be -180 to 180 not 0 to 360
ds_regridded.coords['lon'] = ((ds_regridded.coords['lon'] + 180) % 360) - 180
ds_regridded = ds_regridded.sortby('lon')

# sets data to known grid that matches the mask
ds = ds_regridded.rio.write_crs("EPSG:4326")

# note that GCM data required that the variable you wish to look at is specified
ds = ds['pr'].rio.set_spatial_dims(x_dim = 'lon', y_dim = 'lat', inplace = False)

# clis out the GSLB (everything outside the mask returns NAN)
ds = ds.rio.clip(gslb.geometry.apply(bp.mapping), gslb.crs, drop=False)

#%%
import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/packages')
import base_packages as bp

# APPLY MASK TO MACA DATA
fGCM = '/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/output/netcdf/macav2metdata_GSLBIP_ACCESS-ESM1-5_ssp126_pr.nc'
# decodes time information follownig the Climate and Weather metadata connvention
time_coder = bp.xr.coders.CFDatetimeCoder(use_cftime = True)

# Load in the shape file that contains the boundaries for the GSLB
TOPO_DIR = "/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/gridmet/"
shp  = bp.gpd.read_file(TOPO_DIR + "WBD_16_HU2_Shape/Shape/WBDHU4.shp")
gsl  = shp[shp["huc4"] == "1602"]
br   = shp[shp["huc4"] == "1601"]
gslb = bp.gpd.GeoDataFrame(geometry=[gsl.geometry.unary_union.union(br.geometry.unary_union)], crs=shp.crs)

# Loads in the MACA file I want and set its mapping projection
ds = bp.xr.open_dataset(fGCM, engine = "netcdf4", decode_times = time_coder)
ds = ds.rio.write_crs("EPSG:4326")

# Clips out the GSLB
ds = ds.rio.clip(gslb.geometry.apply(bp.mapping), gslb.crs, drop=False)

