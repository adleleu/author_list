# created on the 10th of October 2020 by Adrien Leleu
# updated on the 18th of January 2021 by Adrien Leleu 
# updated on the 19th of February 2021 by Adrien Leleu 
# updated on the 22nd of May 2021 by Adrien Leleu : now using the csv from the Notion page
# updated on the 2nd of June by C. Broeg: Now allowing for multiple entries in the ID column. 
#                                         Working with full name instead of surname to allow duplicates of surnames
#                                         fully in line with publication policy: added ESAPA, EO (ex officio), MA (mission architect)
#                                         works with MA nominees in Notion table
# updated in January 2022 by C. Broeg and L. Serrano: Adding ORCID ID
#                                                     Orcid ID can be switched on / off by setting flag_oricid = True / False
#                                                     institute command can be given (\inst or \affil or $^)
#                                                     institute list now done using \label{inst:nn} if set with new flag flag_inst_label = True
#                                                     institute list is concatenated with \and instead of \\
# Updated March 2023 by C. Broeg: including use of fields joined and Departed for CST, Associates, 
#                                                     Board, MA to allow for variable team composition.
#                                                     adding variable paper_date to specify timestamp
# updated Sep 2023: read Notion directly from API
#           dependency notion_client added; Install with pip install notion_client
#           User can choose if he/she wants to get the data from Notion, CSV, or both (new configuration option Source_of_author_data)
#           CSV takes preference in case of duplicate Ref_Name entries (use with care, a warning will be given in case of duplicates)
#           CSV file reduced to one line example
#           created configuration file author_list_config.yaml to store all settings and author lists
#           created configuration file notion-server-details.yaml to store private key for Notion access (Get it from plone.)


####################################################################################
#
#       USAGE
#
#  - place file notion-server-details.yaml in same directory (can be obtained from CHEOPS plone site)
#  - edit the configuration file author_list_config.yaml for your choice of authors and preferences
#  - If you use additional authors in a CSV file, edit the example file additional_authors.csv and add your authors
#  - Run the script using python3: >python author_list.py
#
#  The Script will output a number of text files that you can copy into your latex manuscript
#
#
#       PREREQUISITES
#
#   The script depends on the python modules numpy, pandas, notion_client, yaml
#   When using the CSV file, the format of the example must be strictly adhered to 
#   and first name, surname, and address shall not be empty
#
####################################################################################


import numpy as np
import pandas as pd
import unicodedata
from notion_client import Client 
from notion_client.helpers import collect_paginated_api
from pprint import pprint
import yaml, re 

# Please inform C. Broeg or D. Ehrenreich for updates to the Notion page


# Date of the paper (relevant to know which CST members to include automatically)
#
# author_config = {}
# paper_date = datetime(year=2023, month=7, day=3)  # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<   SET PAPER DATE HERE <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

# # Lead Author 
# lead_author='Andrea Fortier'

# # up to 4 Major contributors 
# major_contributors_list=['Attila Simon', 'Christopher Broeg', 'Göran Olofsson', 'Adrien Deline']

# # exactly 4 Science Enablers - rotating from the full list of SE
# science_enablers_list=['Thomas Wilson', 'Pierre Maxted', 'Alexis Brandeker', 'Andrew Collier Cameron'] 

# # for your reference: List of SE as of 8.9.2023 (see Notion page for full list of SE)                    
# science_enablers_list_full=[['Adrien Deline', 'Alexis Brandeker', 'Andrea Fortier', 'Andrew Collier Cameron', 'Anja Bekkelien', 'Attila Simon',
#  'Christopher Broeg', 'David Ehrenreich', 'Didier Queloz', 'Göran Olofsson', 'Hans-Gustav Florén', 'Mathias Beck', 'Monika Lendl',
#  'Nicolas Billot', 'Pascal Guterman', 'Pierre Maxted', 'Sergio Hoyer', 'Sérgio Sousa', 'Thomas Wilson', 'Willy Benz']]

