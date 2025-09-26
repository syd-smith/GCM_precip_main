#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 23 18:06:49 2025

@author: Sydney Smith
"""

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/packages/')
import base_packages as bp

# future period: 2070-2099
# historical period: 1979-2014
# temp change: future - historical (C)
# precip ratio: future / historical 
# APPLY MASK TO MACA DATA

fpath = '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/scatter_plot/masked_MACA/MACA_ACCESS-CM2_ssp126_6-8_1979-2014_masked.nc'

ds = bp.xr.open_dataset(fpath)


#%%
# all possible emission scenarios found in models
emission_scenarios = ['ssp119', 'ssp126', 'ssp245', 'ssp370', 'ssp434', 'ssp585']

# all possible models included in ddownscaling
models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5', 'EC-Earth3-AerChem', 'EC-Earth3-CC',
 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'IITM-ESM', 'INM-CM4-8', 'INM-CM5-0',
 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC-ES2L', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']
    


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
    ds_years = ds_open.sel(time = ds_open.time.dt.year.isin(range(start_year, stop_year + 1)))
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


# for model in models:
#      for emission_scenario in emission_scenarios:
#          try: 
#              mask_MACA(model, 'pr', emission_scenario, save = True)
#          except OSError:
#              print(f'{model}_{emission_scenario} has not been downscaled using MACA.')   
#              continue

mask_MACA(models[0], 'pr', emission_scenarios[1], save = True)

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
      


# define the date ranges for historical and future time periods
hist_years = [year for year in range(1979, 2015)]
fut_years = [year for year in range(2070, 2100)]

# out of function practice
# model = 'KACE-1-0-G'
# emission_scenario = 'ssp585'
# fpath = strong_group_path + model + '_' + emission_scenario + '_pr.nc'
# open_ds = xr.open_dataset(fpath)
# open_ds = open_ds['pr'].sel(lat = slice(min_lat, max_lat), lon = slice(min_lon, max_lon)) 
# year_dat = open_ds.sel(time = open_ds.time.dt.month.isin([6,7,8]) & (open_ds.time.dt.year == 1979))


def hist_precip():
    """
    Returns a list with the model name, emission scenario, and the average 
    precip value across the historical period and all grid points.
    """
    
    hist_precip_data = []
    for model in models:
        for emission_scenario in emission_scenarios:
            fpath = f'/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/scatter_plot/masked_MACA/MACA_{model}_{emission_scenario}_{start_month}-{stop_month}_{start_year}-{stop_year}_{variable}_masked.nc'
            if not bp.os.path.exists(fpath):
                continue
            else:
                ds = mask(fpath)
                
                years_means = []
                for year in hist_years:
                    year_dat = ds['pr'].sel(time = ds.time.dt.month.isin([6,7,8]) & (ds.time.dt.year == year))
                    mean = year_dat.mean().item()
                    years_means.append(mean)
                grand_mean = float(bp.np.mean(years_means))
                hist_precip_data.append([model, emission_scenario, grand_mean])
    return hist_precip_data   

# returns a list with the model name, emission scenario, and the average precip value for it across future years and grid points
def fut_precip():
    fut_precip_data = []
    for model in models:
        for emission_scenario in emission_scenarios:
            fpath = strong_group_path + model + '_' + emission_scenario + '_pr.nc'
            if not bp.os.path.exists(fpath):
                continue
            else:
                ds = mask(fpath)
                
                years_means = []
                for year in fut_years:
                    year_dat = ds['pr'].sel(time = ds.time.dt.month.isin([6,7,8]) & (ds.time.dt.year == year))
                    mean = year_dat.mean().item()
                    years_means.append(mean)
                grand_mean = float(bp.np.mean(years_means))
                fut_precip_data.append([model, emission_scenario, grand_mean])
    return fut_precip_data    

# pulls from lists for future and historical precip values to return a new list containing the precip ratio
def precip_ratio():
    precip_ratio_data = []
    fut_data = fut_precip()
    hist_data = hist_precip()
    for fut, hist in zip(fut_data, hist_data):
        fut_val = fut[2]
        hist_val = hist[2]
        grand_precip = (fut_val / hist_val) *100
        precip_ratio_data.append([fut[0], fut[1], grand_precip])
    return precip_ratio_data   

def hist_temp_year():
    hist_temp_data_year = []
    for model in models:
        for emission_scenario in emission_scenarios:
            fpath_min = strong_group_path + model + '_' + emission_scenario + '_tasmin.nc'
            if not bp.os.path.exists(fpath_min):
                continue
            else:
                open_ds_min = bp.xr.open_dataset(fpath_min)
                open_ds_min = open_ds_min['tasmin'].sel(lat = slice(min_lat, max_lat), lon = slice(min_lon, max_lon))
                years_means_min = []
                for year in hist_years:
                    year_dat_min = open_ds_min.sel(time = open_ds_min.time.dt.month.isin([6,7,8]) & (open_ds_min.time.dt.year == year))
                    mean_min = year_dat_min.mean().item()
                    years_means_min.append(mean_min)
            fpath_max = strong_group_path + model + '_' + emission_scenario + '_tasmax.nc'
            if not bp.os.path.exists(fpath_max):
                continue
            else:
                open_ds_max = bp.xr.open_dataset(fpath_max)
                open_ds_max = open_ds_max['tasmax'].sel(lat = slice(min_lat, max_lat), lon = slice(min_lon, max_lon))
                years_means_max = []
                for year in hist_years:
                    year_dat_max = open_ds_max.sel(time = open_ds_max.time.dt.month.isin([6,7,8]) & (open_ds_max.time.dt.year == year))
                    mean_max = year_dat_max.mean().item()
                    years_means_max.append(mean_max)    
            all_avg = [(min + max)/2 for min, max in zip(years_means_min, years_means_max)]
            grand_mean = float(bp.np.mean(all_avg))
            hist_temp_data_year.append([model, emission_scenario, grand_mean])
    return hist_temp_data_year    

def fut_temp_year():
    fut_temp_data_year = []
    for model in models:
        for emission_scenario in emission_scenarios:
            fpath_min = strong_group_path + model + '_' + emission_scenario + '_tasmin.nc'
            if not bp.os.path.exists(fpath_min):
                continue
            else:
                open_ds_min = bp.xr.open_dataset(fpath_min)
                open_ds_min = open_ds_min['tasmin'].sel(lat = slice(min_lat, max_lat), lon = slice(min_lon, max_lon))
                years_means_min = []
                for year in fut_years:
                    year_dat_min = open_ds_min.sel(time = open_ds_min.time.dt.month.isin([6,7,8]) & (open_ds_min.time.dt.year == year))
                    mean_min = year_dat_min.mean().item()
                    years_means_min.append(mean_min)
            fpath_max = strong_group_path + model + '_' + emission_scenario + '_tasmax.nc'
            if not bp.os.path.exists(fpath_max):
                continue
            else:
                open_ds_max = bp.xr.open_dataset(fpath_max)
                open_ds_max = open_ds_max['tasmax'].sel(lat = slice(min_lat, max_lat), lon = slice(min_lon, max_lon))
                years_means_max = []
                for year in fut_years:
                    year_dat_max = open_ds_max.sel(time = open_ds_max.time.dt.month.isin([6,7,8]) & (open_ds_max.time.dt.year == year))
                    mean_max = year_dat_max.mean().item()
                    years_means_max.append(mean_max)    
            all_avg = [(min + max)/2 for min, max in zip(years_means_min, years_means_max)]
            grand_mean = float(bp.np.mean(all_avg))
            fut_temp_data_year.append([model, emission_scenario, grand_mean])
    return fut_temp_data_year 

# finds the difference in mean temperature between future and historical periods
def delta_temp_year():
    delta_temp_data_year = []
    fut_data = fut_temp_year()
    hist_data = hist_temp_year()
    for fut, hist in zip(fut_data, hist_data):
        fut_val = fut[2]
        hist_val = hist[2]
        grand_temp = fut_val - hist_val
        delta_temp_data_year.append([fut[0], fut[1], grand_temp])
    return delta_temp_data_year


# pull data points (see copied below)
yprecip = precip_ratio()
xtemp = delta_temp_year()



#%%
# copy and pasted data from above code for plotting instead of running all together
yprecip = [['ACCESS-CM2', 'ssp126', 123.04653885765929],
 ['ACCESS-CM2', 'ssp245', 103.51375689164581],
 ['ACCESS-CM2', 'ssp370', 169.43617593472138],
 ['ACCESS-CM2', 'ssp585', 160.9026821226941],
 ['ACCESS-ESM1-5', 'ssp126', 103.62061750595598],
 ['ACCESS-ESM1-5', 'ssp245', 118.24475389310025],
 ['ACCESS-ESM1-5', 'ssp370', 120.92105722643203],
 ['ACCESS-ESM1-5', 'ssp585', 131.67819202995796],
 ['CMCC-ESM2', 'ssp126', 118.32071700216125],
 ['CMCC-ESM2', 'ssp245', 102.54755084367704],
 ['CMCC-ESM2', 'ssp370', 96.08146815651176],
 ['CMCC-ESM2', 'ssp585', 100.4519933251578],
 ['CNRM-CM6-1-HR', 'ssp126', 104.94242958668639],
 ['CNRM-CM6-1-HR', 'ssp585', 81.25836204592567],
 ['CNRM-CM6-1', 'ssp126', 93.94801395246391],
 ['CNRM-CM6-1', 'ssp245', 77.26792990686475],
 ['CNRM-CM6-1', 'ssp370', 79.3558421859867],
 ['CNRM-CM6-1', 'ssp585', 109.72989730393574],
 ['CNRM-ESM2-1', 'ssp119', 96.00607526407144],
 ['CNRM-ESM2-1', 'ssp126', 86.14812132365086],
 ['CNRM-ESM2-1', 'ssp245', 105.56208169245629],
 ['CNRM-ESM2-1', 'ssp370', 85.86151131508791],
 ['CNRM-ESM2-1', 'ssp434', 70.83074635792642],
 ['CNRM-ESM2-1', 'ssp585', 83.63073445899907],
 ['CanESM5', 'ssp119', 112.36990805133964],
 ['CanESM5', 'ssp126', 126.80189652789342],
 ['CanESM5', 'ssp245', 125.34424093453462],
 ['CanESM5', 'ssp370', 176.7210468391327],
 ['CanESM5', 'ssp434', 135.62759232738023],
 ['CanESM5', 'ssp585', 182.60304904518102],
 ['EC-Earth3-AerChem', 'ssp370', 111.66348954934494],
 ['EC-Earth3-CC', 'ssp245', 96.34187921418881],
 ['EC-Earth3-CC', 'ssp585', 95.33403963394946],
 ['EC-Earth3-Veg-LR', 'ssp119', 93.105188357535],
 ['EC-Earth3-Veg-LR', 'ssp126', 90.45804517067597],
 ['EC-Earth3-Veg-LR', 'ssp245', 81.52738540513725],
 ['EC-Earth3-Veg-LR', 'ssp370', 100.07746305713303],
 ['EC-Earth3-Veg-LR', 'ssp585', 95.80937445262279],
 ['EC-Earth3', 'ssp119', 84.01706642487036],
 ['EC-Earth3', 'ssp126', 92.49107135606161],
 ['EC-Earth3', 'ssp245', 86.06645304013296],
 ['EC-Earth3', 'ssp434', 105.49109310681722],
 ['EC-Earth3', 'ssp585', 108.83917303565578],
 ['GFDL-CM4', 'ssp245', 92.21489119982255],
 ['GFDL-CM4', 'ssp585', 92.34912080901175],
 ['GFDL-ESM4', 'ssp119', 116.55928711545229],
 ['GFDL-ESM4', 'ssp126', 109.34590351708032],
 ['GFDL-ESM4', 'ssp245', 116.24351837331047],
 ['GFDL-ESM4', 'ssp370', 117.10928628458772],
 ['GFDL-ESM4', 'ssp585', 111.71930370915662],
 ['HadGEM3-GC31-LL', 'ssp126', 109.71645069134975],
 ['HadGEM3-GC31-LL', 'ssp245', 115.12636532935589],
 ['HadGEM3-GC31-LL', 'ssp585', 142.13778837540295],
 ['HadGEM3-GC31-MM', 'ssp585', 100.47619494289243],
 ['IITM-ESM', 'ssp126', 102.84345599889247],
 ['INM-CM4-8', 'ssp126', 91.84969731188696],
 ['INM-CM4-8', 'ssp245', 85.59345522327105],
 ['INM-CM4-8', 'ssp370', 91.35568265725628],
 ['INM-CM4-8', 'ssp585', 84.33354547019675],
 ['INM-CM5-0', 'ssp126', 93.48073256656475],
 ['INM-CM5-0', 'ssp245', 88.62596762173774],
 ['INM-CM5-0', 'ssp370', 86.83330807365415],
 ['INM-CM5-0', 'ssp585', 90.55445469286907],
 ['KACE-1-0-G', 'ssp126', 127.82636520744887],
 ['KACE-1-0-G', 'ssp245', 146.2619807466494],
 ['KACE-1-0-G', 'ssp370', 185.64333183793076],
 ['KACE-1-0-G', 'ssp585', 230.88818901483438],
 ['KIOST-ESM', 'ssp585', 109.7967843017051],
 ['MIROC-ES2H', 'ssp119', 101.1069053394853],
 ['MIROC-ES2H', 'ssp126', 102.66820181718275],
 ['MIROC-ES2H', 'ssp245', 99.1033077639887],
 ['MIROC-ES2H', 'ssp370', 107.58115269700228],
 ['MIROC-ES2H', 'ssp585', 116.62847988100896],
 ['MIROC-ES2L', 'ssp119', 109.52074152375756],
 ['MIROC-ES2L', 'ssp126', 130.47872376544098],
 ['MIROC-ES2L', 'ssp245', 117.5456087930141],
 ['MIROC-ES2L', 'ssp370', 122.55989432407328],
 ['MIROC6', 'ssp126', 108.21825928648994],
 ['MIROC6', 'ssp370', 120.08565956358316],
 ['MIROC6', 'ssp585', 109.70863813422875],
 ['MPI-ESM1-2-HR', 'ssp126', 118.28515925103946],
 ['MPI-ESM1-2-HR', 'ssp245', 113.10407353427306],
 ['MPI-ESM1-2-HR', 'ssp370', 83.34174722207088],
 ['MPI-ESM1-2-HR', 'ssp585', 95.68939876408322],
 ['MPI-ESM1-2-LR', 'ssp119', 87.78802603114842],
 ['MPI-ESM1-2-LR', 'ssp126', 79.591883180736],
 ['MPI-ESM1-2-LR', 'ssp245', 62.72868031100225],
 ['MPI-ESM1-2-LR', 'ssp370', 95.6431745734582],
 ['MPI-ESM1-2-LR', 'ssp585', 54.04509071810081],
 ['MRI-ESM2-0', 'ssp119', 100.5123752507848],
 ['MRI-ESM2-0', 'ssp126', 111.25303536286609],
 ['MRI-ESM2-0', 'ssp245', 107.88867880311628],
 ['MRI-ESM2-0', 'ssp370', 117.66091054376851],
 ['MRI-ESM2-0', 'ssp434', 110.42415341452039],
 ['MRI-ESM2-0', 'ssp585', 116.57297274599333],
 ['UKESM1-0-LL', 'ssp119', 111.95645301467793],
 ['UKESM1-0-LL', 'ssp126', 125.11857914946323],
 ['UKESM1-0-LL', 'ssp245', 131.6010055712262],
 ['UKESM1-0-LL', 'ssp370', 151.39361329278623],
 ['UKESM1-0-LL', 'ssp434', 122.80370803970935],
 ['UKESM1-0-LL', 'ssp585', 163.46007668979772]]

xtemp = [['ACCESS-CM2', 'ssp126', 4.035470496283665],
 ['ACCESS-CM2', 'ssp245', 5.088811153835707],
 ['ACCESS-CM2', 'ssp370', 6.514884355333095],
 ['ACCESS-CM2', 'ssp585', 8.324157630072648],
 ['ACCESS-ESM1-5', 'ssp126', 2.906580013698999],
 ['ACCESS-ESM1-5', 'ssp245', 3.6730922275119724],
 ['ACCESS-ESM1-5', 'ssp370', 5.547706773545997],
 ['ACCESS-ESM1-5', 'ssp585', 6.336319647894925],
 ['CMCC-ESM2', 'ssp126', 2.374746788872642],
 ['CMCC-ESM2', 'ssp245', 4.332504102918847],
 ['CMCC-ESM2', 'ssp370', 5.151582675509985],
 ['CMCC-ESM2', 'ssp585', 6.25207977294923],
 ['CNRM-CM6-1-HR', 'ssp126', 2.4831239488389656],
 ['CNRM-CM6-1-HR', 'ssp585', 7.107352871365038],
 ['CNRM-CM6-1', 'ssp126', 2.7331831190321054],
 ['CNRM-CM6-1', 'ssp245', 4.037005106608092],
 ['CNRM-CM6-1', 'ssp370', 5.8459721883137945],
 ['CNRM-CM6-1', 'ssp585', 7.2549096001519615],
 ['CNRM-ESM2-1', 'ssp119', 2.121856350368887],
 ['CNRM-ESM2-1', 'ssp126', 2.54962429470487],
 ['CNRM-ESM2-1', 'ssp245', 3.804751502143006],
 ['CNRM-ESM2-1', 'ssp370', 5.748571777343784],
 ['CNRM-ESM2-1', 'ssp434', 3.5254681905110488],
 ['CNRM-ESM2-1', 'ssp585', 6.913173505995019],
 ['CanESM5', 'ssp119', 1.9430319044325302],
 ['CanESM5', 'ssp126', 2.926931593153256],
 ['CanESM5', 'ssp245', 4.613217247856994],
 ['CanESM5', 'ssp370', 6.747901746961816],
 ['CanESM5', 'ssp434', 4.322639634874122],
 ['CanESM5', 'ssp585', 8.165361446804468],
 ['EC-Earth3-AerChem', 'ssp370', 6.492116716172916],
 ['EC-Earth3-CC', 'ssp245', 3.597260114881749],
 ['EC-Earth3-CC', 'ssp585', 7.015608893500428],
 ['EC-Earth3-Veg-LR', 'ssp119', 1.239014604356555],
 ['EC-Earth3-Veg-LR', 'ssp126', 1.9363400777180573],
 ['EC-Earth3-Veg-LR', 'ssp245', 3.5540921529134266],
 ['EC-Earth3-Veg-LR', 'ssp370', 5.26922505696615],
 ['EC-Earth3-Veg-LR', 'ssp585', 6.9697028266058965],
 ['EC-Earth3', 'ssp119', 2.042160458034914],
 ['EC-Earth3', 'ssp126', 2.046162584092883],
 ['EC-Earth3', 'ssp245', 3.717729865180104],
 ['EC-Earth3', 'ssp434', 2.61788762410481],
 ['EC-Earth3', 'ssp585', 6.744886440700952],
 ['GFDL-CM4', 'ssp245', 3.8984911600748546],
 ['GFDL-CM4', 'ssp585', 6.431554497612865],
 ['GFDL-ESM4', 'ssp119', 0.09704233805337026],
 ['GFDL-ESM4', 'ssp126', 1.0986907111274036],
 ['GFDL-ESM4', 'ssp245', 1.6904037475586051],
 ['GFDL-ESM4', 'ssp370', 3.6842773437500114],
 ['GFDL-ESM4', 'ssp585', 3.7494145711262945],
 ['HadGEM3-GC31-LL', 'ssp126', 3.696788448757559],
 ['HadGEM3-GC31-LL', 'ssp245', 5.38947635226782],
 ['HadGEM3-GC31-LL', 'ssp585', 8.479680464002854],
 ['HadGEM3-GC31-MM', 'ssp585', 8.702520328097876],
 ['IITM-ESM', 'ssp126', 0.5429062737359232],
 ['INM-CM4-8', 'ssp126', 1.3087302313910527],
 ['INM-CM4-8', 'ssp245', 2.8796258714463647],
 ['INM-CM4-8', 'ssp370', 4.507332865397132],
 ['INM-CM4-8', 'ssp585', 5.476760270860439],
 ['INM-CM5-0', 'ssp126', 1.8922420925564438],
 ['INM-CM5-0', 'ssp245', 3.0290570576985942],
 ['INM-CM5-0', 'ssp370', 4.880197482638891],
 ['INM-CM5-0', 'ssp585', 5.350921037462001],
 ['KACE-1-0-G', 'ssp126', 3.441060807969791],
 ['KACE-1-0-G', 'ssp245', 4.308889855278892],
 ['KACE-1-0-G', 'ssp370', 6.429534488254092],
 ['KACE-1-0-G', 'ssp585', 7.332312774658192],
 ['KIOST-ESM', 'ssp585', 6.848567538791201],
 ['MIROC-ES2H', 'ssp119', 2.8019455803765254],
 ['MIROC-ES2H', 'ssp126', 2.2288326687282733],
 ['MIROC-ES2H', 'ssp245', 3.9853968302409157],
 ['MIROC-ES2H', 'ssp370', 4.31943571302628],
 ['MIROC-ES2H', 'ssp585', 5.470013427734386],
 ['MIROC-ES2L', 'ssp119', 2.0291964213053006],
 ['MIROC-ES2L', 'ssp126', 2.2807093302408816],
 ['MIROC-ES2L', 'ssp245', 3.428375244140625],
 ['MIROC-ES2L', 'ssp370', 4.820209672715919],
 ['MIROC6', 'ssp126', 1.8556951734754534],
 ['MIROC6', 'ssp370', 3.839194149441198],
 ['MIROC6', 'ssp585', 5.083470577663832],
 ['MPI-ESM1-2-HR', 'ssp126', 1.4712949964735458],
 ['MPI-ESM1-2-HR', 'ssp245', 2.918406846788173],
 ['MPI-ESM1-2-HR', 'ssp370', 4.58917880588109],
 ['MPI-ESM1-2-HR', 'ssp585', 5.728629387749606],
 ['MPI-ESM1-2-LR', 'ssp119', 0.8106803046331947],
 ['MPI-ESM1-2-LR', 'ssp126', 1.2837580362955805],
 ['MPI-ESM1-2-LR', 'ssp245', 3.4428337944878535],
 ['MPI-ESM1-2-LR', 'ssp370', 5.432471042209215],
 ['MPI-ESM1-2-LR', 'ssp585', 6.90986192491323],
 ['MRI-ESM2-0', 'ssp119', 2.1803762647840585],
 ['MRI-ESM2-0', 'ssp126', 2.308200327555369],
 ['MRI-ESM2-0', 'ssp245', 3.6177547878688756],
 ['MRI-ESM2-0', 'ssp370', 4.58668365478519],
 ['MRI-ESM2-0', 'ssp434', 3.310632069905637],
 ['MRI-ESM2-0', 'ssp585', 6.0314595540364735],
 ['UKESM1-0-LL', 'ssp119', 3.419454447428393],
 ['UKESM1-0-LL', 'ssp126', 4.160707770453541],
 ['UKESM1-0-LL', 'ssp245', 5.97176589965818],
 ['UKESM1-0-LL', 'ssp370', 8.05539660983618],
 ['UKESM1-0-LL', 'ssp434', 5.048386467827697],
 ['UKESM1-0-LL', 'ssp585', 8.97464269002279]]

# graph individual datapoints with colors to match  emission scenarios
fig, ax = bp.plt.subplots()
labels = []
marker_colors = ['purple', 'indigo', 'steelblue', 'darkcyan', 'seagreen', 'gold']
for idx, data in enumerate(yprecip):
    temp_data = xtemp[idx][2]
    precip_data = yprecip[idx][2]
    if yprecip[idx][1] == 'ssp119':
        marker = marker_colors[0]
    elif yprecip[idx][1] == 'ssp126':
        marker = marker_colors[1]
    elif yprecip[idx][1] == 'ssp245':
        marker = marker_colors[2]
    elif yprecip[idx][1] == 'ssp370':
         marker = marker_colors[3]
    elif yprecip[idx][1] == 'ssp434':
        marker = marker_colors[4]
    elif yprecip[idx][1] == 'ssp585':
        marker = marker_colors[5]
    labels.append([f"Source: {xtemp[idx][0]}, Scenario: {xtemp[idx][1]}"])
    ax.scatter(temp_data, precip_data, c = marker, s = 25)
    
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
fig.suptitle("Climate Change's Impact on Summer Precipitation", fontsize = 20, y = 1.01)
# subtitle
ax.set_title('1979-2014 vs. 2070-2099', fontsize = 10, pad = 7)

# creating a custom legend for emission scenarios
my_legend = [
    bp.Line2D([0], [0], marker = 'o', color = 'w', markersize = 8, markerfacecolor = marker_colors[0], label = emission_scenarios[0]),
    bp.Line2D([0], [0], marker = 'o', color = 'w', markersize = 8, markerfacecolor = marker_colors[1], label = emission_scenarios[1]),
    bp.Line2D([0], [0], marker = 'o', color = 'w', markersize = 8, markerfacecolor = marker_colors[2], label = emission_scenarios[2]),
    bp.Line2D([0], [0], marker = 'o', color = 'w', markersize = 8, markerfacecolor = marker_colors[3], label = emission_scenarios[3]),
    bp.Line2D([0], [0], marker = 'o', color = 'w', markersize = 8, markerfacecolor = marker_colors[4], label = emission_scenarios[4]),
   bp. Line2D([0], [0], marker = 'o', color = 'w', markersize = 8, markerfacecolor = marker_colors[5], label = emission_scenarios[5])]
ax.legend(handles = my_legend, loc = 'center left', bbox_to_anchor = (1.05, 0.5))

save_path = bp.os.path.join('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/summer_precip_scatter.png')
fig.savefig(save_path, dpi = 400, bbox_inches = 'tight', pad_inches = 0.1)

#%%
# #creating a hoverover for model and emission scenario label
# annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
#                     bbox=dict(boxstyle="round", fc="w"),
#                     arrowprops=dict(arrowstyle="->"))
# annot.set_visible(False)

# def update_annot(ind):
#     pos = ax.get_offsets()[ind["ind"]]
#     annot.xy = pos
#     text = "\n".join([labels[n] for n in ind["ind"]])
#     annot.set_text(text)

# def hover(event):
#     vis = annot.get_visible()
#     if event.inaxes == ax:
#         cont, ind = ax.contains(event)
#         if cont:
#             update_annot(ind)
#             annot.set_visible(True)
#             fig.canvas.draw_idle()
#         else:
#             if vis:
#                 annot.set_visible(False)
#                 fig.canvas.draw_idle()

#saving the hoverover
# p = figure(tools="hover")
# output_file("bokeh_plot.html")
# save(p)

# file that contains models used in courts scatter plot
# dir_coarse = '/uufs/chpc.utah.edu/common/home/strong-group7/court/maca/coarse_grid/'
# find_files = sorted(glob.glob(dir_coarse + '*.mat'))
# prefix = dir_coarse
# scatter_models = []
# for file in find_files:
#     no_prefix = file.replace(prefix, '')
#     model = no_prefix.split('_')[0]
#     if model not in scatter_models:
#         scatter_models.append(model)
        
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

