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
#ids = tables["qdat"].loc[tables["qdat"][cond["qdat"]["column"]] == cond["qdat"]["value"], "StudieID"]

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
    result[table] = df[df["StudieID"].isin(ids)][["StudieID"] + cols]

print(result)

# merge to one table for neat output






'''
# old-ish

# Coloumns user-requested

# Which cols to even include in thetable

with open(json_file, "r") as json_file:
    categories = json.load(json_file)

print(categories)

# get each data sets headers to lists
for name, values in categories.items():
    globals()[name] = values


pdat = pdat[pdat_cats]

thetable = pdat.merge(qdat[qdat_cats], on="StudieID", how="left")


'''

    

''' old

# Empty table
thetable = pd.DataFrame(columns=pd.MultiIndex.from_tuples([(k, v) for k, vals in categories.items() for v in vals]))

# Fill table with data from loaded pandas tables
    
for name, cols in categories.items():
    for col in cols:
        thetable[(name, col)] = globals()[name][col].values

other old:

# categories is a dictionary looking like:
# {"comorbidities": ["Diabetes", "Epilepsy", "VascularD", "Depression"],
#  "diagnosis info": ["main", "main_date", "parkinsons", "age_at_diagnosis"]}





# List of diagnoses present in data sets

diagnoses = []
for col in hdat.loc[:,"DIA1":]:     # loops over dia coloumns
    for dia in hdat[col]:           # loops over the current column entries
        if not pd.isna(dia):        # excludes empty entries
            if dia not in diagnoses:
                diagnoses.append(dia)
#print(diagnoses)




# Combine data to one table

thetable = 

'''



