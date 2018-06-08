#!/usr/bin/python

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


def mean30(data):
#---30 years mean for every grid point in 
#   3 time areas:  71-00, 21-50, 71-00
    mean = np.zeros((3,31,34), 'f')
    for i in range(3):
        mean[i,:,:] = np.mean(data[(0+50*12*i):(30*12+50*12*i),:,:], axis=0)
    return mean

def plot_basemap(data):
    m = Basemap(projection ='cyl',resolution='l', llcrnrlat=51.31250-0.125, llcrnrlon=6.68750-0.125, 
              urcrnrlat=54.0625 ,urcrnrlon=11.5626+0.125)
    m.drawcoastlines()
    #m.drawcountries()
    m.drawmapboundary()

    m.readshapefile('/home/steffen/germany_map/gadm36_DEU_0','gadm36_DEU_0', drawbounds=True)
    m.readshapefile('/home/steffen/germany_map/gadm36_DEU_1','gadm36_DEU_1', drawbounds=True)
    #m.drawmeridians(np.arange(6.68750-0.125,11.5626+0.125,0.125))
    #m.drawparallels(np.arange(51.31250-0.125,54.0625,0.125))
    x,y = m(lons,lats)
    #m.scatter(x,y,alpha=0.5)
    #cs = m.contourf(x,y,data, np.arange(278.0, 286.0, .25), alpha=0.6)
    cs = m.contourf(x,y,data, alpha=0.6)
    cbar = m.colorbar(cs,location='bottom',pad="5%")
    
def read_gp_mean(data):
    f = Dataset(data, 'r')
    gp_mean = f.variables['gp_mean'][:]
    return gp_mean

if __name__ == '__main__':
    
    #data_path = sys.argv[1]
    data_path = "/home/steffen/Masterarbeit/Daten/mon/tas/"
    
    data = sorted(glob.glob(data_path+'*.nc'))
    
    f = Dataset(data[0], 'r')
    rlats=f.variables['rlat'][:]
    rlons=f.variables['rlon'][:]
    tas = f.variables['tas'][:] #(time,lats,lons)
    gp_mean = f.variables['gp_mean'][:] #(gp_mean,lats,lons)
    
    
    #----- ensemble data in one array ---------
    gp_mean_all = np.array([read_gp_mean(ifile) for ifile in data])
    gp_mean_all = np.mean(gp_mean_all[:,:,:,:],axis=0)
    
    
    #sys.exit()
    
    #for name in data:
        
    #    f = Dataset(name, 'r')
    #    var_new = f.variables[var_in][:] #(time,lats,lons)
        
    #    var = np.concatenate((var,var_new),axis=0)

        
    lon_lat_r = np.meshgrid(rlons,rlats)
    lons, lats = ct.coord_traf(2, lon_lat_r[0], lon_lat_r[1])
    lon_lat_geo = np.meshgrid(lons,lats)

    plot_basemap(gp_mean_all[0]-273.15)
    #plot_basemap(gp_mean[1])
    plt.show()

'''
#---- plot in ein fenster   
    fig = plt.figure(1)
    
    plt.subplot(3,1,1)    
    plot_basemap(gp_mean[0])
    
    plt.subplot(3,1,2)    
    plot_basemap(gp_mean[1])

    plt.subplot(3,1,3)    
    plot_basemap(gp_mean[2])
    
    plt.show()
'''    


