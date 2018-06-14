#!/usr/bin/python

'''
-----------------------------------------------
 < Liest Daten aller Modelle ein und kann Gebietsmittel
 < von Niedersachsen bilden (Monatsmittel, Jahresmottel,
 < 30 jaehriges Mittel). Kann Mittel auf ganzes Jahr 
 < oder auf Jahreszeiten beziehen (Winter, Sommer, ...).
 
 Input: [1] Variable (tas, pr,...)
        [2] Jahreszeit (year, djf, mam)
'''

from netCDF4 import Dataset
import numpy as np
import glob 
import matplotlib.pyplot as plt  
import sys
import numpy.ma as ma
from matplotlib import colors
from mpl_toolkits.basemap import Basemap
from scipy.interpolate import griddata
import coord_trafo as ct

        
def read_data(data,data_name):
    f = Dataset(data, 'r')
    data = f.variables[data_name][:]
    #data[0,:,:] = data[0,:,:] - 273.15
    return data

def mon_mean(var):
    mm = np.array([[np.mean(var[j][i]) for i in range(len(var[j]))] for j in range(len(var))])
    return(mm)
'''
def year_mean(data):
    mm = mon_mean(data)
    ym = np.zeros((10,130),'f')    
    for i in range(len(ym)):
        for j in range(len(ym[0])):
            ym[i,j] = np.mean(mm[i,(0+12*j):(12+12*j)])
    return(ym)
'''
def floating_mean(data, jz):
    data = year_mean(data, jz)
    fm = np.zeros((10,101),'f')
    for i in range(len(fm)):
        for j in range(101):
            fm[i,j] = np.mean(data[i,(0+j):(30+j)])
        fm[i,:] = fm[i,:] - fm[i,0]        
    return(fm)                    

def year_mean(data, jz):
    mm = mon_mean(data)
    ym = np.zeros((10,130), 'f')

    if ( jz == "year" ):
        s = 0; e = 12
    if ( jz == "mam" ):
        s = 2; e = 5
    elif ( jz == "jja" ):
        s = 5; e = 8
    elif ( jz == "son" ):
        s = 8; e = 11
    elif (jz == "djf" ):
        for i in range(len(ym)):
            s = 0; e = 2
            for j in range(130):
                start = (s+12*j) 
                end = (e+12*j)
                foo = np.concatenate((mm[i,start:end],[mm[i,start+11]]))
                ym[i,j] = np.mean(foo)
        return(ym)
    
    for i in range(len(ym)):
        for j in range(130):
            start = (s+12*j) 
            end = (e+12*j) 
            ym[i,j] = np.mean(mm[i,start:end])
    return(ym)    

def niedersachsen(var):
    data = np.full((len(var),31,34),True)
    for i in range(len(data)): 
        data[i,2,19] = False
        data[i,3,18:23] = False
        data[i,4,18:26] = False
        data[i,5,19:26] = False
        data[i,6,18:26] = False
        data[i,7,17:26] = False
        data[i,8,17:28] = False
        #data[9,10:14] = False
        data[i,9,16:28] = False
        data[i,10,10:14] = False
        data[i,10,16:28] = False
        data[i,11,16:28] = False
        data[i,11,10:14] = False
        #data[12,5:28] = False
        data[i,12,10:14] = False
        data[i,12,16:28] = False
        data[i,13,5:28] = False
        data[i,14,4:28] = False
        data[i,15,4:28] = False
        data[i,16,4:32] = False
        data[i,17,4:32] = False
        data[i,18,6:30] = False
        data[i,19,7:29] = False
        data[i,20,7:28] = False
        data[i,21,7:26] = False
        data[i,22,7:22] = False
        data[i,23,6:21] = False
        data[i,24,6:21] = False
        data[i,25,5:14] = False
        data[i,25,15:20] = False
        data[i,26,5:14] = False
        data[i,26,15:19] = False
    nied = ma.masked_array(data=var, mask=data, fill_value=0)
    return(nied)

def plot_basemap(data, lons, lats):
    m = Basemap(projection ='cyl',resolution='l', llcrnrlat=51.31250-0.125-1, llcrnrlon=6.68750-0.125-1, 
              urcrnrlat=54.0625+1 ,urcrnrlon=11.5626+0.125+1)
    m.drawcoastlines()
    #m.drawcountries()
    m.drawmapboundary()

    m.readshapefile('/home/steffen/germany_map/gadm36_DEU_0','gadm36_DEU_0', drawbounds=True)
    m.readshapefile('/home/steffen/germany_map/gadm36_DEU_1','gadm36_DEU_1', drawbounds=True)
    #m.drawmeridians(lons)
    #m.drawparallels(lats)    
    #m.drawmeridians(np.arange(6.68750-0.125,11.5626+0.125,0.125))
    #m.drawparallels(np.arange(51.31250-0.125,54.0625,0.125))
    x,y = m(lons,lats)
    #m.scatter(x,y,alpha=0.5)
    #cs = m.contourf(x,y,data, np.arange(278.0, 286.0, .25), alpha=0.6)
    cs = m.contourf(x,y,data, alpha=0.6)
    cbar = m.colorbar(cs,location='bottom',pad="5%")

def plot_ts(var):
    ax.plot(np.arange(101),var[0],'b')
    ax.plot(np.arange(101),var[1],'r')
    ax.plot(np.arange(101),var[2],'y')
    ax.plot(np.arange(101),var[3],'g')
    ax.plot(np.arange(101),var[4],'c')
    ax.plot(np.arange(101),var[5],'k')
    ax.plot(np.arange(101),var[6],'m')
    ax.plot(np.arange(101),var[7],'lightgreen')
    ax.plot(np.arange(101),var[8],'magenta')
    ax.plot(np.arange(101),var[9],'orange')    


if __name__ == '__main__':
    
    var = sys.argv[1]
    jz = sys.argv[2]
    
    data_path = "/home/steffen/Masterarbeit/Daten/mon/"+var+"/"
    
    data = sorted(glob.glob(data_path+'*.nc'))

    #----- rotierte lon und lat einlesen -------------------------
    f = Dataset(data[0], 'r')
    rlats=f.variables['rlat'][:]
    rlons=f.variables['rlon'][:]
        
    '''
    #----- ensemble data jahreszeiten mean -----------------------
    jz_names = ["djf", "mam", "jja", "son"]
    gp_mean = {}                    
    for jz in jz_names:  
        gp_mean_jz = np.array([jahreszeit(read_data(ifile,'tas'),jz) for ifile in data])       
        gp_mean[jz] = np.mean(gp_mean_jz, axis=0)
    '''    
    #----- calculate lons, lats in gographical coordinates ------
    lon_lat_r = np.meshgrid(rlons,rlats)
    lons, lats = ct.coord_traf(2, lon_lat_r[0], lon_lat_r[1])
    
    #----- Niedersachsen Data jedes Modells ----------------------
    nied = [niedersachsen(read_data(ifile, var)) for ifile in data]
    
    #----- Gebietsmittel berechnen -------------------------------    
    ym = year_mean(nied,jz)
    fm = floating_mean(nied, jz)
    
    
    #----- Plotten der Zeitreihen der Temperatur -----------------
    fig, ax = plt.subplots()
    plot_ts(fm)
    plt.show()
    

    #----- plotting spatial distribution ---------
    #plot_basemap(nied[0][0], lons, lats)
    #plt.show()
    


