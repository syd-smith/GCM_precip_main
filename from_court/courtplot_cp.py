import sys
import numpy as np
# import xarray as xr
# from sklearn.linear_model import LinearRegression
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm #, ListedColormap
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['text.usetex'] = False
mpl.rcParams['savefig.format'] = 'pdf'
mpl.pyplot.rcParams['figure.constrained_layout.use'] = True
from scipy.stats import ttest_ind
sys.path.extend([
    '/uufs/chpc.utah.edu/common/home/strong-group7/sydney/GSL_Climate/packages/'])
from court_analyze import linregress_3d
from cartopy.util import add_cyclic_point
import cartopy.crs as ccrs
import matplotlib.ticker as mticker
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
from cartopy.feature import ShapelyFeature
import matplotlib.patches as mpatches


from scipy.stats import zscore
# import pandas as pd
# import matplotlib.colors as mcolors

# import pdb; pdb.set_trace()

from string import ascii_lowercase, ascii_uppercase
import warnings
from shapely.errors import ShapelyDeprecationWarning
warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning) 

prop_cycle = mpl.pyplot.rcParams['axes.prop_cycle']
colororder = prop_cycle.by_key()['color']
    
def std_plot(x,y,axs=[]):
    mean = np.nanmean(x)
    std = np.nanstd(x)
    x = (x - mean) / std
    mean = np.nanmean(y)
    std = np.nanstd(y)
    y = (y - mean) / std
    if axs:
        pass
    else:
        fig, axs = plt.subplots()
    axs.plot(x)
    axs.plot(y)
    

def anomaly_contourf(dat_anom,dat,plot_dict):
    # dat should have dimensions named 'time','lat','lon'
    #   lon should be 0 to 360 
    # contours can be integer or array of values 
    # kwargs:
        # contours=21,cmap='RdBu_r',
        # latlim=[],lonlim=[],
        # add_colorbar=True,
        # fig_proj = ccrs.PlateCarree(),
        # alpha=0.05,axs=-1
        # permutations=None
    if dat_anom['lat'][0]>dat_anom['lat'][1]:
        dat_anom = dat_anom.sel(lat=slice(None, None, -1)) 
        dat = dat.sel(lat=slice(None, None, -1)) 
    permutations = plot_dict.get('permutations',None)
    # restrict data because permutation is expensive 
    # subset the slice needed for latlim 
    latlim = plot_dict['latlim']
    dat_anom = dat_anom.sel(lat=slice(latlim[0],latlim[1]))
    dat = dat.sel(lat=slice(latlim[0],latlim[1]))    
    print(dat)
    # calculate anomaly 
    ddat = dat_anom.mean(dim='time') - dat.mean(dim='time')
    # perform t-test 
    t_statistic_series, p_values = ttest_ind(dat_anom,dat,axis=0,
                                             permutations=permutations,
                                             random_state=0)
    # pdb.set_trace()
    axs_out = my_contourf(ddat,p_values,plot_dict)
    
    return axs_out

def regress_contourf(x,y,plot_dict):
    # plot_dict:
        # contours=21,cmap='RdBu_r',
        # latlim=[],lonlim=[],
        # add_colorbar=True,
        # fig_proj = ccrs.PlateCarree(),
        # alpha=0.05,axs=-1
    slope,pval = linregress_3d(x,y)
    # pdb.set_trace()
    axs_out, mappable = my_contourf(slope,pval,plot_dict)    
    return slope, pval, axs_out, mappable



