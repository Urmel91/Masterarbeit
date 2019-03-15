#!/usr/bin/python3

'''
Calculating spatial distribution or timeseries of daily values like tas, pr, etc. 
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
import calc_functions as ca
#import pandas as pd
from scipy.stats import norm
import mod_calculations as cas
    

if __name__ == '__main__':
    
    var = sys.argv[1]
    opt = sys.argv[2]
    ee = sys.argv[3]

    data_path = "/home/steffen/Masterarbeit/Daten/daily/"+var+"/"
    data, lons, lats, rlons, rlats = ca.readdata(data_path, var, True)
    #data_year = ca.toYears(data)
    mod_count, time_count, lon_count, lat_count = np.shape(data)
    
    #bei spatial auch einfach Daten speichern in .nc datei
    if ( opt == "spat" ):
        '''
        result = ma.array(np.zeros((mod_count,3,lon_count,lat_count),'f'))
        for i in range(len(data)):
            result[i] = ca.extrem(data[i],opt,var,ee)
        em = ma.array(np.zeros((3,lon_count,lat_count),'f'))
        for i in range(3):
            em[i] = np.mean(result[:,i,:,:], axis=0)
        '''
        result = ma.array(np.zeros((mod_count,130,lon_count,lat_count),'f'))
        #result = ca.Data(data,var,ee).calc()
        for i in range(len(data)):
            result[i] = ca.Data(data[i],var,ee).calc()
        
        min_gp = 0
        max_gp = 15
        
        cas.plot_basemap(ct.niedersachsen(result[1,1,:,:]), lons, lats, min_gp, max_gp, var)
        
        #ca.plot_basemap(em[2], lons, lats, min_gp, max_gp, var)
            
        #ca.writing_nc(em, "spat_{}.nc".format(var), var, rlats, rlons)
            
    elif ( opt == 'ts' ):    
        # Zeitreihen Extremereignisse aller Modelle einlesen for every year, mean over niedersachsen
        if ee == 'day':
            index = pd.date_range('1971-01-01','2100-12-31',freq='D')
        else:
            index = pd.date_range('1971', '2100', freq='AS')

        result = pd.DataFrame()
          
        for i in range(len(data)):
            print("calculating for cm{}".format(i))
            foo = ca.extrem(data[i], opt, var, ee)
            result["cm{}".format(i)] = pd.Series(foo,index)
        
        # Ergebnisse abspeichern als csv. Namen um zu speichern
        names_ee = {'hp':'hitzeperiode.csv',\
                    'vp':'vegetationsphase.csv',\
                    'ft':'frosttage.csv',\
                    'tp':'trockenperiode.csv',\
                    'sft': 'speatfrost.csv',\
                    'jm':'jahresmittel_{}.csv'.format(var),\
                    'day':'daily_{}.csv'.format(var)}

        result.to_csv(names_ee[ee])
        
