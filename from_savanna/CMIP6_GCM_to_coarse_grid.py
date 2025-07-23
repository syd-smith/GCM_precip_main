"""
Created: May 27th, 2024
By: Court Strong, court.strong@utah.edu

Edited: September 5th, 2024
By: Savanna Wolvin, s.wolvin@utah.edu


# SUMMARY
Intake the CMIP6 GCM variables and simulation experiements, coarsen to a 
1-degree horizontal grid, and save to a MATLAB file.


# DESCRIPTION
The CMIP6 GCM datasets have varying horizontal grid spacing, therefore these 
datasets are coarsened to consistent horizontal grid of 1-degree. Their 
horizontal grid spacing varies between native grids ('gn'), regridded variables 
to a specified grid for certain variables ('gr'), and any other target 
grid (e.g., 'g1'). The coarsening is done by SciPy's RegularGridInterpolator 
with a linear interpolation method to the desired coarse lat/lon. The newly 
interpolated variable is saved to a .mat file with its lat, lon, day of year, 
year, and units.


# INPUT
start_on_model ('str' or None):
    Define model to start processing from, based on the pkl file from 
    '{BASE_DIR}MACA/01_intake_esgf/catalogs/merged_catalog_updated.pkl'.
    If you want to start from the first model, set variable to None.
    
serial (Bool):
    To use serial processing (True) or parallel processing (False) when 
    coarsening the GCMs
    

# GLOBAL INPUTS FROM PARAMETERS.JSON
    BASE_DIR            -> Directory to all MACA script folders
    CACHE_DIR           -> Directory to the CMIP6 files
    GCM_VARIABLES       -> List of variables downloaded from CMIP6 - file names
    GCM_VAR_UNITS       -> Dictionary of GCM variable units
    COARSE_LAT_MIN      -> Minimum Coarse Latitude
    COARSE_LAT_MAX      -> Maximum Coarse Latitude
    COARSE_LON_MIN      -> Minimum Coarse Longitude
    COARSE_LON_MAX      -> Maximum Coarse Longitude
    COARSE_DIR          -> Directory to save the coarse grid data
    HISTORICAL_YEARS    -> List containing start year and end year of the CMIP6 
                            historical data
    FUTURE_YEARS        -> List containing start year and end year of the CMIP6
                            future SSP simulations
    

# OUTPUTS
    {COARSE_DIR}{source}_{ssp}_{var}.mat
        .mat files containing the coarsened GCM variable (var) per each model 
        ID (source) per each historical or future simulation experiment (ssp), 
        saved to the coarse directory.


"""
#%% Python libraries and variables

start_on_model  = None
serial          = True
max_cores       = None

import os
import multiprocessing
import cftime
import pandas as pd
import numpy as np
import scipy.io as sio
import intake_esgf
import xarray as xr
import glob
# from datetime import datetime, timedelta
from scipy.interpolate import RegularGridInterpolator
from concurrent.futures import ProcessPoolExecutor
# import matplotlib.pyplot as plt
# import cartopy.crs as ccrs
import xarray as xr
import datetime_type_conversion as dttc
import json

# Load in global parameters
with open(f'{os.path.dirname(__file__)}/PARAMETERS.json', 'r') as f:
    params = json.load(f)

BASE_DIR            = params['BASE_DIR']
CACHE_DIR           = params["CACHE_DIR"]
ESGF_CATALOG_NAME   = params["ESGF_CATALOG_NAME"]
GCM_VARIABLES       = params['GCM_VARIABLES']
GCM_VAR_UNITS       = params["GCM_VARIABLE_UNITS"]
COARSE_LAT          = np.arange(params["COARSE_LAT_MIN"], params["COARSE_LAT_MAX"]+1)
COARSE_LON          = np.arange(params["COARSE_LON_MIN"], params["COARSE_LON_MAX"]+1)
COARSE_DIR          = params["COARSE_DIR"]
HISTORICAL_YEARS    = params["HISTORICAL_YEARS"]
FUTURE_YEARS        = params["FUTURE_YEARS"]

# Meshgrid of coarse lat/lon values used in interpolation
COARSE_LON_MESH, COARSE_LAT_MESH = np.meshgrid(COARSE_LON, COARSE_LAT)


