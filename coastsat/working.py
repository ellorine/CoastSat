
import pandas as pd 
from datetime import datetime 

##Merge Tide Data ##

## Read in csvs

data1 = pd.read_csv(r"C:\Users\ecarle\OneDrive - MetService\Documents\2_Consutancy\projects\tauranga\data\topex_tauranga_1966-1995.csv", dtype=str)
data2 = pd.read_csv(r"C:\Users\ecarle\OneDrive - MetService\Documents\2_Consutancy\projects\tauranga\data\topex_tauranga_1995-2024.csv", dtype=str)

data1['date'] = pd.to_datetime(data1['date'], format = '%d/%m/%Y %H:%M')
data2['date'] = pd.to_datetime(data2['date'], format = '%d/%m/%Y %H:%M')

#drop pre 1984 data
data1 = data1[data1['date'].dt.year > 1984]

#merge datasets 
merged = pd.concat([data1, data2], ignore_index=True)

#write to csv
merged.to_csv(r"C:\Users\ecarle\OneDrive - MetService\Documents\2_Consutancy\projects\tauranga\data\topex_tauranga_1984-2024.csv",index=False)

