# created on the 10th of October 2020 by Adrien Leleu
# updated on the 18th of January 2021 by Adrien Leleu 
# updated on the 19th of February 2021 by Adrien Leleu 
# updated on the 22nd of May 2021 by Adrien Leleu : now using the csv from the Notion page


import numpy as np
import pandas as pd
import unicodedata
import csv


# Ask C. Broeg for the spreadsheet
# if any bug occurs : adrien.leleu@unige.ch


# Lead Author 
lead_author=['Benz']

# 4 Major contributors 

major_contirbutors_list=['Erikson',
                         'Bonfanti',
                         'Ehrenreich',
                         'Charnoz']


# 4 Science Enablers 
science_enablers_list=['Deline',
                       'Broeg',
                       'Billot',
                       'Sousa']
                         


#significant contributors (max 15%) 

significant_contributors_list=['Van Grootel',
                               'Bourrier',
                               'Boué', # 'G. Bou{\'e}' in the spreadsheet
                               'Leleu',
                               'Lecavelier des Etangs']
                               

# ID to add to all papers
List_of_ID_to_add=['CST','Associate']


# Additional people to add in the alphabetical order
selected_list=[ 'Brandeker','Bárczy','Smith','Simon']


# initials : True; Full name : False
flag_initials=True

########################################################################
########################################################################
########################################################################

#initialisation of the lists
first_names=[]
institutes=[]
Family_names=[]
authors_institutes=[]
acknowledgements=["CHEOPS is an ESA mission in partnership with Switzerland with important contributions to the payload and the ground segment "+
                   "from Austria, Belgium, France, Germany, Hungary, Italy, Portugal, Spain, Sweden, and the United Kingdom. "+
                   "The CHEOPS Consortium would like to gratefully acknowledge the support received by all the agencies, offices, "+
                   "universities, and industries involved. Their flexibility and willingness to explore new approaches were essential to the success of this mission."]
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

#load the spreadsheet
df_list1 = pd.read_csv('CHEOPS_Science_Team_new.csv')


df_selected=df_list1[df_list1['Surname'].isin(selected_list)]

#check if all entries were found
for surname in selected_list:
    if df_selected.Surname.str.contains(surname).any()==False:
        input('missing '+surname+' in the csv file')

#add all the members of the listed IDs (for exemple : CST, Board, etc.)
for ID in List_of_ID_to_add:
    df_selected=df_selected.append(df_list1[df_list1['ID']==ID])


#create the list of all authors of the paper
all_authors=df_selected.Surname.tolist()

# sort all authors from the spreadsheets in alphabetical order, thanks to P. Maxted!
for name in all_authors:
    Family_names.append(name.split(' ')[-1])

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

  for name in name_list:  # go through each name
    comp=name.split('-')
    if len(comp)>1:
        initials += comp[0][0].upper()+'.-'+comp[1][0]+'. '
    else:
        initials += name[0].upper()+'. '  # append the initial

  return initials

for author in authors:
    print('author',author)
    
    
    author_insistutes_f=df_selected[df_selected['Surname']==author]
    
    
    if flag_initials:
        first_names.append(get_initials(author_insistutes_f.iloc[0]['First Name']))
    else:
        first_names.append(author_insistutes_f.iloc[0]['First Name'])
    
    author_institutes_list=author_insistutes_f.iloc[0]['Adress']
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
            if acknow.strip() not in acknowledgements:
                acknowledgements.append(acknow.strip())
               
    
   

 
# write the author list, with the institutes indexes, on a column
outF = open("authors.txt", "w")
for l,line in zip(range(len(authors)),authors):
  line_str=first_names[l]+authors[l]+"$^{"
  if len(authors_institutes[l])==0:
      line_str+=str(0)+","
  else:
      for k in range(len(authors_institutes[l])):
          line_str+=str(authors_institutes[l][k]+1)+","
  line_str=line_str[:-1]+"}$, "
  outF.writelines(line_str)
  outF.write("\n")

outF.close()


# write the author list, with the institutes indexes, in a line
outF = open("authors_lin.txt", "w")
for l,line in zip(range(len(authors)),authors):
  outF.writelines(first_names[l]+line+", ")

outF.close()


# write the institute list
outF = open("institutes.txt", "w")
for l,line in zip(range(len(institutes)),institutes):
  line_str="$^{"+str(l+1)+"}$ "+line.rstrip()+"\\\\"
  outF.writelines(line_str)
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

