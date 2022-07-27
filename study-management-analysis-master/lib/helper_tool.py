import pandas as pd
import numpy as np
import math


class helper():
    def __init__(self, res):
        self.res = res.copy()
        
    def answer(self, link_id, name):
        self.ans = self.res[(self.res.LINK_ID == link_id)]
        #col_name = 'VALUECODING_CODE' if self.ans.VALUECODING_CODE.iloc[0] else 'VALUE'
        try: 
            if math.isnan(self.ans.VALUECODING_CODE.iloc[0]):
                col_name = 'VALUE'

        except TypeError:
            col_name = 'VALUECODING_CODE'
        self.ans = self.ans[['ALP_ID', 'AUTHORED', 'QUESTIONNAIRE','QUESTIONNAIRE_ID' ,col_name]]
        self.ans.columns = ['ALP_ID', 'AUTHORED', 'QUESTIONNAIRE','qid' ,name]
        return self.ans
    
    def response(self, link_id, questionnaire, name):
        self.ans2 = self.res[(self.res.LINK_ID == link_id) & (self.res.QUESTIONNAIRE == questionnaire)]
        #col_name = 'VALUECODING_CODE' if self.ans.VALUECODING_CODE.iloc[0] else 'VALUE'
        if self.ans2.shape[0] == 0:
            self.ans2 = self.ans2[['ALP_ID', 'AUTHORED', 'QUESTIONNAIRE', 'VALUE']]
            self.ans2.columns = ['ALP_ID', 'AUTHORED', 'QUESTIONNAIRE', name]
            return self.ans2
        try: 
            if math.isnan(self.ans2.VALUECODING_CODE.iloc[0]):
                col_name = 'VALUE'

        except TypeError:
            col_name = 'VALUECODING_CODE'
        self.ans2 = self.ans2[['ALP_ID', 'AUTHORED', 'QUESTIONNAIRE','QUESTIONNAIRE_ID', col_name]]
        self.ans2.columns = ['ALP_ID', 'AUTHORED', 'QUESTIONNAIRE','qid' ,name]
        return self.ans2
    
    def important_dates(self):
        min_dates = self.res[['ALP_ID', "AUTHORED"]].groupby('ALP_ID', as_index = False).min()
        min_dates.columns = ['ALP_ID', "START_DATE"]
        max_dates = self.res[['ALP_ID', "AUTHORED"]].groupby('ALP_ID', as_index = False).max()
        max_dates.columns = ['ALP_ID', "LAST_DONATION"]
        min_dates['START_DATE'] = pd.to_datetime(min_dates['START_DATE']).dt.date
        max_dates['LAST_DONATION'] = pd.to_datetime(max_dates['LAST_DONATION']).dt.date
        min_dates['active_days'] = (max_dates['LAST_DONATION'] - min_dates['START_DATE']).apply(lambda x: x.days)
        self.dates = pd.merge(min_dates, max_dates, how = 'left', on = ['ALP_ID'])
        return self.dates
        
    def when_tested(self, threshold = False, min_test = 2):
        t1 = self.answer('when_tested_positive', 'test_date')
        t2 = self.answer('when_tested_on_demand', 'test_date')
        t3 = self.answer('when_tested', 'test_date')
        t2 = pd.concat([t2, t3])
        self.test = pd.concat([t1, t2])
        if threshold:
            # ids with greater than equal to min_test tests
            ids = self.test.groupby('ALP_ID', as_index = False).count()[['ALP_ID','AUTHORED']].values
            self.ids = ids[ids[:,1]>=min_test, 0]
        return self.test
    
    def how_detected(self):
        how_detected = self.answer("infection_how_detected", 'how_detected')
        how_detected2 = self.answer("what_test_method", 'how_detected')
        self.how_detect = pd.concat([how_detected, how_detected2])
        return self.how_detect
    
    def test_result(self):    
        a = self.answer('corona_test_result', 'covid_result')
        b = self.answer('infection_how_detected', 'how')
        b['how'] = 'test_result_pos'
        b.columns = ['ALP_ID','AUTHORED','QUESTIONNAIRE','qid','covid_result']
        self.result = pd.concat([a,b])
        return self.result
    
    def merged(self):
        how = self.how_detected()
        when = self.when_tested()
        res = self.test_result()
        dates = self.important_dates()
        m1 = pd.merge(when, how, how = 'left', on = ['ALP_ID','AUTHORED', 'QUESTIONNAIRE', 'qid'])
        m2 = pd.merge(m1, res, how = 'left', on = ['ALP_ID','AUTHORED', 'QUESTIONNAIRE', 'qid'])
        self.m3 = pd.merge(m2, dates, how = 'left', on = ['ALP_ID'])
        return self.m3
    
    def vaccine1(self):
        which_vac1 = self.response('which_vaccine_received', 'covid_first_vaccine', 'VAC1')
        when_vac1 = self.response('when_vaccinated_first_time', 'covid_first_vaccine', 'VAC1TIME')
        self.vac1 = pd.merge(which_vac1, when_vac1, how = 'left', on = ['ALP_ID', 'AUTHORED', 'QUESTIONNAIRE', 'qid'])
        self.vac1['VAC1TIME'] = pd.to_datetime(self.vac1['VAC1TIME'], errors = 'coerce').dt.date
        return self.vac1
    
    def vaccine2(self):
        which_vac2 = self.response('which_vaccine_received', 'covid_second_vaccine', 'VAC2')
        when_vac2 = self.response('when_vaccinated_second_time', 'covid_second_vaccine', 'VAC2TIME')
        self.vac2 = pd.merge(which_vac2, when_vac2, how = 'left', on = ['ALP_ID', 'AUTHORED', 'QUESTIONNAIRE', 'qid'])
        self.vac2['VAC2TIME'] = pd.to_datetime(self.vac2['VAC2TIME'], errors = 'coerce').dt.date
        return self.vac2
    
    def booster_time(self):
        self.booster = self.response('when_vaccinated_booster', 'covid_booster_vaccine', 'BOOSTER_TIME')
        self.booster['BOOSTER_TIME'] = pd.to_datetime(self.booster['BOOSTER_TIME'], errors = 'coerce').dt.date
        return self.booster
        
        
    def vac_merger(self):
        _ = self.vaccine1()
        _ = self.vaccine2()
        _ = self.booster_time()
        vac12 = pd.merge(self.vac1, self.vac2, how = 'left', on = ['ALP_ID'])
        vac12b = pd.merge(vac12, self.booster, how = 'left', on = ['ALP_ID'])
        return vac12b
        
        
        
        
        
       

    