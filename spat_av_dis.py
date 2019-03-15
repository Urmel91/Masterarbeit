#!/usr/bin/python3

'''
Berechnungen von jahresmittelwerten oder täglichen Werten von temp, pr oder
extremereignissen. 

Zwei Möglichkeiten:

Räumliche Berechnungen für Temp, Pr oder ein Extremereignis. Zeitliche Mittel 
kann tägliche oder über Zeiträume 1971-2000, 2021-2050, 2071-2100 gemittelte
Daten ausgeben.

Zeitreihen, also über ganz Niedersachsen gemittelte Größen der jahresmittel_
von temp, pr oder Extremereignissen.

input: [1] var , e.g. tas, pr, tasmax,...
       [2] opt, räumlich (spat) oder zeitreihe (ts)
       [3] exer, was soll berechnet werden? Extremereignis, temp, pr,...
       
output: spat: nc_datei
        ts: csv-datei
'''

from netCDF4 import Dataset
import numpy as np
import glob 
import matplotlib.pyplot as plt  
import sys
from matplotlib import colors
from mpl_toolkits.basemap import Basemap
import coord_trafo as ct
import numpy.ma as ma
import time
import mod_calculations as ca
import pandas as pd
from scipy.stats import norm


if __name__ == '__main__':
    
    var = sys.argv[1]
    opt = sys.argv[2]
    exer = sys.argv[3]
    jz = sys.argv[4]
    
    data_path = "/home/steffen/Masterarbeit/Daten/daily/"+var+"/"
    data = sorted(glob.glob(data_path+'*.nc'))
    
    f = Dataset(data[0], 'r')
    rlats=f.variables['rlat'][:]
    rlons=f.variables['rlon'][:]
    f.close()
            
    #----- calculate lons, lats in gographical coordinates ------
    lon_lat_r = np.meshgrid(rlons,rlats)
    lons, lats = ct.coord_traf(2, lon_lat_r[0], lon_lat_r[1])

    if (opt == 'sp'):
        #< räumliche jährliche Werte für jeden GP und jedes Modell
        
        result = ma.array(np.zeros((9,130,31,34),'f'))
        for i, ifile in enumerate(data):
            result[i] = ca.extrem(ca.read_data(ifile, var),opt,var,exer)
        ca.writing_nc(result, "spat_{}_{}.nc".format(var,exer), var, rlats, rlons,ensemble=True)
    '''

    #< räumliche tägliche Werte für jeden GP und jedes Modell
    #< eingabe: exer = day, weitere verarbeitung der jz bei analyse
    #< wichtig für robustheitsanalyse
    if (opt == 'spatday'):
        
        result = ma.array(np.zeros((9,47482,31,34),'f'))
        for i, ifile in enumerate(data):
            result[i] = ca.extrem(ca.read_data(ifile, var),opt,var,exer)
        ca.writing_nc(result, "spat_{}_{}.nc".format(var,exer), var, rlats, rlons,em=False)

    #< räumliche jährlich extremwerte für jeden gp
    if (opt == 'spatex'):
        
        result = ma.array(np.zeros((9,130,31,34),'f'))
        
        for i, ifile in enumerate(data):
            
            print("calculating for cm{}".format(i))
            result[i] = ca.extrem(ca.read_data(ifile, var),opt,var,exer,jz)
            
        ca.writing_nc(result, "spatex_{}_{}_{}.nc".format(var,exer,jz), var, rlats, rlons,em=False)

    #< räumliche Klimaänderugnssignale im ensemblemedian
    #< ensemblemedian oder floatingmean jedes modells berechnen        
    if ( opt == "spat" ):
        
        em_or_fm = sys.argv[5] 
        
        result = ma.array(np.zeros((9,3,31,34),'f'))
        for i, ifile in enumerate(data):
            print("calculating for cm{}".format(i))
            result[i] = ca.extrem(ca.read_data(ifile, var),opt,var,exer,jz)
        em = ma.array(np.zeros((3,31,34),'f'))
        for i in range(3):
            em[i] = np.median(result[:,i,:,:], axis=0)
                
        if em_or_fm == 'em':
            ca.writing_nc(em, "spat_em_{}_{}_{}.nc".format(var, exer,jz), var, rlats, rlons,em=True)
        elif em_or_fm == 'fm':     
            ca.writing_nc(result, "spat_fm_{}_{}_{}.nc".format(var, exer, jz), var, rlats, rlons,em=False)
            
    elif ( opt == 'ts' ):    
        #< zeitreihen berechnen und als csv abspeichern
        
        #<index für zeitreihen anlegen
        if exer == 'day':
            index = pd.date_range('1971-01-01','2100-12-31',freq='D')
        elif exer == 'month':
            index = pd.date_range('1971-01','2100-12',freq='MS')
        else:
            index = pd.date_range('1971', '2100', freq='AS')
        
        result = pd.DataFrame()
        
        #< calculating time series for every model
        for i, ifile in enumerate(data):
            print("calculating for cm{}".format(i))
            foo = ca.extrem((ca.read_data(ifile,var)), opt, var, exer, jz)
            result["cm{}".format(i)] = pd.Series(foo,index)
        
        # eine Zeitreihe eines models    
        #foo1 = ca.extrem((ca.read_data(data[0],var)), opt, var, exer)
        #result["cm{}".format(0)] = pd.Series(foo1,index)

        # Ergebnisse abspeichern als csv. Namen um zu speichern
        names_ee = {'hp':'hitzeperiode.csv',\
                    'vp':'vegetationsphase.csv',\
                    'vp2':'vegetationsphase2.csv',\
                    'wp':'warmeperiode.csv',\
                    'ft':'frosttage.csv',\
                    'st':'sommertage_{}.csv'.format(jz),\
                    'ht':'hitzetage_{}.csv'.format(jz),\
                    'tt':'trockentage_{}.csv'.format(jz),\
                    'snt':'snt_{}.csv'.format(jz),\
                    'tp':'trockenperiode.csv',\
                    'sft': 'speatfrost.csv',\
                    'jm':'jahresmittel_{}.csv'.format(var),\
                    'djf':'winter_{}.csv'.format(var),\
                    'jja':'sommer_{}.csv'.format(var),\
                    'mam':'mam_{}_jm.csv'.format(var),\
                    'son':'son_{}_jm.csv'.format(var),\
                    'month':'month_{}_jm.csv'.format(var),\
                    'day':'daily_{}.csv'.format(var)}
        
        result.to_csv(names_ee[exer])
        print('result to csv: finished')
        
                    
