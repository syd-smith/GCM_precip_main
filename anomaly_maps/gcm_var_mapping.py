#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 13:05:53 2025

@author: u1301408
"""
import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/packages')
import base_packages as bp

# Define the shapefile path (where to find coordinates used by VIC from Maribeth at USBR)
bdir = '/uufs/chpc.utah.edu/common/home/u0660911/Documents/projects/gslbip/'
shapefile_path = bp.os.path.join(bdir,'GSLBIP_shpfiles/MF6_VIC_bounding_box/MF6_VIC_bounding_box.shp')

# Load the shapefile for VIC boundaries of Great Salt Lake Basin (not applied for larger maps)
gdf = bp.gpd.read_file(shapefile_path)
gdf = gdf.to_crs("EPSG:4326")
min_lon, min_lat, max_lon, max_lat = gdf.total_bounds

# output of values in VIC shapefile
# min_lon = -113.69354024533703
# max_lon = -110.59375
# min_lat = 39.553038338687124
# max_lat = 42.84375

# GCM lon values are in 0-360 format while other datasets use -180-180 -> conversion may be needed
def convert_lon_to_0_360(lon):
    # Convert longitude from -180-180 to 0-360
    lon = bp.np.array(lon)
    lon_360 = (lon + 360) % 360
    return lon_360

def convert_lon_360_to_180(lon):
    # Convert longitude from 0360 range to -180 to 180 range
    lon = bp.np.array(lon)  # Ensures input works for lists or arrays
    lon_180 = ((lon + 180) % 360) - 180
    return lon_180

# wet models from the scatter plot (high precip ratio)
H_models = ['UKESM1-0-LL', 'ACCESS-CM2', 'CanESM5', 'KACE-1-0-G']

# dry models (low precip ratio)
L_models = ['MPI-ESM1-2-LR', 'CNRM-ESM2-1', 'CNRM-CM6-1-HR', 'INM-CM4-8']

# function to calculate the mean for each gridpoint across the historical period (1979-2014)
def hist_mean(model_name, variable, time): 
    fpath = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/intake_esgf/ERA5/{variable}/{variable}_Amon_'
    open_hist = bp.xr.open_mfdataset(fpath + model_name + '_hist*.nc', engine = 'netcdf4')
    
    # geopotential height has an extra dimension for what pressure level you want to look at (we chose 500 hPa)
    if variable == 'zg':
        open_hist = open_hist.sel(plev = 50000, method = 'nearest')
    
    years_hist = range(1985, 2015)
    location_hist = open_hist[variable].sel(lat = slice(15, 53), lon = slice(215, 295))
    JJA_hist = location_hist.sel(time = location_hist.time.dt.month.isin([6, 7, 8]))
    means_hist = []
    for year in years_hist:
        year_hist = JJA_hist.sel(time = JJA_hist.time.dt.year == year)
        
        # GCM pr data is in precipitation flux so the time unit has to be taken out
        if variable == 'pr':
            days_in_month = year_hist.time.dt.days_in_month
            seconds_per_month = days_in_month * 24 * 60 * 60
            mean_hist = (year_hist * seconds_per_month).mean(dim = 'time')
        else:
            mean_hist = year_hist.mean(dim = 'time')
            
        means_hist.append(mean_hist)        
    combine_means_hist = bp.xr.concat(means_hist, dim = 'year')
    overall_mean_hist = combine_means_hist.mean(dim = 'year')
    
    if variable == 'psl':
        overall_mean_hist = overall_mean_hist * 0.01 # convert from Pa to hPa
    else:
        overall_mean_hist = overall_mean_hist

    return overall_mean_hist

# function to calculate the mean for each gridpoint across the future period (2070-2099)
# probably should be combined with hist_mean
def fut_mean(model_name, variable, interpolate = False):
    fpath = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/intake_esgf/ERA5/{variable}/{variable}_Amon_'
    open_fut = bp.xr.open_mfdataset(fpath + model_name + '_ssp*.nc', engine = 'netcdf4')

    # geopotential height has an extra dimension for what pressure level you want to look at (we chose 500 hPa)
    if variable == 'zg':
        open_fut = open_fut.sel(plev = 50000, method = 'nearest')
        
    years_fut = range(2070, 2100)
    location_fut = open_fut[variable].sel(lat = slice(15, 53), lon = slice(215, 295))
    JJA_fut = location_fut.sel(time = location_fut.time.dt.month.isin([6, 7, 8]))
    means_fut = []
    for year in years_fut:
        year_fut = JJA_fut.sel(time = JJA_fut.time.dt.year == year)
        
        # GCM pr data is in precipitation flux so the time unit has to be taken out
        if variable == 'pr':
            days_in_month = year_fut.time.dt.days_in_month
            seconds_per_month = days_in_month * 24 * 60 * 60
            mean_fut = (year_fut * seconds_per_month).mean(dim = 'time')
        else:
            mean_fut = year_fut.mean(dim = 'time')
            
        means_fut.append(mean_fut)
    combine_means_fut = bp.xr.concat(means_fut, dim = 'year')
    overall_mean_fut = combine_means_fut.mean(dim = 'year')
    
    if variable == 'psl':
        overall_mean_fut = overall_mean_fut * 0.01 # convert from Pa to hPa
    else:
        overall_mean_fut = overall_mean_fut

    return overall_mean_fut

# function to calculate the change in a variable from 1979-2014 to 2070-2099 as a difference (precipitation is calculated as a percent change)
def anomaly(model_name, variable):
    fpath = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/intake_esgf/ERA5/{variable}/{variable}_Amon_'
    # open both datasets for future and historical periods
    open_hist = bp.xr.open_mfdataset(fpath + model_name + '_hist*.nc', engine = 'netcdf4')
    open_fut = bp.xr.open_mfdataset(fpath + model_name + '_ssp*.nc', engine = 'netcdf4')
    
    # geopotential height has an extra dimension for what pressure level you want to look at (we chose 500 hPa)
    if variable == 'zg':
        open_hist = open_hist.sel(plev = 50000, method = 'nearest')
        open_fut = open_fut.sel(plev = 50000, method = 'nearest')
        
    years_hist = range(1985, 2015)
    location_hist = open_hist[variable].sel(lat = slice(15.5, 53), lon = slice(215, 294))
    JJA_hist = location_hist.sel(time = location_hist.time.dt.month.isin([6, 7, 8]))
    means_hist = []
    for year in years_hist:
        year_hist = JJA_hist.sel(time = JJA_hist.time.dt.year == year)
        mean_hist = year_hist.mean(dim = 'time')
        means_hist.append(mean_hist)        
    combine_means_hist = bp.xr.concat(means_hist, dim = 'year')
    overall_mean_hist = combine_means_hist.mean(dim = 'year')

    years_fut = range(2070, 2100)
    location_fut = open_fut[variable].sel(lat = slice(15, 53), lon = slice(215, 295))
    JJA_fut = location_fut.sel(time = location_fut.time.dt.month.isin([6, 7, 8]))
    means_fut = []
    for year in years_fut:
        year_fut = JJA_fut.sel(time = JJA_fut.time.dt.year == year)
        mean_fut = year_fut.mean(dim = 'time', skipna = True)
        means_fut.append(mean_fut)
    combine_means_fut = bp.xr.concat(means_fut, dim = 'year')
    overall_mean_fut = combine_means_fut.mean(dim = 'year')
   
    if variable == 'pr':
        anomaly = ((overall_mean_fut - overall_mean_hist) / overall_mean_hist) * 100
    else:
        anomaly = overall_mean_fut - overall_mean_hist

    return anomaly

# examples of the anomaly function being used to return a lat and lon xarray.DataArray for the specified variable
# vas = anomaly('ACCESS-CM2', 'vas')
# uas = anomaly('ACCESS-CM2', 'uas')
# psl = anomaly('ACCESS-CM2', 'psl')
# pr = anomaly('ACCESS-CM2', 'pr')


# maps xarray.DataArray from one of the above functions 
def map_anomalies(anomaly_ref, model_name, variable, interpolate = False, quiver = False, step = 1):
    # specified what function to use and calls it to get xarray.DataArray
    data = anomaly_ref(model_name, variable)
    
    # defines a dictionary that stores formatting information for each variable -> see else: for more information
    if variable == 'psl': 
        plot_dict = {'cmap_a' : bp.cmap.cmap('MPL_coolwarm'),
                     'cmap_m' : bp.cmap.cmap('MPL_coolwarm'),
                     'title': 'Sea Level Pressure', 
                     'cbar_a' : 'Change in Sea Level Pressure (hPa)',
                     'cbar_m' : 'Mean Sea Level Pressure (hPa)'
                     }
    elif variable == 'pr':
        plot_dict = {'cmap_a' : bp.cmap.cmap('MPL_BrBG'),
                     'cmap_m' : bp.cmap.cmap('MPL_BrBG'),
                     'title': 'Precipitation',
                     'cbar_a' : 'Change in Precipitation (%)',
                     'cbar_m' : 'Mean Precipitation (mm)'
                     }
    elif variable == 'zg':
        plot_dict = {'cmap_a' : bp.cmap.cmap('MPL_coolwarm'),
                     'cmap_m' : bp.cmap.cmap('MPL_coolwarm'),
                     'title': 'Geopotential Height',
                     'cbar_a' : 'Change in 500-hPa Geopotential Height (m)',
                     'cbar_m' : 'Mean 500-hPa Geopotential Height (m)'
                     }
    elif variable == 'vas':
        plot_dict = {'cmap_a' : bp.cmap.cmap('CBR_wet'),
                     'cmap_m' : bp.cmap.cmap('MPL_coolwarm'),
                     'title': 'Northward Near Surface Wind',
                     'cbar_a' : 'Change in Northward Near Surface Wind (m s\u207B\u00B9)', # m s^-1
                     'cbar_m' : 'Mean Northward Near Surface Wind (m s\u207B\u00B9)' # m s^-1
                     }
    elif variable == 'uas':
        plot_dict = {'cmap_a' : bp.cmap.cmap('CBR_wet'),
                     'cmap_m' : bp.cmap.cmap('MPL_coolwarm'),
                     'title': 'Easthward Near Surface Wind',
                     'cbar_a' : 'Change in Eastward Near Surface Wind (m s\u207B\u00B9)', # m s^-1
                     'cbar_m' : 'Mean Eastward Near Surface Wind (m s\u207B\u00B9)' # m s^-1
                     }
        
    # format and function of dictionary explained
    else:
        plot_dict = {'cmap_a' : 'color map for anomaly',
                     'cmap_m' : 'color map for hist/fut means',
                     'title': 'Test Map Title',
                     'cbar_a' : 'Default Measurement for anomaly colorbar',
                     'cbar_m' : 'Default Measurement for hist/fut mean colorbar'
                     }
        
    #setup map
    fig = bp.plt.figure()
    ax = bp.plt.axes(projection  = bp.ccrs.PlateCarree())
    
    # set the color transition to happen at 0
    data_min = data.values.min()
    data_max = data.values.max()

    # defualts norm if 0 can't be at the center
    if data_min < 0.00 < data_max:
        norm = bp.mcolors.TwoSlopeNorm(vmin=data_min, vcenter=0.00, vmax=data_max)
    else:
        norm = bp.mcolors.Normalize(vmin=data_min, vmax=data_max)

    # create outline of map based on mean values or anomalies
    if anomaly_ref.__name__ == 'fut_mean':
        contour = ax.contourf(data['lon'], data['lat'], data.values, cmap = plot_dict['cmap_m'], transform = bp.ccrs.PlateCarree(), levels = 20, norm = norm)
        ax.set_title(f'{model_name} ssp585\nMean {plot_dict['title']}\n2070-2099', fontsize = 18)
        cbar = bp.plt.colorbar(contour, orientation = 'horizontal', pad = 0.03, aspect = 50, shrink = 0.85)
        cbar.set_label(plot_dict['cbar'], fontsize = 10)
    elif anomaly_ref.__name__ == 'hist_mean':
        contour = ax.contourf(data['lon'], data['lat'], data.values, cmap = plot_dict['cmap_m'], transform = bp.ccrs.PlateCarree(), levels = 20, norm = norm)
        ax.set_title(f'{model_name}\nMean {plot_dict['title']}\n1985-2014', fontsize = 18)
        cbar = bp.plt.colorbar(contour, orientation = 'horizontal', pad = 0.03, aspect = 50, shrink = 0.85)
        cbar.set_label(plot_dict['cbar'], fontsize = 10)
    else:
        contour = ax.contourf(data['lon'], data['lat'], data.values, cmap = plot_dict['cmap_a'], transform = bp.ccrs.PlateCarree(), levels = 20, norm = norm)
        ax.set_title(f'{model_name} ssp585\n{plot_dict['title']} Anomaly\n2070-2099 vs 1985-2014', fontsize = 18)
        cbar = bp.plt.colorbar(contour, orientation = 'horizontal', pad = 0.03, aspect = 50, shrink = 0.85)
        if variable == 'vas' or variable == 'uas':
            cbar.set_label('m s-1', fontsize = 10)
        else:
            cbar.set_label('% Change', fontsize = 10)
        cbar.ax.xaxis.set_major_formatter(bp.ticker.FormatStrFormatter('%.2f'))
    ax.set_ylim(20, 51.25)
    ax.set_xlim(-143, -67.5)
    
    # add features to the map
    ax.coastlines(linewidth=0.5,color = 'k')
    # ax.add_feature(bp.cfeature.LAND, color=land_color,zorder=2)
    states = bp.cfeature.NaturalEarthFeature(category = 'cultural', name = 'admin_1_states_provinces_lines', scale = '50m', facecolor = 'none', edgecolor = 'k')
    ax.add_feature(states, linewidth = 0.5)
    countries = bp.cfeature.NaturalEarthFeature(category = 'cultural', name = 'admin_0_boundary_lines_land', scale = '50m', facecolor = 'none', edgecolor = 'k')
    ax.add_feature(countries, linewidth = 0.5)
    # ax.add_feature(bp.cfeature.LAKES, zorder = 1)
    # ax.add_feature(bp.cfeature.RIVERS)
    
    # add quiver to overlay wind vectors on another variable
    save_name = model_name + '.png'
    if quiver == True:
        #activate my_quiver function
        save_name = model_name + '_quiver.png'
        
        # slice uas and vas data
        u = anomaly_ref(model_name, 'uas')
        v = anomaly_ref(model_name, 'vas')
        
        # set scale to adjust based on being an anomaly or fut/hist mean
        if anomaly_ref.__name__ == 'anomaly':
            scale = 20
        else: 
            scale = 175
        
        # interpolate data to fit same grid if needed
        if interpolate == True:
            ds_out = bp.xr.Dataset(
                {
                    "lat": (["lat"], bp.np.arange(15.625, 51.88, 2.75)),
                    "lon": (["lon"], bp.np.arange(216.5625, 295.275, 2.75)),
                }
            )

            regridder_u = bp.xe.Regridder(u, ds_out, 'bilinear')
            regridder_v = bp.xe.Regridder(v, ds_out, 'bilinear')
            u = regridder_u(u)
            v = regridder_v(v)
       
        # allow to skip values
        lat = u['lat'][::step]
        lon = u['lon'][::step]
        X, Y = bp.np.meshgrid(lon, lat)
        uu = bp.np.array(u[::step,::step])
        vv = bp.np.array(v[::step,::step])
        
        # setup quiver
        quiv = ax.quiver(X, Y, uu, vv,
                    pivot = 'tail',
                    width = 0.0015,
                    scale = scale, 
                    headwidth = 6,
                    color = 'k',
                    transform = bp.ccrs.PlateCarree())
    
    # save path for files
    # all PNGs stored to anomaly_maps directory but ignored in Git
    save_path = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/intake_esgf/anomaly_maps/{variable}_maps/{variable}_'
    if anomaly_ref.__name__ == 'fut_mean':
        save_path = save_path  + 'fut/'
    elif anomaly_ref.__name__ == 'hist_mean':
        save_path = save_path  + 'hist/'
    else:
        save_path = save_path  + 'anom/'
    if model_name in H_models:
        save_path = bp.os.path.join(save_path + 'H_models', save_name)
    elif model_name in L_models:
        save_path = bp.os.path.join(save_path + 'L_models', save_name)
    else:
        save_path  = bp.os.path.join(save_path, save_name)
    
    bp.plt.savefig(save_path, dpi = 400)
    bp.plt.show()   
    
    return fig, ax

    
# loop over multiple models for one variable
for model in L_models:
    map_anomalies(hist_mean, model, 'zg')
    bp.plt.show()

# run one test model for one variable
# test = map_anomalies(fut_mean, 'KACE-1-0-G', 'zg') 
    
# complete list of models analyzed
# models = ['UKESM1-0-LL', 'ACCESS-CM2', 'CanESM5', 'KACE-1-0-G', 'MPI-ESM1-2-LR', 'CNRM-ESM2-1', 'CNRM-CM6-1-HR', 'INM-CM4-8']
