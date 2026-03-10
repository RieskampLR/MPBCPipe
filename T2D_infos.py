# -*- coding: utf-8 -*-
"""

T2D patient numbers at inclusion and stuff script

Created on Mon Mar  9 15:54:47 2026

@author: admin
"""


import pandas as pd
from pathlib import Path


hdat_T2D = pd.read_table(Path("C:/Users/admin/OneDrive/Dokumente/UniLund/Thesis/dats/hdat_T2D_cut.tsv"))
hdat_T2D_case = pd.read_table(Path("C:/Users/admin/OneDrive/Dokumente/UniLund/Thesis/dats/hdat_T2D_Case.tsv"))
hdat_T2D_control = pd.read_table(Path("C:/Users/admin/OneDrive/Dokumente/UniLund/Thesis/dats/hdat_T2D_Control.tsv"))

vdat_T2D = pd.read_table(Path("C:/Users/admin/OneDrive/Dokumente/UniLund/Thesis/dats/vdat_T2D_cut.tsv"))
vdat_T2D_case = pd.read_table(Path("C:/Users/admin/OneDrive/Dokumente/UniLund/Thesis/dats/vdat_T2D_Case.tsv"))
vdat_T2D_control = pd.read_table(Path("C:/Users/admin/OneDrive/Dokumente/UniLund/Thesis/dats/vdat_T2D_Control.tsv"))

qdat = pd.read_table(Path("C:/Users/admin/OneDrive/Dokumente/UniLund/Thesis/dats/qdat_anonymised.tsv"))


# Modify header names

qdat = qdat.rename(columns={"Id": "StudieID"})

hdat_T2D = hdat_T2D.rename(columns={"INDATUMA":"YearofVisit"})
hdat_T2D_case = hdat_T2D_case.rename(columns={"INDATUMA":"YearofVisit"})
hdat_T2D_control = hdat_T2D_control.rename(columns={"INDATUMA":"YearofVisit"})

vdat_T2D = vdat_T2D.rename(columns={"INDATUMA":"YearofVisit"})
vdat_T2D_case = vdat_T2D_case.rename(columns={"INDATUMA":"YearofVisit"})
vdat_T2D_control = vdat_T2D_control.rename(columns={"INDATUMA":"YearofVisit"})



# Modify date to year only

hdat_T2D["YearofVisit"] = hdat_T2D["YearofVisit"].astype(str).str[0:4]
hdat_T2D_case["YearofVisit"] = hdat_T2D_case["YearofVisit"].astype(str).str[0:4]
hdat_T2D_control["YearofVisit"] = hdat_T2D_control["YearofVisit"].astype(str).str[0:4]

vdat_T2D["YearofVisit"] = vdat_T2D["YearofVisit"].astype(str).str[0:4]
vdat_T2D_case["YearofVisit"] = vdat_T2D_case["YearofVisit"].astype(str).str[0:4]
vdat_T2D_control["YearofVisit"] = vdat_T2D_control["YearofVisit"].astype(str).str[0:4]


# Combined data set for hdat and vdat

merged_dat_T2D = pd.concat([vdat_T2D, hdat_T2D], ignore_index=True)
merged_dat_T2D_case = pd.concat([vdat_T2D_case, hdat_T2D_case], ignore_index=True)
merged_dat_T2D_control = pd.concat([vdat_T2D_control, hdat_T2D_control], ignore_index=True)


# Individuals with T2D ########################################################

ids_hdat_T2D = hdat_T2D["StudieID"].drop_duplicates().to_frame()
# 129 individuals in hdat
ids_vdat_T2D = vdat_T2D["StudieID"].drop_duplicates().to_frame()
# 136 individuals in vdat
ids_merged_T2D = merged_dat_T2D["StudieID"].drop_duplicates().to_frame()
# 175 individuals across both (i.e. 90 T2D patients are listed in hdat AND vdat)

# Individuals with T2D & Parinsons (Case) #####################################

ids_hdat_T2D_case = hdat_T2D_case["StudieID"].drop_duplicates().to_frame()
# 64 individuals in hdat
ids_vdat_T2D_case = vdat_T2D_case["StudieID"].drop_duplicates().to_frame()
# 33 individuals in vdat
ids_merged_T2D_case = merged_dat_T2D_case["StudieID"].drop_duplicates().to_frame()
# 70 individuals

