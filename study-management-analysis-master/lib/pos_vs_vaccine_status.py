import numpy as np
import pandas as pd


class pos_vs_vaccine():
    def __init__(self, res):
        self.res = res
    
    def positives(self):
        self.pos1 = self.res[(self.res.LINK_ID == 'corona_test_result') & (self.res.VALUECODING_CODE == 'test_result_pos')]
        self.pos1time = self.res[self.res.LINK_ID == 'when_tested_on_demand']
        self.pnew = self.res[self.res.LINK_ID == 'when_tested']
        self.pos1time = pd.concat([self.pos1time, self.pnew])
        self.pos1 = pd.merge(self.pos1, self.pos1time, how = 'left', on = ['ALP_ID', 'AUTHORED'])[['ALP_ID', 'AUTHORED', 'VALUE_y']]
        self.pos1.columns = ['ALP_ID', 'AUTHORED', 'when_tested_positive']
        self.pos2 = self.res[(self.res.LINK_ID == 'when_tested_positive') & (self.res.QUESTIONNAIRE == 'personal_info')][['ALP_ID', 'AUTHORED', 'VALUE']]
        self.pos2.columns = ['ALP_ID', 'AUTHORED', 'when_tested_positive']
        self.pos = pd.concat([self.pos1, self.pos2])
    
    def vaccinated(self):
        self.vaccine1 = self.res[(self.res.LINK_ID == 'which_vaccine_received') & (self.res.QUESTIONNAIRE == 'covid_first_vaccine')][['ALP_ID', 'AUTHORED', 'VALUECODING_CODE']]
        self.vaccine1.columns = ['ALP_ID', 'AUTHORED', 'VACCINE1']
        self.vac1time = self.res[(self.res.LINK_ID == 'when_vaccinated_first_time') & (self.res.QUESTIONNAIRE == 'covid_first_vaccine')][['ALP_ID', 'AUTHORED', 'VALUE']]
        self.vac1time.columns = ['ALP_ID', 'AUTHORED', 'VAC1TIME']
        self.vaccine2 = self.res[(self.res.LINK_ID == 'which_vaccine_received') & (self.res.QUESTIONNAIRE == 'covid_second_vaccine')][['ALP_ID', 'AUTHORED', 'VALUECODING_CODE']]
        self.vaccine2.columns = ['ALP_ID', 'AUTHORED', 'VACCINE2']
        self.vac2time = self.res[(self.res.LINK_ID == 'when_vaccinated_second_time') & (self.res.QUESTIONNAIRE == 'covid_second_vaccine')][['ALP_ID', 'AUTHORED', 'VALUE']]
        self.vac2time.columns = ['ALP_ID', 'AUTHORED', 'VAC2TIME']
        self.booster = self.res[(self.res.LINK_ID == 'when_vaccinated_booster') & (self.res.QUESTIONNAIRE == 'covid_booster_vaccine')][['ALP_ID', 'AUTHORED', 'VALUE']]
        self.booster.columns = ['ALP_ID', 'AUTHORED', 'BOOSTER_TIME']
        
        self.vac1 = pd.merge(self.vaccine1, self.vac1time, how = 'left', on = ['ALP_ID', 'AUTHORED'])
        self.vac2 = pd.merge(self.vaccine2, self.vac2time, how = 'left', on = ['ALP_ID', 'AUTHORED'])
        self.vac = pd.merge(self.vac1, self.vac2, how = 'left', on = ['ALP_ID', 'AUTHORED'])
        self.vac = pd.merge(self.vac, self.booster, how = 'left', on = ['ALP_ID', 'AUTHORED'])
    
    def final_df(self):
        self.df = pd.merge(self.pos, self.vac, how = 'left', on = ['ALP_ID'])
        self.df = self.df[~self.df.when_tested_positive.isna()]
        self.first_test_date = self.df[['ALP_ID', 'when_tested_positive']].groupby(['ALP_ID'], as_index = False).min()
        self.first_test_date.columns = ['ALP_ID', 'first_test_date']
        self.df = pd.merge(self.df, self.first_test_date, how = 'left', on = ['ALP_ID'])
        
        self.df['when_tested_positive'] = pd.to_datetime(self.df['when_tested_positive'], errors = 'ignore').dt.date
        self.df['VAC1TIME'] = pd.to_datetime(self.df['VAC1TIME'], errors = 'ignore').dt.date
        self.df['VAC2TIME'] = pd.to_datetime(self.df['VAC2TIME'], errors = 'ignore').dt.date
        self.df['BOOSTER_TIME'] = pd.to_datetime(self.df['BOOSTER_TIME'], errors = 'ignore').dt.date
        self.df['first_test_date'] = pd.to_datetime(self.df['first_test_date'], errors = 'ignore').dt.date
        
    
    def get_status(self, row):
        if (row['when_tested_positive'] - row['first_test_date']).days > 0 & (row['when_tested_positive'] - row['first_test_date']).days<180:
            return "infected"
        elif row['VACCINE1'] != row['VACCINE1']:
            return "unvaccinated"
        elif (row['VACCINE1'] == 'johnson') & (14<(row['when_tested_positive'] - row['VAC1TIME']).days <180):
            return "fully_vaccinated"
        elif (row['VACCINE1'] == 'johnson') & ((row['when_tested_positive'] - row['VAC1TIME']).days <14 | (row['when_tested_positive'] - row['VAC1TIME']).days >180):
            return "partially_vaccinated"
        elif (row['VACCINE1'] == 'johnson') & ((row['when_tested_positive'] - row['VAC1TIME']).days <0):
            return "unvaccinated"
    
    ## SECOND VACCINE
        elif pd.notnull(row['VAC2TIME']):
            if 14<(row['when_tested_positive'] - row['VAC2TIME']).days <180:
                return "fully_vaccinated"
            elif (row['when_tested_positive'] - row['VAC1TIME']).days <0:
                return "unvaccinated"
            else:
                return "partially_vaccinated"
        
    
        ## ONLY ONE VACCINE
        elif (row['VACCINE1'] != 'johnson') & (row['VACCINE2'] != row['VACCINE2']) & (0<=(row['when_tested_positive'] - row['VAC1TIME']).days <180):
            return 'partially_vaccinated'

        elif (row['VACCINE1'] != 'johnson') & (row['VACCINE2'] != row['VACCINE2']) & ((row['when_tested_positive'] - row['VAC1TIME']).days <0):
            return 'unvaccinated'

    
        #BOOSTER
        elif pd.notnull(row['BOOSTER_TIME']):
            if 0 < row['when_tested_positive'] - row['BOOSTER_TIME'] <= 180:
                return "fully_vaccinated"
            else:
                return "partially_vaccinated"

        
    def get(self):
        self.positives()
        self.vaccinated()
        self.final_df()
        self.df['status'] = self.df.apply(self.get_status, axis = 1)
        return self
    
    
    
    
    
    
    
    
