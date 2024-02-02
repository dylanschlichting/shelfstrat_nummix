#Packages 
import numpy as np
import xgcm
from xgcm import Grid
import xarray as xr
import xroms
from datetime import datetime

import glob
from xhistogram.xarray import histogram
import cartopy
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import cartopy.feature as cfeature
import cmocean.cm as cmo
import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib.ticker as tick
from matplotlib.dates import DateFormatter
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.dates as mdates
from matplotlib.ticker import AutoMinorLocator

# path = '/d2/home/dylan/idealized_nummix/diurnal_wind/runs/basecase/shelf_ho_5_dx_500_avg.nc'
path = '/d2/home/dylan/idealized_nummix/diurnal_wind/runs/shelf_uwind_1_windtype_2_dx_500/shelf_ho_5_dx_500_uwind_01_di_avg.nc'
# path = '/d2/home/dylan/idealized_nummix/diurnal_wind/runs/downwelling_5_semidiurnal/shelf_ho_5_dx_500_uwind_4_semidiurnal_avg.nc'

ds = xroms.open_netcdf(path)
ds, grid = xroms.roms_dataset(ds)

def surface_vorticity(ds, grid):
    '''
Calculates the surface vertical vorticity normalized by 
the Coriolis frequency. 
----
Inputs:
ds - Xarray Dataset
grid - XGCM grid object 
----
Outputs:
rvort_psi: Normalized vorticity on the psi points 

    '''
    u = ds.u.isel(s_rho=-1)
    v = ds.v.isel(s_rho=-1)

    dudy = grid.derivative(u, 'Y')
    dudy = xroms.to_rho(dudy, grid)
    dvdx = grid.derivative(v, 'X')
    dvdx = xroms.to_rho(dvdx, grid)

    rvort_rho = (dvdx-dudy)/ds.f
    
    return rvort_rho 

def surface_saltgradmag(ds, grid):
    '''
Calculates the surface horizontal salinity gradient magnitude normalized by 
the Coriolis frequency. 
----
Inputs:
ds - Xarray Dataset
grid - XGCM grid object 
----
Outputs:
sgradmag: horizontal salinity gradient magnitude on the psi points

    '''
    s = ds.salt.isel(s_rho=-1)

    dsdx = grid.derivative(s, 'X', boundary = 'extend')
    dsdx_psi = xroms.to_rho(dsdx, grid)
    dsdy = grid.derivative(s, 'Y', boundary = 'extend')
    dsdy_psi = xroms.to_rho(dsdy, grid)
    
    sgradmag = (dsdx_psi**2+dsdy_psi**2)**(1/2)
    
    return sgradmag

sgradmag = surface_saltgradmag(ds, grid)
rv = surface_vorticity(ds, grid)

salt1 = ds.salt[:,-1]
saltfinal = ds.salt[:,-1]
vort1 = rv
vortfinal = rv
sgrad1 = sgradmag
sgradfinal = sgradmag

hours = np.arange(720)
h_day = np.arange(24)
hours_since0 = np.tile(h_day, 30)
timevec_days = np.trunc(np.arange(0,240)/24)

plt.rcParams.update({'font.size': 12})

for tcount in range(len(ds.ocean_time)):
    fig, ax = plt.subplots(3,1, figsize = (12,9), constrained_layout = True)

    #salt
    mappable = ax[0].pcolormesh(ds.x_rho[:]/1000, ds.y_rho[:]/1000, salt1[tcount], cmap = cmo.haline, vmin = 27, vmax = 35)
    cbar = fig.colorbar(mappable, ax = ax[0], label = '', pad = 0.03, ticks = [27, 29, 31, 33, 35],)
    cbar.ax.set_ylabel(r'[g kg$^{-1}$]')

    #Horizontal salinity gradient
    mappable = ax[1].pcolormesh(ds.x_rho[:]/1000, ds.y_rho[:]/1000, np.log10(sgrad1[tcount].where(sgrad1[tcount]>1e-7)), cmap = cmo.thermal, vmin = -6, vmax = -2)
    cbar = fig.colorbar(mappable, ax = ax[1], label = '', extend = 'min', format=tick.FormatStrFormatter('$10^{%d}$'), pad = 0.03)
    cbar.ax.set_ylabel(r'$|\nabla_H s|$ [g kg$^{-1}$ m$^{-1}$]')

    #Relative vertical vorticity 
    mappable = ax[2].pcolormesh(ds.x_rho[:]/1000, ds.y_rho[:]/1000, vort1[tcount], cmap = cmo.curl, vmin = -3, vmax = 3)
    cbar = fig.colorbar(mappable, ax = ax[2], label = '', extend = 'both', pad = 0.03)
    cbar.ax.set_ylabel(r'$(\partial_x v - \partial_y u)/f$')

    for i in range(3):
            ax[i].set(xlim=[0,97], ylim=[0,97], aspect = 0.75)
            ax[i].set_ylabel('Across-shelf dist. [km]')
            minor_locator = AutoMinorLocator(2)
            ax[i].xaxis.set_minor_locator(minor_locator)
            ax[i].yaxis.set_minor_locator(minor_locator)

    ax[2].set_xlabel('Along-shelf dist. [km]')
    for i in range(2):
            ax[i].set_xticklabels([])

    ax[0].set_title('Salinity: ' + 'Day ' + str(int(timevec_days[tcount])) + ' Hour ' + str(hours_since0[tcount]))
    ax[1].set_title('Horz. salinity gradient: ' + 'Day ' + str(int(timevec_days[tcount])) + ' Hour ' + str(hours_since0[tcount]))
    ax[2].set_title('Relative vorticity: ' + 'Day ' + str(int(timevec_days[tcount])) + ' Hour ' + str(hours_since0[tcount]))
    ax[0].annotate('(a)', xy = (3,88), color = 'k', fontsize = 10, fontweight='bold')
    ax[1].annotate('(b)', xy = (3,88), color = 'k', fontsize = 10, fontweight='bold')
    ax[2].annotate('(c)', xy = (3,88), color = 'k', fontsize = 10, fontweight='bold')


    # outpath = '/d2/home/dylan/idealized_nummix/diurnal_wind/ani/shelf_dx_500_nowind_hour_'+ str(int(hours[tcount]))+'.jpg'
    outpath = '/d2/home/dylan/idealized_nummix/diurnal_wind/ani/shelf_dx_500_uwind_01_di_hour_'+ str(int(hours[tcount]))+'.jpg'
    # outpath = '/d2/home/dylan/idealized_nummix/diurnal_wind/ani/shelf_dx_500_semidiurnal_uwind_4_hour_'+ str(int(hours[tcount]))+'.jpg'
    plt.savefig(outpath, dpi = 300, bbox_inches='tight')
    plt.clf()