# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 22:46:11 2016

@author: Manu
"""

import os
import os.path as op
import pandas as pd
import matplotlib.pyplot as plt
inputfiledir = 'C:\Users\Manu\workspace\PyGas\datas'
filename= '09_February_Villarrica.xlsx'
filepath = os.path.join(inputfiledir, filename)

	
df = pd.ExcelFile(filepath).parse('Sheet1')

plt.acorr(df['Flux ton/day'],maxlags=500, usevlines=False)


filename= '17_January_2016_Villarrica.xlsx'
filepath = os.path.join(inputfiledir, filename)

	
df = pd.ExcelFile(filepath).parse('Sheet1')

plt.acorr(df['Temp'].dropna(),maxlags=10000, usevlines=False)