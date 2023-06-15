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

import numpy as np
import pandas as pd
import unicodedata
import csv
from datetime import datetime

# Please inform C. Broeg for updates to the CSV file 


# Date of the paper (relevant to know which CST members to include automatically)
#
paper_date = datetime(year=2023, month=5, day=1)  # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<   SET PAPER DATE HERE <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

# Lead Author 
lead_author=['Willy Benz']

# up to 4 Major contributors 
major_contirbutors_list=['Anders Erikson',
                         'Sébastien Charnoz',
                         'Andrea Fortier',
                         'Thomas Wilson']


# exactly 4 Science Enablers - rotating from the full list of SE
science_enablers_list=['Attila Simon',
                       'Hans-Gustav Florén',
                       'Sérgio Sousa',
                       'Pierre Maxted'] 
                       
science_enablers_list_full=['Mathias Beck','Anja Bekkelien', 'Willy Benz', 'Nicolas Billot', 'Christopher Broeg', 'Andrew Collier Cameron', 
                            'Adrien Deline', 'David Ehrenreich', 'Hans-Gustav Florén', 'Andrea Fortier', 
                            'David Futyan', 'Pascal Guterman', 'Sergio Hoyer', 'Pierre Maxted', 'Göran Olofsson', 
                            'Didier Queloz', 'Attila Simon', 'Sérgio Sousa', 'Monika Lendl']

#significant contributors (max 15%) 
significant_contributors_list=['Valérie Van Grootel',
                               'Vincent Bourrier',
                               'Gwenaël Boué', 
                               'Adrien Leleu',
                               'Alain Lecavelier des Etangs']
                               

# ID to add to all papers
List_of_ID_to_add = ['CST','Associate','Board', 'EO', 'MA', 'ESAPS']

# Additional people to add in the alphabetical order (this is an example)
selected_list=[ 'Vikash Singh','Giovanni Bruno', 'Jo Ann Egger'] 

# separate list for people nominated by the mission architects:
MA_nominees = ['Federico Biondi', 'Francesco Ratti', 'Francesco Verrecchia', 'Maximilian Buder', 'Thierry de Roche']

selected_list.extend(MA_nominees)

# BEGIN FLAGS to modify output style ===============================================================

flag_initials    = True # set to False if you want to print full Names, not initials
flag_orcid       = True # set to False if you don't want the link to orcid ID in the author list
author_separator = r", " # separator used between authors: ", " or r"\and" 
                   # latex command for affiliation (choose the one suitable for your journal):
affil            = r"\inst"   #or one of the following examples:  affil = r"\affil";   affil = r"$^"

flag_inst_label  = True # how to enumerate the institutes: True: uses \label{inst:nn}, False uses $^{nn}$

# END FLAGS to modify output style ===============================================================

def affil_close():
    if affil[0] == '$':
        return r"$"
    else:
        return ""



########################################################################
########################################################################
########################################################################

#initialisation of the lists
first_names=[]
institutes=[]
Family_names=[]
authors_emails=[]
authors_institutes=[]
acknowledgements_always=["CHEOPS is an ESA mission in partnership with Switzerland with important contributions to the payload and the ground segment "+
                   "from Austria, Belgium, France, Germany, Hungary, Italy, Portugal, Spain, Sweden, and the United Kingdom. "+
                   "The CHEOPS Consortium would like to gratefully acknowledge the support received by all the agencies, offices, "+
                   "universities, and industries involved. Their flexibility and willingness to explore new approaches were essential to the success of this mission."]
acknowledgements = acknowledgements_always.copy()
institutes_Id=[]


# Non-alphabetical list
authors_nonalpha=[lead_author]
authors_nonalpha.append(major_contirbutors_list)
authors_nonalpha.append(science_enablers_list)
authors_nonalpha.append(significant_contributors_list)

flatten = lambda l: [item for sublist in l for item in sublist]

authors_nonalpha=flatten(authors_nonalpha)



#ensure that all written authors are in the list
selected_list=[selected_list,authors_nonalpha]
selected_list=flatten(selected_list)

#load the spreadsheet, parse some columns as datetime
dates = ['Departed', 'joined']

df_list1 = pd.read_csv('CHEOPS_Science_Team.csv', parse_dates=dates)

# fix list by changing ID string to list:
# for i,a in df_list1.iterrows(): 
#     #print (i, df_list1['Ref name'][i],df_list1['ID'][i]) 
#     df_list1['ID'][i] = df_list1['ID'][i].split(',') 


df_list1['ID'] = df_list1['ID'].fillna("")  #allow rows without ID

for i in df_list1.index: 
    df_list1.at[i,'ID'] = df_list1.at[i,'ID'].split(',') 



df_selected=df_list1[df_list1['Ref name'].isin(selected_list)]

#check if all entries were found
for refname in selected_list:
    if df_selected['Ref name'].str.contains(refname).any()==False:
        input('missing '+refname+' in the csv file')

#add all the members of the listed IDs (for exemple : CST, Board, etc.)
#for ID in List_of_ID_to_add:
#    df_selected=df_selected.append(df_list1[df_list1['ID']==ID])

