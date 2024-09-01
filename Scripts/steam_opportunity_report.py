from openpyxl import load_workbook
import pandas as pd
import zipfile
import glob
import zipfile
import pickle
import numpy as np
from pathlib import Path
from main import define_config
config_loaded = define_config()

def generate_opp_report_north():
    '''
    Creates a table view for associate input analysis. Difference between First input given for GT loading time and actual start
    time
    :return: press_data_final_output csv
    '''
    path = config_loaded['host_folder']+'Data/Press log/press_data_north.pkl'
    press_log = pd.read_pickle(path)
    print('retrieved for input analysis North')

    press_log['Time_log'] = pd.to_datetime(press_log['Time_log'])
    press_log['Input2'] = pd.to_datetime(press_log['Input2'])
    press_log['Input1'] = press_log['Input1'].astype("string")
    press_log.reset_index(inplace=True, drop=True)
    # press_log.drop('index', axis=1)

    # temp_df = temp_df1.copy(deep=True)

    first_start = 1
    press_log["flag"] = ""
    press_log = press_log.fillna('nan')

    press_log = press_log.sort_values(['Press_no', 'Time_log'])
    press_log.reset_index(inplace=True, drop=True)

    new_temp_df = press_log['flag']

    for i, row in press_log.iterrows():
        '''
        creates start and stop of press input given time (input2 in presslog column) and actual 
        start time.
        '''
        try:
            # print(',,,',i)
            if row[0][-2:] == '_L':
                if row['Input1'] != 'nan' and row['STEP_NUMBER_LHS'] == 0 and first_start == 1:
                    new_temp_df.iloc[i] = "start"
                    first_start = 0
                    print(row['Press_no'])
                elif press_log.iloc[i + 1]['Input1'] == 'nan' and first_start == 0 and \
                        (press_log.iloc[i + 1]['STEP_NUMBER_LHS'] > 0 or press_log.iloc[i + 2]['STEP_NUMBER_LHS'] > 0):
                    new_temp_df.iloc[i] = "end"
                    first_start = 1
                else:
                    new_temp_df.iloc[i] = ""
            elif row[0][-2:] == '_R':
                if row['Input1'] != 'nan' and row['STEP_NUMBER_RHS'] == 0 and first_start == 1:
                    new_temp_df.iloc[i] = "start"
                    first_start = 0
                    print(row['Press_no'])
                elif press_log.iloc[i + 1]['Input1'] == 'nan' and first_start == 0 and \
                        (press_log.iloc[i + 1]['STEP_NUMBER_RHS'] > 0 or press_log.iloc[i + 2]['STEP_NUMBER_RHS'] > 0):
                    new_temp_df.iloc[i] = "end"
                    first_start = 1
                else:
                    new_temp_df.iloc[i] = ""
            else:
                if row['Input1'] != 'nan' and row['STEP_NUMBER_RHS'] == 0 and row[
                    'STEP_NUMBER_LHS'] == 0 and first_start == 1:
                    new_temp_df.iloc[i] = "start"
                    first_start = 0
                    print(row['Press_no'])
                elif press_log.iloc[i + 1]['Input1'] == 'nan' and first_start == 0 and (
                        press_log.iloc[i + 1]['STEP_NUMBER_RHS'] > 0 or press_log.iloc[i + 2][
                    'STEP_NUMBER_RHS'] > 0 or
                        press_log.iloc[i + 1]['STEP_NUMBER_LHS'] > 0 or press_log.iloc[i + 2]['STEP_NUMBER_LHS'] > 0):
                    new_temp_df.iloc[i] = "end"
                    first_start = 1
                # elif press_log.iloc[i + 1]['Input1'] != 'nan' and first_start == 0 and press_log.iloc[i + 1]['Press_no'] != press_log.iloc[i]['Press_no']:
                #     new_temp_df.iloc[i] = "end"
                #     first_start=1
                else:
                    new_temp_df.iloc[i] = ""

        except Exception as e:
            print(".........", e)
            pass

    new_temp_df.reset_index(inplace=True, drop=True)
    press_log['flag'] = new_temp_df

    import numpy as np
    import datetime
    press_log['Time_log'] = pd.to_datetime(press_log['Time_log'])
    press_log['shift_log'] = press_log['Time_log'] - datetime.timedelta(minutes=7 * 60)
    press_log['Shift'] = press_log['shift_log'].astype(str).str.strip().str[11:13]
    press_log['Date'] = press_log['shift_log'].astype(str).str.strip().str[:10]
    # Allocating shifts =======================================================================================
    shift_c = ['16', '17', '18', '19', '20', '21', '22', '23']
    shift_a = ['00', '01', '02', '03', '04', '05', '06', '07']
    shift_b = ['08', '09', '10', '11', '12', '13', '14', '15']

    press_log['Shift'] = np.where(press_log['Shift'].isin(shift_a), 'Shift_A', press_log['Shift'])
    press_log['Shift'] = np.where(press_log['Shift'].isin(shift_b), 'Shift_B', press_log['Shift'])
    press_log['Shift'] = np.where(press_log['Shift'].isin(shift_c), 'Shift_C', press_log['Shift'])

    #writing a csv file for raw data download
    temp_df1 = press_log[press_log['flag'] != ""]
    temp_df1['Actual_Start_Time'] = temp_df1['Time_log'].shift(-1)
    temp_df1.to_pickle(config_loaded['host_folder']+'Data/Press log/press_data_output_north.pkl')

    #creating file table download csv
    #output_df = pd.DataFrame(columns=['Press_no', 'Expected Start Time', 'Expected Start Time Entered Time', 'Time_log', 'time_diff','Actual_Start_Time'])
    output_df = pd.DataFrame(columns=['Press_no','Date','Shift','Reason', 'Expected Start Time', 'Expected Start Time Entered Time', 'Time_log', 'time_diff','Actual_Start_Time','potential_time_diff'])
    temp_df1 = temp_df1.reset_index()
    dict1 = dict()
    for press in temp_df1['Press_no'].unique():
        temp_df2 = temp_df1.loc[temp_df1['Press_no'] == press]
        for i, row in temp_df2.iterrows():
            print(row)
            if row['flag'] == 'start' and i + 1 <= temp_df1.shape[0] - 1:
                # print(row)
                time_diff = (pd.to_datetime(temp_df1.iloc[i + 1]['Time_log']) - pd.to_datetime(
                    temp_df1.iloc[i]['Input2'])).total_seconds() / 60
                potential_time_diff = (pd.to_datetime(temp_df1.iloc[i + 1]['Time_log']) - pd.to_datetime(
                    temp_df1.iloc[i]['Input3'])).total_seconds() / 60
                dict1['Press_no'] = row['Press_no']
                dict1['Date'] = row['Date']
                dict1['Shift'] = row['Shift']
                dict1['Reason'] = row['Input1']
                dict1['Expected Start Time'] = row['Input2']
                dict1['Expected Start Time Entered Time'] = row['Input3']
                dict1['Time_log'] = row['Time_log']
                dict1['time_diff'] = time_diff
                dict1['potential_time_diff'] = potential_time_diff
                dict1['Actual_Start_Time'] = row['Actual_Start_Time']
                output_df = output_df.append(dict1, ignore_index=True)
    pd.set_option('display.max_columns', None)
    output_df['Extended Steam Mins'] = np.where(output_df['time_diff'] > 0, output_df['time_diff'], 0)
    output_df['Potential cut off'] = np.where(output_df['potential_time_diff'] > 0, output_df['potential_time_diff'], 0)
    output_df['Opportunity Loss'] = np.where(output_df['time_diff'] > 0, output_df['time_diff'], 0)
    output_df = output_df.drop(['Time_log', 'time_diff', 'potential_time_diff'], axis=1)
    output_df = output_df.dropna()  # dropping index out of row for display
    output_df = output_df.sort_values(by='Expected Start Time', ascending=False)
    #taking shift of timelog to calculate the actual start time

    #output_df['Opportunity Loss'] = np.where(output_df['time_diff'] > 0, output_df['time_diff'], 0)
    #output_df = output_df.drop(['Time_log', 'time_diff'], axis=1)
    #output_df = output_df.dropna() #dropping index out of row for display
    output_df.to_csv(config_loaded['host_folder']+'Data/Press log/press_data_final_output_north.csv', index=False)
    print("Completed North")

