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
#------------ plotting -----------------------------------------------
#---------------------------------------------------------------------


#------- plotting spatial distribution ---------------------------
def plot_basemap(data, lons, lats, mi, ma, v, abst, color, ax):
    m = Basemap(projection ='merc',resolution='l', llcrnrlat=51.31250-0.125, llcrnrlon=6.68750-0.125, 
              urcrnrlat=54.0625 ,urcrnrlon=11.5626+0.125, ax=ax)
    m.drawcoastlines()

    m.readshapefile('/home/steffen/germany_map/gadm36_DEU_0','gadm36_DEU_0', drawbounds=True)
    m.readshapefile('/home/steffen/germany_map/gadm36_DEU_1','gadm36_DEU_1', drawbounds=True)
    x,y = m(lons,lats)
    #cs = m.contourf(x,y,data, np.arange(0, 5.0, .1), cmap=plt.cm.get_cmap('hot'),alpha=0.8)
    #cs = m.contourf(x,y,data, alpha=0.6)
    cc = color
    '''
    if v == 'pr':
        cc = color#'Blues'
        abst = 5
        #plt.title('Niederschlagsaenderung [%] im 30-Jahresmittel (2071-2100)', fontsize=13)
        #plt.title('Raeumliche Niederschlagsverteilung [mm] im 30-Jahresmittel (1971-2000)', fontsize=13)
    
    elif v == 'tas' or v=='tasmax' or v=='tasmin':
        cc = color#'YlOrRd'#jet
        abst = 5
        #plt.title('Temperaturaenderung [K] im 30-Jahresmittel (2071-2100)', fontsize=13)
        #plt.title('Raeumliche Temperaturverteilung [$^\circ$C] im 30-Jahresmittel (1971-2000)', fontsize=13)
    '''
    cmap = plt.cm.get_cmap(cc, ((ma-mi)/abst))
    cmap.set_over(color='gray')
    #cmap.set_over(alpha=0.3)
    cmap.set_under(color='lightgray')
    #cmap.set_under(alpha=0.3)
    cm = m.pcolormesh(x, y, data, cmap=cmap, vmin=mi, vmax=ma)
    
    bounds = np.arange(mi, ma, abst)
    #cbar = m.colorbar(cm, orientation='horizontal', boundaries = bounds)#, shrink=0.625, aspect=20, fraction=0.2,pad=0.02, )
    cbar = m.colorbar(cm, location='right', boundaries = bounds)
    #plt.savefig(v +"_" + "spat_2086"+".pdf")
    #plt.grid()
    #plt.show()

def plot_signalbandbreite(extrem, ee_names, jahr,o):
    for i, iextrem in enumerate(ee_names.keys()):
        start = abs(max(extrem[iextrem])-min(extrem[iextrem]))
        plt.bar(i, height=start, width=0.4, bottom=min(extrem[iextrem]),color='lightblue')
        plt.plot([i-0.19,i+0.19],[np.median(extrem[iextrem]),np.median(extrem[iextrem])],'r')
        #plt.plot(np.arange(i-0.2,i+0.19,0.044), extrem[iextrem].values, 's', color='black', markersize=3)
        plt.plot(np.full((9),0+i), extrem[iextrem].values, '.', color='black', markersize=3)
    xmin,xmax = plt.xlim()    
    plt.plot([xmin,xmax],[0,0],color = 'grey',linestyle = '--')    
    plt.ylim(min(extrem.min())-5,max(extrem.max())+5)
    if o == 'ex':
        plt.ylabel('Aenderung bis {} bzgl. 1971-2000 [%]'.format(jahr))
        #plt.ylim(min(extrem.min())-5,max(extrem.max())+5)
        plt.ylim(-65, 100)
    elif o == 'tas':
        plt.ylim(-1,6)
        plt.ylabel('$\Delta$ Temperatur [K]')
    elif o == 'pr':
        plt.ylim(-30,40)
        plt.ylabel('$\Delta$ Niederschlag [%]')
    #plt.title('Klimaänderungssignale {}'.format(jahr), fontsize=10)
    plt.xticks(np.arange(3),ee_names.values(),rotation='45',ha='right')
    #plt.xtickslabels()
    #plt.show()


