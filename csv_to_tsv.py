# -*- coding: utf-8 -*-
"""
original csv files to tsv format

python csv_to_tsv.py qdat pdat hdat vdat

"""

from pathlib import Path
import argparse
import pandas as pd


parser = argparse.ArgumentParser()
parser.add_argument("qdat")
parser.add_argument("pdat")
parser.add_argument("hdat")
parser.add_argument("vdat")
args = parser.parse_args()


qdat = pd.read_csv(Path(args.qdat))
pdat = pd.read_table(Path(args.pdat), encoding='unicode_escape')
hdat = pd.read_table(Path(args.hdat), encoding='unicode_escape', low_memory=False)
vdat = pd.read_table(Path(args.vdat), encoding='unicode_escape', low_memory=False)


qdat = qdat.drop("Unnamed: 0", axis=1)
qdat = qdat.convert_dtypes()
pdat = pdat.convert_dtypes()
hdat = hdat.convert_dtypes()
vdat = vdat.convert_dtypes()


qdat.to_csv("qdat.tsv", sep='\t', index=False, index_label=None, na_rep='NA')
pdat.to_csv("pdat.tsv", sep='\t', index=False)
hdat.to_csv("hdat.tsv", sep='\t', index=False)
vdat.to_csv("vdat.tsv", sep='\t', index=False)