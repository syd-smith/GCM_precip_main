#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 30 18:29:48 2026

@author: u1301408
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.colors as mcolors 
from matplotlib.colors import Normalize
import numpy as np

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/tool_belt/')
from file_traversing import write2file, read_file


models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1', 'CanESM5',
          'EC-Earth3-AerChem', 'EC-Earth3-CC', 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4',
          'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'IITM-ESM', 'INM-CM4-8', 'INM-CM5-0', 'KACE-1-0-G', 'KIOST-ESM', 
          'MIROC-ES2H', 'MIROC-ES2L', 'MIROC6', 'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']

ssp585_models = ['ACCESS-CM2', 'ACCESS-ESM1-5', 'CMCC-ESM2', 'CNRM-CM6-1-HR', 'CNRM-CM6-1', 'CNRM-ESM2-1',
                 'CanESM5', 'EC-Earth3-CC', 'EC-Earth3-Veg-LR', 'EC-Earth3', 'GFDL-CM4', 'GFDL-ESM4', 'HadGEM3-GC31-LL',
                  'HadGEM3-GC31-MM', 'INM-CM4-8', 'INM-CM5-0', 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2H', 'MIROC6',
                   'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'UKESM1-0-LL']


def data_build(variable, season, model_list):
    """
    Compile bias and variance data for each model into a numpy array by reading
    it from a dictionary.
    """
    
    data = read_file('gcm_feb19.txt')
    
    bias = np.array([data[model][season]['bias'][variable] for model in model_list])
    var = np.array([data[model][season]['var_ratio'][variable] for model in model_list])
    
    return bias, var


def simple_taylor(bias, stdev_ratio, title, model_to_label = 'SKIP'):
    
    # find largest magnitude value in the dataset and normalize data to that value
    bias_max = abs(bias).max()
    bias_norm = bias / bias_max
    theta = np.pi - np.arccos(bias_norm) # data used for plotting
    
    # build a list of labels for the radial axis that is symetric to 0
    bias_lines = np.linspace(-bias_max, bias_max, 9)

    # manually set obs data point
    obs_bias = 0
    obs_stdev_ratio = 1

    # Setup polar plot: angle = arccos(bias), radius = standard deviation
    fig, axs = plt.subplots(subplot_kw={'projection': 'polar'}, figsize = (5, 5))

    # make the figure a semi-circle 
    axs.set_thetamin(0)
    axs.set_thetamax(180)
    axs.set_theta_zero_location('W')
    axs.set_theta_direction(-1)
    axs.spines['polar'].set_linewidth(0.5)
    axs.spines['polar'].set_edgecolor('black')
    
    # remove x axis
    axs.xaxis.grid(False)

    # Set axis limits and labels
    axs.set_ylim(0, 1.6)
    axs.set_yticks([0.5, 1.0, 1.5, 2.0, 2.5])
    axs.yaxis.grid(True, color = 'black', linewidth = 0.25, linestyle = '-.')
    axs.set_yticklabels([0.5, 1.0, 1.5, 2.0, 2.5], fontsize  = 50)
    
    # plot GCM data
    axs.scatter(theta, stdev_ratio, marker = 'o', edgecolors = 'k', linewidths = 0.25, s = 30)
    
    # highlight specific model
    if model_to_label != 'SKIP':
        for model, color in zip(model_to_label, ['green', 'yellow', 'red']):
            index = models.index(model)
            axs.plot(float(theta[index]), float(stdev_ratio[index]), marker = 'o', markeredgecolor = 'black', 
                     markerfacecolor  = color, markersize = 10, label = model)
        fig.legend(loc = 'lower center', bbox_to_anchor = (0.52, 0.09))
        
    # Plot point for reference data
    axs.plot(np.pi - np.arccos(obs_bias), obs_stdev_ratio, marker = '*', 
             markerfacecolor =  'none', markeredgecolor = 'k', markersize = 25)
    
    # normalize and generate lists of radial axis labels and lines
    tick_angles = []
    tick_labels = []
    for line in bias_lines:
        b_norm = line / bias_max
        angle = np.pi - np.arccos(b_norm)
        axs.plot([angle, angle], [0, 2.62], '-.', color='black', lw=0.5)
        tick_angles.append(angle)
        tick_labels.append(f'{line:.2f}')

    # plot labels and lines
    axs.set_xticks(tick_angles)
    axs.set_xticklabels(tick_labels, fontsize = 12)
    
    # add labels to right side of x axis
    r_ticks = [0.5, 1.0, 1.5, 2.0, 2.5]
    
    for r, move_it in zip(r_ticks, [1, 1.075 ,1.15, 1.23, 1.305]):
        # Default side (right/top, angle ~22.5° or wherever your main labels are)
        # Add labels on the left (angle = À radians)
        fig.text(-0.41 + move_it, 0.2705, f"{r}", ha = 'center', va = 'center', fontsize = 10.1, color =  'k')

    axs.set_title(title, fontsize = 20, pad = -25)
    
    return fig

# bias, stdev = data_build('tasmin', 'SON')
# tasmin = simple_taylor(bias, stdev, 'Fall Minimum Temperature', model_to_label = ['UKESM1-0-LL', 'HadGEM3-GC31-LL', 'KACE-1-0-G'])


def pr_taylor(bias, stdev_ratio, title, model_to_label = 'SKIP'):
    
    # find largest magnitude value in the dataset and normalize data to that value
    bias_max = abs(bias).max()
    bias_norm = bias / bias_max
    theta = np.pi - np.arccos(bias_norm) # data used for plotting
    
    # build a list of labels for the radial axis that is symetric to 0
    bias_lines = np.linspace(0, bias_max, 9)

    # manually set obs data point
    obs_bias = np.pi - np.arccos(1 / bias_max)
    obs_stdev_ratio = 1

    # Setup polar plot: angle = arccos(bias), radius = standard deviation
    fig, axs = plt.subplots(subplot_kw={'projection': 'polar'}, figsize = (5, 5))

    # make the figure a semi-circle 
    axs.set_thetamin(90)
    axs.set_thetamax(180)
    axs.set_theta_zero_location('W')
    axs.set_theta_direction(-1)
    axs.spines['polar'].set_linewidth(0.5)
    axs.spines['polar'].set_edgecolor('black')
    
    # remove x axis
    axs.xaxis.grid(False)

    # Set axis limits and labels
    axs.set_ylim(0, 1.6)
    axs.set_yticks([0.5, 1.0, 1.5, 2.0, 2.5])
    axs.yaxis.grid(True, color = 'black', linewidth = 0.25, linestyle = '-.')
    axs.set_yticklabels([0.5, 1.0, 1.5, 2.0, 2.5], fontsize  = 50)
    
    # plot GCM data
    axs.scatter(theta, stdev_ratio, marker = 'o', edgecolors = 'k', linewidths = 0.25, s = 30)
    
    # highlight specific model
    if model_to_label != 'SKIP':
        for model, color in zip(model_to_label, ['green', 'yellow', 'red']):
            index = models.index(model)
            axs.plot(float(theta[index]), float(stdev_ratio[index]), marker = 'o', markeredgecolor = 'black', 
                     markerfacecolor  = color, markersize = 10, label = model)
        fig.legend(loc = 'upper right', bbox_to_anchor = (0.97, 0.95))
        
    # Plot point for reference data
    axs.plot(obs_bias, obs_stdev_ratio, marker = '*', 
             markerfacecolor = 'none', markeredgecolor = 'k', markersize = 30)
    
    # normalize and generate lists of radial axis labels and lines
    tick_angles = []
    tick_labels = []
    for line in bias_lines:
        b_norm = line / bias_max
        angle = np.pi - np.arccos(b_norm)
        axs.plot([angle, angle], [0, 2.62], '-.', color='black', lw=0.5)
        tick_angles.append(angle)
        tick_labels.append(f'{line:.2f}')

    # plot labels and lines
    axs.set_xticks(tick_angles)
    axs.set_xticklabels(tick_labels, fontsize = 12)
    
    axs.set_title(title, fontsize = 16, pad = 10)
    
    return fig

# for season, label in zip(['yearly', 'DJF', 'MAM', 'JJA', 'SON'], ['Annual', 'Winter', 'Spring', 'Summer', 'Fall']):
#     bias, stdev = data_build('pr', season)
#     pr = pr_taylor(bias, stdev, f'{label} Precipitation', model_to_label = ['UKESM1-0-LL', 'HadGEM3-GC31-LL', 'KACE-1-0-G'])