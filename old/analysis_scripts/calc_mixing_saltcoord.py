'''
Script to calculate volume-integrated mixing, mixing per salinity class, 
diahaline diffusive salt flux, and diahaline volume flux for a 3D control volume.
See 'diahaline_mixing.ipynb' for more information. 
'''
#Packages
import numpy as np
import xgcm
from xgcm import Grid
import xarray as xr
import xroms
from datetime import datetime
import glob
from xhistogram.xarray import histogram
from datetime import timedelta

# Functions to open model output and calculate mixing quantities. 
def open_roms(path):
    ds1 = xroms.open_netcdf(path)
    ds1, grid1 = xroms.roms_dataset(ds1)
    return ds1, grid1

# Don't bin by fronts, i.e., zeta/f>1
def diav_no_fronts(ds,tslice,etaslice,xislice,grid):
    salt = ds.salt.isel(ocean_time = tslice, eta_rho = etaslice,xi_rho = xislice)
    dv = ds.dV.isel(ocean_time = tslice, eta_rho = etaslice,xi_rho = xislice)

    akr = grid.interp(ds.AKr,'Z')
    mphy = (akr*ds.dV).isel(ocean_time = tslice, eta_rho = etaslice,xi_rho = xislice)
    mphy.attrs = ''
    mnum = (ds.dye_03*ds.dV).isel(ocean_time = tslice, eta_rho = etaslice,xi_rho = xislice)
    mnum.attrs = ''
    mtot = ((ds.dye_03+akr)*ds.dV).isel(ocean_time = tslice, eta_rho = etaslice,xi_rho = xislice)
    mtot.attrs = ''
    
    
    # Compute M(S), m(S), J_dia(S), and Q_dia(S)
    Mnum_s = histogram(salt, bins = [sbins], weights = mnum)
    Mnum_s.attrs = ''
    Mnum_s.name = 'Mnum'
    Mphy_s = histogram(salt, bins = [sbins], weights = mphy)
    Mphy_s.attrs = ''
    Mphy_s.name = 'Mphy'
    Mtot_s = histogram(salt, bins = [sbins], weights = mtot)
    Mtot_s.attrs = ''
    Mtot_s.name = 'Mtot'
    
    dsalt = (Mnum_s.salt_bin[1]-Mnum_s.salt_bin[0]).values
    
    mnum_s = Mnum_s.diff('salt_bin')/dsalt
    mnum_s.attrs = ''
    mnum_s.name = 'mnum'
    mphy_s = Mphy_s.diff('salt_bin')/dsalt
    mphy_s.attrs = ''
    mphy_s.name = 'mphy'
    mtot_s = Mtot_s.diff('salt_bin')/dsalt
    mtot_s.attrs = ''
    mtot_s.name = 'mtot'
    
    Jdia_num = -0.5*(mnum_s)
    Jdia_num.attrs = ''
    Jdia_num.name = 'jdia_mnum'
    Jdia_phy = -0.5*(mphy_s)
    Jdia_phy.attrs = ''
    Jdia_phy.name = 'jdia_mphy'
    Jdia_tot = -0.5*(mtot_s)
    Jdia_tot.attrs = ''
    Jdia_tot.name = 'jdia_mtot'

    Qdia_num = 0.5*(mnum_s.diff('salt_bin')/dsalt)
    Qdia_num.attrs = ''
    Qdia_num.name = 'Qdia_num'
    Qdia_phy = 0.5*(mphy_s.diff('salt_bin')/dsalt)
    Qdia_phy.attrs = ''
    Qdia_phy.name = 'Qdia_phy'
    Qdia_tot = 0.5*(mtot_s.diff('salt_bin')/dsalt)
    Qdia_tot.attrs = ''
    Qdia_tot.name = 'Qdia_tot'
    
    dsm = xr.merge([Mnum_s,Mphy_s,Mtot_s], compat = 'override')
    dsm.salt_bin.attrs = ''
    
    return dsm

