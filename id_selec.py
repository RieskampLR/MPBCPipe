# -*- coding: utf-8 -*-
"""

Func to filter IDs by condition based on json file

"""


def id_selection_func(tables, cond):
    
    id_selection = {}

    for table in tables:
        filters = cond[table]
        ids = tables[table]
        for col, val in filters.items():
            if col == "all_diagnoses":
                for x in ids[col]:
                    overlap = [i for i in x if i in val["values"]]
                if overlap:
                    #print(overlap)
                    ids = ids[ids[col].apply(lambda lst: any(i in val["values"] for i in lst))]   
                #print(len(ids[col]))
            else:
                if val["type"] == "range":
                    if val["values"][0] == ">=":
                        ids = ids[ids[col] >= val["values"][1]]
                    elif val["values"][0] == "<=":
                        ids = ids[ids[col] <= val["values"][1]]
                    else:
                        ids = ids[ids[col].between(*val["values"])]
                elif val["type"] == "string":
                    if val["values"] == ["any"]:
                        ids = ids[ids[col].notna()]
                    elif val["values"] == ["none"]:
                        ids = ids[ids[col].isna()]
                    else:
                        ids = ids[ids[col].astype(str).isin(val["values"])]
                        #print(ids["hdia"])
                else:
                    ids = ids[ids[col].isin(val["values"])]
                    
        id_selection[table] = ids["StudieID"]

    # IDs must match ALL conditions

    common_ids = set.intersection(*(set(v) for v in id_selection.values()))
    #print(len(common_ids))
    
    
    
    return common_ids

