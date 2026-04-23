# -*- coding: utf-8 -*-
"""

Func for thetable generation and formatting

"""

import pandas as pd
import numpy as np


def thetable_func (func_dats, cat_tables, common_ids):
    categories = func_dats["categories"]
    
    # Filtering for user-defined output table categories
    # collect info on chosen IDs from other tables
    result = {}
    for table, cols in categories.items():
        df = cat_tables[table]
        filtered = df[df["StudieID"].isin(common_ids)]
        selected_cols = ["StudieID"] + [c for c in cols if c != "StudieID"]
        result[table] = filtered[selected_cols]

    # merge to one table

    # Convert all columns except StudieID to string and fill NaN
    #for tbl in ["pdat", "hvdat", "qdat"]:
     #   df = result[tbl]
        #for col in df.columns:
         #   if col != "StudieID":
          #      df[col] = df[col].fillna("").astype(str)
      #  result[tbl] = df

    

    # Then aggregate by StudieID
    pdat_agg = result["pdat"].groupby("StudieID", as_index=False).agg(",".join)
    #hvdat_agg = result["hvdat"].groupby("StudieID", as_index=False).agg(",".join)
    hvdat_agg = result["hvdat"].groupby("StudieID", as_index=False).agg("first")
    qdat_agg = result["qdat"].groupby("StudieID", as_index=False).agg(",".join)

    thetable = pdat_agg.merge(hvdat_agg, on="StudieID", how="outer") \
                       .merge(qdat_agg, on="StudieID", how="outer")

    # nan for qdat vals where no entries in qdat for IDs that are present in pdat

    # Remove duplicates in fields and nans

    for col in thetable.columns:
        new_val = []
        for val in thetable[col]:
            if isinstance(val, float) and pd.isna(val):
                new_val.append(val)
            elif isinstance(val, list):
                new_val.append(sorted(set(val)))
            else:
                new_val.append(val)
        thetable[col] = new_val

    
    return thetable



