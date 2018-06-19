import numpy as np
import numpy.ma as ma

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
'''
def niedersachsen(var):
    data = np.full(np.shape(var),True)
    for i in range(len(data)):
        for j in range(len(data[i])):
            data[i,2,18:20] = False
            data[i,3,18:23] = False
            data[i,4,18:25] = False
            data[i,5,17:25] = False
            data[i,6,17:25] = False
            data[i,7,17:25] = False
            data[i,8,16:28] = False
            data[i,9,16:28] = False
            data[i,10,9:13] = False
            data[i,10,16:28] = False
            data[i,11,16:28] = False
            data[i,11,10:13] = False
            data[i,12,10:13] = False
            data[i,12,14:28] = False
            data[i,12, 5:7] = False
            data[i,13,5:28] = False
            data[i,14,4:27] = False
            data[i,15,3:30] = False
            data[i,16,4:31] = False
            data[i,17,4:31] = False
            data[i,18,6:29] = False
            data[i,19,7:28] = False
            data[i,20,7:27] = False
            data[i,21,7:24] = False
            data[i,22,6:22] = False
            data[i,23,6:21] = False
            data[i,24,6:13] = False
            data[i,24,15:20] = False
            data[i,25,5:13] = False
            data[i,25,15:20] = False
            #data[i,26,5:14] = False
            #data[i,26,15:19] = False
    nied = ma.masked_array(data=var, mask=data, fill_value=0.0)
    return(nied)
'''
def niedersachsen(var):
    data = np.full((len(var),31,34),True)
    for i in range(len(data)): 
        data[i,2,18:20] = False
        data[i,3,18:23] = False
        data[i,4,18:25] = False
        data[i,5,17:25] = False
        data[i,6,17:25] = False
        data[i,7,17:25] = False
        data[i,8,16:28] = False
        data[i,9,16:28] = False
        data[i,10,9:13] = False
        data[i,10,16:28] = False
        data[i,11,16:28] = False
        data[i,11,10:13] = False
        data[i,12,10:13] = False
        data[i,12,14:28] = False
        data[i,12, 5:7] = False
        data[i,13,5:28] = False
        data[i,14,4:27] = False
        data[i,15,3:30] = False
        data[i,16,4:31] = False
        data[i,17,4:31] = False
        data[i,18,6:29] = False
        data[i,19,7:28] = False
        data[i,20,7:27] = False
        data[i,21,7:24] = False
        data[i,22,6:22] = False
        data[i,23,6:21] = False
        data[i,24,6:13] = False
        data[i,24,15:20] = False
        data[i,25,5:13] = False
        data[i,25,15:20] = False
        #data[i,26,5:14] = False
        #data[i,26,15:19] = False
    nied = ma.masked_array(data=var, mask=data, fill_value=0.0000)
    return(nied)
