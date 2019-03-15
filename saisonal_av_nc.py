#!/usr/bin/python

'''
-----------------------------------------------
 < Liest Daten aller Modelle ein und kann Gebietsmittel
 < von Niedersachsen bilden (Monatsmittel, Jahresmottel,
 < 30 jaehriges Mittel). Kann Mittel auf ganzes Jahr 
 < oder auf Jahreszeiten beziehen (Winter, Sommer, ...).
 
 Input: [1] Variable (tas, pr,...)
        [2] Jahreszeit (year, djf, mam)
'''

from netCDF4 import Dataset
import numpy as np
import glob 
import matplotlib.pyplot as plt  
import sys
from matplotlib import colors
from mpl_toolkits.basemap import Basemap
import coord_trafo as ct
import mod_calculations as ca
import numpy.ma as ma

#< year mean of monthly data. in every year the mean of the jz will
#< be calculated for every gp.
def year_mean_gp(data, jz):
    ym = ma.array(np.zeros((130,31,34), 'f'))

    if ( jz == "year" ):
        s = 0; e = 12
    if ( jz == "mam" ):
        s = 2; e = 5
    elif ( jz == "jja" ):
        s = 5; e = 8
    elif ( jz == "son" ):
        s = 8; e = 11
    elif (jz == "djf" ):
        s = 0; e = 2
        for j in range(130):
            start = (s+12*j) 
            end = (e+12*j)
            foo = np.concatenate((data[start:end,:,:],[data[start+11,:,:]]))
            ym[j,:,:] = np.mean(foo,axis=0)
        return(ym)
    
    for j in range(130):
        start = (s+12*j) 
        end = (e+12*j) 
        ym[j,:,:] = np.mean(data[start:end,:,:],axis=0)
    return(ym)    

def floating_mean(data, jz, v):
    data = year_mean_gp(data, jz)
    fm = ma.array(np.zeros((101,31,34),'f'))
    for j in range(101):
        fm[j,:,:] = np.mean(data[(0+j):(30+j),:,:],axis=0)
    if v == 'tas':
        fm[:,:,:] = fm[:,:,:] - fm[0,:,:]
    elif v == 'pr':
        fm[:,:,:] = (fm[:,:,:]/fm[0,:,:]-1)*100
    #fm = ct.niedersachsen(fm)
    return(fm)                    


#----- spatial distribution of daily data ------------------
#< fur jeden GP wird jahrliches mittel erzeugt aus daily data
def mean_year_gp(data):
    mean_gp = np.zeros((130,np.shape(data)[1],np.shape(data)[2]), 'f')
    year = np.arange(1971,2101)
    day_month = np.array([31,28,31,30,31,30,31,31,30,31,30,31])
    end = 0
    for iyear in year:
        if ( schaltjahr(iyear) ):
            day_month[1] = 29
        else:
            day_month[1] = 28
        start = end
        end = sum(day_month) + end
        index = iyear - 1971
        mean_gp[index] = np.mean(data[start:end,:,:], axis = 0)
    mean_gp = ct.niedersachsen(mean_gp)    
    return(mean_gp)    

#----- spatial average of lower saxony of daily data ------------
def mean_day(var):
    md = np.array([[np.mean(var[j][i]) for i in range(len(var[j]))] for j in range(len(var))])
    return(md)

def schaltjahr(jahr):
    if jahr % 400 == 0:
        return True
    elif jahr % 100 == 0:
        return False
    elif jahr % 4 == 0:
        return True
    else:
        return False
    

#---------------------------------------------------------------------
#------------ functions fur raumliche mittelung, zeitreihen ----------
#---------------------------------------------------------------------

    
def mon_mean(var):
    mm = np.array([[np.mean(var[j][i]) for i in range(len(var[j]))] for j in range(len(var))])
    return(mm)

def floating_mean_ts(data, jz,v):
    data = year_mean(data, jz)
    fm = np.zeros((9,101),'f')
    for i in range(len(fm)):
        for j in range(101):
            fm[i,j] = np.mean(data[i,(0+j):(30+j)])
        #ausklammern wenn nicht saisonal_av_...
        #if v == 'tas':
        #    fm[i,:] = fm[i,:] - fm[i,0]
        #elif v == 'pr':
        #    fm[i,:] = (fm[i,:]/fm[i,0]-1)*100
    
    return(fm)                    


#----- spatial average as year mean ---------
#< input: monthly data
#< do it for daily data also?
def year_mean(data, jz):
    mm = mon_mean(data)
    ym = np.zeros((9,130), 'f')

    if ( jz == "year" ):
        s = 0; e = 12
    if ( jz == "mam" ):
        s = 2; e = 5
    elif ( jz == "jja" ):
        s = 5; e = 8
    elif ( jz == "son" ):
        s = 8; e = 11
    elif (jz == "djf" ):
        for i in range(len(ym)):
            s = 0; e = 2
            for j in range(130):
                start = (s+12*j) 
                end = (e+12*j)
                foo = np.concatenate((mm[i,start:end],[mm[i,start+11]]))
                ym[i,j] = np.mean(foo)
        return(ym)
    
    for i in range(len(ym)):
        for j in range(130):
            start = (s+12*j) 
            end = (e+12*j)
            ym[i,j] = np.mean(mm[i,start:end])
                    
    return(ym)        