class all_vs_vaccine():
    def __init__(self, res):
        self.res = res

    def positives(self):
        self.pos1 = self.res[(self.res.LINK_ID == 'corona_test_result')]
        self.pos1time = self.res[self.res.LINK_ID == 'when_tested_on_demand']
        self.pnew = self.res[self.res.LINK_ID == 'when_tested']
        self.pos1time = pd.concat([self.pos1time, self.pnew])
        self.pos1 = pd.merge(self.pos1, self.pos1time, how = 'left', on = ['ALP_ID', 'AUTHORED'])[['ALP_ID', 'AUTHORED', 'VALUE_y']]
        self.pos1.columns = ['ALP_ID', 'AUTHORED', 'when_tested_positive']
        self.pos2 = self.res[(self.res.LINK_ID == 'when_tested_positive') & (self.res.QUESTIONNAIRE == 'personal_info')][['ALP_ID', 'AUTHORED', 'VALUE']]
        self.pos2.columns = ['ALP_ID', 'AUTHORED', 'when_tested_positive']
        self.pos = pd.concat([self.pos1, self.pos2])

    def vaccinated(self):
        self.vaccine1 = self.res[(self.res.LINK_ID == 'which_vaccine_received') & (self.res.QUESTIONNAIRE == 'covid_first_vaccine')][['ALP_ID', 'AUTHORED', 'VALUECODING_CODE']]
        self.vaccine1.columns = ['ALP_ID', 'AUTHORED', 'VACCINE1']
        self.vac1time = self.res[(self.res.LINK_ID == 'when_vaccinated_first_time') & (self.res.QUESTIONNAIRE == 'covid_first_vaccine')][['ALP_ID', 'AUTHORED', 'VALUE']]
        self.vac1time.columns = ['ALP_ID', 'AUTHORED', 'VAC1TIME']
        self.vaccine2 = self.res[(self.res.LINK_ID == 'which_vaccine_received') & (self.res.QUESTIONNAIRE == 'covid_second_vaccine')][['ALP_ID', 'AUTHORED', 'VALUECODING_CODE']]
        self.vaccine2.columns = ['ALP_ID', 'AUTHORED', 'VACCINE2']
        self.vac2time = self.res[(self.res.LINK_ID == 'when_vaccinated_second_time') & (self.res.QUESTIONNAIRE == 'covid_second_vaccine')][['ALP_ID', 'AUTHORED', 'VALUE']]
        self.vac2time.columns = ['ALP_ID', 'AUTHORED', 'VAC2TIME']
        self.booster = self.res[(self.res.LINK_ID == 'when_vaccinated_second_time') & (self.res.QUESTIONNAIRE == 'covid_booster_vaccine')][['ALP_ID', 'AUTHORED', 'VALUE']]
        self.booster.columns = ['ALP_ID', 'AUTHORED', 'BOOSTER_TIME']

        self.vac1 = pd.merge(self.vaccine1, self.vac1time, how = 'left', on = ['ALP_ID', 'AUTHORED'])
        self.vac2 = pd.merge(self.vaccine2, self.vac2time, how = 'left', on = ['ALP_ID', 'AUTHORED'])
        self.vac = pd.merge(self.vac1, self.vac2, how = 'left', on = ['ALP_ID', 'AUTHORED'])
        self.vac = pd.merge(self.vac, self.booster, how = 'left', on = ['ALP_ID', 'AUTHORED'])

    def final_df(self):
        self.df = pd.merge(self.pos, self.vac, how = 'left', on = ['ALP_ID'])
        self.df = self.df[~self.df.when_tested_positive.isna()]
        self.first_test_date = self.df[['ALP_ID', 'when_tested_positive']].groupby(['ALP_ID'], as_index = False).min()
        self.first_test_date.columns = ['ALP_ID', 'first_test_date']
        self.df = pd.merge(self.df, self.first_test_date, how = 'left', on = ['ALP_ID'])

        self.df['when_tested_positive'] = pd.to_datetime(self.df['when_tested_positive'], errors = 'ignore').dt.date
        self.df['VAC1TIME'] = pd.to_datetime(self.df['VAC1TIME'], errors = 'coerce').dt.date
        self.df['VAC2TIME'] = pd.to_datetime(self.df['VAC2TIME'], errors = 'coerce').dt.date
        self.df['BOOSTER_TIME'] = pd.to_datetime(self.df['BOOSTER_TIME'], errors = 'coerce').dt.date
        self.df['first_test_date'] = pd.to_datetime(self.df['first_test_date'], errors = 'coerce').dt.date


    def get_status(self, row):
        if (((row['when_tested_positive'] - row['first_test_date']).days > 0) & ((row['when_tested_positive'] - row['first_test_date']).days<180)):
            return "infected"
        elif pd.isnull(row['VAC1TIME']):
            return "unvaccinated"
        elif (row['VACCINE1'] == 'johnson') & (14<(row['when_tested_positive'] - row['VAC1TIME']).days <180):
            return "fully_vaccinated"
        elif (row['VACCINE1'] == 'johnson') & ((row['when_tested_positive'] - row['VAC1TIME']).days <14 | (row['when_tested_positive'] - row['VAC1TIME']).days >180):
            return "partially_vaccinated"
        elif (row['VACCINE1'] == 'johnson') & ((row['when_tested_positive'] - row['VAC1TIME']).days <0):
            return "unvaccinated"

        ## SECOND VACCINE
        elif pd.notnull(row['VAC2TIME']):
            if 14<(row['when_tested_positive'] - row['VAC2TIME']).days <180:
                return "fully_vaccinated"
            elif (row['when_tested_positive'] - row['VAC1TIME']).days <0:
                return "unvaccinated"
            else:
                return "partially_vaccinated"


            ## ONLY ONE VACCINE
        elif (row['VACCINE1'] != 'johnson') & (row['VACCINE2'] != row['VACCINE2']) & (0<=(row['when_tested_positive'] - row['VAC1TIME']).days <180) & ((row['VAC1TIME'] - row['first_test_date']).days >=0):
            return 'fully_vaccinated'

        elif (row['VACCINE1'] != 'johnson') & (row['VACCINE2'] != row['VACCINE2']) & (0<=(row['when_tested_positive'] - row['VAC1TIME']).days >=180) & ((row['VAC1TIME'] - row['first_test_date']).days >=0):
            return 'partially_vaccinated'

        elif (row['VACCINE1'] != 'johnson') & (row['VACCINE2'] != row['VACCINE2']) & ((row['when_tested_positive'] - row['VAC1TIME']).days >=0):
            return 'partially_vaccinated'

        elif (row['VACCINE1'] != 'johnson') & (row['VACCINE2'] != row['VACCINE2']) & ((row['when_tested_positive'] - row['VAC1TIME']).days <0):
            return 'unvaccinated'


            #BOOSTER
        elif pd.notnull(row['BOOSTER_TIME']):
            if 0 < row['when_tested_positive'] - row['BOOSTER_TIME'] <= 180:
                return "fully_vaccinated"
            else:
                return "partially_vaccinated"


    def get(self):
        self.positives()
        self.vaccinated()
        self.final_df()
        self.df['status'] = self.df.apply(self.get_status, axis = 1)
        return self



