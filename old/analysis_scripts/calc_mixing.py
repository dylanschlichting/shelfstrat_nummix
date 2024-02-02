'''
Script to calculate volume-integrated physical and numerical salt mixing for 
shelfstrat simulations. 
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

paths = ['/d1/shared/shelfstrat_wind/43N_open/shelf_dx_500_uwind_osc_001/shelf_dx_500_uwind_osc_001_avg.nc',
         '/d1/shared/shelfstrat_wind/43N_open/shelf_dx_500_uwind_osc_002/shelf_dx_500_uwind_osc_002_avg.nc',
         '/d1/shared/shelfstrat_wind/43N_open/shelf_dx_500_uwind_osc_004/shelf_dx_500_uwind_osc_004_avg.nc',
         '/d1/shared/shelfstrat_wind/43N_open/shelf_dx_500_uwind_osc_008/shelf_dx_500_uwind_osc_008_avg.nc',
         '/d1/shared/shelfstrat_wind/43N_open/shelf_dx_500_uwind_osc_01/shelf_dx_500_uwind_osc_01_avg.nc',
         '/d1/shared/shelfstrat_wind/43N_open/shelf_dx_500_uwind_osc_02/shelf_dx_500_uwind_osc_02_avg.nc',
         '/d1/shared/shelfstrat_wind/43N_open/shelf_dx_500_uwind_osc_04/shelf_dx_500_uwind_osc_04_avg.nc']
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
    
def mix_vint(ds, grid, etaslice, xislice):
'''
Computes volume-integrated physical and numerical mixing for ROMS model output.
See Schlichting et al. JAMES for more information
'''
    mnum = ds.dye_03.isel(eta_rho = etaslice, xi_rho = xislice) #Numerical salt mixing
    mphy = ds.AKr.isel(eta_rho = etaslice, xi_rho = xislice) #Destruction of salt variance
    #Interpolate to the s-rho points 
    mphy = grid.interp(mphy, 'Z')
    dV = ds.dV.isel(eta_rho = etaslice, xi_rho = xislice)
    #Volume integrate, then name for concat
    mnum_int = (mnum*dV).sum(['eta_rho', 'xi_rho', 's_rho'])
    mnum_int.attrs = [] # Remove grid so we can save to netcdf 
    mnum_int.name = 'mnum_int'
    mphy_int = (mphy*dV).sum(['eta_rho', 'xi_rho', 's_rho'])
    mphy_int.name = 'mphy_int'

    ds_mix = xr.merge([mnum_int, mphy_int])
    return ds_mix

#Slice over the 50 km plume and save to a netcdf
etaslice = slice(1,100)
xislice = slice(1,-1)
dsmix = []
for i in range(len(paths)):
    print('running mix calcs')
    ds_mix = mix_vint(ds[i],grid[i],etaslice,xislice)
    dsmix.append(ds_mix)

paths = ['/d2/home/dylan/idealized_nummix/diurnal_wind/outputs/mixing/shelf_dx_500_uwind_osc_001_mix.nc',
         '/d2/home/dylan/idealized_nummix/diurnal_wind/outputs/mixing/shelf_dx_500_uwind_osc_002_mix.nc',
         '/d2/home/dylan/idealized_nummix/diurnal_wind/outputs/mixing/shelf_dx_500_uwind_osc_004_mix.nc',
         '/d2/home/dylan/idealized_nummix/diurnal_wind/outputs/mixing/shelf_dx_500_uwind_osc_008_mix.nc',
         '/d2/home/dylan/idealized_nummix/diurnal_wind/outputs/mixing/shelf_dx_500_uwind_osc_01_mix.nc',
         '/d2/home/dylan/idealized_nummix/diurnal_wind/outputs/mixing/shelf_dx_500_uwind_osc_02_mix.nc',
         '/d2/home/dylan/idealized_nummix/diurnal_wind/outputs/mixing/shelf_dx_500_uwind_osc_04_mix.nc']
for i in range(len(paths)):
    print('saving mixing file')
    dsmix[i].to_netcdf(paths[i])