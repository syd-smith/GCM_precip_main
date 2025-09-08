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

# MODELS USED FOR LATEST GROUPING -> HIGH, MODERATE, LOW
# listed in order from highest to lowest
H_models = ['KACE-1-0-G', 'CanESM5', 'UKESM1-0-LL', 'ACCESS-CM2', 'HadGEM3-GC31-LL']
M_models = ['HadGEM3-GC31-MM']
L_models = ['MPI-ESM1-2-LR']
models = ['KACE-1-0-G', 'CanESM5', 'UKESM1-0-LL', 'ACCESS-CM2', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'MPI-ESM1-2-LR']

# MODELS USED FOR INITIAL GROUPING OF HIGH AND LOW
# wet models from monthly_mean_scatter.py (high precip ratio)
# H_models = ['UKESM1-0-LL', 'ACCESS-CM2', 'CanESM5', 'KACE-1-0-G']

# dry models from monthly_mean_scatter.py (low precip ratio)
# L_models = ['MPI-ESM1-2-LR', 'CNRM-ESM2-1', 'CNRM-CM6-1-HR', 'INM-CM4-8']

# function to calculate the mean for each gridpoint across the historical period (1979-2014)
def hist_mean(model_name, variable, start_month, stop_month, zoom_out = False): 
    fpath = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/ERA5/{variable}/{variable}_Amon_'
    open_hist = bp.xr.open_mfdataset(bp.glob.glob(fpath + model_name + '_hist*.nc'))
    
    # geopotential height has an extra dimension for what pressure level you want to look at (we chose 500 hPa)
    if variable == 'zg':
        open_hist = open_hist.sel(plev = 50000, method = 'nearest')
    
    years_hist = range(1985, 2015)
    if zoom_out == True:
        location_hist = open_hist[variable].sel(lat = slice(0, 65), lon = slice(200, 300))
    else: 
        location_hist = open_hist[variable].sel(lat = slice(15, 53), lon = slice(215, 295))
    JJA_hist = location_hist.sel(time = location_hist.time.dt.month.isin(range(start_month, stop_month + 1)))
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
        overall_mean_hist *= 0.01 # convert from Pa to hPa
    elif variable == 'huss':
        overall_mean_hist *= 1000 # convert from kg/kg to g/kg
    # else:
    #     overall_mean_hist = overall_mean_hist

    return overall_mean_hist

# function to calculate the mean for each gridpoint across the future period (2070-2099)
# probably should be combined with hist_mean
def fut_mean(model_name, variable, start_month, stop_month, interpolate = False, zoom_out = False):
    fpath = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/ERA5/{variable}/{variable}_Amon_'
    open_fut = bp.xr.open_mfdataset(bp.glob.glob(fpath + model_name + '_ssp*.nc'))

    # geopotential height has an extra dimension for what pressure level you want to look at (we chose 500 hPa)
    if variable == 'zg':
        open_fut = open_fut.sel(plev = 50000, method = 'nearest')
        
    years_fut = range(2070, 2100)
    if  zoom_out == True:
        location_fut = open_fut[variable].sel(lat = slice(0, 65), lon = slice(200, 300))
    else:
        location_fut = open_fut[variable].sel(lat = slice(15, 53), lon = slice(215, 295))
    JJA_fut = location_fut.sel(time = location_fut.time.dt.month.isin(range(start_month, stop_month + 1)))
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
        overall_mean_fut *= 0.01 # convert from Pa to hPa
    elif variable == 'huss':
        overall_mean_fut *= 1000 # convert from kg/kg to g/kg
    # else:
    #     overall_mean_fut = overall_mean_fut

    return overall_mean_fut

