# MultiParkPiper

Version: 1.00  
Date: 2026-02-28  
Author: Lea Rachel Rieskamp
Supervision: Maria Swanberg, Translational Neurogenetics Lab, Lund University

------------------------------------------------------------------------------------------------------------------------------------------------------

# Overview

piper1.py is a flexible Python pipeline for filtering, combining, stratifying, and summarising clinical and registry data used in Parkinson's disease research.
The script integrates questionnaire, diagnosis, and pharmacy datasets and enables users to:

- Identify individuals matching user-defined conditions
- Generate filtered output tables with user-defined columns
- Combine information across datasets
- Generate additional columns with information derived from cross-table analysis
- Produce optional diagnosis summary tables
- Produce optional pharmacy summary tables
- Export all results as .tsv, .xlsx, and ID list files

The program is currently used in the Translational Neurogenetics Lab at Lund University for:
- General cohort inspection
- Phenotype stratification
- Longitudinal diagnosis analyses
- Cross-table validation and consistency checks
- Polygenic risk score analyses
- Medication analyses

------------------------------------------------------------------------------------------------------------------------------------------------------

# Supported input datasets

The pipeline currently supports the following datasets:

- QuestionnaireData_N1864_FINAL_CLEANED_210621	(Questionnaire / phenotype data)
- UT_R_LMED_14691_2021							(Medication pick-up registry )
- UT_R_PAR_SV_14691_2021						(Hospital diagnosis registry )
- UT_R_PAR_OV_14691_2021						(Outpatient/doctoral visit diagnosis registry)

For efficiency purposes these are referred to in my script and the following descriptions as qdat, pdat, hdat, and vdat, respectively.
hvdat refers to the combined vdat and hdat data.

------------------------------------------------------------------------------------------------------------------------------------------------------

# Requirements

## Python packages

- pandas
- numpy
- openpyxl

Install with:
pip install pandas numpy openpyxl

------------------------------------------------------------------------------------------------------------------------------------------------------

# Input pre-processing

All input files must first be converted to tsv format using the provided csv_to_tsv conversion script before running the pipeline.

------------------------------------------------------------------------------------------------------------------------------------------------------

# Usage

## Basic command

python piper1.py -q qdat.tsv -cat categories.json -cond conditions.json

## Full example

python piper1.py \
-q qdat.tsv \
-p pdat.tsv \
-hd hdat.tsv \
-v vdat.tsv \
-cat categories.json \
-cond conditions.json

## Example with optional flags and example flag arguments

python piper1.py \
-q qdat.tsv \
-p pdat.tsv \
-hd hdat.tsv \
-v vdat.tsv \
-cat categories.json \
-cond conditions.json \
-o PD_patients \
-s Age_Diagnosis StudieID \
-pt after \
-dt Diabetes oneway_G20

------------------------------------------------------------------------------------------------------------------------------------------------------

# Command line arguments

## Required arguments

-cat, --categories		JSON file specifying output columns/categories
-cond, --conditions		JSON file specifying filtering conditions

## Optional input files

-q, --qdat				Questionnaire dataset
-p, --pdat				Pharmacy dataset
-hd, --hdat				Hospital diagnosis dataset
-v, --vdat				Doctoral/outpatient diagnosis dataset

## Optional output & processing flags

-o, --output			Prefix added to all generated output files
-s, --sort				Columns to sort the final output table by
-pt, --pharma			Generate pharmacy summary table
-ptf, --pharmafiltered	Generate filtered pharmacy summary table
-dt, --diagnosis		Generate diagnosis summary table

------------------------------------------------------------------------------------------------------------------------------------------------------

# Flag details & examples

## -o

Adds a prefix to all output files.
Example: -o Parkinsons_subset
Produces files such as:
Parkinsons_subset_filtered_table.tsv
Parkinsons_subset_ids_list.csv

## -s

Sorts the final output table vertically by one or more columns.
Syntax: -s column1 column2 column3
The first column is the primary sort variable, the second is the secondary sort variable, etc.
Example: -s Age_Diagnosis StudieID
Important: Sort columns must also be included in the categories JSON file.

## -pt

Generates a pharmacy summary table (described in further detail under Pharma summary table below).
Optional arguments:
upto
at
after
These define filtering relative to inclusion year.
Example: -pt after

## -ptf

