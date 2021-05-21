import pandas as pd 
import re
import sys
from sys import argv
df=pd.read_csv(sys.argv[1])
subjects=['Maths','Biology','Physics','English','Chemistry','Hindi']
print("\n")
for column in subjects:
    print("Topper in {} is {}".format(column,re.sub("\[|\]|'","",str(((df.loc[(df[column]==df[column].max()),['Name']]).values.tolist())))))
    
print("\n-------------------------------------------\n")
df['total']=df['Maths']+df['Biology']+df['Physics']+df['Chemistry']+df['Hindi']+df['English']
print("Best students in this class are: ")
best=df.nlargest(3, ['total'])['Name'].values
for i in range(len(best)):
    print(str(i+1)+'.'+str(best[i]))