# #significant contributors (max 15%) 
# significant_contributors_list=['Mathias Beck', 'Anja Bekkelien', 'Nicolas Billot', 'Andrea Bonfanti', 'Giovanni Bruno', 'Laetitia Delrez', 'Brice-Olivier Demory', 
#                                'David Futyan', 'Hans-Gustav Florén', 'Maximilian Günther', 'Alexis Heitzmann', 'Sergio Hoyer', 'Kate G. Isaak', 'Sérgio Sousa', 
#                                'Manu Stalport', 'Arnaud Turin', 'Peter Verhoeve'  ]
                               
# # Additional people to add in the alphabetical order (this is an example)
# selected_list=['Gisbert Peter', 'Roland Ottensamer', 'Demetrio Magrin', 'Matteo Munari', 'Amador Lopez Pina', 'David Modrego', 'Pascal Guterman','test man'] 

# # separate list for people nominated by the mission architects:
# MA_nominees = ['Federico Biondi', 'Francesco Ratti', 'Francesco Verrecchia', 'Maximilian Buder', 'Bernd Ulmer']


# # Author information can be taken from Notion DB, From CSV, or from both
# # Use Notion and CSV option to add special authors that are not part of the science team and will not be added to Notion

# Source_of_author_data = 'Notion and CSV'            # 'Notion', 'CSV', 'Notion and CSV'
# filename_CSV = 'CHEOPS_Science_Team.csv' # used for CSV options

# # BEGIN FLAGS to modify output style ===============================================================

# flag_initials    = True # set to False if you want to print full Names, not initials
# flag_orcid       = True # set to False if you don't want the link to orcid ID in the author list
# author_separator = r", " # separator used between authors: ", " or r"\and" 
#                    # latex command for affiliation (choose the one suitable for your journal):
# affil            = r"\inst"   #or one of the following examples:  affil = r"\affil";   affil = r"$^"

# flag_inst_label  = True # how to enumerate the institutes: True: uses \label{inst:nn}, False uses $^{nn}$


# END FLAGS to modify output style ===============================================================


# author_config['flags'] = {}
# author_config['authors'] = {}
# author_config['filenames'] = {}
# author_config['paper_date'] = paper_date
# author_config['authors']['lead_author'] = lead_author
# author_config['authors']['major_contirbutors_list'] = major_contirbutors_list
# author_config['authors']['science_enablers_list'] = science_enablers_list
# author_config['authors']['significant_contributors_list'] = significant_contributors_list
# author_config['authors']['selected_list'] = selected_list
# author_config['authors']['MA_nominees'] = MA_nominees
# author_config['filenames']['Source_of_author_data'] = Source_of_author_data
# author_config['filenames']['filename_CSV'] = filename_CSV
# author_config['flags']['flag_initials'] = flag_initials
# author_config['flags']['flag_orcid'] = flag_orcid
# author_config['flags']['author_separator'] = author_separator
# author_config['flags']['affil'] = affil
# with open("author_list_config.yaml","w") as file_object:
#     yaml.safe_dump(author_config,file_object, allow_unicode=True, default_flow_style=False )

# ID to add to all papers
List_of_ID_to_add = ['CST','Associate','Board', 'EO', 'MA', 'ESAPS']   # all of these IDs are added if paper date is within Joined and Departed date


with open("author_list_config.yaml","r") as file_object:
    author_config = yaml.load(file_object, Loader=yaml.SafeLoader )

paper_date                      = pd.Timestamp(author_config['paper_date'] )
lead_author                     = author_config['authors']['lead_author'] 
major_contributors_list         = author_config['authors']['major_contributors_list'] 
science_enablers_list           = author_config['authors']['science_enablers_list'] 
significant_contributors_list   = author_config['authors']['significant_contributors_list']
selected_list                   = author_config['authors']['selected_list'] 
MA_nominees                     = author_config['authors']['MA_nominees']
Source_of_author_data           = author_config['filenames']['Source_of_author_data']
filename_CSV                    = author_config['filenames']['filename_CSV']
flag_initials                   = author_config['flags']['flag_initials']
flag_orcid                      = author_config['flags']['flag_orcid']
author_separator                = author_config['flags']['author_separator']
affil                           = author_config['flags']['affil']
flag_inst_label                 = author_config['flags']['flag_inst_label']
selected_list.extend(MA_nominees)


