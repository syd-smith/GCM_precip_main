#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  3 09:35:25 2023

@author: u0660911
"""
import numpy as np
import xarray as xr
from sklearn.linear_model import LinearRegression
import matplotlib as mpl
# import matplotlib.pyplot as plt
# from matplotlib.colors import TwoSlopeNorm, ListedColormap
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['text.usetex'] = False
mpl.rcParams['savefig.format'] = 'pdf'
mpl.pyplot.rcParams['figure.constrained_layout.use'] = True
from scipy.stats import t, zscore
#from eofs.xarray import Eof
# from court_analyze import linregress_3d
# from cartopy.util import add_cyclic_point
# import cartopy.crs as ccrs
# import matplotlib.ticker as mticker
# from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
# import cartopy.feature as cfeature
# import sys 
import pandas as pd
# import matplotlib.colors as mcolors

def cpc_to_pandas(fname,var_name):
    # convert standard PSL format (year x month) to pandas
    nino = np.loadtxt(fname) 
    start_date = str(round(nino[0,0])) + '-01-01'
    end_date = str(round(nino[-1,0])) + '-12-31'
    date_range = pd.date_range(start=start_date, end=end_date, freq='M')
    df = pd.DataFrame(index=date_range,data=nino[:,1:].reshape(-1))
    df.columns = [var_name]
    return df
    
def wrapTo360(lons):
    lons_positive = [lon + 360 if lon < 0 else lon for lon in lons]
    return lons_positive

def wrapTo180(lons):
    lons = (lons + 180) % 360 - 180
    return lons

def round_to_eng(number):
    if number == 0:
        return 0
    
    order_of_magnitude = int(np.floor(np.log10(abs(number))))
    rounded_number = round(number / 10**order_of_magnitude)
    return int(rounded_number) * 10**order_of_magnitude

#%% regression, detrend, etc. 
def my_eof(dat,n=3,zscore=False):
    # eofs, pcs, varfrac = my_eof(dat,n=3)
    if zscore:
        dat = ((dat - dat.mean(dim='time')) / dat.std(dim='time'))
    lat = dat['lat'].values
    wgts   = np.cos(np.deg2rad(lat))
    wgts   = wgts.reshape(len(wgts), 1)
#    solver = Eof(dat, weights=wgts)
#    eofs = solver.eofsAsCorrelation(neofs=n)
    pcs  = solver.pcs(npcs=n, pcscaling=1)
    varfrac = solver.varianceFraction()
#    return eofs, pcs, varfrac

def my_mca(x,y,type='cov'):      
    # x_patt, y_patt, x_ind, y_ind, scf = my_mca(x,y,type='cov')
    ntime, nrow_x, ncol_x = x.shape
    nrow_y, ncol_y = y.shape[1:3]
    
    x_lon, x_lat = np.meshgrid(x['lon'],x['lat'])
    x_wgts   = np.cos(np.deg2rad(x_lat))
    x_wgts = np.reshape(x_wgts,-1,order='F')
    
    x_2d = x.values
    x_2d = np.reshape(x_2d, (ntime, nrow_x*ncol_x), order='F')
    x_2d = x_2d*x_wgts
    
    y_lon, y_lat = np.meshgrid(y['lon'],y['lat'])
    y_wgts = np.cos(np.deg2rad(y_lat))
    y_wgts = np.reshape(y_wgts,-1,order='F')
    
    y_2d = y.values
    y_2d = np.reshape(y_2d, (ntime, nrow_y*ncol_y), order='F')
    y_2d = y_2d*y_wgts
    
    x_nonMissingIndex = np.where(np.isnan(x_2d[0]) == False)[0]
    x_NoMissing = x_2d[:, x_nonMissingIndex]
    y_nonMissingIndex = np.where(np.isnan(y_2d[0]) == False)[0]
    y_NoMissing = y_2d[:, y_nonMissingIndex]
    
    if type == 'cov':
            x_NoMissing = x_NoMissing - np.mean(x_NoMissing, axis=0)
            y_NoMissing = y_NoMissing - np.mean(y_NoMissing, axis=0)
    else:  # z-score for correlation MCA
            x_NoMissing = zscore(x_NoMissing, axis=0)
            y_NoMissing = zscore(y_NoMissing, axis=0)
    
    Cxy = np.dot(x_NoMissing.T, y_NoMissing)/(ntime-1.0)
    U, s, V = np.linalg.svd(Cxy, full_matrices=False)
    x_patt = np.reshape(U.T, (U.shape[1], nrow_x, ncol_x), order='F')
    x_patt = xr.DataArray(
            x_patt,
            dims=('mode','lat','lon'),
            coords={'mode':np.arange(1,x_patt.shape[0]+1),
                    'lat':x['lat'], 
                    'lon':x['lon']})
    y_patt = np.reshape(V, (V.shape[0], nrow_y, ncol_y), order='F')
    y_patt = xr.DataArray(
            y_patt,
            dims=('mode','lat','lon'),
            coords={'mode':np.arange(1,y_patt.shape[0]+1),
                    'lat':y['lat'], 
                    'lon':y['lon']})
    x_ind = np.dot(x_NoMissing, U)
    x_ind = zscore(x_ind,axis=0)
    x_ind = xr.DataArray(
            x_ind,
            dims=('time','mode'),
            coords={'time':x.time,
                    'mode':np.arange(1,x_patt.shape[0]+1)})
    
    y_ind = np.dot(y_NoMissing, V.T)
    y_ind = zscore(y_ind,axis=0)
    y_ind = xr.DataArray(
            y_ind,
            dims=('time','mode'),
            coords={'time':x.time,
                    'mode':np.arange(1,y_patt.shape[0]+1)})
    scf = s**2./np.sum(s**2.0)
    return x_patt, y_patt, x_ind, y_ind, scf
    
    
def linregress_3d(x, y):
    # x is time series, y is 3d data (time, lat, lon) 
    # returns slope, p_value 
    # verified agasint 
    #   from scipy.stats import linregress
    #   slope, intercept, r_value, p_value, std_err = linregress(xx, yy)
    
    #number of samples     
    n = x.shape[0]
    
    # means and standard deviations 
    xmean = x.mean(axis=0)
    ymean = y.mean(axis=0)
    xstd  = x.std(axis=0)
    ystd  = y.std(axis=0)
    
    # calculate covariance and correlation 
    cov   =  np.sum((x - xmean)*(y - ymean), axis=0)/(n)
    cor   = cov/(xstd*ystd)
    
    # calculate slope and intercept 
    slope     = cov/(xstd**2)
    intercept = ymean - xmean*slope  
    
    # calculate p-value
    degrees_of_freedom = n - 2
    t_statistic = (cor * np.sqrt(n - 2)) / np.sqrt(1 - cor**2)
    p_value = 2 * (1 - t.cdf(np.abs(t_statistic), df=degrees_of_freedom))
    return slope, p_value

def linearly_remove(data,y):  
    # returns the resids of data with y regressed out of it 
    # Flatten both data and nino34 to 2D arrays
    data = data.fillna(0.0)
    data_flat = data.stack(points=('lat', 'lon'))
    try:
        y_flat = y.values.flatten()
    except:
        y_flat = y.flatten()
    # Perform linear regression using NumPy
    model = LinearRegression().fit(y_flat.reshape(-1, 1), data_flat.values)

    # Predict the ENSO effect and reshape it back to 3D
    y_effect = model.predict(y_flat.reshape(-1, 1)).reshape(data.shape)

    # Remove the ENSO effect from the data
    resids = data - y_effect
    return resids 

