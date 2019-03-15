from netCDF4 import Dataset
import numpy as np
import glob 
import matplotlib.pyplot as plt  
import sys
import coord_trafo as ct
import numpy.ma as ma
import time
from matplotlib import colors
from mpl_toolkits.basemap import Basemap
import matplotlib.dates as mdates

#---------------------------------------------------------------------
#------------ reading data -------------------------------------------
#---------------------------------------------------------------------

def read_data(data,data_name):
    f = Dataset(data, 'r')
    v = f.variables[data_name][:]
    f.close()
    #gp_mean[0,:,:] = gp_mean[0,:,:] - 273.15
    return(v)

def readdata(path, var, ensemble):
    datanames = sorted(glob.glob(path+'*.nc'))
    f = Dataset(datanames[0], 'r')
    v = f.variables[var][:]
    rlats=f.variables['rlat'][:]
    rlons=f.variables['rlon'][:]    
    f.close()
    
    lon_lat_r = np.meshgrid(rlons,rlats)
    lons, lats = ct.coord_traf(2, lon_lat_r[0], lon_lat_r[1])
    
    if ensemble:
        index = np.concatenate([np.shape(datanames),np.shape(v)],axis=0)
        data = np.zeros(index,'f')

        for i, d in enumerate(datanames):
            f = Dataset(d, 'r')
            data[i,:,:,:] = f.variables[var][:]
            f.close()
            
        return(data, lons, lats, rlons, rlats)
    
    return(v, lons, lats, rlons, rlats)

def toYears(data):
    #in data(9,Anzahl Tage 1971-2100,31,34)
    #out: data(Anzahl Jahre)
    data_year = []
    end = 0
    years = np.arange(1971,2101)
    day_month = np.array([31,28,31,30,31,30,31,31,30,31,30,31])
    for i, iyear in enumerate(years):
        if ( schaltjahr(iyear) ):
            day_month[1] = 29
        else:
            day_month[1] = 28
        start=end    
        end = np.sum(day_month) + end
        data_year[i] = data[:,start:end,:,:] 
    return(data_year)

#---------------------------------------------------------------------
#------------ writing data -------------------------------------------
#---------------------------------------------------------------------

def writing_nc(data, outfile, var, rlat, rlon):
    fileobj = Dataset(outfile, 'w')
    fileobj.createDimension('rlat', len(rlat))
    fileobj.createDimension('rlon', len(rlon))
    fileobj.createDimension('time', np.shape(data)[0])
    #fileobj.createDimension('ensemble', np.shape(data)[0])
    
    var_lat = fileobj.createVariable('rlat', 'f', ('rlat'))
    var_lon = fileobj.createVariable('rlon', 'f', ('rlon'))
    var_var = fileobj.createVariable(var, 'f', ('time','rlat','rlon'))
            
    var_var[:,:,:] = data[:,:,:]
    var_lat[:] = rlat[:]
    var_lon[:] = rlon[:]
    
    fileobj.title = outfile
    print("...creating file was succesfull!")
    fileobj.close()

#---------------------------------------------------------------------
#------------ functions fur raumliche darstellung -------------------------------------------
#---------------------------------------------------------------------

