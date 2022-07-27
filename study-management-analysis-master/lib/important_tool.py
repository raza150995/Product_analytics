from helper_tool import helper
from datetime import timedelta,datetime
import pandas as pd
import numpy as np

class important_measures():
    def __init__(self,res, days_to_subtract = 60):
        self.days_to_subtract = days_to_subtract
        self.res = res.copy()
        self.since = (datetime.today() - timedelta(days=days_to_subtract)).date()
        self.h = helper(self.res)
        
    def analysis(self):
        when_tested = self.h.when_tested()
        test_result = self.h.test_result()
        symptoms = self.h.answer("which_new_symptoms", "sym")
        symptoms = symptoms[['ALP_ID', 'AUTHORED', 'sym']]
        
        exposition_sym = self.h.answer("checkin_symptoms_reported", "sym_reported")
        exposition_sym = exposition_sym[exposition_sym.sym_reported == 'yes']
        exposition_sym = exposition_sym[['ALP_ID', 'AUTHORED', 'sym_reported']]
        
        test_yes = self.h.answer("checkin_tests_reported", "test_reported")
        test_yes = test_yes[['ALP_ID', 'AUTHORED', 'test_reported']]
        test_yes = test_yes[test_yes.test_reported== 'yes']
        
        
        
        when_tested['test_date'] = when_tested.test_date.apply(lambda x: pd.to_datetime(x).date())
        self.when_tested = when_tested[when_tested.AUTHORED>=self.since]
        num_test = self.when_tested.groupby("ALP_ID", as_index = False).count()[['ALP_ID','test_date']]
        self.test_result = test_result[test_result.AUTHORED>=self.since]
        test_yes = test_yes[test_yes.AUTHORED>=self.since]
        symptoms = symptoms[symptoms.AUTHORED>=self.since]
        exposition_sym = exposition_sym[exposition_sym.AUTHORED>=self.since]
        
        m = pd.merge(exposition_sym, symptoms, how = 'left', on = ['ALP_ID', 'AUTHORED'])
        m = m.groupby(['ALP_ID','AUTHORED', 'sym_reported'], as_index = False).count()
        
        m2 = pd.merge(test_yes, self.when_tested[['ALP_ID', 'AUTHORED','test_date']], how = 'left', on = ['ALP_ID', 'AUTHORED'])
        m2 = m2.groupby(['ALP_ID','AUTHORED', 'test_reported'], as_index = False).count()
        
        
        print("------------------------TESTS REPORTED----------------------------")
        print()
        print("NUMBER OF TESTS REPORTED IN LAST " + str(self.days_to_subtract) + " DAYS: ", self.when_tested.shape[0])
        print("NUMBER OF UNIQUE PEOPLE REPORTING TESTS IN LAST " + str(self.days_to_subtract) + " DAYS: ", self.when_tested.ALP_ID.unique().shape[0])
        print("NUMBER OF PEOPLE REPORTING MORE THAN 1 TESTS IN LAST " + str(self.days_to_subtract) + " DAYS: ",num_test[num_test.test_date>1].ALP_ID.unique().shape[0])
        print()
        print("number of instances a person said yes in a disclaimer on a specific date", m2.shape[0])
        print("number of times he/she goes on to report the test:", m2[m2.test_date>0].shape[0], "----percentage:", (m2[m2.test_date>0].shape[0]/m2.shape[0])*100)
        
        print()
        print("------------------------TESTS RESULTS----------------------------")
        print()
        
        print("NUMBER OF TEST_RESULTS IN LAST " + str(self.days_to_subtract) + " DAYS: ", self.test_result.shape[0])
        print("NUMBER OF UNIQUE PEOPLE REPORTING TEST_RESULTS IN LAST " + str(self.days_to_subtract) + " DAYS: ", self.test_result.ALP_ID.unique().shape[0])
        print("NUMBER OF POSITIVE TESTS IN LAST "+ str(self.days_to_subtract) + " DAYS: ",self.test_result[self.test_result.covid_result == 'test_result_pos'].shape[0])
        print("NUMBER OF NEGATIVE TESTS IN LAST "+ str(self.days_to_subtract) + " DAYS: ",self.test_result[self.test_result.covid_result == 'test_result_neg'].shape[0])   
        print("NUMBER OF UNIQUE PEOPLE REPORTING POSITIVE TESTS IN LAST "+ str(self.days_to_subtract) + " DAYS: ",self.test_result[self.test_result.covid_result == 'test_result_pos'].ALP_ID.unique().shape[0])
        print("NUMBER OF UNIQUE PEOPLE REPORTING NEGATIVE TESTS IN LAST "+ str(self.days_to_subtract) + " DAYS: ",self.test_result[self.test_result.covid_result == 'test_result_neg'].ALP_ID.unique().shape[0])
        
        print()
        print("------------------------SYMPTOMS TRACKING----------------------------")
        print()
        
        print("NUMBER OF UNIQUE INSTANCE WHERE A PERSON SAID YES IN EXPOSITION ON A SPECIFIC DATE "+ str(self.days_to_subtract) + " DAYS: ", m.shape[0])
        print("NUMBER OF UNIQUE PEOPLE REPORTING SYMPTOMS IN LAST "+ str(self.days_to_subtract) + " DAYS: ",symptoms.ALP_ID.unique().shape[0])
        print("PEOPLE WHO SAID YES IN EXPOSITION AND REPORTED SYMPTOMS IN LAST "+ str(self.days_to_subtract) + " DAYS: ",  m[m.sym>0].shape[0], "----Percentage:", (m[m.sym>0].shape[0]/m.shape[0])*100)
        print("total: ", m.shape[0])