def plot_bandbreite(var, names, v):
    #fig, ax = plt.subplots()
    for i in range(len(var)):
        start = abs(max(var[i])-min(var[i]))
        plt.bar(i, height=start, width=0.4, bottom=min(var[i]),color='lightblue')
        plt.plot([i-0.2,i+0.2],[np.median(var[i]),np.median(var[i])],'r')
    xmin,xmax = plt.xlim()    
    plt.plot([xmin,xmax],[0,0],color = 'grey',linestyle = '--')    
    #ax.set_ylim(-0.5,max(np.max(var,axis=1))+1)
    if v == 'tas':
        plt.ylim(-0.5,6)
        plt.ylabel('$\Delta$ Temperatur [K]')
    elif v == 'pr':
        plt.ylim(-30,40)
        plt.ylabel('$\Delta$ Niederschlag [%]')
    plt.xlim((xmin,xmax))
    plt.xticks(np.arange(5),names)
    #plt.show()

def plot_kde(data1, label, color, ensemble = True):
    if ensemble:
        #sns.kdeplot(data1['cm2'], label='cm2')
        for icol in day.vals.columns.values:
            if icol != 'cm2':
                sns.kdeplot(data1[icol], label=icol, color=color)
        #sns.kdeplot(data2, label='ensemble', linewidth = 3, color = 'black')
        #sns.kdeplot(data3, label='1971-2000', shade=True)
        #sns.kdeplot(data4, label='2071-2100', shade=True)
   
    else:
        sns.kdeplot(data1, label=label, shade=True)
        #sns.kdeplot(data2, label='2071-2100', shade=True)

    plt.title('Verteilung der taeglichen Mitteltemperatur im ')
    #ymax = (max(hv0_w),max(hv2_w))/100
        
    #plt.plot([perc,perc],[ymin,ymax],color = 'grey',linestyle = '--') 
    #plt.xlim([-20,45])
    plt.xlabel('Temperatur [$^\circ$C]')
    plt.ylabel('Relative Haeufigkeitsdichte')
    #plt.savefig("tas_hv_winter_1971.pdf", dpi=96)

#def plot_ts(data, data_y, e, v, year):
def plot_ts(data, e, v, year):    
    fig, ax = plt.subplots(figsize=(11,5))
    #for i in range(len(data)):
    #    ax.plot(np.arange(130),data_y[i], linewidth=1, color = 'lightgray')
    for i in range(len(data)):
        ax.plot(np.arange(15,116),data[i], label="cm_{}".format(i))
    ax.plot(np.arange(15,116),e,linewidth=3.0, color='black', label="Ensemblemittel")
    lgd=ax.legend(bbox_to_anchor=(1, -0.35), loc='lower right', ncol=3)
    time = ['1971','','1991','','2011','','2031','','2051','','2071','','2091']
    if ( v == 'pr' ):
        ax.set_yticks(np.arange(-40,80,20))
        ax.set_ylabel('$\Delta$ Niederschlag [%]')
    elif ( v == 'tas' ):
        ax.set_yticks(np.arange(-3,7,1))
        ax.set_ylabel('$\Delta$ Temperatur [K]')

    plt.xticks(np.arange(0,131,10),time)
    plt.grid()
    #plt.savefig("ts_"+v+'_'+year+".pdf",bbox_extra_artists=(lgd,), bbox_inches='tight')    
    plt.show()    

