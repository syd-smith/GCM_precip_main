#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 23 18:06:49 2025

@author: Sydney Smith
"""

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/packages/')
import base_packages as bp
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/scatter_plot/')
from reference_data import scatter_framework

# check for variables stored in reference_data
# import reference_data
# print(dir(reference_data))


# Future Period: 2070-2099
# Historical Period: 1979-2014
# Temp Change: future - historical (C)
# Precip Ratio: future / historical 


# all possible emission scenarios found in downscaled models
emission_scenarios = ['ssp119', 'ssp126', 'ssp245', 'ssp370', 'ssp434', 'ssp585']

# all possible models included in downscaling
models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5', 'EC-Earth3-AerChem', 'EC-Earth3-CC',
 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'IITM-ESM', 'INM-CM4-8', 'INM-CM5-0',
 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC-ES2L', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']


#%%
# APPLY MASK TO MACA DATA
def mask_MACA(model_name, variable, emission_scenario, start_month = 6, stop_month = 8, start_year = 1979, stop_year = 2014, save = False):
    
    """
    This function applies the boundaries of the GSLB to a given dataset through setting everything
    outside the boundaries to NAN. Default values return a NETCDF file with data for JJA over the 
    historical period. 
    
    Note: For this research, the historical period is defined as 1979 - 2014 and the future period 
          as 2070 - 2099.
    """
    
    # Load in the shape file that contains the boundaries for the GSLB
    TOPO_DIR = "/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/gridmet/"
    shp  = bp.gpd.read_file(TOPO_DIR + "WBD_16_HU2_Shape/Shape/WBDHU4.shp")
    gsl  = shp[shp["huc4"] == "1602"]
    br   = shp[shp["huc4"] == "1601"]
    gslb = bp.gpd.GeoDataFrame(geometry=[gsl.geometry.union_all().union(br.geometry.union_all())], crs=shp.crs)
    
    # decodes time information follownig the Climate and Weather metadata connvention
    time_coder = bp.xr.coders.CFDatetimeCoder(use_cftime = True)
    
    # load file path for data
    fpath = f'/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/output/netcdf/macav2metdata_GSLBIP_{model_name}_{emission_scenario}_{variable}.nc'
    if not bp.os.path.exists(fpath):
        raise OSError(f'{fpath} was not downscaled in the MACA process.')
        
    # open data for specified model and raise error for requests that are not within the scope of the dataset
    ds_open = bp.xr.open_mfdataset(fpath, engine = "netcdf4", decode_times = time_coder)
    
    # slice to focus on specified months and years
    ds_years = ds_open[variable].sel(time = ds_open.time.dt.year.isin(range(start_year, stop_year + 1)))
    ds_slice = ds_years.sel(time = ds_years.time.dt.month.isin(range(start_month, stop_month + 1)))

    # applied data to standard coordinate system (not regridding)
    ds = ds_slice.rio.write_crs("EPSG:4326")

    # clips out the GSLB
    ds = ds.rio.clip(gslb.geometry.apply(bp.mapping), gslb.crs, drop=False)
    
    # saved masked dataset to directory
    if save == True:
        output_dir = '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/scatter_plot/masked_MACA/'
        output_name = f'MACA_{model_name}_{emission_scenario}_{start_month}-{stop_month}_{start_year}-{stop_year}_{variable}_masked.nc'
        output_path = f'{output_dir}{output_name}'
        
        ds.to_netcdf(output_path)
        print(f'Saved: {output_path}')
        return ds    
    
    return ds

model = 'UKESM1-0-LL'
# for model in models:
for emission_scenario in emission_scenarios:
    try: 
        mask_MACA(model, 'tasmax', emission_scenario, start_year = 2070, stop_year = 2099, save = True)
        mask_MACA(model, 'tasmax', emission_scenario, start_year = 1979, stop_year = 2014, save = True)
    except OSError:
        print(f'{model}_{emission_scenario} has not been downscaled using MACA.')   
        continue


    
# apply the model to one test then open and map it to see if boundary application was successful
# mask_MACA(models[0], 'pr', emission_scenarios[1], save = True)
# fpath = '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/scatter_plot/masked_MACA/MACA_ACCESS-CM2_ssp126_6-8_1979-2014_pr_masked.nc'
# ds = bp.xr.open_dataset(fpath)
# ds['pr'].isel(time=0).plot()
# bp.plt.title("Precipitation for First Time Slice")
# bp.plt.show()


#%%
# read in PC data from Savanna's .csv file
df = bp.pd.read_csv('/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/climate_analysis/pca/PCs_zscore_column.csv')

# _ refers to the rows while rows really refers to the columns
for _, row in df.iterrows():
    model = row['Model']
    exp = row['Exp']
    
    record = {
        'delta_temp' : 0,
        'precip_ratio' : 0,
        'PC1' : float(row['PC1']),
        'PC2' : float(row['PC2'])}
    
    scatter_framework.setdefault(model, {})[exp] = record
    
#%%
# CALCULATE PRECIPITATION RATIO
def precip_ratio(save_variable, start_month = 6, stop_month = 8):
    
    """
    Returns precitation ratio data to a nested dictionary under the model name and emission scenario. 
    The average precip value is across the historical period and all grid points.
    Save_variable should be the framework dictionary imported from reference_data.py.
    """
    
    # loop through all listed models and emission scenarios to open all available data
    for model in models:
        for emission_scenario in emission_scenarios:
            fpath = '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/scatter_plot/masked_MACA/'
            hist_path = f'{fpath}MACA_{model}_{emission_scenario}_{start_month}-{stop_month}_1979-2014_pr_masked.nc'
            fut_path = f'{fpath}MACA_{model}_{emission_scenario}_{start_month}-{stop_month}_2070-2099_pr_masked.nc'
            
            # calculate precipitation ratio for found data
            try:
                ds_hist = bp.xr.open_dataset(hist_path)
                ds_fut = bp.xr.open_dataset(fut_path)
                
                years_means_hist = []
                for year in range(1979, 2015):
                    year_dat_hist = ds_hist['pr'].sel(time = ds_hist.time.dt.year == year)
                    mean_hist = year_dat_hist.mean(skipna = True).item() # <- make sure to skip all NAN values outside the boundary
                    years_means_hist.append(mean_hist)
                grand_mean_hist = float(bp.np.mean(years_means_hist))
                
                years_means_fut = []
                for year in range(2070, 2100):
                    year_dat_fut = ds_fut['pr'].sel(time = ds_fut.time.dt.year == year)
                    mean_fut = year_dat_fut.mean(skipna = True).item() # <- make sure to skip all NAN values outside the boundary
                    years_means_fut.append(mean_fut)
                grand_mean_fut = float(bp.np.mean(years_means_fut))
                
                grand_precip = (grand_mean_fut/ grand_mean_hist) *100
                
                save_variable[model][emission_scenario]['precip_ratio'] = grand_precip

            # record default message for files not stored with masked data
            except OSError:
                save_variable[model][emission_scenario]['precip_ratio'] = 'File Not Found'
                
    return save_variable   
 
test = precip_ratio(scatter_framework)


def delta_temp(save_variable, start_month = 6, stop_month = 8):
    
    """
    Returns the change in temperature from the historical to future period to a nested 
    dictionary under the model name and emission scenario. 
    The average temperature calculated is across all grid points in the given period.
    Save_variable should be the framework dictionary imported from reference_data.py.
    """
    
    # loop through all listed models and emission scenarios to open all available data
    for model in models:
        for emission_scenario in emission_scenarios:
            fpath = '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/scatter_plot/masked_MACA/'
            hist_min_path = f'{fpath}MACA_{model}_{emission_scenario}_{start_month}-{stop_month}_1979-2014_tasmin_masked.nc'
            hist_max_path = f'{fpath}MACA_{model}_{emission_scenario}_{start_month}-{stop_month}_1979-2014_tasmax_masked.nc'
            fut_min_path = f'{fpath}MACA_{model}_{emission_scenario}_{start_month}-{stop_month}_2070-2099_tasmin_masked.nc'
            fut_max_path = f'{fpath}MACA_{model}_{emission_scenario}_{start_month}-{stop_month}_2070-2099_tasmax_masked.nc'
            
            try:
                # find the mean for the historical period
                hist_ds_min = bp.xr.open_dataset(hist_min_path)
                hist_means_min = []
                for year in range(1979, 2015):
                    data_hist_min = hist_ds_min['tasmin'].sel(time = hist_ds_min.time.dt.year == year)
                    hist_mean_min = data_hist_min.mean(skipna= True).item()
                    hist_means_min.append(hist_mean_min)
                    
                hist_ds_max = bp.xr.open_dataset(hist_max_path)
                hist_means_max = []
                for year in range(1979, 2015):
                    data_hist_max = hist_ds_max['tasmax'].sel(time = hist_ds_max.time.dt.year == year)
                    hist_mean_max = data_hist_max.mean(skipna = True).item()
                    hist_means_max.append(hist_mean_max)    
                
                # finds the mean between average min and max values
                avg_hist = [(min + max)/2 for min, max in zip(hist_means_min, hist_means_max)]
                hist_val = float(bp.np.mean(avg_hist))
                
                # finds the mean for the future period
                fut_ds_min = bp.xr.open_dataset(fut_min_path)
                fut_means_min = []
                for year in range(2070, 2099):
                    data_fut_min = fut_ds_min['tasmin'].sel(time = fut_ds_min.time.dt.year == year)
                    fut_mean_min = data_fut_min.mean(skipna= True).item()
                    fut_means_min.append(fut_mean_min)
                    
                fut_ds_max = bp.xr.open_dataset(fut_max_path)
                fut_means_max = []
                for year in range(2070, 2099):
                    data_fut_max = fut_ds_max['tasmax'].sel(time = fut_ds_max.time.dt.year == year)
                    fut_mean_max = data_fut_max.mean(skipna = True).item()
                    fut_means_max.append(fut_mean_max)    
                
                # finds the mean between average min and max values
                avg_fut = [(min + max)/2 for min, max in zip(fut_means_min, fut_means_max)]
                fut_val = float(bp.np.mean(avg_fut))    
                    
                # calulate change in temperature and save data to dictionary
                grand_temp = fut_val - hist_val
                save_variable[model][emission_scenario]['delta_temp'] = grand_temp
                
            # skip over model and emission scenario combos that don't exist in the dataset
            except OSError:
                save_variable[model][emission_scenario]['delta_temp'] = 'File Not Found'
                
    return save_variable   

oct_19 = delta_temp(test)


#%%
# save data from the functions to a specified file
printer = bp.pprint.PrettyPrinter(indent = 3, width = 100, sort_dicts = True)
bp.os.chdir('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/scatter_plot/')

with open('oct_19.txt', 'w') as f:
    f.write(printer.pformat(oct_19))
        
        
#%%
# read out the dictionary from the .txt file
import ast

# Open and read the file
with open("oct_19.txt", "r") as f:
    contents = f.read()

# Convert from string representation to actual dictionary
base_dict = ast.literal_eval(contents)

# print(type(base_dict))  # Should show: <class 'dict'>
# print(list(base_dict.keys())[:5])  # Show first few model names


#%%
# graph individual datapoints with colors to match  emission scenarios
def scatter_plot(save_variable, save_name, PC = False, save = False):
    
    """
    This function graphs data points stored in a nested dictionary (save_variable) by the functions above. 
    PC = True changes the size and colors of each point to reflect the respective PC scores assigned in the
    climate analysis process. Note that PC1 and PC2 data was read in from a .csv file. See reference_data.py 
    for more information.
    """
    
    fig, ax = bp.plt.subplots()
    marker_colors = ['purple', 'indigo', 'steelblue', 'darkcyan', 'seagreen', 'gold']
    
    for model in save_variable:
        for scenario in save_variable[model]:
            if save_variable[model][scenario]['delta_temp'] == 'File Not Found' or save_variable[model][scenario]['precip_ratio'] == 'File Not Found':
                continue
            if PC == True:
                val = save_variable[model][scenario]['PC1']
                # norm = bp.colors.Normalize(vmin = -15, vmax = 20)
                size = save_variable[model][scenario]['PC2']
                ax.scatter(save_variable[model][scenario]['delta_temp'], save_variable[model][scenario]['precip_ratio'], c = val, cmap = 'viridis', vmin = -14, vmax = 20,s = size)
            else:
                marker = marker_colors[emission_scenarios.index(scenario)]
                ax.scatter(save_variable[model][scenario]['delta_temp'], save_variable[model][scenario]['precip_ratio'], c = marker, s = 25)
        
    # axis ticks and labels
    ax.set_yticks([50, 100, 150, 200])
    ax.set_yticklabels([0.5, 1, 1.5, 2])
    ax.set_xticks([0, 5])

    # set horizontal and vertical lines
    ax.axhline(y = 50, color = 'lightgray', linewidth = 0.7)
    ax.axhline(y = 100, color = 'lightgray', linewidth = 0.7)
    ax.axhline(y = 150, color = 'lightgray', linewidth = 0.7)
    ax.axhline(y = 200, color = 'lightgray', linewidth = 0.7)
    ax.axvline(x = 0, color = 'lightgray', linewidth = 0.7)
    ax.axvline(x = 5, color = 'lightgray', linewidth = 0.7)

    # remove the black outlines around the graph
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis='both', which='both', length=0)

    # labels for the graph
    ax.set_xlabel('Temperature Change (K)')
    ax.set_ylabel('Precipitation Ratio')
    # title
    fig.suptitle("Climate Change's Impact on Summer Precipitation", fontsize = 20, y = 1.08)
    # subtitle
    ax.set_title('1979-2014 vs. 2070-2099', fontsize = 10, pad = 7)

    # creating a custom legend for emission scenarios
    my_legend = [bp.Line2D([0], [0], marker='o', color='w', markersize=8, 
              markerfacecolor=marker_colors[i], label=emission_scenarios[i])
     for i in range(len(emission_scenarios))]  
    ax.legend(handles = my_legend, loc = 'center left', bbox_to_anchor = (1.05, 0.5))

    if save == True:
        save_path = bp.os.path.join(f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/scatter_plot/{save_name}.png')
        fig.savefig(save_path, dpi = 400, bbox_inches = 'tight', pad_inches = 0.1)
    else: 
        bp.plt.show()
        
    return fig

scatter_plot(base_dict, 'GSLB_scatter', save = True)


#%%
# path to access netcdf files containing the data
strong_group_path = '/uufs/chpc.utah.edu/common/home/strong-group7/savanna/maca/output/netcdf/macav2metdata_GSLBIP_'
find_files = sorted(bp.glob.glob(strong_group_path + '*.nc'))
prefix = strong_group_path

# makes list of all model names by editing file paths
models = []
for file in find_files:
    no_prefix = file.replace(prefix, '')
    model = no_prefix.split('_ssp')[0]
    if model not in models:
        models.append(model)
        
        
# output of models for loop - models used in the maca downscaling      
# ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5', 'EC-Earth3-AerChem', 'EC-Earth3-CC',
#  'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'IITM-ESM', 'INM-CM4-8', 'INM-CM5-0',
#  'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC-ES2L', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']

        
#models pulled from the dir_coarse file that is used in courts scatter plot (for the most part what seems to be used in the plot)
#miroc-es2h and ec-earth3-cc both show on the plot but not on the list
# ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5', 'EC-Earth3-AerChem',
#  'EC-Earth3-CC', 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'IITM-ESM', 
#  'INM-CM4-8', 'INM-CM5-0', 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC-ES2L', 'MIROC6', 'MPI-ESM-1-2-HAM', 'MPI-ESM1-2-HR', 
#  'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']


# list of models found in courts scatter plot code (don't seem to really be the ones used)
# courts_models = ['ACCESS-CM2','ACCESS-ESM1-5','AWI-CM-1-1-MR','BCC-CSM2-MR','CanESM5','CESM2','CESM2-WACCM','EC-Earth3','EC-Earth3-Veg',
#                 'FGOALS-f3-L','FGOALS-g3','GFDL-ESM4','IPSL-CM6A-LR','MIROC6','MPI-ESM1-2-HR',
#                 'MPI-ESM1-2-LR','MRI-ESM2-0','NorESM2-LM']

