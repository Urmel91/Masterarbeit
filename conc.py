#!/usr/bin/python

import numpy as N
import glob 
import matplotlib.pyplot as plt  
import sys


def readfiles(files):
    file2 = []
    for ifile in files:
        f = open(ifile, 'r')
        ifile = f.read().splitlines()
        f.close()
        #ifile = [line.split(' ') for line in ifile]
        for i in range(len(ifile)):
            ifile[i] = ifile[i].split(' ') #um auf einzelne daten zuzugreifen
            ifile[i] = [int(j) if j==ifile[i][0] else float(j) for j in ifile[i]]
        file2 = file2 + ifile    
    return N.array(file2,'object')    

def month_gp(data):
    d = data[0,0] #weil spater noch 1971 als ertses ist statt 1
    index = 0
    for line in data:
        if (line[0] > d):
            return index
        else: 
            index = index + 1    
    
def schaltjahr(jahr):
    if jahr % 400 == 0:
        return True
    elif jahr % 100 == 0:
        return False
    elif jahr % 4 == 0:
        return True
    else:
        return False
    
def to_years_day(data, y):
    day_month = N.array([31,28,31,30,31,30,31,31,30,31,30,31])
    start_mon = 0
    end_mon = 0
    for year in N.arange(1971,2101):            
#        start_mon = (year - 1971)*sum(day_month)*422
        if (schaltjahr(year)):
            day_month[1] = 29
            
        elif (not schaltjahr(year)):
            day_month[1] = 28
        
        for i in N.arange(0,12):
            gp_mon = 422*day_month[i]
            start_mon = end_mon
            end_mon = start_mon + gp_mon            
            data[start_mon:end_mon,0] = str(year) + '|' + str(i+1)
       # start_mon = end_mon
       # end_mon = start_mon
    return data    

def to_years_mon(data, y):
    gp_year = month_gp(data)*12
    for i in range(len(data)):
        n_year = int(i/(gp_year))
        mon = (i % gp_year)/(gp_year/12)
        data[i,0] = str(n_year + y) + "|" + str(mon+1)
    return data    

def mean_day(data):
    day_end = 422
    day_start = 0
    day = day_end - day_start
    anzahl_day = len(data)/day
    day_mean = N.zeros((int(anzahl_day),2),'object')
    for i in xrange(len(day_mean)):
        day_mean[i,0] = data[day_start,0]
        day_mean[i,1] = N.mean(data[day_start:day_end,3])
        day_start = day_start + day
        day_end = day_end + day
    return day_mean

def mean_mon(data):
    month_end = month_gp(data)/12    #so festlegen welche daten noch
    month_start = 0            #zu einem monat gehoeren 
    month = month_end - month_start
    anzahl_mon = len(data)/month
    mm = N.zeros((int(anzahl_mon),2), 'object')
    for i in xrange(len(mm)): 
        mm[i,0] = data[month_start,0]
        mm[i,1] = N.mean(data[month_start:month_end,3])
        month_start = month_start + month    
        month_end = month_end + month
    return mm


if __name__ == '__main__':
 
  data_path = sys.argv[1]
  mon_or_d = sys.argv[2]
  
  data = sorted(glob.glob(data_path + '*.txt'))
  data = readfiles(data)

  if ( mon_or_d == "mon" ):
      concat = to_years_mon(data, 1971)
  elif ( mon_or_d == "daily" ):
      concat = to_years_day(data, 1971)

  print("concat fineshed...")
  path = ""
  data_name = data_path.split("/")[6]+"_"+data_path.split("/")[7]+"_"\
      +data_path.split("/")[8]
  print("save data as...", data_name)
  for i in range(1,len(data_path.split("/"))-2):
      path = path + "/" + data_path.split("/")[i]
  data_name = path + "/" + data_name
  
  if ( mon_or_d == "mon" ):
      result = mean_mon(concat)
  elif ( mon_or_d == "daily" ):
      result = mean_day(concat)
  
#  N.savetxt(data_name,result,fmt='%4d %1.5f')
  N.savetxt(data_name,result,fmt='%7s %1.5f')
  print("data saved!")
        
