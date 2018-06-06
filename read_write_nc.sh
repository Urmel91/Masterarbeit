#!/bin/bash

pat=~/Masterarbeit/Daten/${1}/${2}/${3}/${4}/


if [[ ${5} =~ "-r" ]]; then
    
    read -p "Do you want to cut out lower saxony? [j/n]: " cut

    if [[ ${cut} =~ "j" ]]; then
    
        count=0
        for infile in ${pat}${2}*12.nc; do
            outfile=$(echo ${infile} | sed "s/.nc/_${count}_n.nc/g")
            ./nc_read_write.py ${infile} ${outfile} ${2}
            ((count++))
        done
    else 
        echo "stop script..."
        exit
    fi    
    
    read -p "Do you want to delete the old .nc-files? [j/n]: " janein
    
    if [[ ${janein} =~ "j" ]]; then
        echo "deleting files..."
        mv ${pat}*12.nc ~/.local/share/Trash/files/
    else
        echo "stop script..."
        exit
    fi    
fi

if [[ ${5} =~ "-c" ]] || [[ ${6} =~ "-c" ]]; then
    
    read -p "Do you want to concat the data? [j/n]: " conc

    if [[ ${cut} =~ "j" ]]; then
    
        outfile=${pat%${4}/}${2}_${3}_${4}
        ./conc_mean30_nc.py ${pat} ${outfile} ${2}
    else 
        echo "stop script"
        exit
    fi    
    
fi    
