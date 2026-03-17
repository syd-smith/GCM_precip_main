#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 29 11:52:03 2025

@author: u1301408
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.ticker as ticker
import numpy as np
from pathlib import Path
import sys

# ==================================
# - Establish Relative File Path - 
# ==================================

current_file_directory = Path(__file__).resolve().parent
parent_directory = current_file_directory.parent.parent
sys.path.append(str(parent_directory))

from tool_belt.file_traversing import read_file


# ==============
# - Functions - 
# ==============

def read_in_PC(dictionary_name):
    
    # read in PC data from tabular format in Savanna's .csv file
    df = pd.read_csv(parent_directory.joinpath('from_savanna', 'PCs_zscore_column.csv'))
    scatter_framework = read_file(dictionary_name, 'JJA_climate_change')

    # _refers to the rows while rows really refers to the columns
    for row, col in df.iterrows():
        model = col['Model']
        ssp = col['Exp']
        
        record = {
            # keep temp and precip data the same as original dictionary but read in PC data
            'delta_temp' : scatter_framework[model][ssp]['delta_temp'],
            'precip_ratio' : scatter_framework[model][ssp]['precip_ratio'],
            'PC1' : float(col['PC1']),
            'PC2' : float(col['PC2'])}
        
        # input PC data into the dictionary framework foound in reference_data.py (use this dictionary to compile more data with the calculations below)
        scatter_framework.setdefault(model, {})[ssp] = record
    
    return scatter_framework

def plot_data(dictionary_name, save = True, save_name = 'figure4.png'):
    """
    Plot climate change scatter plot but shaded by either PC1 or PC2 data.
    """
    
    # establish figure for subplots
    fig, axs = plt.subplots(1, 2, figsize = (13.5, 6))
    
    # loop through dictionary to pull out necessary data for scatter
    for model in dictionary_name:
        for scenario in dictionary_name[model]:
            if dictionary_name[model][scenario]['delta_temp'] == 'File Not Found' or dictionary_name[model][scenario]['precip_ratio'] == 'File Not Found':
                continue
            # adjust color of data point relative to PC value
            PC1_scatter = axs[0].scatter(dictionary_name[model][scenario]['delta_temp'], 
                                  dictionary_name[model][scenario]['precip_ratio'], 
                                  c = dictionary_name[model][scenario]['PC1'], 
                                  cmap = plt.get_cmap('viridis', 9), 
                                  s = 30, 
                                  norm = mcolors.Normalize(vmin = -10, vmax = 18))
            PC2_scatter = axs[1].scatter(dictionary_name[model][scenario]['delta_temp'], 
                                  dictionary_name[model][scenario]['precip_ratio'], 
                                  c = dictionary_name[model][scenario]['PC2'], 
                                  cmap = plt.get_cmap('viridis', 9), 
                                  s = 30, 
                                  norm = mcolors.Normalize(vmin = -5, vmax = 6))
            
    # loop through both subplots to add visual features        
    for ax in [0, 1]:        
        # axis ticks and labels
        axs[ax].set_yticks([0.5, 1.0, 1.5, 2.0])
        axs[ax].set_yticklabels([0.5, 1, 1.5, 2])
        axs[ax].set_xticks([0, 5, 10])
        axs[ax].tick_params(axis = 'x', labelsize=12)
        axs[ax].tick_params(axis = 'y', labelsize=12)
    
        # set horizontal and vertical lines
        axs[ax].axhline(y = 0.5, color = 'lightgray', linewidth = 0.7)
        axs[ax].axhline(y = 1.0, color = 'lightgray', linewidth = 0.7)
        axs[ax].axhline(y = 1.5, color = 'lightgray', linewidth = 0.7)
        axs[ax].axhline(y = 2.0, color = 'lightgray', linewidth = 0.7)
        axs[ax].axvline(x = 0, color = 'lightgray', linewidth = 0.7)
        axs[ax].axvline(x = 5, color = 'lightgray', linewidth = 0.7)
        axs[ax].axvline(x = 10, color = 'lightgray', linewidth = 1.15)
    
        # remove the black outlines around the graph
        for spine in axs[ax].spines.values():
            spine.set_visible(False)
        axs[ax].tick_params(axis='both', which='both', length=0)
    
        # labels for the graph
        axs[ax].set_xlabel('Temperature Change (K)', fontsize = 16)
        axs[ax].set_ylabel('Precipitation Ratio', fontsize = 16)
    
    # define norm and levels for PC1
    PC1_levels = np.linspace(-10, 18, 9)
   
    # creating a color bar and legend for PC1 and PC2 data
    PC1_cbar = plt.colorbar(PC1_scatter, 
                               orientation = 'horizontal', 
                               ticks = PC1_levels, 
                               shrink = 0.5, 
                               pad = 0.15,
                               extend = 'both',
                               boundaries = PC1_levels)
    PC1_cbar.ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
    
    # define norm and levels for PC2
    PC2_levels = np.linspace(-5, 6, num = 9)
    
    PC2_cbar = plt.colorbar(PC2_scatter, 
                               orientation = 'horizontal', 
                               ticks = PC2_levels, 
                               shrink = 0.5, 
                               pad = 0.15,
                               extend = 'both', 
                               boundaries = PC2_levels)
    PC2_cbar.ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
    
    # add labels to each subplot
    axs[0].text(0.05, 0.85, 'a.', fontsize = 20, transform = axs[0].transAxes)
    axs[1].text(0.05, 0.85, 'b.', fontsize = 20, transform = axs[1].transAxes)
    
    if save:
        # save figure
        save_path = current_file_directory.joinpath(save_name)
        fig.savefig(save_path, dpi = 400, bbox_inches = 'tight', pad_inches = 0.1)
    
    plt.show()


# ================
# - Entry Point - 
# ================

def main():
    # save PC data to a dictionary structure in a .txt file
    read_in_PC('oct_19.txt')
    
    # Open and read the file
    data = read_file('oct_19.txt', 'JJA_climate_change')
    
    # call function to create scatter plot and fill with data from dictionary
    plot_data(data)
    
if __name__ == '__main__':
    main()