class ExtremErg(object):
    
    def __init__(self, data, var):
        self.var = var
        if ( var == 'tas' or var == 'tasmin' or var == 'tasmax'):
            self.data = data - 273.15
        elif ( var == 'pr' ):
            self.data = data*60*60*24 
    
    def jahresmittel(self, data):
        jm = np.zeros((31,34), 'f')
        #for iday in range(len(data)):
        
        for lon in range(31):
            for lat in range(34):
                if ( self.var == 'tas' or self.var == 'tasmax' or self.var == 'tasmin' ):
                    jm[lon, lat] = np.mean(data[:, lon, lat])
                elif (self.var == 'pr' ):
                    jm[lon, lat] = np.sum(data[:, lon, lat])
        return(jm)
    
    '''
    # Max Anzahl Tage mit Tmax>25. 
    # Wenn Tmax>25 bei GP wird counter hochgesetzt, ansonsten wieder auf 0.
    # Wenn counter > max Anzahl Tagen mit T>25 wird counter zu max_dauer
    def heatperiod(self):
        counter = np.zeros(np.shape(self.data),'f')
        max_dauer = np.zeros((np.shape(self.data)[1],np.shape(self.data)[2]),'f')
        for iday in range(len(self.data)):
            for lon in range(len(self.data[iday])):
                for lat in range(len(self.data[iday,lon])):
                    if(self.data[iday, lon, lat] > 25):
                        
                        counter[iday, lon, lat] = counter[iday-1, lon, lat] + 1
                        if (counter[iday, lon, lat] > max_dauer[lon, lat]):
                            max_dauer[lon, lat] = counter[iday, lon, lat]
                            
                    else:
                        if (counter[iday-1, lon, lat] > max_dauer[lon, lat]):
                            max_dauer[lon, lat] = counter[iday-1, lon, lat]
                        counter[iday, lon, lat] = 0

        return(max_dauer)                
    
    # max anzahl tagen mit pr<1mm zwischen April und Sep
    def trockenperiode(data, apr, sep):
        counter = np.zeros(np.shape(data),'f')
        max_dauer = np.zeros((np.shape(data)[1],np.shape(data)[2]),'f')
        for iday in range(len(data)):
            if( iday > apr and iday < sep ):
                for lon in range(len(data[iday])):
                    for lat in range(len(data[iday,lon])):
                    
                        if(data[iday, lon, lat] < 1):
                        
                            counter[iday,lon,lat] = counter[iday-1,lon,lat] + 1
                            if (counter[iday,lon,lat] > max_dauer[lon,lat]):
                                max_dauer[lon,lat] = counter[iday,lon,lat]
                            
                        else:
                            if (counter[iday-1,lon,lat] > max_dauer[lon,lat]):
                                max_dauer[lon,lat] = counter[iday-1,lon,lat]
                            counter[iday,lon,lat] = 0
                                    
        return(max_dauer)                
       
        
    def vegetationsphase(data):
        start = False
        counter_s = np.zeros(np.shape(data),'i')
        counter_e = np.zeros(np.shape(data),'i')
        dauer = np.zeros((np.shape(data)[1],np.shape(data)[2]),'i')
        for iday in range(len(data)):
            for lon in range(len(data[iday])):
                for lat in range(len(data[iday,lon])):
                    if(data[iday, lon, lat] > 0):
                        counter_s[iday,lon,lat] = counter_s[iday-1,lon,lat] + 1
                        if (start == True):
                            dauer[lon, lat] = dauer[lon, lat] + 1
                        if ((counter_s[iday,lon,lat] > 5)):
                            start = True
                        
                    elif (data[iday, lon, lat] <= 0 and start == True):
                        counter_e[iday,lon,lat] = counter_e[iday-1,lon,lat] + 1
                        if (counter_e[iday,lon,lat] > 5):
                            start = False
                            dauer[lon,lat] = counter_s[iday,lon,lat]
                        else:
                            dauer[lon, lat] = dauer[lon, lat] + 1
                    #if ((counter_s[iday,lon,lat] > 5) or (start == True)):
                    #    dauer[lon,lat] = counter_s[iday,lon,lat]
        return(dauer)                

    # Tage bis April mit Tmin<0 grad
    def frosttage(data, apr):
        counter = np.zeros((np.shape(data)[1],np.shape(data)[2]),'f') 
        for iday in range(len(data)):
            if iday < apr:
                for lon in range(len(data[iday])):
                    for lat in range(len(data[iday,lon])):
                        if ( data[iday, lon, lat] < 0 ):
                            counter[lon, lat] = counter[lon, lat] + 1
        return(counter)

    # Tage ab April mit Tmin<0 grad
    def speatfrost(data, apr):
        counter = np.zeros((np.shape(data)[1],np.shape(data)[2]),'f') 
        for iday in range(len(data)):
            if iday >= apr:
                for lon in range(len(data[iday])):
                    for lat in range(len(data[iday,lon])):
                        if ( data[iday, lon, lat] < 0 ):
                            counter[lon, lat] = counter[lon, lat] + 1
        return(counter)
    '''
    # in: data for one year -> nead only to take mean over complete year 
    # for every lon and lat
    
    

