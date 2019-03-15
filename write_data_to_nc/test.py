#!/usr/bin/python3

'''
----------------------------------------------------
< verkleinert das Gebiet Europa und schneidet ein Viereck 
< um Niedersachsen aus.  

input: [1] File, das eingelesen wird
       [2] Name des Output-Files
       [3] Variable, die eingelesen werden soll
'''

from netCDF4 import Dataset
import numpy as np
import glob 
import matplotlib.pyplot as plt  
import sys
import numpy.ma as ma
import coord_trafo as ct

print(sys.path)