def affil_close():
    if affil[0] == '$':
        return r"$"
    else:
        return ""



########################################################################
########################################################################
########################################################################
def find_non_printable_characters(text):
    if not isinstance(text, str):
        return []
    # Use a regular expression to find non-printable characters
    # regexp = r'[^\x20-\x7E\xC0-\xFF\'"’”]'
    regexp = r'[^\x20-\x7E\xA1-\xFF\'"’”\u201C\u201D\u201E\u2018\u2016\u2017]'
    

    non_printable_chars = re.findall(regexp, text)
    if non_printable_chars!= []: print(non_printable_chars)
    return non_printable_chars

def get_CST_DB():

    print("Contacting Notion DB...")
    with open("notion-server-details.yaml","r") as file_object:
        config_dict = yaml.load(file_object, Loader=yaml.SafeLoader)

    client = Client(auth=config_dict['server']['notion_token_cheops']) 
    page_response = collect_paginated_api( client.databases.query,database_id=config_dict['server']['cheops_db_id'])
    print("Data retrieved from Notion.\n")

    Ref_Name = []
    ID = []
    Surname = []
    First_Name = []
    Address = []
    Acknow = []
    Country = []
    EMAIL = []
    Institute = []
    Joined = []
    Departed = []
    ORCID = []
    ID_1 = [] # unique number ID
    id = []   # unique hash ID, used for sponsor crossref
    sponsor = [] # unique hash ID of sponsor, could be multiple

    i=1
    for page in (page_response):
        #ref column
        # print(i, end=' ')
        info = page['properties']['Ref name']['title']
        if len(info)==0: continue
        Ref_Name.append([i['plain_text'] for i in info][0])
        # print(Ref_Name[-1])
        
        #mulit select
        ID.append([i['name'] for i in page['properties']['ID']['multi_select']])
        Country.append([i['name'] for i in page['properties']['Country']['multi_select']])

        #strings
        surname_list = [i['plain_text'] for i in page['properties']['Surname']['rich_text']]
        Surname.append( surname_list[0] if surname_list else "")  # handle empty surname
        First_Name_list = [i['plain_text'] for i in page['properties']['First Name']['rich_text']]
        First_Name.append( First_Name_list[0] if First_Name_list else "")

        entry = [i['plain_text'] for i in page['properties']['Address']['rich_text']]
        if len(entry)==1: entry = entry[0]
        if len(entry)==0: entry = ""
        Address.append(entry)

        entry = [i['plain_text'] for i in page['properties']['Acknow']['rich_text']]
        if len(entry)==1: entry = entry[0]
        if len(entry)==0: entry = ""
        Acknow.append(entry)

        entry = [i['plain_text'] for i in page['properties']['Institute']['rich_text']]
        if len(entry)==1: entry = entry[0]
        if len(entry)==0: entry = ""
        Institute.append(entry)

        entry = [i['plain_text'] for i in page['properties']['ORCID']['rich_text']]
        if len(entry)==1: entry = entry[0]
        if len(entry)==0: entry = None
        ORCID.append(entry)

        #email
        entry =  page['properties']['EMAIL']['email']
        EMAIL.append(entry)

        #dates
        entry = page['properties']['Departed']['date']
        if entry is None:
            Departed.append (entry)
        else:
            Departed.append (entry['start'])

        entry = page['properties']['Joined']['date']
        if entry is None:
            Joined.append (entry)
        else:
            Joined.append (entry['start'])    

        #numbers
        ID_1.append( page['properties']['ID 1']['unique_id']['number'])

        # unique IDs
        id.append(page['id'])

        entry = page['properties']['Sponsor']['relation']
        if entry == []:
            sponsor.append("")
        else:
            sponsor.append([ i['id'] for i in entry])
        i+=1

    table = dict(Ref_Name=Ref_Name, First_Name = First_Name, ID=ID, Surname=Surname, Address=Address, Acknow=Acknow, Country=Country,EMAIL=EMAIL,INSTITUT=Institute, 
    Departed=Departed, Joined=Joined, ORCID=ORCID, ID_1=ID_1, id=id, sponsor=sponsor)
    db= pd.DataFrame.from_dict(table)
    db['Departed'] = pd.to_datetime(db['Departed'])
    db['Joined'] = pd.to_datetime(db['Joined'])



    return db

