import numpy as np


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
