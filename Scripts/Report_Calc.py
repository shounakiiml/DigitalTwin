from openpyxl import load_workbook
import pandas as pd
import numpy as np
import zipfile
import glob
import zipfile
import pickle
import math
import numpy as np
from pathlib import Path
from main import define_config
config_loaded = define_config()
warm_up = config_loaded['Associate Inputs']['Warm Up period']
def excess_idling_report_north():
    '''
    Creates a table view for associate input analysis. Difference between First input given for GT loading time and actual start
    time
    :return: press_data_final_output csv
    '''
    path = config_loaded['host_folder']+'Data/Press log/press_data_north.pkl'
    press_log = pd.read_pickle(path)

    press_log['Time_log'] = pd.to_datetime(press_log['Time_log'])
    first_start = 1
    press_log["flag"] = ""
    press_log = press_log.fillna('nan')
    press_log = press_log.loc[press_log['Time'] != 0]

    press_log = press_log.sort_values(['Press_no', 'Time_log'])
    press_log.reset_index(inplace=True, drop=True)
    #import numpy as np
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

    new_temp_df = press_log['flag']
    time = 0
    shift = 0
    press_log['date_shift'] = press_log['Date'] + press_log['Shift']
    for i in np.arange(len(press_log)):
        try:
            time_new = press_log['Time'][i]
            shift_new=press_log['date_shift'][i]
            if time==0 and shift==0 and time_new != time:
                time = time_new
                shift=shift_new
                new_temp_df.iloc[i] = "start"
            elif time!=0 and time_new!=time:
                time=time_new
                new_temp_df.iloc[i-1] = "end"
                new_temp_df.iloc[i] = "start"
            elif time_new==time:
                shift_old=press_log['date_shift'][i-1]
                if shift_new!=shift_old:
                    new_temp_df.iloc[i - 1] = "end"
                    new_temp_df.iloc[i] = "start"
                else:
                    new_temp_df.iloc[i] = ""

        except:
            n=0
    new_temp_df.reset_index(inplace=True, drop=True)
    press_log['flag'] = new_temp_df



    #writing a csv file for raw data download
    temp_df1 = press_log[press_log['flag'] != ""]
    temp_df1['Actual_Start_Time'] = temp_df1['Time_log'].shift(-1)
    output_df = pd.DataFrame(columns=['Press_no','Date','Shift','Time_log', 'Actual_Start_Time','time_diff'])
    temp_df1 = temp_df1.reset_index()
    dict1 = dict()
    for press in temp_df1['Press_no'].unique():
        temp_df2 = temp_df1.loc[temp_df1['Press_no'] == press]
        for i, row in temp_df2.iterrows():
            if row['flag'] == 'start' and i + 1 <= temp_df1.shape[0] - 1:
                time_diff = round((pd.to_datetime(temp_df1.iloc[i]['Actual_Start_Time']) - pd.to_datetime(
                    temp_df1.iloc[i]['Time_log'])).total_seconds() / 60,0)
                dict1['Press_no'] = row['Press_no']
                dict1['Date'] = row['Date']
                dict1['Shift'] = row['Shift']
                dict1['Time_log'] = row['Time_log']
                dict1['Actual_Start_Time'] = row['Actual_Start_Time']
                dict1['time_diff'] = time_diff
                output_df = output_df.append(dict1, ignore_index=True)
            else:
                n=0
    pd.set_option('display.max_columns', None)
    output_df['Extended Steam Mins'] = np.where(output_df['time_diff'] >= 75, (output_df['time_diff']-warm_up), 0)
    #output_df['Extended Steam Mins'] = np.where(output_df['time_diff'] >= 25, (output_df['time_diff']), 0)
    output_df = output_df.dropna()  # dropping index out of row for display
    print("Completed North Idling Calculation")
    return output_df

