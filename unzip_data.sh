#!/bin/bash

for myfile in Downloads/ras*.tar; do
    new_folder="${myfile%.*}/"
    mkdir -p ${new_folder}
    tar -xf ${myfile} -C ${new_folder}
    for zipfile in ${new_folder}/*.gz; do
        gzip -d ${zipfile} 
    done
    echo "."
done

#klappt es?