#%% Set the cache directory for intake-esgf

intake_esgf.conf.set(local_cache=CACHE_DIR)

print(f"Cache directory set to: {CACHE_DIR}")
print(f"Can write to cache directory: {os.access(CACHE_DIR, os.W_OK)}")


#%% 
"""
FUNCTION DEFINITION: inventory_and_source_paths  ** done    
    OUTPUT
    - inventory (DataFrame): Dataframe of available historical and ssp 
        simulations.
    - source_paths (dict): Dictionary of paths to models with sufficient 
        historical and SSP simulations.
"""
def inventory_and_source_paths():
    print("Load CMIP6 inventory...")
    inventory_file = os.path.join(
        BASE_DIR, f'MACA/01_intake_esgf/catalogs/{ESGF_CATALOG_NAME}.pkl')
    inventory = pd.read_pickle(inventory_file)
    
    # Check for historical and at least one ssp simulation
    subset_df = inventory[(inventory['historical'] == 1) & (
        inventory.drop('historical', axis=1) == 1).any(axis=1)]
    
    # Parse out inventory and determine if starting model is selected
    subset_df = inventory
    if start_on_model is not None:
        start_index = subset_df[subset_df['source_id']
                                == start_on_model].index[0] - 1
        subset_df = subset_df.iloc[start_index:]

    print("Generate source paths to CMIP6...")    
    source_paths = {} # variable to save file paths
    cmip6_base_dir = os.path.join(CACHE_DIR, 'CMIP6/CMIP/')

    # loop through model simulations of sufficient historical and SSP 
    # simulations, based on source ID and add path to list
    for source_id in subset_df['source_id'].unique():
        search_pattern = os.path.join(cmip6_base_dir, '**', source_id)
        matching_dirs = glob.glob(search_pattern, recursive=True)
        if matching_dirs: # if matching path found, save source path
            for match in matching_dirs:
                relative_path = os.path.relpath(match, cmip6_base_dir)
                source_paths[source_id] = relative_path
                break
    
    return subset_df, source_paths
    

#%%
"""
FUNCTION DEFINITION: create_consistent_datetimes
    INPUT
    - ds (xarray.Dataset): Dataset of specified CMIP6 model, variable, and 
            experiment
    - ssp (str): CMIP6 experiment name extracted from inventory
    
    OUTPUT
    - ds_subset (xarray.Dataset): Dataset of specified CMIP6 model, variable, 
            and experiment subsetted to start and end years
    - converted_times (pandas.DatetimeIndex): DatetimeIndex list of gregorian 
            datetimes to the xarray.Dataset 

"""
def create_consistent_datetimes(ds, ssp):
    # Return dtype of datetime coordinates
    calendar_type = type(ds['time'].values[0])
    
    # # Formulate datetime thresholds
    # if ssp == 'historical': start_year, end_year = HISTORICAL_YEARS[0], HISTORICAL_YEARS[1]+1
    # else: start_year, end_year = FUTURE_YEARS[0], FUTURE_YEARS[1]+1
    # start_date = calendar_type(start_year, 1, 1) if calendar_type != np.datetime64 else np.datetime64(f'{start_year}-01-01')
    # end_date = calendar_type(end_year, 1, 1) if calendar_type != np.datetime64 else np.datetime64(f'{end_year}-01-01')
    
    # VERSION 2 ###########################################################
    # Formulate datetime thresholds
    if ssp == 'historical': start_year, end_year = HISTORICAL_YEARS[0], HISTORICAL_YEARS[1]
    else: start_year, end_year = FUTURE_YEARS[0], FUTURE_YEARS[1]
    
    if calendar_type != np.datetime64:
        start_date = calendar_type(start_year, 1, 1, 0)
        if not isinstance(ds['time'].values[0], cftime.Datetime360Day):
            end_date = calendar_type(end_year, 12, 31, 23)
        else:
            end_date = calendar_type(end_year, 12, 30, 23)
    else:
        start_date = np.datetime64(f'{start_year}-01-01T00:00:00')
        end_date = np.datetime64(f'{end_year}-12-31T23:00:00')
    # start_date = calendar_type(start_year, 1, 1, 0) if calendar_type != np.datetime64 else np.datetime64(f'{start_year}-01-01T00:00:00')
    # end_date = calendar_type(end_year, 12, 31, 23) if calendar_type != np.datetime64 else np.datetime64(f'{end_year}-12-31T23:00:00')
    ########################################################################
    
    # Check if the exact end date exists in the time coordinates
    time_values = ds['time'].values
    if end_date not in time_values:
        # Find the nearest available date before the desired end date
        end_date = max(time for time in time_values if time <= end_date)
        print(f"Adjusted end date: {end_date}")
        
    # slice xarray to desired time slice
    ds_subset = ds.sel(time=slice(start_date, end_date)) 
    
    # Convert to pandas datetime if necessary
    time = ds_subset['time']

    # Convert the list of datetime objects to pandas datetime
    converted_times = dttc.convert_to_gregorian(time)
    
    return ds_subset, converted_times
    

