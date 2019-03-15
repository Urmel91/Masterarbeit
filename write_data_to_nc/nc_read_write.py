#!/usr/bin/python3

'''
----------------------------------------------------
< verkleinert das Gebiet Europa und schneidet ein Viereck 
< um Niedersachsen aus.  

input: [1] File, das eingelesen wird
       [2] Name des Output-Files
       [3] Variable, die eingelesen werden soll
'''

from netCDF4 import Dataset
import numpy as np
import glob 
import matplotlib.pyplot as plt  
import sys
import numpy.ma as ma
import coord_trafo as ct


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
    
    infile = sys.argv[1]
    outfile = sys.argv[2]
    varin = sys.argv[3]
          
    f = Dataset(infile, 'r')
    rlats=f.variables['rlat'][:]
    rlons=f.variables['rlon'][:]
    var = f.variables[varin][:] #(time,lats,lons)
        
    lon_lat_r = np.meshgrid(rlons,rlats)

#------ Niedersachsen-Gitter ------------
    lat_n = np.arange(54.0+0.0625,51.31250-0.125,-0.0625)#nur noch 54 drin
    lon_n = np.arange(6.68750-0.125*2,11.5626+0.125,0.0625)#nur noch 11.5 drin
    lon_lat_n = np.meshgrid(lon_n,lat_n)
    
    lon_lat_n_rot = ct.coord_traf(1,lon_lat_n[0],lon_lat_n[1])

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
    
    lon_geo, lat_geo = ct.coord_traf(2, lons_lats[0], lons_lats[1])
    
    var_n = var[:,lat_min_ind:lat_max_ind,lon_min_ind:lon_max_ind]
   
    f.close()
#------ write to netcdf file ------------------------------
    #fileobj = Dataset('/home/steffen/Masterarbeit/Daten/daily/tasmax/MPI/cclm/new.nc', 'w')
    fileobj = Dataset(outfile, 'w')
    fileobj.createDimension('rlat', len(lats))
    fileobj.createDimension('rlon', len(lons))
    fileobj.createDimension('time', np.shape(var)[0])
    
    lat_var = fileobj.createVariable('rlat', 'f', ('rlat',))
    lon_var = fileobj.createVariable('rlon', 'f', ('rlon',))
    var_var = fileobj.createVariable(varin, 'f', ('time','rlat','rlon'))
    
    lat_var[:] = lats[:]
    lon_var[:] = lons[:]
    var_var[:,:,:] = var_n[:,:,:]
    fileobj.title = outfile
    print("...creating file was succesfull!")
    fileobj.close()
    
    
    
    
