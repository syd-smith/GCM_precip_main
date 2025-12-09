#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  8 20:37:00 2025

@author: u1301408
"""

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/packages')
import base_packages as bp
import ast

MACA_models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5', 'EC-Earth3-CC',
 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'INM-CM4-8', 'INM-CM5-0',
 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']

# Open and read the file
bp.os.chdir('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/GCM_bias')
with open('gcm_dict_dec_3.txt', 'r') as f:
    contents = f.read()

# Convert from string representation to actual dictionary
gcm_dict = ast.literal_eval(contents)

#%%

df_list = []

# order = ['Precipitation Ratio', 'Change in Max Temperature',  'Change in Min Temperature', ]

for model in MACA_models:
    per_model = []
    per_model.append(gcm_dict[model]['pr_ratio'])
    per_model.append(gcm_dict[model]['tasmax_change'])
    per_model.append(gcm_dict[model]['tasmin_change'])
    per_model.append(gcm_dict[model]['summer_bias']['pr'])
    per_model.append(gcm_dict[model]['JJA_stdev_ratio']['pr'])
    per_model.append(gcm_dict[model]['summer_bias']['tasmax'])
    per_model.append(gcm_dict[model]['JJA_stdev_ratio']['tasmax'])
    per_model.append(gcm_dict[model]['summer_bias']['tasmin'])
    per_model.append(gcm_dict[model]['JJA_stdev_ratio']['tasmin'])
    df_list.append(per_model)
    
# note: all calculations are for JJA
df = bp.pd.DataFrame(df_list, columns = ['Precip Ratio', 'Delta Tasmax', 'Delta Tasmin', 'Precip Bias', 'Precip StDev Ratio', 'Tasmax Bias', 'Tasmax StDev Ratio', 'Tasmin Bias', 'Tasmin StDev Ratio'])

def corr_pvalues(df):
    cols = df.columns
    pvals = bp.np.zeros((len(cols), len(cols)))

    for i, col_i in enumerate(cols):
        for j, col_j in enumerate(cols):
            r, p = bp.pearsonr(df[col_i], df[col_j])
            pvals[i, j] = p

    return bp.pd.DataFrame(pvals, index=cols, columns=cols)

pvalues = corr_pvalues(df)

# significance level
alpha = 0.05
# label for box is a star if less than alpha (statistically significant)
annot = bp.np.where(pvalues.values < alpha, '*', '').astype(object)

# create correlation matrix with pearson r values (plus mask to hide half the square)
corr_matrix =  df.corr(method  = 'pearson').round(2)
mask = bp.np.triu(bp.np.ones_like(corr_matrix, dtype = bool))

# add specifications for the colorbar
levels = bp.np.array([-1, -0.75, -0.5, -0.25, 0, 0.25, 0.5,  0.75, 1])
norm = bp.mcolors.BoundaryNorm(levels, ncolors = bp.plt.get_cmap('RdBu', 8).N) # 9 bins means 8 edges
    
# set figure size and call heatmmap
bp.plt.figure(figsize = (10, 10))
matrix = bp.sb.heatmap(corr_matrix, 
                       cmap = 'RdBu', 
                       vmin = -1, 
                       vmax = 1, 
                       annot = True, 
                       fmt = '0.2f', 
                       square = True, 
                       mask = mask, 
                       cbar = False)

# pull mappable from matrix to pass in colorbar
mappable = matrix.collections[0]

# set colorbar
cbar = bp.plt.colorbar(mappable, 
                           orientation = 'vertical', 
                           ticks = levels, 
                           shrink = 0.75, 
                           pad = 0.1,
                           boundaries = levels)
# round labels to two decimal places
cbar.ax.xaxis.set_major_formatter(bp.ticker.FormatStrFormatter('%.2f'))

bp.plt.show()





