# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 22:46:11 2016

@author: Manu
"""

import os
import os.path as op
import pandas as pd

import multigas_analysis_tools as multools

try:
    import seaborn
except:
    pass

# Replace with your local dir
#inputfiledir = 'C:\Users\Manu\workspace\PyGas\datas'
inputfiledir = '/Users/manumouss/workspace/PyGas/datas'
#inputfiledir = '/home/manu/workspace/PyGas/datas'

filename= '09_February_Villarrica.xlsx'
filepath = os.path.join(inputfiledir, filename)
df = pd.read_excel(filepath, 'Sheet1')
df = multools.get_raw_data_xls(filepath,   decimal_time_name='Decimal time')

multools.plot_acorr(df['Flux ton/day'], 500, newfig=True, index=df.index)



filename= '17_January_2016_Villarrica.xlsx'
filepath = os.path.join(inputfiledir, filename)

df = multools.get_raw_data_xls(filepath)
multools.plot_acorr(df['Temp'].dropna(), 5000, newfig=True, index=df.index)

