# -*- coding: utf-8 -*-
"""
Created on Thu Mar 03 22:04:50 2016

A set of tools to manipulate multigas data

@author: Manu
"""

import numpy as np
from scipy.stats import linregress
import pandas as pad
import matplotlib.pyplot as plt
import datetime
try:
    import seaborn
except:
    pass

def get_raw_data(filepath):
    """ open the csv, parse the values and return
    a pandas Dataframe object
    TODO parameterize
    """
    df = pad.read_csv(filepath, parse_dates=[0,1],index_col=[1])
    return df

def get_raw_data_xls(filepath, decimal_time_name='Time '):
    """ open the xls, parse the values and return
    a pandas Dataframe object
    TODO parameterize
    """
    df = pad.read_excel(filepath, 'Sheet1').dropna()
    df['Time'] = pad.Series([datetime.timedelta(seconds=t, microseconds=(t-int(t))*1000000) for t in df[decimal_time_name]],
                                index=df.index)
    df.set_index(pad.TimedeltaIndex(df['Time']), inplace=True)
    #df.drop('Time ') # remove the one with trailing whitespace
    return df

def estimate_atmospheric_constant(df, gas, reference='SO2',
                                  minimum_value = 10):
    """ estimate atmospheric constant
    
    It uses the reference (default is SO2) to look for points where is is 
    close to 0
    which means the plume is not measured yet, so we have purely
    atmospheric data """    
    
    atmospheric_constant = df[gas].where(df[reference] < minimum_value).mean()
    print "Atmospheric %s evaluated at %2.1f ppm" % (gas, atmospheric_constant)
    return atmospheric_constant


def correct_for_atmo(raw_data, gas_tar, gas_ref, minimum_filter=False, plot_result=True):
    """ estimate the atmospheric constant and removes it from 
    the target gas value """
    atmo_constant = estimate_atmospheric_constant(raw_data, gas_tar,
                                                  reference=gas_ref)
    corrected_data = raw_data.copy()
    
    if minimum_filter:
        # TODO remove trend
        from scipy.ndimage.filters import  minimum_filter
        all_max = max(raw_data[gas_tar].values) - raw_data[gas_tar].mean()
        gas_median_filt = pad.Series(minimum_filter(raw_data[gas_tar].values,
                                                  size=(100,)),
                                    index=raw_data.index)
        corrected_data[gas_tar] = raw_data[gas_tar] - gas_median_filt
        corrected_data[gas_tar] = pad.Series([min(all_max, max(i, 0)) for i in corrected_data[gas_tar].values],
                                   index=raw_data.index)

    # Replace value of target gas by the corrected value
    else:
        corrected_data[gas_tar] = pad.Series(raw_data[gas_tar] - atmo_constant,
                                     index=raw_data.index)
    if plot_result:
        plt.figure(figsize=(12,8))
        raw_data[gas_tar].plot()
        corrected_data[gas_tar].plot(style='r')
        plt.legend(['%s measured' %  gas_tar,
                    '%s corrected for atmospheric constant' %  gas_tar])
        plt.ylabel('%s ppm' %  gas_tar)
    return corrected_data


def limit_to_active_points(df, reference='SO2', minimum_value=10):
    """ Only consider values where reference Gas is above some
    minimal value

    Inputs
    ------
    df : a pandas DataFrame object
        df contains the data
    
    """
    return df.where(df[reference] > minimum_value).dropna()

def estimate_slope(df, gas_tar, gas_ref, plot_scatter=True):
    """ estimate the slope (mean ratio) between two gas
    
    performs a simple linear regression:
    
    Inputs
    ------
    df : a pandas DataFrame object
        df contains the data
    gas_tar : str
        the name of the target gas (e.g 'CO2')
    gas_ref : str
        the name of the reference gas (e.g 'SO2')
    """
    
    slope, intercept, r, p, stderr = linregress(df[gas_ref],
                                                df[gas_tar])
    ratio_gas = df[gas_tar]/df[gas_ref]
    median_value = np.median(ratio_gas)
    mean_value = np.mean(ratio_gas)
    print "ratio %s / %s is %1.2f in linreg" % (gas_tar, gas_ref, slope)
    print "ratio %s / %s is %1.2f in average" % (gas_tar, gas_ref, mean_value)
    print "ratio %s / %s is %1.2f in median" % (gas_tar, gas_ref, median_value)
    if plot_scatter:
        # Now if you don't want to infer
        plt.figure(figsize=(12,8))
        ax1 = plt.subplot(2,1,1)
        df.plot.scatter(x=gas_ref, y=gas_tar, ax=ax1)
        ref_x = np.arange(0, df[gas_ref].max(),df[gas_ref].max()/10)
        p1 = plt.plot(ref_x, slope * ref_x, 'r', linewidth=3.0)
        p2 = plt.plot(ref_x, median_value * ref_x, 'g', linewidth=3.0)
        p3 = plt.plot(ref_x, mean_value * ref_x, 'c', linewidth=3.0)
        plt.legend(['linreg','median','mean','data'])
        plt.subplot(2,1,2)
        # TODO plot value histogram
        ratio_gas.plot.hist(100)
        plt.title('Histogram of Ratio values')
    return slope, median_value, mean_value


def add_ratio(df, gas_tar, gas_ref, plot_result=True):
    """ add the ratio between two gases as a new column
    
    Inputs
    ------
    df : a pandas DataFrame object
        df contains the data
    gas_tar : str
        the name of the target gas (e.g 'CO2')
    gas_ref : str
        the name of the reference gas (e.g 'SO2')
    """
    new_df = df.copy()
    new_column_name= '%s/%s'%(gas_tar, gas_ref)
    new_df[new_column_name] = pad.Series(df[gas_tar] / df[gas_ref],
           index=df.index)
    if plot_result:
        plt.figure(figsize=(12,8))
        new_df[new_column_name].plot()
        plt.ylabel(new_column_name)
    return new_df


def plot_acorr(dfcol, maxlags, newfig=False, index=None):
    """ plot the autocorrelation function """
    if newfig:
        plt.figure(figsize=(12,8))
    bins, values,_,_ = plt.acorr(dfcol - dfcol.mean(), maxlags=maxlags, usevlines=False)    
    plt.xlim([0, bins[-1]])
    plt.grid()
    if index is not None:
        xticks = plt.gca().get_xticks()
        plt.gca().set_xticklabels([str(index[t]) for t in xticks])


def harmo_analysis(df, gas_tar, gas_ref, maxlags=1000):
    # TO be continued
    new_column_name= '%s/%s'%(gas_tar, gas_ref)
    plt.figure(figsize=(12,8))
    plt.subplot(211)                                     
    plot_acorr(df[new_column_name], maxlags, index=df.index)

    # ok now cwt
    from scipy import signal
    import numpy as np
    L=512
    widths = np.arange(1, L)
    cwtmatr = signal.cwt(df[new_column_name], signal.ricker, widths)
    plt.subplot(212)
    plt.imshow(abs(cwtmatr), extent=[-1, 1, 1, L], cmap='jet', aspect='auto',
                vmax=abs(cwtmatr).max(), vmin=0)

def ultimate_plot(df, gas_tar, gas_ref):
    ratio_column_name= '%s/%s'%(gas_tar, gas_ref)
    plt.figure(figsize=(12,8))
    plt.subplot(211)
    df[ratio_column_name].plot(ax=plt.gca())
    plt.legend([ratio_column_name])
    plt.subplot(212)
    df[[gas_tar, gas_ref]].plot(ax=plt.gca())
    plt.ylabel('ppm')