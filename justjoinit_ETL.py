import requests
import json
import os
import pandas as pd
import sys
import argparse
import time
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from forex_python.converter import CurrencyRates
from google.cloud import bigquery

class Extractor:

    def __init__(self, path='', if_test='n'):
        print(datetime.now().strftime("%H:%M:%S") + ': Extractor class initialized...')
        self.path = path
        os.chdir(self.path)
        self.if_test = if_test
        self.get_jjit_data()
        self.export_dataframe()

    def get_jjit_data(self):
        url = "https://justjoin.it/api/offers"
        r = requests.get(url, allow_redirects=True)
        open('offers.json', 'wb').write(r.content)
        print(datetime.now().strftime("%H:%M:%S") + ': Got jj.it data')

    def load_jjit_data(self):
        f = open('offers.json', encoding="utf-8")
        print(datetime.now().strftime("%H:%M:%S") + ': Loaded jj.it data')
        return json.load(f)

    def create_dataframe(self):
        data = []
        data_json = self.load_jjit_data()
        i = 0
        for record in data_json:
            data.append([
                data_json[i]['title'],
                data_json[i]['street'],
                data_json[i]['city'],
                data_json[i]['country_code'],
                data_json[i]['address_text'],
                data_json[i]['marker_icon'],
                data_json[i]['workplace_type'],
                data_json[i]['company_name'],
                data_json[i]['company_url'],
                data_json[i]['company_size'],
                data_json[i]['experience_level'],
                data_json[i]['latitude'],
                data_json[i]['longitude'],
                data_json[i]['published_at'],
                data_json[i]['remote_interview'],
                data_json[i]['id'],
                data_json[i]['employment_types'],
                data_json[i]['company_logo_url'],
                data_json[i]['skills'],
                data_json[i]['remote'],
                data_json[i]['open_to_hire_ukrainians']])
            i += 1
        df = pd.DataFrame(data,
                          columns=['Title',
                                   'Street',
                                   'City',
                                   'Country Code',
                                   'Address Text',
                                   'Marker Icon',
                                   'Workplace Type',
                                   'Company Name',
                                   'Company Url',
                                   'Company Size',
                                   'Experience Level',
                                   'Latitude',
                                   'Longitude',
                                   'Published at',
                                   'Remote interview',
                                   'Id jj.it',
                                   'Employment types',
                                   'Company logo',
                                   'Skills',
                                   'Remote',
                                   'Open to hire Ukrainians'])
        print(datetime.now().strftime("%H:%M:%S") + ': Dataframe created')
        if self.if_test == 'Y':
            return df.iloc[0]
        else:
            return df

    def merge_dataframe_and_remove_duplicates(self):
        df = self.create_dataframe()
        try:
            actual_data = pd.read_csv('data.csv', encoding="utf-8")
        except:
            # if it fails to find the data, it assumes that the dataset is created from scratch
            actual_data = pd.DataFrame()
        df = pd.concat([df, actual_data])
        df['Employment types'] = df['Employment types'].astype(str)
        df['Skills'] = df['Skills'].astype(str)
        df = df.drop_duplicates(subset=['Id jj.it',
                                        'Published at'])
        print(datetime.now().strftime("%H:%M:%S") + ': Dropped duplicates')
        # data below will be used later to optimize transformation time (to apply transformation
        # only for new rows). The program exports it so it can be used for transformation later as well.
        # pivot_data = df[~df['Id jj.it','Published at'].isin(data['Id jj.it','Published at'])]
        # pivot_data = pd.merge(df,actual_data,how='outer',on=['Id jj.it','Published at']).query('_merge != "left"')
        pivot_data = df.append(actual_data).drop_duplicates(subset=['Id jj.it',
                                                                    'Published at'], keep=False)
        pivot_data[['Id jj.it', 'Published at']].to_csv(self.path + '/pivot_data.csv')
        print(datetime.now().strftime("%H:%M:%S") + ': Exported pivot data')
        return df

    def export_dataframe(self):
        # all time
        df = self.merge_dataframe_and_remove_duplicates()
        print(df)
        if self.if_test == 'Y':
            filename = 'test_data.csv'
        else:
            filename = 'data.csv'
        df.to_csv(filename, index=False, encoding="utf-8")
        print(datetime.now().strftime("%H:%M:%S") + ': Exported actual data')
        # daily
        df_daily = self.create_dataframe()
        today = str(date.today())
        filename_daily = self.path + '/daily_data/data_' + today + '.csv'
        df_daily.to_csv(filename_daily, index=False, encoding="utf-8")
        print(datetime.now().strftime("%H:%M:%S") + ': Exported actual daily data')


