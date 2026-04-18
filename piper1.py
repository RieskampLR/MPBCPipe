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

from pathlib import Path
import argparse
import json
import pandas as pd
import numpy as np
import warnings

from dia_vs_incl import diagnosis_vs_inclusion_time_func
from id_selec import id_selection_func
from pharma_table import pharma_table_func
from diagnosis_table import diagnosis_table_func


# Storing Paths of arguments in variables:

warnings.simplefilter("ignore", category=pd.errors.PerformanceWarning)

'''
# Set up argument parser
parser = argparse.ArgumentParser(description="Specify input files and optionally: Columns to sort by and other summary tables")
parser.add_argument("qdat")
parser.add_argument("pdat")
parser.add_argument("hdat")
parser.add_argument("vdat")
parser.add_argument("json_file_cats")
parser.add_argument("json_file_conds")
parser.add_argument("-s", "--sort", type=str, nargs="+", help="Column to sort by")
parser.add_argument("-p", "--pharma", action="store_true", help="Pharma pick ups summary")
parser.add_argument("-d", "--diagnosis", action="store_true", help="Diagnosis cases summary")
args = parser.parse_args()

qdat = pd.read_csv(Path(args.qdat), sep="\t")
pdat = pd.read_table(Path(args.pdat), encoding='unicode_escape')
hdat = pd.read_table(Path(args.hdat), encoding='unicode_escape', low_memory=False)
vdat = pd.read_table(Path(args.vdat), encoding='unicode_escape', low_memory=False)
json_file_cats = Path(args.json_file_cats)
json_file_conds = Path(args.json_file_conds)


if args.sort is not None:
    sort_cols = list(args.sort)
else:
    sort_cols = []

'''


qdat = pd.read_table(Path("C:/Users/admin/OneDrive/Dokumente/UniLund/Thesis/dats/qdat_anonymised.tsv"))
pdat = pd.read_table(Path("C:/Users/admin/OneDrive/Dokumente/UniLund/Thesis/dats/pdat_anonymised.tsv"), encoding='unicode_escape')
hdat = pd.read_table(Path("C:/Users/admin/OneDrive/Dokumente/UniLund/Thesis/dats/hdat_anonymised.tsv"), encoding='unicode_escape', low_memory=False)
vdat = pd.read_table(Path("C:/Users/admin/OneDrive/Dokumente/UniLund/Thesis/dats/vdat_anonymised.tsv"), encoding='unicode_escape', low_memory=False)
json_file_cats = Path("C:/Users/admin/OneDrive/Dokumente/UniLund/Thesis/dats/json_file_cats_3.json")
json_file_conds = Path("C:/Users/admin/OneDrive/Dokumente/UniLund/Thesis/dats/json_file_conds_3.json")


# Input file checks
# ...
  

# Formatting and additional coloumns prep

qdat = qdat.rename(columns={"Id": "StudieID"})

hvdat = pd.concat([hdat, vdat], ignore_index=True, join="outer")
hvdat["UTDATUMA"] = hvdat["UTDATUMA"].astype("Int64")


# qdat.insert(4, "Inclusion_Year", qdat.pop("Inclusion_Year"))


# Get json file contents

# chosen cats/headers
with open(json_file_cats, "r") as json_file:
    categories = json.load(json_file)
# chosen conditions
with open(json_file_conds) as json_file:
    cond = json.load(json_file)



# Variable and data dics for functions

func_dats = {
    "qdat": qdat,
    "hvdat": hvdat,
    "hdat": hdat,
    "vdat": vdat,
    "pdat": pdat,
    "categories": categories,
    "cond": cond
}

# tables dic
tables = {
    "qdat": qdat,
    "pdat": pdat,
    "hvdat": hvdat
}


#------------------------------------------------------------------------------
# Additional info coloumns generation
#------------------------------------------------------------------------------

# Diagnosis time vs inclusion time

col_names = ["Doctoral_diagnoses_received_after_inclusion_year", "Doctoral_diagnoses_at_inclusion_+-1year", "Doctoral_diagnoses_recorded_till_inclusion_+1year"]

qdat = diagnosis_vs_inclusion_time_func(func_dats, col_names)

# cat tables dic
cat_tables = {
    "qdat": qdat,
    "pdat": pdat,
    "hdat": hdat,
    "vdat": vdat
}

