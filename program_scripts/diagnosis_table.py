# -*- coding: utf-8 -*-
"""

Func for table of diagnoses overview and check

"""

import pandas as pd
import numpy as np


def diagnosis_table_func(func_dats, common_ids, dia_cols, qdat_dias):
    hvdat = func_dats["hvdat"]
    qdat = func_dats["qdat"]
    
    # Pivot dates into ID-rows
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
    # Pheno_G20 (from qdat)
    diagnosis_summary = diagnosis_summary.merge(qdat[["StudieID", "PHENO"]], on='StudieID', how='left').rename(columns={'PHENO': 'Pheno_G20'})
    
    # G20_Conversion
    half_condition = diagnosis_summary.groupby("StudieID")["diagnosis"].transform(lambda x: x.str.contains("G20", na=False).any()) # Indiv has G20 somewhere
    
    # one-way flag option to show only those that have G20 but are not included in qdat as control (likely due to developing PD later)
    if "oneway_G20" in qdat_dias:
        conv_cond = (~(diagnosis_summary["Pheno_G20"] == 1) & half_condition)
        diagnosis_summary = diagnosis_summary.rename(columns={'G20_Conversion': 'Pheno_G20_Conv_1way'}) # rename col
        qdat_dias = [x for x in qdat_dias if x != "oneway_G20"] # remove one-way from qdat_dias list
    
    # one-way flag option to show only those that do not have G20 in hvdat but are included in qdat case (likely due to no further doctoral visits)
    elif "onewayother_G20" in qdat_dias:
        conv_cond = ((diagnosis_summary["Pheno_G20"] == 1) & ~half_condition)
        diagnosis_summary = diagnosis_summary.rename(columns={'G20_Conversion': 'Pheno_G20_Conv_1way_other'}) # rename col
        qdat_dias = [x for x in qdat_dias if x != "onewayother_G20"] # remove one-way from qdat_dias list
    
    # default: Conversion in any direction
    else:
        conv_cond = (
            ((diagnosis_summary["Pheno_G20"] != 1) & half_condition) |
            ((diagnosis_summary["Pheno_G20"] == 1) & ~half_condition)
        )
    diagnosis_summary["G20_Conversion"] = np.where( # returns one val where a condition is true, another where it is false
        diagnosis_summary["Pheno_G20"].isna(),      # condition: Is NA val
        np.nan,                                     # val if false: nan
        conv_cond                                   # val if true: boolean, 1 or 0
    ).astype(int)
    
    
    
    # Pheno-user-defined (from qdat)
    if qdat_dias is not None:
        merge_qdat_dias = [x for x in qdat_dias if x not in ["oneway_E11", "onewayother_E11"]] # exclude non-dia flag options
        diagnosis_summary = diagnosis_summary.merge(qdat[["StudieID"] + merge_qdat_dias], on="StudieID", how="left").rename(columns={c: f"Pheno_{c}" for c in merge_qdat_dias}) 
        

    # E11_Conversion
    if "Diabetes" in qdat_dias:
        half_condition = diagnosis_summary.groupby("StudieID")["diagnosis"].transform(lambda x: x.str.contains("E11", na=False).any()) # Indiv has E11 somewhere
        
        # one-way flag option to show only those that have E11 but did not say so in qdat
        if "oneway_E11" in qdat_dias:
            conv_cond = (~(diagnosis_summary["Pheno_Diabetes"] == 1) & half_condition)
            diagnosis_summary = diagnosis_summary.rename(columns={'E11_Conversion': 'Pheno_E11_Conv_1way'}) # rename col
            qdat_dias = [x for x in qdat_dias if x != "oneway_E11"] # remove one-way from qdat_dias list
        
        # one-way flag option to show only those that do not have E11 in hvdat but astate to have Diabetes in qdat
        elif "onewayother_E11" in qdat_dias:
            conv_cond = ((diagnosis_summary["Pheno_Diabetes"] == 1) & ~half_condition)
            diagnosis_summary = diagnosis_summary.rename(columns={'E11_Conversion': 'Pheno_E11_Conv_1way_other'}) # rename col
            qdat_dias = [x for x in qdat_dias if x != "onewayother_E11"] # remove one-way from qdat_dias list
        
        # default: Conversion in any direction
        else:
            conv_cond = (
                ((diagnosis_summary["Pheno_Diabetes"] != 1) & half_condition) |
                ((diagnosis_summary["Pheno_Diabetes"] == 1) & ~half_condition)
            )
        diagnosis_summary["E11_Conversion"] = np.where( # returns one val where a condition is true, another where it is false
            diagnosis_summary["Pheno_Diabetes"].isna(), # condition: Is NA val
            np.nan,                                     # val if true: nan
            conv_cond                                   # val if false: boolean, 1 or 0
        ).astype(int)  
    

    # Move cols
    cols = diagnosis_summary.columns.tolist()
    cols.insert(1, cols.pop(cols.index("Inclusion_Year")))
    cols.insert(3, cols.pop(cols.index("Pheno_G20")))
    
    if "G20_Conversion" in diagnosis_summary:
        cols.insert(4, cols.pop(cols.index("G20_Conversion")))
    elif "Pheno_G20_Conv_1way" in diagnosis_summary:
        cols.insert(4, cols.pop(cols.index("Pheno_G20_Conv_1way")))
    elif 'Pheno_G20_Conv_1way_other' in diagnosis_summary:
        cols.insert(4, cols.pop(cols.index("Pheno_G20_Conv_1way_other")))
    
    if "E11_Conversion" in diagnosis_summary:
        cols.insert(5, cols.pop(cols.index("E11_Conversion")))
    elif "Pheno_E11_Conv_1way" in diagnosis_summary:
        cols.insert(5, cols.pop(cols.index("Pheno_E11_Conv_1way")))
    elif 'Pheno_E11_Conv_1way_other' in diagnosis_summary:
        cols.insert(5, cols.pop(cols.index("Pheno_E11_Conv_1way_other")))

    if qdat_dias != None:
        for i, c in enumerate([f"Pheno_{dia}" for dia in qdat_dias]):
            cols.insert(5 + i, cols.pop(cols.index(c)))
    
    diagnosis_summary = diagnosis_summary[cols]
    
    
    # Replace NA with blanks
    diagnosis_summary = diagnosis_summary.fillna('')

    
    return diagnosis_summary


