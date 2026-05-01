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
    # Aggregate by StudieID
    pdat_agg = result["pdat"].groupby("StudieID", as_index=False).agg(list) if "pdat" in result else None
    hvdat_agg = result["hvdat"].groupby("StudieID", as_index=False).agg(list) if "hvdat" in result else None
    qdat_agg = result["qdat"].groupby("StudieID", as_index=False).agg(list) if "qdat" in result else None

     
    thetable = None
    for df in [pdat_agg, hvdat_agg, qdat_agg]:
        if df is not None:
            thetable = df if thetable is None else thetable.merge(df, on="StudieID", how="outer")


    # nan for qdat vals where no entries in qdat for IDs that are present in pdat

    # Remove duplicates in fields and nans

    for col in thetable.columns:
        new_val = []
        for val in thetable[col]:
            if isinstance(val, float) and pd.isna(val):
                new_val.append(val)
            elif isinstance(val, list):
                val_flat = [y for x in val for y in (x if isinstance(x, (list, np.ndarray)) else [x])] # ensures next line's iteration iterates over each list entry if nested
                val_cleaned = [x for x in val_flat if not pd.isna(x)]  # remove nans cause they mess with sorting
                new_val.append(sorted(set(val_cleaned), key=str))
            else:
                new_val.append(val)
        thetable[col] = new_val

    # Reformat cols to non-lists
    for col in thetable.columns:
        thetable[col] = thetable[col].apply(lambda x: ", ".join(map(str, x)) if isinstance(x, list) else x)      
    
    # Cols with .0 floats to integers
    for col in thetable.columns:
        thetable[col] = thetable[col].apply(
            lambda x: ", ".join(map(str, x)) if isinstance(x, list)             # map() converts each entry to str
            else (int(float(x)) if isinstance(x, str) and x.replace('.', '', 1).isdigit() and float(x).is_integer()
            else (int(x) if isinstance(x, (float, int)) and float(x).is_integer()
            else x))
        )

    
    return thetable