def my_quiver(u,v,step,plot_dict):
    fig_proj = plot_dict.get('fig_proj',ccrs.PlateCarree())
    arrow_label = plot_dict.get('arrow_label',[])
    arrow_color = plot_dict.get('arrow_color','k')
    arrow_scale = plot_dict.get('arrow_scale',6)
    arrow_fontproperties = plot_dict.get('arrow_fontproperties',{})
    arrow_labelpos = plot_dict.get('arrow_labelpos','N')
    # latlim = plot_dict.get('latlim',[])
    # lonlim = plot_dict.get('lonlim',[])
    axs = plot_dict.get('axs',-1)
    # labels = plot_dict.get('labels',[True,True,False,False])
    # ypadding = plot_dict.get('ypadding',15)
    fig = plot_dict.get('fig',[])
    # contour_type = plot_dict.get('contour_type','filled')
    # zorder = plot_dict.get('zorder',1)
    # linewidth = plot_dict.get('linewidth',0.5)
    
    lon_mesh, lat_mesh = np.meshgrid(u['lon'],u['lat'])
    # create axis if one was not in plot_dict
    if axs==-1:
        fig, axs = plt.subplots(
            subplot_kw={'projection':fig_proj})
    xx = lon_mesh[::step,::step]
    yy = lat_mesh[::step,::step]
    uu = np.array(u[::step,::step])
    vv = np.array(v[::step,::step])
    quiv = axs.quiver(xx[0,:],yy[:,0],uu,vv,
               pivot='tail',
               width=0.0005,
               scale=arrow_scale,
               headwidth=6,
               color=arrow_color,
               transform=ccrs.PlateCarree()) 
    # gl = axs.gridlines(draw_labels=True,
    #                   linewidth=0.5, 
    #                   color='gray', 
    #                   alpha=0.4, 
    #                   linestyle='-',
    #                   ypadding=ypadding)
    
    # gl.left_labels = labels[0]
    # gl.bottom_labels = labels[1]
    # gl.right_labels = labels[2]
    # gl.top_labels = labels[3]
    if arrow_label:
        aloc = plot_dict['arrow_loc']
        quiverkey = plt.quiverkey(quiv,aloc[0],aloc[1],
                      plot_dict['arrow_size'],
                      arrow_label,
                      labelpos=arrow_labelpos,sd
                      fontproperties=arrow_fontproperties)
    else:
        quiverkey=[]
    
    return axs, quiverkey