def generate_opp_report_south():
    '''
    Creates a table view for associate input analysis. Difference between First input given for GT loading time and actual start
    time
    :return: press_data_final_output csv
    '''
    path = config_loaded['host_folder'] + 'Data/Press log/press_data_south.pkl'
    press_log = pd.read_pickle(path)
    print('retrieved for input analysis South')

    press_log['Time_log'] = pd.to_datetime(press_log['Time_log'])
    press_log['Input2'] = pd.to_datetime(press_log['Input2'])
    press_log['Input1'] = press_log['Input1'].astype("string")
    press_log.reset_index(inplace=True, drop=True)
    # press_log.drop('index', axis=1)

    # temp_df = temp_df1.copy(deep=True)

    first_start = 1
    press_log["flag"] = ""
    press_log = press_log.fillna('nan')

    press_log = press_log.sort_values(['Press_no', 'Time_log'])
    press_log.reset_index(inplace=True, drop=True)

    new_temp_df = press_log['flag']
    for i, row in press_log.iterrows():
        '''
        creates start and stop of press input given time (input2 in presslog column) and actual 
        start time.
        '''
        try:
            # print(',,,',i)
            if row[0][-2:] == '_L':
                if row['Input1'] != 'nan' and row['STEP_NUMBER_LHS'] == 0 and first_start == 1:
                    new_temp_df.iloc[i] = "start"
                    first_start = 0
                    print(row['Press_no'])
                elif press_log.iloc[i + 1]['Input1'] == 'nan' and first_start == 0 and \
                        (press_log.iloc[i + 1]['STEP_NUMBER_LHS'] != 0 or press_log.iloc[i + 2][
                            'STEP_NUMBER_LHS'] != 0):
                    new_temp_df.iloc[i] = "end"
                    first_start = 1
                else:
                    new_temp_df.iloc[i] = ""
            elif row[0][-2:] == '_R':
                if row['Input1'] != 'nan' and row['STEP_NUMBER_RHS'] == 0 and first_start == 1:
                    new_temp_df.iloc[i] = "start"
                    first_start = 0
                    print(row['Press_no'])
                elif press_log.iloc[i + 1]['Input1'] == 'nan' and first_start == 0 and \
                        (press_log.iloc[i + 1]['STEP_NUMBER_RHS'] != 0 or press_log.iloc[i + 2][
                            'STEP_NUMBER_RHS'] != 0):
                    new_temp_df.iloc[i] = "end"
                    first_start = 1
                else:
                    new_temp_df.iloc[i] = ""
            else:
                if row['Input1'] != 'nan' and row['STEP_NUMBER_RHS'] == 0 and row[
                    'STEP_NUMBER_LHS'] == 0 and first_start == 1:
                    new_temp_df.iloc[i] = "start"
                    first_start = 0
                    print(row['Press_no'])
                elif press_log.iloc[i + 1]['Input1'] == 'nan' and first_start == 0 and (
                        press_log.iloc[i + 1]['STEP_NUMBER_RHS'] != 0 or press_log.iloc[i + 2][
                    'STEP_NUMBER_RHS'] != 0 or
                        press_log.iloc[i + 1]['STEP_NUMBER_LHS'] != 0 or press_log.iloc[i + 2]['STEP_NUMBER_LHS'] != 0):
                    new_temp_df.iloc[i] = "end"
                    first_start = 1
                # elif press_log.iloc[i + 1]['Input1'] != 'nan' and first_start == 0 and press_log.iloc[i + 1]['Press_no'] != press_log.iloc[i]['Press_no']:
                #     new_temp_df.iloc[i] = "end"
                #     first_start=1
                else:
                    new_temp_df.iloc[i] = ""

        except Exception as e:
            print(".........", e)
            pass

    new_temp_df.reset_index(inplace=True, drop=True)
    press_log['flag'] = new_temp_df

    import numpy as np
    import datetime
    press_log['Time_log'] = pd.to_datetime(press_log['Time_log'])
    press_log['shift_log'] = press_log['Time_log'] - datetime.timedelta(minutes=7 * 60)
    press_log['Shift'] = press_log['shift_log'].astype(str).str.strip().str[11:13]
    press_log['Date'] = press_log['shift_log'].astype(str).str.strip().str[:10]
    # Allocating shifts =======================================================================================
    shift_c = ['16', '17', '18', '19', '20', '21', '22', '23']
    shift_a = ['00', '01', '02', '03', '04', '05', '06', '07']
    shift_b = ['08', '09', '10', '11', '12', '13', '14', '15']

    press_log['Shift'] = np.where(press_log['Shift'].isin(shift_a), 'Shift_A', press_log['Shift'])
    press_log['Shift'] = np.where(press_log['Shift'].isin(shift_b), 'Shift_B', press_log['Shift'])
    press_log['Shift'] = np.where(press_log['Shift'].isin(shift_c), 'Shift_C', press_log['Shift'])

    # writing a csv file for raw data download
    temp_df1 = press_log[press_log['flag'] != ""]
    temp_df1['Actual_Start_Time'] = temp_df1['Time_log'].shift(-1)
    temp_df1.to_pickle(config_loaded['host_folder'] + 'Data/Press log/press_data_output_south.pkl')

    # creating file table download csv
    # output_df = pd.DataFrame(columns=['Press_no', 'Expected Start Time', 'Expected Start Time Entered Time', 'Time_log', 'time_diff','Actual_Start_Time'])
    output_df = pd.DataFrame(
        columns=['Press_no', 'Date', 'Shift', 'Reason', 'Expected Start Time', 'Expected Start Time Entered Time',
                 'Time_log', 'time_diff', 'Actual_Start_Time', 'potential_time_diff'])
    temp_df1 = temp_df1.reset_index()
    dict1 = dict()

    for press in temp_df1['Press_no'].unique():
        temp_df2 = temp_df1.loc[temp_df1['Press_no'] == press]
        for i, row in temp_df2.iterrows():
            print(row)
            if row['flag'] == 'start' and i + 1 <= temp_df1.shape[0] - 1:
                # print(row)
                time_diff = (pd.to_datetime(temp_df1.iloc[i + 1]['Time_log']) - pd.to_datetime(
                    temp_df1.iloc[i]['Input2'])).total_seconds() / 60
                potential_time_diff = (pd.to_datetime(temp_df1.iloc[i + 1]['Time_log']) - pd.to_datetime(
                    temp_df1.iloc[i]['Input3'])).total_seconds() / 60
                dict1['Press_no'] = row['Press_no']
                dict1['Date'] = row['Date']
                dict1['Shift'] = row['Shift']
                dict1['Reason'] = row['Input1']
                dict1['Expected Start Time'] = row['Input2']
                dict1['Expected Start Time Entered Time'] = row['Input3']
                dict1['Time_log'] = row['Time_log']
                dict1['time_diff'] = time_diff
                dict1['potential_time_diff'] = potential_time_diff
                dict1['Actual_Start_Time'] = row['Actual_Start_Time']
                output_df = output_df.append(dict1, ignore_index=True)
    pd.set_option('display.max_columns', None)
    # taking shift of timelog to calculate the actual start time
    output_df['Extended Steam Mins'] = np.where(output_df['time_diff'] > 0, output_df['time_diff'], 0)
    output_df['Potential cut off'] = np.where(output_df['potential_time_diff'] > 0, output_df['potential_time_diff'], 0)
    output_df['Opportunity Loss'] = np.where(output_df['time_diff'] > 0, output_df['time_diff'], 0)
    output_df = output_df.drop(['Time_log', 'time_diff', 'potential_time_diff'], axis=1)
    output_df = output_df.dropna()  # dropping index out of row for display
    output_df = output_df.sort_values(by='Expected Start Time', ascending=False)
    # taking shift of timelog to calculate the actual start time

    output_df.to_csv(config_loaded['host_folder'] + 'Data/Press log/press_data_final_output_south.csv', index=False)
    print("Completed South")