
import pandas as pd 
from datetime import datetime, timezone
import pytz
import matplotlib.pyplot as plt
from matplotlib import gridspec
import numpy as np 
import pickle 

##Merge Tide Data ##


filename_output = r"C:\Users\ecarle\git\CoastSat\data\MATAKANA_All_1984_2024\MATAKANA_All_1984_2024_output.pkl"
with open(filename_output, 'rb') as f:
    output = pickle.load(f)

print('yay')
## Read in csvs

if False: 
    data1 = pd.read_csv(r"C:\Users\ecarle\OneDrive - MetService\Documents\2_Consutancy\projects\tauranga\data\topex_tauranga_1966-1995.csv", dtype=str)
    data2 = pd.read_csv(r"C:\Users\ecarle\OneDrive - MetService\Documents\2_Consutancy\projects\tauranga\data\topex_tauranga_1995-2024.csv", dtype=str)
    
    data1['dates'] = pd.to_datetime(data1['date'], format = '%d/%m/%Y %H:%M')
    data2['dates'] = pd.to_datetime(data2['date'], format = '%d/%m/%Y %H:%M')
    
    #drop pre 1984 data
    data1 = data1[data1['dates'].dt.year > 1984]
    
    data1.dates = data1.dates.dt.tz_localize('UTC')
    data2.dates = data2.dates.dt.tz_localize('UTC')
    
    data1 = data1[['dates', 'tide']]
    data2 = data2[['dates', 'tide']]
    #merge datasets 
    merged = pd.concat([data1, data2], ignore_index=True)
    
    #write to csv
    merged.to_csv(r"C:\Users\ecarle\OneDrive - MetService\Documents\2_Consutancy\projects\tauranga\data\topex_tauranga_1984-2024.csv",index=False)


if False:
    
    #load data
    cross_distance = pd.read_csv(r"C:\Users\ecarle\git\CoastSat\data\MATAKANA_All_1984_2024\transect_time_series.csv",  parse_dates=['dates'])
    cross_distance_tidally_corrected = pd.read_csv(r"C:\Users\ecarle\git\CoastSat\data\MATAKANA_All_1984_2024\transect_time_series_tidally_corrected.csv", parse_dates=['dates'])
    
    dates = cross_distance['dates']

    cross_distance = cross_distance.drop('dates', axis=1)
    cross_distance_tidally_corrected = cross_distance_tidally_corrected.drop('dates', axis=1)
    

    ##cleanup outliers
    cross_distance[cross_distance < 50] = np.nan 
    cross_distance_tidally_corrected[cross_distance_tidally_corrected < 50] = np.nan
    
    cross_distance = cross_distance[['Transect matakana2', 'Transect matakana4', 
                                     'Transect matakana6', 'Transect matakana8']]
    
    # plot the time-series of shoreline change (both raw and tidally-corrected)
    
    
    fig = plt.figure(figsize=[10,8])
    fig.tight_layout(pad=1)
    gs = gridspec.GridSpec(len(cross_distance.columns),1)
    gs.update(left=0.05, right=0.95, bottom=0.05, top=0.95, hspace=0.05)
    
    for i,key in enumerate(cross_distance.keys()):
        # if np.all(np.isnan(cross_distance[key])):
        #     continue
        ax = fig.add_subplot(gs[i,0])
        ax.grid(linestyle=':', color='0.5')
        ax.set_ylim([-120,120])
        ax.plot(dates, cross_distance[key]- np.nanmedian(cross_distance[key]), '-o', ms=2, mfc='w', label='raw')
        ax.plot(dates, cross_distance_tidally_corrected[key]- np.nanmedian(cross_distance[key]), '-o', ms=2, mfc='w', alpha = 0.8, label='tidally-corrected')
        ax.set_ylabel('distance [m]', fontsize=8)
        ax.text(0.5,0.95, key, bbox=dict(boxstyle="square", ec='k',fc='w'), ha='center',
                va='top', transform=ax.transAxes, fontsize=14)
        ax.tick_params(axis='both', labelsize=10)
    ax.legend()
    plt.savefig(r'C:\Users\ecarle\git\CoastSat\data\MATAKANA_All_1984_2024\output\shoreline_change_transects_ts.png',dpi=200)
    #
if False:

