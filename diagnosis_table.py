# -*- coding: utf-8 -*-
"""

Func for table of diagnoses overview and check

"""

import pandas as pd
import numpy as np


def diagnosis_table_func(func_dats, common_ids, dia_cols):
    hvdat = func_dats["hvdat"]
    
    
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
    diagnosis_summary.columns = ["StudieID", "diagnosis", "number_of_pickups"] + list(diagnosis_summary.columns[3:])
    
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
    
    
    return diagnosis_summary


