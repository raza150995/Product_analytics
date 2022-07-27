import numpy as np
import pandas as pd
from datetime import date
from datetime import datetime 

class Engine():
    def __init__(self, res, start_week = 9):
        self.res = res.copy()
        self.start_week = start_week
        # self.res = self.res[self.res.AUTHORED >=date(year,1,1)]

        self.res['week'] = self.res.AUTHORED.apply(lambda x: x.isocalendar()[1])
        self.res['year'] = self.res.AUTHORED.apply(lambda x: x.isocalendar()[0])
        self.res = self.res[((self.res.week >= self.start_week) & (self.res.year == 2021)) | (self.res.year > 2021)]
        max_year = max(self.res.year)
        max_week = max(self.res[self.res.year == max_year]['week'])
        self.total_weeks = (max_year - 2021)*53 + max_week
        self.mat = np.ones((np.unique(self.res.ALP_ID).shape[0], self.total_weeks))*-3  
        self.allIds = np.unique(self.res.ALP_ID)
        self.last_scene = pd.Series(np.ones(len(self.allIds))*-1, index = self.allIds)
        
        
    def matrix(self):
        enroll = 1
        nd = 0
        inactive = -1
        revival = 2
        na = -2
        self.week_lst = ['W'+str(i) for i in range(self.start_week, self.total_weeks)]
        
        for w in range(self.start_week ,self.total_weeks):
            we = w if w<=52 else w-52
            ye = 2022 if w>=53 else 2021
            present = np.unique(self.res[(self.res.week == we) & (self.res.year == ye)].ALP_ID)
            if present.shape[0] == 0:
                continue
            absent = self.allIds[np.invert(np.isin(self.allIds, present))]
            rm = absent[(self.last_scene[absent] == -1).values]
            row_ne = np.isin(self.allIds, rm)
            self.mat[row_ne, w] = na
            idx = np.in1d(absent, rm)
            absent = absent[~idx]
            row_p = np.isin(self.allIds, present)
            row_a = np.isin(self.allIds, absent)
            self.mat[row_p, w] = np.where(self.last_scene[present]>=8, revival, enroll)
            self.last_scene[present] = 0
            self.mat[row_a, w] = np.where(self.last_scene[absent]>=7, inactive, nd )
            self.last_scene[absent]+=1
        
        return self.mat
    
    def get_status(self):
        _ = self.matrix()
        self.revival = []
        self.inactive = []
        self.answering = []
        
        for c, w in enumerate(range(self.start_week+1 ,self.total_weeks)):
            check = self.mat[:, w]
            past = self.mat[:, w-1]
            rev = check[past == -1]
            if rev.shape[0] == 0:
                self.revival.append(0)
            else:
                self.revival.append((np.sum(rev==2)/(rev.shape[0]))*100)
            inactive = check[past==0]
            if inactive.shape[0] == 0:
                self.inactive.append(0)
            else:    
                self.inactive.append((np.sum(inactive == -1)/(inactive.shape[0] + check[past==1].shape[0]))*100)
            ans = check[(past == 1) | (past == 0) | (past == -1)]
            if ans.shape[0] == 0:
                self.answering.append(0)
            else:  
                self.answering.append((np.sum(ans == 1)/(ans.shape[0]))*100)
        return self      