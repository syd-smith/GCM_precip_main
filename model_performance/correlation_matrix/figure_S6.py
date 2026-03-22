#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  5 13:42:47 2026

@author: u1301408
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import sys

# ==================================
# - Establish Relative File Path - 
# ==================================

current_file_directory = Path(__file__).resolve().parent
parent_directory = current_file_directory.parent.parent
sys.path.append(str(parent_directory))

from model_performance.correlation_matrix.seasonal_matrix import mk_df


# ===============
#  - Constants - 
# ===============

# creates dataframe with summer data from ssp585  models
data = mk_df(['pr', 'tasmin', 'tasmax'], 'JJA', 'ssp585')


# ==============
# - Functions - 
# ==============

def heteroskedasticity_graphs():
    """
    Create two graphs showing projected precipitation as a function of historical
    model performance. These graphs are meant to outline the heteroskedastic 
    nature of the dataset where a wider range of y values is exhibited when the 
    x value is smaller.
    """
    
    # defines the axes for each plot
    x1 = 'pr bias'
    x2 = 'pr var'
    y = 'projected precip'
    
    # initializes the ploting function outlining that there are two subplots
    fig, axs = plt.subplots(1, 2, figsize = (12, 5))
    
    ###  plot #1 - pr bias vs. projected pr ###
    m1, b1 = np.polyfit(data[x1], data[y]/100, 1) 
    axs[0].plot(data[x1], m1*data[x1]+b1, '-', color  = 'red') # plot a regression  line
    axs[0].scatter(data[x1], data[y]/100) # display both axes as a ratio
    axs[0].set_xlabel('Precipitation Bias')
    axs[0].set_ylabel('Projected Precipitation')
    axs[0].text(0.03, 0.92, 'a.', transform = axs[0].transAxes, fontsize = 15)
    
    ### plot #2 - pr varriance ratio vs. projected pr ###
    m2, b2 = np.polyfit(data[x2], data[y]/100, 1)
    axs[1].plot(data[x2], m2*data[x2]+b2, '-', color  = 'red')
    axs[1].scatter(data[x2], data[y]/100)
    axs[1].set_xlabel('Precipitation Variance Ratio')
    axs[1].set_ylabel('Projected Precipitation')
    axs[1].text(0.03, 0.92, 'b.', transform = axs[1].transAxes, fontsize = 15)

    return fig


# ================
# - Entry Point - 
# ================

def main():
    heteroskedasticity_graphs()
    
if __name__ == '__main__':
    main()