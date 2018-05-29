#!/usr/bin/python3

from netCDF4 import Dataset
#from scipy.io import netcdf
import numpy as np
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

if __name__ == '__main__':
    
    lat_end_ind = 44
    lon_end_ind = 78
    
    f = Dataset('/home/steffen/Schreibtisch/Masterarbeit/'\
        'tasmax_EUR-11_CNRM-CERFACS-CNRM-CM5_historical_r1i1p1_CLMcom-CCLM4-8-17_v1_day_19710101-19751231.nc','r')

    rlats=f.variables['rlat'][:]
    rlons=f.variables['lat'][:]
    tasmax = f.variables['tasmax'][:]
    
#    lon_lat_r = np.meshgrid(rlons,rlats)
'''
    #------ Niedersachsen-Gitter ------------
#    lat_n = np.arange(51.31250,54.0625,0.0625)#nur noch 54 drin
    lat_n = np.arange(54.0,51.31250-0.0625,-0.0625)#nur noch 54 drin
    lon_n = np.arange(6.68750,11.5626,0.0625)#nur noch 11.5 drin
    lon_lat_n = np.meshgrid(lon_n,lat_n)
    
#    lat_lon = np.meshgrid()
    lon_lat_r = coord_traf(1,lon_lat_n[0],lon_lat_n[1])
    lon_lat_n = gp(lon_lat_n,lon_lat_r)
    print(lon_lat_n.rot[1][0,:])
'''    
'''
def in_niedersachsen(lat, lon):
    y = np.arange(lat_min, lat_max+step_lat, step_lat).round(6)
    x = np.arange(lon_min, lon_max+step_lon, step_lon).round(6)
    er = 0.00001
    in_n = False
    
    if (lat==(y[0]-er) and lat<=y[6]):
            if (lon <= 9.566667+er and lon >= 9.566667-er)\
            or (lon <= 9.683333+er and lon >= 9.683333-er):  
                in_n = True
    if (lat>=y[7] and lat<=y[14]):
            if (lon <= 9.566667+er and lon >= 9.566667-er)\
            or (lon <= 9.683333+er and lon >= 9.683333-er):  
                in_n = True
    if lat>=y[15] and lat<=y[21]:
            if (lon >= 9.566667 and lon <= 10.066667 ) :  
                in_n = True  
    if lat>=y[22] and lat<=y[29]:
            if (lon >= 9.566667 and lon <= 10.066667 ) :  
                in_n = True
    if lat>=y[30] and lat<=y[36]:
            if (lon >= 9.566667 and lon <= 10.566667 ) :  
                in_n = True
    if lat>=y[37] and lat<=y[44]:
            if(lon >= 9.566667 and lon <= 10.566667 ) :  
                in_n = True
    if lat>=y[45] and lat<=y[59]:
            if(lon >= 9.316666 and lon <= 10.566667 ) :  
                in_n = True
    if lat>=y[60] and lat<=y[74]:
            if(lon >= 9.316666 and lon <= 10.566667 ) :  
                in_n = True
    if lat>=y[75] and lat<=y[81]:
            if(lon >= 9.183333 and lon <= 10.816666 ) :  
                in_n = True
    if lat>=y[82] and lat<=y[89]:
            if(lon >= 9.183333 and lon <= 10.816666 ) :  
                in_n = True
    if lat>=y[90] and lat<=y[96]:
            if((lon>=7.816666 and lon<=8.316666)or(lon >= 9.066667 \
            and lon <= 10.933333)) :  
                in_n = True
    if lat>=y[97] and lat<=y[104]:
            if((lon>=7.816666 and lon<=8.316666)or(lon >= 9.066667 \
            and lon <= 10.933333)) :  
                in_n = True
    if lat>=y[105] and lat<=y[111]:
            if((lon>=7.816666 and lon<=8.566667)or(lon >= 8.933333 \
            and lon <= 11.066667)) :  
                in_n = True
    if lat>=y[112] and lat<=y[119]:
            if((lon>=7.816666 and lon<=8.566667)or(lon >= 8.933333 \
            and lon <= 11.066667)) :  
                in_n = True
    if lat>=y[120] and lat<=y[126]:
            if((lon>=7.816666 and lon<=11.066667) \
            or (lon>=6.816666 and lon<=7.316666)) :  
                in_n = True
    if lat>=y[127] and lat<=y[134]:
            if((lon>=7.816666 and lon<=11.066667) \
            or (lon>=6.816666 and lon<=7.316666)) :  
                in_n = True
    if lat>=y[135] and lat<=y[149]:
            if(lon>=6.816666 and lon<=10.933333) :  
                in_n = True
    if lat>=y[150] and lat<=y[164]:
            if(lon <= 10.933333 ) :  
                in_n = True
    if lat>=y[165] and lat<=y[179]:
            if(lon <= 10.816666) :  
                in_n = True
    if lat>=y[180] and lat<=y[194]:
            if(lon >= 6.816666 and lon <= 10.683333 ) :  
                in_n = True
    if lat>=y[195] and lat<=y[209]:
            if(lon >= 6.933333) :  
                in_n = True
    if lat>=y[210] and lat<=y[224]:
            if(lon >= 7.066667) :  
                in_n = True
    if lat>=y[225] and lat<=y[239]:
            if(lon >= 7.066667 and lon<=11.183333 ) :  
                in_n = True
    if lat>=y[240] and lat<=y[254]:
            if(lon >= 7.066667 and lon<=10.933333 ) :  
                in_n = True
    if lat>=y[255] and lat<=y[269]:
            if(lon >= 6.816666 and lon <= 10.816666) :  
                in_n = True
    if lat>=y[270] and lat<=y[284]:
            if(lon >= 6.816666 and lon <= 9.933333) :  
                in_n = True
    if lat>=y[285] and lat<=y[299]:
            if(lon >= 6.816666 and lon <= 9.433333) :  
                in_n = True
    if lat>=y[300] and lat<=y[314]:
            if((lon >= 6.933333 and lon<=8.066667) \
              or (lon >= 8.433333 and lon<=9.316666)) :  
                in_n = True
    if lat>=y[315] and lat<=(y[322]+1*er):
            if(lon >= 8.566667 and lon <= 9.183333) :  
                in_n = True
    
    return in_n
'''
