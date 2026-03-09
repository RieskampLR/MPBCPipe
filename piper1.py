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

  
qdat = pd.read_csv(Path(sys.argv[1]), sep="\t") # questionnaire data
pdat = pd.read_table(Path(sys.argv[2]), encoding='unicode_escape') # pharmacy data
hdat = pd.read_table(Path(sys.argv[3]), encoding='unicode_escape', low_memory=False) # hospital data
vdat = pd.read_table(Path(sys.argv[4]), encoding='unicode_escape', low_memory=False) # visits data
json_file_cats = Path(sys.argv[5]) # json file for user's coloumn selections
json_file_conds = Path(sys.argv[6])
"""

qdat = pd.read_table(Path("C:/Users/admin/OneDrive/Dokumente/UniLund/Thesis/dats/qdat_anonymised.tsv"))
pdat = pd.read_table(Path("C:/Users/admin/OneDrive/Dokumente/UniLund/Thesis/dats/pdat_anonymised.tsv"), encoding='unicode_escape')
hdat = pd.read_table(Path("C:/Users/admin/OneDrive/Dokumente/UniLund/Thesis/dats/hdat_anonymised.tsv"), encoding='unicode_escape', low_memory=False)
vdat = pd.read_table(Path("C:/Users/admin/OneDrive/Dokumente/UniLund/Thesis/dats/vdat_anonymised.tsv"), encoding='unicode_escape', low_memory=False)
json_file_cats = Path("C:/Users/admin/OneDrive/Dokumente/UniLund/Thesis/dats/json_file_2.json")
json_file_conds = Path("C:/Users/admin/OneDrive/Dokumente/UniLund/Thesis/dats/json_file_conds.json")
"""

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

id_selection = {}

for table in tables:
    filters = cond[table]
    ids = tables[table]
    for col, val in filters.items():
        if val["type"] == "range":
            ids = ids[ids[col].between(*val["values"])]
        elif val["type"] == "string":
            ids = ids[ids[col].astype(str).isin(val["values"])]
        else:
            ids = ids[ids[col].isin(val["values"])]
    id_selection[table] = ids["StudieID"]

print(id_selection)

# IDs must match ALL conditions
common_ids = set.intersection(*(set(ids) for ids in id_selection.values()))
print(common_ids)

# collect info on chosen IDs from other tables

#print(pdat["StudieID"].isin(common_ids))
#print(pdat.loc[pdat["StudieID"].isin(common_ids), "StudieID"])



result = {}

for table, cols in categories.items():
    df = tables[table]
    result[table] = df[df["StudieID"].isin(common_ids)][["StudieID"] + [c for c in cols if c != "StudieID"]]

print(result)
for table, df in result.items():
    print(table, len(df["StudieID"].unique()))



# merge to one table for neat output

thetable = result["pdat"].merge(result["hdat"], on="StudieID", how="outer") \
                        .merge(result["vdat"], on="StudieID", how="outer") \
                        .merge(result["qdat"], on="StudieID", how="outer")
# nan for qdat vals where no entries in qdat for IDs that are present in pdat


#print(thetable)

thetable.to_csv("filtered_table.csv", sep='\t', index=False, index_label=None, na_rep='NA')


# just to be able to open and check in spyder
print(thetable.head(100))




