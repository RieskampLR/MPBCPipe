README

Description:
piper1.py filters and combines the datasets
UT_R_LMED_14691_2021,
UT_R_PAR_OV_14691_2021,
UT_R_PAR_SV_14691_2021,
and QuestionnaireData_N1864_FINAL_CLEANED_210621

Command to run the pipeline:
python piper1.py -q QuestionnaireData_N1864_FINAL_CLEANED_210621 -p UT_R_LMED_14691_2021 -hd UT_R_PAR_SV_14691_2021 -v UT_R_PAR_OV_14691_2021 -cat categories.json -cond conditions.json
Optional: -o output_name_prefix -s example example -pt -dt example example

Flags:
-s: The user can add this flag to specify the categories by which the output table should be sorted by.
The first category stated is the main sort variable, the second the sub-sorting variable and so on.
The categories have to be included in the categories displayed in the output table. They are to be listed without "" and separated by tab space.
-p: The addition of this flag leads to an additional output table with pharmacy data on the patients included in the main output table.
The pharmacy data table shows the medications (subnamn) picked up by each individual, the number of pick ups, the time span across which pick ups occurred, and the specific pick up dates.
This flag does not take any arguments.

Json files and user specifications:
The user is required to provide
- A json file stating the categories wanted in the output table
- A json file stating the conditions for individuals being included in the output table
Example files are available and can be easily modified.


Installations:
python
	pandas
	numpy
	...
openpyxl
...


Json file formats and modifications:
Categories:
The json file for output table category specifications must contain a dictionary with "pdat", "qdat", and "hvdat" as keys,
representing pharmacy, questionnaire, and hospital+doctoral visits data,
and lists containing the requested categories from within the corresponding data sets as values.
In qdat "Id" is to be noted as "StudieID" (the questionnaire header contains "Id").
Conditions:
The json file specifying the conditions under which samples are included in the output table must also contain a dictionary.
Here the keys are the same as in the categories file.
The values in this case are again dictionaries. These contain the category that a condition is applied to as key and a further dictionary as a value.
The further dictionaries contain 1. "type" as a key followed by a string as a value
and 2. "value" as key and a list stating the condition as a value.
Depending on this condition's format in the list the string for the "type" key is either "values", "range", or "string".
The conditions lists also allow for ">=" and "<=" in ranges and "any" (stating to exclude empty / NA entries) and "none" as strings.
If all entries in a string list should appear, the list should start with the entry "&", which functions as a marker, stating that all (instead of any) entries must appear in the selected IDs.


If qdat, pdat, or hdat and vdat are not provided the json entries for these are to be removed from the categories and conditions files.



The script calculates additional categories from combining data across the sets. These categories can be included in the json files and currently include:
qdat:
When hdat and/or vdat are provided:
	Doctoral_diagnoses_at_inclusion_+-1year
	Doctoral_diagnoses_recorded_till_inclusion_+1year
	Doctoral_diagnoses_received_after_inclusion_year
hvdat:
When hdat and/or vdat are provided:
	all_diagnoses



