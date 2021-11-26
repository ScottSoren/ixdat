# -*- coding: utf-8 -*-
"""
Created on Fri Nov 26 15:02:23 2021

@author: scott
"""

from ixdat import Measurement



meas = Measurement.read(
    r"C:\Users\scott\Dropbox\ixdat_resources\test_data\gamryA02_2_CP_5minhold.DTA", 
    reader="gamry"
)

meas.plot()