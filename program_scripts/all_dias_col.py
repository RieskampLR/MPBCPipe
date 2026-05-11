# -*- coding: utf-8 -*-
"""

Func for column generation of all diagnoses in 1 col combined

"""

import pandas as pd

def all_diagnoses_func(func_dats, dia_cols):
    hvdat = func_dats["hvdat"]

    hvdat["all_diagnoses"] = hvdat[dia_cols].values.tolist()
    hvdat["all_diagnoses"] = hvdat["all_diagnoses"].apply(set)
    hvdat["all_diagnoses"] = hvdat["all_diagnoses"].apply(list)
    
    # Remove nan entries
    hvdat["all_diagnoses"] = hvdat["all_diagnoses"].apply(lambda x: [i for i in x if i != "nan" and pd.notna(i)])
    

    return hvdat