# Individuals with T2D & no Parkinson (Control) ###############################

ids_hdat_T2D_control = hdat_T2D_control["StudieID"].drop_duplicates().to_frame()
# 89 individuals in hdat
ids_vdat_T2D_control = vdat_T2D_control["StudieID"].drop_duplicates().to_frame()
# 126 individuals in vdat
ids_merged_T2D_control = merged_dat_T2D_control["StudieID"].drop_duplicates().to_frame()
# 154 individuals

# Individuals that have G20 in some entries in some not  ######################

hdat_included_in_case_and_control = set(hdat_T2D_case["StudieID"]).intersection(hdat_T2D_control["StudieID"])
# 24 individuals in hdat
vdat_included_in_case_and_control = set(vdat_T2D_case["StudieID"]).intersection(vdat_T2D_control["StudieID"])
# 23 individuals in hdat
merged_included_in_case_and_control = set(merged_dat_T2D_case["StudieID"]).intersection(merged_dat_T2D_control["StudieID"])
# 49




# Diagnosis status at inclusion year ##

# Table formatting

qdat_inclusion_years = qdat[["StudieID","Control","Diabetes","Inclusion_Year"]]

qdat_inclusion_years["Inclusion_Year"] = pd.to_numeric(qdat_inclusion_years["Inclusion_Year"])
merged_dat_T2D["YearofVisit"] = pd.to_numeric(merged_dat_T2D["YearofVisit"])

qdat_control = qdat_inclusion_years[qdat_inclusion_years["Control"] == 1]
qdat_case = qdat_inclusion_years[qdat_inclusion_years["Control"] == 0]


# Individuals with self-reported diabetes (Control & Case) ####################

qdat_T2D_control = qdat_control[qdat_control["Diabetes"] == 1]
# 77 Controls with Diabetes in qdat
qdat_T2D_case = qdat_case[qdat_case["Diabetes"] == 1]
# 71 non_Controls with Diabetes in qdat


# Table of hdat and vdat with qdat-inclusion-year for each individual added

merged = merged_dat_T2D.merge(qdat_inclusion_years[["StudieID", "Inclusion_Year"]],
                              on="StudieID",
                              how="left")

merged = merged[[*merged.columns[:3], "Inclusion_Year", *merged.columns[3:].drop("Inclusion_Year")]] # moves coloumns around

# merged["Inclusion_Year"].value_counts(dropna=False)
# 72 Indivs where not included in qdat (i.e. inclusion year is NaN) ###########


# Table of only those entries that match the diagnosis and inclusion year

merged_filtered_strict = merged[merged["YearofVisit"] == merged["Inclusion_Year"]]
# --> only contains individuals that have T2D at inclusion year in qdat
# --> 95 entries

merged_filtered = merged[
    (merged["YearofVisit"] == merged["Inclusion_Year"] - 1) |
    (merged["YearofVisit"] == merged["Inclusion_Year"]) |
    (merged["YearofVisit"] == merged["Inclusion_Year"] + 1)
]
# --> only contains individuals that have T2D at inclusion year +-1 in qdat
# --> 342 entries


ids_merged_filtered_strict = merged_filtered_strict["StudieID"].drop_duplicates().to_frame()
# --> 45 individuals ##########################################################
ids_merged_filtered = merged_filtered["StudieID"].drop_duplicates().to_frame()
# --> 45 individuals ##########################################################











# ?????????????????????????????????????????????????????????????????????????????:
qdat_only_controls = qdat_controls[~qdat_controls["StudieID"].isin(merged["StudieID"])]
# len(qdat_only_controls)
# 860 patients in qdat but not in vdat or hdat

lying_patients = qdat_non_controls_with_T2D[~qdat_non_controls_with_T2D["StudieID"].isin(merged_filtered["StudieID"])]
# len(lying_patients)
# 48 patients stating in qdat to have T2D but are not in vdat or hdat T2D patients

# How many patients are diagnosed with T2D at time of inclusion but do not say so in qdat:



