#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 16 16:14:29 2025

@author: u1301408
"""

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/packages/')
import base_packages as bp

# Define the shapefile path (where to find coordinates used by VIC from Maribeth at USBR)
bdir = '/uufs/chpc.utah.edu/common/home/u0660911/Documents/projects/gslbip/'
shapefile_path = bp.os.path.join(bdir,'GSLBIP_shpfiles/MF6_VIC_bounding_box/MF6_VIC_bounding_box.shp')

# Load the shapefile for VIC boundaries of Great Salt Lake Basin (not applied for larger maps)
gdf = bp.gpd.read_file(shapefile_path)
gdf = gdf.to_crs("EPSG:4326")
min_lon, min_lat, max_lon, max_lat = gdf.total_bounds

# function to find the mean for each gridpoint from 2070-2099 in the region for a given model
def fut_mean(model_name, variable, interpolate = False):
    #sea surface temperature is oceanic data rather than atmospheric data
    if variable == 'tos':
        fpath = fpath = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/intake_esgf/ERA5/{variable}/{variable}_Omon_'
    # file path format for atmospheric data
    else:
        fpath = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/intake_esgf/ERA5/{variable}/{variable}_Amon_'
    open_fut = bp.xr.open_mfdataset(fpath + model_name + '_ssp*.nc', engine = 'netcdf4')
    # geopotential height has an extra dimension for what pressure level you want to look at (we chose 500 hPa)
    if variable == 'zg':
        open_fut = open_fut.sel(plev=50000, method = 'nearest')

    if interpolate == True:
        # interploate data to fit on the same gridpoints (required when averaging over models on different grids)
        ds_out = bp.xr.Dataset(
            {
                "lat": (["lat"], bp.np.arange(15.62, 51.88, 1.25)),
                "lon": (["lon"], bp.np.arange(216.5625, 295.275, 1.875)),
            }
        )

        regridder = bp.xe.Regridder(open_fut, ds_out, 'bilinear')
        open_fut = regridder(open_fut)
        
    years_fut = range(2070, 2100)
    location_fut = open_fut[variable].sel(lat = slice(15, 53), lon = slice(215, 295)) # region was selected that was large enough to view influencing patterns over the ocean
    JJA_fut = location_fut.sel(time = location_fut.time.dt.month.isin([6, 7, 8]))
    means_fut = []
    for year in years_fut:
        year_fut = JJA_fut.sel(time = JJA_fut.time.dt.year == year)
        mean_fut = year_fut.mean(dim = 'time', skipna = True)
        means_fut.append(mean_fut)
    combine_means_fut = bp.xr.concat(means_fut, dim = 'year')
    overall_mean_fut = combine_means_fut.mean(dim = 'year')
    
    if variable == 'psl':
        overall_mean_fut = overall_mean_fut * 0.01 #convert from Pa to hPa
    else:
        overall_mean_fut = overall_mean_fut

    return overall_mean_fut

# list of all variables run for fut_mean
#vas wind vector combine wet model data
models = ['UKESM1-0-LL', 'ACCESS-CM2', 'CanESM5', 'KACE-1-0-G']
data = []
for i, model in enumerate(models):
    get = fut_mean(models[i], 'vas', interpolate = True)
    data.append(get)

combine = bp.xr.concat(data, dim = 'model')
average_vas = combine.mean(skipna = True, dim = 'model')

#uas wind vector combine wet model data
models = ['UKESM1-0-LL', 'ACCESS-CM2', 'CanESM5', 'KACE-1-0-G']
data = []
for i, model in enumerate(models):
    get = fut_mean(models[i], 'uas', interpolate = True)
    data.append(get)

combine = bp.xr.concat(data, dim = 'model')
average_uas = combine.mean(skipna = True, dim = 'model')

#sea level pressure combine wet model data
models = ['UKESM1-0-LL', 'ACCESS-CM2', 'CanESM5', 'KACE-1-0-G']
data = []
for i, model in enumerate(models):
    get = fut_mean(models[i], 'psl', interpolate = True)
    data.append(get)

combine = bp.xr.concat(data, dim = 'model')
average_psl = combine.mean(skipna = True, dim = 'model')

#geopotential height combine wet model data
models = ['UKESM1-0-LL', 'ACCESS-CM2', 'CanESM5', 'KACE-1-0-G']
data = []
for i, model in enumerate(models):
    get = fut_mean(models[i], 'zg', interpolate = True)
    get = get.drop_vars('plev')
    data.append(get)
    
combine = bp.xr.concat(data, dim = 'model')
average_zg = combine.mean(skipna = True, dim = 'model')



# function to calculate the change in a variable from 1979-2014 to 2070-2099 as a difference (precipitation is calculated as a percent change)
def anomaly(model_name, variable, interpolate = False):
    fpath = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/intake_esgf/ERA5/{variable}/{variable}_Amon_'
    # open seperate datasets for comparison
    open_hist = bp.xr.open_mfdataset(fpath + model_name + '_hist*.nc', engine = 'netcdf4')
    open_fut = bp.xr.open_mfdataset(fpath + model_name + '_ssp*.nc', engine = 'netcdf4')
    
    # geopotential height has an extra dimension for what pressure level you want to look at (we chose 500 hPa)
    if variable == 'zg':
        open_fut = open_fut.sel(plev=50000, method = 'nearest')
        open_hist = open_hist.sel(plev=50000, method = 'nearest')

    if interpolate == True:
        # interploate data to fit on the same gridpoints (required when averaging over models on different grids)
        ds_out = bp.xr.Dataset(
            {
                "lat": (["lat"], bp.np.arange(15.62, 51.88, 1.25)),
                "lon": (["lon"], bp.np.arange(216.5625, 295.275, 1.875)),
            }
        )

        regridder_hist = bp.xe.Regridder(open_hist, ds_out, 'bilinear')
        regridder_fut = bp.xe.Regridder(open_fut, ds_out, 'bilinear')
        open_fut = regridder_fut(open_fut)
        open_hist = regridder_hist(open_hist)
        
    
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
   
    # precipitation is the only anomaly measured as a percent change
    if variable == 'pr':
        anomaly = ((overall_mean_fut - overall_mean_hist) / overall_mean_hist) * 100
    else:
        anomaly = overall_mean_fut - overall_mean_hist
        
    return anomaly

# list of all varibales run for anomaly
# anomaly for precipitation combined across all wet models
models = ['UKESM1-0-LL', 'ACCESS-CM2', 'CanESM5', 'KACE-1-0-G']
data = []
for i, model in enumerate(models):
    get = anomaly(models[i], 'pr', interpolate = True)
    data.append(get)

combine = bp.xr.concat(data, dim = 'model')
anom_pr = combine.mean(skipna = True, dim = 'model')

# anomaly for eastward near surface wind combined across all wet models
models = ['UKESM1-0-LL', 'ACCESS-CM2', 'CanESM5', 'KACE-1-0-G']
data = []
for i, model in enumerate(models):
    get = anomaly(models[i], 'uas', interpolate = True)
    data.append(get)

combine = bp.xr.concat(data, dim = 'model')
anom_uas = combine.mean(skipna = True, dim = 'model')

# anomaly for northward near surface wind combined across all wet models
models = ['UKESM1-0-LL', 'ACCESS-CM2', 'CanESM5', 'KACE-1-0-G']
data = []
for i, model in enumerate(models):
    get = anomaly(models[i], 'vas', interpolate = True)
    data.append(get)

combine = bp.xr.concat(data, dim = 'model')
anom_vas = combine.mean(skipna = True, dim = 'model')

# anomaly for sea level pressure combined across all wet models
models = ['UKESM1-0-LL', 'ACCESS-CM2', 'CanESM5', 'KACE-1-0-G']
data = []
for i, model in enumerate(models):
    get = anomaly(models[i], 'psl', interpolate = True)
    data.append(get)

combine = bp.xr.concat(data, dim = 'model')
anom_psl = combine.mean(skipna = True, dim = 'model')


# adjusted function to map anomaly of mean data from averaging over multiple models
def map_anomalies(anomaly_ref, data, variable, udata = None, vdata = None, interpolate = False, quiver = False, step = 1):
    # data = anomaly_ref(model_name, variable)
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
    else:
        plot_dict = {'cmap_a' : bp.cmap.cmap('cmp_b2r'),
                     'cmap_m' : bp.cmap.cmap('amwg256'),
                     'title': 'Test Variable',
                     'cbar_a' : 'Default Measurement',
                     'cbar_m' : 'Default Measurement'
                     }
        
    # setup map
    fig = bp.plt.figure()
    ax = bp.plt.axes(projection  = bp.ccrs.PlateCarree())
    
    # set the color transition to happen at 0
    data_min = data.values.min()
    data_max = data.values.max()

    if data_min < 0.00 < data_max:
        norm = bp.mcolors.TwoSlopeNorm(vmin=data_min, vcenter=0.00, vmax=data_max)
    else:
        norm = bp.mcolors.Normalize(vmin=data_min, vmax=data_max)

    # create outline of map based on mean values or anomalies
    if anomaly_ref.__name__ == 'fut_mean':
        contour = ax.contourf(data['lon'], data['lat'], data.values, cmap = plot_dict['cmap_m'], transform = bp.ccrs.PlateCarree(), levels = 20, norm = norm)
        ax.set_title(f'Wet Models ssp585\nMean {plot_dict['title']}\n2070-2099', fontsize = 18)
        cbar = bp.plt.colorbar(contour, orientation = 'horizontal', pad = 0.03, aspect = 50, shrink = 0.85)
        cbar.set_label(plot_dict['cbar_m'], fontsize = 10)
    elif anomaly_ref.__name__ == 'hist_mean':
        contour = ax.contourf(data['lon'], data['lat'], data.values, cmap = plot_dict['cmap_m'], transform = bp.ccrs.PlateCarree(), levels = 20, norm = norm)
        ax.set_title(f'Wet Models\nMean {plot_dict['title']}\n1985-2014', fontsize = 18)
        cbar = bp.plt.colorbar(contour, orientation = 'horizontal', pad = 0.03, aspect = 50, shrink = 0.85)
        cbar.set_label(plot_dict['cbar_m'], fontsize = 10)
    else:
        contour = ax.contourf(data['lon'], data['lat'], data.values, cmap = plot_dict['cmap_a'], transform = bp.ccrs.PlateCarree(), levels = 20, norm = norm)
        ax.set_title(f'Wet Models ssp585\n{plot_dict['title']} Anomaly\n2070-2099 vs 1985-2014', fontsize = 18)
        cbar = bp.plt.colorbar(contour, orientation = 'horizontal', pad = 0.03, aspect = 50, shrink = 0.85)
        cbar.set_label(plot_dict['cbar_a'], fontsize = 10)
        cbar.ax.xaxis.set_major_formatter(bp.ticker.FormatStrFormatter('%.0f'))
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
    save_name = f'Wet_Models_{anomaly_ref.__name__}_{data.name}.png'
    if quiver == True:
        save_name = f'Wet_Models_{anomaly_ref.__name__}_{data.name}_quiver.png'
        
        # slice uas and vas data
        if  anomaly_ref.__name__ == 'anomaly':
            u = anom_uas
            v = anom_vas
            scale = 20
        else:
            u = average_uas
            v = average_vas
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

            # the entire dataset can be processed at once
            u = regridder_u(u)
            v = regridder_v(v)
       
        # allow to skip values
        lat = u['lat'][::step]
        lon = u['lon'][::step]
        X, Y = bp.np.meshgrid(lon, lat)
        uu = bp.np.array(u[::step,::step])
        vv = bp.np.array(v[::step,::step])

        quiv = ax.quiver(X, Y, uu, vv,
                    pivot = 'tail',
                    width = 0.0015,
                    scale = scale, 
                    headwidth = 6,
                    color = 'k',
                    transform = bp.ccrs.PlateCarree())
    
    # save path for files
    save_path = '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSL_Climate/poster/'
    save_path  = bp.os.path.join(save_path, save_name)
    
    bp.plt.savefig(save_path, dpi = 400)
    bp.plt.show()   
    
    return fig, ax

#example of using  map_anomalies function to map the anomaly of sea level pressure with wind vectors overlayed 
map_anomalies(anomaly, anom_pr, 'pr')


