#!/bin/bash
set -e 

./netcdf_read.sh daily tas ICHEC cclm c kom
./netcdf_read.sh daily tas ICHEC racmo c kom
./netcdf_read.sh daily tas ICHEC rca c kom
./netcdf_read.sh daily tas ICHEC remo c kom

./netcdf_read.sh daily tas MIROC cclm c kom
./netcdf_read.sh daily tas MIROC remo c kom

./netcdf_read.sh daily tas MPI cclm c kom
./netcdf_read.sh daily tas MPI rca c kom