# function to calculate the change in a variable from 1979-2014 to 2070-2099 as a difference (precipitation is calculated as a percent change)
def anomaly(model_name, variable, start_month, stop_month, zoom_out = False):
    fpath = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/ERA5/{variable}/{variable}_Amon_'
    # open both datasets for future and historical periods
    open_hist = bp.xr.open_mfdataset(bp.glob.glob(fpath + model_name + '_hist*.nc'))
    open_fut = bp.xr.open_mfdataset(bp.glob.glob(fpath + model_name + '_ssp*.nc'))
    
    # geopotential height has an extra dimension for what pressure level you want to look at (we chose 500 hPa)
    if variable == 'zg':
        open_hist = open_hist.sel(plev = 50000, method = 'nearest')
        open_fut = open_fut.sel(plev = 50000, method = 'nearest')
        
    years_hist = range(1985, 2015)
    if zoom_out == True:
        location_hist = open_hist[variable].sel(lat = slice(0, 65), lon = slice(200, 300))
    else: 
        location_hist = open_hist[variable].sel(lat = slice(15, 53), lon = slice(215, 295))
    JJA_hist = location_hist.sel(time = location_hist.time.dt.month.isin(range(start_month, stop_month + 1)))
    means_hist = []
    for year in years_hist:
        year_hist = JJA_hist.sel(time = JJA_hist.time.dt.year == year)
        mean_hist = year_hist.mean(dim = 'time')
        means_hist.append(mean_hist)        
    combine_means_hist = bp.xr.concat(means_hist, dim = 'year')
    overall_mean_hist = combine_means_hist.mean(dim = 'year')

    years_fut = range(2070, 2100)
    if zoom_out == True:
        location_fut = open_fut[variable].sel(lat = slice(0, 65), lon = slice(200, 300))
    else:
        location_fut = open_fut[variable].sel(lat = slice(15, 53), lon = slice(215, 295))
    JJA_fut = location_fut.sel(time = location_fut.time.dt.month.isin(range(start_month, stop_month + 1)))
    means_fut = []
    for year in years_fut:
        year_fut = JJA_fut.sel(time = JJA_fut.time.dt.year == year)
        mean_fut = year_fut.mean(dim = 'time', skipna = True)
        means_fut.append(mean_fut)
    combine_means_fut = bp.xr.concat(means_fut, dim = 'year')
    overall_mean_fut = combine_means_fut.mean(dim = 'year')
   
    # Sets up all variables as a difference between time periods except for precipitation as a percent change
    if variable == 'pr':
        anomaly = ((overall_mean_fut - overall_mean_hist) / overall_mean_hist) * 100
    else:
        anomaly = overall_mean_fut - overall_mean_hist
        
    # conversions for some variables
    if variable == 'psl':
        anomaly *= 0.01 # convert from Pa to hPa
    elif variable == 'huss':
        anomaly *= 1000 # convert from kg/kg to g/kg

    return anomaly

# examples of the anomaly function being used to return a lat and lon xarray.DataArray for the specified variable
# vas = anomaly('ACCESS-CM2', 'vas')
# uas = anomaly('ACCESS-CM2', 'uas')
# psl = anomaly('ACCESS-CM2', 'psl')
# pr = anomaly('ACCESS-CM2', 'pr')


