#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  3 21:07:39 2022

@author: roy
"""

import os
os.environ['R_HOME'] = '/Library/Frameworks/R.framework/Resources'

import rpy2.robjects as robjects
robjects.r.setwd("/Users/roy/coding/PGT/DIA")

print(robjects.r.getwd())

robjects.r('f=3')
print(robjects.r('f'))