def my_contourf(dat,p_values=[],plot_dict=[]):
    # plot_dict:
        # contours=21,cmap='RdBu_r',
        # latlim=[],lonlim=[],
        # add_colorbar=True,
        # fig_proj = ccrs.PlateCarree(),
        # alpha=0.05,axs=-1
    # create new axis if axs not provided 
    fig_proj = plot_dict.get('fig_proj',ccrs.PlateCarree())
    latlim = plot_dict.get('latlim',[])
    lonlim = plot_dict.get('lonlim',[])
    latlim_mag_check = plot_dict.get('latlim_mag_check',latlim)
    contours = plot_dict.get('contours',21)
    add_colorbar = plot_dict.get('add_colorbar',True)
    cb_title= plot_dict.get('cb_title',[])
    alpha = plot_dict.get('alpha',0.05)
    axs = plot_dict.get('axs',-1)
    cmap = plot_dict.get('cmap','RdBu_r')
    shrink = plot_dict.get('shrink',0.6)
    labels = plot_dict.get('labels',[True,True,False,False])
    latlabel_size = plot_dict.get('latlabel_size',10)
    latlabel_color = plot_dict.get('latlabel_color','k')
    lat_tick = plot_dict.get('lat_tick',[])
    lon_tick = plot_dict.get('lon_tick',[])
    ypadding = plot_dict.get('ypadding',15)
    fig = plot_dict.get('fig',[])
    land_color = plot_dict.get('land_color',[])
    coast_color = plot_dict.get('coast_color','k')
    draw_coasts = plot_dict.get('draw_coasts',True)
    hashing = plot_dict.get('hashing','..')
    hash_color = plot_dict.get('hash_color','gray')
    contour_type = plot_dict.get('contour_type','filled')
    zorder = plot_dict.get('zorder',1)
    linewidth = plot_dict.get('linewidth',1)
    extend = plot_dict.get('extend','neither')
    state_color = plot_dict.get('state_color',None)
    
    # create axis if one was not in plot_dict
    if axs==-1:
        fig, axs = plt.subplots(
            subplot_kw={'projection':fig_proj})
       
    # nan the values outside latlim to set contour levels
    dat = dat.where(np.logical_and(dat.lat<=max(latlim_mag_check),
                                       dat.lat>min(latlim_mag_check)),
                                       np.nan)
       
    # eliminate gap at prime meridian 
    ddat2, lon2 = add_cyclic_point(dat, coord=dat['lon'].values)
     
    
    # contours
    if contour_type=='filled':
        contour = axs.contourf(lon2,dat['lat'],ddat2,levels=contours,
                               norm=TwoSlopeNorm(0),
                               extend=extend,
                               transform=ccrs.PlateCarree(),
                               cmap=cmap)
    else: # pos_neg_dash
        contour_color = cmap[0]
        contour = axs.contour(lon2,dat['lat'],ddat2,levels=contours,
                               colors = contour_color,
                               transform=ccrs.PlateCarree(),
                               zorder=zorder,
                               linewidths=linewidth)
        
    # set map limits 
    if latlim:
        axs.set_ylim(min(latlim),max(latlim))
    if lonlim:
        axs.set_xlim(lonlim[0],lonlim[1])
                 
    # add coastlines and land 
    if draw_coasts:
        axs.coastlines(linewidth=0.5,color=coast_color)
    if land_color:
            axs.add_feature(cfeature.LAND, color=land_color,zorder=2)
   
    # add states 
    if not state_color is None:
        states = cfeature.NaturalEarthFeature(
            category='cultural', name='admin_1_states_provinces_lines', scale='50m', facecolor='none', edgecolor=state_color)
        axs.add_feature(states)
    
    # lakes = cfeature.NaturalEarthFeature(
    #     category='physical', name='admin_1_states_provinces_lines', scale='50m', facecolor='none', edgecolor=state_color)
    # axs.add_feature(states)
    
    axs.add_feature(cfeature.LAKES, zorder = 1)
    axs.add_feature(cfeature.RIVERS)
    
    #Add roads to map (interstates only)
    # Path to the shapefile
    roads_shp = '/uufs/chpc.utah.edu/common/home/u1301408//tl_2024_us_primaryroads.shp'
    reader = shpreader.Reader(roads_shp)

    # Filter for interstates (optional)
    geoms = []
    for rec in reader.records():
        if rec.attributes['FULLNAME'].startswith('I-'):  # Only interstates
            geoms.append(rec.geometry)
    roads_feature = ShapelyFeature(geoms, ccrs.PlateCarree(), edgecolor='black', linewidth=0.25, facecolor='none')
    axs.add_feature(roads_feature)


    box_lon = -112.25
    box_lat = 40.4
    box_width = 0.71   # degrees longitude
    box_height = 0.5  # degrees latitude

    rect = mpatches.Rectangle(
        (box_lon, box_lat), box_width, box_height,
        edgecolor='red', facecolor='none', linewidth=2,
        transform=ccrs.PlateCarree(), zorder = 3
        )
    axs.add_patch(rect)
    
    
    # # Create a Cartopy feature for the roads
    # roads_shp2 = '/uufs/chpc.utah.edu/common/home/u1301408//Roads.shp'
    # reader2 = shpreader.Reader(roads_shp2)
    
    # geoms2 = []
    # for rec in reader2.records():
    #     if 'SR 210' in rec.attributes['DOT_HWYNAM']:  # Only interstates
    #         geoms2.append(rec.geometry)
    #     elif 'SR 209' in rec.attributes['DOT_HWYNAM']:
    #         geoms2.append(rec.geometry)
    #     elif 'SR 190' in rec.attributes['DOT_HWYNAM']:
    #         geoms2.append(rec.geometry)
    #     else: 
    #         continue
    # # geoms_state2 = [rec.geometry for rec in reader2.records() if rec.attributes['DOT_HWYNAM'] == 'SR*']
    # roads_feature2 = ShapelyFeature(geoms2, ccrs.PlateCarree(), edgecolor='black', linewidth=0.5, facecolor='none')
    # axs.add_feature(roads_feature2)
    
    # # Filter for interstates (optional)
    # geoms2 = []
    # for rec in reader.records():
    #     if rec.attributes['RTTYP'] == 'SR':
    #         geoms2.append(rec.geometry)

    # # Create a Cartopy feature for the roads
    # roads_feature2 = ShapelyFeature(geoms2, ccrs.PlateCarree(), edgecolor='black', linewidth=0.5, facecolor='none')
    # axs.add_feature(roads_feature2)
        
    # add colorbar 
    if add_colorbar:
        my_add_cbar(fig,contour,ax=axs,
                    shrink=shrink,
                    cb_title=cb_title)   
            
    # grid lines 
    gl = axs.gridlines(draw_labels=True,
                      linewidth=0.5, 
                      color='gray', 
                      alpha=0.4, 
                      linestyle='-',
                      ypadding=ypadding)
    
    # lat lon labels 
    gl.left_labels = labels[0]
    gl.bottom_labels = labels[1]
    gl.right_labels = labels[2]
    gl.top_labels = labels[3]
    
    if lat_tick:
        gl.xlocator = mticker.FixedLocator(np.arange(-180,180,lon_tick))
        gl.ylocator = mticker.FixedLocator(np.arange(-90,90,lat_tick))
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        gl.xlabel_style = {'size': latlabel_size, 'color': latlabel_color, 'rotation': 0}
        gl.ylabel_style = {'size': latlabel_size, 'color': latlabel_color, 'rotation': 0}
    
    # significance    
    if len(p_values)>0:
        ddat2, lon2 = add_cyclic_point(p_values, coord=dat['lon'].values)
        hatch = axs.contourf(lon2,dat['lat'],ddat2,
                             levels=[0,alpha],
                             colors ='none',
                             hatches = [hashing],
                             extend = 'min',
                             transform=ccrs.PlateCarree())
        for i, collection in enumerate(hatch.collections):
            collection.set_edgecolor(hash_color)
        for collection in hatch.collections:
            collection.set_linewidth(0.)
    return axs, contour          