class Transformer:

    def __init__(self, path='', if_test='n'):
        print(datetime.now().strftime("%H:%M:%S") + ': Transformer class initialized...')
        self.path = path
        os.chdir(self.path)
        self.if_test = if_test
        self.export_transformed_data()

    def get_extracted_data(self):
        if self.if_test == 'Y':
            data = pd.read_csv(self.path + '/test_data.csv', sep=',')
        else:
            data = pd.read_csv(self.path + '/data.csv', sep=',')
        print(datetime.now().strftime("%H:%M:%S") + ': Loaded extracted data')
        return data

    def get_extracted_pivot_data(self):
        try:
            pivot_data = pd.read_csv(self.path + '/pivot_data.csv', sep=',', usecols=['Id jj.it', 'Published at'])
            print(datetime.now().strftime("%H:%M:%S") + ': Loaded pivot data')
        except:
            pivot_data = pd.DataFrame()
            print(datetime.now().strftime("%H:%M:%S") + ': No pivot data found. Proceeding with empty dataframe')
        print('Pivot data: ')
        print(pivot_data)
        return pivot_data

    def get_extracted_recent_transformation_data(self):
        if self.if_test == 'Y':
            try:
                recent_data = pd.read_csv(self.path + '/final_test_data.csv', sep=',')
                print(datetime.now().strftime("%H:%M:%S") + ': Loaded transformed data')
            except:
                recent_data = pd.DataFrame()
                print(datetime.now().strftime(
                    "%H:%M:%S") + ': No recent transformed data found. Proceeding with empty dataframe')
        else:
            try:
                recent_data = pd.read_csv(self.path + '/final_data.csv', sep=',')
                print(datetime.now().strftime("%H:%M:%S") + ': Loaded transformed data')
            except:
                recent_data = pd.DataFrame()
                print(datetime.now().strftime(
                    "%H:%M:%S") + ': No recent transformed data found. Proceeding with empty dataframe')
        print('Recent data: ')
        print(recent_data)
        return recent_data

    def transform_data(self):
        print(datetime.now().strftime("%H:%M:%S") + ': Transforming data...')
        data = self.get_extracted_data()
        print(data)
        pivot_data = self.get_extracted_pivot_data()
        recent_data = self.get_extracted_recent_transformation_data()

        if not recent_data.empty:
            if not pivot_data.empty:
                data = pd.merge(data, pivot_data, how='inner', on=['Id jj.it', 'Published at'])
            else:
                data = data[0:0]

        if not data.empty:
            data['Employment types'] = data['Employment types'].apply(lambda x: eval(x))
            data['Skills'] = data['Skills'].apply(lambda x: eval(x))
            data['Company Size'] = data['Company Size'].str.replace('-', 'STOP')
            data['Company Size'] = data['Company Size'].apply(lambda x: re.sub(r"[^a-zA-Z0-9]", "", str(x)))
            try:
                data[['Company Size from', 'Company Size to']] = data['Company Size'].str.split('STOP', expand=True)
            except:
                data[['Company Size from']]=data['Company Size']
                data[['Company Size to']]=None
            #data['Employment types list'] = ''
            details = pd.DataFrame(columns=['Id jj.it', 'salary.from [permanent]', 'salary.to [permanent]',
                                            'salary.currency [permanent]', 'salary.from [b2b]', 'salary.to [b2b]',
                                            'salary.currency [b2b]', 'salary.from [mandate]', 'salary.to [mandate]',
                                            'salary.currency [mandate]', 'salary.from [other]', 'salary.to [other]',
                                            'salary.currency [other]','currency check'])
            currency_rates = CurrencyRates().get_rates('PLN')
            i = 0
            while i < len(data):
                details.loc[i, 'Id jj.it'] = data['Id jj.it'][i]
                details.loc[i, 'Published at'] = data['Published at'][i]

                # employment
                j = 0
                len_record = len(data['Employment types'][i])
                while j < len_record:
                    if data['Employment types'][i][j]['type'] == 'permanent':
                        #data['Employment types list'][i] = 'permanent'
                        if data['Employment types'][i][j]['salary'] != None:
                            details.loc[i, 'salary.currency [permanent]'] = data['Employment types'][i][j]['salary'][
                                'currency']
                            if details['salary.currency [permanent]'][i]!='pln':
                                try:
                                    details.loc[i, 'salary.from [permanent]'] = data['Employment types'][i][j]['salary']
                                    ['from']/currency_rates[str(details['salary.currency [permanent]'][i]).upper()]
                                    details.loc[i, 'salary.to [permanent]'] = data['Employment types'][i][j]['salary']
                                    ['to']/currency_rates[str(details['salary.currency [permanent]'][i]).upper()]
                                except:
                                    details.loc[i, 'salary.from [permanent]'] = data['Employment types'][i][j]['salary'][
                                        'from']
                                    details.loc[i, 'salary.to [permanent]'] = data['Employment types'][i][j]['salary']['to']
                                    details.loc[i, 'currency check'] = 'unknown'
                            else:
                                details.loc[i, 'salary.from [permanent]'] = data['Employment types'][i][j]['salary'][
                                    'from']
                                details.loc[i, 'salary.to [permanent]'] = data['Employment types'][i][j]['salary']['to']
                    elif data['Employment types'][i][j]['type'] == 'b2b':
                        #if data['Employment types list'][i] == '':
                        #    data['Employment types list'][i] = 'b2b'
                        #else:
                        #    data['Employment types list'][i]=data['Employment types list'][i]+',b2b'
                        if data['Employment types'][i][j]['salary'] != None:
                            details.loc[i, 'salary.currency [b2b]'] = data['Employment types'][i][j]['salary'][
                                'currency']
                            if details['salary.currency [b2b]'][i] != 'pln':
                                try:
                                    details.loc[i, 'salary.from [b2b]'] = data['Employment types'][i][j]['salary']
                                    ['from']/currency_rates[str(details['salary.currency [b2b]'][i]).upper()]
                                    details.loc[i, 'salary.to [b2b]'] = data['Employment types'][i][j]['salary']
                                    ['to']/currency_rates[str(details['salary.currency [b2b]'][i]).upper()]
                                except:
                                    details.loc[i, 'salary.from [b2b]'] = data['Employment types'][i][j]['salary'][
                                        'from']
                                    details.loc[i, 'salary.to [b2b]'] = data['Employment types'][i][j]['salary']['to']
                                    details.loc[i, 'currency check'] = 'unknown'
                            else:
                                details.loc[i, 'salary.from [b2b]'] = data['Employment types'][i][j]['salary'][
                                    'from']
                                details.loc[i, 'salary.to [b2b]'] = data['Employment types'][i][j]['salary']['to']
                    elif data['Employment types'][i][j]['type'] == 'mandate_contract':
                        #if data['Employment types list'][i] == '':
                        #    data['Employment types list'][i] = 'mandate'
                        #else:
                        #    data['Employment types list'][i]=data['Employment types list'][i]+',mandate'
                        if data['Employment types'][i][j]['salary'] != None:
                            details.loc[i, 'salary.currency [mandate]'] = data['Employment types'][i][j]['salary'][
                                'currency']
                            if details['salary.currency [mandate]'][i] != 'pln':
                                try:
                                    details.loc[i, 'salary.from [mandate]'] = data['Employment types'][i][j]['salary']
                                    ['from']/currency_rates[str(details['salary.currency [mandate]'][i]).upper()]
                                    details.loc[i, 'salary.to [mandate]'] = data['Employment types'][i][j]['salary']
                                    ['to']/currency_rates[str(details['salary.currency [mandate]'][i]).upper()]
                                except:
                                    details.loc[i, 'salary.from [mandate]'] = data['Employment types'][i][j]['salary'][
                                        'from']
                                    details.loc[i, 'salary.to [mandate]'] = data['Employment types'][i][j]['salary']['to']
                                    details.loc[i, 'currency check'] = 'unknown'
                            else:
                                details.loc[i, 'salary.from [mandate]'] = data['Employment types'][i][j]['salary'][
                                    'from']
                                details.loc[i, 'salary.to [mandate]'] = data['Employment types'][i][j]['salary']['to']
                    else:
                        #if data['Employment types list'][i] == '':
                        #    data['Employment types list'][i] = 'other'
                        #else:
                        #    data['Employment types list'][i]=data['Employment types list'][i]+',other'
                        if data['Employment types'][i][j]['salary'] != None:
                            details.loc[i, 'salary.currency [other]'] = data['Employment types'][i][j]['salary'][
                                'currency']
                            if details['salary.currency [other]'][i] != 'pln':
                                try:
                                    details.loc[i, 'salary.from [other]'] = data['Employment types'][i][j]['salary']
                                    ['from']/currency_rates[str(details['salary.currency [other]'][i]).upper()]
                                    details.loc[i, 'salary.to [other]'] = data['Employment types'][i][j]['salary']
                                    ['to']/currency_rates[str(details['salary.currency [other]'][i]).upper()]
                                except:
                                    details.loc[i, 'salary.from [mandate]'] = data['Employment types'][i][j]['salary'][
                                       'from']
                                    details.loc[i, 'salary.to [mandate]'] = data['Employment types'][i][j]['salary']['to']
                                    details.loc[i, 'currency check'] = 'unknown'
                            else:
                                details.loc[i, 'salary.from [other]'] = data['Employment types'][i][j]['salary'][
                                    'from']
                                details.loc[i, 'salary.to [other]'] = data['Employment types'][i][j]['salary']['to']
                    j += 1

                # skills
                j = 0
                len_record = len(data['Skills'][i])
                while j < len_record:
                    details.loc[i, 'skills.name_' + str(j)] = data['Skills'][i][j]['name']
                    details.loc[i, 'skills.value_' + str(j)] = data['Skills'][i][j]['level']
                    j += 1
                i += 1

            #data['Employment types']=data['Employment types list']
            data = pd.merge(data, details, how='inner', on=['Id jj.it', 'Published at'])
            #data = data.drop(['Employment types list', 'Skills','Company Size'], axis=1)
            data = data.drop(['Employment types', 'Skills', 'Company Size'], axis=1)
            if not pivot_data.empty:
                if not recent_data.empty:
                    data = data.append(recent_data)
        print(datetime.now().strftime("%H:%M:%S") + ': Data transformed:')
        print(data)
        return data

    def export_transformed_data(self):
        data = self.transform_data()
        if self.if_test == 'Y':
            data.to_csv('final_test_data.csv', index=False, encoding="utf-8")
        elif len(data.columns)==39:
            data.to_csv('final_data.csv', index=False, encoding="utf-8")
        print(datetime.now().strftime("%H:%M:%S") + ': Transformed final data exported.')


