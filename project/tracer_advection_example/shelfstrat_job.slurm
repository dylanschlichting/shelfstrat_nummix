#!/bin/bash

##NECESSARY JOB SPECIFICATIONS
#SBATCH --job-name=SHELFSTRAT       #Set the job name to "JobExample3"
#SBATCH --time=5:00:00            #Set the wall clock limit to 12hr
#SBATCH --ntasks=72                   #Request 64 tasks
#SBATCH --ntasks-per-node=36          #Request 32 tasks/cores per node
#SBATCH --output=shelfstrat_out.%j      #Send stdout/err to "Example3Out.[jobID]"
#SBATCH --mem=15G  

##OPTIONAL JOB SPECIFICATIONS
#SBATCH --mail-type=ALL              #Send email on all job events
#SBATCH --mail-user=dylan.schlichting@tamu.edu    #Send all emails to email_address 
#SBATCH --account=132754566627 


# load intel toolchain
module load iccifort/2020.4.304 
module load impi/2019.9.304 
module load netCDF-Fortran/4.5.3
# export NETCDF=$EBROOTNETCDFMINFORTRAN
# export NETCDF_INCDIR=$EBROOTNETCDFMINFORTRAN/include
# export NETCDF_LIBDIR=$EBROOTNETCDFMINFORTRAN/lib
# export I_MPI_HYDRA_BRANCH_COUNT=8

###Timestep experiments
mpirun -np 72 ./coawstM ocean_shelfstrat_hsimt_uwind_zerop1_dt_30_50d_ensmb7.in