#%%
def my_pcolormesh(dat,p_values=[],plot_dict=[]):
    # plot_dict:
        # contours=21,cmap='RdBu_r',
        # latlim=[],lonlim=[],
        # add_colorbar=True,
        # fig_proj = ccrs.PlateCarree(),
        # alpha=0.05,axs=-1
    # create new axis if axs not provided 
    fig_proj = plot_dict.get('fig_proj',ccrs.PlateCarree())
    latlim = plot_dict.get('latlim',[])
    grid_lines = plot_dict.get('grid_lines',True)
    lonlim = plot_dict.get('lonlim',[])
    latlim_mag_check = plot_dict.get('latlim_mag_check',latlim)
    add_colorbar = plot_dict.get('add_colorbar',True)
    cb_title= plot_dict.get('cb_title',[])
    alpha = plot_dict.get('alpha',0.05)
    axs = plot_dict.get('axs',-1)
    cmap = plot_dict.get('cmap','RdBu_r')
    shrink = plot_dict.get('shrink',0.6)
    labels = plot_dict.get('labels',[True,True,False,False])
    latlabel_size = plot_dict.get('latlabel_size',10)
    latlabel_color = plot_dict.get('latlabel_color','k')
    lat_tick = plot_dict.get('lat_tick',[])
    lon_tick = plot_dict.get('lon_tick',[])
    ypadding = plot_dict.get('ypadding',15)
    fig = plot_dict.get('fig',[])
    land_color = plot_dict.get('land_color',[])
    coast_color = plot_dict.get('coast_color','k')
    draw_coasts = plot_dict.get('draw_coasts',True)
    state_color = plot_dict.get('state_color',None)
    hashing = plot_dict.get('hashing','..')
    hash_color = plot_dict.get('hash_color','gray')
    # contour_type = plot_dict.get('contour_type','filled')
    zorder = plot_dict.get('zorder',1)
    linewidth = plot_dict.get('linewidth',1)
    extend = plot_dict.get('extend','neither')
    vmin = plot_dict.get('vmin', None)
    vmax = plot_dict.get('vmax', None)
    extent = plot_dict.get('extent', None)
    
    # create axis if one was not in plot_dict
    if axs==-1:
        fig, axs = plt.subplots(
            subplot_kw={'projection':fig_proj})
        
    # nan the values outside latlim to set contour levels
    # dat = dat.where(np.logical_and(dat.lat<=max(latlim_mag_check),
    #                                     dat.lat>min(latlim_mag_check)),
    #                                     np.nan)
    try:
        ddat2, lon2 = add_cyclic_point(dat, coord=dat['lon'].values)
    except:
        ddat2 = dat
        lon2 = dat['lon'].values
    # ddat2 = ddat2.transpose((1,0))
    # ddat2=ddat2.values
    # ddat2=ddat2.transpose((1,0))
    
    mapp = axs.pcolormesh(lon2,dat['lat'],ddat2,shading='nearest',
                          transform=ccrs.PlateCarree(),
                          cmap=cmap,vmin=vmin,vmax=vmax)
   # set map limits 
    if latlim:
        axs.set_ylim(min(latlim),max(latlim))
    if lonlim:
        axs.set_xlim(lonlim[0],lonlim[1])
    if extent:
        axs.set_extent(extent, crs=ccrs.PlateCarree())
        
    # add coastlines and land 
    if draw_coasts:
        axs.coastlines(linewidth=0.5,color=coast_color)
    if land_color:
            axs.add_feature(cfeature.LAND, color=land_color,zorder=2)
    if not state_color is None:
        states = cfeature.NaturalEarthFeature(
            category='cultural', name='admin_1_states_provinces_lines', scale='50m', facecolor='none', edgecolor=state_color)
        axs.add_feature(states)
    # add colorbar 
    if add_colorbar:
        my_add_cbar(fig,mapp,ax=axs,
                    shrink=shrink,
                    cb_title=cb_title)   
            
    # grid lines 
    if grid_lines:
        gl = axs.gridlines(draw_labels=True,
                          linewidth=0.5, 
                          color='gray', 
                          alpha=0.4, 
                          linestyle='-',
                          ypadding=ypadding)
    else:
        gl = axs.gridlines(draw_labels=True,
                          linewidth=0.5, 
                          color='gray', 
                          alpha=0.0, 
                          ypadding=ypadding)
    # lat lon labels 
    gl.left_labels = labels[0]
    gl.bottom_labels = labels[1]
    gl.right_labels = labels[2]
    gl.top_labels = labels[3]
    
    if lat_tick:
        gl.xlocator = mticker.FixedLocator(np.arange(-180,180,lon_tick))
        gl.ylocator = mticker.FixedLocator(np.arange(-90,90,lat_tick))
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        gl.xlabel_style = {'size': latlabel_size, 'color': latlabel_color, 'rotation': 0}
        gl.ylabel_style = {'size': latlabel_size, 'color': latlabel_color, 'rotation': 0}
    
    # significance    
    if len(p_values)>0:
        ddat2, lon2 = add_cyclic_point(p_values, coord=dat['lon'].values)
        hatch = axs.contourf(lon2,dat['lat'],ddat2,
                             levels=[0,alpha],
                             colors ='none',
                             hatches = [hashing],
                             extend = 'min',
                             transform=ccrs.PlateCarree())
        for i, collection in enumerate(hatch.collections):
            collection.set_edgecolor(hash_color)
        for collection in hatch.collections:
            collection.set_linewidth(0.)
    return axs



