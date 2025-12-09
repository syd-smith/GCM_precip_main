#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 27 12:10:16 2025

@author: u1301408
"""

import intake_esgf
import sys
import os
import glob
import regex as re
import numpy as np
import xarray as xr
import pandas as pd
import calendar
from sklearn.linear_model import LinearRegression
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm #, ListedColormap
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['text.usetex'] = False
mpl.rcParams['savefig.format'] = 'pdf'
mpl.pyplot.rcParams['figure.constrained_layout.use'] = True
from scipy import stats
import scipy.io
from scipy.stats import ttest_ind
from scipy.stats import pearsonr
from cartopy.util import add_cyclic_point
import cartopy.crs as ccrs
import matplotlib.ticker as ticker
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
from cartopy.feature import ShapelyFeature
import geopandas as gpd
import calendar
import warnings
from shapely.errors import ShapelyDeprecationWarning
warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning) 
import cmocean
from bokeh.plotting import figure, output_file, save
import xesmf as xe
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/from_savanna/')
import nclcmaps as cmap
import rioxarray 
from shapely.geometry import mapping
from matplotlib.patches import FancyBboxPatch
import pprint
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.projections import PolarAxes
# import mpl.toolkits.axisartist.floating_axes as fa 
# import mpl.toolkits.axisartist.grid_finder as gf 
import seaborn as sb



