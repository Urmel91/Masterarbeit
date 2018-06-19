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
from matplotlib import colors
from mpl_toolkits.basemap import Basemap
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

#----- spatial average as year mean ---------
#< input: monthly data
#< do it for daily data also?
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

#----- spatial average of lower saxony of daily data ------------
def mean_day(var):
    md = np.array([[np.mean(var[j][i]) for i in range(len(var[j]))] for j in range(len(var))])
    return(md)
    
#----- spatial distribution of daily data ------------------
# < nur zur kontrolle
def mean_year_gp(data):
    mean_gp = np.zeros((130,np.shape(data)[1],np.shape(data)[2]), 'f')
    year = np.arange(1971,2101)
    day_month = np.array([31,28,31,30,31,30,31,31,30,31,30,31])
    end = 0
    for iyear in year:
        if ( schaltjahr(iyear) ):
            day_month[1] = 29
        else:
            day_month[1] = 28
        start = end
        end = sum(day_month) + end
        index = iyear - 1971
        mean_gp[index] = np.mean(data[start:end,:,:], axis = 0)
        '''
        for i in range(start, end):
            mean_gp[index]
        for days in day_month:
            days = start + days
            mean_mon[] = np.mean(data[start:days,:,:], axis=0)
            start = start+days
        '''
    return(mean_gp)    

def schaltjahr(jahr):
    if jahr % 400 == 0:
        return True
    elif jahr % 100 == 0:
        return False
    elif jahr % 4 == 0:
        return True
    else:
        return False


def plot_ts(var):
    fig, ax = plt.subplots()
    for i in range(len(var)):
        ax.plot(np.arange(15,116),var[i])
    plt.xticks(np.arange(0,131,10),np.arange(1971,2101,10))
    plt.grid()    
    plt.show()    

def plot_bandbreite(var, names):
    #fig, ax = plt.subplots()
    for i in range(len(var)):
        start = abs(max(var[i,:])-min(var[i,:]))
        plt.bar(i, height=start, width=0.4, bottom=min(var[i,:]),color='lightblue')
        plt.plot([i-0.2,i+0.2],[np.median(var[i,:]),np.median(var[i,:])],'r')
    xmin,xmax = plt.xlim()    
    plt.plot([xmin,xmax],[0,0],color = 'grey',linestyle = '--')    
    #ax.set_ylim(-0.5,max(np.max(var,axis=1))+1)
    plt.ylim(-0.5,6)
    plt.xlim((xmin,xmax))
    plt.xticks(np.arange(5),names)

def plot_basemap(data, lons, lats):
    m = Basemap(projection ='cyl',resolution='l', llcrnrlat=51.31250-0.125, llcrnrlon=6.68750-0.125, 
              urcrnrlat=54.0625 ,urcrnrlon=11.5626+0.125)
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
    #cs = m.contourf(x,y,data, np.arange(0, 5.0, .1), cmap=plt.cm.get_cmap('hot'),alpha=0.8)
    #cs = m.contourf(x,y,data, alpha=0.6)
    plt.pcolormesh(lons, lats, data)
    cbar = plt.colorbar(orientation='horizontal', shrink=0.625, aspect=20, fraction=0.2,pad=0.02)
    #cbar = m.colorbar(cs,location='bottom',pad="5%")
    #plt.show()


if __name__ == '__main__':
    
    time = sys.argv[1]
    var = sys.argv[2]
    opt = sys.argv[3]
    
    data_path = "/home/steffen/Masterarbeit/Daten/"+time+"/"+var+"/"
    
    data = sorted(glob.glob(data_path+'*.nc'))

    #----- rotierte lon und lat einlesen -------------------------
    f = Dataset(data[0], 'r')
    rlats=f.variables['rlat'][:]
    rlons=f.variables['rlon'][:]
        
    #----- calculate lons, lats in gographical coordinates ------
    lon_lat_r = np.meshgrid(rlons,rlats)
    lons, lats = ct.coord_traf(2, lon_lat_r[0], lon_lat_r[1])
    
    #----- Niedersachsen Data jedes Modells ----------------------
    nied = [ct.niedersachsen(read_data(ifile, var)) for ifile in data]
    
    #----- Gebietsmittel 30 years berechnen ------------------------------- 
    if ( opt == "ts" ):
        jz = sys.argv[4]
        #ym = year_mean(nied,jz)
        fm = floating_mean(nied, jz)
        plot_ts(fm)
    
    #----- Bandbreiten berechnen ---------------------------------
    elif ( opt == "bb" ):
        jz_names = ["year", "djf", "mam", "jja", "son"]
        sig = []
        for i in range(1,3):
            sig.append(np.array([floating_mean(nied, jz)[:,i*50] for jz in jz_names]))

        for i in range(1,3):
            plt.subplot(1,2,i)    
            plot_bandbreite(sig[i-1], jz_names)
        plt.savefig(var +"_"+ opt+".pdf")
        plt.show()
    
    else:
    #----- plotting spatial distribution ---------
        plot_basemap(nied[0][0], lons, lats)
        plt.show()
    


