#!/usr/bin/python3

from netCDF4 import Dataset
import numpy as np
import glob 
import matplotlib.pyplot as plt  
import sys
from matplotlib import colors
from mpl_toolkits.basemap import Basemap
import coord_trafo as ct
import numpy.ma as ma
import time
import mod_calculations as ca
import mod_plot as mp
import pandas as pd
from scipy.stats import norm
from scipy import stats
import seaborn as sns
from sklearn.neighbors.kde import KernelDensity
#%matplotlib inline
#import matplotlib.pyplot as plt
#import seaborn; seaborn.set()


# norm means the change of the extreme event -> klimasignal
class Extrem(object):

    def __init__(self, name_ee, o, var):
        data = "/home/steffen/Masterarbeit/Daten/{}/{}.csv".format(o,name_ee)
        self.vals = pd.read_csv(data, index_col=0)
        self.name = name_ee
        self.var = var
            
    def rolling_mean(self):
        return self.vals.rolling(30,center=True).mean()
    
    def ensemble_mean(self):
        return self.vals.mean(1)
    
    def ensemble_rm(self):
        return self.rolling_mean().mean(1)
    
    def rm_norm(self):
        if self.var == "tas":
            return self.rolling_mean()-self.rolling_mean().iloc[15]
        elif self.var == "pr":
            return (self.rolling_mean()/self.rolling_mean().iloc[15]-1)*100
        
    def ensemble_rm_norm(self):
        return self.rm_norm().mean(1)
    
    def signal(self):
        if self.name == "vp" or self.var == "tas":
            return self.rm_norm()
        else:
            return (self.rolling_mean()/self.rolling_mean().iloc[15]-1)*100
    
    def signal_ensemble(self):
        return self.signal().mean(1)
    
    def year_mean_norm(self):
        if self.var == "tas":
            return self.vals - self.rolling_mean().iloc[15]
        elif self.var == "pr":
            return (self.vals/self.rolling_mean().iloc[15]-1)*100
    
    def jahreszeit(self, st, jz, em=False):
        # gibt mir die täglichen Daten für bestimmte jahreszeit
        # em steht für ensemblemean und berechnet em aus allen modellen
        year = np.arange(st,st+30)
        hv = np.array([])
        hv_all = pd.DataFrame() 
        if jz == 'year':
            if em:
                for iyear in year:
                    foo = self.vals.loc['{}-01-01'.format(iyear):'{}-12-31'.format(iyear)]
                    hv = np.append(hv, foo)
                    
                return hv    
                
            else:
                '''
                for icol in self.vals.columns.values:
                    hv_all[icol] = self.vals[icol].loc['{}-01-01'.format(start):'{}-12-31'.format(start+29)] 
                return hv_all
                '''
                for icol in self.vals.columns.values:
                    hv = np.array([])
                    for iyear in year:
                        foo = self.vals[icol].loc['{}-01-01'.format(iyear):'{}-12-31'.format(iyear)]
                        hv = np.append(hv, foo)      
                    hv_all[icol] = hv
                return hv_all

        elif jz == 'djf':
            if em:
                for iyear in year:
                    foo = self.vals.loc['{}-12'.format(iyear-1):'{}-03'.format(iyear)]
                    hv = np.append(hv, foo)
                return hv    
            else:
                for icol in self.vals.columns.values:
                    hv = np.array([])
                    for iyear in year:
                        foo = self.vals[icol].loc['{}-12'.format(iyear-1):'{}-03'.format(iyear)]
                        hv = np.append(hv, foo)      
                    hv_all[icol] = hv
                return hv_all
        
        else:
            if jz == 'mam':
                start = '03'
                end = '06'
            elif jz == 'jja':
                start = '06'
                end = '09'
            elif jz == 'son':
                start = '09'
                end = '12'
            
            if em:
                for iyear in year:
                    foo = self.vals.loc['{}-{}'.format(iyear, start):'{}-{}'.format(iyear, end)]
                    hv = np.append(hv, foo)
                return hv    
            else:
                for icol in self.vals.columns.values:
                    hv = np.array([])
                    for iyear in year:
                        foo = self.vals[icol].loc['{}-{}'.format(iyear, start):'{}-{}'.format(iyear, end)]
                        hv = np.append(hv, foo)      
                    hv_all[icol] = hv
                return hv_all
            
        

