import numpy as np
import xarray as xr
from datetime import datetime

# def make_frc(output='../project/shelfstrat_frc.nc',
#              ndays=11, dtw=1/48, wind_freq = 2, u_amp = 0.01, v_amp = 0, wind_freq = 2):
  
#     t = xr.DataArray(np.arange(0, ndays+dtw, dtw)[:-1], dims=['sms_time'])
#     #t*2.0*pi for diurnal, 4pi for semidiurnal. This is for downwelling winds only. 
#     uwind_strs = xr.DataArray((np.sin(t*wind_freq*np.pi)*0.5*u_amp+(0.5*u_amp)), dims=['sms_time'])
#     vwind_strs = xr.DataArray((np.sin(t*wind_freq*np.pi)*0.5*v_amp+(0.5*v_amp)), dims=['sms_time'])


#     # Create dataset
#     ds = xr.Dataset({'sms_time': t, 'sustr': uwind_strs, 'svstr': vwind_strs})

#     ds.attrs['Description'] = 'Forcing for ideal shelf'
#     ds.attrs['Author'] = 'Dylan Schlichting'
#     ds.attrs['Created'] = datetime.now().isoformat()
#     ds.attrs['type'] = 'ROMS FRC file'
#     ds['sms_time'].attrs['units'] = 'days'
#     ds['sustr'].attrs['units'] = 'Newton meter-2'
#     ds['svstr'].attrs['units'] = 'Newton meter-2'

#     print('Writing netcdf FRC file: '+output)
#     # Save dataset to a netcdf file  
#     # ds.to_netcdf(output)


# if __name__ == '__main__':
#     make_frc()

#Old code below --------
def make_frc(output='../project/shelfstrat_frc.nc',
             uwind=0, vwind=0, wind_freq = 2, Cd=1.5e-3, Rho0=1027.,
             ndays=30, dtw=1 / 24, Tramp=1.0, Tflat=1.):
  
    sustr0 = Cd * np.sqrt(uwind**2 + vwind**2) * uwind
    svstr0 = Cd * np.sqrt(uwind**2 + vwind**2) * vwind
    t = xr.DataArray(np.arange(0, ndays+dtw, dtw)[:-1], dims=['sms_time'])
    
    ramp = np.sin(t * wind_freq * np.pi) #t*2.0*pi for diurnal, 4pi for semidiurnal
    nt = int(Tflat / dtw)
    sustr1 = xr.DataArray((sustr0 * ramp), dims=['sms_time'])
    svstr1 = xr.DataArray((svstr0 * ramp), dims=['sms_time'])
    #Offset values so they are positive definite, i.e. downwelling for uwind only
    sustr2 = sustr1-sustr1.min().values
    svstr2 = svstr1-svstr1.min().values

    # Create dataset

    ds = xr.Dataset({'sms_time': t, 'sustr': sustr2, 'svstr': svstr2})

    ds.attrs['Description'] = 'Forcing for ideal shelf'
    ds.attrs['Author'] = 'Dylan Schlichting'
    ds.attrs['Created'] = datetime.now().isoformat()
    ds.attrs['type'] = 'ROMS FRC file'
    ds['sms_time'].attrs['units'] = 'days'
    ds['sustr'].attrs['units'] = 'Newton meter-2'
    ds['svstr'].attrs['units'] = 'Newton meter-2'
#     ds['bhflux'].attrs['units'] = 'watt meter-2'

    print('Writing netcdf FRC file: '+output)
    # Save dataset to a netcdf file  
    # ds.to_netcdf(output)


if __name__ == '__main__':
    make_frc()