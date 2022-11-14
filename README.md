# author_list

script to automatically generate authors, insitutes, and acknowledgments lists for scientific publications.

Created by Adrien Leleu and modified by Chris Broeg. ORCID update by Luisa Serrano.

# Overview

The author_list tool was mainly devoloped to be used in the frame of the ESA CHEOPS mission for the Science Team publications. It automatically fulfills the CHEOPS publication policy and allows to use a homogenized author database.

## Inputs

### Database of people

The script uses the CSV file containing all members of the CHEOPS Science Team and associated authors ("CHEOPS_Science_Team.csv"). It can in principle be replaced by any other list. Mandatory columns are:

* "Ref name": names to use as reference when building the first and special author list
* "ID": group id that the author belongs to used to identify in `List_of_ID_to_add`, Multiple entries must be separated by ";"
* "ORCID": ORCID ID if available. Linked to author name if flag_orcid = True
* "surname"
* "First name": first name including additional initials
* "Adress": affiliation to print in the article. Multiple entries must be separated by ";"
* "Acknow": acknowledgements. Muliple entries separated by ";"

### Editing the author_list.py

The tool must be configured by editing the python code. The following items have to be edited:

A number of lists must be populated using "Ref name":

* lead_author
* major_contirbutors_list: additional key contributors to the paper (typically up to 4)
* science_enablers_list: 4 science enables chosen from the science_enablers_list_full
* significant_contributors_list: up to 15% listed before the alphabetical list
* MA_nominees: name 5 people selected by the mission architects (will be added to the alphabetical list)
* selected_list: additional authors in the alphabetical order not in `List_of_ID_to_add`

All members of the following group IDs will be added in alphabetical order:
```python
List_of_ID_to_add = ['CST','Associate','Board', 'EO', 'MA', 'ESAPS']
```

These lists define the content and order of the author list. The order will be as in the bullet list above.

In addition, the following configurations are possible:

* flag_initials: set to False if you want to print full Names, not initials
* flag_orcid:  set to False if you don't want the link to orcid ID in the author list
* affil: LaTex command to use for institue  (Replace by your journal needs, e.g. one of the following examples:  affil = r"\affil";   affil = r"$^"

## Output

Simply run the code as

```
> python author_list.py
```

in the same directory as the CSV file and it will output the following files:

* authors.txt: latex code to include in the paper to list the authors.
* authors_lin.txt: simple list of authors
* institutes.txt: latex code to include in the paper for the institues with the appropriate idexes for the author list
* acknowledgements.txt: the string to put for acknowledgements. This part may need some manual editing in case of overlaps of almost similar text.

## Updating the CSV database file

Please make sure that your information in the consortium DB is up-to-date. It will periodically be exported to CSV and pushed to github. Let C. Broeg know in case you need to make updates for your paper.
