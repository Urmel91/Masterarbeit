#!/usr/bin/python

import numpy as N
import glob 
import matplotlib.pyplot as plt
import mystats as ms  
import sys

def length_files(files):
    length = 0
    for ifile in files:
        fileobj = open(ifile, 'r')
        afile = fileobj.readlines()
        length = length + len(afile)
        fileobj.close()
    return length

def readfiles(files):
    length = length_files(files)
    output = N.zeros((length, 4), 'object') #object damit jahre in int
    k = 0
    for ifile in files:
        fileobj = open(ifile, 'r')
        afile = fileobj.readlines()
        fileobj.close()
        for i in xrange(len(afile)): #-1 weil letzte zeit \n ist
            afile[i] = afile[i][0:28].split(' ') #bis 28 um \n loszuwerden
            for j in xrange(len(afile[i])):
                output[k + i][j] = float(afile[i][j])
        k = k + len(afile) 
    return output    

def conc(data1, data2):
    length = len(data1) + len(data2)
    data = N.zeros((length, N.shape(data1)[1]), 'object') #shape gibt (anzahl zeilen, anzahl spalten) aus, brauchen nur spalten
    data[0:len(data1)] = data1
    data[len(data1):length] = data2
    return data
    
def month_gp(data):
    d = data[0,0] #weil spater noch 1971 als ertses ist statt 1
    index = N.where(data[:,0] > d) #wo 2ter zeitschritt beginnt
    month_end = index[0][0]    #so festlegen welche daten noch
    month_start = 0            #zu einem monat gehoeren 
    month = month_end - month_start
    return month

def to_years(data, y):
    gp_year = month_gp(data)*12
    for i in xrange(len(data)):
        rest = int(i/(gp_year)) 
        data[i,0] = rest + y
        data[i,0] = int(data[i,0])        
    return data    

def read_conc(his, data):
    his = readfiles(his)
    data = readfiles(data)
    data = conc(his, data)
    to_years(data, 1971)
    return data    

def mean_mon(data):
    month_end = month_gp(data)/12    #so festlegen welche daten noch
    month_start = 0            #zu einem monat gehoeren 
    month = month_end - month_start
    anzahl_mon = len(data)/month
    mm = N.zeros((int(anzahl_mon),2), 'object')
    for i in xrange(len(mm)): 
        mm[i,0] = int(data[month_start,0])
        mm[i,1] = N.mean(data[month_start:month_end,3])
        month_start = month_start + month    
        month_end = month_end + month
    return mm


if __name__ == '__main__':
 
  hist_path = sys.argv[1]
  rcp_path = sys.argv[2]

  his_data = sorted(glob.glob(hist_path + '*.txt'))
  rcp_data = sorted(glob.glob(rcp_path+'*.txt'))

  concat = read_conc(his_data, rcp_data)
  path = ""
  data_name = rcp_path.split("/")[5]+"_"+rcp_path.split("/")[6]
  for i in range(1,len(rcp_path.split("/"))-2):
      path = path + "/" + rcp_path.split("/")[i]

  data_name = path + "/" + data_name
  result = mean_mon(concat)
        
  N.savetxt(data_name,result,fmt='%4d %1.5f')
        
