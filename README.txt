README

Description:
piper1.py is a flexible program filtering, combining, and stratifying data from the Parkinsons registry, Styrelsen, and ... !!!!!!!???????
It enables the identification of individuals meeting certain user-defined conditions and provides output tables with user-defined categories
and optional, additional coloumns generated based on information provided across the data sets.
The program output a table with all user-specified columns of the individual's IDs matching the user-specified conditions.
Additionally, it provides a file listing the IDs and can produce a table with further information on diagnoses and a table with summarised pharmacy data.
The program is and will be used in the Translational Neurogenetics lab at Lund University to enable efficient data analysis,
including general data inspection and polygenic risk scores analyses.
The datasets currently available to the lab are
UT_R_LMED_14691_2021,
UT_R_PAR_OV_14691_2021,
UT_R_PAR_SV_14691_2021,
and QuestionnaireData_N1864_FINAL_CLEANED_210621

Command to run the program:
python piper1.py -q QuestionnaireData_N1864_FINAL_CLEANED_210621 -p UT_R_LMED_14691_2021 -hd UT_R_PAR_SV_14691_2021 -v UT_R_PAR_OV_14691_2021 -cat categories.json -cond conditions.json
Optional: -o output_name_prefix -s example example -pt -dt example example


Required packages:
python
	pandas
	numpy
openpyxl


Usage:
The program requires the questionnaire data (qdat) and can optionally include hospital (hdat), doctoral visits (vdat), and pharmacy (pdat) data.
It further requires the user to provide 2 json files. One with the columns/categories the output table should include
and one with the conditions for individuals to be included in the final output table. Further details on these are described below
and a range of example files are provided with the program on git hub.
Besides the flags indicating input files, the program has 4 further flags that can be added in the command line.
These and their functions are described in the section "Flags" below.



Flags:
-o:
-s: The user can add this flag to specify the categories by which the output table should be sorted by.
The first category stated is the main sort variable, the second the sub-sorting variable and so on.
The categories have to be included in the categories displayed in the output table. They are to be listed without "" and separated by tab space.
-pt: The addition of this flag leads to an additional output table with pharmacy data on the patients included in the main output table.
The pharmacy data table shows the medications (subnamn) picked up by each individual, the number of pick ups, the time span across which pick ups occurred, and the specific pick up dates.
This flag does not take any arguments.
-dt: 


Json files and user specifications:
The user is required to provide
- A json file stating the categories wanted in the output table
- A json file stating the conditions for individuals being included in the output table
Example files are available and can be easily modified.


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





Diagnosis table:
...
- E11 conversion is only calculated and displayed if Diabetes is added as an argument to the -dt flag
- The conversion for both, G20 and E11, can be based on one- or both-way:
	Both ways (default): Any case is considered "1" (conversion detected) if the qdat diagnosis and the hvdat diagnoses don't match
						(so an individual has a diagnosis stated in qdat which is not confirmed in hvdat, or does not have a diagnosis stated in qdat which is stated in hvdat)
	One way: Only cases that have a diagnosis in hvdat but not in qdat (Pheno_G20 is "0") are considered "1" (conversion detected).
			 This can be used to filter e.g., for individuals that likely developed e.g. G20 after questionnaire inclusion.
			 To use this option add oneway_G20 or oneway_E11 after the -dt flag. If other qdat diagnosis columns are requested, it can simply be listed among them.
	Other way: Only cases that do not have a diagnosis in hvdat but have/state this diagnosis in qdat (Pheno_E11/Diabetes is "1") are considered "1" (conversion detected).
			 This can be used to filter e.g., for individuals that stated to have Diabetes but have no confirmed diagnosis of this in hvdat.
			 To use this option add onewayother_G20 or onewayother_E11 after the -dt flag. If other qdat diagnosis columns are requested, it can simply be listed among them.




Pharma table:
- filtered based on subnamn
