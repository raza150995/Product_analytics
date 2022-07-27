import numpy as np
import pandas as pd
import datetime
from datetime import date
from datetime import timedelta
import math

class date_analysis():
    
    # _from must have a syntax: 'ddmmyyyy'
    
    def __init__(self, res, _from, to = 0):
        self.res = res
        self._from = datetime.datetime.strptime(_from, "%d%m%Y").date()
        if ~to:
            self.to = date.today()
        else:
            self.to = to
        self.numweeks = math.ceil((self.to - self._from).days/7)
        self.dates_lst = [self._from + timedelta(days = i*7) for i in range(self.numweeks)]
        self.col_names = list(map(lambda x: x.isocalendar()[1], self.dates_lst))
        self.col_names=['W'+str(i)+ "-" + 'W'+str(j) for i,j in zip(self.col_names, self.col_names[1:])]
     
    

    def user_analysis(self):
        self.min_dates = self.res[['ALP_ID', 'AUTHORED']].groupby(['ALP_ID'], as_index = False).min()
        self.arr = np.zeros((len(self.dates_lst)-1, len(self.dates_lst)-1))
        self.members = []

        for cnt, (s,e) in enumerate(zip(self.dates_lst, self.dates_lst[1:])):
            #lst = []
            self.ids = self.min_dates[(self.min_dates['AUTHORED'] >= s) & (self.min_dates['AUTHORED'] < e)]['ALP_ID'].values
            self.df = self.res[self.res.ALP_ID.isin(self.ids)]
            for col ,(s1,e1) in  enumerate(zip(self.dates_lst[cnt:], self.dates_lst[cnt+1:])):
                #lst+=self.df[(self.df.AUTHORED >= s1) & (self.df.AUTHORED < e1)]['ALP_ID'].unique().tolist()
                if col == 0:
                    self.arr[cnt, col+cnt] = self.df[(self.df.AUTHORED >= s1) & (self.df.AUTHORED < e1)]['ALP_ID'].unique().shape[0]
                else:
                    self.arr[cnt, col+cnt] = self.df[(self.df.AUTHORED >= s1) & (self.df.AUTHORED < e1) & (self.df.QUESTIONNAIRE== 'covid_exposition')]['ALP_ID'].unique().shape[0]
            #self.members.append(lst)
            
       
        #col_names = [str(i)+ "-" + str(j) for i,j in zip(self.dates_lst, self.dates_lst[1:])]
        #row_names = [str(i)+ "-" + str(j) for i,j in zip(self.dates_lst, self.dates_lst[1:])]
        self.df = pd.DataFrame(self.arr, columns = self.col_names, index = self.col_names)
        return self
            
            
        
    
        
        
    
            