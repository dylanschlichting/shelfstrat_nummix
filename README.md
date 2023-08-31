# Shelfstrat - Idealized simulations of submesoscale baroclinic instabilities over sloping bathymetry
```shelfstrat``` contains information required to run idealized ROMS simulations of submesoscale baroclinic instabilities over sloping bathymetry. Developed by Rob Hetland for Hetland (2017) JPO. Model setup modified by Dylan Schlichting for exploration of numerical salinity mixing and surface fronts. ROMS is configured as part of COAWST ver. 3.7 for these simulations.
## Running the model
Six input files are required to run ```shelfstrat```: the numerical grid, initial conditions, forcing (if applicable), a header file used to compile the model, a ROMS input file, and a slurm job script. The simulations are run on the Grace cluster from TAMU's HPRC resources. The key scripts and files are

    grd/make_grd.py
    ini/make_ini.py
    frc/make_frc.py
    project/shelfstrat.h
    project/ocean_shelfstrat_basecase_f_43N.in
    project/shelfstrat_job.slurm

## Model setup
Key points of the unforced and wind-forced configurations are documented for reference:
> - Standard output frequency: 1 hour
> - 500 m isotropic lateral grid resolution
> - 192 x 192 x 30 grid points
> > - ```Vtransform=2,Vstretching=4```, ```\theta_s = 5.0, \theta_b = 0.4```
> > - Tested ```\theta_s = 3.0, \theta_b = 1``` and ```\theta_s = 2.5, \theta_b = 2.5``` for vertical resolution experiments
> > - Changed number of vertical layers to 60 and 120 for vertical resolution experiments
> - Online timestep ```dt= 30 s```
> - MPDATA for momentum and tracer advection
> > - HSIMT and U3HC4 tested for tracer advection experiments (in progress)
> - No explicit lateral mixing (viscosity or diffusivity coefficients) applied
> - Calculates online physical and numerical mixing with average files.
> > - Physical mixing is the destruction of salinity variance $\chi^s = 2 \mathbf{\kappa} \left(\nabla s \right)^2$ (Osborn & Cox, 1972)
> > - Numerical mixing is defined using the Burchard and Rennau (2008) *O.M.* algorithm: $\mathcal{M}_{num} = \frac{\mathcal{A}(s^2)-(\mathcal{A})^2}{\Delta t}$,
> > > - $\mathcal{A}$ is the advection operator
> > > - $\Delta t$ is the model timestep

## Output analysis
Key analyses are presented here. There are scripts and notebooks to calculate
> - Volume-integrated physical ```Akr``` and numerical mixing ```dye_03```(see Schlichting et al. 2023)
> - Volume-integrated EKE, MKE, and TKE
> - Mean vertical salinity gradient $|\partial_z s|$ and vertical salinity diffusivity $\kappa_s$ ```Aks```
> - Analyze mixing in salinity coordinates

## Misc notes
Miscellaneous analysis and code tests are also stored in this repository. For example,
> - ```/project/lmd_tests/``` contains a 15 day test run where the vertical mixing scheme is changed from GLS to KPP (Large et al., 1994) for a postdoc at PNNL. 
