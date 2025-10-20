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


# output of values in VIC shapefile
# min_lon = -113.69354024533703
# max_lon = -110.59375
# min_lat = 39.553038338687124
# max_lat = 42.84375


def convert_lon_to_0_360(lon):
    
    """
    GCM lon values are in 0-360 format while other datasets use -180-180 -> 
    conversion may be needed.
    """
    
    # Convert longitude from -180-180 to 0-360
    lon = bp.np.array(lon)
    lon_360 = (lon + 360) % 360
    
    return lon_360


def convert_lon_360_to_180(lon):
    
    """
    Convert longitude from 0360 range to -180 to 180 range
    """
    
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


def region_mean(model_name, variable, start_month, stop_month, level = None, start_year = 1979, stop_year = 2014, zoom_out = False, *kwargs): 
    
    """
    Function to calculate the mean for each gridpoint across the historical period 
    (1979-2014). Intended to run for the summer months. Zoom out expands the region 
    to have a broader view of the Pacific Ocean. Returns an xarray.DataArray.
    
    Note that the level (plev) is selected in Pa not hPa so 500 hPa = 50000.
    """
    
    fpath = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/ERA5/{variable}/{variable}_Amon_'
    
    # lets the function know what file to open for the given model and variable based on date range
    if 1970 <= start_year <= 2014:
        date = '_hist*.nc'
    else:
        date = '_ssp585*.nc'
    
    fname = fpath + model_name + date
    open = bp.xr.open_mfdataset(bp.glob.glob(fname), decode_times = True)
    # print('Files Found:', bp.glob.glob(fname))
    
    # variables that have an extra dimension for what pressure level you want to look at needs to be selected
    # geopotential height should be at the  500 hPa level
    if level == None:
        print('No level to select')
    else:
        open = open.sel(plev = level, method = 'nearest')
    
    if zoom_out == True:
        location = open[variable].sel(lat = slice(0, 65), lon = slice(200, 300))
    else: 
        location = open[variable].sel(lat = slice(15, 53), lon = slice(215, 295))
        
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
    combine_means = bp.xr.concat(means, dim = 'year')
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
    
    if zoom_out == True:
        overall_mean_hist = region_mean(model_name, variable, start_month, stop_month, level, start_year = 1979, stop_year = 2014, zoom_out = True)
        overall_mean_fut = region_mean(model_name, variable, start_month, stop_month, level, start_year = 2070, stop_year = 2099, zoom_out = True)
        
    else:
        overall_mean_hist = region_mean(model_name, variable, start_month, stop_month, level, start_year = 1979, stop_year = 2014)
        overall_mean_fut = region_mean(model_name, variable, start_month, stop_month, level, start_year = 2070, stop_year = 2099)
   
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

# example of the anomaly function being used to return a lat and lon xarray.DataArray for the specified variable
# vas = anomaly('ACCESS-CM2', 'vas')


def quiver(u, v, ax, anomaly_ref, model_name, start_month, stop_month, level, start_year, stop_year, zoom_out = False, step = 1, *kwargs):
    
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
        scale = 35
        U = 1
        label = '1 m/s'
    else: 
        scale = 175
        U = 5
        label = '5 m/s'
        
    # interpolate data to fit same grid
    if zoom_out == True:
        ds_out = bp.xr.Dataset(
            {
                "lat": (["lat"], bp.np.arange(1.25, 63, 3)),
                "lon": (["lon"], bp.np.arange(200, 300, 3)),
            }
        )
        
        # patch size for key
        width = 0.14
        height = 0.035
        
    else:
        ds_out = bp.xr.Dataset(
            {
                "lat": (["lat"], bp.np.arange(15.625, 51.88, 2.75)),
                "lon": (["lon"], bp.np.arange(216.5625, 295.275, 2.75)),
            }
        )
        
        # patch size for key
        width = 0.1
        height = 0.035
    
    regridder_u = bp.xe.Regridder(u, ds_out, 'bilinear')
    regridder_v = bp.xe.Regridder(v, ds_out, 'bilinear')
    u = regridder_u(u)
    v = regridder_v(v)

    # allow to skip values
    lat = u['lat'][::step]
    lon = u['lon'][::step]
    X, Y = bp.np.meshgrid(lon, lat)
    uu = bp.np.array(u[::step, ::step])
    vv = bp.np.array(v[::step, ::step])
    
    # setup quiver
    quiv = ax.quiver(X, Y, uu, vv,
                pivot = 'tail',
                width = 0.0015,
                scale = scale, 
                headwidth = 6,
                color = 'k',
                transform = bp.ccrs.PlateCarree())
    
    
    bbox = bp.FancyBboxPatch((0.03, 0.04), width, height,
                      transform=ax.transAxes,
                      fc='white', ec='black', boxstyle='round,pad=0.02', zorder=1)
    
    ax.add_patch(bbox)
    
    key = ax.quiverkey(quiv, 
                       X = 0.05, 
                       Y = 0.05, 
                       U = U, 
                       label = label, 
                       labelpos = 'E')
        
    return quiv, key


