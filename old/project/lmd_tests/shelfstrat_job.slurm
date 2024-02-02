#!/bin/bash

##NECESSARY JOB SPECIFICATIONS
#SBATCH --job-name=SHELFSTRAT       #Set the job name to "JobExample3"
#SBATCH --time=02:00:00            #Set the wall clock limit to 1 Day and 12hr
#SBATCH --ntasks=64                   #Request 64 tasks
#SBATCH --ntasks-per-node=32          #Request 32 tasks/cores per node
#SBATCH --output=shelfstrat_out.%j      #Send stdout/err to "Example3Out.[jobID]"
#SBATCH --mem=8G  

##OPTIONAL JOB SPECIFICATIONS
#SBATCH --mail-type=ALL              #Send email on all job events
#SBATCH --mail-user=dylan.schlichting@tamu.edu    #Send all emails to email_address 
#SBATCH --account=132754564351 #Account with 100k SUs


# load intel toolchain
module load iccifort/2020.4.304 
module load impi/2019.9.304 
module load netCDF-Fortran/4.5.3
# export NETCDF=$EBROOTNETCDFMINFORTRAN
# export NETCDF_INCDIR=$EBROOTNETCDFMINFORTRAN/include
# export NETCDF_LIBDIR=$EBROOTNETCDFMINFORTRAN/lib
# export I_MPI_HYDRA_BRANCH_COUNT=8

mpirun -np 64 ./coawstM shelfstrat_uwind_zerpoint1_f_43N.in
