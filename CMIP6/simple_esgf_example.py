#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  6 10:34:56 2025

@author: u1215181
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 31 11:13:47 2024

@author: u0660911
"""
import intake_esgf

intake_esgf.conf.set(all_indices = False) #if true then searches all servers
intake_esgf.conf.set(indices={"esg-dn1.nsc.liu.se": False}) 
intake_esgf.conf.set(indices={"esgf-data.dkrz.de": False})
intake_esgf.conf.set(indices={"esgf-node.ipsl.upmc.fr": False}) 
intake_esgf.conf.set(indices={"esgf-node.llnl.gov": False})
intake_esgf.conf.set(indices={"esgf-node.ornl.gov": False})
intake_esgf.conf.set(indices={"esgf.ceda.ac.uk": False})
intake_esgf.conf.set(indices={"esgf.nci.org.au": False})
cat = intake_esgf.ESGFCatalog()

# some variables that can be used
# variables_to_check = ['tas', 'huss', 'ps', 'psl', 'vas', 'uas', 'ts', 'mrsos', 'tsl','hus', 'ta', 'va', 'ua', 'zg', 'mrsol']
# currently looking for precipitation
variables_to_check  = ['zg']

# used to look at multiple emission scenarios
# set ssp = ssps
# ssps = ['historical', 'ssp119', 'ssp126', 'ssp245', 'ssp434', 'ssp370', 'ssp534-over','ssp585']

# single emission scenario as used in data analysis
ssp = 'ssp585'


cat=cat.search(
    source_id = 'HadGEM3-GC31-MM',
    activity_id = ['ScenarioMIP'],
    # activity_id = ['CMIP'], 
    experiment_id = [ssp],
    # experiment_id=['historical'], # xu18_ssp, 
    member_id = 'r1i1p1f3',
    # table_id=["6hrPlevPt","6hrPlev","3hr"],
    # table_id='month',
    table_id = 'Amon',
    variable_id = variables_to_check
    # grid_label='gr1'
    )

#%%
# cat=cat.search(
#     source_id='MPI-ESM1-2-HR',
#     experiment_id=['ssp126','ssp245','ssp370','ssp585'],
#     member_id='r1i1p1f1',
#     # table_id=["6hrPlevPt","3hr"],
#     table_id=["Amon"],
#     variable_id=['pr','tas']
#     # grid_label='gr1'
#     )

cat.remove_ensembles()
varis = cat.df['variable_id'].unique()
print(varis)
print(len(varis))
ds = cat.to_dataset_dict(add_measures=False)

# MPI 126, 245, 370, 'ssp585'
# MIROC6 126 245, 370, 585
# multi: 245 585 /uufs/chpc.utah.edu/common/home/strong-group7/husile/gsl/cmip_data/bias_corrected_cmip6

# import xarray as xr 

# fpath = '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/intake_esgf/CMIP6/ScenarioMIP/NIMS-KMA/KACE-1-0-G/ssp585/r1i1p1f1/day/huss/gr/v20190920/'
# open = xr.open_dataset(fpath + 'huss_day_KACE-1-0-G_ssp585_r1i1p1f1_gr_20150101-21001230.nc')
# sliced = open['huss'].sel(lat = slice(39.55, 42.84), lon = slice(246.31, 259.41))

