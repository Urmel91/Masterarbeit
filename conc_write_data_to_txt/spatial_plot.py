#!/usr/bin/python

import numpy as np
import glob 
import matplotlib.pyplot as plt  
import sys
import numpy.ma as ma
from matplotlib import colors
from mpl_toolkits.basemap import Basemap
from scipy.interpolate import griddata

class GP(object):
    def __init__(self, lat, lon, val):
        self.lat = lat
        self.lon = lon
        self.val = val

def where(data, i):
    index = 0
    for line in data:
        if (line[0] > i):
            return index
        else: 
            index = index + 1

def readfiles(files):
    file2 = []
    for ifile in files:
        f = open(ifile, 'r')
        ifile = f.read().splitlines()
        f.close()
        #ifile = [line.split(' ') for line in ifile]
        for i in range(len(ifile)):
            ifile[i] = ifile[i].split(' ') #um auf einzelne daten zuzugreifen
            ifile[i] = [int(j) if j==ifile[i][0] else float(j) for j in ifile[i]]
        file2 = file2 + ifile    
    return np.array(file2,'object')    

def month_gp(data):
    d = data[0,0] #weil spater noch 1971 als ertses ist statt 1
    return where(data, d) #wo 2ter zeitschritt beginnt

def to_years_mon(data, y):
    gp_year = month_gp(data)*12
    for i in range(len(data)):
        n_year = int(i/(gp_year))
        mon = (i % gp_year)/(gp_year/12)
        data[i,0] = str(n_year + y) + "|" + str(mon+1)
    return data    

def to_years_day(data, y):
    day_month = [31,28,31,30,31,30,31,31,30,31,30,31]
    start_mon = 0
    end_mon = 0
    for year in N.arange(1971,2101):            
        if (schaltjahr(year)):
            day_month[1] = 29
            
        elif (not schaltjahr(year)):
            day_month[1] = 28
        
        for i in N.arange(0,12):
            gp_mon = 422*day_month[i]
            start_mon = end_mon
            end_mon = start_mon + gp_mon 
            print(end_mon)
            for k in range(start_mon, end_mon):
                data[k][0] = str(year) + '|' + str(i+1)
    return data    

def schaltjahr(jahr):
    if jahr % 400 == 0:
        return True
    elif jahr % 100 == 0:
        return False
    elif jahr % 4 == 0:
        return True
    else:
        return False

def mittel30(data):
    mean30 = data[0:422]
    bla = []
    for i in range(422):
        for j in range(1,30*12):
            mean30[i,3] = (mean30[i,3] + data[i+j*422,3])            
        mean30[i,3] = mean30[i,3]/(30*12)
    mean30[:,0] = data[0,0] + "-" + data[29*12*422,0]    
    return mean30       

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


if __name__ == '__main__':

#  data_path = "/home/vanselow/Masterarbeit/Masterarbeit/Originaldaten/mon/tas/CNRM/cclm/" 
  data_path = "/home/steffen/Masterarbeit/Originaldaten/mon/tas/CNRM/cclm/" 

  data = sorted(glob.glob(data_path + '*.txt'))
 
  data = readfiles(data)
  
  data = to_years_mon(data, 1971)
  
  data_30 = mittel30(data)

#  lat = np.arange(min(data[:,1]),max(data[:,1])+0.11,0.11)
#  lon = np.arange(min(data[:,2]),max(data[:,2])+0.11,0.11)
  lat = np.arange(min(data[:,1])-0.11,max(data[:,1])+0.11,0.11)
  lon = np.arange(min(data[:,2])-0.11,max(data[:,2])+0.11,0.11)
  
  #print((6.68750-0.125) + (83-1)*0.0625)
  lon_lat = np.meshgrid(lon,lat)
  #N.savetxt("mean_gp_30",data_30,fmt="%s %f %f %f")
  
  lon_geo, lat_geo = coord_traf(2, lon_lat[0], lon_lat[1])
  nied = np.zeros((len(lat),len(lon)),'f')
  #nied[:,:] = N.float(278.0)
  for line in data_30:
      ilat = line[1]+0.001
      ilon = line[2]+0.001
	  
      lat_ind = int((ilat-0.825000)/0.11)
      lon_ind = int((ilon+6.815000)/0.11)
      nied[lat_ind,lon_ind] = line[3]
  
  nied = ma.masked_less(nied, 270.0)  
  print(lon)
  '''
  m = Basemap(projection ='merc',resolution='l', llcrnrlat=51.31250-0.125, llcrnrlon=6.68750-0.125, 
              urcrnrlat=54.0625 ,urcrnrlon=11.5626+0.125)
  m.drawcoastlines()
  #m.drawcountries()
  m.fillcontinents(color='lightgrey',alpha=0.2)
  m.drawmapboundary()

  m.readshapefile('/home/steffen/germany_map/gadm36_DEU_0','gadm36_DEU_0', drawbounds=True)
  m.readshapefile('/home/steffen/germany_map/gadm36_DEU_1','gadm36_DEU_1', drawbounds=True)
  m.drawmeridians(np.arange(6.68750-0.125,11.5626+0.125,0.125))
  m.drawparallels(np.arange(51.31250-0.125,54.0625,0.125))
  x,y = m(lon_geo,lat_geo)
  #m.scatter(x,y,alpha=0.5)
  cs = m.contourf(x,y,nied, alpha=0.5)
  plt.show()


#--- contour plot 
  #con = plt.contourf(lon_geo,lat_geo,nied)
  #plt.scatter(lon_lat[0],lon_lat[1],s=0.5)
  #plt.grid(True)
  #plt.show()
  #print(lon_lat[1][0,:]) 
  '''
  
#--- grid plot   
'''
# create discrete colormap
cmap = colors.ListedColormap(['darkblue','blue','lightblue','mediumseagreen','g','yellowgreen','greenyellow','y','coral','red'])
bounds = [278,278.5,279,279.5,280,280.5,281,281.5,282,282.5]
norm = colors.BoundaryNorm(bounds, cmap.N)

fig, ax = plt.subplots()
ax.imshow(nied, cmap=cmap, norm=norm, origin='lower')
#ax.axis([min(lon),max(lon),min(lat),max(lat)])

# draw gridlines
#ax.grid(which='major', axis='both', linestyle='-', color='k', linewidth=2)
#ax.set_xticks(lon);
#ax.set_yticks(lat);
#ax.set_xlim(min(lon),max(lon))
#ax.set_ylim(min(lat),max(lat))
plt.show() 
'''
