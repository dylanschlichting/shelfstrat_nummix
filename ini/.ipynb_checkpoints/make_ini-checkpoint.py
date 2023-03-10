import numpy as np
import xarray as xr
from datetime import datetime

'''
    Create an initialization file.
    Horizontal stratification is controlled by salinity (only)
    Vertical stratification is controlled by temperature (only)
    Stratification properties are conservative through
    a linear equation of state:
       R0 == 1027.0d0                   ! kg/m3
       T0 == 25.0d0                      ! Celsius
       S0 == 35.0d0                     ! PSU
    TCOEF == 1.7d-4                     ! 1/Celsius
    SCOEF == 7.6d-4                     ! 1/PSU
'''

def get_depths(h, hc, s, Cs, dim):
    """SEE Eq. (2) or (3) on https://www.myroms.org/wiki/Vertical_S-coordinate"""
    return (hc * s + h * Cs) / (hc + h) * h


def C(theta_s, theta_b, s):
    C = (1.0 - np.cosh(theta_s * s)) / (np.cosh(theta_s) - 1.0)
    if theta_b > 0.0:
        return (np.exp(theta_b * C) - 1.0) / (1.0 - np.exp(-theta_b))
    else:
        return -C

#Veronica's O2 code - comment out
def ox_sat(temp, salt):
    A1 = -173.4292
    A2 =  249.6339
    A3 =  143.3483
    A4 =  -21.8492
    B1 =   -0.033096
    B2 =    0.014259
    B3 =   -0.0017000

    Tk = temp + 273.15 #     Convert temperature to Deg. Kelvin
    #Calculate saturation O2.
    return np.exp(A1 + A2 * (100.0 / Tk) + A3 * np.log(Tk / 100.0) + A4 * (Tk / 100.0) +
                  salt * (B1 + B2 * (Tk / 100.0) + B3 * ((Tk / 100.0)**2))) * 44.661

# Modified by Dylan Schlichting. Base case below!
def make_ini(output='../project/shelfstrat_ini.nc', grd_path='../project/shelfstrat_grd.nc',
             zlevs=30, theta_s=3.0, theta_b=0.4, hc=5.0,
             R0=1027.0, T0=25.0, S0=35.0, TCOEF=1.7e-4, SCOEF=7.6e-4,
             M20=1e-6, M2_yo=50e3, M2_r=5e3,
             N20=1e-4, N2_zo=50.0, N2_r=50.0,
             balanced_run=True):
    '''
    Create an initialization file.

    Horizontal stratification is controlled by salinity (only)
    Vertical stratification is controlled by temperature (only)

    Stratification properties are conservative through
    a linear equation of state:

       R0 == 1027.0d0                   ! kg/m3
       T0 == 25.0d0                      ! Celsius
       S0 == 35.0d0                     ! PSU
    TCOEF == 1.7d-4                     ! 1/Celsius
    SCOEF == 7.6d-4                     ! 1/PSU
    '''

    grd = xr.open_dataset(grd_path)
    g = 9.81
    dy = 1 / grd.pn
    s_w = xr.DataArray(np.linspace(-1., 0., zlevs + 1), dims=['s_w'])
    s_rho = np.linspace(-1., 0., zlevs + 1)
    s_rho = s_rho[:-1] + np.diff(s_rho) / 2
    s_rho = xr.DataArray(s_rho, dims=['s_rho'])
    Cs_r = C(theta_s, theta_b, s_rho)
    Cs_w = C(theta_s, theta_b, s_w)

    M2 = M20 * np.exp((M2_yo - grd.y_rho) / M2_r)
    M2 = M2.where(grd.y_rho > M2_yo, M20)
    salt = (M2 * dy / g / SCOEF).cumsum(axis=0)
    salt -= salt[-1] - S0
    salt = salt.expand_dims('s_rho') * np.ones((zlevs, 1, 1), 'd')
    salt.coords['s_rho'] = s_rho
    # (h, hc, s, Cs)
    z = get_depths(grd.h, hc, s_rho, Cs_r, 's_rho')
    Hz = get_depths(grd.h, hc, s_w, Cs_w, 's_w').diff('s_w').rename({'s_w': 's_rho'})
    Hz.coords['s_rho'] = s_rho
    N2 = N20 * np.exp(-(N2_zo - z) / N2_r)
    N2 = N2.where(z > N2_zo, N20)

    temp = xr.zeros_like(salt)
    for n in range(zlevs):
        temp[n] = T0 - np.trapz(N2[n:] / (g * TCOEF), x=z[n:], axis=0)

    #########################################
    # Create dataset

    ds = xr.Dataset({'temp': temp, 'salt': salt,
                     's_rho': s_rho, 'xi_rho': grd.xi_rho, 'eta_rho': grd.eta_rho})

    if balanced_run:
        rhs = Hz * M2 / grd.f
        u_z = 0.5 * (rhs[:, :, 1:] + rhs[:, :, :-1])
        u = np.cumsum(u_z, axis=0)
        ubottom = np.zeros((1, u.shape[1], u.shape[2]))
        u = np.concatenate((ubottom, u))
        u = 0.5 * (u[1:] + u[:-1])
    else:
        u = 0.

    ds['ocean_time'] = xr.DataArray([0.0], dims=['ocean_time'])
    ds['ocean_time'].attrs['units'] = 'days'

    ds['u'] = xr.DataArray(u[np.newaxis, :, :, :],
                           dims=['ocean_time', 's_rho', 'eta_u', 'xi_u'],
                           attrs={'units': 'm s-1'})
    ds['v'] = xr.DataArray(np.zeros((1, int(zlevs), grd.dims['eta_v'], grd.dims['xi_v'])),
                           dims=['ocean_time', 's_rho', 'eta_v', 'xi_v'],
                           attrs={'units': 'm s-1'})
    ds['zeta'] = xr.DataArray(np.zeros((1, grd.dims['eta_rho'], grd.dims['xi_rho'])),
                              dims=['ocean_time', 'eta_rho', 'xi_rho'],
                              attrs={'units': 'm'})
    ds['ubar'] = xr.DataArray(np.zeros((1, grd.dims['eta_u'], grd.dims['xi_u'])),
                              dims=['ocean_time', 'eta_u', 'xi_u'],
                              attrs={'units': 'm s-1'})
    ds['vbar'] = xr.DataArray(np.zeros((1, grd.dims['eta_v'], grd.dims['xi_v'])),
                              dims=['ocean_time', 'eta_v', 'xi_v'],
                              attrs={'units': 'm s-1'})
#     ds['dye_01'] = ox_sat(ds.temp, ds.salt)

    ds.attrs['type'] = 'ROMS FRC file'
    ds.attrs['Description'] = 'Initial conditions for ideal shelf'
    ds.attrs['Author'] = 'Dylan Schlichting'
    ds.attrs['Created'] = datetime.now().isoformat()
    print('Writing netcdf INI file: '+output)
    ds.to_netcdf(output)


if __name__ == '__main__':
    make_ini()