def readdata(path, var, ensemble):
    #< liest Variablen aus einer oder mehreren nc-dateien ein
    #< für räumliche daten genutzt
    
    path = "/home/steffen/Masterarbeit/Daten/spat/"+path
    datanames = sorted(glob.glob(path+'.nc'))
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

    
def mann_whitney(hv0, hv1, em):
    #< untersucht jedes modell auf:
    #< 1. unterschiedliche hv
    #< 2. welche richtung Klimaänderungssignal zeigt
    #< erfüllen 6 von 9 modellen test 1 und stimmen in test 2 überein
    #< -> signal robust
    #< in: zeitreihe jährlicher daten für zeitraum (shape hv0/hv1: (zahl modelle, daten[zeitraum]))
    #<     und ensemblemean für zweiten zeitraum um änderungssignal nachzugucken
    #< out: 1 wenn beide test erfüllt, 2 wenn nur richtung, 0 wenn nicht mal richtung 
    
    sig = np.zeros(9)
    a = 0
    
    for i, mod in enumerate(hv0.columns):
        if np.array_equal(hv0[mod].values, hv1[mod].values):
            p = 1
        else: 
            st, p = stats.mannwhitneyu(hv0[mod],hv1[mod])
        alpha = 0.1
        #print(p)
        if p < alpha:
            a = a + 1
        if em[mod] > 0:
            sig[i] = 1
        else:
            sig[i] = 0
    
    if np.count_nonzero(sig[:])>=6 or np.count_nonzero(sig[:])<=3: 
        # ab hier sind alle wahrscheilich
        if a >= 6: #6 von 9 haben test bestanden
            return 1
        else:
            return 2
    else:
        # käs nicht wahrscheinlich
        return 0

    
def jahreszeit(data, st, jz):
    # Funktion, die täglichen Daten in Jahreszeiten einteilen kann
    # in: monatliche gemittelte Daten, jahreszeit und startjahr
    # out: monatliche Daten einer Jahreszeit für Zeitraum 30 Jahre
    out = pd.DataFrame()
    year = np.arange(st,st+30)

    if jz == 'year':
        out = data.loc['{}-01-01'.format(st):'{}-12-31'.format(st+29)]
    
    elif jz == 'djf':
        for icol in data.columns:
            hv = np.array([])
            for iyear in year:
                foo = data[icol].loc['{}-12'.format(iyear-1):'{}-03'.format(iyear)]
                hv = np.append(hv, foo)
            out[icol] = hv

    else:
        if jz == 'mam':
            start = '03'
            end = '06'
        elif jz == 'jja':
            start = '06'
            end = '09'
        elif jz == 'son':
            start = '09'
            end = '12'

        for icol in data.columns:
            hv = np.array([])
            for iyear in year:
                foo = data[icol].loc['{}-{}'.format(iyear,start):'{}-{}'.format(iyear, end)]
                hv = np.append(hv, foo)
            out[icol] = hv
    return out

def loghv(data):
    hist = plt.hist(data, bins=int(round(max(data))), normed=True, alpha=0.5)
    den, bins, patches = hist
    log = np.log10(den)
    log = pd.Series(log, index=np.arange(1,log.shape[0]+1))
    plt.close()
    return log
    
def printextrem(extrem):
    #ee = 'frosttage'
    #ref =  Extrem(extrem,'ts',var).rolling_mean().loc['1986-01-01']
    ref =  Extrem(extrem,'ts',var).signal().loc['2036-01-01']
    print(ref)
    #print('{}: min: {}, max:{}'.format(extrem, min(ref),max(ref)))
    print('mean: {}'.format(np.median(ref)))
    return 
    
#< berechnet käs für alle modelle, nur jahr eingeben
def klimaänderungssignal(dic, year):
    sig = pd.DataFrame()
    for iextrem in dic.keys():
        sig[iextrem] = Extrem(iextrem,'ts',var).signal().loc['{}-01-01'.format(year)]
    return sig

