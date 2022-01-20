# import pandas with shortcut 'pd'
import pandas as pd  
  
# read_csv function which is used to read the required CSV file
data = pd.read_csv('CHEOPS_Science_Team_new.csv')
  
# display 
print("Original 'input.csv' CSV Data: \n")
print(data)
  
# drop function which is used in removing or deleting rows or columns from the CSV files
data.drop(['EMAIL','NDA', 'PhD', 'WG', 'Related to Science Enablers (ST link)','Related to CHEOPS Papers (NAME)',
'INSTITUT','Inherited country','joint','Related to CHEOPS Paper (Property)', 'sponsor','Country','NDA check'], 
inplace=True, axis=1)
  
#NDA, 

# display 
print("\nCSV Data after deleting columns:\n")
print(data)

# write new table
data.to_csv('CHEOPS_Science_Team.csv', index=False)