#%%

def my_add_cbar(fig, mappable, ax, cb_title=[],shrink=False):
    cax = fig.add_axes([ax.get_position().x1 + 0.1,
                        ax.get_position().y0,
                        0.01,
                        ax.get_position().height])
    cbar = plt.colorbar(mappable, cax=cax)  # Similar to fig.colorbar(im, cax = cax)
    if cb_title:
        cbar.ax.set_title(cb_title, loc='left')
    return cax



def cross_section_latpres(dat,p_values,plot_dict):
    xlim = plot_dict.get('xlim',[])
    ylim = plot_dict.get('ylim',[])
    contours = plot_dict.get('contours',21)
    add_colorbar = plot_dict.get('add_colorbar',True)
    cb_title= plot_dict.get('cb_title',[])
    axs = plot_dict.get('axs',-1)
    cmap = plot_dict.get('cmap','RdBu_r')
    shrink = plot_dict.get('shrink',0.6)
    lat_tick = plot_dict.get('lat_tick',[])
    ypadding = plot_dict.get('ypadding',15)
    fig = plot_dict.get('fig',[])
    hashing = plot_dict.get('hashing','..')
    hash_color = plot_dict.get('hash_color','gray')
    contour_type = plot_dict.get('contour_type','filled')
    zorder = plot_dict.get('zorder',1)
    linewidth = plot_dict.get('linewidth',1)
    extend = plot_dict.get('extend','neither')
    alpha = plot_dict.get('alpha',0.05)
    
    if axs==-1:
        fig, axs = plt.subplots()
            
       
    # contours
    if contour_type=='filled':
        contour = axs.contourf(dat['lat'],dat['level'],dat,
                               levels=contours,
                               norm=TwoSlopeNorm(0),
                               extend=extend,
                               cmap=cmap)
    else: # pos_neg_dash
        contour_color = cmap[0]
        contour = axs.contour(dat['lat'],dat['level'],dat,
                              levels=contours,
                              colors = contour_color,
                              zorder=zorder,
                              linewidths=linewidth)
    axs.set_yscale('log')
    y_ticks = np.arange(1000,90,-100)#  [1000, 900, 800, 700, 600, 500, 400, 300, 200, 100]  # Add more ticks as needed
    tick_labels = [str(int(value)) for value in y_ticks]
    axs.set_yticks(y_ticks,tick_labels)
    axs.set_ylim(1000,100)
    if xlim:
        axs.set_xlim(xlim)
    if ylim:
        axs.set_ylim(ylim)
    # significance
    if len(p_values) > 0:
        hatch = axs.contourf(dat['lat'], dat['level'], p_values,
                             levels=[0, alpha],
                             colors='none',
                             hatches=[hashing],
                             extend='min')

        for i, collection in enumerate(hatch.collections):
            collection.set_edgecolor(hash_color)
        for collection in hatch.collections:
            collection.set_linewidth(0.)
            # add colorbar
    if add_colorbar:
        cax = my_add_cbar(fig,contour,ax=axs,
        shrink=shrink,
        cb_title=cb_title)    
    else:
        cax = []
    return contour, cax       
    