Same as -pt, but restricts the displayed output to pharmacy entries matching the requested subnamn conditions.
Example: -ptf after
Important: -pt and -ptf cannot be used simultaneously.

## -dt

Generates a diagnosis summary table (described in further detail under Diagnosis summary table below).
Optional arguments can specify:
qdat diagnosis columns to be included
diagnosis conversion analysis modes
Example: -dt Diabetes
Example with conversion mode: -dt oneway_G20
Example with multiple arguments: -dt Diabetes Depression oneway_G20

------------------------------------------------------------------------------------------------------------------------------------------------------

# Output files

The pipeline generates the following output files as .tsv and excel files:

filtered_table.tsv/xlsx				Main filtered output table
ids_list.tsv/xlsx					Included patient IDs

Optional outputs:

pharma_summary_table.tsv/xlsx		Pharmacy summary table
diagnosis_summary_table.tsv/xlsx	Diagnosis summary table

------------------------------------------------------------------------------------------------------------------------------------------------------

# JSON configuration files

The pipeline requires two JSON files:

categories.json
conditions.json

Their structuring and use are described in the following below.
Example files are provided on GitHub and can be adjusted easily.

------------------------------------------------------------------------------------------------------------------------------------------------------

# Categories JSON file

The categories JSON defines which columns should appear in the final output table.
The file contains a simple dictionary with dataset names as keys and lists of column names as items:

## Basic structure

{
  "qdat": [],
  "pdat": [],
  "hvdat": []
}

## Example:

{
  "qdat":
  ["StudieID",
  "Doctoral_diagnoses_at_inclusion_+-1year"],

  "pdat":
  ["ATC",
  "produkt"],

  "hvdat":
  ["hdia",
  "all_diagnoses"]
}

## Important Notes

qdat should contain "StudieID" (noted as "id" in the original file).
The file can contain additional column names (not present in the original data sets).
These are generated by the program based on data stratification within and across tables (described in detail under Additional generated columns).

------------------------------------------------------------------------------------------------------------------------------------------------------

# Conditions JSON file

The conditions JSON defines which individuals are included in the final output table.
The file contains nested dictionaries with dataset names as top-level keys with dictionaries as items.
These nested dictionaries contain column names as keys and again dictionaries as items,
which contain "type" as a key with a string as the item followed by "values" as a key and a list as the item.
The nesting represents the structure:
dataset --> column/category --> condition imposed on it

## Basic structure

{
  "qdat": {},
  "pdat": {},
  "hvdat": {}
}

## Condition setting format

To set a condition the user needs to specify the "type" of condition under the key "type".
Supported types are:
string
range
values

Example:
{
  "type": "range",
  "values": [5, 10]
}

### Values conditions

Used for numerical values filtering, e.g., to include individuals at specific Hoehn&Yahr stages.

Basic example:
{
  "Hoehn_Yahr": {
    "type": "values",
	"values": [3, 5]
  }
}
Filters for all individuals that have Hoehn&Yahr stage of 3 OR 5.

### Range conditions

Used for numerical range filtering, e.g., to include any individuals within an age range.

Basic example:
{
  "type": "range",
  "values": [20, 40]
}
Where the outer limit values, 20 and 40, are included in the selected range.

#### Supported operators:

>=
<=
>
<

Example:
{
  "Age_Diagnosis": {
    "type": "range",
    "values": ["<=", 40]
  }
}
Filters for all individuals that received their diagnosis at 40 or younger.

### String conditions

Used for text matching, e.g., diagnosis or medication codes.
Capable of regex matching.

Basic example:
{
  "hvdat": {
    "all_diagnoses": {
      "type": "string",
      "values": ["G20"]
    }
  }
}
Filters for individuals having "G20" in "all_diagnoses" (an hvdat column).

#### Match to exclude:

Individuals can also be EXCLUDED from the final table by matching a condition.
To exclude if a string is matched, begin the string with: "!"
Example:	["!G20"]
Filters for individuals NOT having G20.

#### Multiple match conditions:

Match any - Example:	["G20", "E11"]
Filters for all individuals containing G20 AND/OR E11.

Match both - Example: 	["&", "G20", "E11"]
Filters for all individuals containing G20 AND E11.
If all entries must match, begin the list with: "&"

Complex combination - Example: ["&", "G20", "E.*", "!E11"]
Filters for all individuals that have G20 AND have any diagnosis starting with E, but NOT E11.

