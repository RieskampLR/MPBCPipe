# -*- coding: utf-8 -*-
"""

Func for table of pharma product pick up

"""

import pandas as pd
import numpy as np


def pharma_table_func(func_dats, common_ids, cond, filtered):
    pdat = func_dats["pdat"]
    
    # groupby object for group in grouped func
    grouped = pdat[pdat["StudieID"].isin(common_ids)].groupby(["StudieID","subnamn"])
    
    # Collect pick up cases info
    substance_info_rows = []
    for (stu_id, prod), group in grouped:
        dates = sorted(group["EDATUM"].tolist())   # all pickup dates for this ID+substance
        count = len(dates)               # number of pickups
        substance_info_rows.append([stu_id, prod, count] + dates)
    
    # Collect diagnosis cases info
    pharma_summary = pd.DataFrame(substance_info_rows)
    # Col headers
    pharma_summary.columns = ["StudieID", "subnamn", "number_of_pickups"] + list(pharma_summary.columns[3:])
    
    # Time frame column
    # Get date col names
    pharma_cols = pharma_summary.columns.tolist()
    for i in range(3, len(pharma_summary.columns)):
        pharma_cols[i] = f'Date_{i-2}'
    # Add to table
    pharma_summary.columns = pharma_cols
    date_cols = pharma_summary.columns[3:]
    pharma_summary[date_cols] = pharma_summary[date_cols].apply(pd.to_datetime, errors='coerce')
    pharma_summary["min_date"] = pharma_summary[date_cols].min(axis=1)
    pharma_summary["max_date"] = pharma_summary[date_cols].max(axis=1)
    # Find min max and add
    for col in list(date_cols) + ["min_date", "max_date"]:
        pharma_summary[col] = pharma_summary[col].dt.strftime("%Y-%m-%d")
    pharma_summary.insert(3, "span", np.nan)
    # Add col for span and rm min max cols
    pharma_summary["span"] = pharma_summary["min_date"] + " - " + pharma_summary["max_date"]
    pharma_summary = pharma_summary.drop(columns=["min_date", "max_date"])
    
    # Replace NA with blanks
    pharma_summary = pharma_summary.fillna('')
    
    # Filter option for displayed subnamn entries
    if filtered == True:
        pharma_summary = pharma_summary[pharma_summary["subnamn"].isin(cond["pdat"]["subnamn"]["values"])]
        
    # Filter by inclusion year
    
    
    return pharma_summary