# maps xarray.DataArray from one of the above functions 
def map_anomalies(anomaly_ref, model_name, variable, start_month, stop_month, quiver = False, step = 1, zoom_out = False):
    # specified what function to use and calls it to get xarray.DataArray
    if zoom_out == True:
        data = anomaly_ref(model_name, variable, start_month, stop_month, zoom_out = True)
        shrink = 0.6
    else:
        data = anomaly_ref(model_name, variable, start_month, stop_month)
        shrink = 0.85
    
    # defines a dictionary that stores formatting information for each variable -> see else: for more information
    if variable == 'psl': 
        plot_dict = {'cmap_a' : bp.cmap.cmap('MPL_coolwarm'),
                     'cmap_m' : bp.cmap.cmap('MPL_coolwarm'),
                     'title': 'Sea Level Pressure', 
                     'cbar_a' : 'Change in Sea Level Pressure (hPa)',
                     'cbar_m' : 'Mean Sea Level Pressure (hPa)',
                     'min_m' : 1002.8295312500001,
                     'max_m' : 1027.75984375,
                     'min_a' : -2.1117968559265137,
                     'max_a' : 3.2
                     }
    elif variable == 'pr':
        plot_dict = {'cmap_a' : bp.cmap.cmap('MPL_BrBG'),
                     'cmap_m' : bp.cmap.cmap('cmocean_haline', revBool = True),
                     'title': 'Precipitation',
                     'cbar_a' : 'Change in Precipitation (%)',
                     'cbar_m' : 'Mean Precipitation (mm)',
                     'min_m' : 0.21196805760707713,
                     'max_m' : 360,
                     'min_a' : -75,
                     'max_a' : 300
                     }
    elif variable == 'zg':
        plot_dict = {'cmap_a' : bp.cmap.cmap('BlAqGrYeOrReVi200'),
                     'cmap_m' : bp.cmap.cmap('MPL_coolwarm'),
                     'title': 'Geopotential Height',
                     'cbar_a' : 'Change in 500-hPa Geopotential Height (m)',
                     'cbar_m' : 'Mean 500-hPa Geopotential Height (m)',
                     'min_m' : 5676.18017578125,
                     'max_m' : 5978.65869140625,
                     'min_a' : 75,
                     'max_a' : 200
                     }
    elif variable == 'vas':
        plot_dict = {'cmap_a' : bp.cmap.cmap('CBR_wet'),
                     'cmap_m' : bp.cmap.cmap('MPL_coolwarm'),
                     'title': 'Northward Near Surface Wind',
                     'cbar_a' : 'Change in Northward Near Surface Wind (m s\u207B\u00B9)', # m s^-1
                     'cbar_m' : 'Mean Northward Near Surface Wind (m s\u207B\u00B9)', # m s^-1
                     'min_m' : -9.491390228271484,
                     'max_m' : 6.107685565948486,
                     'min_a' : -1.862033486366272,
                     'max_a' : 3.81015682220459
                     }
    elif variable == 'uas':
        plot_dict = {'cmap_a' : bp.cmap.cmap('CBR_wet'),
                     'cmap_m' : bp.cmap.cmap('MPL_coolwarm'),
                     'title': 'Easthward Near Surface Wind',
                     'cbar_a' : 'Change in Eastward Near Surface Wind (m s\u207B\u00B9)', # m s^-1
                     'cbar_m' : 'Mean Eastward Near Surface Wind (m s\u207B\u00B9)', # m s^-1
                     'min_m' : -11.079482078552246,
                     'max_m' : 5.9408488273620605,
                     'min_a' : -3.5138015747070312,
                     'max_a' : 2.595974922180176
                     }
    elif variable == 'ts':
        plot_dict = {'cmap_a' : bp.cmap.cmap('MPL_YlOrRd'),
                     'cmap_m' : bp.cmap.cmap('MPL_YlOrRd'),
                     'title': 'Surface Temperature',
                     'cbar_a' : 'Change in Surface Temperature (K)',
                     'cbar_m' : 'Mean Surface Temperature (K)',
                     'min_m' : 281.8443298339844,
                     'max_m' : 318.0555114746094,
                     'min_a' : 0.475433349609375,
                     'max_a' : 15.549346923828125
                     }
    elif variable == 'huss':
        plot_dict = {'cmap_a' : bp.cmap.cmap('MPL_YlGnBu'),
                     'cmap_m' : bp.cmap.cmap('cmocean_haline', revBool = True),
                     'title': 'Near Surface Specific Humidity',
                     'cbar_a' : 'Change in Near Surface Specific Humidity (g/kg)', # xr dataset says units are 1 but I think g/kg?
                     'cbar_m' : 'Mean Near Surface Specific Humidity (g/kg)',
                     'min_m' : 4.40641213208437,
                     'max_m' : 27.03595533967018,
                     'min_a' : 0,
                     'max_a' : 7.801617622375488
                     }
        
    # format and function of dictionary explained
    else:
        plot_dict = {'cmap_a' : 'color map for anomaly',
                     'cmap_m' : 'color map for hist/fut means',
                     'title': 'Test Map Title',
                     'cbar_a' : 'Default Measurement for anomaly colorbar',
                     'cbar_m' : 'Default Measurement for hist/fut mean colorbar',
                     'min_m' : 0,
                     'max_m' : 100,
                     'min_a' : 0,
                     'max_a' : 100
                     }
        
    #setup map
    fig = bp.plt.figure()
    ax = bp.plt.axes(projection  = bp.ccrs.PlateCarree())
    
    # set the color transition to happen at 0
    if anomaly_ref.__name__ == 'anomaly':
        data_min = plot_dict['min_a']
        data_max = plot_dict['max_a']
    else:
        data_min = plot_dict['min_m']
        data_max = plot_dict['max_m']

    # defualts norm if 0 can't be at the center
    if data_min < 0.00 < data_max:
        norm = bp.mcolors.TwoSlopeNorm(vmin=data_min, vcenter=0.00, vmax=data_max)
    else:
        norm = bp.mcolors.Normalize(vmin=data_min, vmax=data_max)

    # create outline of map based on mean values or anomalies
    if anomaly_ref.__name__ == 'fut_mean':
        contour = ax.contourf(data['lon'], data['lat'], data.values, cmap = plot_dict['cmap_m'], transform = bp.ccrs.PlateCarree(), levels = 20, norm = norm)
        ax.set_title(f'{model_name} ssp585\nMean {plot_dict['title']}\n2070-2099', fontsize = 18)
        cbar = bp.plt.colorbar(contour, orientation = 'horizontal', pad = 0.03, aspect = 50, shrink = shrink, extend = 'both')
        cbar.set_label(plot_dict['cbar_m'], fontsize = 10)
        cbar.ax.xaxis.set_major_formatter(bp.ticker.FormatStrFormatter('%.0f'))
    elif anomaly_ref.__name__ == 'hist_mean':
        contour = ax.contourf(data['lon'], data['lat'], data.values, cmap = plot_dict['cmap_m'], transform = bp.ccrs.PlateCarree(), levels = 20, norm = norm)
        ax.set_title(f'{model_name}\nMean {plot_dict['title']}\n1985-2014', fontsize = 18)
        cbar = bp.plt.colorbar(contour, orientation = 'horizontal', pad = 0.03, aspect = 50, shrink = shrink, extend = 'both')
        cbar.set_label(plot_dict['cbar_m'], fontsize = 10)
        cbar.ax.xaxis.set_major_formatter(bp.ticker.FormatStrFormatter('%.0f'))
    else:
        contour = ax.contourf(data['lon'], data['lat'], data.values, cmap = plot_dict['cmap_a'], transform = bp.ccrs.PlateCarree(), levels = 20, norm = norm)
        ax.set_title(f'{model_name} ssp585\n{plot_dict['title']} Anomaly\n2070-2099 vs 1985-2014', fontsize = 18)
        cbar = bp.plt.colorbar(contour, orientation = 'horizontal', pad = 0.03, aspect = 50, shrink = shrink, extend = 'both')
        cbar.set_label(plot_dict['cbar_a'], fontsize = 10)
        if variable == 'pr' or variable == 'ts' or variable == 'zg':
            cbar.ax.xaxis.set_major_formatter(bp.ticker.FormatStrFormatter('%.0f'))
        else:
            cbar.ax.xaxis.set_major_formatter(bp.ticker.FormatStrFormatter('%.2f'))
    if zoom_out == True:
        ax.set_ylim(1.25, 63)
        ax.set_xlim(-157.75, -61.5)
    else:
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
    if zoom_out == True:
        save_name = f'ZOOOMED_{variable}_{anomaly_ref.__name__}_{start_month}-{stop_month}_{model_name}.png'
        # slice uas and vas data
        u = anomaly_ref(model_name, 'uas', start_month, stop_month, zoom_out = True)
        v = anomaly_ref(model_name, 'vas', start_month, stop_month, zoom_out = True)
        
    else:
        save_name = f'{variable}_{anomaly_ref.__name__}_{start_month}-{stop_month}_{model_name}.png'
        # slice uas and vas data
        u = anomaly_ref(model_name, 'uas', start_month, stop_month,)
        v = anomaly_ref(model_name, 'vas', start_month, stop_month,)

    # activate my_quiver function
    if quiver == True:
        if zoom_out == True:
            save_name = f'ZOOMED_{variable}_{anomaly_ref.__name__}_{start_month}-{stop_month}_{model_name}_quiver.png'
        else:
            save_name = f'{variable}_{anomaly_ref.__name__}_{start_month}-{stop_month}_{model_name}_quiver.png'
            
        # set scale to adjust based on being an anomaly or fut/hist mean
        if anomaly_ref.__name__ == 'anomaly':
            scale = 20
        else: 
            scale = 175
        
        # interpolate data to fit same grid
        if zoom_out == True:
            ds_out = bp.xr.Dataset(
                {
                    "lat": (["lat"], bp.np.arange(1.25, 63, 3)),
                    "lon": (["lon"], bp.np.arange(200, 300, 3)),
                }
            )
        else:
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
    save_path = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/anomaly_maps/{model_name}/'
    if start_month == 6 and stop_month == 8:
        save_path = bp.os.path.join(save_path, 'JJA/' + save_name)
    elif start_month == 7 and stop_month == 8:
        save_path = bp.os.path.join(save_path, 'JA/' + save_name)
    elif start_month == 7 and stop_month == 9:
        save_path = bp.os.path.join(save_path, 'JAS/' + save_name)
    else:
        save_path = bp.os.path.join(save_path)
    
    bp.plt.savefig(save_path, dpi = 400)
    bp.plt.show()   
    
    return fig, ax


