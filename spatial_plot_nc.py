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
    return(fm)                    


#---------------------------------------------------------------
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

def schaltjahr(jahr):
    if jahr % 400 == 0:
        return True
    elif jahr % 100 == 0:
        return False
    elif jahr % 4 == 0:
        return True
    else:
        return False

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

    
def read_data(data,data_name):
    f = Dataset(data, 'r')
    gp_mean = f.variables[data_name][:]
    #gp_mean[0,:,:] = gp_mean[0,:,:] - 273.15
    return gp_mean

if __name__ == '__main__':
    
    time = sys.argv[1]
    var = sys.argv[2]
    jz = sys.argv[3]
    #period = int(sys.argv[4])
    
    data_path = "/home/steffen/Masterarbeit/Daten/"+time+"/"+var+"/"
    
    data = sorted(glob.glob(data_path+'*.nc'))
    
    f = Dataset(data[0], 'r')
    rlats=f.variables['rlat'][:]
    rlons=f.variables['rlon'][:]
    #var = f.variables[var][:]
    
    #----- calculate lons, lats in gographical coordinates ------
    lon_lat_r = np.meshgrid(rlons,rlats)
    lons, lats = ct.coord_traf(2, lon_lat_r[0], lon_lat_r[1])
    
    nied = [ct.niedersachsen(read_data(ifile, var)) for ifile in data]
    
    #----- ensemble data jahreszeiten mean -----------------------
    #< erzeugt mir dic in dem fur jede jahreszeit uber alle ensembles 30 jahresmittel
    #< jedes GP stehen-
    jz_names = ["year","djf", "mam", "jja", "son"]
    gp_mean = {}
    
    for j in jz_names:  
        gp_mean_jz = np.array([floating_mean(read_data(ifile,var),j) for ifile in data])       
        gp_mean[j] = ct.niedersachsen(np.mean(gp_mean_jz, axis=0))
        
    #----- plotting spatial distribution ---------
    plot_basemap(gp_mean["year"][50], lons, lats)
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
'''
def mean30_gp(data,jz):
#---30 years mean for every grid point in 
#   3 time areas:  71-00, 21-50, 71-00
#   jz ist jahreszeit
#   50*12 um die perioden zu wechseln 
    jz_array = np.zeros((90,31,34), 'f')
    mean = np.zeros((3,31,34), 'f')
    
    if ( jz == "year" ):
        for i in range(3):
            mean[i,:,:] = np.mean(data[(0+50*12*i):(30*12+50*12*i),:,:], axis=0)
        mean[2,:,:] = mean[2,:,:]-mean[0,:,:]   
        mean[1,:,:] = mean[1,:,:]-mean[0,:,:]   
        return mean
    if ( jz == "mam" ):
        s = 2; e = 5
    elif ( jz == "jja" ):
        s = 5; e = 8
    elif ( jz == "son" ):
        s = 8; e = 11
    elif (jz == "djf" ):
        for i in range(3):
            start = 0 + 50*12*i
            end = 2 + 50*12*i
            jz_array[0:2,:,:] = data[start:end,:,:]
            s = 11; e = 14
            for j in range(30):
                start = (s+12*j) + 50*12*i
                end = (e+12*j) + 50*12*i
                jz_array[(0+3*j):(3+3*j),:,:] = data[start:end,:,:]
                if ( j == 29 ):
                    jz_array[(2+3*j),:,:] = data[start,:,:]
            mean[i,:,:] = np.mean(jz_array, axis=0)
        mean[2,:,:] = mean[2,:,:]-mean[0,:,:]   
        mean[1,:,:] = mean[1,:,:]-mean[0,:,:]   
        return mean    

    for i in range(3):
        for j in range(30):
            start = (s+12*j) + 50*12*i
            end = (e+12*j) + 50*12*i
            jz_array[(0+3*j):(3+3*j),:,:] = data[start:end,:,:]
        mean[i,:,:] = np.mean(jz_array, axis=0)
        
    mean[2,:,:] = mean[2,:,:]-mean[0,:,:]   
    mean[1,:,:] = mean[1,:,:]-mean[0,:,:] 
    return mean    
'''