def excess_idling_report_south():
    '''
    Creates a table view for associate input analysis. Difference between First input given for GT loading time and actual start
    time
    :return: press_data_final_output csv
    '''
    path = config_loaded['host_folder'] + 'Data/Press log/press_data_south.pkl'
    #path = "C:/Users/Shounak.Pal/PycharmProjects/pythonProject/Data/Press log/press_data_south.pkl"
    press_log = pd.read_pickle(path)

    press_log['Time_log'] = pd.to_datetime(press_log['Time_log'])
    first_start = 1
    press_log["flag"] = ""
    press_log = press_log.fillna('nan')
    press_log = press_log.loc[press_log['Time'] != 0]

    press_log = press_log.sort_values(['Press_no', 'Time_log'])
    press_log.reset_index(inplace=True, drop=True)

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

    new_temp_df = press_log['flag']
    time = 0
    shift = 0
    press_log['date_shift'] = press_log['Date'] + press_log['Shift']
    for i in np.arange(len(press_log)):
        try:
            time_new = press_log['Time'][i]
            shift_new=press_log['date_shift'][i]
            if time==0 and shift==0 and time_new != time:
                time = time_new
                shift=shift_new
                new_temp_df.iloc[i] = "start"
            elif time!=0 and time_new!=time:
                time=time_new
                new_temp_df.iloc[i-1] = "end"
                new_temp_df.iloc[i] = "start"
            elif time_new==time:
                shift_old=press_log['date_shift'][i-1]
                if shift_new!=shift_old:
                    new_temp_df.iloc[i - 1] = "end"
                    new_temp_df.iloc[i] = "start"
                else:
                    new_temp_df.iloc[i] = ""

        except:
            n=0
    new_temp_df.reset_index(inplace=True, drop=True)
    press_log['flag'] = new_temp_df

    #writing a csv file for raw data download
    temp_df1 = press_log[press_log['flag'] != ""]
    temp_df1['Actual_Start_Time'] = temp_df1['Time_log'].shift(-1)
    output_df = pd.DataFrame(columns=['Press_no','Date','Shift','Time_log', 'Actual_Start_Time','time_diff'])
    temp_df1 = temp_df1.reset_index()
    dict1 = dict()
    for press in temp_df1['Press_no'].unique():
        temp_df2 = temp_df1.loc[temp_df1['Press_no'] == press]
        for i, row in temp_df2.iterrows():
            #print(row)
            if row['flag'] == 'start' and i + 1 <= temp_df1.shape[0] - 1:
                # print(row)
                time_diff = round((pd.to_datetime(temp_df1.iloc[i]['Actual_Start_Time']) - pd.to_datetime(
                    temp_df1.iloc[i]['Time_log'])).total_seconds() / 60,0)
                dict1['Press_no'] = row['Press_no']
                dict1['Date'] = row['Date']
                dict1['Shift'] = row['Shift']
                dict1['Time_log'] = row['Time_log']
                dict1['Actual_Start_Time'] = row['Actual_Start_Time']
                dict1['time_diff'] = time_diff
                output_df = output_df.append(dict1, ignore_index=True)
            else:
                n = 0
    pd.set_option('display.max_columns', None)
    output_df['Extended Steam Mins'] = np.where(output_df['time_diff'] >= 75, (output_df['time_diff'] - warm_up), 0)
    #output_df['Extended Steam Mins'] = np.where(output_df['time_diff'] >= 25, output_df['time_diff'], 0)
    output_df = output_df.dropna()  # dropping index out of row for display
    print("Completed South Idling Calculation")
    return output_df