#%%
"""
FUNCTION DEFINITION: load_dataset
    INPUT
    - ssp (str): CMIP6 experiment name extracted from inventory
    - var (str): GCM variable name of variable file
    - source (str): Source model name
    - source_paths (dict): Dictionary of paths to models with sufficient 
        historical and SSP simulations. 
    - tableid (str): Temporal resolution of dataset
    
    OUPUT (xarray.Dataset): Dataset of specified CMIP6 model, variable, and 
            experiment
"""
def load_dataset(ssp, var, source, source_paths, tableid='day'):
    print(f"Loading {source} {ssp} {var}...")
    
    # Locate path to source_id
    source_path = source_paths.get(source)
    if not source_path:
        raise ValueError(f"Source path for {source} not found in dictionary")

    # Determine Path to Model Experiment
    model_dir = os.path.join(CACHE_DIR, 'CMIP6/CMIP' if ssp ==
                            'historical' else 'CMIP6/ScenarioMIP', source_path)
    
    # Pattern to all files of Model Experiment and Variable
    # file_pattern = os.path.join(f'{model_dir}/{ssp}/????????/day/{var}/??/**', f'{var}_{tableid}_{source}_{ssp}_*.nc') 
    
    # List all netCDF files which fit the file pattern
    file_pattern = os.path.join(f'{model_dir}/{ssp}/**/day/{var}/??/**', f'{var}_{tableid}_{source}_{ssp}_*.nc') 
    nc_files = glob.glob(file_pattern, recursive=True)
    
    file_pattern = os.path.join(f'{model_dir}/{ssp}/**/day/{var}/???/**', f'{var}_{tableid}_{source}_{ssp}_*.nc') 
    nc_files += glob.glob(file_pattern, recursive=True)
    
    nc_files.sort()   
    
    # If variable not available for this model and experiment
    if len(nc_files) == 0:
        print(f"{source} {ssp} {var}. No files found. Continuing...")
        return None
    
    # Check that you are only pulling from one type of data grid
    split = np.array([nc_path.split('/') for nc_path in nc_files]) # split path strings
    grid_type = split[:, -3] # Pull grid labels
    if len(np.unique(grid_type)) > 1: # if there is more than one grid, remove least used
        count = pd.Series(split[:, -3]).value_counts()  # Count used grids
        grid_to_use = count.idxmax()                    # Pull most used grid
        nc_files = [nc_path for nc_path in nc_files if grid_to_use in nc_path]   

    # Open multifile datasets for entire experiment
    try:
        ds = xr.open_mfdataset(nc_files, combine='by_coords')
    except:
        ds = xr.open_mfdataset(nc_files, combine='by_coords', use_cftime=True)
    
    if ds[var].units != GCM_VAR_UNITS[var]:
          raise ValueError(f"Expected units {GCM_VAR_UNITS[var]}, found {ds[var].units}. Exiting.")
    
    return ds


