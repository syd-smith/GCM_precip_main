#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 10 12:59:57 2025

@author: u1301408
"""

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/strong-group7/sydney/data_analysis/packages')
import base_packages as bp

# The desired covariance matrix.
cov = bp.np.array(
       [[1,  0.8, 0.6, 0.4, 0.2],
       [0.8, 1.2, 0.8, 0.6, 0.4],
       [0.6, 0.8, 0.8, 0.8, 0.6],
       [0.4, 0.6, 0.8, 1.4, 0.8],
       [0.2, 0.4, 0.6, 0.8, 0.6]]
)

# Generate the random samples.
rng = bp.np.random.default_rng(313)
data = rng.multivariate_normal(bp.np.zeros(5), cov, size=100)
print(data.shape)

observations =  data[:, 0]
simulations =  {"LSTM": data[:, 1],
            "CNN": data[:, 2],
            "TCN": data[:, 3],
            "CNN-LSTM": data[:, 4]}
taylor = bp.taylor_plot(observations=observations,
            simulations=simulations,
            title="Taylor Plot")