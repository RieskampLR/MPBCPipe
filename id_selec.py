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
                else:
                    ids = ids[ids[col].astype(str).isin(val["values"])]
            else:
                ids = ids[ids[col].isin(val["values"])]
        id_selection[table] = ids["StudieID"]

    # print(id_selection)

    # IDs must match ALL conditions

    common_ids = set.intersection(*(set(ids) for ids in id_selection.values()))
    # print(common_ids)
    
    return common_ids