#%%
"""
FUNCTION DEFINITION: to_coarse_grid
    INPUT
    - source (str): Source model name
    - ssp (str): CMIP6 experiment name extracted from inventory
    - var (str): GCM variable name of variable file
    - lock (parallel processor or None): 
    - source_paths (dict): Dictionary of paths to models with sufficient 
        historical and SSP simulations.
    
    OUTPUT
    - {COARSE_DIR}{source}_{ssp}_{var}.mat (.mat): MATLAB file dictionary 
            containing the interpolated data, coarse lat, coarse lon, day of 
            year, year, and units.
"""
def to_coarse_grid(source, ssp, var, lock, source_paths):
    print(f"Processing: {source} {ssp} {var} on PID {os.getpid()}")
    
    # Get dataset
    dataset = load_dataset(ssp, var, source, source_paths)
    
    # check if dataset was found
    if not dataset:
        return
    
    # Process datasets DateTime variable 
    dataset, time = create_consistent_datetimes(dataset, ssp)
    
    # Check if dataset contains all years
    # years = np.unique([datex.year for datex in dataset.time.values])
    years = np.unique([datex.year for datex in time])

    if ((years[1:-1] - years[0:-2]) > 1).any():
        print("Missing years within the dataset. Skipping")
        return
    
    # Extract day of year and year array
    dayOfYear = np.arange(1, np.max(time.dayofyear) + 1)
    years = np.arange(min(time.year), max(time.year) + 1)
    first_year = np.min(years)
    
    # Extract lat lon
    lat, lon = dataset['lat'].values, dataset['lon'].values
    
    # Convert the lon values to range from 0 -> 180 to -180 -> -1
    if np.any(lon > 180): 
        lon = ((lon + 180) % 360) - 180
    
    # Sort lat lon values so that Lat = [-90, 90], Lon = [-180, 180]
    lat_sorted_idx, lon_sorted_idx = np.argsort(lat), np.argsort(lon)
    lat_sorted, lon_sorted = lat[lat_sorted_idx], lon[lon_sorted_idx]
    
    # Initialize array to hold the coarse-interpolated data
    # interp_dataset = [lat x lon x DOY x year]
    interp_dataset = np.full((len(COARSE_LAT), len(COARSE_LON), 
                              len(dayOfYear), len(years)), 
                              np.nan)
    
    # Loop through all days, interpolate, and quality check
    for datex in range(len(dataset.time)):
        print(f'{source} {ssp} {var} {time[datex].year} {time[datex].dayofyear} {datex}')
        
        # Extract single day of data
        day_data = dataset.isel(time=datex)
        
        # Check for NaNs, skip if NaNs found
        if np.isnan(day_data[var].values).any():
            print(f'NaN found in GCM file at time index {datex}, skipping')
            return
        
        # Linearly interpolate from origrinal grid to coarse grid
        interpolator = RegularGridInterpolator((lat_sorted, lon_sorted), 
                                    day_data[var].values[lat_sorted_idx][:, lon_sorted_idx], 
                                    method='linear')
        interp_day = interpolator((COARSE_LAT_MESH, COARSE_LON_MESH))
        
        # For datasets of DatetimeNoLeap, the time[datex].dayofyear will report 
        # as #61 twice (i.e., it goes 58 59 61 61 61), due to leap day being 
        # skipped, to fix this indexing issue, we manually count day of year.
        if time[datex].dayofyear==1: 
            dayofyear_idx = 0
        else:
            dayofyear_idx +=1
        
        # Check again for NaNs, raise error if NaNs exist
        if np.isnan(interp_day).any():
            raise ValueError(f'NaN value detected in interpolated array at time index {datex}') 
        
        # Add interpolated day to interpolated dataset
        interp_dataset[:, :, dayofyear_idx, time[datex].year - first_year] = interp_day
        
    # Quality check size of interpolated dataset array
    if interp_dataset.nbytes < 1e6:
        raise ValueError(f"Interpolated data size is unexpectedly small for {source} {ssp} {var}. Exiting.")
           
    # July 1st, 2025 - Savanna Wolvin - Changing file save type from MATLAB to NETCDF
    ds = xr.DataArray(data = interp_dataset, 
                      dims = ["lat", "lon", "DOY", "year"],
                      coords = dict(
                          lat = COARSE_LAT,
                          lon = COARSE_LON, 
                          DOY = dayOfYear,
                          year = years),
                      attrs = dict(
                          units = dataset[var].units))
    ds = ds.rename(f"{var}")
    
    ds.to_netcdf(path = f"{COARSE_DIR}{source}_{ssp}_{var}.nc")
    print(f"File {COARSE_DIR}{source}_{ssp}_{var}.nc written successfully.")
       
    ##### COMMENTED OUT SAVING THE DATAFILES AS MATLAB FILES
    # # Create dictionary to save
    # data_dict = {
    #     'interpolated_data': interp_dataset,
    #     'lat': COARSE_LAT, 
    #     'lon': COARSE_LON, 
    #     'day_of_year': dayOfYear,
    #     'year': years,
    #     'units': dataset[var].units
    # }
    
    # # Name File 
    # file_name = os.path.join(COARSE_DIR, f"{source}_{ssp}_{var}.mat")
    
    # # Save file
    # if lock is None: 
    #     sio.savemat(file_name, data_dict)
    # else:
    #     with lock: sio.savemat(file_name, data_dict)
    
    # print(f"File {file_name} written successfully.")
        

