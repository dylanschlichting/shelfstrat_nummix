# Shelfstrat - Idealized coastal shelf model
```shelfstrat``` contains information required to run idealized ROMS simulations of submesoscale baroclinic instabilities over sloping bathymetry as described in Schlichting et al. 2024 *JAMES*. Developed by Rob Hetland, as documented in Hetland (2017) *JPO*. Here, the model setup is modified to explore the relationship between numerical salinity mixing and surface fronts. ROMS is configured as part of COAWST ver. 3.7 for these simulations. ROMS ver. 3.9 is used in all simulations.
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
> - 97 x 97 km in the along- and across-shore directions for all cases except tracer advection ensemble
> > - 192 x 192 x 30 grid points
> > - ```Vtransform=2,Vstretching=4```, ```\theta_s = 5.0, \theta_b = 0.4```
> > - Tested ```\theta_s = 3.0, \theta_b = 1``` and ```\theta_s = 2.5, \theta_b = 2.5``` for vertical resolution experiments
> > - Changed number of vertical layers to 60 and 120 for vertical resolution experiments
> - Online timestep ```dt= 30 s```
> - MPDATA for momentum and tracer advection
> > - HSIMT and U3HC4 used in tracer advection experiments
> - No explicit lateral mixing (viscosity or diffusivity coefficients) applied
> - Calculates online physical and numerical mixing with average files
> > - Physical mixing is the destruction of salinity variance $\chi^s = 2 \mathbf{\kappa} \left(\nabla s \right)^2$ (Osborn & Cox, 1972)
> > - Numerical mixing is defined using the Burchard and Rennau (2008) *OM* algorithm: $\mathcal{M}_{num} = \frac{\mathcal{A}(s^2)-(\mathcal{A})^2}{\Delta t}$,
> > > - $\mathcal{A}$ is the advection operator
> > > - $\Delta t$ is the model timestep
> - Tracer advection ensemble:
> > - Input files provided in ```project/tracer_advection_example```

## Output analysis and QC
Key analyses are presented here. There are scripts and notebooks to calculate
> - Volume-integrated physical ```Akr``` and numerical mixing ```dye_03```(see Schlichting et al. (2023) *JAMES*)
> - Volume-integrated EKE, MKE, and TKE
> - Alongshore and ensemble averaged tracer cross sections
> - Check lateral and vertical resolution parameters for the idealized and realistic model

## Key publications
> - Ruiz Xomchuk, V. I. (2020). Intraseasonal Variability in Northern Gulf of Mexico Hypoxia: Impacts of Baroclinic Instability, Rough Topography, and Exposure Duration (*Doctoral dissertation*).
> - Zhang, W., & Hetland, R. D. (2018). A study of baroclinic instability induced convergence near the bottom using water age simulations. *Journal of Geophysical Research: Oceans*, 123, 1962–1977. https://doi.org/10.1002/2017JC013561.
> - Hetland, R. D. (2017). Suppression of baroclinic instabilities in buoyancy-driven flow over sloping bathymetry. *Journal of Physical Oceanography*, 47(1), 49-68. https://doi.org/10.1175/JPO-D-15-0240.1.