class Loader:

    def __init__(self, path='', google_path='', project_id='', full_table_id=''):
        print(datetime.now().strftime("%H:%M:%S") + ': Loader class initialized...')
        self.path = path
        os.chdir(path)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.google_path = google_path
        self.project_id = project_id
        self.full_table_id = full_table_id
        self.load_data_to_bigquery()

    def get_transformed_data(self):
        data = pd.read_csv(self.path + '/final_data.csv', sep=',')
        data.columns = ['Title', 'Street', 'City', 'Country_code', 'Address_text', 'Marker_icon', 'Workplace_type',
                        'Company_name',
                        'Company_url','Experience_level', 'Latitude', 'Longitude', 'Published_at',
                        'Remote_interview', 'Id_jjit',
                        'Company_logo', 'Remote', 'Open_to_hire_Ukrainians', 'Company_size_from',
                        'Company_size_to','salary_from_permanent', 'salary_to_permanent',
                        'salary_currency_permanent', 'salary_from_b2b', 'salary_to_b2b', 'salary_currency_b2b',
                        'salary_from_mandate',
                        'salary_to_mandate', 'salary_currency_mandate', 'salary_from_other', 'salary_to_other',
                        'salary_currency_other', 'currency_check',
                        'skills_name_0', 'skills_value_0', 'skills_name_1', 'skills_value_1', 'skills_name_2',
                        'skills_value_2']
        print(datetime.now().strftime("%H:%M:%S") + ': Loaded transformed final data into class')
        return data

    def load_data_to_bigquery(self):
        data = self.get_transformed_data()
        data['Open_to_hire_Ukrainians'] = data['Open_to_hire_Ukrainians'].astype(
            "string")  # for some reason it didn't work with default boolean type
        data.to_gbq(self.full_table_id, project_id=self.project_id, if_exists='replace')
        print(datetime.now().strftime("%H:%M:%S") + ': Transformed final data should be loaded into BigQuery')


