#!/usr/bin/python3
# -*- coding: utf-8 -*-


"""
piper1.py

Description:


User-defined functions: None
Non-standard modules: None

Procedure:

    
Input: 
Output: 

Usage: piper1.py ...

Version: 1.00
Date: 2026-02-28
Author: Lea Rachel Rieskamp

"""


# Imports:

import sys
import pandas as pd
from pathlib import Path


# Storing Paths of arguments in variables:
    
qdat = pd.read_csv(Path(sys.argv[1])) # questionnaire data
pdat = pd.read_table(Path(sys.argv[2]), encoding='unicode_escape') # pharmacy data
hdat = pd.read_table(Path(sys.argv[3]), encoding='unicode_escape', low_memory=False) # hospital data
vdat = pd.read_table(Path(sys.argv[4]), encoding='unicode_escape', low_memory=False) # visits data

print(hdat)
print (hdat[0:1])
print(hdat["FLAND"])


# Input file checks
# ...
    

# Combine data to one table