# run more at once
variables = ['pr', 'psl', 'zg', 'ts', 'huss']
refs = [hist_mean, fut_mean, anomaly]

for ref in refs:
    for variable in variables:
        for model in models:
            map_anomalies(ref, model, variable, 7, 9)
            bp.plt.show()
            print(model, variable, ref.__name__)


# DATA FOR NEW MODEL GROUPS
# map_anomalies(hist_mean, H_models[-1], 'psl') 

# EXAMPLES FOR OLD MODEL GROUPS
# loop over multiple models for one variable
# for model in L_models:
#     map_anomalies(hist_mean, model, 'zg')
#     bp.plt.show()

# run one test model for one variable
# test = map_anomalies(fut_mean, 'KACE-1-0-G', 'zg') 
    
# complete list of models analyzed
# models = ['UKESM1-0-LL', 'ACCESS-CM2', 'CanESM5', 'KACE-1-0-G', 'MPI-ESM1-2-LR', 'CNRM-ESM2-1', 'CNRM-CM6-1-HR', 'INM-CM4-8']

                  #%%
variable = 'pr'
model_name = 'KACE-1-0-G'
fpath = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/ERA5/{variable}/{variable}_Amon_'
files = bp.xr.open_mfdataset(bp.glob.glob(fpath + model_name + '*.nc'))