def plot_ts_pandas(data, data_rm, v):    
    fig, ax = plt.subplots(1, figsize=(11,5))
    
    time = np.arange(1971,2101,1)
    
    ax.plot(time, data, color='lightgray')
    for cols in data_rm.columns:
        ax.plot(time,data_rm[cols], label=cols)
    
    ax.plot(time, data_rm.median(1),linewidth=3.0, color='black', label="Ensemblemittel")    #ensemblemittel

    lgd = ax.legend(bbox_to_anchor=(1, -0.35), loc='lower right', ncol=3)
    
    if ( v == 'pr' ):
        ax.set_yticks(np.arange(-40,80,20))
        ax.set_ylabel('$\Delta$ Niederschlag [%]')
        ax.set_title('Sommer Niederschlagsänderung [%] im 30-Jahresmittel', fontsize=13)
    
    elif ( v == 'tas' ):
        ax.set_yticks(np.arange(-3,7,1))
        ax.set_ylabel('$\Delta$ Temperatur [K]')
        ax.set_title('Jährliche Temperaturänderung [K] im 30-Jahresmittel', fontsize=13)
    
    plt.xticks(np.arange(1970,2101,10))
    plt.grid()
    #plt.savefig("ts_all_"+v+"_"+"pandas"+".pdf")    
    
    plt.show()    


def plot_jahresgang(ensemble, dwd, j_min, j_max, v):
    fig, ax = plt.subplots()
    ax.plot(ensemble, color='blue', label='Mittelwert Simulationen')
    ax.plot(dwd, color='red',label='Messwerte DWD')
    ax.fill_between(np.arange(12),j_min,j_max, facecolor='lightgray', 
                    label='Spannweite aller Simulationen')
    #ax.plot(j_min)
    #ax.plot(j_max)
    #for i in jahresgang:
    #    ax.plot(i)
    #plt.xticks(np.arange(0,131,10),np.arange(1971,2101,10))
    if ( v == 'pr' ):
        ax.set_title('Jahresgang Niederschlag (1971-2000)')
        ax.set_yticks(np.arange(0,150,10))
        ax.set_ylabel('Niederschlag [mm/Monat]')
        lgd=ax.legend(bbox_to_anchor=(1, -0.3), loc='lower right', ncol=1)
    elif ( v == 'tas' ):
        ax.set_title('Jahresgang Temperatur (1971-2000)')
        ax.set_yticks(np.arange(0,21,2))
        ax.set_ylabel('Temperatur [$^\circ$C]')
        lgd=ax.legend(bbox_to_anchor=(1, -0.3), loc='lower right', ncol=1)
        
    names = ['J','F','M','A','M','J','J','A','S','O','N','D']    
    plt.xticks(np.arange(12),names)
    plt.grid() 
    plt.savefig("validierung_"+v+".pdf",bbox_extra_artists=(lgd,), bbox_inches='tight')    
    plt.show()    
    
def plot_jahresgang_hist(var_tas, var_pr):
    fig, ax1 = plt.subplots()
    #ax3 = fig.add_subplot(111)
    ax1.plot(var_tas, color = 'r')
    ax1.set_yticks(np.arange(0,55,5))
    ax1.set_ylabel('Temperatur [$^\circ$C]')
    #ax3.annotate('hallo',xy=(20,5),xytext=(20, 5),arrowprops=dict(facecolor='black', shrink=0.05))
    #plt.xticks(np.arange(0,131,10),np.arange(1971,2101,10))
    
    ax2 = ax1.twinx()
    ax2.bar(np.arange(12), var_pr, width=0.4, color='b',align='center', alpha=0.4)
    ax2.set_yticks(np.arange(0,110,10))
    ax2.set_ylabel('Niederschlag [mm/Monat]')

    # beschriftung mit werten 
    tas_mean = round(np.mean(var_tas),2)
    pr_sum = round(np.sum(var_pr),2)
    ax1.text(0, 45 ,"_\nT = {} $^\circ$C".format(tas_mean), fontsize=12)
    ax1.text(0, 40 ,"Pr = {} mm".format(pr_sum), fontsize=12)
    
    names = ['J','F','M','A','M','J','J','A','S','O','N','D']    
    plt.xticks(np.arange(12),names)
    plt.grid()
    fig.tight_layout()
    plt.savefig("klimadiagramm_dwd.pdf")
    plt.show()    

