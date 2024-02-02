
"""
basecase_wind.py

Created by Rob Hetland on 2007-10-15.
Initially modified by Veronica Ruiz Xomchuk on 2019-08 for hypoxia work
Further modified by Dylan Schlichting on 2022-10 for numerical mixing work
Copyright (c) 2022 Texas A&M Univsersity. All rights reserved.
Release under MIT license.

Same as basecase.py, but for prescribed surface momentum stress via winds 
"""
from grd import make_grd
from frc import make_frc
from ini import make_ini

import os
import warnings


class ROMS_in(object):
    """docstring for ROMS_IN"""

    def __init__(self, infile):
        self.infile = infile
        f = open(self.infile)

        self.variables = {}
        self._varlist = [] # to keep the order of variables
        same = False
        for line in f.readlines():
            if '!' not in line[0]:
                if '=' in line:
                    vals = line.split('=')
                    varname = vals[0].strip()
                    self._varlist.append(varname)
                    varval = vals[-1].strip()
                elif same:
                    varval = varval+'\n' +  line.strip('\n')
                else:
                    varname = 'none'
                    varval = 'none'
                if '\\' in line.split('!')[0]:
                    same = True
                else:
                    same = False
                self.variables[varname] = varval

    def write(self, filename):
        """docstring for write"""
        f = open(filename, 'w')
        for key in self._varlist:
            f.write('%s == %s\n' % (key, str(self.variables[key])))
        f.close()

    def __setitem__(self, key, val):
        """docstring for __setitem__"""
        if key not in self._varlist:
            self._varlist.append(key)
            warnings.warn('%s not previously in variable list.' % key)
        self.variables[key] = str(val)


def run_case(case, z0=0.003, dt=30.0, rootdir='./runs/across_shelf_long/'):

    print('BUILD new case')
    if not os.path.exists(rootdir):
        os.makedirs(rootdir)

    grd_str = 'ho_' + str(int(case['grd']['ho']))
    frc_str = 'uwind_' + str(case['frc']['uwind'])+'_windtype_' + str(int(case['frc']['wind_freq']))
    dx_str = 'dx_' + str(int(case['grd']['dx'])) # the grid resolution is isotropic so dx = dy.
    ID = grd_str + '_' + frc_str + '_' + dx_str
    # grd_name = rootdir + 'shelf_' + grd_str + '_' + dx_str + '_f_43N' + '_grd.nc'
    # frc_name = rootdir + 'shelf_' + frc_str + '_' + dx_str + '_frc.nc'
    # ini_name = rootdir + 'shelf_' + grd_str + '_' + dx_str + '_f_43N' + '_ini.nc'
    
    grd_name = rootdir + 'shelf_' + grd_str + '_' + dx_str + '_f_43N_' + 'across2x_ensmb7' + '_grd.nc'
    frc_name = rootdir + 'shelf_' + frc_str + '_' + dx_str + '_frc.nc'
    ini_name = rootdir + 'shelf_' + grd_str + '_' + dx_str + '_f_43N_' + 'across2x_ensmb7' + '_ini.nc'


    if not os.path.isfile(grd_name):
        make_grd(grd_name,
                 Hmin=case['grd']['Hmin'],
                 alpha=case['grd']['alpha'],
                 ho=case['grd']['ho'],

                 f=case['grd']['f'],
                 dx=case['grd']['dx'],
                 dy=case['grd']['dy'],
                 shp=case['grd']['shp'])
    if not os.path.isfile(frc_name):
        make_frc(frc_name,
                 uwind=case['frc']['uwind'],
                 vwind=case['frc']['vwind'],
                 ndays=case['frc']['ndays'],
                 dtw = case['frc']['dtw'],
                 Tramp=case['frc']['Tramp'],
                 Tflat=case['frc']['Tflat'],
                 Cd=case['frc']['Cd'])
    if not os.path.isfile(ini_name):
        make_ini(ini_name, grd_name,
                 zlevs=case['ini']['zlevs'],
                 theta_s=case['ini']['theta_s'],
                 theta_b=case['ini']['theta_b'],
                 hc=case['ini']['hc'],
                 R0=case['ini']['R0'],
                 T0=case['ini']['T0'],
                 S0=case['ini']['S0'],
                 TCOEF=case['ini']['TCOEF'],
                 SCOEF=case['ini']['SCOEF'],
                 M20=case['ini']['M20'],
                 M2_yo=case['ini']['M2_yo'],
                 M2_r=case['ini']['M2_r'],
                 N20=case['ini']['N20'],
                 N2_zo=case['ini']['N2_zo'],
                 N2_r=case['ini']['N2_r'],
                 balanced_run=True)

    return
#shp:97 by 97 km. 
#shp: 51 by 51 for 2000 m, 99X99 for 1000 m case, 195x195 for 500 m case.
#387x387 for the 250 m case
if __name__ == '__main__':

    case = {'grd': {'Hmin': 5.0,
                    'alpha': 0.001,
                    'ho': 5.,
                    'f': 1e-4,# 6.846773271669432e-05 for 28N, 1e-4 for 43N
                    'dx': 500, #originally 1000, then 500, then 250
                    'dy': 500,
                    'shp': (390, 195), #195x195 for original domain
                    },
            'frc': {'uwind': 0, 
                    'vwind': 0.,
                    'Cd': 1.5e-3,
                    'wind_freq': 2., #2 for diurnal, 4 for semidiurnal
                    'Rho0': 1027.,
                    'ndays': 30,
                    'dtw': 1/24,
                    'Tramp': 3.,
                    'Tflat': 3.,
                    },
            'ini': {'zlevs': 30, # Originally 30 
                    'theta_s': 5.,
                    'theta_b': .4,
                    'hc': 5.,
                    'R0': 1027.,
                    'T0': 25.,
                    'S0': 35.,
                    'TCOEF': 1.7e-4,
                    'SCOEF': 7.6e-4,
                    'M20': 1e-6,#10**(-5.55882) to get initial salinity from 15 to 35 
                    'M2_yo': 50e3,
                    'M2_r': 5e3,
                    'N20': 1e-4,
                    'N2_zo': 50.,
                    'N2_r': 50.,
                    },
            }

    run_case(case, dt=30.0)