#----- spatial average of lower saxony of daily data ------------
def mean_day(var):
    md = np.array([[np.mean(var[j][i]) for i in range(len(var[j]))] for j in range(len(var))])
    return(md)
    
#----- spatial distribution of daily data ------------------
# < nur zur kontrolle
def mean_year_gp(data):
    mean_gp = np.zeros((130,np.shape(data)[1],np.shape(data)[2]), 'f')
    year = np.arange(1971,2101)
    day_month = np.array([31,28,31,30,31,30,31,31,30,31,30,31])
    end = 0
    for iyear in year:
        if ( schaltjahr(iyear) ):
            day_month[1] = 29
        else:
            day_month[1] = 28
        start = end
        end = sum(day_month) + end
        index = iyear - 1971
        mean_gp[index] = np.mean(data[start:end,:,:], axis = 0)
        '''
        for i in range(start, end):
            mean_gp[index]
        for days in day_month:
            days = start + days
            mean_mon[] = np.mean(data[start:days,:,:], axis=0)
            start = start+days
        '''
    return(mean_gp)    

        

if __name__ == '__main__':
    
    time = sys.argv[1]
    var = sys.argv[2]
    opt = sys.argv[3]
    
    data_path = "/home/steffen/Masterarbeit/Daten/"+time+"/"+var+"/"
    
    data = sorted(glob.glob(data_path+'*.nc'))

    #----- rotierte lon und lat einlesen -------------------------
    f = Dataset(data[0], 'r')
    rlats=f.variables['rlat'][:]
    rlons=f.variables['rlon'][:]
        
    #----- calculate lons, lats in gographical coordinates ------
    lon_lat_r = np.meshgrid(rlons,rlats)
    lons, lats = ct.coord_traf(2, lon_lat_r[0], lon_lat_r[1])
    
    #----- Niedersachsen Data jedes Modells ----------------------
    #nied = [ct.niedersachsen(ca.read_data(ifile, var)) for ifile in data]
    
    nied = ma.array(np.zeros((9,1560,31,34),'f'))
    #nied = np.zeros((9,1560,31,34),'f')
    for i, ifile in enumerate(data):
        nied[i] = ct.niedersachsen(ca.read_data(ifile, var))

    #------ Datenaufbereitung --------------------------------------
    '''
    if (var == 'pr' ):
        day_month = np.array([31,28,31,30,31,30,31,31,30,31,30,31])
        for i in range(9):
            for j in range(1560):
                nied[i,j,:,:] =  nied[i,j,:,:] * day_month[j%12]*60*60*24
    '''            
    #----- Gebietsmittel 30 years berechnen ------------------------------- 
    if ( opt == "ts" ):
        jz = sys.argv[4]
        
        fm = ca.floating_mean_ts(nied, jz,var)
        ym = ca.year_mean(nied, jz)
        #---- Normieren auf Referenzzeitraum 1971-2000 (floating mean)---
        for i in range(len(ym)):
            if var == 'tas':
                ym[i,:] = ym[i,:] - fm[i,0]
                fm[i,:] = fm[i,:] - fm[i,0]
            elif var == 'pr':
                ym[i,:] = (ym[i,:]/fm[i,0]-1)*100
                fm[i,:] = (fm[i,:]/fm[i,0]-1)*100
        fm_e = np.mean(fm, axis=0)
        ca.plot_ts(fm, ym, fm_e, var, jz)
    
    #----- Bandbreiten berechnen ---------------------------------
    elif ( opt == "bb" ):
        #ausklammern von floating_mean_ts in mod_calculations
        jz_names = ["year", "djf", "mam", "jja", "son"]
        sig = []
        for i in range(1,3):
            sig.append(np.array([ca.floating_mean_ts(nied, jz, var)[:,i*50] for jz in jz_names]))
            
        zeit = ['2021-2050', '2071-2100']
        fig = plt.figure()
        fig.subplots_adjust(wspace=0.5)
        for i in range(1,3):
            ax = fig.add_subplot(1,2,i)
            ax.set_title('Klimaaenderungssignal {}'.format(zeit[i-1]), fontsize=10)
            if var == 'tas':
                ax.set_ylabel('$\Delta$ Temperatur [K]')

            elif var == 'pr':
                ax.set_ylabel('$\Delta$ Niederschlag [%]')
        
        plt.savefig(var +"_"+ opt+".pdf")
        plt.savefig(var +"_2071_"+ opt+".pdf")
        
        plt.show()
        '''
        for i in range(1,3):
            plt.subplot(1,2,i) 
            if var == 'tas':
                plt.ylabel('$\Delta$ Temperatur [K]')
                plt.set_title('hallo')
            elif var == 'pr':
                plt.ylabel('$\Delta$ Niederschlag [%]')

            ca.plot_bandbreite(sig[i-1], jz_names, var)
        plt.subplots_adjust(wspace=0.5)    
        plt.savefig(var +"_"+ opt+".pdf")
        plt.show()
        '''
    #----- plotting spatial distribution ---------
    elif ( opt == "spat" ):
        ca.plot_basemap(nied[0,1559,:,:], lons, lats, var, time)
    
    else:
        sys.exit()
       


