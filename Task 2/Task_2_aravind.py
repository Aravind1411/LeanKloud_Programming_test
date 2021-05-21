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



'''Time complexity:
Time complexity is O(nlog(n))

Let row=n,col=m
1.loop goes over all columns for each row => O(n * m) complexity.
2.Calculation of totals does the same => O(n* m)
3.Using nlargest for top 3 students takes O(n*log(3)) 
4.In the given qn m<<n,so overall time complexity is O(nlog(n))'''


