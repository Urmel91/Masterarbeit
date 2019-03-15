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
import pandas as pd
from scipy.stats import norm
from scipy import stats

#---------------------------------------------------------------------
#------------ reading data -------------------------------------------
#---------------------------------------------------------------------


def read_data(data,data_name):
    f = Dataset(data, 'r')
    v = f.variables[data_name][:]
    f.close()
    #gp_mean[0,:,:] = gp_mean[0,:,:] - 273.15
    return(v)


#---------------------------------------------------------------------
#------------ writing data -------------------------------------------
#---------------------------------------------------------------------

def writing_nc(data, outfile, var, rlat, rlon, em=True):
    #< em==True heißt, dass em gebildet wird
    
    fileobj = Dataset(outfile, 'w')
    fileobj.createDimension('rlat', len(rlat))
    fileobj.createDimension('rlon', len(rlon))
    if em:
        fileobj.createDimension('time', np.shape(data)[0])
        
        var_lat = fileobj.createVariable('rlat', 'f', ('rlat'))
        var_lon = fileobj.createVariable('rlon', 'f', ('rlon'))
        var_var = fileobj.createVariable(var, 'f', ('time','rlat','rlon'))
                
        var_var[:,:,:] = data[:,:,:]
    
    else:
        fileobj.createDimension('time', np.shape(data)[1])
        fileobj.createDimension('ensemble', np.shape(data)[0])

        var_lat = fileobj.createVariable('rlat', 'f', ('rlat'))
        var_lon = fileobj.createVariable('rlon', 'f', ('rlon'))        
        var_var = fileobj.createVariable(var, 'f', ('ensemble','time','rlat','rlon'))
        
        var_var[:,:,:,:] = data[:,:,:,:]

    var_lat[:] = rlat[:]
    var_lon[:] = rlon[:]
    
    fileobj.title = outfile
    print("...creating file was succesfull!")
    fileobj.close()

#---------------------------------------------------------------------
#------------ functions fur raumliche darstellung -------------------------------------------
#---------------------------------------------------------------------


#< weist tag index der daten zu -> moeglich daten per datum zu adressieren
def index_data(data, opt):
    if opt == 'day':
        index = pd.date_range('1971-01-01','2100-12-31',freq='D')
        number=np.arange(np.shape(data)[0])
        return pd.Series(number,index)
    elif opt == 'year':
        index = pd.date_range('1971','2100',freq='AS')
        number=np.arange(np.shape(data)[0])
        return pd.Series(number,index)
        
#< guckt, ob hv von daily data sich aendert und
#< in welche richtung klimasignal zeigt 
#< output: sig True wenn signal positiv und 1 wenn hv unterschiedlich
def robust(data, ave):
    if ave > 0:
        sig = True
    else:
        sig = False
    #index = index_data(data)
    ref_hv = data[:index['2001-01-01']]
    #hv1 = data[index['2021-01-01']:index['2051-01-01']] 
    hv2 = data[index['2071-01-01']:]
    st, p = stats.mannwhitneyu(ref_hv, hv2)
    alpha = 0.05
    if p < alpha:
        return 1, sig
    else:
        return 0, sig

def jz_index(jz, yr, i):
    if jz == 'year':
        return i['{}'.format(yr)]
    elif jz == 'djf':
        return i['{}-12'.format(yr):'{}-02'.format(yr+1)]
    elif jz == 'jja':
        return i['{}-06'.format(yr):'{}-08'.format(yr)]
    elif jz == 'son':
        return i['{}-09'.format(yr):'{}-11'.format(yr)]
    elif jz == 'mam':
        return i['{}-03'.format(yr):'{}-05'.format(yr)]

def countbigger(data, t):
    counter = np.zeros((np.shape(data)[1],np.shape(data)[2]),'f')
    for iday in range(len(data)):
        for lon in range(len(data[iday])):
            for lat in range(len(data[iday,lon])):
                if(data[iday, lon, lat] > t):
                    counter[lon, lat] = counter[lon, lat] + 1
    return counter                

def countsmaller(data, t):
    counter = np.zeros((np.shape(data)[1],np.shape(data)[2]),'f')    
    for iday in range(len(data)):
        for lon in range(len(data[iday])):
            for lat in range(len(data[iday,lon])):
                if(data[iday, lon, lat] < t):
                    counter[lon, lat] = counter[lon, lat] + 1
    return(counter)                