def hillshade(array,azimuth,angle_altitude):
    azimuth = 360.0 - azimuth 
    
    x, y = np.gradient(array)
    slope = np.pi/2. - np.arctan(np.sqrt(x*x + y*y))
    aspect = np.arctan2(-x, y)
    azimuthrad = azimuth*np.pi/180.
    altituderad = angle_altitude*np.pi/180.
 
    shaded = np.sin(altituderad)*np.sin(slope) + np.cos(altituderad)*np.cos(slope)*np.cos((azimuthrad - np.pi/2.) - aspect)
    
    return 255*(shaded + 1)/2

def label_subplots(axs, *, location='ul', upper_case=False,
                   offset_points=(-5, -5), fontweight='bold',
                   letts=None,prefix='',suffix='.',color='k',
                   fontsize=12):
    """ 
    adds letter labels to suplots
    :axs should be a list of axis handles
    :fontweight: 'normal', 'bold', 'extra bold' or numerical 0-1000
    :location: 'ul' for upper left,'ur' for upper right,
    :    'll' for lower left, 'lr' for lower right
    :letts can be list of letters or defaults to a,b,c...
    :prefix is text appended before each letter 
    :suffix is text appended after each letter
    :fontsize is font size 
    
    """
    if isinstance(location,str):
        locs = [location]*len(axs)
    else:
        locs = location
    
    if isinstance(color,str):
        colors = [color]*len(axs)
    else:
        colors = color
    
    
        
    if letts is None and upper_case:
        letts = ascii_uppercase[0:len(np.ravel(axs))]
    elif letts is None and not upper_case:
        letts = ascii_lowercase[0:len(np.ravel(axs))]
    look = plt.gca().get_ylim()
    if look[1]<look[0]:
        ysign = -1
    else:
        ysign = 1
    look = plt.gca().get_xlim()
    if look[1]<look[0]:
        xsign = -1
    else:
        xsign = 1
        
    spot = -1
    for ax, lab in zip(np.ravel(axs), letts):
        spot = spot+1
        location = locs[spot]
        color = colors[spot]
        if location == 'ur':
            offset_points = (-5*xsign, -5*ysign)
            ha = 'right'
            va = 'top'
            xy = (1,1)
        elif location == 'ul':
            offset_points = (5*xsign, -5*ysign)
            ha = "left"
            va = "top"
            xy = (0,1)
        elif location == 'll':
            offset_points = (5*xsign, 5*ysign)
            ha = "left"
            va = "bottom"
            xy = (0,0)
        elif location == 'lr':
            offset_points = (-5*xsign, 5*ysign)
            ha = "right"
            va = "bottom"
            xy = (1,0)
        else:
            print("unknown location")

        ax.annotate(f'{prefix}{lab}{suffix}', xy,
                    xytext=offset_points,
                    xycoords='axes fraction',
                    textcoords='offset points',
                    ha=ha, va=va, fontweight=fontweight,
                    color=color,
                    fontsize=fontsize)