mask = np.zeros(df_list1.shape[0], dtype=bool)    
for id in List_of_ID_to_add: # check all IDs in the "always in paper id list"  using the dataframe method .apply would have been cleaner...
     mask2 = [] 
     for i,r in df_list1.iterrows(): 
         mask2.append( (id in r['ID']) and r['Departed'] > paper_date and r['joined'] < paper_date   )  # add AND with date JOINED and DEPARTED values
     mask = mask | np.array(mask2) 
df_selected = df_selected.append(df_list1[mask])   

#create the list of all authors of the paper
all_authors=df_selected['Ref name'].tolist()

# sort all authors from the spreadsheets in alphabetical order, thanks to P. Maxted!
for ref_name in all_authors:
    name = df_list1[df_list1['Ref name'] == ref_name].Surname.tolist()[0] 
    Family_names.append(name.split('.')[-1])
    
df_selected['ORCID'] = df_selected['ORCID'].fillna('missing')
    
    

nfkd = [unicodedata.normalize('NFKD', s) for s in Family_names] 
no_diacrit = [s.encode('ASCII', 'ignore') for s in nfkd]
Id_sort=sorted(range(len(Family_names)), key=lambda k: no_diacrit[k])
all_authors_sorted=[all_authors[i] for i in Id_sort]


# create the author list
authors=authors_nonalpha
for author in all_authors_sorted:
    if author not in authors:
        authors.append(author)

# Return intials of first names 
def get_initials(fullname):
  xs = (fullname)
  name_list = xs.split()

  initials = ""

  digraphs = ['Sz', 'sz', 'Gy', 'gy', 'Cs','cs', 'Dz','dz', 'Zs', 'zs', 'Ch', 'ch']

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
        if len(name) > 1 and name[0:2] in digraphs:    # not treating ty, ly, ny as they can appear in non-Hungarian names
            initials += name[0].upper()+name[1]+'. '  # append the initial
        else:
            initials += name[0].upper()+'. '  # append the initial

  return initials[:-1]

author_ack = {}
for author in authors:
    print('author',author)
    
    
    author_insistutes_f=df_selected[df_selected['Ref name']==author]
    
    
    if flag_initials:
        first_names.append(get_initials(author_insistutes_f.iloc[0]['First Name']))
    else:
        first_names.append(author_insistutes_f.iloc[0]['First Name'])
    
    author_institutes_list=author_insistutes_f.iloc[0]['Adress']
    #print(author_institutes_list)
    author_institutes_fnn = author_institutes_list.split(';')
   
    #create the list for the institute indices next to the name
    author_institutes=[]
    for institute in author_institutes_fnn:
        # if the institute is already in the list, add its index next to the author name
        if institute.strip() in institutes: 
            author_institutes.append(institutes.index(institute.strip()))
        #if not, create a new entry in the institute list
        else:
            institutes.append(institute.strip())
            author_institutes.append(institutes.index(institute.strip()))
            
    authors_institutes.append(author_institutes)
    
    #acknowledgments list following the order of the author list
    author_acknow_list=author_insistutes_f.iloc[0]['Acknow']
    
    if str(author_acknow_list) != 'nan' :
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
    author_email=author_insistutes_f.iloc[0]['EMAIL']
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
    name = df_list1[df_list1['Ref name'] == ref_name].Surname.tolist()[0].strip()
    surnames.append(name)

    orcid_number = df_selected[df_selected['Ref name'] == ref_name].ORCID.tolist()[0]
    #print(orcid_number)
    orcid.append(orcid_number)
   

 
# write the author list, with the institutes indexes, on a column
outF = open("authors.txt", "w")
last_author_idx = len(authors) - 1
for l,line in enumerate(authors): 
  line_str=f"{first_names[l]} {surnames[l]}" + affil + r"{"
  if len(authors_institutes[l])==0:
      line_str+=str(0) + r"}" + affil_close() + ","
  else:
      for k in range(len(authors_institutes[l])):
          line_str+=str(authors_institutes[l][k]+1)+","
  line_str=line_str[:-1] + r"}" + affil_close()
  if (orcid[l] != 'missing' and flag_orcid):
      line_str+=   " $^{\href{https://orcid.org/" + str(orcid[l]) + "}{\includegraphics[scale=0.5]{figures/orcid.jpg}}}$"
  if l != last_author_idx:
      line_str+=   author_separator
  outF.writelines(line_str)
  outF.write("\n")

outF.close()

 
# write the author list
outF = open("authors_lin.txt", "w")
for l,name in enumerate(surnames):
  outF.writelines(f"{first_names[l]} {name}, ")
outF.close()


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

# write a list of email addresses
outF = open("emails.txt", "w")
for l,line in zip(range(len(authors_emails)),authors_emails):
  toprint=line.rstrip()
  if toprint[-1]=='.':
      outF.writelines(line.rstrip()+" ")
  else:
      outF.writelines(line.rstrip()+", ")
  #outF.write("\n")

outF.close()