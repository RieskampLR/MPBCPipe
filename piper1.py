#!/usr/bin/python3
# -*- coding: utf-8 -*-


"""
piper1.py

Description:


Hard-code conditions:
- Header entries / short codes have to be named the same in any new data collection files

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
import json


# Storing Paths of arguments in variables:

"""    
qdat = pd.read_csv(Path(sys.argv[1])) # questionnaire data
pdat = pd.read_table(Path(sys.argv[2]), encoding='unicode_escape') # pharmacy data
hdat = pd.read_table(Path(sys.argv[3]), encoding='unicode_escape', low_memory=False) # hospital data
vdat = pd.read_table(Path(sys.argv[4]), encoding='unicode_escape', low_memory=False) # visits data
json_file = Path(sys.argv[5]) # json file for user's coloumn selections
"""

qdat = pd.read_table(Path("C:/Users/admin/OneDrive/Dokumente/UniLund/Thesis/dats/qdat_anonymised.tsv"))
pdat = pd.read_table(Path("C:/Users/admin/OneDrive/Dokumente/UniLund/Thesis/dats/pdat_anonymised.tsv"), encoding='unicode_escape')
hdat = pd.read_table(Path("C:/Users/admin/OneDrive/Dokumente/UniLund/Thesis/dats/hdat_anonymised.tsv"), encoding='unicode_escape', low_memory=False)
vdat = pd.read_table(Path("C:/Users/admin/OneDrive/Dokumente/UniLund/Thesis/dats/vdat_anonymised.tsv"), encoding='unicode_escape', low_memory=False)
json_file_cats = Path("C:/Users/admin/OneDrive/Dokumente/UniLund/Thesis/dats/json_file_2.json")
json_file_conds = Path("C:/Users/admin/OneDrive/Dokumente/UniLund/Thesis/dats/json_file_conds.json")


# Input file checks
# ...
  


qdat = qdat.rename(columns={"Id": "StudieID"})


# tables dic
tables = {
    "qdat": qdat,
    "pdat": pdat,
    "hdat": hdat,
    "vdat": vdat
}



# get json file contents
# chosen cats/headers
with open(json_file_cats, "r") as json_file:
    categories = json.load(json_file)
# chosen conditions
with open(json_file_conds) as json_file:
    cond = json.load(json_file)


# filter IDs by condition

filters = cond["qdat"]["filters"]

ids = tables["qdat"]
for col, val in filters.items():
    if len(val) == 2:  # range
        ids = ids[ids[col].between(*val)]
    else:            # list of allowed values
        ids = ids[ids[col].isin(val)]

ids = ids["StudieID"]



# collect info on chosen IDs from other tables
result = {}

for table, cols in categories.items():
    df = tables[table]
    result[table] = df[df["StudieID"].isin(ids)][cols].assign(StudieID=df["StudieID"])

print(result)



# merge to one table for neat output
thetable = result["pdat"].merge(result["qdat"], on="StudieID", how="outer")