def map_anomalies(anomaly_ref, model_name, variable, start_month, stop_month, level = None, start_year = 1979, stop_year = 2014, add_quiver = None, u = 'uas', v = 'vas', save = False, zoom_out = False):
    
    """
    Maps xarray.DataArray from specified function. Can use contourfill to visualize a 
    single variable and also overlay wind vectors (quiver). Mapping dictionary contains
    data for each variable to set associated titles, colors, and standardization of the 
    scale for the color bar. 
    
    Note that the level (plev) is selected in Pa not hPa so 500 hPa = 50000.
    """
    
    # defines a dictionary that stores formatting information for each variable -> see else: for more information
    plot_dict = {'psl' : {
                     'anomaly' : {
                          'cmap' : bp.cmap.cmap('MPL_coolwarm'),
                           'cbar' : 'Change in Sea Level Pressure (hPa)',
                           'min' : -2.1117968559265137,
                           'max' : 3.2,
                           'title': 'Sea Level Pressure'
                      },
                      'region_mean' : 
                          {'cmap' : bp.cmap.cmap('MPL_coolwarm'),
                           'cbar' : 'Mean Sea Level Pressure (hPa)',
                           'min' : 1002.8295312500001,
                           'max' : 1027.75984375,
                           'title': 'Sea Level Pressure'
                        }
                    },
                    'pr': {
                        'anomaly': {
                            'cmap': bp.cmap.cmap('MPL_BrBG'),
                            'cbar': 'Change in Precipitation (%)',
                            'min': -75,
                            'max': 300,
                            'title': 'Precipitation'
                        },
                        'region_mean': {
                            'cmap': bp.cmap.cmap('cmocean_haline', revBool=True),
                            'cbar': 'Mean Precipitation (mm)',
                            'min': 0.21196805760707713,
                            'max': 360,
                            'title': 'Precipitation'
                        }
                    },
                    'zg': {
                        'anomaly': {
                            'cmap': bp.cmap.cmap('BlAqGrYeOrReVi200'),
                            'cbar': 'Change in 500-hPa Geopotential Height (m)',
                            'min': 75,
                            'max': 200,
                            'title': 'Geopotential Height'
                        },
                        'region_mean': {
                            'cmap': bp.cmap.cmap('MPL_coolwarm'),
                            'cbar': 'Mean 500-hPa Geopotential Height (m)',
                            'min': 5676.18017578125,
                            'max': 5978.65869140625,
                            'title': 'Geopotential Height'
                        }
                    },
                    'vas': {
                        'anomaly': {
                            'cmap': bp.cmap.cmap('CBR_wet'),
                            'cbar': 'Change in Northward Near Surface Wind (m s\u207B\u00B9)',
                            'min': -1.862033486366272,
                            'max': 3.81015682220459,
                            'title': 'Northward Near Surface Wind'
                        },
                        'region_mean': {
                            'cmap': bp.cmap.cmap('MPL_coolwarm'),
                            'cbar': 'Mean Northward Near Surface Wind (m s\u207B\u00B9)',
                            'min': -9.491390228271484,
                            'max': 6.107685565948486,
                            'title': 'Northward Near Surface Wind'
                        }
                    },
                    'uas': {
                        'anomaly': {
                            'cmap': bp.cmap.cmap('CBR_wet'),
                            'cbar': 'Change in Eastward Near Surface Wind (m s\u207B\u00B9)',
                            'min': -3.5138015747070312,
                            'max': 2.595974922180176,
                            'title': 'Eastward Near Surface Wind'
                        },
                        'region_mean': {
                            'cmap': bp.cmap.cmap('MPL_coolwarm'),
                            'cbar': 'Mean Eastward Near Surface Wind (m s\u207B\u00B9)',
                            'min': -11.079482078552246,
                            'max': 5.9408488273620605,
                            'title': 'Eastward Near Surface Wind'
                        }
                    },
                    'ts': {
                        'anomaly': {
                            'cmap': bp.cmap.cmap('MPL_YlOrRd'),
                            'cbar': 'Change in Surface Temperature (K)',
                            'min': 0.475433349609375,
                            'max': 15.549346923828125,
                            'title': 'Surface Temperature'
                        },
                        'region_mean': {
                            'cmap': bp.cmap.cmap('MPL_YlOrRd'),
                            'cbar': 'Mean Surface Temperature (K)',
                            'min': 281.8443298339844,
                            'max': 318.0555114746094,
                            'title': 'Surface Temperature'
                        }
                    },
                    'huss': {
                        'anomaly': {
                            'cmap': bp.cmap.cmap('MPL_YlGnBu'),
                            'cbar': 'Change in Near Surface Specific Humidity (g/kg)',
                            'min': 0,
                            'max': 7.801617622375488,
                            'title': 'Near Surface Specific Humidity'
                        },
                        'region_mean': {
                            'cmap': bp.cmap.cmap('cmocean_haline', revBool=True),
                            'cbar': 'Mean Near Surface Specific Humidity (g/kg)',
                            'min': 4.40641213208437,
                            'max': 27.03595533967018,
                            'title': 'Near Surface Specific Humidity'
                        }
                    },
                    'hus': {
                        'anomaly': {
                            'cmap': bp.cmap.cmap('MPL_YlGnBu'),
                            'cbar': f'Change in Specific Humidity (g/kg) at {level} Pa',
                            'min': 0,
                            'max': 3.5, #7801.617622375488,
                            'title': 'Specific Humidity'
                        },
                        'region_mean': {
                            'cmap': bp.cmap.cmap('cmocean_haline', revBool=True),
                            'cbar': f'Mean Specific Humidity (g/kg) at {level} Pa',
                            'min': 0.9462222806178033,
                            'max': 6, #4.642414394766092,
                            'title': 'Specific Humidity'
                        }
                    },
                    'ua': {
                        'anomaly': {
                            'cmap': bp.cmap.cmap('MPL_YlGnBu'),
                            'cbar': 'Change in Near Surface Specific Humidity (g/kg)',
                            'min': 0,
                            'max': 7.801617622375488,
                            'title': 'Near Surface Specific Humidity'
                        },
                        'region_mean': {
                            'cmap': bp.cmap.cmap('cmocean_haline', revBool=True),
                            'cbar': 'Mean Near Surface Specific Humidity (g/kg)',
                            'min': 4.40641213208437,
                            'max': 27.03595533967018,
                            'title': 'Near Surface Specific Humidity'
                        }
                    },
                    'va': {
                        'anomaly': {
                            'cmap': bp.cmap.cmap('MPL_YlGnBu'),
                            'cbar': 'Change in Near Surface Specific Humidity (g/kg)',
                            'min': 0,
                            'max': 7.801617622375488,
                            'title': 'Near Surface Specific Humidity'
                        },
                        'region_mean': {
                            'cmap': bp.cmap.cmap('cmocean_haline', revBool=True),
                            'cbar': 'Mean Near Surface Specific Humidity (g/kg)',
                            'min': 4.40641213208437,
                            'max': 27.03595533967018,
                            'title': 'Near Surface Specific Humidity'
                        }
                    }
                }

    # specified what function to use and calls it to get xarray.DataArray
    if zoom_out == True:
        shrink = 0.6
        if anomaly_ref.__name__ == 'anomaly':
            save_name = f'ZOOOMED_{variable}_{anomaly_ref.__name__}_{start_month}-{stop_month}_{model_name}.png'
            data = anomaly_ref(model_name, variable, start_month, stop_month, level, zoom_out = True)
        else:
            save_name = f'ZOOOMED_{variable}_{anomaly_ref.__name__}_{start_month}-{stop_month}_{start_year}-{stop_year}_{model_name}.png'
            data = anomaly_ref(model_name, variable, start_month, stop_month, level, start_year, stop_year, zoom_out = True)
        
    else:
        shrink = 0.85
        if anomaly_ref.__name__ == 'anomaly':
            save_name = f'{variable}_{anomaly_ref.__name__}_{start_month}-{stop_month}_{model_name}.png'
            data = anomaly_ref(model_name, variable, start_month, stop_month, level)
        else:
            save_name = f'{variable}_{anomaly_ref.__name__}_{start_month}-{stop_month}_{start_year}-{stop_year}_{model_name}.png'
            data = anomaly_ref(model_name, variable, start_month, stop_month, level, start_year, stop_year)
        
    # setup map
    fig = bp.plt.figure()
    ax = bp.plt.axes(projection  = bp.ccrs.PlateCarree())
    
    # set the color transition to happen at 0
    variable_min = plot_dict[variable][anomaly_ref.__name__]['min']
    variable_max = plot_dict[variable][anomaly_ref.__name__]['max']
    ticks = bp.np.linspace(variable_min, variable_max, num = 9)

    # defualts norm if 0 can't be at the center
    if variable_min < 0.00 < variable_max:
        norm = bp.mcolors.TwoSlopeNorm(vmin = variable_min, vcenter = 0.00, vmax = variable_max)
    else:
        norm = bp.mcolors.Normalize(vmin = variable_min, vmax = variable_max)

    # create outline of map based on mean values or anomalies
    contour = ax.contourf(data['lon'], data['lat'], data.values, cmap = plot_dict[variable][anomaly_ref.__name__]['cmap'], transform = bp.ccrs.PlateCarree(), levels = 20, norm = norm)
    
    # create a scalar mappable as a standin for contour so the colorbar remains standardized across different maps
    sm = bp.mpl.cm.ScalarMappable(norm = norm, cmap = plot_dict[variable][anomaly_ref.__name__]['cmap'])
    sm.set_array([]) # makes sure no data is attached to the colorbar
    
    # specify the layout of the colorbar
    cbar = bp.plt.colorbar(sm, ax = ax, orientation = 'horizontal', pad = 0.03, aspect = 50, shrink = shrink, extend = 'both', ticks = ticks)
    cbar.set_label(plot_dict[variable][anomaly_ref.__name__]['cbar'], fontsize = 10)
    
    if variable == 'ts' or variable == 'zg' or variable == 'pr' or variable == 'huss' or variable == 'psl':
        cbar.ax.xaxis.set_major_formatter(bp.ticker.FormatStrFormatter('%.0f'))
    else:
        cbar.ax.xaxis.set_major_formatter(bp.ticker.FormatStrFormatter('%.2f'))
        
    if anomaly_ref.__name__ == 'region_mean':
        ax.set_title(f'{model_name} ssp585\nMean {plot_dict[variable][anomaly_ref.__name__]['title']}\n{time_dict[range(start_month, stop_month +1)]} {start_year}-{stop_year}', fontsize = 18)
        
    else:
        ax.set_title(f'{model_name} ssp585\n{plot_dict[variable][anomaly_ref.__name__]['title']} Anomaly\n{time_dict[range(start_month, stop_month +1)]} 2070-2099 vs 1985-2014', fontsize = 18)
        
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
    
    # add arrows to show wind vectors
    if add_quiver == True:
        quiver_obj, quiver_key = quiver(u, v, ax, anomaly_ref, model_name, start_month, stop_month, level, start_year, stop_year, zoom_out, step = 1)
            
    # save path for files
    if save == True:
        # all PNGs stored to anomaly_maps directory but ignored in Git
        save_path = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/anomaly_maps/{model_name}/'
        
        # refers to time_dict for the naming files based on the given months
        save_path = bp.os.path.join(save_path, time_dict[range(start_month, stop_month +1)] + save_name)
        bp.plt.savefig(save_path, dpi = 400)
        
    bp.plt.show()   
    
    return fig, ax


variables = ['pr', 'huss', 'psl', 'ts']
H_variables = ['hus', 'zg']

for variable in variables:
    for model in models:
        map_anomalies(region_mean, model, variable, 6, 6, start_year = 1979, stop_year = 2014, save = True)
        map_anomalies(region_mean, model, variable, 6, 6, start_year = 2070, stop_year = 2099, save = True)
        bp.plt.show()


# run more at once
# variables = ['pr', 'psl', 'zg', 'ts', 'huss']


# for variable in variables:
#     for model in models:
#         map_anomalies(anomaly, model, variable, 7, 9)
#         map_anomalies(region_mean, model, variable, 7, 9, 2070, 2099)
#         map_anomalies(region_mean, model, variable, 7, 9, 1979, 2014)
#         bp.plt.show()
    

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
        if variable == 'zg' or variable == 'hus':
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
        
print(min_max('hus'))

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
        if variable == 'zg' or variable == 'hus':
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

print(anom_min_max('hus'))
    
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

    