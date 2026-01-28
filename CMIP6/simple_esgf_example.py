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

# intake_esgf.conf.set(xarray_open_kwargs = {"use_cftime": True})

intake_esgf.conf.set(all_indices = True) #if true then searches all servers
intake_esgf.conf.set(indices={"esg-dn1.nsc.liu.se": False}) 
intake_esgf.conf.set(indices={"esgf-data.dkrz.de": False})
intake_esgf.conf.set(indices={"esgf-node.ipsl.upmc.fr": False}) 
intake_esgf.conf.set(indices={"esgf-node.llnl.gov": True})
intake_esgf.conf.set(indices={"esgf-node.ornl.gov": False})
intake_esgf.conf.set(indices={"esgf.ceda.ac.uk": False})
intake_esgf.conf.set(indices={"esgf.nci.org.au": False})
cat = intake_esgf.ESGFCatalog()

# surface_air_pressure
variables_to_check  = ['ps']

# list of models used in MACA process
models_to_check = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 
                   'CanESM5', 'EC-Earth3-AerChem', 'EC-Earth3-CC', 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4',
                   'GFDL-ESM4', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'IITM-ESM', 'INM-CM4-8', 'INM-CM5-0',
                   'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC-ES2L', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR',
                   'MRI-ESM2-0', 'UKESM1-0-LL']

# used to look at multiple emission scenarios
# set ssp = ssps
ssps = ['ssp119', 'ssp126', 'ssp245', 'ssp434', 'ssp370', 'ssp585']

cat=cat.search(
    source_id = models_to_check[0],
    # activity_id = ['ScenarioMIP'],
    # activity_id = ['CMIP'], # for historical
    experiment_id = ssps[1],
    # experiment_id=['historical'], # xu18_ssp, 
    # member_id = 'r1i1p1f1',
    # table_id=["6hrPlevPt","6hrPlev","3hr"],
    # table_id='month',
    table_id = 'Amon',
    variable_id = variables_to_check,
    grid_label='gn'
    )


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
ds = cat.to_dataset_dict(add_measures = False)

# MPI 126, 245, 370, 'ssp585'
# MIROC6 126 245, 370, 585
# multi: 245 585 /uufs/chpc.utah.edu/common/home/strong-group7/husile/gsl/cmip_data/bias_corrected_cmip6