def idle_time_report_north(phase1_listing):
    '''
    Creates a table view for associate input analysis. Difference between First input given for GT loading time and actual start
    time
    :return: press_data_final_output csv
    '''
    path = config_loaded['host_folder'] + 'Data/Press log/press_data_north.pkl'
    #path = "C:/Users/Shounak.Pal/PycharmProjects/pythonProject/Data/Press log/press_data_south.pkl"
    press_log = pd.read_pickle(path)

    press_log['Time_log'] = pd.to_datetime(press_log['Time_log'])
    first_start = 1
    press_log["flag"] = ""
    press_log = press_log.fillna('nan')
    press_log = press_log.loc[(press_log['Color'] != 'grey')]
    ######
    press_idle_rhs = press_log[(press_log['STEP_NUMBER_RHS'] == 0)].sort_values(['Press_no', 'Time_log']).reset_index(drop=True)
    press_idle_lhs = press_log[(press_log['STEP_NUMBER_LHS'] == 0)].sort_values(['Press_no', 'Time_log']).reset_index(drop=True)
    phase_1_press = list(phase1_listing.keys())
    press_log1_lhs = press_idle_lhs[press_idle_lhs['Press_no'].isin(phase_1_press)].reset_index(drop=True)
    press_log1_rhs = press_idle_rhs[press_idle_rhs['Press_no'].isin(phase_1_press)].reset_index(drop=True)
    press_log2_lhs = press_idle_lhs[np.logical_not(press_idle_lhs['Press_no']
                                                   .isin(phase_1_press))].reset_index(drop=True)
    press_log2_rhs = press_idle_rhs[np.logical_not(press_idle_rhs['Press_no']
                                                   .isin(phase_1_press))].reset_index(drop=True)
    press_log1_lhs['Press_no'] = press_log1_lhs['Press_no'] + '_L'
    press_log1_rhs['Press_no'] = press_log1_rhs['Press_no'] + '_R'
    press_log_final=press_log1_lhs.append(press_log1_rhs)
    press_log_final=press_log_final.append(press_log2_lhs)
    press_log_final=press_log_final.append(press_log2_rhs)
    press_log_final = press_log_final.sort_values(['Press_no', 'Time_log'])
    press_log_final.reset_index(inplace=True, drop=True)

    import datetime
    press_log_final['Time_log'] = pd.to_datetime(press_log_final['Time_log'])
    press_log_final['shift_log'] = press_log_final['Time_log'] - datetime.timedelta(minutes=7 * 60)
    press_log_final['Shift'] = press_log_final['shift_log'].astype(str).str.strip().str[11:13]
    press_log_final['Date'] = press_log_final['shift_log'].astype(str).str.strip().str[:10]

    # ###################Tab-5- Single Side Idling############
    # press_idle_rhs['Time_log'] = pd.to_datetime(press_idle_rhs['Time_log'])
    # press_idle_rhs['shift_log'] = press_idle_rhs['Time_log'] - datetime.timedelta(minutes=7 * 60)
    # press_idle_rhs['Shift'] = press_idle_rhs['shift_log'].astype(str).str.strip().str[11:13]
    # press_idle_rhs['Date'] = press_idle_rhs['shift_log'].astype(str).str.strip().str[:10]
    # ##LHS
    # press_idle_lhs['Time_log'] = pd.to_datetime(press_idle_lhs['Time_log'])
    # press_idle_lhs['shift_log'] = press_idle_lhs['Time_log'] - datetime.timedelta(minutes=7 * 60)
    # press_idle_lhs['Shift'] = press_idle_lhs['shift_log'].astype(str).str.strip().str[11:13]
    # press_idle_lhs['Date'] = press_idle_lhs['shift_log'].astype(str).str.strip().str[:10]
    # Allocating shifts =======================================================================================
    shift_c = ['16', '17', '18', '19', '20', '21', '22', '23']
    shift_a = ['00', '01', '02', '03', '04', '05', '06', '07']
    shift_b = ['08', '09', '10', '11', '12', '13', '14', '15']

    press_log_final['Shift'] = np.where(press_log_final['Shift'].isin(shift_a), 'Shift_A', press_log_final['Shift'])
    press_log_final['Shift'] = np.where(press_log_final['Shift'].isin(shift_b), 'Shift_B', press_log_final['Shift'])
    press_log_final['Shift'] = np.where(press_log_final['Shift'].isin(shift_c), 'Shift_C', press_log_final['Shift'])
    #
    # new_temp_df = press_log['flag']
    # time = 0
    # shift = 0
    # press_log['date_shift'] = press_log['Date'] + press_log['Shift']
    # ###duplicate######
    # for i in np.arange(len(press_log)):
    #     try:
    #         time_new = press_log['Time'][i]
    #         shift_new=press_log['date_shift'][i]
    #         if time==0 and shift==0 and time_new != time:
    #             time = time_new
    #             shift=shift_new
    #             new_temp_df.iloc[i] = "start"
    #         elif time!=0 and time_new!=time:
    #             time=time_new
    #             new_temp_df.iloc[i-1] = "end"
    #             new_temp_df.iloc[i] = "start"
    #         elif time_new==time:
    #             shift_old=press_log['date_shift'][i-1]
    #             if shift_new!=shift_old:
    #                 new_temp_df.iloc[i - 1] = "end"
    #                 new_temp_df.iloc[i] = "start"
    #             else:
    #                 color_new = press_log['Color'][i]
    #                 color_old=press_log['Color'][i-1]
    #                 if color_old==color_new:
    #                     new_temp_df.iloc[i] = ""
    #                 elif color_old!=color_new:
    #                     if (color_new=='#C76666') or (color_new=='#3085B0'):
    #                         if color_old=='green' or color_old=='yellow' or color_old=='red' or color_old=='#FF9333':
    #                             new_temp_df.iloc[i - 1] = "end"
    #                             new_temp_df.iloc[i] = "start"
    #                         else:
    #                             new_temp_df.iloc[i] = ""
    #                     elif color_new=='green' or color_new=='yellow' or color_new=='red' or color_new=='#FF9333':
    #                         if (color_old=='#C76666') or (color_old=='#3085B0'):
    #                             new_temp_df.iloc[i - 1] = "end"
    #                             new_temp_df.iloc[i] = "start"
    #                         else:
    #                             new_temp_df.iloc[i] = ""
    #
    #     except:
    #         n=0
    # ####end######
    # new_temp_df.reset_index(inplace=True, drop=True)
    # press_log['flag'] = new_temp_df
    #
    # ##Calculation
    # temp_df1 = press_log[press_log['flag'] != ""]
    #
    # #writing a csv file for raw data download
    # temp_df1['Idling_Start_Time'] = temp_df1['Time_log']
    # temp_df1['Idling_End_Time'] = temp_df1['Time_log'].shift(-1)
    # temp_df1['Idle Time(in minutes)']=(temp_df1['Idling_End_Time']-temp_df1['Idling_Start_Time'])
    # temp_df1['Idle Time(in minutes)']=(temp_df1['Idle Time(in minutes)'] / np.timedelta64(1, 'm')).astype('float').round(0)
    # temp_df1['Idling_Start_Time']=temp_df1['Idling_Start_Time'].dt.strftime('%I:%M %p')
    # temp_df1['Idling_End_Time'] = temp_df1['Idling_End_Time'].dt.strftime('%I:%M %p')
    # temp_df1=temp_df1[temp_df1['flag'] != "end"]
    # temp_df1 = temp_df1[(temp_df1['Color'] != "#3085B0")]
    # temp_df1 = temp_df1[(temp_df1['Color'] != "#C76666")]
    # temp_df1 = temp_df1.reset_index(drop=True)
    # temp_df1 = temp_df1.sort_values(['Press_no','Time_log']).reset_index()
    # output_df = temp_df1[['Press_no', 'Date', 'Shift', 'Idling_Start_Time', 'Idling_End_Time', 'Idle Time(in minutes)']]
    # output_df=output_df[output_df['Idle Time(in minutes)']>=4].reset_index(drop=True)
    # output_df.to_pickle(config_loaded['host_folder'] + 'Data/Press log/idling_data_north.pkl')
    #####Calculation for Single Side Idling####################
    new_temp_df1 = press_log_final['flag']
    time_lhs = 0
    shift_lhs = 0
    press_log_final['date_shift'] = press_log_final['Date'] + press_log_final['Shift']
    for i in np.arange(len(press_log_final)):
        try:
            time_new_lhs = press_log_final['Time_log'][i]
            shift_new_lhs = press_log_final['date_shift'][i]
            if time_lhs == 0 and shift_lhs == 0 and time_new_lhs != time_lhs:
                time_lhs = time_new_lhs
                shift_lhs = shift_new_lhs
                new_temp_df1.iloc[i] = "start"
            elif time_lhs != 0 and time_new_lhs != time_lhs:
                time_diff = time_new_lhs - time_lhs
                time_diff = time_diff.total_seconds() / 60
                time_lhs = time_new_lhs
                shift_old = press_log_final['date_shift'][i - 1]
                if shift_new_lhs != shift_old:
                    new_temp_df1.iloc[i - 1] = "end"
                    new_temp_df1.iloc[i] = "start"
                else:
                    if time_diff > 2 and new_temp_df1.iloc[i - 1] == "start":
                        ###color condition starts here###
                        color_new = press_log_final['Color'][i]
                        color_old = press_log_final['Color'][i - 1]
                        if color_old == color_new:
                            new_temp_df1.iloc[i - 1] = ""
                            new_temp_df1.iloc[i] = "start"
                        elif color_old != color_new:
                            if (color_new == '#C76666') or (color_new == '#3085B0'):
                                if color_old == 'green' or color_old == 'yellow' or color_old == 'red' or color_old == '#FF9333':
                                    new_temp_df1.iloc[i - 1] = "end"
                                    new_temp_df1.iloc[i] = "start"
                                else:
                                    new_temp_df1.iloc[i - 1] = ""
                                    new_temp_df1.iloc[i] = "start"
                            elif color_new == 'green' or color_new == 'yellow' or color_new == 'red' or color_new == '#FF9333':
                                if (color_old == '#C76666') or (color_old == '#3085B0'):
                                    new_temp_df1.iloc[i - 1] = "end"
                                    new_temp_df1.iloc[i] = "start"
                                else:
                                    new_temp_df1.iloc[i - 1] = ""
                                    new_temp_df1.iloc[i] = "start"
                    elif time_diff > 2 and new_temp_df1.iloc[i - 1] == "":
                        ###color condition starts here###
                        color_new = press_log_final['Color'][i]
                        color_old = press_log_final['Color'][i - 1]
                        if color_old == color_new:
                            new_temp_df1.iloc[i - 1] = "end"
                            new_temp_df1.iloc[i] = "start"
                        elif color_old != color_new:
                            if (color_new == '#C76666') or (color_new == '#3085B0'):
                                if color_old == 'green' or color_old == 'yellow' or color_old == 'red' or color_old == '#FF9333':
                                    new_temp_df1.iloc[i - 1] = "end"
                                    new_temp_df1.iloc[i] = "start"
                                else:
                                    new_temp_df1.iloc[i - 1] = "end"
                                    new_temp_df1.iloc[i] = "start"
                            elif color_new == 'green' or color_new == 'yellow' or color_new == 'red' or color_new == '#FF9333':
                                if (color_old == '#C76666') or (color_old == '#3085B0'):
                                    new_temp_df1.iloc[i - 1] = "end"
                                    new_temp_df1.iloc[i] = "start"
                                else:
                                    new_temp_df1.iloc[i - 1] = "end"
                                    new_temp_df1.iloc[i] = "start"
                    else:
                        ###color condition starts here###
                        color_new = press_log_final['Color'][i]
                        color_old = press_log_final['Color'][i - 1]
                        if color_old == color_new:
                            new_temp_df1.iloc[i] = ""
                        elif color_old != color_new:
                            if (color_new == '#C76666') or (color_new == '#3085B0'):
                                if color_old == 'green' or color_old == 'yellow' or color_old == 'red' or color_old == '#FF9333':
                                    new_temp_df1.iloc[i - 1] = "end"
                                    new_temp_df1.iloc[i] = "start"
                                else:
                                    new_temp_df1.iloc[i] = ""
                            elif color_new == 'green' or color_new == 'yellow' or color_new == 'red' or color_new == '#FF9333':
                                if (color_old == '#C76666') or (color_old == '#3085B0'):
                                    new_temp_df1.iloc[i - 1] = "end"
                                    new_temp_df1.iloc[i] = "start"
                                else:
                                    new_temp_df1.iloc[i] = ""


            elif time_new_lhs == time_lhs:
                time_lhs = time_new_lhs
                shift_old = press_log_final['date_shift'][i - 1]
                if shift_new_lhs != shift_old:
                    new_temp_df1.iloc[i - 1] = "end"
                    new_temp_df1.iloc[i] = "start"
                else:
                    color_new = press_log_final['Color'][i]
                    color_old = press_log_final['Color'][i - 1]
                    if color_old == color_new:
                        new_temp_df1.iloc[i - 1] = ""
                        new_temp_df1.iloc[i] = "start"
                    elif color_old != color_new:
                        if (color_new == '#C76666') or (color_new == '#3085B0'):
                            if color_old == 'green' or color_old == 'yellow' or color_old == 'red' or color_old == '#FF9333':
                                new_temp_df1.iloc[i - 1] = "end"
                                new_temp_df1.iloc[i] = "start"
                            else:
                                new_temp_df1.iloc[i - 1] = ""
                                new_temp_df1.iloc[i] = "start"
                        elif color_new == 'green' or color_new == 'yellow' or color_new == 'red' or color_new == '#FF9333':
                            if (color_old == '#C76666') or (color_old == '#3085B0'):
                                new_temp_df1.iloc[i - 1] = "end"
                                new_temp_df1.iloc[i] = "start"
                            else:
                                new_temp_df1.iloc[i - 1] = ""
                                new_temp_df1.iloc[i] = "start"

        except:
            n = 0
    new_temp_df1.reset_index(inplace=True, drop=True)
    press_log_final['flag'] = new_temp_df1
    ###Calculation
    temp_df2 = press_log_final[press_log_final['flag'] != ""]

    # writing a csv file for raw data download
    temp_df2['Idling_Start_Time'] = temp_df2['Time_log']
    temp_df2['Idling_End_Time'] = temp_df2['Time_log'].shift(-1)
    temp_df2['Idle Time(in minutes)'] = (temp_df2['Idling_End_Time'] - temp_df2['Idling_Start_Time'])
    temp_df2['Idle Time(in minutes)'] = (temp_df2['Idle Time(in minutes)'] / np.timedelta64(1, 'm')).astype(
        'float').round(0)
    temp_df2['Idling_Start_Time'] = temp_df2['Idling_Start_Time'].dt.strftime('%I:%M %p')
    temp_df2['Idling_End_Time'] = temp_df2['Idling_End_Time'].dt.strftime('%I:%M %p')
    temp_df2 = temp_df2[temp_df2['flag'] != "end"]
    temp_df2 = temp_df2[(temp_df2['Color'] != "#3085B0")]
    temp_df2 = temp_df2[(temp_df2['Color'] != "#C76666")]
    temp_df2 = temp_df2.reset_index(drop=True)
    temp_df2 = temp_df2.sort_values(['Press_no', 'Time_log'])
    output_df1 = temp_df2[
        ['Press_no', 'Date', 'Shift', 'Idling_Start_Time', 'Idling_End_Time', 'Idle Time(in minutes)']]
    output_df1 = output_df1[output_df1['Idle Time(in minutes)'] >= 4]\
        .sort_values(['Press_no','Date','Idling_Start_Time']).reset_index(drop=True)
    output_df1.to_pickle(config_loaded['host_folder'] + 'Data/Press log/idling_data_north.pkl')

