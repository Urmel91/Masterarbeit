#!/bin/bash



choose_path() {
  if [[ "${1}" =~ "cnrm" ]]; then
    if [[ "${2}" =~ "cclm" ]]; then
#      if [[ "${3}" =~ "hist" ]]; then
	phist=~/MA/Originaldaten/CNRM/cclm/hist/
#      elif [[ "${3}" =~ "rcp" ]]; then
	prcp=~/MA/Originaldaten/CNRM/cclm/rcp85/
#      fi
    fi
  fi
}

choose_path ${1} ${2} #${3}

echo "reading hist data..."

count=0
for infile in ${phist}pr*.nc; do
    outfile=${infile%.nc}
    ifort netcdf_read.f90 -o netcdf_read -I/muksoft/packages/netcdf/4_intel/include/ -L/muksoft/packages/netcdf/4_intel/lib64/ -lnetcdf -lnetcdff
    ./netcdf_read ${infile} ${count} ${#outfile} ${outfile}
    ((count++))
done

echo "reading rcp85 data..."

count=0
for infile in ${prcp}pr*.nc; do
    outfile=${infile%.nc}
    ifort netcdf_read.f90 -o netcdf_read -I/muksoft/packages/netcdf/4_intel/include/ -L/muksoft/packages/netcdf/4_intel/lib64/ -lnetcdf -lnetcdff
    ./netcdf_read ${infile} ${count} ${#outfile} ${outfile}
   ((count++))
done

echo "concat data..."

./concat.py ${phist} ${prcp}