class Data(ExtremErg):
        
    def __init__(self, data, var, ee_name):
        super().__init__(data, var)
        self.ee_name = ee_name
    
    def call_ee(self):
        ee = {#'hp': self.hitzeperiode,
            #'vp': self.vegetationsphase,
            #'ft': self.frosttage,
            #'tp': self.trockenperiode,
            #'sft': self.speatfrost,
            'jm': self.jahresmittel}

        return ee.get(self.ee_name)
    
    def calc(self):
        #fm = ma.array(np.zeros((3,np.shape(data)[1],np.shape(data)[2]),'f'))
        days_per_year = ma.array(np.zeros((130,np.shape(self.data)[1],np.shape(self.data)[2]), 'f'))
        #spatial_mean = np.zeros((130), 'f')  
        year = np.arange(1971,2101)
        day_month = np.array([31,28,31,30,31,30,31,31,30,31,30,31])
        end = 0
        # betrachte jedes jahr einzeln und rechne for this year extremereignisse aus
        for index, iyear in enumerate(year):
            if ( schaltjahr(iyear) ):
                day_month[1] = 29
            else:
                day_month[1] = 28
                
            start = end
            april = np.sum(day_month[0:3])
            sept = np.sum(day_month[0:8])
            end = np.sum(day_month) + end

            days_per_year[index] = self.call_ee()(self.data[start:end,:,:])
            print(index)
        return days_per_year
        

    '''   
    def toYears(data):
        #in data(9,Anzahl Tage 1971-2100,31,34)
        #out: data(Anzahl Jahre)
        data_year = {}
        end = 0
        years = np.arange(1971,2101)
        day_month = np.array([31,28,31,30,31,30,31,31,30,31,30,31])
        for i, iyear in enumerate(years):
            if ( schaltjahr(iyear) ):
                day_month[1] = 29
            else:
                day_month[1] = 28
            start=end    
            end = np.sum(day_month) + end
            data_year[str(iyear)] = data[:,start:end,:,:] 
        return(data_year)
    '''

    
def extrem(data, o, v, ee):
    fm = ma.array(np.zeros((3,np.shape(data)[1],np.shape(data)[2]),'f'))
    days_year = ma.array(np.zeros((130,np.shape(data)[1],np.shape(data)[2]), 'f'))
    year = np.arange(1971,2101)
    spatial_mean = np.zeros((130), 'f')    
    day_month = np.array([31,28,31,30,31,30,31,31,30,31,30,31])
    print(len(data))
    end = 0
    if ( v == 'tas' or v == 'tasmin' or v == 'tasmax'):
        data += (-273.15)
    elif ( v == 'pr' ):
        data = data*60*60*24 
    # betrachte jedes jahr einzeln und rechne for this year extremereignisse aus
    for index, iyear in enumerate(year):
        if ( schaltjahr(iyear) ):
            day_month[1] = 29
        else:
            day_month[1] = 28
            
        start = end
        april = np.sum(day_month[0:3])
        sept = np.sum(day_month[0:8])
        end = np.sum(day_month) + end
        if ee == 'hp':
            days_year[index] = heatperiod(data[start:end,:,:])
        elif ee == 'vp':   
            days_year[index] = vegetationsphase(data[start:end,:,:])
        elif ee == 'jm':
            days_year[index] = jahresmittel(data[start:end,:,:], v)
        elif ee == 'tp':
            days_year[index] = trockenperiode(data[start:end,:,:], april, sept)
        elif ee == 'ft':
            days_year[index] = frosttage(data[start:end,:,:], april)
        elif ee == 'sft':    
            days_year[index] = speatfrost(data[start:end,:,:], april)
        print(index)
        
    if o == 'ts':
        # Ausgabe Zeitreihe mit yearly Werten
        # hier region wahlen, die man betrachten will
        # kann auch zeitreihe mit taeglichen werten ausgeben
        if ee == 'day':
            return(np.mean(np.mean(ct.niedersachsen(data),axis=1),axis=1))
        else:
            spatial_mean = np.mean(np.mean(ct.niedersachsen(days_year),axis=1),axis=1)
            return(spatial_mean)
    elif o == 'spat':
        # klimasignale ref, 21, 71    
        for j in range(3):
            fm[j,:,:] = np.mean(ct.niedersachsen(days_year[(0+j*50):(30+j*50),:,:]),axis=0)
        
        if v == 'tas':
            fm[1,:,:] = fm[1,:,:] - fm[0,:,:]
            fm[2,:,:] = fm[2,:,:] - fm[0,:,:]
            #fm[0,:,:] = fm[0,:,:] - 273.15
            #fm = ct.niedersachsen(fm)
        elif v == 'pr':
            #fm[0,:,:] = fm[0,:,:]/12
            fm[1,:,:] = (fm[1,:,:]/fm[0,:,:]-1)*100
            fm[2,:,:] = (fm[2,:,:]/fm[0,:,:]-1)*100
            #fm[0,:,:] = fm[1,:,:]/fm[0,:,:]-1)*100
        return(fm) 
    else:
        sys.exit('wrong option in extrem')

def schaltjahr(jahr):
    if jahr % 400 == 0:
        return True
    elif jahr % 100 == 0:
        return False
    elif jahr % 4 == 0:
        return True
    else:
        return False