# Bin by fronts 
def diav_fronts(ds,tslice,etaslice,xislice,grid,zeta):
    salt = ds.salt.isel(ocean_time = tslice, eta_rho = etaslice,xi_rho = xislice)
    dv = ds.dV.isel(ocean_time = tslice, eta_rho = etaslice,xi_rho = xislice)

    akr = grid.interp(ds.AKr,'Z')
    mphy = (akr*ds.dV).isel(ocean_time = tslice, eta_rho = etaslice,xi_rho = xislice)
    mphy.attrs = ''
    mnum = (ds.dye_03*ds.dV).isel(ocean_time = tslice, eta_rho = etaslice,xi_rho = xislice)
    mnum.attrs = ''
    mtot = ((ds.dye_03+akr)*ds.dV).isel(ocean_time = tslice, eta_rho = etaslice,xi_rho = xislice)
    mtot.attrs = ''
    
    # Compute M(S), m(S), J_dia(S), and Q_dia(S)
    Mnum_s = histogram(salt.where(zeta>1), bins = [sbins], weights = mnum.where(zeta>1))
    Mnum_s.attrs = ''
    Mnum_s.name = 'Mnum'
    Mphy_s = histogram(salt.where(zeta>1), bins = [sbins], weights = mphy.where(zeta>1))
    Mphy_s.attrs = ''
    Mphy_s.name = 'Mphy'
    Mtot_s = histogram(salt.where(zeta>1), bins = [sbins], weights = mtot.where(zeta>1))
    Mtot_s.attrs = ''
    Mtot_s.name = 'Mtot'
    
    dsalt = (Mnum_s.salt_bin[1]-Mnum_s.salt_bin[0]).values
    
    mnum_s = Mnum_s.diff('salt_bin')/dsalt
    mnum_s.attrs = ''
    mnum_s.name = 'mnum'
    mphy_s = Mphy_s.diff('salt_bin')/dsalt
    mphy_s.attrs = ''
    mphy_s.name = 'mphy'
    mtot_s = Mtot_s.diff('salt_bin')/dsalt
    mnum_s.attrs = ''
    mphy_s.name = 'mtot'
    
    Jdia_num = -0.5*(mnum_s)
    Jdia_num.attrs = ''
    Jdia_num.name = 'jdia_tot'
    Jdia_phy = -0.5*(mphy_s)
    Jdia_phy.attrs = ''
    Jdia_phy.name = 'jdia_tot'
    Jdia_tot = -0.5*(mtot_s)
    Jdia_tot.attrs = ''
    Jdia_tot.name = 'jdia_tot'

    Qdia_num = 0.5*(mnum_s.diff('salt_bin')/dsalt)
    Qdia_num.attrs = ''
    Qdia_num.name = 'Qdia_num'
    Qdia_phy = 0.5*(mphy_s.diff('salt_bin')/dsalt)
    Qdia_phy.attrs = ''
    Qdia_phy.name = 'Qdia_phy'
    Qdia_tot = 0.5*(mtot_s.diff('salt_bin')/dsalt)
    Qdia_tot.attrs = ''
    Qdia_tot.name = 'Qdia_tot'
    
    dsm = xr.merge([Mnum_s,Mphy_s,Mtot_s], compat = 'override')
    dsm.salt_bin.attrs = ''
    
    return dsm

# Calculate vertical relative vorticity using a jacobian 
def rel_vort(ds,grid):
    dudx, dudy = xroms.hgrad(ds.u, grid)
    dvdx, dvdy = xroms.hgrad(ds.v, grid)
    #Interpolate horz. to rho points
    dudy_rho = xroms.to_rho(dudy, grid)
    dvdx_rho = xroms.to_rho(dudx, grid)
    #Interpolate vertically to s-rho points
    dudy_srho = grid.interp(dudy_rho, 'Z', boundary = 'extend')
    dvdx_srho = grid.interp(dvdx_rho, 'Z', boundary = 'extend')

    zeta = (dvdx_srho-dudy_srho)/ds.f
    zeta.name = 'zeta'
    
    return zeta

# Run the functions
paths = ['/d1/shared/shelfstrat_wind/43N_open/shelf_dx_500_mpdata_uwind_osc_1/shelf_dx_500_mpdata_uwind_osc_1_avg.nc',
         '/d1/shared/shelfstrat_wind/43N_open/shelf_dx_500_u3hc4_uwind_osc_1/shelf_dx_500_u3hc4_uwind_osc_1_avg.nc', 
         '/d1/shared/shelfstrat_wind/43N_open/shelf_dx_500_hsimt_uwind_osc_1/shelf_dx_500_hsimt_uwind_osc_1_avg.nc']
 
ds = []
grid = []
for i in range(len(paths)):
    ds1, grid1 = open_roms(paths[i])
    ds.append(ds1)
    grid.append(grid1)

xislice = slice(1,-1) #Exclude boundary points bc periodic BC
etaslice = slice(1,100) # Initially stratified region
tslice = slice(156,337) # Days 7.5-15 

sbins = np.linspace(27,35,51)

# Compute vorticity
zeta = rel_vort(ds[i],grid[i])
zeta = zeta.isel(ocean_time = tslice, eta_rho = etaslice, xi_rho = xislice)

ds_mix_fronts = []
ds_mix_no_fronts = []
for i in range(len(paths)):
    # Sorted by fronts 
    dsm_fronts = diav_fronts(ds[i],tslice,etaslice,xislice,grid[i],zeta[i])
    ds_mix_fronts.append(dsm_fronts)
    # Not sorted by fronts
    dsm_no_fronts = diav_no_fronts(ds[i],tslice,etaslice,xislice,grid[i])
    ds_mix_no_fronts.append(dsm_no_fronts)
    
ds_mix_fronts[0].to_netcdf('volint_mix_fronts_mpdata_shelf_dx_500_mpdata_uwind_osc_1.nc')
ds_mix_fronts[1].to_netcdf('volint_mix_fronts_mpdata_shelf_dx_500_u3hc4_uwind_osc_1.nc')
ds_mix_fronts[2].to_netcdf('volint_mix_fronts_mpdata_shelf_dx_500_hsimt_uwind_osc_1.nc')

ds_mix_no_fronts[0].to_netcdf('volint_mix_mpdata_shelf_dx_500_mpdata_uwind_osc_1.nc')
ds_mix_no_fronts[1].to_netcdf('volint_mix_mpdata_shelf_dx_500_u3hc4_uwind_osc_1.nc')
ds_mix_no_fronts[2].to_netcdf('volint_mix_mpdata_shelf_dx_500_hsimt_uwind_osc_1.nc')