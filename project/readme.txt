#This file contains information about the simulation output. 
Working document so check for changes.

#10/2022
## Simulation naming convention
--- shelf + dx + vertical layers + wind + time + tracer advection scheme
--- Unforced simulation example: shelf_dx_1000_nvert_30_30days_MPDATA
--- Forced simulation with U wind stress example: shelf_dx_1000_nvert_30_uwind_5_30days_MPDATA

## All simulations have an initial depth at the southern coast of 5 m. 
## ROMS will have to compiled and run separately for the below simulations because they are unforced, meaning they require pure analytical forcing. Check one of the directories for header file
/shelf_ho_5_dh_0_dx_1000_2days/ : Test of the basecase designed to be run for just 2 days to make sure the output parameters are correct. 
/shelf_ho_5_dh_0_dx_1000_2days_nummix/ : Same as /shelf_ho_5_dh_0_dx_1000_2days/, but includes online resolved and numerical mixing
/shelf_ho_5_dh_0_dx_1000_30days/ : Same same as /shelf_ho_5_dh_0_dx_1000_2days_nummix/ but run for 30 days. 

## Start of forced simulations: All 30 days with wind stress & online mixing 
/shelf_ho_5_dh_0_dx_1000_uwind_5_30days/ : along-shelf wind stress based on a variable wind speed from 0-5 m/s  
/shelf_ho_5_dh_0_dx_1000_vwind_5_30days/ : across-shelf wind stress based on a variable wind speed from 0-5 m/s  

##The compiled coawst file coawstM is configured for the current version of shelfstrat.h listed in this directory. If other CPP flags are required, then the model will have to be recompiled with coawst.bash. That can take up to five minutes to run if not cleaned first. 

#Update: 02/07/2023
shelfstrat is being used on two clusters: Grace, TAMU HPRC and Copano, in-house
linux cluster for the Physical Oceanography Numerical Group. I usually generate 
the input for the simulations on Copano then run on Grace. The build script and 
COAWST executable are valid for Grace only because of the paths. <br>

Naming convention is changing frequently. Will provide better documentation in
Q1 2023 to clarify. 

