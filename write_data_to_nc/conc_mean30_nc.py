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
#   building differences to ref period
    mean = np.zeros((3,np.shape(data)[1],np.shape(data)[2]), 'f')
    for i in range(3):
        mean[i,:,:] = np.mean(data[(0+50*12*i):(30*12+50*12*i),:,:], axis=0)
    mean[2,:,:] = mean[2,:,:]-mean[0,:,:]   
    mean[1,:,:] = mean[1,:,:]-mean[0,:,:]   
    return mean
    

if __name__ == '__main__':
    
    in_file = sys.argv[1]
    out_file = sys.argv[2]
    var_in = sys.argv[3]
    
    #data_path = "/home/steffen/Masterarbeit/Daten/mon/tas/CNRM/cclm/"

    data = sorted(glob.glob(in_file + '*.nc'))
    
    f = Dataset(data[0], 'r')
    rlats=f.variables['rlat'][:]
    rlons=f.variables['rlon'][:]
    var = f.variables[var_in][:] #(time,lats,lons)
    data = data[1:]
    f.close()
    for name in data:
        
        f = Dataset(name, 'r')

        var_new = f.variables[var_in][:] #(time,lats,lons)
        var = np.concatenate((var,var_new),axis=0)

    #gp_mean = mean30(var)
       
#------ write to netcdf file ------------------------------
    fileobj = Dataset(out_file+'.nc', 'w')
    fileobj.createDimension('rlat', len(rlats))
    fileobj.createDimension('rlon', len(rlons))
    fileobj.createDimension('time', np.shape(var)[0])
    #fileobj.createDimension('gp_mean', np.shape(gp_mean)[0])
    
    lat_var = fileobj.createVariable('rlat', 'f', ('rlat',))
    lon_var = fileobj.createVariable('rlon', 'f', ('rlon',))
    var_var = fileobj.createVariable(var_in, 'f', ('time','rlat','rlon'))
    #mean_var = fileobj.createVariable('gp_mean', 'f', ('gp_mean','rlat','rlon'))
    
    lat_var[:] = rlats[:]
    lon_var[:] = rlons[:]
    var_var[:,:,:] = var[:,:,:]
    #mean_var[:,:,:] = gp_mean[:,:,:]
    fileobj.title = out_file
    print("...creating file was succesfull!")
    fileobj.close()