# file = files[0]
# ds = bp.xr.open_dataset(file)
# print(ds)


#%%
# finding min and max across datasets for each variable
models = ['KACE-1-0-G', 'CanESM5', 'UKESM1-0-LL', 'ACCESS-CM2', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'MPI-ESM1-2-LR']

def min_max (variable):
    all_mins = []
    all_maxs = []
    for model in models:
        open = bp.xr.open_mfdataset(f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/ERA5/{variable}/{variable}_Amon_{model}_*.nc')
        open = open[variable].sel(lat = slice(15, 53), lon = slice(215, 295))
        open = open.sel(time = open.time.dt.month.isin([6, 7, 8]))
        years = range(1985, 2099)
        if variable == 'zg':
            open = open.sel(plev = 50000, method = 'nearest')
        means = []
        for year in years:
            one_year = open.sel(time = open.time.dt.year == year)
            # GCM pr data is in precipitation flux so the time unit has to be taken out
            if variable == 'pr':
                days_in_month = open.time.dt.days_in_month
                seconds_per_month = days_in_month * 24 * 60 * 60
                mean = (one_year * seconds_per_month).mean(dim = 'time')
            else:
                mean = one_year.mean(dim = 'time')
            means.append(mean)
        combine = bp.xr.concat(means, dim = 'year')
        total_mean = combine.mean(dim = 'year')
        data_min = float(total_mean.min())
        data_max = float(total_mean.max())
            
        if variable == 'psl':
            data_min *= 0.01 # convert from Pa to hPa
            data_max *= 0.01
        elif variable == 'huss':
            data_min *= 1000 # convert from kg/kg to g/kg
            data_max *= 1000
                
        all_mins.append(data_min)
        all_maxs.append(data_max)
            
    final_min = min(all_mins)
    final_max = max(all_maxs)
    
    result = f'Min for {variable}: {final_min}\nMax for {variable}: {final_max}'
    return result
        
print(min_max('uas'))

#MIN AND MAX VALUES FOR HIST AND FUT MEANS
# Min for pr: 0.21196805760707713
# Max for pr: 783.1986581526485

# Min for psl: 1002.8295312500001
# Max for psl: 1027.75984375

# Min for huss: 4.40641213208437
# Max for huss: 27.03595533967018

# Min for ts: 281.8443298339844
# Max for ts: 318.0555114746094

# Min for zg: 5676.18017578125
# Max for zg: 5978.65869140625

# Min for vas: -9.491390228271484
# Max for vas: 6.107685565948486

# Min for uas: -11.079482078552246
# Max for uas: 5.9408488273620605

#%%
def anom_min_max(variable):
    all_mins = []
    all_maxs = []
    for model in models:
        open_hist = bp.xr.open_mfdataset(f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/ERA5/{variable}/{variable}_Amon_{model}_hist*.nc')
        open_fut = bp.xr.open_mfdataset(f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/ERA5/{variable}/{variable}_Amon_{model}_ssp*.nc')
     
        open_hist = open_hist[variable].sel(lat = slice(15, 53), lon = slice(215, 295))
        open_hist = open_hist.sel(time = open_hist.time.dt.month.isin([6, 7, 8]))
        
        open_fut = open_fut[variable].sel(lat = slice(15, 53), lon = slice(215, 295))
        open_fut = open_fut.sel(time = open_fut.time.dt.month.isin([6, 7, 8]))
    
        # geopotential height has an extra dimension for what pressure level you want to look at (we chose 500 hPa)
        if variable == 'zg':
            open_hist = open_hist.sel(plev = 50000, method = 'nearest')
            open_fut = open_fut.sel(plev = 50000, method = 'nearest')
            
        years_hist = range(1985, 2015)
        means_hist = []
        for year in years_hist:
            year_hist = open_hist.sel(time = open_hist.time.dt.year == year)
            mean_hist = year_hist.mean(dim = 'time')
            means_hist.append(mean_hist)        
        combine_means_hist = bp.xr.concat(means_hist, dim = 'year')
        overall_mean_hist = combine_means_hist.mean(dim = 'year')

        years_fut = range(2070, 2100)
        means_fut = []
        for year in years_fut:
            year_fut = open_fut.sel(time = open_fut.time.dt.year == year)
            mean_fut = year_fut.mean(dim = 'time', skipna = True)
            means_fut.append(mean_fut)
        combine_means_fut = bp.xr.concat(means_fut, dim = 'year')
        overall_mean_fut = combine_means_fut.mean(dim = 'year')
       
        # Sets up all variables as a difference between time periods except for precipitation as a percent change
        if variable == 'pr':
            anomaly = ((overall_mean_fut - overall_mean_hist) / overall_mean_hist) * 100
        else:
            anomaly = overall_mean_fut - overall_mean_hist
        
        # conversions for some variables
        if variable == 'psl':
            anomaly *= 0.01 # convert from Pa to hPa
        elif variable == 'huss':
            anomaly *= 1000 # convert from kg/kg to g/kg
            
        # find min and max of all returned anomalies
        data_max = float(anomaly.max())
        data_min = float(anomaly.min())
        
        all_mins.append(data_min)
        all_maxs.append(data_max)
    
    total_min = min(all_mins)
    total_max = max(all_maxs)
    result = f'Anom min for {variable}: {total_min}\nAnom max for {variable}: {total_max}'
        
    return result

print(anom_min_max('zg'))
    
# MIN AND MAX VALUES FOR ANOMALIES 
# Anom min for pr: -84.02847290039062
# Anom max for pr: 362.8335266113281

# Anom min for psl: -2.1117968559265137
# Anom max for psl: 4.881171703338623

# Anom min for huss: -0.7689297199249268
# Anom max for huss: 7.801617622375488

# Anom min for ts: 0.475433349609375
# Anom max for ts: 15.549346923828125

# Anom min for uas: -3.5138015747070312
# Anom max for uas: 2.595974922180176

# Anom min for vas: -1.862033486366272
# Anom max for vas: 3.81015682220459

# Anom min for zg: 69.8876953125
# Anom max for zg: 210.7177734375


#%%
variable = 'pr'
model = 'CanESM5'
open = bp.xr.open_mfdataset(f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/ERA5/{variable}/{variable}_Amon_{model}_*.nc')
open = open[variable].sel(lat = slice(15, 53), lon = slice(215, 295))
open = open.sel(time = open.time.dt.month.isin([6, 7, 8]))
years = range(1985, 2099)
means = []
for year in years:
    one_year = open.sel(time = open.time.dt.year == year)
    # GCM pr data is in precipitation flux so the time unit has to be taken out
    if variable == 'pr':
        days_in_month = open.time.dt.days_in_month
        seconds_per_month = days_in_month * 24 * 60 * 60
        mean = (one_year * seconds_per_month).mean(dim = 'time')
    else:
        mean = one_year.mean(dim = 'time')
data_max = float(mean.max())
data_min = float(mean.min())

    