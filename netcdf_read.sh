#!/bin/bash



choose_path() {
  if [[ "${1}" =~ "cnrm" ]]; then
    if [[ "${2}" =~ "cclm" ]]; then
      if [[ "${3}" =~ "hist" ]]; then
	p=~/MA/Originaldaten/CNRM/cclm/hist/
      fi
    fi
  fi
}

choose_path ${1} ${2} ${3}

count=0
for myfile in ${p}pr*.nc; do
    ifort test_read.f90 -o test_read -I/muksoft/packages/netcdf/4_intel/include/ -L/muksoft/packages/netcdf/4_intel/lib64/ -lnetcdf -lnetcdff
    ./test_read ${myfile} ${count} ${#p} ${p}
    ((count++))
done


