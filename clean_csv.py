# import pandas with shortcut 'pd'
import pandas as pd  
  
# read_csv function which is used to read the required CSV file
data = pd.read_csv('CHEOPS Science Team new.csv')
  
# display 
# print("Original 'input.csv' CSV Data: \n")
# print(data)
  
# drop function which is used in removing or deleting rows or columns from the CSV files
# data.drop(['NDA', 'PhD', 'WG', 'Related to Science Enablers (ST link)','Related to CHEOPS Papers (NAME)',
# 'INSTITUT','Inherited country','Related to CHEOPS Paper (Property)', 'sponsor','Country','NDA check'], 
# inplace=True, axis=1)
  
#NDA, 

# display 
# print("\nCSV Data after deleting columns:\n")
# print(data)

cols = ["Ref name","First Name","Surname","ID","joined","Departed","EMAIL","Adress","Acknow","ORCID"]


# write new table
data.to_csv('CHEOPS_Science_Team.csv',columns = cols, index=False)

cols = ["Ref name","ID","joined","Departed","EMAIL"]
print(data[cols])
