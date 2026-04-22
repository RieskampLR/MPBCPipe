# -*- coding: utf-8 -*-
"""

Func for column generation of all diagnoses in 1 col combined

"""

import pandas as pd

def all_diagnoses_func(func_dats, dia_cols):
    hvdat = func_dats["hvdat"]

    # New column
    hvdat["all_diagnoses"] = (
        hvdat[dia_cols]
        .stack()
        .dropna()
        .groupby(level=0)
        .agg(list)
    )
    
    # Remove duplicates
    hvdat["all_diagnoses"] = hvdat["all_diagnoses"].apply(set).apply(list)
    
    # Formatting
    hvdat["all_diagnoses"] = hvdat["all_diagnoses"].apply(", ".join)
    
    return hvdat