def load_author_data_from_Notion():
    df = get_CST_DB()
    return df

def load_author_data_from_CSV(filename='CHEOPS_Science_Team.csv'):
    #load the spreadsheet, parse some columns as datetime
    dates = ['Departed', 'Joined']

    df_list1 = pd.read_csv(filename, parse_dates=dates)

    df_list1['ID'].fillna("", inplace=True)  #allow rows without ID
    df_list1['Acknow'].fillna("", inplace=True)  #allow rows without ID

    for i in df_list1.index: 
        df_list1.at[i,'ID'] = df_list1.at[i,'ID'].split(',') 

    df_list1.rename(columns={'Ref name': 'Ref_Name', 'First Name': 'First_Name'}, inplace=True)
    # df_list1.rename(columns={'Ref name': 'Ref_Name', 'Adress': 'Address', 'First Name': 'First_Name'}, inplace=True)
    # pprint(df_list1)
    return df_list1

# Return intials of first names 
def get_initials(fullname):
  "First Name is passed and Initials are returned"

  xs = (fullname)
  name_list = xs.split()

  initials = ""

  digraphs = ['Sz', 'sz', 'Gy', 'gy', 'Cs','cs', 'Dz','dz', 'Zs', 'zs'] # removing ch from digraphs, 'Ch', 'ch']

  for name in name_list:  # go through each name
    comp=name.split('-')
    if len(comp)>1:
        part = comp[0]
        if len(part) > 1 and part[0:2] in digraphs:
            part = part[0:2]
        else:
            part = part[0].upper()
        initials += part
        
        part = comp[1]
        if len(part) > 1 and part[0:2] in digraphs:
            part = part[0:2]
        else:
            part = part[0].upper()
        initials += '.-' + part + '. '
    else:
        if '.' in name:  # if already abbreviated, don't touch.
            initials+= name + ' '
        elif len(name) > 1 and name[0:2] in digraphs:    # not treating ty, ly, ny as they can appear in non-Hungarian names
            initials += name[0].upper()+name[1]+'. '  # append the initial
        else:
            initials += name[0].upper()+'. '  # append the initial

  return re.sub("\s+", "~",  initials[:-1])

# Validate Inputs

print("\n\nWelcome to the author_list tool. \nUsing author data from ", Source_of_author_data,". Writing files to include in LaTeX source ...\n" )

# check if there are duplicate names

assert lead_author not in major_contributors_list, "The lead author should not be in major contributors list"
assert lead_author not in science_enablers_list, "The lead author should not be in science_enablers_list"
assert lead_author not in significant_contributors_list, "The lead author should not be in significant_contributors_list"

assert len(set(major_contributors_list) & set(science_enablers_list))==0, "There must be no common elements in major_contirbutors_list and science_enablers_list"
assert len(set(major_contributors_list) & set(significant_contributors_list))==0, "There must be no common elements in major_contirbutors_list and significant_contributors_list"
assert len(set(science_enablers_list) & set(significant_contributors_list))==0, "There must be no common elements in science_enablers_list and significant_contributors_list"

