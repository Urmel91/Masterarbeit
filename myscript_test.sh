#!/bin/bash

#for myfile in /path/to/*.gz; do
#   gunzip ${myfile}
#done

#if [[ 0 -eq 0 ]]; then
#  echo "bla"
#fi

#for n in {1..20}; do
#  echo ${n}
#done

echo "Das hier ist text Nr. 1 von Steffen!" | sed "s/1/400/g"

#mit $() wird befehl in klammern ausgeführt und ergebnis kann
# mit liste=$() in liste gespeichert werden
liste=$(echo "Das hier ist text Nr. 1 von Steffen!")
echo ${liste}
#oder direkt:
echo $(echo "Das hier ist text Nr. 1 von Steffen!")

pat=~/Masterarbeit/*.f90

for myfile in ${pat}; do
    echo $(basename ${myfile})
    echo $(dirname ${myfile})
done    

#read -p "geben sie irgendwas ein: " text
#echo "Das ist ihre Eingabe: ${text}"

#if [[ $(echo "Das hier ist text Nr. 1 von Steffen!") =~ "Steffen" ]]; then
#  echo "Steffen kommt im text vor"
#else
#  echo "Steffen kommt nicht im text vor"
#fi

#if [[ $(echo "Das hier ist text Nr. 1 von Steffen!") =~ "Peter" ]]; then
#  echo "Peter kommt im text vor"
#else
#  echo "Peter kommt nicht im text vor"
#fi

#check_text() {
#  if [[ "${1}" =~ "${2}" ]]; then
#    echo "${2} kommt im text vor"
#  else
#    echo "${2} kommt nicht im text vor"
#  fi
#}

#check_text "${1}" "${2}"


#h=ja/ich/bin
#echo ${#h}

#myfile=hallo/iwww.nc
#outfile=${myfile%.nc}
#echo "${#outfile}"
