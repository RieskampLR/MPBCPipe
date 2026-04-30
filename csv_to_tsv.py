# -*- coding: utf-8 -*-
"""
original csv files to tsv format

python csv_to_tsv.py qdat pdat hdat vdat

"""

from pathlib import Path
import argparse
import pandas as pd


parser = argparse.ArgumentParser()
parser.add_argument("-q", "--qdat")
parser.add_argument("-p", "--pdat")
parser.add_argument("-hd", "--hdat") # -h is reserved by argparse for help
parser.add_argument("-v", "--vdat")
args = parser.parse_args()


qdat = pd.read_csv(Path(args.qdat)) if args.qdat else None
pdat = pd.read_table(Path(args.pdat), encoding='unicode_escape') if args.pdat else None
hdat = pd.read_table(Path(args.hdat), encoding='unicode_escape', low_memory=False) if args.hdat else None
vdat = pd.read_table(Path(args.vdat), encoding='unicode_escape', low_memory=False) if args.vdat else None


if qdat is not None:
    qdat = qdat.drop("Unnamed: 0", axis=1)
    qdat = qdat.convert_dtypes()
    qdat.to_csv("qdat.tsv", sep='\t', index=False, index_label=None, na_rep='NA')
if pdat is not None:
    pdat = pdat.convert_dtypes()
    pdat.to_csv("pdat.tsv", sep='\t', index=False)
if hdat is not None:
    hdat = hdat.convert_dtypes()
    hdat.to_csv("hdat.tsv", sep='\t', index=False)
if vdat is not None:
    vdat = vdat.convert_dtypes()
    vdat.to_csv("vdat.tsv", sep='\t', index=False)


