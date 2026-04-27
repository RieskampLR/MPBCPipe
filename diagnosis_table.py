# -*- coding: utf-8 -*-
"""

Func for table of diagnoses overview and check

"""

import pandas as pd
import numpy as np


def diagnosis_table_func(func_dats, common_ids, dia_cols):
    hvdat = func_dats["hvdat"]
    qdat = func_dats["qdat"]
    
    
    id_to_dias = hvdat.melt(id_vars=["StudieID", "INDATUM"],        # sets identifier var
                             value_vars=dia_cols,      # cols to pivot by id_vars
                             value_name="diagnosis"     # new col name
                             ).dropna(subset=["diagnosis"])[["StudieID", "diagnosis", "INDATUM"]].drop_duplicates()
                            # drop nan's and duplicates
    
    # Filter for user-set conditions
    id_to_dias = id_to_dias[id_to_dias["StudieID"].isin(common_ids)]
    
    
    # groupby object for group in grouped func
    grouped = id_to_dias.groupby(["StudieID","diagnosis"])
    
    # Collect diagnosis cases info
    dias_info_rows = []
    for [stu_id, dia], group in grouped:
        dates = group["INDATUM"].tolist()   # all visit dates
        count = len(dates)               # number of this diagnosis received
        dias_info_rows.append([stu_id, dia, count] + dates)
    
    # To table format
    diagnosis_summary = pd.DataFrame(dias_info_rows)
    # Col headers
    diagnosis_summary.columns = ["StudieID", "diagnosis", "number_of_times_diagnosed"] + list(diagnosis_summary.columns[3:])
    
    # Time frame column
    # Get date col names
    diagnosis_cols = diagnosis_summary.columns.tolist()
    for i in range(3, len(diagnosis_summary.columns)):
        diagnosis_cols[i] = f'Date_{i-2}'
    # Add to table
    diagnosis_summary.columns = diagnosis_cols
    date_cols = diagnosis_summary.columns[3:]
    diagnosis_summary[date_cols] = diagnosis_summary[date_cols].apply(pd.to_datetime, errors='coerce')
    diagnosis_summary["min_date"] = diagnosis_summary[date_cols].min(axis=1)
    diagnosis_summary["max_date"] = diagnosis_summary[date_cols].max(axis=1)
    # Find min max and add
    for col in list(date_cols) + ["min_date", "max_date"]:
        diagnosis_summary[col] = diagnosis_summary[col].dt.strftime("%Y-%m-%d")
    diagnosis_summary.insert(3, "span", np.nan)
    # Add col for span and rm min max cols
    diagnosis_summary["span"] = diagnosis_summary["min_date"] + " - " + diagnosis_summary["max_date"]
    diagnosis_summary = diagnosis_summary.drop(columns=["min_date", "max_date"])
    
    # Add Inclusion_Year col
    qdat_cut = qdat[["StudieID", "Inclusion_Year"]].drop_duplicates()
    diagnosis_summary = diagnosis_summary.merge(qdat_cut, on="StudieID", how="left")
    

    # Phenoconv cols
    # PhenoG20 (from qdat)
    diagnosis_summary = diagnosis_summary.merge(qdat[["StudieID", "PHENO"]], on='StudieID', how='left').rename(columns={'PHENO': 'PhenoG20'})
    
    # Conversion
    half_condition = diagnosis_summary["diagnosis"].str.contains("G20", na=False)
    diagnosis_summary["G20_Conversion"] = np.where( # returns one val where a condition is true, another where it is false
        diagnosis_summary["PhenoG20"].isna(),       # condition: Is NA val
        np.nan,                                     # val if false: nan
        (diagnosis_summary["PhenoG20"] != 1) & half_condition | # val if true: boolean, 1 or 0
        (diagnosis_summary["PhenoG20"] != 1) & ~half_condition
    ).astype(int)

    

    
    # Move cols
    cols = diagnosis_summary.columns.tolist()
    cols.insert(1, cols.pop(cols.index("Inclusion_Year")))
    cols.insert(3, cols.pop(cols.index("PhenoG20")))
    cols.insert(4, cols.pop(cols.index("G20_Conversion")))
    diagnosis_summary = diagnosis_summary[cols]


    
    return diagnosis_summary


