#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 10 13:13:16 2025

@author: u1301408
"""

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSL_Climate/packages/')
import base_packages as bp

# Define the shapefile path (where to find coordinates used by VIC from Maribeth)
bdir = '/uufs/chpc.utah.edu/common/home/u0660911/Documents/projects/gslbip/'
shapefile_path = bp.os.path.join(bdir,'GSLBIP_shpfiles/MF6_VIC_bounding_box/MF6_VIC_bounding_box.shp')

#VIC boundary coordinates
gdf = bp.gpd.read_file(shapefile_path)
gdf = gdf.to_crs("EPSG:4326")
min_lon, min_lat, max_lon, max_lat = gdf.total_bounds

def convert_lon_to_0_360(lon):
    # Convert longitude from -180-180 to 0-360
    lon = bp.np.array(lon)
    lon_360 = (lon + 360) % 360
    return lon_360

def gridmet_mean(variable):
    data = []
    if variable == 'pr':
        gridmet_fpath = '/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/gridmet/gsl_region_pr_1979-2024.nc'
        gridmet = bp.xr.open_dataset(gridmet_fpath)
        gridmet = gridmet['precipitation_amount'].sel(lat = slice(max_lat, min_lat), lon = slice(min_lon, max_lon))
        for year in range(1979, 2015):
            for month in range(6, 9):
                dat = gridmet.sel(day = (gridmet.day.dt.month == month) & (gridmet.day.dt.year == year))
                dat_mean = dat.mean(skipna = True)
                data.append([f'{month}/{year}', float(dat_mean)])
        obs = gridmet.sel(day = gridmet.day.dt.month.isin([6,7,8]))
        mean_obs = obs.mean(skipna = True)    
        
    elif variable == 'tas':
        #min precipitation data
        gridmet_fpath_min = '/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/gridmet/gsl_region_tmmn_1979-2024.nc'
        gridmet_min = bp.xr.open_dataset(gridmet_fpath_min)
        gridmet_min = gridmet_min['air_temperature'].sel(lat = slice(max_lat, min_lat), lon = slice(min_lon, max_lon))
        
        #max precipitation data
        gridmet_fpath_max = '/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/gridmet/gsl_region_tmmx_1979-2024.nc'
        gridmet_max = bp.xr.open_dataset(gridmet_fpath_max)
        gridmet_max = gridmet_max['air_temperature'].sel(lat = slice(max_lat, min_lat), lon = slice(convert_lon_to_0_360(min_lon), convert_lon_to_0_360(max_lon)))
       
        for year in range(1979, 2015):
            for month in range(6, 9):
                dat_min = gridmet_min.sel(day = (gridmet_min.day.dt.month == month) & (gridmet_min.day.dt.year == year))
                dat_mean_min = dat_min.mean(skipna = True)
                
                dat_max = gridmet_min.sel(day = (gridmet_max.day.dt.month == month) & (gridmet_max.day.dt.year == year))
                dat_mean_max = dat_max.mean(skipna = True)
                
                combined_mean = bp.xr.concat([dat_mean_max, dat_mean_min], dim = 'M')
                dat_mean = combined_mean.mean(dim = 'M', skipna = True)
                
                data.append([f'{month}/{year}', float(dat_mean)])
                
        obs_min = gridmet_min.sel(day = gridmet_min.day.dt.month.isin([6,7,8]))
        obs_max = gridmet_max.sel(day = gridmet_max.day.dt.month.isin([6,7,8]))
        combined_mean = bp.xr.concat([obs_max, obs_min], dim = 'M')
        mean_obs = obs.mean(dim = 'M', skipna = True) 
    
    return data
# , f'Mean of dataset : {float(mean_obs)}'

def mean_JJA(model_name, variable):
    #open historical dataset for model
    fpath = fpath = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/intake_esgf/ERA5/{variable}/{variable}_Amon_'
    open_hist = bp.xr.open_mfdataset(fpath + model_name + '_hist*.nc')

    ds = open_hist[variable].sel(lat = 41.198394, lon = 247.85635489, method = 'nearest')    
    data = []
    
    for year in range(1979, 2015):
        for month in range(6, 9):
            dat = ds.sel(time = (ds.time.dt.month == month) & (ds.time.dt.year == year))
            data.append([f'{month}/{year}', float(dat)])
    model = ds.sel(time = ds.time.dt.month.isin([6,7,8]))
    mean_model = model.mean(skipna = True)    
    
    return data
# , f'Mean of dataset : {float(mean_model.values)}'

def var(model_name, variable):
    if model_name == 'gridmet':
        data = []
        if variable == 'tas':
            gridmet_fpath_min = '/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/gridmet/gsl_region_tmmn_1979-2024.nc'
            gridmet_min = bp.xr.open_dataset(gridmet_fpath_min)
            gridmet_min = gridmet_min['air_temperature'].sel(lat = 41.198394, lon = 247.85635489, method = 'nearest')
           
            gridmet_fpath_max = '/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/gridmet/gsl_region_tmmx_1979-2024.nc'
            gridmet_max = bp.xr.open_dataset(gridmet_fpath_max)
            gridmet_max = gridmet_max['air_temperature'].sel(lat = 41.198394, lon = 247.85635489, method = 'nearest')
            
            for year in range(1979, 2015):
                dat_min = gridmet_min.sel(day = (gridmet_min.day.dt.month.isin([6, 7, 8])) & (gridmet_min.day.dt.year == year))
                dat_mean_min = dat_min.mean(skipna = True)
                
                dat_max = gridmet_min.sel(day = (gridmet_max.day.dt.month.isin([6, 7, 8])) & (gridmet_max.day.dt.year == year))
                dat_mean_max = dat_max.mean(skipna = True)
                
                combined_mean = bp.xr.concat([dat_mean_max, dat_mean_min], dim = 'M')
                dat_mean = combined_mean.mean(dim = 'M', skipna = True)
                data.append(float(dat_mean)) 
        
        else:
            gridmet_fpath = '/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/gridmet/gsl_region_pr_1979-2024.nc'
            gridmet = bp.xr.open_dataset(gridmet_fpath)
            gridmet = gridmet['precipitation_amount'].sel(lat = 41.198394, lon = 247.85635489, method = 'nearest')
            
            for year in range(1979, 2015):
                dat = gridmet.sel(day = (gridmet.day.dt.month.isin([6, 7, 8])) & (gridmet.day.dt.year == year))
                dat_mean = dat.mean(skipna = True)
                data.append(float(dat_mean))                   
    else:
        fpath = fpath = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/intake_esgf/ERA5/{variable}/{variable}_Amon_'
        open_hist = bp.xr.open_mfdataset(fpath + model_name + '_hist*.nc')
        ds = open_hist[variable].sel(lat = 41.198394, lon = 247.85635489, method = 'nearest') 
        ds = ds.sel(time = (ds.time.dt.month.isin([6, 7, 8])) & (ds.time.dt.year.isin(range(1979, 2015))))
        ds_mean = ds.mean(skipna = True)
        
        if variable == 'pr':
            days_in_month = data.time.dt.days_in_month
            seconds_per_month = days_in_month * 24 * 60 * 60
            summer_precip = float((data * seconds_per_month).mean())
            data.append(summer_precip)
        else:
            ds = (ds.sel(time = (ds.time.dt.month.isin([6, 7, 8])) & (ds.time.dt.year.isin(range(1979, 2015))))).values
            for item in list(ds):
                data.append(float(item))
                
    var = bp.np.var(data, ddof = 1) 
    
    return float(var)


    
models = ['UKESM1-0-LL', 'ACCESS-CM2', 'CanESM5', 'KACE-1-0-G', 'MPI-ESM1-2-LR', 'CNRM-ESM2-1', 'CNRM-CM6-1-HR', 'INM-CM4-8']
biases =[]
obs = var('gridmet', 'pr')
for model in models:
    mod = var(model, 'pr')
    bias = mod / obs
    biases.appen([model, bias])
    
#%%
data = []
model_name = 'CanESM5'
variable = 'pr'
fpath = fpath = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/intake_esgf/ERA5/{variable}/{variable}_Amon_'
open_hist = bp.xr.open_mfdataset(fpath + model_name + '_hist*.nc')
ds = open_hist[variable].sel(lat = 41.198394, lon = 247.85635489, method = 'nearest') 
ds = ds.sel(time = (ds.time.dt.month.isin([6, 7, 8])) & (ds.time.dt.year.isin(range(1979, 2015))))
# ds_mean = ds.mean(skipna = True)

if variable == 'pr':
    days_in_month = ds.time.dt.days_in_month
    seconds_per_month = days_in_month * 24 * 60 * 60
    summer_precip = float((ds * seconds_per_month).mean())
    data.append(summer_precip)
# else:
#     ds = (ds.sel(time = (ds.time.dt.month.isin([6, 7, 8])) & (ds.time.dt.year.isin(range(1979, 2015))))).values
#     for item in list(ds):
#         data.append(float(item))

#%%
#mean precip bias
for model in models:
    mod = mean_JJA(model, 'pr')
    obs = gridmet_mean('pr')
    for mod_item, obs_item in zip(mod, obs):
        monthly_mean_mod = mod_item[1]
        monthly_mean_obs = obs_item[1]
        bias = monthly_mean_mod / monthly_mean_obs
        biases.append([model, mod_item[0], bias])
    

#%%

obs = var('gridmet', 'pr')
for model in models:
    var_mod = var(model, 'pr')
    var_obs = var('gridmet', 'pr')
    bias = var_mod / var_obs
    biases.append([model, bias])

# all_models =  ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5', 'EC-Earth3-AerChem', 'EC-Earth3-CC',
#   'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'IITM-ESM', 'INM-CM4-8', 'INM-CM5-0',
#   'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC-ES2L', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']

#%%
import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSL_Climate/packages/')
import base_packages as bp

# Define the shapefile path (where to find coordinates used by VIC from Maribeth)
bdir = '/uufs/chpc.utah.edu/common/home/u0660911/Documents/projects/gslbip/'
shapefile_path = bp.os.path.join(bdir,'GSLBIP_shpfiles/MF6_VIC_bounding_box/MF6_VIC_bounding_box.shp')

#VIC boundary coordinates
gdf = bp.gpd.read_file(shapefile_path)
gdf = gdf.to_crs("EPSG:4326")
min_lon, min_lat, max_lon, max_lat = gdf.total_bounds

#mean of each year
def gridmet_mean_yr(variable):
    data = []
    if variable == 'pr':
        gridmet_fpath = '/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/gridmet/gsl_region_pr_1979-2024.nc'
        gridmet = bp.xr.open_dataset(gridmet_fpath)
        gridmet = gridmet['precipitation_amount'].sel(lat = slice(max_lat, min_lat), lon = slice(min_lon, max_lon))
        for year in range(1979, 2015):
            dat = gridmet.sel(day = (gridmet.day.dt.month.isin([6, 7, 8])) & (gridmet.day.dt.year == year))
            dat_mean = dat.mean(skipna = True)
            data.append(float(dat_mean))   
        
    elif variable == 'tas':
        #min precipitation data
        gridmet_fpath_min = '/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/gridmet/gsl_region_tmmn_1979-2024.nc'
        gridmet_min = bp.xr.open_dataset(gridmet_fpath_min)
        gridmet_min = gridmet_min['air_temperature'].sel(lat = slice(max_lat, min_lat), lon = slice(min_lon, max_lon))
        
        #max precipitation data
        gridmet_fpath_max = '/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/gridmet/gsl_region_tmmx_1979-2024.nc'
        gridmet_max = bp.xr.open_dataset(gridmet_fpath_max)
        gridmet_max = gridmet_max['air_temperature'].sel(lat = slice(max_lat, min_lat), lon = slice(convert_lon_to_0_360(min_lon), convert_lon_to_0_360(max_lon)))
       
        for year in range(1979, 2015):
            for month in range(6, 9):
                dat_min = gridmet_min.sel(day = (gridmet_min.day.dt.month.isin([6, 7, 8])) & (gridmet_min.day.dt.year == year))
                dat_mean_min = dat_min.mean(skipna = True)
                
                dat_max = gridmet_min.sel(day = (gridmet_max.day.dt.month.isin([6, 7, 8])) & (gridmet_max.day.dt.year == year))
                dat_mean_max = dat_max.mean(skipna = True)
                
                combined_mean = bp.xr.concat([dat_mean_max, dat_mean_min], dim = 'M')
                dat_mean = combined_mean.mean(dim = 'M', skipna = True)
                
                data.append(float(dat_mean)) 
    return data

def mean_JJA_yr(model_name, variable):
    #open historical dataset for model
    fpath = fpath = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/intake_esgf/ERA5/{variable}/{variable}_Amon_'
    open_hist = bp.xr.open_mfdataset(fpath + model_name + '_hist*.nc')

    ds = open_hist[variable].sel(lat = 41.198394, lon = 247.85635489, method = 'nearest')    
    data = []
    
    for year in range(1979, 2015):
        # Select all JJA months for this year
        dat = ds.sel(time=(ds.time.dt.month.isin([6, 7, 8])) & (ds.time.dt.year == year), drop=True)

        days_in_month = dat.time.dt.days_in_month
        seconds_per_month = days_in_month * 24 * 60 * 60
        summer_precip = float((dat * seconds_per_month).mean())

        data.append(summer_precip)
                   
    return data

def heat_map_bias(bias_matrix):
    models = ['UKESM1-0-LL', 'ACCESS-CM2', 'CanESM5', 'KACE-1-0-G', 'MPI-ESM1-2-LR', 'CNRM-ESM2-1', 'CNRM-CM6-1-HR', 'INM-CM4-8']
    years = bp.np.arange(1979, 2015)

    fig, ax = bp.plt.subplots(figsize=(15, 5))

    bias_array = bp.np.array(bias_matrix)
    vmin = float(bp.np.min(bias_array))
    vmax = float(bp.np.max(bias_array))

    # Create the heatmap
    cax = ax.imshow(bias_matrix, aspect='auto', cmap='bwr', vmin = vmin, vmax = vmax, interpolation='nearest')
    # Optionally: cmap='coolwarm', set vmin/vmax to keep white near bias=1

    # Add colorbar
    cb = fig.colorbar(cax, orientation='vertical')
    cb.set_label('Bias (JJA Mean Model - JJA Mean Obs)')

    # Set axis labels and ticks
    ax.set_yticks(bp.np.arange(len(models)))
    ax.set_yticklabels(models)
    ax.set_xticks(bp.np.arange(0, len(years), 2))
    ax.set_xticklabels(years[::2])
    ax.set_xlabel('Year')
    ax.set_ylabel('Model')
    ax.set_title('Summer Temperature Bias (GCM vs Grid Met)')

    # plt.tight_layout()
    bp.plt.show()

bias_matrix = []
models = ['UKESM1-0-LL', 'ACCESS-CM2', 'CanESM5', 'KACE-1-0-G', 'MPI-ESM1-2-LR', 'CNRM-ESM2-1', 'CNRM-CM6-1-HR', 'INM-CM4-8']
for model in models:
    biases = []
    model_dat = mean_JJA_yr(model, 'tas')
    obs_dat = gridmet_mean_yr('tas')
    for mod, obs in zip(model_dat, obs_dat):
        bias = mod - obs
        biases.append(bias)
    bias_matrix.append(biases)

heat_map_bias(bias_matrix)

#%%
bias_matrix = []
models = ['UKESM1-0-LL', 'ACCESS-CM2', 'CanESM5', 'KACE-1-0-G', 'MPI-ESM1-2-LR', 'CNRM-ESM2-1', 'CNRM-CM6-1-HR', 'INM-CM4-8']
for model in models:
    biases = []
    model_dat = mean_JJA_yr(model, 'pr')
    obs_dat = gridmet_mean_yr('pr')
    for mod, obs in zip(model_dat, obs_dat):
        bias = mod / obs
        biases.append(bias)
    bias_matrix.append(biases)

heat_map_bias(bias_matrix)
#%%
model_name = 'CNRM-CM6-1-HR'
variable = 'pr'
fpath = fpath = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/intake_esgf/ERA5/{variable}/{variable}_Amon_'
open_hist = bp.xr.open_mfdataset(fpath + model_name + '_hist*.nc')

ds = open_hist[variable].sel(lat = 41.198394, lon = 247.85635489, method = 'nearest')    
# data = []

# for year in range(1979, 2015):
#     for month in range(6, 9):
#         dat = ds.sel(time = (ds.time.dt.month.isin([6, 7, 8])) & (ds.time.dt.year == year))
#         dat = dat.mean(skipna = True)
#         data.append(float(dat))   

#%%
models = ['UKESM1-0-LL', 'ACCESS-CM2', 'CanESM5', 'KACE-1-0-G', 'MPI-ESM1-2-LR', 'CNRM-ESM2-1', 'CNRM-CM6-1-HR', 'INM-CM4-8']
biases = []
for model in models: 
    var_obs = var('gridmet', 'pr')
    var_model = var(model, 'pr')
    bias = mean_model / mean_obs
    biases.append([model, bias])


#%%
fpath = fpath = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/intake_esgf/ERA5/pr/pr_Amon_'
open_hist = bp.xr.open_mfdataset(fpath + 'INM-CM4-8' + '_hist*.nc') 

ds = open_hist['pr'].sel(lat = 41.198394, lon = 247.85635489, method = 'nearest')

gridmet_fpath = '/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/gridmet/gsl_region_pr_1979-2024.nc'
gridmet = bp.xr.open_dataset(gridmet_fpath)
gridmet = gridmet['precipitation_amount'].sel(lat = slice(max_lat, min_lat), lon = slice(min_lon, max_lon))

# data = []


# for year in range(1979, 2015):
#     for month in range(6, 9):
#         dat = ds.sel(time = (ds.time.dt.month == month) & (ds.time.dt.year == year))
#         data.append([f'{month}/{year}', float(dat)])
# model = ds.sel(time = ds.time.dt.month.isin([6,7,8]))
# mean_model = model.mean(skipna = True

# convert_lon_to_0_360(-112.1436451)
#%%

#bias calculation outputs

precip_var_ratio = [['UKESM1-0-LL', 1.056958314179215e-10],
                    ['ACCESS-CM2', 2.004468680920104e-10],
                    ['CanESM5', 3.9701592723427714e-11],
                    ['KACE-1-0-G', 4.733389226704712e-11],
                    ['MPI-ESM1-2-LR', 1.843664652979088e-10],
                    ['CNRM-ESM2-1', 6.232267841197376e-11],
                    ['CNRM-CM6-1-HR', 4.2023769013099805e-10],
                    ['INM-CM4-8', 1.8764931457169425e-10]]

# UKESM1-0-LL
precip_mean_ratio = [['6/1979', 1.72990525484771e-05],
                     ['7/1979', 6.254545524549549e-07],
                     ['8/1979', 8.618293199526015e-06],
                     ['6/1980', 8.751119327751449e-06],
                     ['7/1980', 8.32615751864595e-06],
                     ['8/1980', 3.0740246709218324e-06],
                     ['6/1981', 2.4923890306910445e-05],
                     ['7/1981', 1.6245090146648082e-05],
                     ['8/1981', 2.0349608715459838e-05],
                     ['6/1982', 1.02990966883575e-05],
                     ['7/1982', 5.248274708855974e-06],
                     ['8/1982', 7.76816255503232e-06],
                     ['6/1983', 5.660427571663724e-06],
                     ['7/1983', 2.0452785905537924e-06],
                     ['8/1983', 3.3099343411177137e-06],
                     ['6/1984', 2.554285847071047e-06],
                     ['7/1984', 4.108371553714374e-06],
                     ['8/1984', 8.443597518106027e-06],
                     ['6/1985', 3.32279875951039e-06],
                     ['7/1985', 7.941001300632654e-07],
                     ['8/1985', 1.883812119905476e-05],
                     ['6/1986', 2.6088141637775052e-06],
                     ['7/1986', 5.42366112222046e-06],
                     ['8/1986', 8.428286870526333e-06],
                     ['6/1987', 9.853706651720709e-06],
                     ['7/1987', 4.229838613134666e-06],
                     ['8/1987', 1.434755392866159e-05],
                     ['6/1988', 1.170476141049059e-05],
                     ['7/1988', 1.620837905814126e-05],
                     ['8/1988', 2.0686339090095004e-05],
                     ['6/1989', 3.902231879566482e-06],
                     ['7/1989', 1.8515634488866793e-06],
                     ['8/1989', 8.458378202820584e-06],
                     ['6/1990', 2.4708465079270307e-05],
                     ['7/1990', 1.7953105824785544e-06],
                     ['8/1990', 1.7161504996265068e-05],
                     ['6/1991', 5.618166804917227e-06],
                     ['7/1991', 4.73510701497337e-06],
                     ['8/1991', 9.004628721426533e-06],
                     ['6/1992', 1.3875672348401832e-05],
                     ['7/1992', 5.1956285391512015e-06],
                     ['8/1992', 1.8770465528339299e-06],
                     ['6/1993', 1.203985061099011e-05],
                     ['7/1993', 9.54689481860871e-06],
                     ['8/1993', 9.524689333771715e-06],
                     ['6/1994', 0.00015668947831792295],
                     ['7/1994', 2.8572576425105496e-05],
                     ['8/1994', 7.400690518508647e-06],
                     ['6/1995', 5.069715974034948e-06],
                     ['7/1995', 8.100405822446306e-06],
                     ['8/1995', 1.0639332102978208e-05],
                     ['6/1996', 2.375693689151836e-05],
                     ['7/1996', 8.17550243251779e-06],
                     ['8/1996', 5.831714132598183e-05],
                     ['6/1997', 5.518352526881165e-07],
                     ['7/1997', 1.073806238211737e-05],
                     ['8/1997', 2.0445049222897143e-05],
                     ['6/1998', 6.420981054194418e-06],
                     ['7/1998', 1.0600158057046569e-05],
                     ['8/1998', 1.0039298435613138e-05],
                     ['6/1999', 1.9785688105674915e-06],
                     ['7/1999', 9.795337300901597e-07],
                     ['8/1999', 3.4680745480626325e-06],
                     ['6/2000', 2.776317383205748e-05],
                     ['7/2000', 1.6110368207183446e-05],
                     ['8/2000', 6.37818203030944e-06],
                     ['6/2001', 1.6579320701892466e-05],
                     ['7/2001', 7.920849796084452e-07],
                     ['8/2001', 1.1584544020240121e-05],
                     ['6/2002', 2.9746405471030333e-05],
                     ['7/2002', 2.8452810594623357e-06],
                     ['8/2002', 6.636156345254539e-05],
                     ['6/2003', 2.8678387120765465e-06],
                     ['7/2003', 2.241452147427051e-06],
                     ['8/2003', 6.997419548331149e-06],
                     ['6/2004', 1.1111489078041177e-05],
                     ['7/2004', 1.7799904935702728e-05],
                     ['8/2004', 5.765135596546267e-06],
                     ['6/2005', 5.1353820387280175e-06],
                     ['7/2005', 8.988555479312383e-06],
                     ['8/2005', 5.9508817785731345e-06],
                     ['6/2006', 2.3547246308882453e-05],
                     ['7/2006', 1.6278528719775764e-05],
                     ['8/2006', 1.1031860136529923e-05],
                     ['6/2007', 4.466415849765351e-06],
                     ['7/2007', 1.9589924886755488e-05],
                     ['8/2007', 1.3573153221385383e-05],
                     ['6/2008', 5.234451848549027e-06],
                     ['7/2008', 1.1970284124720781e-05],
                     ['8/2008', 1.5773395470193725e-05],
                     ['6/2009', 1.0649077156608334e-06],
                     ['7/2009', 8.649280851240284e-06],
                     ['8/2009', 3.3947549055810724e-05],
                     ['6/2010', 7.499727444114282e-06],
                     ['7/2010', 8.05631971597719e-05],
                     ['8/2010', 1.8558790965370052e-05],
                     ['6/2011', 1.463418626322055e-05],
                     ['7/2011', 7.384114949846986e-07],
                     ['8/2011', 1.76966116374813e-05],
                     ['6/2012', 2.0364187159128538e-05],
                     ['7/2012', 6.3840190368493235e-06],
                     ['8/2012', 1.5054343812686534e-05],
                     ['6/2013', 0.0004008946645483431],
                     ['7/2013', 6.553625333160623e-06],
                     ['8/2013', 2.1008605448594874e-05],
                     ['6/2014', 7.320613957046997e-06],
                     ['7/2014', 1.9667463288740108e-05],
                     ['8/2014', 5.210683243206702e-06]]


temp_var_ratio = 

temp_mean_diff = 

#%%



#%%
#compare one model over time by month
import matplotlib.pyplot as plt
import numpy as np

# Example fake data
months = ['June', 'July', 'August']
years = np.arange(1979, 2015)
bias_matrix = np.random.uniform(0.5, 1.5, (len(models), len(years)))  # Replace with your real data

[1.72990525484771e-05, 8.751119327751449e-06, 2.4923890306910445e-05, 1.02990966883575e-05, 5.660427571663724e-06,
 2.554285847071047e-06, 3.32279875951039e-06, 2.6088141637775052e-06, 9.853706651720709e-06, 1.170476141049059e-05,
 3.902231879566482e-06, 2.4708465079270307e-05, 5.618166804917227e-06, 1.3875672348401832e-05, 1.203985061099011e-05,
 0.00015668947831792295, 5.069715974034948e-06, 2.375693689151836e-05, 5.518352526881165e-07, 6.420981054194418e-06, 
 1.9785688105674915e-06, 2.776317383205748e-05, 1.6579320701892466e-05],

 [6.254545524549549e-07, 8.32615751864595e-06, 1.6245090146648082e-05, 5.248274708855974e-06, 2.0452785905537924e-06,
  4.108371553714374e-06, 7.941001300632654e-0,  5.42366112222046e-06, 4.229838613134666e-06, 1.620837905814126e-05,
  1.8515634488866793e-06, 1.7953105824785544e-06, 4.73510701497337e-06, 5.1956285391512015e-06, 9.54689481860871e-06,
  2.8572576425105496e-05, 8.100405822446306e-06, 8.17550243251779e-06, 1.073806238211737e-05, 1.0600158057046569e-05,
  9.795337300901597e-07, 1.6110368207183446e-05, 7.920849796084452e-07],
 
 [8.618293199526015e-06, 3.0740246709218324e-06, 2.0349608715459838e-05, 7.76816255503232e-06, 3.3099343411177137e-06,
  8.443597518106027e-06, 1.883812119905476e-05, 8.428286870526333e-06, 1.434755392866159e-05, 2.0686339090095004e-05, 
  8.458378202820584e-06, 1.7161504996265068e-05, 9.004628721426533e-06, 1.8770465528339299e-06, 9.524689333771715e-06,
  7.400690518508647e-06, 1.0639332102978208e-05, 5.831714132598183e-05, 2.0445049222897143e-05, 1.0039298435613138e-05,
  3.4680745480626325e-06, 6.37818203030944e-06],
  ],
 ['8/2001', 1.1584544020240121e-05],
 ['6/2002', 2.9746405471030333e-05],
 ['7/2002', 2.8452810594623357e-06],
 ['8/2002', 6.636156345254539e-05],
 ['6/2003', 2.8678387120765465e-06],
 ['7/2003', 2.241452147427051e-06],
 ['8/2003', 6.997419548331149e-06],
 ['6/2004', 1.1111489078041177e-05],
 ['7/2004', 1.7799904935702728e-05],
 ['8/2004', 5.765135596546267e-06],
 ['6/2005', 5.1353820387280175e-06],
 ['7/2005', 8.988555479312383e-06],
 ['8/2005', 5.9508817785731345e-06],
 ['6/2006', 2.3547246308882453e-05],
 ['7/2006', 1.6278528719775764e-05],
 ['8/2006', 1.1031860136529923e-05],
 ['6/2007', 4.466415849765351e-06],
 ['7/2007', 1.9589924886755488e-05],
 ['8/2007', 1.3573153221385383e-05],
 ['6/2008', 5.234451848549027e-06],
 ['7/2008', 1.1970284124720781e-05],
 ['8/2008', 1.5773395470193725e-05],
 ['6/2009', 1.0649077156608334e-06],
 ['7/2009', 8.649280851240284e-06],
 ['8/2009', 3.3947549055810724e-05],
 ['6/2010', 7.499727444114282e-06],
 ['7/2010', 8.05631971597719e-05],
 ['8/2010', 1.8558790965370052e-05],
 ['6/2011', 1.463418626322055e-05],
 ['7/2011', 7.384114949846986e-07],
 ['8/2011', 1.76966116374813e-05],
 ['6/2012', 2.0364187159128538e-05],
 ['7/2012', 6.3840190368493235e-06],
 ['8/2012', 1.5054343812686534e-05],
 ['6/2013', 0.0004008946645483431],
 ['7/2013', 6.553625333160623e-06],
 ['8/2013', 2.1008605448594874e-05],
 ['6/2014', 7.320613957046997e-06],
 ['7/2014', 1.9667463288740108e-05],
 ['8/2014', 5.210683243206702e-06]]

fig, ax = plt.subplots(figsize=(15, 5))

# Create the heatmap
cax = ax.imshow(bias_matrix, aspect='auto', cmap='bwr', vmin=0.5, vmax=1.5, interpolation='nearest')
# Optionally: cmap='coolwarm', set vmin/vmax to keep white near bias=1

# Add colorbar
cb = fig.colorbar(cax, orientation='vertical')
cb.set_label('Bias (JJA Mean Model / JJA Mean Obs)')

# Set axis labels and ticks
ax.set_yticks(np.arange(len(models)))
ax.set_yticklabels(models)
ax.set_xticks(np.arange(0, len(years), 2))
ax.set_xticklabels(years[::2])
ax.set_xlabel('Year')
ax.set_ylabel('Model')
ax.set_title('Summer Precipitation Bias (GCM vs Grid Met)')

plt.tight_layout()
plt.show()


#%%

model_name = 'CanESM5'
variable = 'pr'
import xarray as xr
import numpy as np

# File path to historical data
fpath = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/intake_esgf/ERA5/{variable}/{variable}_Amon_'
open_hist = xr.open_mfdataset(fpath + model_name + '_hist*.nc')

# Select grid point nearest to specified lat/lon
ds = open_hist[variable].sel(lat=41.198394, lon=247.85635489, method='nearest')
data = []

for year in range(1979, 2015):
    # Select all JJA months for this year
    dat = ds.sel(time=(ds.time.dt.month.isin([6, 7, 8])) & (ds.time.dt.year == year), drop=True)

    days_in_month = dat.time.dt.days_in_month
    seconds_per_month = days_in_month * 24 * 60 * 60
    summer_precip = float((dat * seconds_per_month).mean())

    data.append(summer_precip)


