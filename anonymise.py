#!/usr/bin/python3
# -*- coding: utf-8 -*-


"""
anonymise.py

To anonymise Patient IDs

Run as python anonymise.py questionnaire_data.csv pharmacy_data.txt hospitalisations_data.txt visits_data.txt

Non_prescription and Prescription_Med_text have empty entries in the original instead of NAs,
this pipe's output replaces them with NAs

"""


# Imports:

import sys
import pandas as pd
from pathlib import Path


# Storing Paths of arguments in variables:
    
qdat = pd.read_csv(Path(sys.argv[1])) # questionnaire data
pdat = pd.read_table(Path(sys.argv[2]), encoding='unicode_escape') # pharmacy data
hdat = pd.read_table(Path(sys.argv[3]), encoding='unicode_escape', low_memory=False) # hospital data
vdat = pd.read_table(Path(sys.argv[4]), encoding='unicode_escape', low_memory=False) # visits data


# New ID's dictionary (numbered based on qdat)

id_dictionary = {}
new_id = 1

for i in qdat["Id"]:
    if i not in id_dictionary:
        id_dictionary[i] = new_id
        new_id = new_id + 1
        
for i in pdat["StudieID"]:
    if i not in id_dictionary:
        id_dictionary[i] = new_id
        new_id = new_id + 1

for i in hdat["StudieID"]:
    if i not in id_dictionary:
        id_dictionary[i] = new_id
        new_id = new_id + 1
        
for i in vdat["StudieID"]:
    if i not in id_dictionary:
        id_dictionary[i] = new_id
        new_id = new_id + 1

#print(id_dictionary)


# Use dictionary to transform data files into anonymised versions

qdat_anonym = qdat
qdat_anonym["Id"] = qdat_anonym["Id"].replace(id_dictionary)
qdat_anonym = qdat_anonym.drop("Unnamed: 0", axis=1)
qdat_anonym = qdat_anonym.convert_dtypes()
#print(qdat_anonym)
#print(qdat_anonym.dtypes)

pdat_anonym = pdat
pdat_anonym["StudieID"] = pdat_anonym["StudieID"].replace(id_dictionary)
#print(pdat_anonym)

hdat_anonym = hdat
hdat_anonym["StudieID"] = hdat_anonym["StudieID"].replace(id_dictionary)
hdat_anonym = hdat_anonym.convert_dtypes()
#print(pdat_anonym)

vdat_anonym = vdat
vdat_anonym["StudieID"] = vdat_anonym["StudieID"].replace(id_dictionary)
#print(pdat_anonym)


# Save

id_dic_pdtable = pd.DataFrame.from_dict(id_dictionary, orient="index")
id_dic_pdtable.to_csv("id_anonymised_dictionary.txt", sep='\t', header=False)

qdat_anonym.to_csv("qdat_anonymised.tsv", sep='\t', index=False, index_label=None, na_rep='NA')

pdat_anonym.to_csv("pdat_anonymised.tsv", sep='\t', index=False)

hdat_anonym.to_csv("hdat_anonymised.tsv", sep='\t', index=False)

vdat_anonym.to_csv("vdat_anonymised.tsv", sep='\t', index=False)