def extrem(data, o, v, ee, jz):
    fm = ma.array(np.zeros((3,np.shape(data)[1],np.shape(data)[2]),'f'))
    days_year = ma.array(np.zeros((130,np.shape(data)[1],np.shape(data)[2]), 'f'))
    vp = ma.array(np.zeros((3,130,np.shape(data)[1],np.shape(data)[2]), 'f'))
    month = ma.array(np.zeros((130*12,np.shape(data)[1],np.shape(data)[2]), 'f'))
    monjz = ma.array(np.zeros((130*3,np.shape(data)[1],np.shape(data)[2]), 'f'))    
    spatial_mean = np.zeros((130), 'f')    
    if ( v == 'tas' or v == 'tasmin' or v == 'tasmax'):
        data += (-273.15)
    elif ( v == 'pr' ):
        data = data*60*60*24 
    ind = index_data(data,'day')  
    
    # betrachte jedes jahr einzeln und rechne for this year extremereignisse aus
    for i, iyear in enumerate(np.arange(1971,2101)):
        print(iyear)
        index=jz_index(jz,iyear,ind)
        if ee == 'wp':
            days_year[i] = heatperiod(data[index,:,:], 25)
        elif ee == 'hp':
            days_year[i] = heatperiod(data[index,:,:], 30)
        elif ee == 'vp':   
            days_year[i] = vegetationsphase(data[index,:,:])
        elif ee == 'vp2':   
            days_year[i] = vegetationsphase2(data[index,:,:])
        elif ee == 'st':   
            days_year[i] = countbigger(data[index,:,:], 25)
        elif ee == 'ht':
            days_year[i] = countbigger(data[index,:,:], 30)
        elif ee == 'tt':   
            days_year[i] = countsmaller(data[index,:,:], 1)
        elif ee == 'snt':
            days_year[i] = countbigger(data[index,:,:], 20)
        elif ee == 'jm':
            days_year[i] = jahresmittel(data[index,:,:], v)
        elif ee == 'tp':
            days_year[i] = trockenperiode(data[ind['{}-04'.format(iyear):'{}-08'.format(iyear)],:,:])
        elif ee == 'ft':
            days_year[i] = frosttage(data[ind['{}-01'.format(iyear):'{}-03'.format(iyear)],:,:],
                                     data[ind['{}-08'.format(iyear):'{}-12'.format(iyear)],:,:])
        elif ee == 'sft':    
            days_year[i] = countsmaller(data[ind['{}-04'.format(iyear):'{}-07'.format(iyear)],:,:],0)
        elif ee == 'month':
            for mon in range(12):
                month[mon+(i*12)] = jahresmittel(data[ind['{}-{}'.format(iyear,mon+1)],:,:],v)
        '''
        elif ee == 'djf':
            days_year[i] = jahresmittel(data[ind['{}-12'.format(iyear):'{}-02'.format(iyear+1)],:,:],v)
        elif ee == 'jja':
            days_year[i] = jahresmittel(data[ind['{}-06'.format(iyear):'{}-08'.format(iyear)],:,:],v)
        elif ee == 'mam':
            days_year[i] = jahresmittel(data[ind['{}-03'.format(iyear):'{}-05'.format(iyear)],:,:],v)
        elif ee == 'son':
            days_year[i] = jahresmittel(data[ind['{}-09'.format(iyear):'{}-11'.format(iyear)],:,:],v)
        '''
            
    if o == 'ts':
        # Ausgabe Zeitreihe mit yearly Werten
        # hier region wahlen, die man betrachten will
        # kann auch zeitreihe mit taeglichen werten ausgeben
        if ee == 'day':
            return(np.mean(np.mean(ct.niedersachsen(data),axis=1),axis=1))
        elif ee == 'month':
            return(np.mean(np.mean(ct.niedersachsen(month),axis=1),axis=1))
        #elif ee == 'vp':
        #    spatial_mean = np.mean(np.mean(ct.niedersachsen(vp),axis=2),axis=2)
        #    return(spatial_mean)
        else:
            spatial_mean = np.mean(np.mean(ct.niedersachsen(days_year),axis=1),axis=1)
            return(spatial_mean)
    elif o == 'sp' or o == 'spatex':
        return ct.niedersachsen(days_year)
    elif o == 'spatday':
        return ct.niedersachsen(data)
    elif o == 'spat':
        # klimasignale ref, 21, 71    
        for j in range(3):
            fm[j,:,:] = np.mean(ct.niedersachsen(days_year[(0+j*50):(30+j*50),:,:]),axis=0)
        
        if v == 'tas' or ee == 'vp' or ee == 'vp2':
            fm[1,:,:] = fm[1,:,:] - fm[0,:,:]
            fm[2,:,:] = fm[2,:,:] - fm[0,:,:]
            #fm[0,:,:] = fm[0,:,:] - 273.15
            #fm = ct.niedersachsen(fm)
        else:
            #fm[0,:,:] = fm[0,:,:]/12
            fm[1,:,:] = (fm[1,:,:]/fm[0,:,:]-1)*100
            fm[2,:,:] = (fm[2,:,:]/fm[0,:,:]-1)*100
            #fm[0,:,:] = fm[1,:,:]/fm[0,:,:]-1)*100
        return(fm) 
    else:
        sys.exit('wrong option in extrem')


#< zählt anzahl tage, die grenzwert überschreiten innerhalb zeitraumes.
#< zb t=25, dann tage mit maxtemp größer 25 grade.
#< für starkniederschlagstage, sommertage
#< daran denken tmax statt tas zu nehmen
def countbigger(data, t):
    counter = np.zeros((np.shape(data)[1],np.shape(data)[2]),'f')
    for iday in range(len(data)):
        for lon in range(len(data[iday])):
            for lat in range(len(data[iday,lon])):
                if(data[iday, lon, lat] > t):
                    counter[lon, lat] = counter[lon, lat] + 1
    return counter                

#< zum Beispiel trockentage, also t=1 oder frosttage t=0
def countsmaller(data, t):
    counter = np.zeros((np.shape(data)[1],np.shape(data)[2]),'f')    
    for iday in range(len(data)):
        for lon in range(len(data[iday])):
            for lat in range(len(data[iday,lon])):
                if(data[iday, lon, lat] < t):
                    counter[lon, lat] = counter[lon, lat] + 1
    return(counter)                


# Max Anzahl Tage mit Tmax>25 oder größer 30. 
# Wenn Tmax>25 bei GP wird counter hochgesetzt, ansonsten wieder auf 0.
# Wenn counter > max Anzahl Tagen mit T>25 wird counter zu max_dauer
def heatperiod(data, t):
    counter = np.zeros(np.shape(data),'f')
    max_dauer = np.zeros((np.shape(data)[1],np.shape(data)[2]),'f')
    for iday in range(len(data)):
        for lon in range(len(data[iday])):
            for lat in range(len(data[iday,lon])):
                if(data[iday, lon, lat] > t):
                    
                    counter[iday, lon, lat] = counter[iday-1, lon, lat] + 1
                    if (counter[iday, lon, lat] > max_dauer[lon, lat]):
                        max_dauer[lon, lat] = counter[iday, lon, lat]
                        
                else:
                    if (counter[iday-1, lon, lat] > max_dauer[lon, lat]):
                        max_dauer[lon, lat] = counter[iday-1, lon, lat]
                    counter[iday, lon, lat] = 0

    return(max_dauer)                


# max anzahl tagen am stück mit pr<1mm zwischen April und Sep
def trockenperiode(data):
    counter = np.zeros(np.shape(data),'f')
    max_dauer = np.zeros((np.shape(data)[1],np.shape(data)[2]),'f')
    for iday in range(len(data)):
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
    
#< beginnt nachdem 6 tage in folge tas>5 grad. endet in zweiter 
#< jahreshälfte wenn 6 tage in folge tas<5 grad.
def vegetationsphase(data):
    start = np.zeros((np.shape(data)[1],np.shape(data)[2]))
    end = np.zeros((np.shape(data)[1],np.shape(data)[2]))
    counter_s = np.zeros(np.shape(data),'f')
    counter_e = np.zeros(np.shape(data),'f')
    #dauer = np.zeros((np.shape(data)[1],np.shape(data)[2]),'f')
    result = np.zeros((np.shape(data)[1],np.shape(data)[2]),'f')
    for iday in range(len(data)):
        for lon in range(len(data[iday])):
            for lat in range(len(data[iday,lon])):
                        
                if start[lon, lat] == 0.0 and data[iday, lon, lat] > 5.0:
                    
                    counter_s[iday,lon,lat] = counter_s[iday-1,lon,lat] + 1.0
                    
                    if counter_s[iday,lon,lat] == 6.0:
                        
                        start[lon, lat] = iday

                elif start[lon, lat] > 0.0 and data[iday, lon, lat] <= 5.0 and iday>200:
                    
                    counter_e[iday,lon,lat] = counter_e[iday-1,lon,lat] + 1
                    
                    if counter_e[iday,lon,lat] == 6 and end[lon,lat]==0.0:
                        
                        end[lon, lat] = iday
                        result[lon, lat] = end[lon,lat] - start[lon,lat]
                        
                if end[lon, lat] == 0 and iday == 364:
                    
                    end[lon, lat] = iday
                    result[lon, lat] = end[lon,lat] - start[lon,lat]
                        
    return result

#< start, wenn wärmesumme größer als 200 ist. alle positiven werte gezählt
#< im januar mit 0.5. februar mit 0.75 und ab märz mit 200
def vegetationsphase2(data):
    start = np.zeros((np.shape(data)[1],np.shape(data)[2]))
    end = np.zeros((np.shape(data)[1],np.shape(data)[2]))
    ws = np.zeros((np.shape(data)[1],np.shape(data)[2]),'f')
    counter_e = np.zeros(np.shape(data),'f')
    #dauer = np.zeros((np.shape(data)[1],np.shape(data)[2]),'f')
    result = np.zeros((np.shape(data)[1],np.shape(data)[2]),'f')
    for iday in range(len(data)):
        for lon in range(len(data[iday])):
            for lat in range(len(data[iday,lon])):
                
                if data[iday, lon, lat] > 0.0 and iday<150:
                    
                    if iday<31:
                        ws[lon, lat] = 0.5 * data[iday, lon, lat] + ws[lon, lat]
                    elif iday>30 and iday<58:
                        ws[lon, lat] = 0.75 * data[iday, lon, lat] + ws[lon, lat]
                    elif iday>57:
                        ws[lon, lat] = data[iday, lon, lat] + ws[lon, lat]
                        
                if ws[lon, lat] > 200 and start[lon, lat] == 0.0:
                    start[lon, lat] = iday
                    
                if start[lon, lat] > 0.0 and data[iday, lon, lat] <= 5.0 and iday>200:
                    
                    counter_e[iday,lon,lat] = counter_e[iday-1,lon,lat] + 1
                    
                    if counter_e[iday,lon,lat] == 6 and end[lon,lat]==0.0:
                        
                        end[lon, lat] = iday
                        result[lon, lat] = end[lon,lat] - start[lon,lat]
                        
                if end[lon, lat] == 0 and iday == 364:
                    
                    end[lon, lat] = iday
                    result[lon, lat] = end[lon,lat] - start[lon,lat]
    
    return result               
                    

# Tage bis April und ab august mit tmin<0
def frosttage(data1, data2):
    counter1 = countsmaller(data1, 0)
    counter2 = countsmaller(data2, 0)
    return(counter1 + counter2)

# in: data for one year -> nead only to take mean over complete year 
# for every lon and lat
def jahresmittel(data, v):
    jm = np.zeros((31,34), 'f')
    #for iday in range(len(data)):
    for lon in range(31):
        for lat in range(34):
            if ( v == 'tas' or v == 'tasmax' or v == 'tasmin' ):
                jm[lon, lat] = np.mean(data[:, lon, lat])
            elif (v == 'pr' ):
                jm[lon, lat] = np.sum(data[:, lon, lat])
    return(jm)


 

#---------------------------------------------------------------------
#------------ functions fur hist raumliche mittelung, zeitreihen -----
#---------------------------------------------------------------------
 
def read_his(data):
    fileobj = open(data, 'r')
    afile = fileobj.readlines()
    fileobj.close()
    output = np.ndarray((len(afile),3), 'object')
    for i in range(len(afile)): #-1 weil letzte zeit \n ist
        output[i][0] = int(afile[i][0:4]) #bis 28 um \n loszuwerden
        output[i][1] = int(afile[i][5:7]) #bis 28 um \n loszuwerden
        #output[i][2] = float(afile[i][75:79]) #Niedersachsen  
        output[i][2] = afile[i][74:79] #Niedersachsen
        output[i][2] = float(output[i][2].strip())
        
    his = np.zeros((len(output),3), 'object')

    for j in range(30):
        for i in range(12):
            his[i+j*12] = output[i*30+j] 
    out = mon_over_y_dwd(his)
        
    return(out)    

def read_his_new(data):
    fileobj = open(data, 'r')
    afile = fileobj.readlines()
    fileobj.close()
    output = np.ndarray((len(afile),1), 'object')
    for i in range(len(afile)): #-1 weil letzte zeit \n ist
        output[i] = int(afile[i][5:12]) #bis 28 um \n loszuwerden
    return output    

 
# spatial, monthly average: every month has average over full lower saxony
def mon_mean_his(data):
    mean = np.zeros((np.shape(data)[0],np.shape(data)[1]),'f')
    for j in range(len(mean)): 
        mean[j,:] = [np.mean(data[j][i]) for i in range(len(data[j]))]
    return(mean)    

# es werden monatlich gemittelte daten aus normalen daten gemacht. Also Daten liegen fur jedes Jahr monatlich vor.
# fur januar jeden jahres gemittelt usw
def mon_over_y_dwd(data):
    mean = np.zeros((12), 'object')
    k = 0
    for i in range(12):
        counter = 0
        for j in range(int(len(data)/12)):
            mean[i] = mean[i] + data[j*12+k,2]
            counter = counter + 1
        mean[i] = mean[i]/counter 
        #mean[i,0] = i+1
        k = k + 1
    return mean

def mon_over_y(data):
    mean = np.zeros((12), 'f')
    k = 0
    for i in range(12):
        counter = 0
        for j in range(30):
            mean[i] = mean[i] + data[j*12+k]
            counter = counter + 1
        mean[i] = mean[i]/counter 
        #mean[i,0] = i+1
        k = k + 1
    return mean