def plot_extrem(dic):
    sig = [klimaänderungssignal(dic, '2036'), klimaänderungssignal(dic, '2086')]
    jahr = ['2021-2050','2071-2100']
    #subplots benutzen
    for i in range(1,3):
        plt.subplot(1,2,i)    
        mp.plot_signalbandbreite(sig[i-1], dic, jahr[i-1],'ex')
    plt.tight_layout() 
    plt.subplots_adjust(wspace=0.5)
    plt.savefig("veg_änderung.pdf", dpi=96)
    #plt.savefig("extrem_"+ opt+".pdf", dpi=96)
    #plt.savefig("trockentage_sig_jz.pdf", dpi=96)
    plt.show()
    
if __name__ == '__main__':
    
    opt = sys.argv[1]
    var = sys.argv[2]
    
    ext = 'snt'
    snt = {"{}_djf".format(ext):"djf","{}_mam".format(ext):"mam", "{}_jja".format(ext):"jja",
            "{}_son".format(ext):"son", "{}_year".format(ext):"year"}
    
    ee = {'warmeperiode':'wp', 'trockenperiode':'tp', 'frosttage':'ft', 'speatfrost':'sft'}
    
    veg = {'vegetationsphase':'vp', 'vegetationsphase_start':'start', 'vegetationsphase_ende':'ende'}

    #printextrem('vegetationsphase_ende')
    #sys.exit()
     
    if opt == 'bb':
        # plotting klimasignale der extremereignisse

        '''
        if var == 'tas':
            ee = {"{}_year".format(ext):"year", "{}_djf".format(ext):"djf","{}_mam".format(ext):"mam",
                  "{}_jja".format(ext):"jja","{}_son".format(ext):"son"}
        '''
        plot_extrem(veg)
        
    elif opt == 'ts':
        #ts = Extrem('jahresmittel_{}'.format(var),opt,var)
        #ts = Extrem('sommer_{}_jm'.format(var),opt,var)
        #ts = Extrem('winter_{}_jm'.format(var),opt,var)
        ts = Extrem('son_{}_jm'.format(var),opt,var)
        #ts = Extrem('mam_{}_jm'.format(var),opt,var)
        
        mp.plot_signalbandbreite(extrem, ee_names, jahr,o)
        
        #sommer = Extrem('sommer_{}_jm'.format(var),opt,var).rm_norm()
        #winter = Extrem('winter_{}_jm'.format(var),opt,var).rm_norm()
        #mon = Extrem('month_{}_jm'.format(var),opt,var).vals
        #tas_rm = ts.rm_norm()
        #print(ts.signal_ensemble()['2086-01-01'])
        #tas_ym = ts.year_mean_norm()
        #mp.plot_ts_pandas(tas_ym, tas_rm, var)
        #plt.savefig("ts_"+v+'djf'+".pdf",bbox_extra_artists=(lgd,), bbox_inches='tight')    
        #plt.show()
        sys.exit()
        hv_year = pd.DataFrame()
        hv_mon = pd.DataFrame()
        hv_year2 = pd.DataFrame()
        hv_mon2 = pd.DataFrame()
        
        jahreszeit(mon,'year',1971)
        
        
        for col in mon.columns:
            hv_year[col] = ts.vals['1971':'2000'][col].values.flatten()
            hv_year2[col] = ts.vals['2071':'2100'][col].values.flatten()
            hv_mon[col] = mon['1971':'2000'][col].values.flatten()
            hv_mon2[col] = mon['2071':'2100'][col].values.flatten()

        print(stats.mannwhitneyu(hv_mon['cm1'], hv_mon2['cm1']))
        #plot_kde(hv_year, ensemble=True)
        #plot_kde(hv_mon, ensemble=True)
        #print(ts.vals['1971':'2000'])
        #sns.kdeplot(hv_mon['cm1'], label='mon', linewidth=2)
        #sns.kdeplot(hv_mon2['cm1'], label='mon2', linewidth=2)
        sns.kdeplot(hv_mon['cm1'], label='year', linewidth=2)
        sns.kdeplot(hv_mon2['cm1'], label='year2', linewidth=2)
        
        plt.show()
        #sns.kdeplot(hv2_e, label='2071-2100', linewidth=3, color='black')
        
        #mon['cm0'].plot()
        #plt.show()
        #bb = [max(tas_ym[i]) for i in range(len(tas_ym))]
        #bb_ym = [max(tas_rm.loc['{}-01-01'.format(year)])-min(tas_rm.loc['{}-01-01'.format(year)]) for year in range(1986,2087)]
        #bb_w = [max(winter.loc['{}-01-01'.format(year)])-min(winter.loc['{}-01-01'.format(year)]) for year in range(1986,2087)]
        #bb_s = [max(sommer.loc['{}-01-01'.format(year)])-min(sommer.loc['{}-01-01'.format(year)]) for year in range(1986,2087)]

        #plt.plot(bb_ym, label='year')
        #plt.plot(bb_w, label='winter')
        #plt.plot(bb_s, label='sommer')
        #plt.legend()
        #plt.show()
        #print(tas_ym.loc['1986-01-01']) 
        #ca.plot_ts_pandas(tas_ym, tas_rm, var)
            
    elif opt == 'hv':
        # haeufigkeitsverteilung tageswerte
        jz = sys.argv[3]
        #time = sys.argv[4]
        
        
        if jz == 'jja':
            jahreszeit = 'im Sommer'
        elif jz == 'djf':
            jahreszeit = 'im Winter'
        else:
            jahreszeit = ' '
        
        sns.set()
        day = Extrem('daily_{}'.format(var),'ts',var)        
        sig = Extrem('winter_pr_jm','ts',var).signal().loc['2086-01-01']
        #em = Extrem('winter_pr_jm','ts',var).rm_norm().loc['{}-01-01'.format(period+15)]
        
        hv0 = day.jahreszeit(1971, jz, em=False)
        hv1 = day.jahreszeit(2021, jz, em=False)
        hv2 = day.jahreszeit(2071, jz, em=False)

        hv0e = day.jahreszeit(1971, jz, em=True)
        hv1e = day.jahreszeit(2021, jz, em=True)
        hv2e = day.jahreszeit(2071, jz, em=True)
        
        hv0s = day.jahreszeit(1971, 'jja', em=True)
        hv0w = day.jahreszeit(1971, 'djf', em=True)
        hv0h = day.jahreszeit(1971, 'son', em=True)
        hv0f = day.jahreszeit(1971, 'mam', em=True)
        '''
        x = hv0e[:, np.newaxis]
        kde = KernelDensity(kernel='gaussian', bandwidth=0.2).fit(x)
        d = kde.score_samples(x)
        print(d.shape)
        '''
        
        #vllt noch brauchbar für ensembleplot
        '''
        plot_kde(hv0, label='1971-2000', color='red', ensemble=True)
        plot_kde(hv2, label='2021-2050', color='blue', ensemble=True)        
        #plot_kde(hv2, label='2071-2100', ensemble=False)
        sns.kdeplot(hv0e, label='1971-2000', linewidth=3, color='black')
        #sns.kdeplot(hv2, label='2071-2100', linewidth=3, color='black')
        #sns.kdeplot(hv0_e, label='2071-2100', linewidth=3, color='black')
        plt.legend()
        plt.show()
        sys.exit()
        '''
        '''
        # pr ensemble hv plotten
        density_e = []
        for icol in day.vals.columns:            
            density_e.append(loghv(hv0[icol]))
        density_e = np.array(density_e)

        density_e2 = []
        for icol in day.vals.columns:            
            density_e2.append(loghv(hv2[icol]))
        density_e2 = np.array(density_e2)

        density_e1 = []
        for icol in day.vals.columns:            
            density_e1.append(loghv(hv1[icol]))
        density_e1 = np.array(density_e1)
        '''
        # Ich teile die Verteilungen so ein, dass jeder x wert 1 mm niederschlag darstellt.
        loghv0 = loghv(hv0e)
        loghv1 = loghv(hv1e)
        loghv2 = loghv(hv2e)
        #print('{}: {}'.format(jz, mann_whitney(hv0,hv2, sig)))
        #for d, icol in enumerate(day.vals.columns):
            #plt.plot(density_e[d][:400], color='red')
            #plt.plot(density_e1[d][:400], color='blue')
            #sns.kdeplot(hv0[icol], alpha=0.5, color='red')
            #sns.kdeplot(hv1[icol], alpha=0.5, color='blue')
            #plt.show()

        plt.plot(loghv0[:40], label='1971-2000')
        plt.plot(loghv1[:40], label='2021-2050')
        plt.plot(loghv2[:40], label='2071-2100')
        plt.legend()
        plt.show()
        #plt.savefig("{}_hvlog_{}.pdf".format(var, jz))
        sys.exit()
        
        '''
        Problem beim speichern: Da plt.close gemacht wird, kann bild nicht richtig gespeichert werden
        vllt mit axes arbeiten? 
        '''
        
        
        # HV aller Zeiträume
        #sns.kdeplot(hv0e, label='1971-2000', shade=True)
        #sns.kdeplot(hv1e, label='2021-2050', shade=True)        
        #sns.kdeplot(hv2e, label='2071-2100', shade=True)
        '''
        sns.kdeplot(hv0e, label='Jahr', shade=True, color='grey')
        
        sns.kdeplot(hv0s, label='Sommer', color='red')
        sns.kdeplot(hv0w, label='Winter', color='blue')
        sns.kdeplot(hv0h, label='Herbst', color='brown')
        sns.kdeplot(hv0f, label='Frühling', color='green')
        
        #plt.title('Verteilung der taeglichen Mitteltemperatur {}'.format(jahreszeit))
        plt.title('Temperaturverteilung im Referenzzeitraum 1971-2000 [Ensemble]')
        plt.xlabel('Niederschlag [$^\circ$C]')
        plt.ylabel('Relative Haeufigkeitsdichte')
        #plt.savefig("{}_hv_{}.pdf".format(var, jz), dpi=96)
        #plt.savefig("tas_hv_vglsommerwinter.pdf", dpi=96)
        '''
        # Perzentil-Plots
        p_delta = 0.5
        perc0e = np.percentile(hv0e, np.arange(0,100,p_delta))
        perc1e = np.percentile(hv1e, np.arange(0,100,p_delta))
        perc2e = np.percentile(hv2e, np.arange(0,100,p_delta))
        perc_diff1e = perc1e - perc0e
        perc_diff2e = perc2e - perc0e
        
        for icol in day.vals.columns.values:
            perc0 = np.percentile(hv0[icol], np.arange(0,100,p_delta))
            perc1 = np.percentile(hv1[icol], np.arange(0,100,p_delta))
            perc2 = np.percentile(hv2[icol], np.arange(0,100,p_delta))
            perc_diff1 = perc1 - perc0
            perc_diff2 = perc2 - perc0
            #print(np.percentile(hv0_s, 95))
            #print(np.percentile(hv2_s, 95))
            #print(np.percentile(hv2_s, 95)-np.percentile(hv0_s, 95))
            
            #plt.plot(np.arange(0,100,5), perc0)
            #plt.plot(np.arange(0,100,5), perc2)
            #plt.plot(np.arange(0,100,p_delta), perc0, label = icol)
            plt.plot(np.arange(0,100,p_delta), perc_diff1, label = icol)
            #plt.plot(np.arange(0,100,p_delta), perc_diff2, label=icol)
        
        #plt.plot(np.arange(0,100,p_delta), perc0e, linewidth=3, color='black', label='Ensemble')
        plt.plot(np.arange(0,100,p_delta), perc_diff1e, linewidth=3, color='black', label='Ensemble')
        #plt.plot(np.arange(0,100,p_delta), perc_diff2e, linewidth=3, color='black', label='Ensemble')
        lgd = plt.legend(bbox_to_anchor=(1, -0.35), loc='lower right', ncol=3)
        #plt.title('Perzentiländerung bis 2021-2050 {}'.format(jahreszeit))
        #plt.savefig("{}_perc_{}_{}.pdf".format(var, jz, '2'),bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.show()
        sys.exit()
        
        
    elif opt == 'test':
        #< ts Daten auf signifikanz testen
        #< Eingabe von Periode, die getestet werden soll: 2021 oder 2071
        #< data stellt für jede Jahreszeit die jährlichen Mittel zusammen. Aus diesen kann dann schnell 
        #< ensemblemean berechnet werden. Ansonsten rechnerischer aufwand größer
        
        period = int(sys.argv[3])

        data = {'year':'jahresmittel_{}'.format(var), 'djf':'winter_{}_jm'.format(var),'mam':'mam_{}_jm'.format(var),\
              'jja':'sommer_{}_jm'.format(var),'son':'son_{}_jm'.format(var)}

        day = Extrem('daily_{}'.format(var),'ts',var)

        for jz in data:
            hv0 = day.jahreszeit(1971,jz)
            hv1 = day.jahreszeit(period,jz)
            em = Extrem(data[jz],'ts',var).rm_norm().loc['{}-01-01'.format(period+15)]
            print('{}: {}'.format(jz, mann_whitney(hv0,hv1, em)))
    
    elif opt == 'testex':
        #< ts extremwertdaten auf signifikanz testen
        #< Eingabe von Periode, die getestet werden soll: 2021 oder 2071
        #< data stellt für jede Jahreszeit die jährlichen Mittel zusammen. Aus diesen kann dann schnell 
        #< ensemblemean berechnet werden. Ansonsten rechnerischer aufwand größer
        
        period = int(sys.argv[3])
        
        for ex in veg.keys():
            hv0 = Extrem(ex,'ts',var).vals.loc['1971-01-01':'2000-01-01']
            hv1 = Extrem(ex,'ts',var).vals.loc['{}-01-01'.format(period):'{}-01-01'.format(period+30)]
            em = Extrem(ex,'ts',var).rm_norm().loc['{}-01-01'.format(period+15)]
            print('{}: {}'.format(ex, mann_whitney(hv0,hv1, em)))
        
            
        
    elif opt == 'testspatex':
        # brauche: ensemblewert, jährlichen wert an jedem gp und für jeden modell käs an jedem gp
        
        #jz = sys.argv[3]
        
        fm = 'spat_fm_pr_tp'
        year = 'spatex_pr_tp_year'
        em = 'spat_em_pr_tp'
        
        year, lons, lats, rlons, rlats = readdata(year, var, False)
        fm, lons, lats, rlons, rlats = readdata(fm, var, False)
        em, lons, lats, rlons, rlats = readdata(em, var, False)
        
        jm = ma.array(np.zeros((2,31,34), 'f'))
        jm = ct.niedersachsen(jm)
        ind = pd.date_range('1971','2100',freq='As')
        cols = ['cm0','cm1','cm2','cm3','cm4','cm5','cm6','cm7','cm8']
        
        for i, period in enumerate([2021, 2071]):
            print(period)
            for lon in range(31):
                print(lon)
                for lat in range(34):
                    ref = year[0,0:2,lon,lat]
                    if ~ref.mask[0]:
                        #< erstellt dataframe, in dem alle hv aller modelle sind
                        
                        t = pd.DataFrame(np.transpose(year[:,:,lon,lat]),columns=cols,index=ind)
                        s = pd.DataFrame(np.transpose(fm[:,:,lon,lat]),columns=cols,index=['0','2021','2071'])
                        hv0 = t.loc['1971':'2000']
                        hv1 = t.loc['{}'.format(period):'{}'.format(period+29)]
                        #em = Extrem(data[jz],'ts',var).rm_norm().loc['2036-01-01']
                        #print('{}: {}'.format(lat, mann_whitney(hv0,hv1, e.loc['2'])))
                        test = mann_whitney(hv0,hv1, s.loc[str(period)])
                        if test == 1:
                            # wahrscheinlich und u-test
                            jm[i, lon, lat] = em[i+1 ,lon,lat]
                        elif test == 2:
                            # wahrscheinlich, aber bestehen u-test nicht
                            jm[i, lon, lat] = -10000
                        else:
                            # nicht wahrscheinlich
                            jm[i, lon, lat] = +10000
                        
        ca.writing_nc(jm, "spat_test_tp_1.nc", var, rlats, rlons,em=True)                
        
    elif opt == 'testspat':
        #< räumliche Daten auf signifikanz testen
        #< fm ist für jeden gp klimaänderungssignal jeden modells um änderung anzuzeigen
        #< d sind tägliche werte für jeden gp, für hv vergleich 
        #< em ist ensemblemean des klimaänderugnssignals

        jahreszeiten = ['year', 'djf', 'mam', 'jja', 'son']
        
        #if period == 2021:
        #    em_ind = 1
        #else:
        #    em_ind = 2
        
        
        for jz in jahreszeiten:
            
            print(jz)
            fm = 'spat_fm_{}_{}'.format(var, jz)
            d = 'spat_{}_day'.format(var)
            em = 'spat_em_{}_{}'.format(var, jz)
            
            d, lons, lats, rlons, rlats = readdata(d, var, False)
            fm, lons, lats, rlons, rlats = readdata(fm, var, False)
            em, lons, lats, rlons, rlats = readdata(em, var, False)

            jm = ma.array(np.zeros((2,31,34), 'f'))
            jm = ct.niedersachsen(jm)
            ind = pd.date_range('1971-01-01','2100-12-31',freq='D')
            cols = ['cm0','cm1','cm2','cm3','cm4','cm5','cm6','cm7','cm8']
            
            for i, period in enumerate([2021,2071]):
                print(period)
                
                for lon in range(31):
                    print(lon)
                    for lat in range(34):
                        ref = d[0,0:2,lon,lat]
                        if ~ref.mask[0]:
                            #< erstellt dataframe, in dem alle hv aller modelle sind
                            
                            t = pd.DataFrame(np.transpose(d[:,:,lon,lat]),columns=cols,index=ind)
                            s = pd.DataFrame(np.transpose(fm[:,:,lon,lat]),columns=cols,index=['0','2021','2071'])
                            hv0 = jahreszeit(t, 1971, jz)
                            hv1 = jahreszeit(t, period, jz)
                            #hv1= t.loc['{}-01-01'.format(period):'{}-12-31'.format(period+29)]
                            #em = Extrem(data[jz],'ts',var).rm_norm().loc['2036-01-01']
                            #print('{}: {}'.format(lat, mann_whitney(hv0,hv1, e.loc['2'])))
                            test = mann_whitney(hv0,hv1, s.loc[str(period)])
                            if test == 1:
                                jm[i, lon, lat] = em[i+1 ,lon,lat]
                            elif test == 2:
                                # wahrscheinlich, aber bestehen u-test nicht
                                jm[i, lon, lat] = -10000
                            else:
                                # nicht wahrscheinlich
                                jm[i, lon, lat] = +10000
                #jm[i,:,:] = ct.niedersachsen_1(jm[i,:,:])
            
            ca.writing_nc(jm, "spat_test_{}_{}.nc".format(var,jz), var, rlats, rlons,em=True)

    
    elif opt == 'spat':
        '''
        colors:
        tas:
        pr: GnBu (-20 bis 24)
        frosttage: Spectral
        wärmeperiode: jet
        vegetationsperiode: YlGnBu
        trockenperiode: YlOrRd
        snt: YlGnBu
        '''
        jz = sys.argv[3]
        
        data = 'spat_test_pr_{}'.format(jz)
        '''
        year = 'spat_em_{}_year'.format(var)
        djf = 'spat_em_{}_djf'.format(var)
        mam = 'spat_em_{}_mam'.format(var)
        jja = 'spat_em_{}_jja'.format(var)
        son = 'spat_em_{}_son'.format(var)
        '''
        data, lons, lats, rlons, rlats = readdata(data, var, False)
                                
        min_gp=-20
        max_gp=24
        clr = 'GnBu' 
        abst = 2
        
        fig, ax = plt.subplots(1, 2, sharex=True, sharey=False)
        mp.plot_basemap(data[0], lons, lats, min_gp, max_gp, var, abst, color=clr,ax=ax[0])
        mp.plot_basemap(data[1], lons, lats, min_gp, max_gp, var, abst, color=clr,ax=ax[1])
        ax[0].set_xlabel('a) 2021-2050')
        ax[1].set_xlabel('b) 2071-2100')
        plt.savefig('spat_test_pr_{}.pdf'.format(jz), bbox_inches='tight')
        #plt.show()
        
