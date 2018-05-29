#!/usr/bin/python

import numpy as N
import glob 
import matplotlib.pyplot as plt  
import sys

def where(data, i):
    index = 0
    for line in data:
        if (line[0] > i):
            return index
        else: 
            index = index + 1

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
    return where(data, d) #wo 2ter zeitschritt beginnt

def to_years_mon(data, y):
    gp_year = month_gp(data)*12
    for i in range(len(data)):
        n_year = int(i/(gp_year))
        mon = (i % gp_year)/(gp_year/12)
        data[i,0] = str(n_year + y) + "|" + str(mon+1)
    return data    

def to_years_day(data, y):
    day_month = [31,28,31,30,31,30,31,31,30,31,30,31]
    start_mon = 0
    end_mon = 0
    for year in N.arange(1971,2101):            
        if (schaltjahr(year)):
            day_month[1] = 29
            
        elif (not schaltjahr(year)):
            day_month[1] = 28
        
        for i in N.arange(0,12):
            gp_mon = 422*day_month[i]
            start_mon = end_mon
            end_mon = start_mon + gp_mon 
            print(end_mon)
            for k in range(start_mon, end_mon):
                data[k][0] = str(year) + '|' + str(i+1)
    return data    

def schaltjahr(jahr):
    if jahr % 400 == 0:
        return True
    elif jahr % 100 == 0:
        return False
    elif jahr % 4 == 0:
        return True
    else:
        return False

def mittel30(data):
    mean30 = data[0:422]
    bla = []
    for i in range(422):
        for j in range(1,30*12):
            mean30[i,3] = (mean30[i,3] + data[i+j*422,3])            
        mean30[i,3] = mean30[i,3]/(30*12)
    mean30[:,0] = data[0,0] + "-" + data[29*12*422,0]    
    return mean30       


if __name__ == '__main__':

  data_path = "/home/vanselow/Masterarbeit/Masterarbeit/Originaldaten/mon/tas/CNRM/cclm/" 

  data = sorted(glob.glob(data_path + '*.txt'))
 
  data = readfiles(data)
  
  data = to_years_mon(data, 1971)
  
  data_30 = mittel30(data)
  
  lat = N.arange(min(data[:,1]),max(data[:,1])+0.11,0.11)
  lon = N.arange(min(data[:,2]),max(data[:,2])+0.11,0.11)
  
  lon_lat = N.meshgrid(lon,lat)
  #N.savetxt("mean_gp_30",data_30,fmt="%s %f %f %f")
  
  #test = N.zeros((2,3),'f')
  #print(test)
  
  
  nied = N.zeros((len(lat),len(lon)),'f')
  nied[:,:] = N.float(278.0)
  for line in data_30:
      ilat = line[1]+0.001
      ilon = line[2]+0.001
	  
      lat_ind = int((ilat-0.825000)/0.11)
      lon_ind = int((ilon+6.815000)/0.11)
      nied[lat_ind,lon_ind] = line[3]
  
    
  con = plt.contourf(lon_lat[0],lon_lat[1],nied)
  plt.show()
 