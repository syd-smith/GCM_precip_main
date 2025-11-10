#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  9 21:32:43 2025

@author: u1301408
"""

# learn how to read GCM data out of matlab files
# make taylor plot repeatable for different variables


# dimensions for MACA region
# lat      (lat) float32 672B 36.03 36.07 36.11 36.15 ... 42.9 42.94 42.98
# * lon      (lon) float32 684B -115.1 -115.1 -115.0 ... -108.1 -108.1 -108.0

# PolarAxes.PolarTransform() # this tells plot to set std for radius and cor for angle
# diagram = TaylorDiagram(reference.std(ddof=1), fig=myfig)
# diagram.add_sample(stddev2, corrcoef2, label = 'Model 2', marker = 'o')