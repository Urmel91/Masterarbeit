#!/usr/bin/python

# plotting spatial distribution of a variable like tas, pr, ...
# the variable is averaged over 30 years:
# 1971-2000 fm[0](reference period), 2021-2050 fm[50], 2071-2100 fm[100]
# possible to distinguish between winter, spring, summer, autumn, year 

# input: [1] var , e.g. tas, pr, tasmax,...
#        [2] period, 0 for ref period, 1 for 21-50, 2 for 71-00

from netCDF4 import Dataset
import numpy as np
import glob 
import matplotlib.pyplot as plt  
import sys
from matplotlib import colors
from mpl_toolkits.basemap import Basemap
import coord_trafo as ct
import numpy.ma as ma


def read_data(data,data_name):
    f = Dataset(data, 'r')
    #gp_mean[0,:,:] = gp_mean[0,:,:] - 273.15
    return(f.variables[data_name][:])

#----------------------------------------------------------------
#< year mean of monthly data. in every year the mean of the jz will
#< be calculated.
def year_mean_gp(data, jz):
    ym = np.zeros((130,31,34), 'f')

    if ( jz == "year" ):
        s = 0; e = 12
    if ( jz == "mam" ):
        s = 2; e = 5
    elif ( jz == "jja" ):
        s = 5; e = 8
    elif ( jz == "son" ):
        s = 8; e = 11
    elif (jz == "djf" ):
        s = 0; e = 2
        for j in range(130):
            start = (s+12*j) 
            end = (e+12*j)
            foo = np.concatenate((data[start:end,:,:],[data[start+11,:,:]]))
            ym[j,:,:] = np.mean(foo,axis=0)
        return(ym)
    
    for j in range(130):
        start = (s+12*j) 
        end = (e+12*j) 
        ym[j,:,:] = np.mean(data[start:end,:,:],axis=0)
    return(ym)    

def floating_mean(data, jz):
    data = year_mean_gp(data, jz)
    fm = np.zeros((101,31,34),'f')
    for j in range(101):
        fm[j,:,:] = np.mean(data[(0+j):(30+j),:,:],axis=0)
    fm[:,:,:] = fm[:,:,:] - fm[0,:,:] 
    fm = ct.niedersachsen(fm)
    return(fm)                    


#----- spatial distribution of daily data ------------------
#< fur jeden GP wird jahrliches mittel erzeugt aus daily data
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
    return(mean_gp)    

#----- spatial average of lower saxony of daily data ------------
def mean_day(var):
    md = np.array([[np.mean(var[j][i]) for i in range(len(var[j]))] for j in range(len(var))])
    return(md)

def schaltjahr(jahr):
    if jahr % 400 == 0:
        return True
    elif jahr % 100 == 0:
        return False
    elif jahr % 4 == 0:
        return True
    else:
        return False
    
#------- plotting spatial distribution ---------------------------
def plot_basemap(data, lons, lats):
    m = Basemap(projection ='merc',resolution='l', llcrnrlat=51.31250-0.125, llcrnrlon=6.68750-0.125, 
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
    m.pcolormesh(x, y, data)
    cbar = plt.colorbar(orientation='horizontal', shrink=0.625, aspect=20, fraction=0.2,pad=0.02)
    #cbar = m.colorbar(cs,location='bottom',pad="5%")
    #plt.show()

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
        start = abs(max(var[i])-min(var[i]))
        plt.bar(i, height=start, width=0.4, bottom=min(var[i]),color='lightblue')
        plt.plot([i-0.2,i+0.2],[np.median(var[i]),np.median(var[i])],'r')
    xmin,xmax = plt.xlim()    
    plt.plot([xmin,xmax],[0,0],color = 'grey',linestyle = '--')    
    #ax.set_ylim(-0.5,max(np.max(var,axis=1))+1)
    plt.ylim(-0.5,6)
    plt.xlim((xmin,xmax))
    plt.xticks(np.arange(5),names)


if __name__ == '__main__':
    
    time = sys.argv[1]
    var = sys.argv[2]
    jz = sys.argv[3]
    opt = sys.argv[4]

    data_path = "/home/steffen/Masterarbeit/Daten/"+time+"/"+var+"/"
    
    data = sorted(glob.glob(data_path+'*.nc'))
    
    f = Dataset(data[0], 'r')
    rlats=f.variables['rlat'][:]
    rlons=f.variables['rlon'][:]
    
    #----- calculate lons, lats in gographical coordinates ------
    lon_lat_r = np.meshgrid(rlons,rlats)
    lons, lats = ct.coord_traf(2, lon_lat_r[0], lon_lat_r[1])
    
    nied = [ct.niedersachsen(read_data(ifile, var)) for ifile in data]
    
    #----- ensemble data jahreszeiten mean every GP -----------------------
    #< erzeugt mir dic in dem fur jede jahreszeit uber alle ensembles 30 jahresmittel
    #< jedes GP stehen.
    jz_names = ["year","djf", "mam", "jja", "son"]
    gp_mean = {}
    gp_ensemble = {}
    for name in jz_names:  
        gp_ensemble[name] = [floating_mean(read_data(ifile,var),name) for ifile in data]
        gp_mean[name] = ct.niedersachsen(np.mean(gp_ensemble[name],axis=0))
        
    #-------ensemble data spatial floating mean ---------------------------
    #< jede jz hat liste mit spatial mean jedes modells for every time step
    fm_jz = {}
    for name in jz_names:
        fm = []
        for i in range(len(gp_ensemble[name])):
            fm.append([np.mean(gp_ensemble[name][i][j]) for j in range(len(gp_ensemble[name][i]))])
            
        fm_jz[name] = np.array(fm)
    
    #----- plotting spatial distribution ---------
    if ( opt == "spat" ):    
        plot_basemap(gp_mean["year"][50], lons, lats)
        plt.show()
    
    #----- Gebietsmittel 30 years berechnen ------------------------------- 
    elif ( opt == "ts" ):
        plot_ts(fm_jz[jz])
        
    #----- Bandbreiten berechnen ---------------------------------
    elif ( opt == "bb" ):
        jz_names = ["year", "djf", "mam", "jja", "son"]
        sig = []
        for i in range(1,3):
            sig.append([fm_jz[j][:,i*50] for j in jz_names])
        print(np.shape(sig))
        for i in range(1,3):
            plt.subplot(1,2,i)    
            plot_bandbreite(sig[i-1], jz_names)
        plt.savefig(var +"_"+ opt+".pdf")
        plt.show()
    
    '''
#---- plot in ein fenster   
    fig = plt.figure(1)

    for i in range(1,2):
        plt.subplot(2,1,i)    
        plot_basemap(gp_mean[jz][i-1], lons, lats)
    #savename = var + "_gp_mean_" + jz 
    #plt.savefig(savename+".pdf")

    plt.show()
    '''