#%% 5. Time-series post-processing
        
    # load mapped shorelines from 1984 (mapped with the previous code)
    filename_output = r"C:\Users\ecarle\git\CoastSat\data\MATAKANA_All_1984_2024\MATAKANA_All_1984_2024_output.pkl"
    with open(filename_output, 'rb') as f:
        output = pickle.load(f)
    
    if False:
        # load long time-series (1984-2021)
        filepath = os.path.join(os.getcwd(),'examples','NARRA_time_series_tidally_corrected.csv')
        df = pd.read_csv(filepath, parse_dates=['dates'])
        dates = [_.to_pydatetime() for _ in df['dates']]
        cross_distance = dict([])
        for key in transects.keys():
            cross_distance[key] = np.array(df[key])
        
        #%% 5.1 Remove outliers
        
        # plot Otsu thresholds for the mapped shorelines
        fig,ax = plt.subplots(1,1,figsize=[12,5],tight_layout=True)
        ax.grid(which='major',ls=':',lw=0.5,c='0.5')
        ax.plot(output['dates'],output['MNDWI_threshold'],'o-',mfc='w')
        ax.axhline(y=-0.5,ls='--',c='r',label='otsu_threshold limits')
        ax.axhline(y=0,ls='--',c='r')
        ax.set(title='Otsu thresholds on MNDWI for the %d shorelines mapped'%len(output['shorelines']),
               ylim=[-0.6,0.2],ylabel='otsu threshold')
        ax.legend(loc='upper left')
        fig.savefig(os.path.join(inputs['filepath'], inputs['sitename'], 'otsu_threhsolds.jpg'))
        
        # remove outliers in the time-series (despiking)
        settings_outliers = {'otsu_threshold':     [-.5,0],        # min and max intensity threshold use for contouring the shoreline
                             'max_cross_change':   40,             # maximum cross-shore change observable between consecutive timesteps
                             'plot_fig':           True,           # whether to plot the intermediate steps
                            }
        cross_distance = SDS_transects.reject_outliers(cross_distance,output,settings_outliers)
        
        #%% 5.2 Seasonal averaging
        
        # compute seasonal averages along each transect
        season_colors = {'DJF':'C3', 'MAM':'C1', 'JJA':'C2', 'SON':'C0'}
        for key in cross_distance.keys():
            chainage = cross_distance[key]
            # remove nans
            idx_nan = np.isnan(chainage)
            dates_nonan = [dates[_] for _ in np.where(~idx_nan)[0]]
            chainage = chainage[~idx_nan]
        
            # compute shoreline seasonal averages (DJF, MAM, JJA, SON)
            dict_seas, dates_seas, chainage_seas, list_seas = SDS_transects.seasonal_average(dates_nonan, chainage)
        
            # plot seasonal averages
            fig,ax=plt.subplots(1,1,figsize=[14,4],tight_layout=True)
            ax.grid(which='major', linestyle=':', color='0.5')
            ax.set_title('Time-series at %s'%key, x=0, ha='left')
            ax.set(ylabel='distance [m]')
            ax.plot(dates_nonan, chainage,'+', lw=1, color='k', mfc='w', ms=4, alpha=0.5,label='raw datapoints')
            ax.plot(dates_seas, chainage_seas, '-', lw=1, color='k', mfc='w', ms=4, label='seasonally-averaged')
            for k,seas in enumerate(dict_seas.keys()):
                ax.plot(dict_seas[seas]['dates'], dict_seas[seas]['chainages'],
                         'o', mec='k', color=season_colors[seas], label=seas,ms=5)
            ax.legend(loc='lower left',ncol=6,markerscale=1.5,frameon=True,edgecolor='k',columnspacing=1)
        
        #%% 5.3 Monthly averaging
        
        # compute monthly averages along each transect
        month_colors = plt.cm.get_cmap('tab20')
        for key in cross_distance.keys():
            chainage = cross_distance[key]
            # remove nans
            idx_nan = np.isnan(chainage)
            dates_nonan = [dates[_] for _ in np.where(~idx_nan)[0]]
            chainage = chainage[~idx_nan]
        
            # compute shoreline seasonal averages (DJF, MAM, JJA, SON)
            dict_month, dates_month, chainage_month, list_month = SDS_transects.monthly_average(dates_nonan, chainage)
        
            # plot seasonal averages
            fig,ax=plt.subplots(1,1,figsize=[14,4],tight_layout=True)
            ax.grid(which='major', linestyle=':', color='0.5')
            ax.set_title('Time-series at %s'%key, x=0, ha='left')
            ax.set(ylabel='distance [m]')
            ax.plot(dates_nonan, chainage,'+', lw=1, color='k', mfc='w', ms=4, alpha=0.5,label='raw datapoints')
            ax.plot(dates_month, chainage_month, '-', lw=1, color='k', mfc='w', ms=4, label='monthly-averaged')
            for k,month in enumerate(dict_month.keys()):
                ax.plot(dict_month[month]['dates'], dict_month[month]['chainages'],
                         'o', mec='k', color=month_colors(k), label=month,ms=5)
            ax.legend(loc='lower left',ncol=7,markerscale=1.5,frameon=True,edgecolor='k',columnspacing=1)
