#!/usr/bin/python3

#!/usr/bin/python

from netCDF4 import Dataset
import numpy as np
import glob 
import matplotlib.pyplot as plt  
import sys
import numpy.ma as ma
from matplotlib import colors
from mpl_toolkits.basemap import Basemap

'''
class GP(object):
    def __init__(self, lat, lon, lat_rot, lon_rot, n):
        self.lat = lat
        self.lon = lon
        self.lat_rot = lat_rot
        self.lon_rot = lon_rot
        self.n = n

class gp(object):
    def __init__(self, unrot, rot):
        self.unrot = unrot
        self.rot = rot

def coord_trafo(k, lat, lon):
    lat_rad = lat*np.pi/180.0
    lon_rad = lon*np.pi/180.0
    theta = 50.75*np.pi/180.0
    phi = 18.0*np.pi/180.0
    x = np.cos(lon_rad)*np.cos(lat_rad)
    y = np.sin(lon_rad)*np.cos(lat_rad)
    z = np.sin(lat_rad)
    if(k == 1): #geo zu rot
        x_new = np.cos(theta)*np.cos(phi) * x + np.sin(phi)*np.cos(theta)*y + np.sin(theta)*z
        y_new = -np.sin(phi) * x + np.cos(phi) * y
        z_new = -np.cos(phi) * np.sin(theta) * x - np.sin(phi)*np.sin(theta)*y + np.cos(theta)* z
        lat_new = np.arcsin(z_new)
        lon_new = np.arctan2(y_new, x_new)
        lat_out = lat_new*180.0/np.pi
        lon_out = lon_new*180.0/np.pi
    elif(k == 2): #rot zu geo
        theta = -theta
        phi = -phi
        x_new = np.cos(theta)*np.cos(phi) * x + np.sin(phi)*y + np.sin(theta) * np.cos(phi)*z
        y_new = -np.cos(theta) * np.sin(phi) * x + np.cos(phi)*y - np.sin(theta)*np.sin(phi) * z
        z_new = -np.sin(theta) * x + np.cos(theta) * z
        lat_new = np.arcsin(z_new)
        lon_new = np.arctan2(y_new, x_new)
        lat_out = lat_new*180.0/np.pi
        lon_out = lon_new*180.0/np.pi
    else: 
        print("falsches k!")
    return(lon_out, lat_out)    
'''
def coord_traf(k, lon, lat):
    lon_out = lon
    lat_out = lat
    for i in range(len(lat[:,0])):
        for j in range(len(lon[0,:])):
            
            lat_rad = lat[i,j]*np.pi/180.0
            lon_rad = lon[i,j]*np.pi/180.0
            theta = 50.75*np.pi/180.0
            phi = 18.0*np.pi/180.0
            x = np.cos(lon_rad)*np.cos(lat_rad)
            y = np.sin(lon_rad)*np.cos(lat_rad)
            z = np.sin(lat_rad)
            if(k == 1): #geo zu rot
                x_new = np.cos(theta)*np.cos(phi) * x + np.sin(phi)*np.cos(theta)*y + np.sin(theta)*z
                y_new = -np.sin(phi) * x + np.cos(phi) * y
                z_new = -np.cos(phi) * np.sin(theta) * x - np.sin(phi)*np.sin(theta)*y + np.cos(theta)* z
                lat_new = np.arcsin(z_new)
                lon_new = np.arctan2(y_new, x_new)
                lat_out[i,j] = lat_new*180.0/np.pi
                lon_out[i,j] = lon_new*180.0/np.pi
            elif(k == 2): #rot zu geo
                theta = -theta
                phi = -phi
                x_new = np.cos(theta)*np.cos(phi) * x + np.sin(phi)*y + np.sin(theta) * np.cos(phi)*z
                y_new = -np.cos(theta) * np.sin(phi) * x + np.cos(phi)*y - np.sin(theta)*np.sin(phi) * z
                z_new = -np.sin(theta) * x + np.cos(theta) * z
                lat_new = np.arcsin(z_new)
                lon_new = np.arctan2(y_new, x_new)
                lat_out[i,j] = lat_new*180.0/np.pi
                lon_out[i,j] = lon_new*180.0/np.pi
            else: 
                print("falsches k!")
    return(lon_out, lat_out)    

