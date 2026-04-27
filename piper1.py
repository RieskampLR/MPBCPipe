#!/usr/bin/python3
# -*- coding: utf-8 -*-


"""
piper1.py

Description:
    dias before/at/after inclusion year in qdat currently refer to hdia!
    For details on any diagnosis refer to the additionally generated diagnosis table

Additional info/columns provided:
    qdat:
        Doctoral_diagnoses_at_inclusion_+-1year
        Doctoral_diagnoses_recorded_till_inclusion_+1year
        Doctoral_diagnoses_received_after_inclusion_year
    hvdat:
        all_diagnoses

Hard-code conditions:
- Header entries / short codes have to be named the same in any new data collection files

User-defined functions: None
Non-standard modules: None

Procedure:
    !Files have to be converted to tsv using the provided script csv_to_tsv to be applicable to this pipeline!

    
Input: 
Output: 

Usage: python piper1.py qdat_anonymised.tsv pdat_anonymised.tsv hdat_anonymised.tsv vdat_anonymised.tsv json_file_cats_3.json json_file_conds_3.json

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

from all_dias_col import  all_diagnoses_func
from dia_vs_incl import diagnosis_vs_inclusion_time_func
from id_selec import id_selection_func
from pharma_table import pharma_table_func
from diagnosis_table import diagnosis_table_func
from thetable import thetable_func


# Storing Paths of arguments in variables:

warnings.simplefilter("ignore", category=pd.errors.PerformanceWarning)


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

'''
# Input file checks
# ...
  

# Formatting and additional coloumns prep

qdat = qdat.rename(columns={"Id": "StudieID"})

hvdat = pd.concat([hdat, vdat], ignore_index=True, join="outer")
hvdat["UTDATUMA"] = hvdat["UTDATUMA"].astype("Int64")



# Get json file contents

# chosen cats/headers
with open(json_file_cats, "r") as json_file:
    categories = json.load(json_file)
# chosen conditions
with open(json_file_conds) as json_file:
    cond = json.load(json_file)




# List of cols containing diagnosis info
dia_cols = ["hdia"] + [f"DIA{i}" for i in range(1, 31)]

# Turning all Dia entries to simple strings cause the entry formats ARE A MESS
hvdat[dia_cols] = hvdat[dia_cols].apply(lambda col: col.map(str))


# Variable and data dics for functions and other

func_dats = {
    "qdat": qdat,
    "hvdat": hvdat,
    "hdat": hdat,
    "vdat": vdat,
    "pdat": pdat,
    "categories": categories,
    "cond": cond
}

#------------------------------------------------------------------------------
# Additional info coloumns generation
#------------------------------------------------------------------------------

# All Diagnoses listed in 1 col (All listed diagnoses at that visit)

hvdat = all_diagnoses_func(func_dats, dia_cols)
hvdat[dia_cols] = hvdat[dia_cols].replace("nan", np.nan)


# Update func dats entry
func_dats["hvdat"] = hvdat


# Diagnosis time vs inclusion time

qdat = diagnosis_vs_inclusion_time_func(func_dats)

# Update func dats entry
func_dats["qdat"] = qdat


# More variable and data dics for functions and other

# cat tables dic
cat_tables = {
    "qdat": qdat,
    "pdat": pdat,
    "hvdat": hvdat
}

# tables dic
tables = {
    "qdat": qdat,
    "pdat": pdat,
    "hvdat": hvdat
}

# -----------------------------------------------------------------------------
# Filtering for user-defined conditions
#------------------------------------------------------------------------------


# filter IDs by condition based on json file

common_ids = id_selection_func(tables, cond)

df_hdia = hvdat.loc[hvdat["StudieID"].isin(common_ids), ["StudieID", "hdia"]]
#print(df_hdia)

# -----------------------------------------------------------------------------
# Output table generation and formatting
#------------------------------------------------------------------------------

thetable = thetable_func(func_dats, cat_tables, common_ids)


#------------------------------------------------------------------------------
# Optional table transformations
#------------------------------------------------------------------------------

# sort format thetable

#sort_cols = ["Age_Diagnosis", "StudieID"] # Spyder version

if len(sort_cols) > 0:
    thetable = thetable.sort_values(by=sort_cols)


thetable.to_csv("filtered_table.tsv",
                sep='\t', index=False, index_label=None, na_rep='NA')
thetable.to_excel("filtered_table.xlsx", index=False, na_rep='NA')


#------------------------------------------------------------------------------
# Pharma table generation
#------------------------------------------------------------------------------

# by pharma product pick up

if args.pharma:
    pharma_summary = pharma_table_func(func_dats, common_ids)
    pharma_summary.to_csv("pharma_summary_table.tsv",
                    sep='\t', index=False, index_label=None, na_rep='NA')
    pharma_summary.to_excel("pharma_summary_table.xlsx", index=False, na_rep='NA')


#------------------------------------------------------------------------------
# Diagnosis table generation
#------------------------------------------------------------------------------

if args.diagnosis:
    diagnosis_summary = diagnosis_table_func(func_dats, common_ids, dia_cols)
    diagnosis_summary.to_csv("diagnosis_summary_table.tsv",
                    sep='\t', index=False, index_label=None, na_rep='NA')
    diagnosis_summary.to_excel("diagnosis_summary_table.xlsx", index=False, na_rep='NA')





