'''
Script to calculate volume-integrated MKE,EKE, and TKE for shelfstrat 
simulations. See Hetland 2017 JPO for more information. 
'''
#Packages 
import numpy as np
import xgcm
from xgcm import Grid
import xarray as xr
import xroms
from datetime import datetime
import glob
#The chaotic option, used to suppress issues with cf_time with xroms 
import warnings
warnings.filterwarnings("ignore")

paths = ['/d1/shared/shelfstrat_wind/43N_open/shelf_dx_500_uwind_osc_001/shelf_dx_500_uwind_osc_001_his.nc',
         '/d1/shared/shelfstrat_wind/43N_open/shelf_dx_500_uwind_osc_002/shelf_dx_500_uwind_osc_002_his.nc',
         '/d1/shared/shelfstrat_wind/43N_open/shelf_dx_500_uwind_osc_004/shelf_dx_500_uwind_osc_004_his.nc',
         '/d1/shared/shelfstrat_wind/43N_open/shelf_dx_500_uwind_osc_008/shelf_dx_500_uwind_osc_008_his.nc',
         '/d1/shared/shelfstrat_wind/43N_open/shelf_dx_500_uwind_osc_01/shelf_dx_500_uwind_osc_01_his.nc',
         '/d1/shared/shelfstrat_wind/43N_open/shelf_dx_500_uwind_osc_02/shelf_dx_500_uwind_osc_02_his.nc',
         '/d1/shared/shelfstrat_wind/43N_open/shelf_dx_500_uwind_osc_04/shelf_dx_500_uwind_osc_04_his.nc']
#Open model output with xroms
def open_roms(path):
    ds = xroms.open_netcdf(path)
    ds, grid = xroms.roms_dataset(ds)
    return ds, grid

ds = []
grid = []
for i in range(len(paths)):
    dsa, grida = open_roms(paths[i])
    ds.append(dsa)
    grid.append(grida)

etaslice = slice(1,100)
xislice = slice(1,-1)

def energy_vint(ds,grid,xislice,etaslice):
    '''
Calculates volume-integrated eddy, mean, and total kinetic energy based on 
Hetland (2017) JPO.
Notes:
------
EKE = 1/2(uprime^2 + v^2). 
MKE = 1/2(ubar^2)
TKE = 1/2(u^2+v^2)
u = ubar+uprime, ubar = 1/L int_0^L u dx, i.e., alongshore mean
vbar = 0 by design.
Velocities interpolated to their respective rho points
    '''
    u = xroms.to_rho(ds.u, grid)
    u = u.isel(eta_rho = etaslice, xi_rho = xislice) 
    v = xroms.to_rho(ds.v, grid)
    v = v.isel(eta_rho = etaslice, xi_rho = xislice)
    ubar = u.mean('xi_rho')
    uprime = u-ubar
    vprime = v
    
    #Eddy kinetic energy
    eke = 0.5*(uprime**2 + vprime**2)
    dV = ds.dV.isel(eta_rho = etaslice, xi_rho = xislice)
    eke_int = (eke*dV).sum(['eta_rho', 'xi_rho', 's_rho'])
    eke_int.attrs = ''
    eke_int.name = 'eke'
    
    #Mean kinetic energy
    mke = 0.5*ubar**2
    mke_int = (mke*dV).sum(['eta_rho', 'xi_rho', 's_rho'])
    mke_int.attrs = ''
    mke_int.name = 'mke'
    
    #Total kinetic energy 
    tke = 0.5*(u**2+v**2)
    tke_int = (tke*dV).sum(['eta_rho', 'xi_rho', 's_rho'])
    tke_int.attrs = ''
    tke_int.name = 'tke'
    
    ds_energy = xr.merge([eke_int, mke_int, tke_int])
    return ds_energy

dse = []
for i in range(len(paths)):
    ds_energy = energy_vint(ds[i],grid[i],xislice,etaslice)
    dse.append(ds_energy)

paths = ['/d2/home/dylan/idealized_nummix/diurnal_wind/outputs/energy/shelf_dx_500_uwind_osc_001_ene.nc',
         '/d2/home/dylan/idealized_nummix/diurnal_wind/outputs/energy/shelf_dx_500_uwind_osc_002_ene.nc',
         '/d2/home/dylan/idealized_nummix/diurnal_wind/outputs/energy/shelf_dx_500_uwind_osc_004_ene.nc',
         '/d2/home/dylan/idealized_nummix/diurnal_wind/outputs/energy/shelf_dx_500_uwind_osc_008_ene.nc',
         '/d2/home/dylan/idealized_nummix/diurnal_wind/outputs/energy/shelf_dx_500_uwind_osc_01_ene.nc',
         '/d2/home/dylan/idealized_nummix/diurnal_wind/outputs/energy/shelf_dx_500_uwind_osc_02_ene.nc',
         '/d2/home/dylan/idealized_nummix/diurnal_wind/outputs/energy/shelf_dx_500_uwind_osc_04_ene.nc']
for i in range(len(paths)):
    print('saving energy file')
    dse[i].to_netcdf(paths[i])