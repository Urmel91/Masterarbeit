#!/usr/bin/python3

'''
----------------------------------------------------
< liest dwd.txt data ein und schreibt diese in nc data
'''

from netCDF4 import Dataset
import numpy as np
import glob 
import matplotlib.pyplot as plt  
import sys
import numpy.ma as ma
import coord_trafo as ct
import mod_calculations as ca

if __name__ == '__main__':

    opt = sys.argv[1]
    time = sys.argv[2]
    var = sys.argv[3]
        

    data_path = "/home/steffen/Masterarbeit/Daten/"+time+"/"+var+"/"
    
    data = sorted(glob.glob(data_path+'*.nc'))
    
    f = Dataset(data[0], 'r')
    rlats=f.variables['rlat'][:]
    rlons=f.variables['rlon'][:]
    f.close()
    
    #----- calculate lons, lats in gographical coordinates ------
    lon_lat_r = np.meshgrid(rlons,rlats)
    lons, lats = ct.coord_traf(2, lon_lat_r[0], lon_lat_r[1])
    
    #----- calculating floating mean for every month -------------------------
    fm_month = np.zeros((len(data),30*12), 'f')
    data = [ca.read_data(data[i],var) for i in range(len(data))]
    
    mon = ca.mon_mean_his(data)
    
    jahresgang = np.zeros((len(mon),12),'f')
    for k in range(len(data)):
        for j in range(30):
            for i in range(12):
                fm_month[k, i+j*12] = mon[k][i+j*12] 
        jahresgang[k] = ca.mon_over_y(fm_month[k])
    
    #------ Datenaufbereitung --------------------------------------
    if ( var == 'tas' ):
        jahresgang = jahresgang - 273.15
        
    elif (var == 'pr' ):
        day_month = np.array([31,28,31,30,31,30,31,31,30,31,30,31])
        for i in range(12):
            jahresgang[:,i] =  jahresgang[:,i] * day_month[i]*60*60*24
            
    #-------- Bandbreite berechnen ------------------------------------
    jg_min = [min(jahresgang[:,i]) for i in range(len(jahresgang[0]))]
    jg_max = [max(jahresgang[:,i]) for i in range(len(jahresgang[0]))]
    
    
    #------- reading dwd data --------------------------------------------
    if ( var == 'tas' ):
        data_his = ca.read_his('hDWD.txt')
        if ( opt == 'h' ):
            data_his2 = ca.read_his('dwdpr.txt')
            
    elif ( var == 'pr' or var2 == 'pr'):    
        data_his = ca.read_his('dwdpr.txt')

    #print(max(data_his),min(data_his))

    if ( opt == 'h' ):
        ca.plot_jahresgang_hist(data_his, data_his2)
        
    elif ( opt == 'e' ):
        #print(jahresgang)
        jahresgang_e = np.median(jahresgang, axis=0)
        dif = data_his - jahresgang_e
        pro = dif/data_his * 100
        for i in range(12):
            print('{}: {} entspricht {}'.format(i, dif[i], pro[i]))
        print('dif mean: {} entspricht {}'.format(np.mean(dif),np.mean(pro)))    
            
        #ca.plot_jahresgang(jahresgang_e, data_his, jg_min, jg_max, var)
    