def max_min(lon_lat, mi_ma):
    #print(lon_lat)
    if (mi_ma == 'max'):
        m = max(lon_lat[0,:]) # max erste zeile
        for line in lon_lat:
            if (m < max(line)):
                m = max(line)
    elif (mi_ma == 'min'):
        m = min(lon_lat[0,:]) # max erste zeile
        for line in lon_lat:
            if (m > min(line)):
                m = min(line)
    return(m)

if __name__ == '__main__':
    
    pa = sys.argv[1]
          
    f = Dataset(pa, 'r')
#    f = Dataset('/home/steffen/Masterarbeit/'\
#        'Daten/mon/tas/CNRM/cclm/tas_EUR-11_CNRM-CERFACS-CNRM-CM5_historical_r1i1p1_CLMcom-CCLM4-8-17_v1_mon_197101-198012.nc','r')
#    f = Dataset('/home/steffen/Masterarbeit/Daten/mon/tas/CNRM/cclm/new.nc', 'r')
    rlats=f.variables['rlat'][:]
    rlons=f.variables['rlon'][:]
    tas = f.variables['tas'][:] #(time,lats,lons)
    
    lon_lat_r = np.meshgrid(rlons,rlats)

#------ Niedersachsen-Gitter ------------
    lat_n = np.arange(54.0+0.0625,51.31250-0.125,-0.0625)#nur noch 54 drin
    lon_n = np.arange(6.68750-0.125*2,11.5626+0.125,0.0625)#nur noch 11.5 drin
    lon_lat_n = np.meshgrid(lon_n,lat_n)
    
    lon_lat_n_rot = coord_traf(1,lon_lat_n[0],lon_lat_n[1])

    min_lon_n = max_min(lon_lat_n_rot[0],'min')
    max_lon_n = max_min(lon_lat_n_rot[0],'max')
    min_lat_n = max_min(lon_lat_n_rot[1],'min')
    max_lat_n = max_min(lon_lat_n_rot[1],'max')
    
    lat_min_ind = np.where(rlats > min_lat_n)[0][0]-1
    lat_max_ind = np.where(rlats > max_lat_n)[0][0]+1
    lon_min_ind = np.where(rlons > min_lon_n)[0][0]-1
    lon_max_ind = np.where(rlons > max_lon_n)[0][0]+1
    
    lats = rlats[lat_min_ind:lat_max_ind]
    lons = rlons[lon_min_ind:lon_max_ind]
    lons_lats = np.meshgrid(lons,lats)
    
    lon_geo, lat_geo = coord_traf(2, lons_lats[0], lons_lats[1])
    
    tas_n = tas[:,lat_min_ind:lat_max_ind,lon_min_ind:lon_max_ind]
        

#------ write to netcdf file ------------------------------
    fileobj = Dataset(pa, 'w')
    fileobj.createDimension('rlat', len(lats))
    fileobj.createDimension('rlon', len(lons))
    fileobj.createDimension('time', 120)
    
    lat_var = fileobj.createVariable('rlat', 'f', ('rlat',))
    lon_var = fileobj.createVariable('rlon', 'f', ('rlon',))
    tas_var = fileobj.createVariable('tas', 'f', ('time','rlat','rlon'))
    
    lat_var[:] = lats[:]
    lon_var[:] = lons[:]
    tas_var[:,:,:] = tas_n[:,:,:]
    fileobj.title = "New netCDF file"
    print("...creating file was succesfull!")
    fileobj.close()
    
    
    
    
