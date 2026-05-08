# -*- coding: utf-8 -*-
"""

Func to filter IDs by condition based on json file

"""

import re

# Helper function for regex matching and going through list entries (+ treating single string as list)
import pandas as pd
import re

def match(v, x):
    if x is None or (isinstance(x, float) and pd.isna(x)): # handles NaNs (cause re.fullmatch sees them as floats)
        return False
    return any(re.fullmatch(v, str(item)) for item in (x if isinstance(x, list) else [x]))

def id_selection_func(tables, cond):
    
    id_selection = {}

    for table in tables:
        
        filters = cond[table]
        ids = tables[table]
        
        for col, val in filters.items():
            
            # ----------------------------range--------------------------------
            if val["type"] == "range":
                if val["values"][0] == ">=":
                    ids = ids[ids[col] >= val["values"][1]]
                elif val["values"][0] == "<=":
                    ids = ids[ids[col] <= val["values"][1]]
                else:
                    ids = ids[ids[col].between(*val["values"])]
                    
            # ----------------------------strings------------------------------
            elif val["type"] == "string":
                
                exclude = [v[1:] for v in val["values"] if v.startswith("!")]   # [1:] strips the !
                exclusion_filter = lambda x: any(match(v, x) for v in exclude) # func to get ids to exclude (if !-val is in list)
                excluded_ids = ids.loc[ids[col].apply(lambda x: exclusion_filter(x)), "StudieID"].tolist()
                ids = ids[~ids["StudieID"].isin(excluded_ids)]
                
                if val["values"] == ["any"]:
                    ids = ids[ids[col].notna()]
                    
                elif val["values"] == ["none"]:
                    ids = ids[ids[col].isna()]
                    
                elif "&" in val["values"]:   # & marker: ALL entries must be present
                    stripped_vals = [v for v in val["values"] if v not in ["&"] and not v.startswith("!")] # remove & and !-vals
                    ids = ids[ids[col].apply(
                        lambda x: all(match(v, x) for v in stripped_vals))] # Checks if all entries are in the indiv's entry
                
                else:
                    ids = ids[ids[col].apply(
                        lambda x: any(match(v, x) for v in val["values"]))] # Checks if any entries are in the indiv's entry
            
            # ----------------------------exact_numbers------------------------           
            else:
                ids = ids[ids[col].isin(val["values"])]
                    
        id_selection[table] = ids["StudieID"]


    # IDs must match ALL conditions
    common_ids = set.intersection(*(set(v) for v in id_selection.values()))
    
    
    return common_ids

