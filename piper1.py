#!/usr/bin/python3
# -*- coding: utf-8 -*-


"""
piper1.py

Description:

Additional info/columns provided:
    qdat:
        Doctoral_diagnoses_at_inclusion_+-1year
        Doctoral_diagnoses_recorded_till_inclusion_+1year
        Doctoral_diagnoses_received_after_inclusion_year

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
from pathlib import Path
import json
import pandas as pd
import numpy as np


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
  

# Formatting and additional coloumns prep

qdat = qdat.rename(columns={"Id": "StudieID"})


# Participants with diagnosis at inclusion +-1

# IDs where INDATUMA == Inclusion_Year +- 1
year = qdat.set_index("StudieID")["Inclusion_Year"].astype(int)

ids_atInc = pd.concat([
    hdat.loc[(hdat["INDATUMA"].astype(str).str[:4].astype(int) - hdat["StudieID"].map(year)).abs() <= 1, "StudieID"],
    vdat.loc[(vdat["INDATUMA"].astype(str).str[:4].astype(int) - vdat["StudieID"].map(year)).abs() <= 1, "StudieID"]
]).unique()


ids_tillInc = pd.concat([
    hdat.loc[hdat["INDATUMA"].astype(str).str[:4].astype(int) <= hdat["StudieID"].map(year) + 1, "StudieID"],
    vdat.loc[vdat["INDATUMA"].astype(str).str[:4].astype(int) <= vdat["StudieID"].map(year) + 1, "StudieID"]
]).unique()
# Includes diagnoses recorded at inclusion and inclusion + 1 year


ids_afterInc = pd.concat([
    hdat.loc[hdat["INDATUMA"].astype(str).str[:4].astype(int) > hdat["StudieID"].map(year), "StudieID"],
    vdat.loc[vdat["INDATUMA"].astype(str).str[:4].astype(int) > vdat["StudieID"].map(year), "StudieID"]
]).unique()
ids_afterInc = np.setdiff1d(ids_afterInc, ids_tillInc)



col_names = ["Doctoral_diagnoses_received_after_inclusion_year", "Doctoral_diagnoses_at_inclusion_+-1year", "Doctoral_diagnoses_recorded_till_inclusion_+1year"]
counter = 0

for ids in [ids_atInc, ids_tillInc, ids_afterInc]:

    # get diagnoses for these
    cols = ["StudieID"] + ["hdia"] + [c for c in hdat.columns if c.startswith("DIA") and c!= "DIA_ANT"]
    doc_combined = pd.concat([hdat, vdat], ignore_index=True)
    result = doc_combined.loc[doc_combined["StudieID"].isin(ids), cols]
    
    # To 1 coloumn
    col_name = col_names[counter]
    counter = counter + 1
    result[col_name] = (
        result.drop(columns="StudieID").fillna("").astype(str).agg(",".join, axis=1)
        .str.replace(r"(,+)", ",", regex=True).str.strip(","))
    result = result[["StudieID", col_name]]
    
    # Each patient once (diagnoses fused)
    result = result.groupby("StudieID", as_index=False).agg({col_name: ",".join})
    
    for i, entry in enumerate(result [col_name]):
        diagnoses = entry.split(",")
        cut = set(diagnoses)
        result.at[i, col_name] = ",".join(sorted(cut)) # replace entry
    
    # Add to qdat table
    qdat = qdat.merge(result, on="StudieID", how="left")
    #qdat = pd.concat([qdat.iloc[:, :5], result.drop(columns="StudieID"), qdat.iloc[:, 5:]], axis=1) # move column to 6th position
    qdat.insert(5 + counter - 1, col_name, qdat.pop(col_name))


qdat = qdat.copy() # removes saved memory of column movement

#diff_entries = qdat[qdat.iloc[:, 5] != qdat.iloc[:, 6]]



# -----------------------------------------------------------------------------


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