#%%
"""
FUNCTION DEFINITION: check_for_missing_matlab_files
    INPUT (): 
    
    OUTPUT
"""
def check_for_missing_matlab_files(df):
    missing_files = []
    total_files_searched = 0

    for index, row in df.iterrows():
        source = row['source_id']
        for ssp in df.columns[1:]:
            if row[ssp] == 1:
                for var in GCM_VARIABLES:
                    file_path = COARSE_DIR + f'/{source}_{ssp}_{var}.mat'
                    total_files_searched += 1
                    if not os.path.exists(file_path):
                        missing_files.append(file_path)

    print(f"Total files searched: {total_files_searched}")
    print(f"Total missing files: {len(missing_files)}")

    return missing_files


#%%
"""
FUNCTION DEFINITION: compare_sampled_data
    INPUT
    - source ():
    - ssp ():
    - var ():
    - year ():
    - month ():
    - day ():
    - source_paths ():
    
    OUTPUT (matplotlib.figure):
"""
# def compare_sampled_data(source, ssp, var, year, month, day, source_paths):
    # Read the original .nc file data
    # subset, time = get_ds_from_disk(ssp, var, source, source_paths, CACHE_DIR)
    
    # # Normalize the times to the same time of day
    # time_normalized = time.normalize()
    
    # # Convert the input date to the appropriate format
    # input_date = pd.to_datetime(f"{year}-{month:02d}-{day:02d}").normalize()
    # day_of_year = input_date.dayofyear
    
    # # Find the corresponding index in the original data
    # try:
    #     original_index = np.where(time_normalized == input_date)[0][0]
    # except IndexError:
    #     raise ValueError(f"Date {input_date} not found in the dataset.")
    
    # original_data = subset[var].isel(time=original_index).compute()
    
    # # Adjust original data longitude to be within -180 to 180
    # original_lon = original_data['lon'].values
    # if np.any(original_lon > 180):
    #     original_lon = ((original_lon + 180) % 360) - 180
    # original_data['lon'] = original_lon
    
    # # Read the corresponding .mat file data
    # mat_file_path = os.path.join(COARSE_DIR, f"{source}_{ssp}_{var}.mat")
    # mat_data = sio.loadmat(mat_file_path)
    
    # # Extract interpolated data
    # interpolated_data = mat_data['interpolated_data']
    # lat = mat_data['lat'].flatten()
    # lon = mat_data['lon'].flatten()
    
    # # Find the corresponding year index in the interpolated data
    # year_index = np.where(mat_data['year'].flatten() == year)[0][0]
    
    # interpolated_day_data = interpolated_data[:, :, day_of_year - 1, year_index]
    
    # # Create a meshgrid for the interpolated data
    # lon_mesh, lat_mesh = np.meshgrid(lon, lat)
    
    # # Set extent for North America: [west, east, south, north]
    # extent = [-170, -50, 5, 85]
    
    # # Filter original data for North America extent
    # original_data_na = original_data.where(
    #     (original_data['lon'] >= extent[0]) & (original_data['lon'] <= extent[1]) & 
    #     (original_data['lat'] >= extent[2]) & (original_data['lat'] <= extent[3]), drop=True)
    
    # # Calculate the global min and max values for colorbar limits based on North America data
    # vmin = original_data_na.min().item()
    # vmax = original_data_na.max().item()
    
    # # Determine colorbar ticks
    # ticks = np.linspace(vmin, vmax, num=10)
    
    # # Create a GridSpec layout
    # fig = plt.figure(figsize=(14, 8))
    # gs = fig.add_gridspec(2, 2, height_ratios=[1, 0.05], hspace=0.3)
    
    # # Original data plot (North America only)
    # ax1 = fig.add_subplot(gs[0, 0], projection=ccrs.PlateCarree())
    # original_plot = ax1.contourf(original_data_na['lon'], original_data_na['lat'], original_data_na, levels=20, cmap='viridis', vmin=vmin, vmax=vmax)
    # ax1.set_extent(extent, crs=ccrs.PlateCarree())
    # ax1.coastlines()
    # ax1.set_title(f'Original {var} on {input_date.strftime("%Y-%m-%d")}')
    
    # # Interpolated data plot (North America extent)
    # ax2 = fig.add_subplot(gs[0, 1], projection=ccrs.PlateCarree())
    # ax2.contourf(lon_mesh, lat_mesh, interpolated_day_data, levels=20, cmap='viridis', vmin=vmin, vmax=vmax)
    # ax2.set_extent(extent, crs=ccrs.PlateCarree())
    # ax2.coastlines()
    # ax2.set_title(f'Interpolated {var} on {input_date.strftime("%Y-%m-%d")}')
    
    # # Single colorbar for both plots
    # cbar_ax = fig.add_subplot(gs[1, :])
    # cbar = fig.colorbar(original_plot, cax=cbar_ax, orientation='horizontal', ticks=ticks)
    # cbar.set_label(subset[var].units)
    
    # plt.show()
    
    
