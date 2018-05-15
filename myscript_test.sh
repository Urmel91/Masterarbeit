#!/bin/bash

#for myfile in /path/to/*.gz; do
#   gunzip ${myfile}
#done

if [[ 0 -eq 0 ]]; then
  echo "bla"
fi

for n in {1..20}; do
  echo ${n}
done

echo "Das hier ist text Nr. 1 von Steffen!" | sed "s/1/400/g"

echo $(echo "Das hier ist text Nr. 1 von Steffen!")


if [[ $(echo "Das hier ist text Nr. 1 von Steffen!") =~ "Steffen" ]]; then
  echo "Steffen kommt im text vor"
else
  echo "Steffen kommt nicht im text vor"
fi

if [[ $(echo "Das hier ist text Nr. 1 von Steffen!") =~ "Peter" ]]; then
  echo "Peter kommt im text vor"
else
  echo "Peter kommt nicht im text vor"
fi

check_text() {
  if [[ "${1}" =~ "${2}" ]]; then
    echo "${2} kommt im text vor"
  else
    echo "${2} kommt nicht im text vor"
  fi
}

check_text "${1}" "${2}"

count=0
for n in {1..3}; do
    echo ${count}
    ((count++))
done

h=ja/ich/bin
echo ${#h}