#initialisation of the lists
first_names=[]
institutes=[]
Family_names=[]
authors_emails=[]
authors_institutes=[]
acknowledgements_always=["CHEOPS is an ESA mission in partnership with Switzerland with important contributions to the payload and the ground segment "+
                   "from Austria, Belgium, France, Germany, Hungary, Italy, Portugal, Spain, Sweden, and the United Kingdom. "+
                   "The CHEOPS Consortium would like to gratefully acknowledge the support received by all the agencies, offices, "+
                   "universities, and industries involved. Their flexibility and willingness to explore new approaches were essential to the success of this mission."
                   +" CHEOPS data analysed in this article will be made available in the CHEOPS mission archive (\\url{https://cheops.unige.ch/archive_browser/})."]
acknowledgements = acknowledgements_always.copy()
institutes_Id=[]


# Non-alphabetical list
authors_nonalpha=[lead_author,]
authors_nonalpha.extend(major_contributors_list)
authors_nonalpha.extend(science_enablers_list)
authors_nonalpha.extend(significant_contributors_list)

flatten = lambda l: [item for sublist in l for item in sublist]

#ensure that all written authors are in the list
manual_author_list = authors_nonalpha.copy()
manual_author_list.extend(selected_list)


#  READ the data of all CHEOPS authors
if Source_of_author_data == 'Notion':
    df_author_information_DB = load_author_data_from_Notion()
elif Source_of_author_data == 'CSV':
    df_author_information_DB = load_author_data_from_CSV(filename=filename_CSV)
elif Source_of_author_data == 'Notion and CSV':
    df_author_information_DB_Notion = load_author_data_from_Notion()
    df_author_information_DB_CSV = load_author_data_from_CSV(filename=filename_CSV)
    
    df= pd.concat([df_author_information_DB_Notion,df_author_information_DB_CSV])
    df=df[df.duplicated(['Ref_Name'])]
    count_row = df.shape[0]
    if count_row>0: print ("Warning: there are ", count_row, " duplicates in CSV. CSV verison is used. It is your responsibility to give correct data.\n" )

    df_author_information_DB= pd.concat([df_author_information_DB_Notion,df_author_information_DB_CSV]).drop_duplicates(subset="Ref_Name", keep='last') # set to 'fist'if you want to give preference to Notion
else:
    assert False, "Please set Source_of_author_data to one of 'Notion', 'CSV', 'Notion_and_CSV'"


#find non-printable characters ==========================================

# Select only string columns
string_columns = df_author_information_DB.select_dtypes(include=['object'])

# Apply the function to the string columns
df_with_non_printable = string_columns.applymap(find_non_printable_characters)


rows_with_non_printable = df_with_non_printable.applymap(lambda x: len(x) > 0)

df_containing_non_printable = df_author_information_DB[rows_with_non_printable.any(axis=1)]
if len(df_containing_non_printable):
    print("\n Warning: Some fields contain non-printing characters:")
    pprint(df_containing_non_printable)
    print("done \n")



# warn for empty entries:
for author in df_author_information_DB['Ref_Name'].tolist():
    # Check if the 'First Name' is NaN for the current author
    mask = (df_author_information_DB['Ref_Name'] == author) & (df_author_information_DB['First_Name'].isna())
    if mask.any():
        # Print a warning message and replace NaN with an empty string
        print(f"Warning: The first name of author {author} is NaN, replacing by ''\n")
    mask = (df_author_information_DB['Ref_Name'] == author) & (df_author_information_DB['Surname'].isna())
    if mask.any():
        # Print a warning message and replace NaN with an empty string
        print(f"Warning: The surname of author {author} is NaN, replacing by ''\n")
# convert empty entries in CSV to ""
# df_author_information_DB['Surname'].fillna('', inplace=True)
# df_author_information_DB['First_Name'].fillna('', inplace=True)
df_author_information_DB['Surname'] = df_author_information_DB['Surname'].fillna('')
df_author_information_DB['First_Name'] = df_author_information_DB['First_Name'].fillna('')

# for i,row in (df_author_information_DB.iterrows()):
#     print(row['Ref_Name'])

# check that science enablers are in the science enablers list
science_enablers_list_full = df_author_information_DB[['SE' in ids for ids in df_author_information_DB['ID'].to_list()]]['Ref_Name'].to_list()
if not set(science_enablers_list).issubset (science_enablers_list_full):
    print("Warning: you have selected a science enabler that is not in the official science enabler list.\n")