# -----------------------------------------------------------------------------
# Filtering for user-defined conditions
#------------------------------------------------------------------------------



# filter IDs by condition based on json file

common_ids = id_selection_func(tables, cat_tables, cond)


#print(pdat["StudieID"].isin(common_ids))
#print(pdat.loc[pdat["StudieID"].isin(common_ids), "StudieID"])


# -----------------------------------------------------------------------------
# Output table generation and formatting
#------------------------------------------------------------------------------

# Filtering for user-defined output table categories

# collect info on chosen IDs from other tables

result = {}

for table, cols in categories.items():
    df = cat_tables[table]
    filtered = df[df["StudieID"].isin(common_ids)]
    selected_cols = ["StudieID"] + [c for c in cols if c != "StudieID"]
    result[table] = filtered[selected_cols]


# print(result)
# for table, df in result.items():
  #   print(table, len(df["StudieID"].unique()))



# merge to one table for neat output

# Convert all columns except StudieID to string and fill NaN
for tbl in ["pdat", "hdat", "vdat", "qdat"]:
    df = result[tbl]
    for col in df.columns:
        if col != "StudieID":
            df[col] = df[col].fillna("").astype(str)
    result[tbl] = df

# Then aggregate by StudieID
pdat_agg = result["pdat"].groupby("StudieID", as_index=False).agg(",".join)
hdat_agg = result["hdat"].groupby("StudieID", as_index=False).agg(",".join)
vdat_agg = result["vdat"].groupby("StudieID", as_index=False).agg(",".join)
qdat_agg = result["qdat"].groupby("StudieID", as_index=False).agg(",".join)

thetable = pdat_agg.merge(hdat_agg, on="StudieID", how="outer") \
                   .merge(vdat_agg, on="StudieID", how="outer") \
                   .merge(qdat_agg, on="StudieID", how="outer")

# nan for qdat vals where no entries in qdat for IDs that are present in pdat

# Remove duplicates in fields

for col in thetable.columns:
    new_val = []
    for val in thetable[col]:
        if pd.isna(val):
            new_val.append(val)
        else:
            items = str(val).split(",")
            unique_items = sorted(set(items))
            new_val.append(",".join(unique_items))
    thetable[col] = new_val



#------------------------------------------------------------------------------
# Pharma table generation
#------------------------------------------------------------------------------

# by pharma product pick up


if args.pharma:
    pharma_summary = pharma_table_func(func_dats, common_ids)
    pharma_summary.to_csv("C:/Users/admin/OneDrive/Dokumente/UniLund/Thesis/dats/pharma_summary_table.csv",
                    sep='\t', index=False, index_label=None, na_rep='NA')
    pharma_summary.to_excel("C:/Users/admin/OneDrive/Dokumente/UniLund/Thesis/dats/pharma_summary_table.xlsx", index_label=None, na_rep='NA')


#------------------------------------------------------------------------------
# Diagnosis table generation
#------------------------------------------------------------------------------

if args.diagnosis:
    diagnosis_summary = diagnosis_table_func(func_dats, common_ids)
    diagnosis_summary.to_csv("C:/Users/admin/OneDrive/Dokumente/UniLund/Thesis/dats/diagnosis_summary_table.csv",
                    sep='\t', index=False, index_label=None, na_rep='NA')
    diagnosis_summary.to_excel("C:/Users/admin/OneDrive/Dokumente/UniLund/Thesis/dats/diagnosis_summary_table.xlsx", index_label=None, na_rep='NA')




#------------------------------------------------------------------------------
# Optional table transformations
#------------------------------------------------------------------------------

# sort format thetable

#sort_cols = ["Age_Diagnosis", "StudieID"]

if len(sort_cols) > 0:
    thetable = thetable.sort_values(by=sort_cols)


# thetable = thetable.drop_duplicates() # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Currently for easy look at and speed


#print(thetable)

thetable.to_csv("C:/Users/admin/OneDrive/Dokumente/UniLund/Thesis/dats/filtered_table.csv",
                sep='\t', index=False, index_label=None, na_rep='NA')
thetable.to_excel("C:/Users/admin/OneDrive/Dokumente/UniLund/Thesis/dats/filtered_table.xlsx", index_label=None, na_rep='NA')

# just to be able to open and check in spyder:
# print(thetable.head(100))