def idle_time_report_south(phase1_listing):
    '''
    Creates a table view for associate input analysis. Difference between First input given for GT loading time and actual start
    time
    :return: press_data_final_output csv
    '''
    path = config_loaded['host_folder'] + 'Data/Press log/press_data_south.pkl'
    #path = "C:/Users/Shounak.Pal/PycharmProjects/pythonProject/Data/Press log/press_data_south.pkl"
    press_log = pd.read_pickle(path)

    press_log['Time_log'] = pd.to_datetime(press_log['Time_log'])
    first_start = 1
    press_log["flag"] = ""
    press_log = press_log.fillna('nan')
    press_log = press_log.loc[(press_log['Color'] != 'grey')]
    ######
    press_idle_rhs = press_log[(press_log['STEP_NUMBER_RHS'] == 0)].sort_values(['Press_no', 'Time_log']).reset_index(drop=True)
    press_idle_lhs = press_log[(press_log['STEP_NUMBER_LHS'] == 0)].sort_values(['Press_no', 'Time_log']).reset_index(drop=True)
    phase_1_press = list(phase1_listing.keys())
    press_log1_lhs = press_idle_lhs[press_idle_lhs['Press_no'].isin(phase_1_press)].reset_index(drop=True)
    press_log1_rhs = press_idle_rhs[press_idle_rhs['Press_no'].isin(phase_1_press)].reset_index(drop=True)
    press_log2_lhs = press_idle_lhs[np.logical_not(press_idle_lhs['Press_no']
                                                   .isin(phase_1_press))].reset_index(drop=True)
    press_log2_rhs = press_idle_rhs[np.logical_not(press_idle_rhs['Press_no']
                                                   .isin(phase_1_press))].reset_index(drop=True)
    press_log1_lhs['Press_no'] = press_log1_lhs['Press_no'] + '_L'
    press_log1_rhs['Press_no'] = press_log1_rhs['Press_no'] + '_R'
    press_log_final=press_log1_lhs.append(press_log1_rhs)
    press_log_final=press_log_final.append(press_log2_lhs)
    press_log_final=press_log_final.append(press_log2_rhs)
    press_log_final = press_log_final.sort_values(['Press_no', 'Time_log'])
    press_log_final.reset_index(inplace=True, drop=True)

    import datetime
    press_log_final['Time_log'] = pd.to_datetime(press_log_final['Time_log'])
    press_log_final['shift_log'] = press_log_final['Time_log'] - datetime.timedelta(minutes=7 * 60)
    press_log_final['Shift'] = press_log_final['shift_log'].astype(str).str.strip().str[11:13]
    press_log_final['Date'] = press_log_final['shift_log'].astype(str).str.strip().str[:10]

    # ###################Tab-5- Single Side Idling############
    # press_idle_rhs['Time_log'] = pd.to_datetime(press_idle_rhs['Time_log'])
    # press_idle_rhs['shift_log'] = press_idle_rhs['Time_log'] - datetime.timedelta(minutes=7 * 60)
    # press_idle_rhs['Shift'] = press_idle_rhs['shift_log'].astype(str).str.strip().str[11:13]
    # press_idle_rhs['Date'] = press_idle_rhs['shift_log'].astype(str).str.strip().str[:10]
    # ##LHS
    # press_idle_lhs['Time_log'] = pd.to_datetime(press_idle_lhs['Time_log'])
    # press_idle_lhs['shift_log'] = press_idle_lhs['Time_log'] - datetime.timedelta(minutes=7 * 60)
    # press_idle_lhs['Shift'] = press_idle_lhs['shift_log'].astype(str).str.strip().str[11:13]
    # press_idle_lhs['Date'] = press_idle_lhs['shift_log'].astype(str).str.strip().str[:10]
    # Allocating shifts =======================================================================================
    shift_c = ['16', '17', '18', '19', '20', '21', '22', '23']
    shift_a = ['00', '01', '02', '03', '04', '05', '06', '07']
    shift_b = ['08', '09', '10', '11', '12', '13', '14', '15']

    press_log_final['Shift'] = np.where(press_log_final['Shift'].isin(shift_a), 'Shift_A', press_log_final['Shift'])
    press_log_final['Shift'] = np.where(press_log_final['Shift'].isin(shift_b), 'Shift_B', press_log_final['Shift'])
    press_log_final['Shift'] = np.where(press_log_final['Shift'].isin(shift_c), 'Shift_C', press_log_final['Shift'])
    #
    # new_temp_df = press_log['flag']
    # time = 0
    # shift = 0
    # press_log['date_shift'] = press_log['Date'] + press_log['Shift']
    # ###duplicate######
    # for i in np.arange(len(press_log)):
    #     try:
    #         time_new = press_log['Time'][i]
    #         shift_new=press_log['date_shift'][i]
    #         if time==0 and shift==0 and time_new != time:
    #             time = time_new
    #             shift=shift_new
    #             new_temp_df.iloc[i] = "start"
    #         elif time!=0 and time_new!=time:
    #             time=time_new
    #             new_temp_df.iloc[i-1] = "end"
    #             new_temp_df.iloc[i] = "start"
    #         elif time_new==time:
    #             shift_old=press_log['date_shift'][i-1]
    #             if shift_new!=shift_old:
    #                 new_temp_df.iloc[i - 1] = "end"
    #                 new_temp_df.iloc[i] = "start"
    #             else:
    #                 color_new = press_log['Color'][i]
    #                 color_old=press_log['Color'][i-1]
    #                 if color_old==color_new:
    #                     new_temp_df.iloc[i] = ""
    #                 elif color_old!=color_new:
    #                     if (color_new=='#C76666') or (color_new=='#3085B0'):
    #                         if color_old=='green' or color_old=='yellow' or color_old=='red' or color_old=='#FF9333':
    #                             new_temp_df.iloc[i - 1] = "end"
    #                             new_temp_df.iloc[i] = "start"
    #                         else:
    #                             new_temp_df.iloc[i] = ""
    #                     elif color_new=='green' or color_new=='yellow' or color_new=='red' or color_new=='#FF9333':
    #                         if (color_old=='#C76666') or (color_old=='#3085B0'):
    #                             new_temp_df.iloc[i - 1] = "end"
    #                             new_temp_df.iloc[i] = "start"
    #                         else:
    #                             new_temp_df.iloc[i] = ""
    #
    #     except:
    #         n=0
    # ####end######
    # new_temp_df.reset_index(inplace=True, drop=True)
    # press_log['flag'] = new_temp_df
    #
    # ##Calculation
    # temp_df1 = press_log[press_log['flag'] != ""]
    #
    # #writing a csv file for raw data download
    # temp_df1['Idling_Start_Time'] = temp_df1['Time_log']
    # temp_df1['Idling_End_Time'] = temp_df1['Time_log'].shift(-1)
    # temp_df1['Idle Time(in minutes)']=(temp_df1['Idling_End_Time']-temp_df1['Idling_Start_Time'])
    # temp_df1['Idle Time(in minutes)']=(temp_df1['Idle Time(in minutes)'] / np.timedelta64(1, 'm')).astype('float').round(0)
    # temp_df1['Idling_Start_Time']=temp_df1['Idling_Start_Time'].dt.strftime('%I:%M %p')
    # temp_df1['Idling_End_Time'] = temp_df1['Idling_End_Time'].dt.strftime('%I:%M %p')
    # temp_df1=temp_df1[temp_df1['flag'] != "end"]
    # temp_df1 = temp_df1[(temp_df1['Color'] != "#3085B0")]
    # temp_df1 = temp_df1[(temp_df1['Color'] != "#C76666")]
    # temp_df1 = temp_df1.reset_index(drop=True)
    # temp_df1 = temp_df1.sort_values(['Press_no','Time_log']).reset_index()
    # output_df = temp_df1[['Press_no', 'Date', 'Shift', 'Idling_Start_Time', 'Idling_End_Time', 'Idle Time(in minutes)']]
    # output_df=output_df[output_df['Idle Time(in minutes)']>=4].reset_index(drop=True)
    # output_df.to_pickle(config_loaded['host_folder'] + 'Data/Press log/idling_data_north.pkl')
    #####Calculation for Single Side Idling####################
    new_temp_df1 = press_log_final['flag']
    time_lhs = 0
    shift_lhs = 0
    press_log_final['date_shift'] = press_log_final['Date'] + press_log_final['Shift']
    for i in np.arange(len(press_log_final)):
        try:
            time_new_lhs = press_log_final['Time_log'][i]
            shift_new_lhs = press_log_final['date_shift'][i]
            if time_lhs == 0 and shift_lhs == 0 and time_new_lhs != time_lhs:
                time_lhs = time_new_lhs
                shift_lhs = shift_new_lhs
                new_temp_df1.iloc[i] = "start"
            elif time_lhs != 0 and time_new_lhs != time_lhs:
                time_diff = time_new_lhs - time_lhs
                time_diff = time_diff.total_seconds() / 60
                time_lhs = time_new_lhs
                shift_old = press_log_final['date_shift'][i - 1]
                if shift_new_lhs != shift_old:
                    new_temp_df1.iloc[i - 1] = "end"
                    new_temp_df1.iloc[i] = "start"
                else:
                    if time_diff > 2 and new_temp_df1.iloc[i - 1] == "start":
                        ###color condition starts here###
                        color_new = press_log_final['Color'][i]
                        color_old = press_log_final['Color'][i - 1]
                        if color_old == color_new:
                            new_temp_df1.iloc[i - 1] = ""
                            new_temp_df1.iloc[i] = "start"
                        elif color_old != color_new:
                            if (color_new == '#C76666') or (color_new == '#3085B0'):
                                if color_old == 'green' or color_old == 'yellow' or color_old == 'red' or color_old == '#FF9333':
                                    new_temp_df1.iloc[i - 1] = "end"
                                    new_temp_df1.iloc[i] = "start"
                                else:
                                    new_temp_df1.iloc[i - 1] = ""
                                    new_temp_df1.iloc[i] = "start"
                            elif color_new == 'green' or color_new == 'yellow' or color_new == 'red' or color_new == '#FF9333':
                                if (color_old == '#C76666') or (color_old == '#3085B0'):
                                    new_temp_df1.iloc[i - 1] = "end"
                                    new_temp_df1.iloc[i] = "start"
                                else:
                                    new_temp_df1.iloc[i - 1] = ""
                                    new_temp_df1.iloc[i] = "start"
                    elif time_diff > 2 and new_temp_df1.iloc[i - 1] == "":
                        ###color condition starts here###
                        color_new = press_log_final['Color'][i]
                        color_old = press_log_final['Color'][i - 1]
                        if color_old == color_new:
                            new_temp_df1.iloc[i - 1] = "end"
                            new_temp_df1.iloc[i] = "start"
                        elif color_old != color_new:
                            if (color_new == '#C76666') or (color_new == '#3085B0'):
                                if color_old == 'green' or color_old == 'yellow' or color_old == 'red' or color_old == '#FF9333':
                                    new_temp_df1.iloc[i - 1] = "end"
                                    new_temp_df1.iloc[i] = "start"
                                else:
                                    new_temp_df1.iloc[i - 1] = "end"
                                    new_temp_df1.iloc[i] = "start"
                            elif color_new == 'green' or color_new == 'yellow' or color_new == 'red' or color_new == '#FF9333':
                                if (color_old == '#C76666') or (color_old == '#3085B0'):
                                    new_temp_df1.iloc[i - 1] = "end"
                                    new_temp_df1.iloc[i] = "start"
                                else:
                                    new_temp_df1.iloc[i - 1] = "end"
                                    new_temp_df1.iloc[i] = "start"
                    else:
                        ###color condition starts here###
                        color_new = press_log_final['Color'][i]
                        color_old = press_log_final['Color'][i - 1]
                        if color_old == color_new:
                            new_temp_df1.iloc[i] = ""
                        elif color_old != color_new:
                            if (color_new == '#C76666') or (color_new == '#3085B0'):
                                if color_old == 'green' or color_old == 'yellow' or color_old == 'red' or color_old == '#FF9333':
                                    new_temp_df1.iloc[i - 1] = "end"
                                    new_temp_df1.iloc[i] = "start"
                                else:
                                    new_temp_df1.iloc[i] = ""
                            elif color_new == 'green' or color_new == 'yellow' or color_new == 'red' or color_new == '#FF9333':
                                if (color_old == '#C76666') or (color_old == '#3085B0'):
                                    new_temp_df1.iloc[i - 1] = "end"
                                    new_temp_df1.iloc[i] = "start"
                                else:
                                    new_temp_df1.iloc[i] = ""


            elif time_new_lhs == time_lhs:
                time_lhs = time_new_lhs
                shift_old = press_log_final['date_shift'][i - 1]
                if shift_new_lhs != shift_old:
                    new_temp_df1.iloc[i - 1] = "end"
                    new_temp_df1.iloc[i] = "start"
                else:
                    color_new = press_log_final['Color'][i]
                    color_old = press_log_final['Color'][i - 1]
                    if color_old == color_new:
                        new_temp_df1.iloc[i - 1] = ""
                        new_temp_df1.iloc[i] = "start"
                    elif color_old != color_new:
                        if (color_new == '#C76666') or (color_new == '#3085B0'):
                            if color_old == 'green' or color_old == 'yellow' or color_old == 'red' or color_old == '#FF9333':
                                new_temp_df1.iloc[i - 1] = "end"
                                new_temp_df1.iloc[i] = "start"
                            else:
                                new_temp_df1.iloc[i - 1] = ""
                                new_temp_df1.iloc[i] = "start"
                        elif color_new == 'green' or color_new == 'yellow' or color_new == 'red' or color_new == '#FF9333':
                            if (color_old == '#C76666') or (color_old == '#3085B0'):
                                new_temp_df1.iloc[i - 1] = "end"
                                new_temp_df1.iloc[i] = "start"
                            else:
                                new_temp_df1.iloc[i - 1] = ""
                                new_temp_df1.iloc[i] = "start"

        except:
            n = 0
    new_temp_df1.reset_index(inplace=True, drop=True)
    press_log_final['flag'] = new_temp_df1
    ###Calculation
    temp_df2 = press_log_final[press_log_final['flag'] != ""]

    # writing a csv file for raw data download
    temp_df2['Idling_Start_Time'] = temp_df2['Time_log']
    temp_df2['Idling_End_Time'] = temp_df2['Time_log'].shift(-1)
    temp_df2['Idle Time(in minutes)'] = (temp_df2['Idling_End_Time'] - temp_df2['Idling_Start_Time'])
    temp_df2['Idle Time(in minutes)'] = (temp_df2['Idle Time(in minutes)'] / np.timedelta64(1, 'm')).astype(
        'float').round(0)
    temp_df2['Idling_Start_Time'] = temp_df2['Idling_Start_Time'].dt.strftime('%I:%M %p')
    temp_df2['Idling_End_Time'] = temp_df2['Idling_End_Time'].dt.strftime('%I:%M %p')
    temp_df2 = temp_df2[temp_df2['flag'] != "end"]
    temp_df2 = temp_df2[(temp_df2['Color'] != "#3085B0")]
    temp_df2 = temp_df2[(temp_df2['Color'] != "#C76666")]
    temp_df2 = temp_df2.reset_index(drop=True)
    temp_df2 = temp_df2.sort_values(['Press_no', 'Time_log'])
    output_df1 = temp_df2[
        ['Press_no', 'Date', 'Shift', 'Idling_Start_Time', 'Idling_End_Time', 'Idle Time(in minutes)']]
    output_df1 = output_df1[output_df1['Idle Time(in minutes)'] >= 4]\
        .sort_values(['Press_no','Date','Idling_Start_Time']).reset_index(drop=True)
    output_df1.to_pickle(config_loaded['host_folder'] + 'Data/Press log/idling_data_south.pkl')