df_manual_selected = df_author_information_DB[df_author_information_DB['Ref_Name'].isin(manual_author_list)]

#check if all entries were found
for refname in manual_author_list:
    assert df_author_information_DB['Ref_Name'].str.contains(refname).any()==True, ('Error !!! Missing author "'+refname+'" in the Database. Aborting.')

#add all the members of the listed IDs (for exemple : CST, Board, etc.)

mask = np.zeros(df_author_information_DB.shape[0], dtype=bool)    
for id in List_of_ID_to_add: # check all IDs in the "always in paper id list"  using the dataframe method .apply would have been cleaner...
     mask2 = [] 
     for i,r in df_author_information_DB.iterrows(): 
         mask2.append( (id in r['ID']) and r['Departed'] > paper_date and r['Joined'] < paper_date   )  # add AND with date JOINED and DEPARTED values
     # now OR the mask for each run of IDs to add:
     mask = mask | np.array(mask2) 
# use this mask to get a list of all authors that should be added to every paper and add it to the manually selected authors (there will be duplicates!):
df_manual_selected_plus_all_ST = pd.concat([ df_manual_selected, df_author_information_DB[mask]])   

#create the list of all authors of the paper - in arbitrary sort
all_authors=df_manual_selected_plus_all_ST['Ref_Name'].tolist()




# sort all authors from the spreadsheet and notion in alphabetical order, thanks to P. Maxted!
for ref_name in all_authors:
    name = df_author_information_DB[df_author_information_DB['Ref_Name'] == ref_name].Surname.tolist()[0]
    Family_names.append(name.split('.')[-1])
    
df_manual_selected_plus_all_ST['ORCID'] = df_manual_selected_plus_all_ST['ORCID'].fillna('missing')

nfkd = [unicodedata.normalize('NFKD', s) for s in Family_names] 
no_diacrit = [s.encode('ASCII', 'ignore') for s in nfkd]
Id_sort=sorted(range(len(Family_names)), key=lambda k: no_diacrit[k])
all_authors_sorted=[all_authors[i] for i in Id_sort]

# create the author list: add alphabetical list after the manually placed authors (if they are not already there); this removes all duplicates
authors=authors_nonalpha
for author in all_authors_sorted:
    if author not in authors:
        authors.append(author)

author_ack = {}

for author in authors:
    # Check if the 'First Name' is NaN for the current author
    mask = (df_manual_selected_plus_all_ST['Ref_Name'] == author) & (df_manual_selected_plus_all_ST['First_Name'].isna())
    if mask.any():
        # Print a warning message and replace NaN with an empty string
        print(f"The first name of author {author} is NaN, replacing by ''")
        df_manual_selected_plus_all_ST.loc[mask, 'First_Name'] = ''

    mask = (df_manual_selected_plus_all_ST['Ref_Name'] == author) & (df_manual_selected_plus_all_ST['Surname'].isna())
    if mask.any():
        # Print a warning message and replace NaN with an empty string
        print(f"The surname of author {author} is NaN, replacing by ''")
        df_manual_selected_plus_all_ST.loc[mask, 'Surname'] = ''


for author in authors:
    df_current_author_only=df_manual_selected_plus_all_ST[df_manual_selected_plus_all_ST['Ref_Name']==author]

    if  isinstance(df_current_author_only.iloc[0]['First_Name'],str):
        if (df_current_author_only.iloc[0]['First_Name']).strip()=="": 
            print("Warning: author ",  author, " does not have first name.")

      
