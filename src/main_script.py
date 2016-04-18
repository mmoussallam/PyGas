# -*- coding: utf-8 -*-
"""
Created on Sat Mar 05 14:09:11 2016

@author: Manu
"""

import os

# All necessary methods are in the following utility module
import multigas_analysis_tools as multools

# NOW we need the path to your data
inputfiledir = 'C:\Users\Manu\workspace\PyGas\datas'
csvname = 'Sabancaya_For_Python-Script.csv'
filepath = os.path.join(inputfiledir, csvname)

# Thus function will read the csv and return a pandas DataFrame object
raw_data = multools.get_raw_data(filepath)
# the Dataframe object is very handy: try the following command:
# raw_data.info()
# raw_data.Tair.plot()
# raw_data.plot(x='SO2', y='CO2')

# Now let's manipulate the data a little
# Select a Pair of gas
gas_ref = 'SO2' # SO2 is the reference
gas_tar = 'CO2' # CO2 is the target: we will be interested in the CO2/SO2 ratio

# First we correct the gas value for atmospheric constant
corrected_data = multools.correct_for_atmo(raw_data, gas_tar, gas_ref,
                                           plot_result=True)
# CO2_offset not negative
# TODO remove trend

# Now limit the analysis to points where the reference gas is actually measured
resized_data = multools.limit_to_active_points(corrected_data,
                                               minimum_value=5)
# ALTERNATE METHOD IF YOU KNOW BOUNDARIES OR WANT To Set by hand:
#Tstart=500;Tstop=2500
#resized_data = corrected_data[2694:5770]

# Now start real work: estimate slope and build the scatter plot
# to visually validate the model
linreg, median_value, mean_value = multools.estimate_slope(resized_data, gas_tar, gas_ref,
                                     plot_scatter=True)
                                 
# Now plot the evolution of the ratio 
data_with_ratio = multools.add_ratio(resized_data, gas_tar, gas_ref,
                                       plot_result=True)


# Finally perform harmonic analysis to find periodicity
multools.harmo_analysis(data_with_ratio, gas_tar, gas_ref)