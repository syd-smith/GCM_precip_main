#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 10:33:53 2026

@author: u1301408
"""

import numpy as np
from pathlib import Path
from scipy.stats import pearsonr
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan, het_white
import sys 


# ==================================
# - Establish Relative File Path - 
# ==================================

current_file_directory = Path(__file__).resolve().parent
print(f'CURRENT FILE DIRECTORY: {current_file_directory}')
parent_directory = current_file_directory.parent
sys.path.append(str(parent_directory))

from model_performance.correlation_matrix.seasonal_matrix import mk_df
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

emission_scenarios = ['ssp119', 'ssp126', 'ssp245', 'ssp370', 'ssp434', 'ssp585']
MACA_data = read_file('projections_feb10.txt') # calculations over the entire MACA dommain
GSLB_data = read_file('oct_19.txt','JJA_climate_change') # calculations specific to  the GSLB

# Pearson R and P values of correlation between GSLB and MACA region
MACA = np.array([])
GSLB =  np.array([])
for model in models:
    print(model)
    for emission_scenario in emission_scenarios:
        print(emission_scenario)
        try:
            #  read out specific data point - GSLB_value will be cast to a float later 
            GSLB_value = GSLB_data[model][emission_scenario]['precip_ratio']
            #  cast data as a float and divide by 100 to make it a ratio not percentage
            MACA_value = float(MACA_data[emission_scenario][model]['JJA']['pr'])
            
            if GSLB_value == 'File Not Found':
                print(f'Skipping {model} {emission_scenario}: missing data.')
                continue
            
            GSLB =  np.append(GSLB, float(GSLB_value))
            MACA = np.append(MACA, MACA_value)
            print(f'Added {model} {emission_scenario}: GSLB={float(GSLB_value)}, MACA={MACA_value}')
                
        except KeyError:
            print(f'{model} {emission_scenario}: Key not found in one of the MACA dataset.')
            continue
        
# calculate the correlation between the two datasets        
values = pearsonr(GSLB, MACA)
r  = float(values[0])
p =  float(values[1])


#%%
# ==============
# - Functions - 
# ==============

def MACA_vs_GSLB_correlation():
    """
    Tests the correlation between the precipitation ratios (futue precip/ 
    historical precip) calculated over the GSLB and MACA regions. 
    """
    
    # Pearson R and P values of correlation between GSLB and MACA region
    MACA = np.array([])
    GSLB =  np.array([])
    for model in models:
        print(model)
        for emission_scenario in emission_scenarios:
            print(emission_scenario)
            try:
                #  read out specific data point - GSLB_value will be cast to a float later 
                GSLB_value = GSLB_data[model][emission_scenario]['precip_ratio']
                #  cast data as a float and divide by 100 to make it a ratio not percentage
                MACA_value = float(MACA_data[emission_scenario][model]['JJA']['precip_ratio']) / 100
                
                if GSLB_value == 'File Not Found':
                    print(f'Skipping {model} {emission_scenario}: missing data.')
                    continue
                
                GSLB =  np.append(GSLB, float(GSLB_value))
                MACA = np.append(MACA, MACA_value)
                print(f'Added {model} {emission_scenario}: GSLB={float(GSLB_value)}, MACA={MACA_value}')
                    
            except KeyError:
                print(f'{model} {emission_scenario}: Key not found in one of the MACA dataset.')
                continue
            
    # calculate the correlation between the two datasets        
    values = pearsonr(GSLB, MACA)
    r  = float(values[0])
    p =  float(values[1])
    
    return r, p

def bias_vs_pr_ratio():
    """
    Tests for correlation between precipitation bias and variance ratio. 
    """
    
    # read out stored data
    check = read_file('gcm_feb19.txt')
    # pull bias values for all models
    bias = np.array([check[model]['JJA']['bias']['pr'] for model in ssp585_models])
    # pull variance ratio values for all models
    var =  np.array([check[model]['JJA']['var_ratio']['pr'] for model in ssp585_models])
    #calculate correlation
    values = pearsonr(bias, var)
    r  = float(values[0]) # isloate pearson r value
    p =  float(values[1]) # isolate p-value
    
    return r, p

def heteroskedasticity_test():
    # creates dataframe with summer data from ssp585  models read out of gcm_feb19.txt and projections_feb10.txt
    data = mk_df(['pr', 'tasmin', 'tasmax'], 'JJA', 'ssp585')
    
    # Breusch-Pagan test for heteroskedasticity on pr bias vs. projected pr
    bias = sm.add_constant(data['pr bias'])
    results = sm.OLS(data['projected precip'], bias).fit()
    # print(results.summary())
    
    residuals = results.resid
    exog = results.model.exog
    
    # Return order: LM value, LM p-value, F value,  F p-value
    bp_test = het_breuschpagan(residuals, exog) 
    white_test = het_white(residuals, exog)
    
    return bp_test, white_test
   

# ================
# - Entry Point - 
# ================

def main():
        # MACA vs. GSLB correlation
        region_R, region_P = MACA_vs_GSLB_correlation()
        print('Correlation between precipitation ratios in the MACA domain vs. GSLB')
        print(f'r={region_R}')
        print(f'p-value={region_P}')
        
        # bias vs. variance ratio correlation
        mod_perform_R, mod_perform_P = bias_vs_pr_ratio()
        print('Correlation between SSP5-8.5 models historical precipitation bias and variance ratio')
        print(f'r={mod_perform_R}')
        print(f'p={mod_perform_P}')
        
        # test for heteroskedasticity between historical model performance and projected precipitation
        bp_test, white_test = heteroskedasticity_test()
        print('Breusch-Pagan Test for heteroskedasticity')
        print(f'Lagrange Multiplier Statistic: {float(bp_test[0])} | LM P-Value: {float(bp_test[1])}')
        print(f'F-Statistic: {float(bp_test[2])} | F-Statistic P-Value: {float(bp_test[3])}')
        print('White Test for heteroskedasticity')
        print(f'Lagrange Multiplier Statistic: {float(white_test[0])} | LM P-Value: {float(white_test[1])}')
        print(f'F-Statistic: {float(white_test[2])} | F-Statistic P-Value: {float(white_test[3])}')
        # all findings were staatistically significant
        
if __name__ == '__main__':
    main()

    