for author in authors:
    df_current_author_only=df_manual_selected_plus_all_ST[df_manual_selected_plus_all_ST['Ref_Name']==author]

    
    if flag_initials:
        first_names.append(get_initials(df_current_author_only.iloc[0]['First_Name']))
    else:
        first_names.append(re.sub("\s+","~",df_current_author_only.iloc[0]['First_Name']))
    
    author_institutes_list=df_current_author_only.iloc[0]['Address']
    #print(author_institutes_list)
    author_institutes_fnn = author_institutes_list.split(';')
   
    #create the list for the institute indices next to the name
    author_institutes=[]
    for institute in author_institutes_fnn:
        # if the institute is already in the list, add its index next to the author name
        if institute.strip() in institutes: 
            author_institutes.append(institutes.index(institute.strip()))
        #if not, create a new entry in the institute list
        elif institute.strip()!="":
            institutes.append(institute.strip())
            author_institutes.append(institutes.index(institute.strip()))
            
    authors_institutes.append(author_institutes)
    
    #acknowledgments list following the order of the author list
    author_acknow_list=df_current_author_only.iloc[0]['Acknow']
    if (not isinstance(author_acknow_list, str) and str(author_acknow_list) != 'nan'):
        author_acknow_list = author_acknow_list[0]
    
    if (author_acknow_list != '' ):
        author_acknow_fnn = author_acknow_list.split(';')
        for acknow in author_acknow_fnn:
            ack_stripped = acknow.strip()
            if ack_stripped not in acknowledgements:
                acknowledgements.append(ack_stripped)
                author_ack[ack_stripped] = [author,]                
            else:
                # print(author)
                author_ack[ack_stripped].append(author) 

    

    # List of emails
    author_email=df_current_author_only.iloc[0]['EMAIL']
    authors_emails.append(author_email)

# print (author_ack)

def author_name_to_initials(authors):
    result = []

    for author in authors:
        allnames = author.split(" ")
        initials = ""
        for n in allnames[:-1]:
            initials = initials + n[:1]
        initials = initials + allnames[-1][:2]
        result.append(initials)
    return result

def magic_merge_acknowledgements(author_ack):
    "automagically find similar acknowledgement strings and group authors TA and VV acknowledge..."

        # pick out all that contain acknowledge
    author_ack2 = {}
    author_ack_no_duplicates = {}
    for ack, author in author_ack.items():
        if "acknowledge" in ack.lower():
            idx = ack.lower().index("acknowledge")
            ack_tail = ack[idx+12:].strip()
            if ack_tail in author_ack2:
                # print(author,author_ack2[ack_tail])
                author_ack2[ack_tail].extend(author) 
                # print(author,author_ack2[ack_tail])
            else:   
                author_ack2[ack_tail] = author.copy()
                author_ack_no_duplicates[ack] = author.copy()
                # print(author)
        else:
            author_ack_no_duplicates[ack] = author.copy()

        
    # delete single entries
    dict3={}
    for key, author in author_ack2.items():
        if len(author) > 1:
            dict3[key]=author
    # reconstruct full string with all authors
    dict4={}
    for key, authors in dict3.items():
        authors_initials = (author_name_to_initials(authors))
        text = key
        if len(authors_initials) == 2:
            prefix = authors_initials[0] + " and " + authors_initials[1] + " acknowledge "
        else:
            prefix = ""
            for a in authors_initials[:-2]:
                prefix = prefix + a + ", "
            prefix = prefix + authors_initials[-2] + ", and " + authors_initials[-1] + " acknowledge "
        dict4[prefix + key ] = authors

    def author_in_dict(author, dict0):
        author_in_dict = False
        for ack, auth in dict0.items():
            if author in auth: 
                author_in_dict=True
                return True, ack
        return author_in_dict, None

    # now go through author_ack and check if any names need updates
    result_dict = {}
    for ack, author in author_ack_no_duplicates.items():
        # if len(author) == 1:
            # if author in any value of dict4, replace ack with dict4 version
        if author_in_dict(author[0], dict4)[0]:
            tmp, new_ack = author_in_dict(author[0], dict4)
            result_dict[new_ack] = author_ack_no_duplicates[ack]
            # print("new ack for ", author[0], new_ack)
        else:
            result_dict[ack] = author_ack_no_duplicates[ack]
            # print("keeping entry", author, ack)
    return result_dict,author_ack_no_duplicates