#### Special Conditions:

any
Includes only non-empty entries.
Example:
{
  "produkt": {
    "type": "string",
    "values": ["any"]
  }
}

none
Matches empty and na entries.
Example:
{
  "produkt": {
    "type": "string",
    "values": ["none"]
  }
}

## Example condition JSON
{
  "qdat": {
  },
  "pdat": {
    "ATC": {
      "type": "string",
      "values": ["^C05.*"]
    }
  },
  "hvdat": {
    "all_diagnoses": {
      "type": "string",
      "values": ["G20"]
    }
  }
}

------------------------------------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------------------------------------

Additional Generated Columns

The pipeline generates additional derived columns when diagnosis data (hdat and/or vdat) is provided.

Additional qdat Columns

Available when hdat and/or vdat are included:

Column	Description
Doctoral_diagnoses_at_inclusion_+-1year	Diagnoses around inclusion year
Doctoral_diagnoses_recorded_till_inclusion_+1year	Diagnoses recorded up to inclusion
Doctoral_diagnoses_received_after_inclusion_year	Diagnoses received after inclusion
Additional hvdat Columns
Column	Description
all_diagnoses	All diagnoses combined into one column

------------------------------------------------------------------------------------------------------------------------------------------------------

Diagnosis Summary Table

The diagnosis summary table compares questionnaire diagnoses with diagnosis registry data.

Conversion Analyses
G20 Conversion

Can be analysed in:

two-way mode (default)
one-way mode
reverse one-way mode
Default Mode (Two-Way)

A conversion is flagged if:

qdat diagnosis and hvdat diagnosis do not match

This includes:

Diagnosis stated in qdat but absent in hvdat
Diagnosis absent in qdat but present in hvdat
One-Way Mode

Only detects cases where:

hvdat diagnosis exists
qdat diagnosis does NOT exist

Useful for identifying likely post-inclusion diagnosis development.

Enable with:

-dt oneway_G20

or

-dt oneway_E11
Reverse One-Way Mode

Only detects cases where:

qdat diagnosis exists
hvdat diagnosis does NOT exist

Useful for identifying self-reported diagnoses lacking registry confirmation.

Enable with:

-dt onewayother_G20

or

-dt onewayother_E11

------------------------------------------------------------------------------------------------------------------------------------------------------

Pharmacy Summary Table

The table summarises:
Medications picked up
Number of pick-ups
Time span of pick-ups
Pick-up dates

The pharmacy summary table summarises medication pick-up data for all individuals included in the filtered cohort.
Filtered table displays only the medications filtered by.

Filtering Relative to Inclusion Year

Pharmacy data can be analysed in:

upto mode
at mode
after mode

Default Mode

If no argument is provided after -pt or -ptf:

all available pharmacy data is included

This includes:

All recorded medication pick-ups
All available years
All matching medications

Upto Mode

Only includes medication pick-ups occurring up to inclusion year.

Enable with:

-pt upto

or

-ptf upto

At Mode

Only includes medication pick-ups occurring around inclusion year.

Enable with:

-pt at

or

-ptf at

After Mode

Only includes medication pick-ups occurring after inclusion year.

Useful for identifying medication use after questionnaire inclusion.

Enable with:

-pt after

or

-ptf after

Filtered Pharmacy Mode

The filtered pharmacy summary table only includes medications matching requested subnamn conditions from the conditions json file.

Useful for:

Medication-specific analyses
Treatment stratification
Exposure analyses

Enable with:

-ptf

or

-ptf after




------------------------------------------------------------------------------------------------------------------------------------------------------

Error Handling

The script checks for:

Missing required datasets
Invalid optional flag combinations
Conditions/categories referencing unavailable datasets
Empty filtered results

Examples:

Using -pt without pdat
Using diagnosis-derived columns without diagnosis data
Using both -pt and -ptf

------------------------------------------------------------------------------------------------------------------------------------------------------

Important Notes
If a dataset is not provided, corresponding entries must be removed from:
categories JSON
conditions JSON
hdat and vdat are automatically merged internally into:
hvdat
Diagnosis columns are internally converted to strings because source formatting varies substantially across datasets.

------------------------------------------------------------------------------------------------------------------------------------------------------
Current Diagnosis Columns

The script currently processes:

hdia
DIA1
DIA2
...
DIA30

------------------------------------------------------------------------------------------------------------------------------------------------------

