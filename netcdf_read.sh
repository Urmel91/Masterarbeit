#!/bin/bash

pat=~/Schreibtisch/Masterarbeit/Originaldaten/${1}/${2}/${3}/${4}/

phist=${pat}hist/
prcp=${pat}rcp85/

if [[ ${5} =~ "r" ]]; then

    echo "reading hist data..."

    count=0
    for infile in ${phist}${2}*.nc; do
        outfile=${infile%.nc}
        gfortran-6 netcdf_read.f90 -o netcdf_read -I/usr/local/netcdf/include -L/usr/local/netcdf/lib/ -lnetcdf -lnetcdff    
#       ifort netcdf_read.f90 -o netcdf_read -I/muksoft/packages/netcdf/4_intel/include/ -L/muksoft/packages/netcdf/4_intel/lib64/ -lnetcdf -lnetcdff
        ./netcdf_read ${infile} ${count} ${#outfile} ${outfile} ${2}
        ((count++))
    done

    echo "reading rcp85 data..."

    count=0
    for infile in ${prcp}${2}*.nc; do
        outfile=${infile%.nc}
        gfortran-6 netcdf_read.f90 -o netcdf_read -I/usr/local/netcdf/include -L/usr/local/netcdf/lib/ -lnetcdf -lnetcdff        
#       ifort netcdf_read.f90 -o netcdf_read -I/muksoft/packages/netcdf/4_intel/include/ -L/muksoft/packages/netcdf/4_intel/lib64/ -lnetcdf -lnetcdff
        ./netcdf_read ${infile} ${count} ${#outfile} ${outfile} ${2}
        ((count++))
    done

    rm -r ${phist}*.nc
    rm -r ${prcp}*.nc
fi

if [[ ${5} =~ "c" ]] || [[ ${6} =~ "c" ]]; then
    echo "concat data..."

    ./concat.py ${phist} ${prcp}
fi