res,author_ack_no_duplicates = (magic_merge_acknowledgements(author_ack=author_ack))
# res = author_ack
author_ack = res

# for ack, auth in author_ack_no_duplicates.items():
#     print(ack, auth)


# get all surnames

surnames = []    
orcid    = [] 

for ref_name in authors:
    name = df_author_information_DB[df_author_information_DB['Ref_Name'] == ref_name].Surname.tolist()[0].strip()
    surnames.append(re.sub("\s+","~",name))

    orcid_number = df_manual_selected_plus_all_ST[df_manual_selected_plus_all_ST['Ref_Name'] == ref_name].ORCID.tolist()[0]
    #print(orcid_number)
    orcid.append(orcid_number)
   

 
# write the author list, with the institutes indexes, on a column
outF = open("authors.txt", "w")
last_author_idx = len(authors) - 1

for l,line in enumerate(authors): 
  line_str=f"{first_names[l]}~{surnames[l]}" + affil + r"{"
  if len(authors_institutes[l])==0:
      line_str+=str(0) + r"}" + affil_close() + ","
  else:
      for k in range(len(authors_institutes[l])):
          line_str+=r"\ref{inst:" + str(authors_institutes[l][k]+1) + "}"  +","
  line_str=line_str[:-1] + r"}" + affil_close()

  if (orcid[l] != 'missing' and flag_orcid):
      line_str+=   "\,$^{\href{https://orcid.org/" + str(orcid[l]) + "}{\protect\includegraphics[height=0.19cm]{figures/orcid.pdf}}}$"

  if l != last_author_idx:
      line_str+=   author_separator
  if l == last_author_idx - 1: 
    #special treatment for second to last author: write , and not ,
    if author_separator[:4]!= r"\and":
        line_str+=   "and"
  outF.writelines(line_str)
  outF.write("\n")

outF.close()
print("File authors.txt written.")
 
# write the author list
outF = open("authors_lin.txt", "w")
for l,name in enumerate(surnames):
  outF.writelines(f"{first_names[l]} {name},\n")
outF.close()
print("File authors_lin.txt written.")


# write the institute list
outF = open("institutes.txt", "w")
# for l,line in zip(range(len(institutes)),institutes):
last_inst_idx = len(institutes) - 1
for l,line in enumerate(institutes):
  if flag_inst_label:
    line_str="\label{inst:"+str(l+1)+"} "+line.rstrip()
  else:
    line_str="$^{"+str(l+1)+"}$ "+line.rstrip()
  if l != last_inst_idx: line_str = line_str +r" \and"
  outF.writelines(line_str)
  outF.write("\n")

outF.close()
print("File institutes.txt written.")


# write the acknowledgement list
outF = open("acknowledgements_magic_merge.txt", "w")
for line in acknowledgements_always:
  toprint=line.rstrip()
  if toprint[-1]=='.':
      outF.writelines(line.rstrip()+" ")
  else:
      outF.writelines(line.rstrip()+". ")
  outF.write("\n")

for ack, author in author_ack.items():
  toprint = ack
  if toprint[-1]=='.':
      outF.writelines(toprint+" ")
  else:
      outF.writelines(toprint+". ")
  outF.write("\n")

outF.close()
print("File acknowledgements_magic_merge.txt written.")

# write the acknowledgement list
outF = open("acknowledgements.txt", "w")
for l,line in zip(range(len(acknowledgements)),acknowledgements):
  toprint=line.rstrip()
  if toprint[-1]=='.':
      outF.writelines(line.rstrip()+" ")
  else:
      outF.writelines(line.rstrip()+". ")
  outF.write("\n")

outF.close()
print("File acknowledgements.txt written.")

# write a list of email addresses
outF = open("emails.txt", "w")
for l,line in zip(range(len(authors_emails)),authors_emails):
  if isinstance(line, str):
    toprint=line.rstrip()
    outF.writelines(toprint+", ")

  #outF.write("\n")

outF.close()
print("File emails.txt written.")
print("Done.")