def check_file_permission(path, file):
    print(datetime.now().strftime("%H:%M:%S") + ': Checking file ' + file + ' permission...')
    path_cfp = Path(path + '/' + file)
    try:
        path_cfp.rename(path_cfp)
    except FileNotFoundError:
        pass
        print(datetime.now().strftime(
            "%H:%M:%S") + ': File ' + file + ' does not exist. Data will be saved into new file')
    except PermissionError:
        print(datetime.now().strftime("%H:%M:%S") + ': Error 13: ' + file + ' has permission denied')
        time.sleep(4)
        sys.exit()
    else:
        print(datetime.now().strftime("%H:%M:%S") + ': File ' + file + ' available')


if __name__ == '__main__':
    print(datetime.now().strftime("%H:%M:%S") + ': Program started.')
    parser = argparse.ArgumentParser(description="Get current data from justjoin.it API - and ETL that into BigQuery!",
                                     prog="your_python_script.py",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--path', type=str,
                        help="Enter a file path. Required unconditionally")
    parser.add_argument('--test', type=str, default='n',
                        help="do you want to test the program? [Y/n] If yes, only one record within a data frame will" +
                             " be created. Warning: testing won't work with loading into BigQuery.")
    parser.add_argument('--extract', type=str, default='Y',
                        help="do you want to extract data from API? [Y/n]")
    parser.add_argument('--transform', type=str, default='Y',
                        help="do you want to transform data for an appropriate dataset used in dashboard? [Y/n]")
    parser.add_argument('--load', type=str, default='n',
                        help="do you want to load data into Google BigQuery? [Y/n]")
    parser.add_argument('--google_path', type=str,
                        help="Enter a Google credentials environment path. Required for loading into BigQuery")
    parser.add_argument('--project_id', type=str,
                        help="Enter a project id from BigQuery. Required for loading into BigQuery")
    parser.add_argument('--table_id', type=str,
                        help="Enter a table id from BigQuery. Required for loading into BigQuery")
    args = parser.parse_args()
    params = vars(args)
    print("provided parameters:")
    [print(f"{k} : {v}") for k, v in params.items()]
    # Check if a program can access all files to avoid problems with messy data
    if params['path'] == None:
        print(datetime.now().strftime(
            "%H:%M:%S") + ': Error - path file not specified. For details, enter python justjoinit_etl.py --help')
        time.sleep(4)
        sys.exit()
    if params['load'] != 'n' and params['test'] != 'n':
        print(datetime.now().strftime("%H:%M:%S") + ': Error - Loading into BigQuery is disabled for testing')
        time.sleep(4)
        sys.exit()
    if params['load'] != 'n' and params['google_path'] == None and params['project_id'] == None and params[
        'table_id'] == None:
        print(datetime.now().strftime(
            "%H:%M:%S") + ': Error - google path file not specified while data load into BigQuery is enabled.' +
              ' For details, enter python justjoinit_etl.py --help')
        time.sleep(4)
        sys.exit()
    try:
        path = params['path']
        check_file_permission(path, 'data.csv')
        check_file_permission(path, 'final_data.csv')
        check_file_permission(path, 'pivot_data.csv')
        is_test = 'n' if params['test'] == 'n' else 'Y'
        extract = 'n' if params['extract'] == 'n' else 'Y'
        transform = 'n' if params['transform'] == 'n' else 'Y'
        load = 'n' if params['load'] == 'n' else 'Y'
        google_path = params['google_path']
        project_id = params['project_id']
        full_table_id = params['table_id']
        if extract == 'Y':
            print(datetime.now().strftime("%H:%M:%S") + ': Starting data extraction...')
            start_time = time.time()
            extractor_instance = Extractor(path, is_test)
            end_time = time.time()
            print(datetime.now().strftime("%H:%M:%S") + ': Data extraction completed.')
            print(datetime.now().strftime("%H:%M:%S") + ': Data extraction lasted ' + str(
                end_time - start_time) + ' seconds')
        if transform == 'Y':
            print(datetime.now().strftime("%H:%M:%S") + ': Starting data transformation... (it can take some time)')
            start_time = time.time()
            transformer_instance = Transformer(path, is_test)
            end_time = time.time()
            print(datetime.now().strftime("%H:%M:%S") + ': Data transformation completed.')
            print(datetime.now().strftime("%H:%M:%S") + ': Data transformation lasted ' + str(
                end_time - start_time) + ' seconds')
        if load == 'Y':
            print(datetime.now().strftime("%H:%M:%S") + ': Starting data load to BigQuery...')
            start_time = time.time()
            loader_instance = Loader(path, google_path, project_id, full_table_id)
            end_time = time.time()
            print(datetime.now().strftime("%H:%M:%S") + ': Data load to BigQuery completed.')
            print(datetime.now().strftime("%H:%M:%S") + ': Data load to BigQuery lasted ' + str(
                end_time - start_time) + ' seconds')
        print(datetime.now().strftime("%H:%M:%S") + ': Done!')
        time.sleep(4)
    except Exception as e:
        print(datetime.now().strftime("%H:%M:%S") + ': Exception line {}'.format(sys.exc_info()[-1].tb_lineno))
        print(str(e))
        print('####')
        print('For command details, enter python justjoinit_etl.py --help')
        time.sleep(4)
        sys.exit()