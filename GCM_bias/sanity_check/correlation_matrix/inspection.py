#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  5 13:42:47 2026

@author: u1301408
"""

import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/tool_belt/')
from file_traversing import write2file, read_file

sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/GCM_bias/sanity_check/correlation_matrix/')
from seasonal_matrix import mk_df

test = mk_df(['pr', 'tasmin', 'tasmax'], 'JJA', 'ssp585')

x = 'tasmax bias'
y = 'projected precip'
plt.scatter(test[x], test[y]/100)

m, b = np.polyfit(test[x], test[y]/100, 1)
plt.plot(test[x], m*test[x]+b, '-', color  = 'red')

plt.xlabel(x)
plt.ylabel(y)


#%%
bias = sm.add_constant(test['pr bias'])
results = sm.OLS(test['projected precip'], bias).fit()
# print(results.summary())

residuals = results.resid
exog = results.model.exog

bp_test = het_breuschpagan(residuals, exog)

