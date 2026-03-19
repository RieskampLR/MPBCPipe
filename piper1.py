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
import argparse
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
json_file_conds = Path("C:/Users/admin/OneDrive/Dokumente/UniLund/Thesis/dats/json_file_conds_2.json")
"""

# Input file checks
# ...
  

# Formatting and additional coloumns prep

qdat = qdat.rename(columns={"Id": "StudieID"})

hvdat = pd.concat([hdat, vdat], ignore_index=True, join="outer")
hvdat["UTDATUMA"] = hvdat["UTDATUMA"].astype("Int64")


# qdat.insert(4, "Inclusion_Year", qdat.pop("Inclusion_Year"))


# get json file contents
# chosen cats/headers
with open(json_file_cats, "r") as json_file:
    categories = json.load(json_file)
# chosen conditions
with open(json_file_conds) as json_file:
    cond = json.load(json_file)


#------------------------------------------------------------------------------

# Additional info coloumns

# Diagnosis time vs inclusion time

col_names = ["Doctoral_diagnoses_received_after_inclusion_year", "Doctoral_diagnoses_at_inclusion_+-1year", "Doctoral_diagnoses_recorded_till_inclusion_+1year"]

if any(col in categories["qdat"] or col in cond["qdat"] for col in col_names):

    # Participants with diagnosis at inclusion +-1
    
    year = qdat.set_index("StudieID")["Inclusion_Year"].astype(int)
    
    # IDs where INDATUMA ==, <=, or > Inclusion_Year +- 1
    
    ids_atInc = pd.concat([
        hvdat.loc[(hvdat["INDATUMA"].astype(str).str[:4].astype(int) - hvdat["StudieID"].map(year)).abs() <= 1, "StudieID"]
    ]).unique()
    
    
    ids_tillInc = pd.concat([
        hvdat.loc[hvdat["INDATUMA"].astype(str).str[:4].astype(int) <= hvdat["StudieID"].map(year) + 1, "StudieID"]
    ]).unique()
    # Includes diagnoses recorded at inclusion and inclusion + 1 year
    
    
    ids_afterInc = pd.concat([
        hvdat.loc[hvdat["INDATUMA"].astype(str).str[:4].astype(int) > hvdat["StudieID"].map(year), "StudieID"]
    ]).unique()
    ids_afterInc = np.setdiff1d(ids_afterInc, ids_tillInc)
    
    
    counter = 0
    
    for ids in [ids_afterInc, ids_atInc, ids_tillInc]:
    
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
    
    # Controls that received a diagnosis starting with G
    # ids = qdat.loc[(qdat["Control"] == 1) & qdat.iloc[:, 5:8].astype(str).stack().str.contains(r"\bG", na=False).groupby(level=0).any(), "StudieID"]
    # sub_qdat = qdat[qdat["StudieID"].isin(ids)]


# -----------------------------------------------------------------------------

# Filtering for user-defined conditions


# tables dic
tables = {
    "qdat": qdat,
    "pdat": pdat,
    "hvdat": hvdat
}

cat_tables = {
    "qdat": qdat,
    "pdat": pdat,
    "hdat": hdat,
    "vdat": vdat
}





# filter IDs by condition based on json file

id_selection = {}

for table in tables:
    filters = cond[table]
    ids = tables[table]
    for col, val in filters.items():
        if val["type"] == "range":
            if val["values"][0] == ">=":
                ids = ids[ids[col] >= val["values"][1]]
            elif val["values"][0] == "<=":
                ids = ids[ids[col] <= val["values"][1]]
            else:
                ids = ids[ids[col].between(*val["values"])]
        elif val["type"] == "string":
            if val["values"] == ["any"]:
                ids = ids[ids[col].notna()]
            else:
                ids = ids[ids[col].astype(str).isin(val["values"])]
        else:
            ids = ids[ids[col].isin(val["values"])]
    id_selection[table] = ids["StudieID"]

# print(id_selection)

# IDs must match ALL conditions

common_ids = set.intersection(*(set(ids) for ids in id_selection.values()))
# print(common_ids)


#print(pdat["StudieID"].isin(common_ids))
#print(pdat.loc[pdat["StudieID"].isin(common_ids), "StudieID"])


# -----------------------------------------------------------------------------

# Filtering for user-defined output table categories

# collect info on chosen IDs from other tables

result = {}

for table, cols in categories.items():
    df = cat_tables[table]
    result[table] = df[df["StudieID"].isin(common_ids)][["StudieID"] + [c for c in cols if c != "StudieID"]]

# print(result)
# for table, df in result.items():
  #   print(table, len(df["StudieID"].unique()))



# merge to one table for neat output

thetable = result["pdat"].merge(result["hdat"], on="StudieID", how="outer") \
                        .merge(result["vdat"], on="StudieID", how="outer") \
                        .merge(result["qdat"], on="StudieID", how="outer")
# nan for qdat vals where no entries in qdat for IDs that are present in pdat


# Sort output-table flag

# Set up argument parser
#sort_flag = argparse.ArgumentParser(description="Specify columns to sort by")
#sort_flag.add_argument("-s", "--sort", type=str, nargs="+", help="Column to sort by")
#args = sort_flag.parse_args() # reads all arguments from command line in
#sort_cols = args.sort  # variable (list) for the sort argument string


# sort format thetable

sort_cols = ["Age_Diagnosis", "StudieID"]

thetable = thetable.sort_values(by=sort_cols)

# thetable = thetable.drop_duplicates()


#print(thetable)

thetable.to_csv("C:/Users/admin/OneDrive/Dokumente/UniLund/Thesis/dats/filtered_table.csv",
                sep='\t', index=False, index_label=None, na_rep='NA')


# just to be able to open and check in spyder
# print(thetable.head(100))




