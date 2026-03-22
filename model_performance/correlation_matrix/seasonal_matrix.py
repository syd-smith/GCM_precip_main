#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  3 12:45:42 2026

@author: u1301408
"""

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import pearsonr
import seaborn as sb
import sys

# ==================================
# - Establish Relative File Path - 
# ==================================

current_file_directory = Path(__file__).resolve().parent
parent_directory = current_file_directory.parent.parent
sys.path.append(str(parent_directory))

from tool_belt.file_traversing import read_file


# ===============
#  - Constants - 
# ===============

models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5',
          'EC-Earth3-AerChem', 'EC-Earth3-CC', 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4',
          'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'IITM-ESM', 'INM-CM4-8', 'INM-CM5-0', 'KACE-1-0-G', 'KIOST-ESM', 
          'MIROC-ES2H', 'MIROC-ES2L', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']

ssp585_models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1',
                 'CanESM5', 'EC-Earth3-CC', 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL',
                  'HadGEM3-GC31-MM', 'INM-CM4-8', 'INM-CM5-0', 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC6',
                   'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']

ssp370_models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5', 'EC-Earth3-AerChem',
                 'EC-Earth3-Veg-LR', 'GFDL-ESM4', 'INM-CM4-8', 'INM-CM5-0', 'KACE-1-0-G', 'MIROC-ES2H', 'MIROC-ES2L',
                  'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']

ssp245_models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5', 'EC-Earth3-CC',
                 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL', 'INM-CM4-8', 'INM-CM5-0',
                  'KACE-1-0-G', 'MIROC-ES2H', 'MIROC-ES2L', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']

ssp126_models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1',
                 'CanESM5', 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-ESM4', 'HadGEM3-GC31-LL', 'IITM-ESM',
                 'INM-CM4-8', 'INM-CM5-0', 'KACE-1-0-G', 'MIROC-ES2H', 'MIROC-ES2L', 'MIROC6', 'MPI-ESM1-2-HR',
                 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']


# ==============
# - Functions - 
# ==============

def mk_df(variables, season, ssp):
    """
    Create pandas dataframe of data you want displayed in correlation matrix.
    """
    
    historical = read_file('gcm_feb19.txt')
        # model -> season -> bias/stdev -> variable
    projections = read_file('projections_feb10.txt')
        # ssp -> model -> season -> projection
        
    if ssp == 'ssp126':
        model_list = ssp126_models
    elif ssp == 'ssp245':
        model_list = ssp245_models
    elif ssp == 'ssp370':
        model_list = ssp370_models
    elif ssp == 'ssp585':
        model_list = ssp585_models
    else:
        model_list = models
        print('Projection not defined.')
    
    df_list = []
    for model in model_list:
        per_model = []
        for variable in variables:
            per_model.append(historical[model][season]['bias'][variable])
            per_model.append(historical[model][season]['var_ratio'][variable])
        per_model.append(projections[ssp][model][season]['pr'])
        per_model.append(projections[ssp][model][season]['tasmin'])
        per_model.append(projections[ssp][model][season]['tasmax'])
        df_list.append(per_model)
        
    # assign column names to the dataframe
    base_cols = ['projected precip', 'projected tasmin', 'projected tasmax']
    col_names = ([name for v in variables for name in (f'{v} bias', f'{v} var')] + base_cols)
    df = pd.DataFrame(df_list, columns = col_names)
    
    return df

def expanded_df(variables, season, ssp):
    """
    Create pandas dataframe of data you want displayed in correlation matrix.
    """
    
    historical = read_file('gcm_feb19.txt')
        # model -> season -> bias/stdev -> variable
    projections = read_file('projections_feb10.txt')
        # ssp -> model -> season -> projection
    lag_one = read_file('lag_one_feb23.txt')
        # model -> season -> variable
        
    if ssp == 'ssp126':
        model_list = ssp126_models
    elif ssp == 'ssp245':
        model_list = ssp245_models
    elif ssp == 'ssp370':
        model_list = ssp370_models
    elif ssp == 'ssp585':
        model_list = ssp585_models
    else:
        model_list = models
        print('Projection not defined.')
    
    df_list = []
    for model in model_list:
        per_model = []
        for variable in variables:
            per_model.append(historical[model][season]['bias'][variable])
            per_model.append(historical[model][season]['var_ratio'][variable])
            per_model.append(lag_one[model][season][variable]['lag_one'])
        per_model.append(projections[ssp][model][season]['precip_ratio'])
        per_model.append(projections[ssp][model][season]['delta_tasmin'])
        per_model.append(projections[ssp][model][season]['delta_tasmax'])
        df_list.append(per_model)
        
    # assign column names to the dataframe
    base_cols = ['projected precip', 'projected tasmin', 'projected tasmax']
    col_names = ([name for v in variables for name in (f'{v} bias', f'{v} var', f'{v} lag-one')] + base_cols)
    df = pd.DataFrame(df_list, columns = col_names)
    
    return df

def corr_pvalues(df):
    cols = df.columns
    pvals = np.zeros((len(cols), len(cols)))

    for i, col_i in enumerate(cols):
        for j, col_j in enumerate(cols):
            r, p = pearsonr(df[col_i], df[col_j])
            pvals[i, j] = p

    return pd.DataFrame(pvals, index = cols, columns = cols)

def correlation_matrix(df, mask = False, pvals = True, title = 'SKIP'):
    
    # create correlation matrix with pearson r values (plus mask to hide half the square)
    corr_matrix =  df.corr(method  = 'pearson').round(2)
    
    if mask == True:
        mask = np.triu(np.ones_like(corr_matrix, dtype = bool))
    else:
        mask = np.eye(corr_matrix.shape[0], dtype=bool)

    if pvals == True:
        # significance level
        alpha = 0.05
        pvalues = corr_pvalues(df)
    
        # label for box is a star if less than alpha (statistically significant)
        annot = np.where(pvalues.values < alpha, '*', '').astype(object)
    else:
        annot = None

    # add specifications for the colorbar
    levels = np.array([-1, -0.75, -0.5, -0.25, 0, 0.25, 0.5,  0.75, 1])
    norm = mcolors.BoundaryNorm(levels, ncolors = plt.get_cmap('RdBu', 8).N) # 9 bins means 8 edges
        
    # set figure size and call heatmmap
    plt.figure(figsize = (10, 10))
    matrix = sb.heatmap(corr_matrix, 
                           cmap = 'RdBu_r', 
                           vmin = -1, 
                           vmax = 1, 
                           annot = annot, 
                           fmt = '', 
                           square = True, 
                           mask = mask, 
                           cbar = False, 
                           annot_kws = dict(color = 'black',
                                            fontsize = 35,
                                            va = 'center'))

    # pull mappable from matrix to pass in colorbar
    mappable = matrix.collections[0]

    # set colorbar
    cbar = plt.colorbar(mappable, 
                               orientation = 'vertical', 
                               ticks = levels, 
                               shrink = 0.75, 
                               pad = 0.1,
                               boundaries = levels)
    # round labels to two decimal places
    cbar.ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))
    
    if title != 'SKIP':
        plt.title(title, size = 30, pad = 20)
    
    return plt.show()


# ================
# - Entry Point - 
# ================

def main():
    # creates a pandas dataframe that organizes specific GCMM data read out of a dictionary
    dataframe = mk_df(['pr', 'tasmin', 'tasmax', 'huss', 'rsds', 'uas', 'vas'], 'JJA', 'ssp585')
    
    # creates another dataframe that includes more calculations
    expanded_dataframe  = expanded_df(['pr', 'tasmin', 'tasmax', 'huss', 'rsds', 'uas', 'vas'], 'JJA', 'ssp585')

    # plot above dataframes into correlation matrixes
    normal_martix = correlation_matrix(dataframe)
    expanded_matrix = correlation_matrix(expanded_dataframe)

# if __name__ == '__main__':
#     main()

