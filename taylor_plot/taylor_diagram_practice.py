#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 10 12:59:57 2025

@author: u1301408
"""

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/packages')
import base_packages as bp

# evaluation of historical efficieny from 1979-2014 using an adpated version of a taylor diagram

# standard deviation : MACA
# correlation : MACA
# bias : GCM (shown on colorscale)


# list of all models used in the MACA downscaling process
MACA_models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5', 'EC-Earth3-AerChem', 'EC-Earth3-CC',
 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'IITM-ESM', 'INM-CM4-8', 'INM-CM5-0',
 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC-ES2L', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']
    
# list of models that we currently have pr GCM data downloaded for
GCM_models = ['KACE-1-0-G', 'CanESM5', 'UKESM1-0-LL', 'ACCESS-CM2', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'MPI-ESM1-2-LR']

# find the variable average for every grid point across the historical period before doing calculations
# same averaging can be used for standard deviation and correlation
# learn how to read GCM data out of matlab files
# make taylor plot repeatable for different variables


#%%
def matlab_to_netcdf(model, variable):
    
    # convert matlab file to netcdf
    matlab_file = bp.scipy.io.loadmat(f'/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/coarse_grid/{model}_historical_{variable}.mat')
    
    # Suppose you have lat, lon, time, and var in your file:
    lat = bp.np.squeeze(matlab_file['lat'])
    lon = bp.np.squeeze(matlab_file['lon'])
    var = bp.np.squeeze(matlab_file['interpolated_data'])  # shape: (time, lat, lon), check and reshape if necessary

    years = bp.np.arange(1979, 2015)                 # 36 years
    # days_per_year = 365                           # change to 366 if all leap years
    year_full = []
    day_full = []
    for year in years:
        max_day = 366 if bp.calendar.isleap(year) else 365
        for day in range(1, max_day + 1):
            year_full.append(year)
            day_full.append(day)
    year_full = bp.np.array(year_full)
    day_full = bp.np.array(day_full)

    time = bp.pd.to_datetime({'year' : year_full, 'month' : 1, 'day' : 1}) + bp.pd.to_timedelta(day_full - 1, unit = 'D')
    
    # Create an xarray DataArray (or Dataset for multiple variables)
    ds = bp.xr.DataArray(
        var,
        coords = {'time': time, 'lat': lat, 'lon': lon},
        dims = (variable, 'time', 'lat', 'lon'),
        name = variable
    )
    
    # Save to NetCDF
    ds.to_netcdf(f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/taylor_plot/GCM_data/{model}_historical_{variable}.nc')
    
    return ds


#%%
# read out the dictionary from the .txt file
import ast

# Open and read the file
with open("taylor_dict_framework.txt", "r") as f:
    contents = f.read()

# Convert from string representation to actual dictionary
base_dict = ast.literal_eval(contents)


def st_dev_MACA(model, variable, dictionary):
    """
    First average data across the time dimension and then
    calculate the spatial standard deviaton.
    """
    
    ds = bp.xr.open_dataset(f'/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/output/netcdf/macav2metdata_GSLBIP_{model}_ssp585_{variable}.nc')
    time_average = ds.mean(skipna = True, dim = 'time')
    
    st_dev = time_average.std(dim = ['lat', 'lon'])
    
    dictionary[model]['std'][variable] = st_dev
    
    return st_dev

for model in MACA_models[-3:]:
    st_dev_MACA(model, 'pr', base_dict)
    
print(base_dict)
#%%
def st_dev_obs(variable):
    """
    Averages observational data over the time dimension and then 
    calculates thee spatial standard deviation. Note that tasmin 
    is tmmin and tasmax is tmmax for observational data. 
    """
    
    ds = bp.xr.open_dataset(f'/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/gridmet/gsl_region_{variable}_1979-2014.nc')
    time_average = ds.mean(skipna = True, dim = 'day')
    
    st_dev = time_average.std(dim = ['lat', 'lon'])
    
    return st_dev


def corr_coef(model, variable):
    """
    Calulate the spatial correlation coefficient using the model
    and observational data. 
    """
    # average model data across time
    ds_MACA = bp.xr.open_dataset(f'/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/output/netcdf/macav2metdata_GSLBIP_{model}_ssp585_{variable}.nc')
    time_average_MACA = ds_MACA.mean(skipna = True, dim = 'time')
    MACA_data = time_average_MACA[variable].values.flatten()
    
    # convert varibale name for observational data
    if variable == 'tasmin':
        variable = 'tmmin'
    elif variable == 'tasmax':
        variable = 'tmmin'
        
    # average observational data across time
    ds_obs = bp.xr.open_dataset(f'/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/gridmet/gsl_region_{variable}_1979-2014.nc')
    time_average_obs = ds_obs.mean(skipna = True, dim = 'day')
    
    if variable == 'pr':
        variable ='precipitation_amount'
        
    obs_data = time_average_obs[variable].values.flatten()
    
    # correlation coefficient calculation
    corr_coef = bp.np.corrcoef(MACA_data, obs_data)[0,1] # selects the right correlation coefficient out of an array
    
    return float(corr_coef)
    
corr_coef(MACA_models[0], 'pr')



# lat      (lat) float32 672B 36.03 36.07 36.11 36.15 ... 42.9 42.94 42.98
# * lon      (lon) float32 684B -115.1 -115.1 -115.0 ... -108.1 -108.1 -108.0

# PolarAxes.PolarTransform() # this tells plot to set std for radius and cor for angle
# diagram = TaylorDiagram(reference.std(ddof=1), fig=myfig)
# diagram.add_sample(stddev2, corrcoef2, label = 'Model 2', marker = 'o')

#%%

ds = bp.scipy.io.loadmat('/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/coarse_grid/ACCESS-CM2_historical_pr.mat')

var = bp.np.squeeze(ds['interpolated_data'])
# year = bp.np.squeeze(ds['year'])

print(var.shape)
# print(day_of_year.shape)


#%%
# list of models to add to framework including obs
models = [
    'ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1',
    'CanESM5', 'EC-Earth3-AerChem', 'EC-Earth3-CC', 'EC-Earth3-Veg-LR', 'EC-Earth3',
    'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'IITM-ESM', 'INM-CM4-8',
    'INM-CM5-0', 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC-ES2L', 'MIROC6',
    'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL', 'Obs'
]

# variables used in MACA
variables = ['pr', 'huss', 'tasmin', 'tasmax', 'rsds', 'uas', 'vas']

# loop through model dictionary framework to add all models and variables with a placeholder for each value
model_dict = {
    model: {
        'std': {var: 'x' for var in variables},
        'corrcoef':  {var: 'x' for var in variables},
        'bias': {var: 'x' for var in variables}
    }
    for model in models
}

# save the dictionary to a specified file
printer = bp.pprint.PrettyPrinter(indent = 3, width = 100, sort_dicts = True)
bp.os.chdir('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/taylor_plot/')

with open('taylor_dict_framework.txt', 'w') as f:
    f.write(printer.pformat(model_dict))

# bp.pprint.pprint(model_dict)