#%% MAIN

if __name__ == "__main__":
    
    # Generate source paths and inventory
    inventory, source_paths = inventory_and_source_paths()

    # Inspect your processing power
    num_cores = multiprocessing.cpu_count()
    print(f"Number of available cores: {num_cores}")
    if max_cores is not None: 
        num_cores=np.min([num_cores,max_cores])
    print(f"Number of cores using: {num_cores}")

    # Construct parallel processor
    manager = multiprocessing.Manager()
    lock = manager.Lock()

    with ProcessPoolExecutor(max_workers=min(20, num_cores)) as executor:
        futures = [] # list to contain execution calls to which will run asynchronously
        
        # Loop through each model and simulation, use if available based on inventory
        for _, row in inventory.iterrows(): 
            for col_name, val in row.items(): 
                if val == 1: 
                    
                    # Model and simulation exists, list source ID and SSP simulation
                    source, ssp = row.source_id, col_name
                    print(source)
                    
                    # Loop through each variable, check if it already exists, 
                    # if not, process this case
                    for var in GCM_VARIABLES:
                        #######################################################
                        # July 1st, 2025 COmmented out becasue we changed file type to netcdf
                        #####################################################
                        # fname = os.path.join(
                        #     COARSE_DIR, f"{source}_{ssp}_{var}.mat")
                        fname = os.path.join(
                            COARSE_DIR, f"{source}_{ssp}_{var}.nc")
                        if os.path.exists(fname):
                            # print(f"File {fname} already exists. Skipping.")
                            continue
                        else:
                            # serial processing
                            if serial:
                                to_coarse_grid(
                                    source, ssp, var, None, source_paths)
                                
                            # add to parallel processing list
                            else:
                                futures.append(executor.submit(
                                    to_coarse_grid, source, ssp, var, lock, source_paths))

        for future in futures:
            try:
                future.result()
            except Exception as exc:
                print(f"Generated an exception: {exc}")
        
    # confirm that all .mat files were created 
    missing_files = check_for_missing_matlab_files(inventory)


    # # visual inspection of interpolation 
    # compare_sampled_data(
    #     source='CanESM5', 
    #     ssp='historical', 
    #     var='huss', 
    #     year=1980, 
    #     month=6, 
    #     day=6, 
    #     source_paths = source_paths,
    #     cache_directory=CACHE_DIR, 
    #     coarse_dir=COARSE_DIR
    # )










