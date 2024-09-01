from typing import List
import os
import pandas as pd
import numpy as np
import datetime
import pyodbc
import os
import warnings
import time
import glob
from main import define_config
from datetime import datetime,timedelta
config_loaded = define_config()

def log_extraction_north():
    """ Extract Historical logs for consolidated SKU and Trench View
        saves press log data for user input analysis.
        Extracts historical data in two for loops (first 1000: press_data_fin1
         and next 1000: press_data_fin2) for fast processing.
        Creates shift column and appends to consolidated press_data_fin
        returns: press_data_fin - With all the allocated shift details for press condition log
    """
    press_data_fin_north = pd.DataFrame()
    press_data_fin1_north = pd.DataFrame()
    press_data_fin2_north = pd.DataFrame()
    esc_set_north = config_loaded['host_folder1']+"Data\Historical Logs North\log" + "*" + ".pkl"
    list_of_files_north: List[str] = glob.glob(esc_set_north)
    df_north = []

    # Extracting recent most 1000 entries==============================================================================

    list_of_files_north = sorted(list_of_files_north, key=os.path.getmtime)
    list_of_files_north = list_of_files_north[-1000:]


    for file in list_of_files_north:
        list_of_files_north.index(file)
        #print(list_of_files.index(file))
        try:
            df_north.append(pd.read_pickle(file))
            press_data_fin1_north = pd.concat(df_north, ignore_index=True)
        except:
            time.sleep(1)
            df_north.append(pd.read_pickle(file))
            press_data_fin1_north = pd.concat(df_north, ignore_index=True)

    list_of_files_north = glob.glob(esc_set_north)
    list_of_files_north = sorted(list_of_files_north, key=os.path.getmtime)
    df_north = []
    # Extracting recent most 2000 to 1000 entries=======================================================================
    list_of_files_north = list_of_files_north[-2000:-1000]
    for file in list_of_files_north:
        list_of_files_north.index(file)
        #print(list_of_files.index(file))
        try:
            df_north.append(pd.read_pickle(file))
            press_data_fin2_north = pd.concat(df_north, ignore_index=True)
        except:
            time.sleep(7)
            df_north.append(pd.read_pickle(file))
            press_data_fin2_north = pd.concat(df_north, ignore_index=True)

    # Consolidating all entries and sorting by time===========================================================
    press_data_fin_north = pd.concat([press_data_fin1_north, press_data_fin2_north], axis=0)
    press_data_fin_north['Time_log'] = pd.to_datetime(press_data_fin_north['Time_log'])
    press_data_fin_north = press_data_fin_north.sort_values(['Time_log'], ascending=False)

    press_data_fin_north = press_data_fin_north.sort_values(['Press_no'])
    # press_data back up without shift details
    press_data_fin_north.to_pickle(config_loaded['host_folder']+'Data/Press log/press_data_north.pkl')


    # Reducing 7 hours from the time log to create shift views=================================================
    press_data_fin_north['Time_log'] = press_data_fin_north['Time_log'] - timedelta(minutes=7 * 60)
    press_data_fin_north['Date'] = press_data_fin_north['Time_log'].astype(str).str.strip().str[:10]
    press_data_fin_north['Hour'] = press_data_fin_north['Time_log'].astype(str).str.strip().str[11:13]
    # Allocating shifts =======================================================================================
    shift_c = ['16', '17', '18', '19', '20', '21', '22', '23']
    shift_a = ['00', '01', '02', '03', '04', '05', '06', '07']
    shift_b = ['08', '09', '10', '11', '12', '13', '14', '15']

    press_data_fin_north['Hour'] = np.where(press_data_fin_north['Hour'].isin(shift_a), 'Shift_A', press_data_fin_north['Hour'])
    press_data_fin_north['Hour'] = np.where(press_data_fin_north['Hour'].isin(shift_b), 'Shift_B', press_data_fin_north['Hour'])
    press_data_fin_north['Hour'] = np.where(press_data_fin_north['Hour'].isin(shift_c), 'Shift_C', press_data_fin_north['Hour'])

    return press_data_fin_north


def log_extraction_south():
    """ Extract Historical logs for consolidated SKU and Trench Vie
        saves press log data for user input analysis.
        Extracts historial data in two for loops (first 1000: press_data_fin1
         and next 1000: press_data_fin2) for fast processing.
        Creates shift column and appends to consolidated press_data_fin
        returns: press_data_fin - With all the allocated shift details for press condition log
    """
    press_data_fin_south = pd.DataFrame()
    press_data_fin1_south = pd.DataFrame()
    press_data_fin2_south = pd.DataFrame()
    esc_set_south = config_loaded['host_folder1']+"Data\Historical Logs South\log" + "*" + ".pkl"
    list_of_files_south: List[str] = glob.glob(esc_set_south)
    df_south = []

    # Extracting recent most 10000 entries==============================================================================

    list_of_files_south = sorted(list_of_files_south, key=os.path.getmtime)
    list_of_files_south = list_of_files_south[-1000:]


    for file in list_of_files_south:
        list_of_files_south.index(file)
        #print(list_of_files.index(file))
        try:
            df_south.append(pd.read_pickle(file))
            press_data_fin1_south = pd.concat(df_south, ignore_index=True)
        except:
            time.sleep(7)
            df_south.append(pd.read_pickle(file))
            press_data_fin1_south = pd.concat(df_south, ignore_index=True)

    list_of_files_south = glob.glob(esc_set_south)
    list_of_files_south = sorted(list_of_files_south, key=os.path.getmtime)
    df_south = []
    # Extracting recent most 200 to 100 entries=======================================================================
    list_of_files_south = list_of_files_south[-2000:-1000]
    for file in list_of_files_south:
        list_of_files_south.index(file)
        #print(list_of_files.index(file))
        try:
            df_south.append(pd.read_pickle(file))
            press_data_fin2_south = pd.concat(df_south, ignore_index=True)
        except:
            time.sleep(7)
            df_south.append(pd.read_pickle(file))
            press_data_fin2_south = pd.concat(df_south, ignore_index=True)

    # Consolidating all entries and sorting by time===========================================================
    press_data_fin_south = pd.concat([press_data_fin1_south, press_data_fin2_south], axis=0)
    press_data_fin_south['Time_log'] = pd.to_datetime(press_data_fin_south['Time_log'])
    press_data_fin_south = press_data_fin_south.sort_values(['Time_log'], ascending=False)

    press_data_fin_south = press_data_fin_south.sort_values(['Press_no'])
    # press_data back up without shift details
    press_data_fin_south.to_pickle(config_loaded['host_folder']+'Data/Press log/press_data_south.pkl')


    # Reducing 7 hours from the time log to create shift views=================================================
    press_data_fin_south['Time_log'] = press_data_fin_south['Time_log'] - timedelta(minutes=7 * 60)
    press_data_fin_south['Date'] = press_data_fin_south['Time_log'].astype(str).str.strip().str[:10]
    press_data_fin_south['Hour'] = press_data_fin_south['Time_log'].astype(str).str.strip().str[11:13]
    # Allocating shifts =======================================================================================
    shift_c = ['16', '17', '18', '19', '20', '21', '22', '23']
    shift_a = ['00', '01', '02', '03', '04', '05', '06', '07']
    shift_b = ['08', '09', '10', '11', '12', '13', '14', '15']

    press_data_fin_south['Hour'] = np.where(press_data_fin_south['Hour'].isin(shift_a), 'Shift_A', press_data_fin_south['Hour'])
    press_data_fin_south['Hour'] = np.where(press_data_fin_south['Hour'].isin(shift_b), 'Shift_B', press_data_fin_south['Hour'])
    press_data_fin_south['Hour'] = np.where(press_data_fin_south['Hour'].isin(shift_c), 'Shift_C', press_data_fin_south['Hour'])

    return press_data_fin_south

def log_extrac_hr_north(phase1_listing,max_time):
    """ Extract Historical logs for consolidated SKU and Trench View
        saves press log data for user input analysis.
        Extracts historical data in two for loops (first 1000: press_data_fin1
         and next 1000: press_data_fin2) for fast processing.
        Creates shift column and appends to consolidated press_data_fin
        returns: press_data_fin - With all the allocated shift details for press condition log
    """
    press_data_fin_north = pd.DataFrame()
    esc_set_north = config_loaded['host_folder']+"Data/Historical Logs North/log" + "*" + ".pkl"
    list_of_files_north: List[str] = glob.glob(esc_set_north)
    df_north = []

    # Extracting recent most 1000 entries==============================================================================

    list_of_files_north = sorted(list_of_files_north, key=os.path.getmtime)
    list_of_files_north = list_of_files_north[-120:]


    for file in list_of_files_north:
        list_of_files_north.index(file)
        #print(list_of_files.index(file))
        try:
            df_north.append(pd.read_pickle(file))
            press_data_fin_north = pd.concat(df_north, ignore_index=True)
        except:
            time.sleep(1)
            df_north.append(pd.read_pickle(file))
            press_data_fin_north = pd.concat(df_north, ignore_index=True)

    list_of_files_north = glob.glob(esc_set_north)
    list_of_files_north = sorted(list_of_files_north, key=os.path.getmtime)
    # Consolidating all entries and sorting by time===========================================================
    press_data_fin_north['Time_log'] = pd.to_datetime(press_data_fin_north['Time_log'])
    # Remove leading and trailing whitespace characters
    press_data_fin_north['TYRE_SIZE_RHS'] = press_data_fin_north['TYRE_SIZE_RHS'].str.strip()
    press_data_fin_north['TYRE_SIZE_LHS'] = press_data_fin_north['TYRE_SIZE_LHS'].str.strip()

    press_data_fin_north = press_data_fin_north.sort_values(['Time_log'], ascending=True).reset_index(drop=True)
    #max_time =press_data_fin_north['Time_log'][len(press_data_fin_north)-1]
    min_time=pd.to_datetime(max_time)-timedelta(minutes=60)
    press_data_fin_north=press_data_fin_north[press_data_fin_north['Time_log']>=min_time]
    press_data_fin_north = press_data_fin_north[press_data_fin_north['Time_log'] <= pd.to_datetime(max_time)]
    press_data_fin_north = press_data_fin_north.sort_values(['Press_no','Time_log'], ascending=True).reset_index(drop=True)
    # press_data back up without shift details
    # Reducing 7 hours from the time log to create shift views=================================================
    press_data_fin_north['Time_log2'] = press_data_fin_north['Time_log'] - timedelta(minutes=7 * 60)
    press_data_fin_north['Date'] = press_data_fin_north['Time_log2'].astype(str).str.strip().str[:10]
    press_data_fin_north['Hour'] = press_data_fin_north['Time_log2'].astype(str).str.strip().str[11:13]
    # Allocating shifts =======================================================================================
    shift_c = ['16', '17', '18', '19', '20', '21', '22', '23']
    shift_a = ['00', '01', '02', '03', '04', '05', '06', '07']
    shift_b = ['08', '09', '10', '11', '12', '13', '14', '15']

    press_data_fin_north['Hour'] = np.where(press_data_fin_north['Hour'].isin(shift_a), 'Shift_A', press_data_fin_north['Hour'])
    press_data_fin_north['Hour'] = np.where(press_data_fin_north['Hour'].isin(shift_b), 'Shift_B', press_data_fin_north['Hour'])
    press_data_fin_north['Hour'] = np.where(press_data_fin_north['Hour'].isin(shift_c), 'Shift_C', press_data_fin_north['Hour'])
    press_data_fin_north['date_shift'] = press_data_fin_north['Date'] + press_data_fin_north['Hour']
    press_log1_lhs = press_data_fin_north[press_data_fin_north['Press_no'].isin(phase1_listing)].reset_index(drop=True)
    press_log1_rhs = press_data_fin_north[press_data_fin_north['Press_no'].isin(phase1_listing)].reset_index(drop=True)
    press_log2 = press_data_fin_north[np.logical_not(press_data_fin_north['Press_no']
                                                   .isin(phase1_listing))].reset_index(drop=True)
    press_log2['TYRE_SIZE']=np.where(press_log2['Press_no'].astype(str).str.strip().str[-2:] == '_L',
                                     press_log2['TYRE_SIZE_LHS'], press_log2['TYRE_SIZE_RHS'])
    press_log2['STEP_NUMBER']=np.where(press_log2['Press_no'].astype(str).str.strip().str[-2:] == '_L',
                                     press_log2['STEP_NUMBER_LHS'], press_log2['STEP_NUMBER_RHS'])
    press_log1_lhs['Press_no'] = press_log1_lhs['Press_no'] + '_L'
    press_log1_lhs['STEP_NUMBER'] = press_log1_lhs['STEP_NUMBER_LHS']
    press_log1_lhs['TYRE_SIZE'] = press_log1_lhs['TYRE_SIZE_LHS']
    press_log1_rhs['Press_no'] = press_log1_rhs['Press_no'] + '_R'
    press_log1_rhs['STEP_NUMBER'] = press_log1_rhs['STEP_NUMBER_RHS']
    press_log1_rhs['TYRE_SIZE'] = press_log1_rhs['TYRE_SIZE_RHS']
    press_log_fin_north = press_log1_lhs.append(press_log1_rhs)
    press_log_fin_north = press_log_fin_north.append(press_log2)
    press_log_fin_north=press_log_fin_north.drop(columns=['STEP_NUMBER_RHS','STEP_NUMBER_LHS',
                                                          'TYRE_SIZE_RHS','TYRE_SIZE_LHS'], axis=1)
    press_log_fin_north['press_date_shift'] = press_log_fin_north['Press_no'] + press_log_fin_north['Date'] + \
                                               press_log_fin_north['Hour']
    # press_log_fin_north['press_date_shift_tyre'] =press_log_fin_north['Press_no'] + press_log_fin_north['Date'] + \
    #                                            press_log_fin_north['Hour']+press_log_fin_north['TYRE_SIZE']
    ###calculate ratio
    maxlen=0
    for x in press_log_fin_north['press_date_shift'].unique():
        press_len_check=press_log_fin_north.loc[press_log_fin_north['press_date_shift'] == x]
        if len(press_len_check)>=maxlen:
            maxlen=len(press_len_check)
    try:
        ratio=60/maxlen
    except Exception as e:
        ratio=0
    press_log_fin_north['Ratio']=ratio
    ####calculate ratio end ################
    ###################Steam Shut Down#################
    press_log_fin_north = press_log_fin_north.loc[(press_log_fin_north['Color'] != 'grey')]
    press_log_fin_north = press_log_fin_north.loc[(press_log_fin_north['Color'] != '#C76666')]
    press_log_fin_north = press_log_fin_north.loc[(press_log_fin_north['Color'] != '#3085B0')]
    ######Running Minutes Calculation########################################
    press_not_idle_log = press_log_fin_north.loc[(press_log_fin_north['STEP_NUMBER'] != 0)].reset_index(drop=True)
    press_not_idle_summary=press_not_idle_log[['Press_no', 'TYRE_SIZE','Input1','Input2', 'Input3',
                                               'Date', 'Hour','date_shift', 'press_date_shift', 'Ratio']]
    press_not_idle=press_not_idle_summary.groupby(['press_date_shift']).size().reset_index(name='Count')
    press_not_idle_summary=press_not_idle_summary.drop_duplicates().reset_index(drop=True)
    press_not_idle_summary=pd.merge(press_not_idle_summary,press_not_idle,on='press_date_shift',how='inner')
    press_not_idle_summary['Running_mins']=round(press_not_idle_summary['Count'] * press_not_idle_summary['Ratio'],0)
    press_not_idle_summary=press_not_idle_summary.rename(columns={'Hour': 'Shift'})
    press_not_idle_summary['Hour_Range']=max_time[-11:]
    ########################End Running Minutes#################################################
    ###finding idle log###

    press_idle_log_north = press_log_fin_north.loc[(press_log_fin_north['STEP_NUMBER'] == 0)]
    press_idle_log_north = press_idle_log_north.loc[(press_idle_log_north['Color'] != 'grey')].sort_values(['Press_no', 'Time_log'])\
        .reset_index(drop=True)
    press_idle_log_north["flag"] = ""
    new_temp_df1 = press_idle_log_north['flag']
    time_lhs = 0
    shift_lhs = 0
    ###copy pasted from idle_report= idle time calculation
    for i in np.arange(len(press_idle_log_north)):
        try:
            time_new_lhs = press_idle_log_north['Time_log'][i]
            shift_new_lhs = press_idle_log_north['press_date_shift'][i]
            if time_lhs == 0 and shift_lhs == 0 and time_new_lhs != time_lhs:
                time_lhs = time_new_lhs
                shift_lhs = shift_new_lhs
                new_temp_df1.iloc[i] = "start"
            elif time_lhs != 0 and time_new_lhs != time_lhs:
                time_diff = time_new_lhs - time_lhs
                time_diff = time_diff.total_seconds() / 60
                time_lhs = time_new_lhs
                shift_old = press_idle_log_north['press_date_shift'][i - 1]
                if shift_new_lhs != shift_old:
                    new_temp_df1.iloc[i - 1] = "end"
                    new_temp_df1.iloc[i] = "start"
                else:
                    if time_diff > 2 and new_temp_df1.iloc[i - 1] == "start":
                        ###color condition starts here###
                        color_new = press_idle_log_north['Color'][i]
                        color_old = press_idle_log_north['Color'][i - 1]
                        if color_old == color_new:
                            new_temp_df1.iloc[i - 1] = "1"
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
                        color_new = press_idle_log_north['Color'][i]
                        color_old = press_idle_log_north['Color'][i - 1]
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
                        color_new = press_idle_log_north['Color'][i]
                        color_old = press_idle_log_north['Color'][i - 1]
                        if color_old == color_new:
                            if i==len(press_idle_log_north)-1:
                                new_temp_df1.iloc[i] = "end"
                            else:
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
                shift_old = press_idle_log_north['press_date_shift'][i - 1]
                if shift_new_lhs != shift_old:
                    new_temp_df1.iloc[i - 1] = "end"
                    new_temp_df1.iloc[i] = "start"
                else:
                    color_new = press_idle_log_north['Color'][i]
                    color_old = press_idle_log_north['Color'][i - 1]
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
    press_idle_log_north['flag'] = new_temp_df1
    ###Calculation
    df_north1 = press_idle_log_north[press_idle_log_north['flag'] != ""]
    df_north1['Idling_Start_Time'] = df_north1['Time_log'].shift(-1)
    df_north1 = df_north1.reset_index()
    temp_df2 = pd.DataFrame()
    for press in df_north1['Press_no'].unique():
        temp_df3 = df_north1.loc[df_north1['Press_no'] == press]
        for i, row in temp_df3.iterrows():
            #print(row)
            if row['flag'] == 'start' and i + 1 <= df_north1.shape[0] - 1:
                # print(row)
                time_diff = round((pd.to_datetime(df_north1.iloc[i]['Idling_Start_Time']) - pd.to_datetime(
                    df_north1.iloc[i]['Time_log'])).total_seconds() / 60,0)
                time_diff+=1
                row['Idle Time(in minutes)']=time_diff
                temp_df2=temp_df2.append(row)
            if row['flag'] == '1' and i + 1 <= df_north1.shape[0] - 1:
                # print(row)
                time_diff = 1
                row['Idle Time(in minutes)']=time_diff
                temp_df2=temp_df2.append(row)
    # if len(temp_df2)==0:
    #     temp_df2=pd.DataFrame(columns=['index', 'Press_no', 'Time', 'Color', 'PLATEN_TEMPERATURE',
    #    'Time_to_cut_off', 'Idle_Alarm', 'Current Condition', 'Last Input Time',
    #    'Last Change To', 'Input1', 'Input2', 'Input3', 'Time_log', 'Time_log2',
    #    'Date', 'Hour', 'date_shift', 'STEP_NUMBER', 'TYRE_SIZE',
    #    'press_date_shift', 'Ratio', 'flag', 'Idling_Start_Time',
    #    'Idle Time(in minutes)'])
    temp_df2=temp_df2.drop(columns=['index'],axis=1)
    temp_df2['Idling_Start_Time'] = temp_df2['Idling_Start_Time'].dt.strftime('%I:%M %p')
    temp_df2 = temp_df2[(temp_df2['Color'] != "#3085B0")]
    temp_df2 = temp_df2[(temp_df2['Color'] != "#C76666")]
    temp_df2 = temp_df2.reset_index(drop=True)
    temp_df2 = temp_df2.sort_values(['Press_no', 'Time_log'])
    temp_df2['Input1'] = temp_df2['Input1'].astype(str)
    temp_df2['Input_press_date_shift'] = temp_df2['press_date_shift'] + temp_df2['Input1']
    sum_df = temp_df2.groupby(by=['Input_press_date_shift'], as_index=False)['Idle Time(in minutes)'].sum()

    temp_df2 = temp_df2.drop(columns=['flag', 'Idling_Start_Time', 'Idle Time(in minutes)'], axis=1)
    temp_df2 = temp_df2.drop(
        columns=['Time', 'Color', 'Time_to_cut_off', 'PLATEN_TEMPERATURE', 'Idle_Alarm',
                 'Current Condition', 'Last Input Time', 'Last Change To', 'STEP_NUMBER',
                 'Time_log', 'Time_log2']
        , axis=1).drop_duplicates().reset_index(drop=True)
    temp_df2 = pd.merge(temp_df2, sum_df, on='Input_press_date_shift', how='inner')
    #####Idle minutes sum done####################
    temp_df2['Idle Time(rounded)'] = round(temp_df2['Idle Time(in minutes)'] * temp_df2['Ratio'], 0)
    temp_df2 = temp_df2.drop(columns=['Idle Time(in minutes)'], axis=1)
    temp_df2 = temp_df2.rename(columns={'Hour': 'Shift'})
    idle_with_no_idle = temp_df2[temp_df2['Press_no'].isin(press_not_idle_summary['Press_no'])]
    idle_only_df = temp_df2[np.logical_not(temp_df2['Press_no'].isin(press_not_idle_summary['Press_no']))]
    idle_with_comments = temp_df2[temp_df2['Input1'].astype(str) != 'nan']  ### separating ones with comments
    idle_with_no_idle = idle_with_no_idle.drop(idle_with_comments.index, errors='ignore', axis=0).reset_index(drop=True)
    idle_only_df = idle_only_df.drop(idle_with_comments.index, errors='ignore', axis=0).reset_index(drop=True)
    idle_only_df['Hour_Range'] = max_time[-11:]
    idle_only_df['Running_mins'] = 0
    idle_only_df = idle_only_df.drop(columns=['Input_press_date_shift'], axis=1)
    idle_only_df = idle_only_df[['Press_no', 'TYRE_SIZE', 'Input1', 'Input2', 'Input3', 'Date', 'Shift',
                                 'date_shift', 'press_date_shift', 'Ratio',
                                 'Running_mins', 'Hour_Range', 'Idle Time(rounded)']]
    temp_df = idle_with_no_idle[['press_date_shift', 'Idle Time(rounded)']]
    press_summary = pd.merge(press_not_idle_summary, temp_df, how='outer', on='press_date_shift')
    press_summary = press_summary.drop(columns=['Count'], axis=1)
    press_summary = pd.concat([press_summary, idle_only_df], ignore_index=True) \
        .sort_values(['Press_no']).reset_index(drop=True)
    idle_with_comments.rename(columns={'Idle Time(rounded)': 'Idle with comments'}, inplace=True)
    idle_with_comments['Idle Time(rounded)'] = 0
    idle_with_comments['Hour_Range'] = max_time[-11:]
    idle_with_comments['Running_mins'] = 0
    idle_with_comments = idle_with_comments.drop(columns=['Input_press_date_shift'], axis=1)

    idle_with_comments = idle_with_comments[['Press_no', 'Date', 'Shift','date_shift', 'press_date_shift',
                                             'Ratio','Running_mins', 'Hour_Range','Idle Time(rounded)',
                                             'Idle with comments']].reset_index(drop=True)
    temp_df_new = pd.DataFrame()
    try:
        db1 = pyodbc.connect(
            'Driver={SQL Server};Server=SRVNGPPRD2SQL1;Database=Curing_Inventory;Uid=LH;Pwd=Lighthouse@123;')
        cursor_new = db1.cursor()
    except:
        print('No cursor connection')
    for index, row in idle_with_comments.iterrows():
        print(row)
        if row['press_date_shift'] in press_summary['press_date_shift'].values:
            print(temp_df_new)
            row1 = pd.DataFrame(row).T
            # temp_df_new = idle_with_comments[idle_with_comments['press_date_shift_tyre'] == row['press_date_shift_tyre']]
            print(row1)
            temp_df_new = pd.concat([temp_df_new, row1], ignore_index=False)
            idle_with_comments.drop(index, inplace=True)
    if len(temp_df_new)>0:
        temp_df_new = temp_df_new[['press_date_shift', 'Idle with comments']]
        press_summary1 = pd.merge(press_summary, temp_df_new, how='outer', on='press_date_shift')
        press_summary1 = pd.concat([press_summary1, idle_with_comments], ignore_index=True) \
            .sort_values(['Press_no']).reset_index(drop=True)
    else:
        press_summary1=press_summary.copy()
        press_summary1['Idle with comments']=0
    press_summary2=press_summary1[['Date', 'Shift','Press_no', 'TYRE_SIZE', 'Ratio','Running_mins',
                                  'Idle Time(rounded)','Idle with comments','Hour_Range']]
    #####working on Number of cycles, Number of Mould Change,
    press_cycle=pd.DataFrame(columns=['press_date_shift','cycles'])
    min_time = pd.to_datetime(max_time) - timedelta(minutes=60)
    min_time_str = min_time.strftime("%Y-%m-%d %H:%M:%S")
    max_time_date = pd.to_datetime(max_time)
    max_time_str = max_time_date.strftime("%Y-%m-%d %H:%M:%S")
    for x in press_not_idle_log['press_date_shift'].unique():
        press_check=press_not_idle_log.loc[press_not_idle_log['press_date_shift'] == x, 'Press_no'].iloc[0]
        print(press_check)
        try:
            if press_check[-2:]=='_R':
                data=pd.read_sql_query("""SELECT COUNT(*) as cycle FROM 
                [Curing_Inventory].[dbo].[Bladder_mould_C1C2] where _TIMESTAMP>='"""+min_time_str+"""' 
                and _TIMESTAMP<'"""+max_time_str+"""' and _NAME LIKE '%"""+press_check[:-2]+""".Barcode%'""",con=db1)
            else:
                data = pd.read_sql_query("""SELECT COUNT(*) as cycle FROM 
                                [Curing_Inventory].[dbo].[Bladder_mould_C3C4] where _TIMESTAMP>='""" + min_time_str + """' 
                                and _TIMESTAMP<'""" + max_time_str + """' and _NAME LIKE '%""" + press_check[
                                                                                             :-2] + """.Barcode%'""",con=db1)
            press_cycle = press_cycle.append({'press_date_shift': x, 'cycles': data['cycle'][0]}, ignore_index=True)

        except Exception as e:
            print("while checking for cycle count",e)

            #print(cycle)
    #######################end cycle##################################
    press_summary3= pd.merge(press_summary1, press_cycle, how='outer', on='press_date_shift')
    press_log_fin_north['press_date_shift_tyre']=press_log_fin_north['press_date_shift']+press_log_fin_north['TYRE_SIZE']
    new_df=press_log_fin_north[['press_date_shift','press_date_shift_tyre']].drop_duplicates()
    new_df=new_df.dropna()
    mould_count = new_df.groupby(by=['press_date_shift'], as_index=False)['press_date_shift_tyre'].count()
    mould_count = mould_count.rename(columns={'press_date_shift_tyre': 'Mould_Count'})
    press_summary4 = pd.merge(press_summary3, mould_count, how='inner', on='press_date_shift')
    press_summary4["Idle with comments"]= np.where(press_summary4["Idle with comments"].astype(str) == "nan", 0,
                                                   press_summary4["Idle with comments"])
    press_summary4["cycles"] = np.where(press_summary4["cycles"].astype(str) == "nan", 0,
                                                    press_summary4["cycles"])
    press_summary4["Mould_Count"] = np.where(press_summary4["cycles"] == 0, 0,
                                                    press_summary4["Mould_Count"])
    mould_classify=pd.read_csv(config_loaded['host_folder'] + 'Data/Master Datasets/mould_type.csv')
    mould_classify = mould_classify.rename(columns={'Size': 'TYRE_SIZE'})
    press_summary5=pd.merge(press_summary4,mould_classify,how='inner',on='TYRE_SIZE')
    press_summary5 = press_summary5.rename(columns={'SEGMENT': 'TYPE_CHANGE'})
    press_summary5["TYPE_CHANGE"] = np.where(press_summary5["TYPE_CHANGE"] == "MCY", 1,0)
    press_summary5["MC_Count"] = np.where(press_summary5["TYPE_CHANGE"] == 1, press_summary5["cycles"],0)
    press_summary5["SC_Count"] = np.where(press_summary5["TYPE_CHANGE"] == 0, press_summary5["cycles"], 0)
    press_summary5.to_csv(config_loaded['host_folder'] + 'Data/press_running_mins_North.csv', index=False)
    cursor_new.close()
    db1.close()
    return press_summary5


def log_extrac_hr_south(phase1_listing, max_time):
    """ Extract Historical logs for consolidated SKU and Trench View
        saves press log data for user input analysis.
        Extracts historical data in two for loops (first 1000: press_data_fin1
         and next 1000: press_data_fin2) for fast processing.
        Creates shift column and appends to consolidated press_data_fin
        returns: press_data_fin - With all the allocated shift details for press condition log
    """
    press_data_fin_south = pd.DataFrame()
    esc_set_south = config_loaded['host_folder']+"Data/Historical Logs South/log" + "*" + ".pkl"
    list_of_files_south: List[str] = glob.glob(esc_set_south)
    df_south = []

    # Extracting recent most 1000 entries==============================================================================

    list_of_files_south = sorted(list_of_files_south, key=os.path.getmtime)
    list_of_files_south = list_of_files_south[-120:]


    for file in list_of_files_south:
        list_of_files_south.index(file)
        #print(list_of_files.index(file))
        try:
            df_south.append(pd.read_pickle(file))
            press_data_fin_south = pd.concat(df_south, ignore_index=True)
        except:
            time.sleep(1)
            df_south.append(pd.read_pickle(file))
            press_data_fin_south = pd.concat(df_south, ignore_index=True)

    list_of_files_south = glob.glob(esc_set_south)
    list_of_files_south = sorted(list_of_files_south, key=os.path.getmtime)
    # Consolidating all entries and sorting by time===========================================================
    press_data_fin_south['Time_log'] = pd.to_datetime(press_data_fin_south['Time_log'])

    press_data_fin_south = press_data_fin_south.sort_values(['Time_log'], ascending=True).reset_index(drop=True)
    #max_time =press_data_fin_south['Time_log'][len(press_data_fin_south)-1]
    min_time=pd.to_datetime(max_time)-timedelta(minutes=60)
    press_data_fin_south=press_data_fin_south[press_data_fin_south['Time_log']>=min_time]
    press_data_fin_south = press_data_fin_south[press_data_fin_south['Time_log'] <= pd.to_datetime(max_time)]
    press_data_fin_south = press_data_fin_south.sort_values(['Press_no','Time_log'], ascending=True).reset_index(drop=True)
    # press_data back up without shift details
    # Reducing 7 hours from the time log to create shift views=================================================
    press_data_fin_south['Time_log2'] = press_data_fin_south['Time_log'] - timedelta(minutes=7 * 60)
    press_data_fin_south['Date'] = press_data_fin_south['Time_log2'].astype(str).str.strip().str[:10]
    press_data_fin_south['Hour'] = press_data_fin_south['Time_log2'].astype(str).str.strip().str[11:13]
    # Allocating shifts =======================================================================================
    shift_c = ['16', '17', '18', '19', '20', '21', '22', '23']
    shift_a = ['00', '01', '02', '03', '04', '05', '06', '07']
    shift_b = ['08', '09', '10', '11', '12', '13', '14', '15']

    press_data_fin_south['Hour'] = np.where(press_data_fin_south['Hour'].isin(shift_a), 'Shift_A', press_data_fin_south['Hour'])
    press_data_fin_south['Hour'] = np.where(press_data_fin_south['Hour'].isin(shift_b), 'Shift_B', press_data_fin_south['Hour'])
    press_data_fin_south['Hour'] = np.where(press_data_fin_south['Hour'].isin(shift_c), 'Shift_C', press_data_fin_south['Hour'])
    press_data_fin_south['date_shift'] = press_data_fin_south['Date'] + press_data_fin_south['Hour']
    press_log1_lhs = press_data_fin_south[press_data_fin_south['Press_no'].isin(phase1_listing)].reset_index(drop=True)
    press_log1_rhs = press_data_fin_south[press_data_fin_south['Press_no'].isin(phase1_listing)].reset_index(drop=True)
    press_log2 = press_data_fin_south[np.logical_not(press_data_fin_south['Press_no']
                                                   .isin(phase1_listing))].reset_index(drop=True)
    press_log2['TYRE_SIZE']=np.where(press_log2['Press_no'].astype(str).str.strip().str[-2:] == '_L',
                                     press_log2['TYRE_SIZE_LHS'], press_log2['TYRE_SIZE_RHS'])
    press_log2['STEP_NUMBER']=np.where(press_log2['Press_no'].astype(str).str.strip().str[-2:] == '_L',
                                     press_log2['STEP_NUMBER_LHS'], press_log2['STEP_NUMBER_RHS'])
    press_log1_lhs['Press_no'] = press_log1_lhs['Press_no'] + '_L'
    press_log1_lhs['STEP_NUMBER'] = press_log1_lhs['STEP_NUMBER_LHS']
    press_log1_lhs['TYRE_SIZE'] = press_log1_lhs['TYRE_SIZE_LHS']
    press_log1_rhs['Press_no'] = press_log1_rhs['Press_no'] + '_R'
    press_log1_rhs['STEP_NUMBER'] = press_log1_rhs['STEP_NUMBER_RHS']
    press_log1_rhs['TYRE_SIZE'] = press_log1_rhs['TYRE_SIZE_RHS']
    press_log_fin_south = press_log1_lhs.append(press_log1_rhs)
    press_log_fin_south = press_log_fin_south.append(press_log2)
    press_log_fin_south=press_log_fin_south.drop(columns=['STEP_NUMBER_RHS','STEP_NUMBER_LHS',
                                                          'TYRE_SIZE_RHS','TYRE_SIZE_LHS'], axis=1)
    press_log_fin_south['press_date_shift'] = press_log_fin_south['Press_no'] + press_log_fin_south['Date'] + \
                                               press_log_fin_south['Hour']
    ###calculate ratio
    maxlen=0
    for x in press_log_fin_south['press_date_shift'].unique():
        press_len_check=press_log_fin_south.loc[press_log_fin_south['press_date_shift'] == x]
        if len(press_len_check)>=maxlen:
            maxlen=len(press_len_check)
    try:
        ratio = 60 / maxlen
    except Exception as e:
        ratio = 0
    press_log_fin_south['Ratio']=ratio
    ####calculate ratio end ################
    ###################Steam Shut Down#################
    press_log_fin_south = press_log_fin_south.loc[(press_log_fin_south['Color'] != 'grey')]
    press_log_fin_south = press_log_fin_south.loc[(press_log_fin_south['Color'] != '#C76666')]
    press_log_fin_south = press_log_fin_south.loc[(press_log_fin_south['Color'] != '#3085B0')]

    ######Running Minutes Calculation########################################
    press_not_idle_log = press_log_fin_south.loc[(press_log_fin_south['STEP_NUMBER'] != 0)]
    press_not_idle_summary = press_not_idle_log[['Press_no', 'TYRE_SIZE', 'Input1', 'Input2', 'Input3', 'Date',
                                                 'Hour', 'date_shift', 'press_date_shift','Ratio']]
    press_not_idle=press_not_idle_summary.groupby(['press_date_shift']).size().reset_index(name='Count')
    press_not_idle_summary=press_not_idle_summary.drop_duplicates().reset_index(drop=True)
    press_not_idle_summary=pd.merge(press_not_idle_summary,press_not_idle,on='press_date_shift',how='inner')
    press_not_idle_summary['Running_mins']=round(press_not_idle_summary['Count'] * press_not_idle_summary['Ratio'],0)
    press_not_idle_summary.rename(columns={'Hour': 'Shift'}, inplace=True)
    press_not_idle_summary['Hour_Range']=max_time[-11:]
    ########################End Running Minutes#################################################
    #####################Idle Minutes Calculation#############################################
    press_idle_log_south = press_log_fin_south.loc[(press_log_fin_south['STEP_NUMBER'] == 0)]
    press_idle_log_south = press_idle_log_south.loc[(press_idle_log_south['Color'] != 'grey')].sort_values(['Press_no', 'Time_log']) \
        .reset_index(drop=True)
    press_idle_log_south["flag"] = ""
    new_temp_df1 = press_idle_log_south['flag']
    time_lhs = 0
    shift_lhs = 0
    ###copy pasted from idle_report= idle time calculation
    for i in np.arange(len(press_idle_log_south)):
        try:
            time_new_lhs = press_idle_log_south['Time_log'][i]
            shift_new_lhs = press_idle_log_south['press_date_shift'][i]
            if time_lhs == 0 and shift_lhs == 0 and time_new_lhs != time_lhs:
                time_lhs = time_new_lhs
                shift_lhs = shift_new_lhs
                new_temp_df1.iloc[i] = "start"
            elif time_lhs != 0 and time_new_lhs != time_lhs:
                time_diff = time_new_lhs - time_lhs
                time_diff = time_diff.total_seconds() / 60
                time_lhs = time_new_lhs
                shift_old = press_idle_log_south['press_date_shift'][i - 1]
                if shift_new_lhs != shift_old:
                    new_temp_df1.iloc[i - 1] = "end"
                    new_temp_df1.iloc[i] = "start"
                else:
                    if time_diff > 2 and new_temp_df1.iloc[i - 1] == "start":
                        ###color condition starts here###
                        color_new = press_idle_log_south['Color'][i]
                        color_old = press_idle_log_south['Color'][i - 1]
                        if color_old == color_new:
                            new_temp_df1.iloc[i - 1] = "1"
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
                        color_new = press_idle_log_south['Color'][i]
                        color_old = press_idle_log_south['Color'][i - 1]
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
                        color_new = press_idle_log_south['Color'][i]
                        color_old = press_idle_log_south['Color'][i - 1]
                        if color_old == color_new:
                            if i == len(press_idle_log_south) - 1:
                                new_temp_df1.iloc[i] = "end"
                            else:
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
                shift_old = press_idle_log_south['press_date_shift'][i - 1]
                if shift_new_lhs != shift_old:
                    new_temp_df1.iloc[i - 1] = "end"
                    new_temp_df1.iloc[i] = "start"
                else:
                    color_new = press_idle_log_south['Color'][i]
                    color_old = press_idle_log_south['Color'][i - 1]
                    if color_old == color_new:
                        new_temp_df1.iloc[i - 1] = "1"
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
    press_idle_log_south['flag'] = new_temp_df1
    ###Calculation
    df_south1 = press_idle_log_south[press_idle_log_south['flag'] != ""]
    df_south1['Idling_Start_Time'] = df_south1['Time_log'].shift(-1)
    df_south1 = df_south1.reset_index()
    temp_df2=pd.DataFrame()
    for press in df_south1['Press_no'].unique():
        temp_df3 = df_south1.loc[df_south1['Press_no'] == press]
        for i, row in temp_df3.iterrows():
            #print(row)
            if row['flag'] == 'start' and i + 1 <= df_south1.shape[0] - 1:
                # print(row)
                time_diff = round((pd.to_datetime(df_south1.iloc[i]['Idling_Start_Time']) - pd.to_datetime(
                    df_south1.iloc[i]['Time_log'])).total_seconds() / 60,0)
                time_diff+=1
                row['Idle Time(in minutes)']=time_diff
                temp_df2=temp_df2.append(row)
            if row['flag'] == '1' and i + 1 <= df_south1.shape[0] - 1:
                # print(row)
                time_diff = 1
                row['Idle Time(in minutes)']=time_diff
                temp_df2=temp_df2.append(row)
    temp_df2=temp_df2.drop(columns=['index'],axis=1)
    temp_df2['Idling_Start_Time'] = temp_df2['Idling_Start_Time'].dt.strftime('%I:%M %p')
    temp_df2 = temp_df2[(temp_df2['Color'] != "#3085B0")]
    temp_df2 = temp_df2[(temp_df2['Color'] != "#C76666")]
    temp_df2 = temp_df2.reset_index(drop=True)
    temp_df2 = temp_df2.sort_values(['Press_no', 'Time_log'])
    temp_df2['Input1'] = temp_df2['Input1'].astype(str)
    temp_df2['Input_press_date_shift'] = temp_df2['press_date_shift'] + temp_df2['Input1']
    sum_df = temp_df2.groupby(by=['Input_press_date_shift'], as_index=False)['Idle Time(in minutes)'].sum()

    temp_df2 = temp_df2.drop(columns=['flag', 'Idling_Start_Time', 'Idle Time(in minutes)'], axis=1)
    temp_df2 = temp_df2.drop(
        columns=['Time', 'Color', 'Time_to_cut_off', 'PLATEN_TEMPERATURE', 'Idle_Alarm',
                 'Current Condition', 'Last Input Time', 'Last Change To', 'STEP_NUMBER',
                 'Time_log', 'Time_log2']
        , axis=1).drop_duplicates().reset_index(drop=True)
    temp_df2 = pd.merge(temp_df2, sum_df, on='Input_press_date_shift', how='inner')
    #####Idle minutes sum done####################
    temp_df2['Idle Time(rounded)'] = round(temp_df2['Idle Time(in minutes)'] * temp_df2['Ratio'], 0)
    temp_df2 = temp_df2.drop(columns=['Idle Time(in minutes)'], axis=1)
    temp_df2 = temp_df2.rename(columns={'Hour': 'Shift'})
    idle_with_no_idle = temp_df2[temp_df2['Press_no'].isin(press_not_idle_summary['Press_no'])]
    idle_only_df = temp_df2[np.logical_not(temp_df2['Press_no'].isin(press_not_idle_summary['Press_no']))]
    idle_with_comments = temp_df2[temp_df2['Input1'].astype(str) != 'nan']  ### separating ones with comments
    idle_with_no_idle = idle_with_no_idle.drop(idle_with_comments.index, errors='ignore', axis=0).reset_index(drop=True)
    idle_only_df = idle_only_df.drop(idle_with_comments.index, errors='ignore', axis=0).reset_index(drop=True)
    idle_only_df['Hour_Range'] = max_time[-11:]
    idle_only_df['Running_mins'] = 0
    idle_only_df = idle_only_df.drop(columns=['Input_press_date_shift'], axis=1)
    idle_only_df = idle_only_df[['Press_no', 'TYRE_SIZE', 'Input1', 'Input2', 'Input3', 'Date', 'Shift',
                                 'date_shift', 'press_date_shift', 'Ratio','Running_mins', 'Hour_Range',
                                 'Idle Time(rounded)']]
    temp_df = idle_with_no_idle[['press_date_shift', 'Idle Time(rounded)']]
    press_summary = pd.merge(press_not_idle_summary, temp_df, how='outer', on='press_date_shift')
    press_summary = press_summary.drop(columns=['Count'], axis=1)
    press_summary = pd.concat([press_summary, idle_only_df], ignore_index=True) \
        .sort_values(['Press_no']).reset_index(drop=True)
    idle_with_comments.rename(columns={'Idle Time(rounded)': 'Idle with comments'}, inplace=True)
    idle_with_comments['Idle Time(rounded)'] = 0
    idle_with_comments['Hour_Range'] = max_time[-11:]
    idle_with_comments['Running_mins'] = 0
    idle_with_comments = idle_with_comments.drop(columns=['Input_press_date_shift'], axis=1)
    idle_with_comments = idle_with_comments[['Press_no', 'Date', 'Shift','date_shift', 'press_date_shift',
                                             'Ratio','Running_mins', 'Hour_Range', 'Idle Time(rounded)',
                                             'Idle with comments']].reset_index(drop=True)
    #press_summary['Idle with comments']=''
    temp_df_new=pd.DataFrame()
    try:
        db1 = pyodbc.connect(
            'Driver={SQL Server};Server=SRVNGPPRD2SQL1;Database=Curing_Inventory;Uid=LH;Pwd=Lighthouse@123;')
        cursor_new = db1.cursor()
    except:
        print('No cursor connection')
    for index, row in idle_with_comments.iterrows():
        print(row)
        if row['press_date_shift'] in press_summary['press_date_shift'].values:
            print(temp_df_new)
            row1=pd.DataFrame(row).T
            #temp_df_new = idle_with_comments[idle_with_comments['press_date_shift_tyre'] == row['press_date_shift_tyre']]
            print(row1)
            temp_df_new = pd.concat([temp_df_new, row1], ignore_index=False)
            idle_with_comments.drop(index, inplace=True)

    if len(temp_df_new) > 0:
        temp_df_new = temp_df_new[['press_date_shift', 'Idle with comments']]
        press_summary1 = pd.merge(press_summary, temp_df_new, how='outer', on='press_date_shift')
        press_summary1 = pd.concat([press_summary1, idle_with_comments], ignore_index=True) \
            .sort_values(['Press_no']).reset_index(drop=True)
    else:
        press_summary1 = press_summary.copy()
        press_summary1['Idle with comments'] = 0
    press_summary2 = press_summary1[['Date', 'Shift', 'Press_no', 'TYRE_SIZE', 'Ratio', 'Running_mins',
                                     'Idle Time(rounded)', 'Idle with comments', 'Hour_Range']]
    #####working on Number of cycles, Number of Mould Change,
    press_cycle = pd.DataFrame(columns=['press_date_shift', 'cycles'])
    min_time = pd.to_datetime(max_time) - timedelta(minutes=60)
    min_time_str = min_time.strftime("%Y-%m-%d %H:%M:%S")
    max_time_date = pd.to_datetime(max_time)
    max_time_str = max_time_date.strftime("%Y-%m-%d %H:%M:%S")
    for x in press_not_idle_log['press_date_shift'].unique():
        press_check = press_not_idle_log.loc[press_not_idle_log['press_date_shift'] == x, 'Press_no'].iloc[0]
        print(press_check)
        try:
            if press_check[-2:] == '_R':
                data = pd.read_sql_query("""SELECT COUNT(*) as cycle FROM 
                    [Curing_Inventory].[dbo].[Bladder_mould_C1C2] where _TIMESTAMP>='""" + min_time_str + """' 
                    and _TIMESTAMP<'""" + max_time_str + """' and _NAME LIKE '%""" + press_check[:-2] + """.Barcode%'""",
                                         con=db1)
            else:
                data = pd.read_sql_query("""SELECT COUNT(*) as cycle FROM 
                                    [Curing_Inventory].[dbo].[Bladder_mould_C3C4] where _TIMESTAMP>='""" + min_time_str + """' 
                                    and _TIMESTAMP<'""" + max_time_str + """' and _NAME LIKE '%""" + press_check[
                                                                                                 :-2] + """.Barcode%'""",
                                         con=db1)
            press_cycle = press_cycle.append({'press_date_shift': x, 'cycles': data['cycle'][0]}, ignore_index=True)

        except Exception as e:
            print("while checking for cycle count", e)

            # print(cycle)
    #######################end cycle##################################
    press_summary3 = pd.merge(press_summary1, press_cycle, how='outer', on='press_date_shift')
    press_log_fin_south['press_date_shift_tyre'] = press_log_fin_south['press_date_shift'] + press_log_fin_south[
        'TYRE_SIZE']
    new_df = press_log_fin_south[['press_date_shift', 'press_date_shift_tyre']].drop_duplicates()
    new_df = new_df.dropna()
    mould_count = new_df.groupby(by=['press_date_shift'], as_index=False)['press_date_shift_tyre'].count()
    mould_count = mould_count.rename(columns={'press_date_shift_tyre': 'Mould_Count'})
    press_summary4 = pd.merge(press_summary3, mould_count, how='inner', on='press_date_shift')
    press_summary4["Idle with comments"] = np.where(press_summary4["Idle with comments"].astype(str) == "nan", 0,
                                                    press_summary4["Idle with comments"])
    press_summary4["cycles"] = np.where(press_summary4["cycles"].astype(str) == "nan", 0,
                                        press_summary4["cycles"])
    press_summary4["Mould_Count"] = np.where(press_summary4["cycles"] == 0, 0,
                                             press_summary4["Mould_Count"])
    mould_classify = pd.read_csv(config_loaded['host_folder'] + 'Data/Master Datasets/mould_type.csv')
    mould_classify = mould_classify.rename(columns={'Size': 'TYRE_SIZE'})
    press_summary5 = pd.merge(press_summary4, mould_classify, how='inner', on='TYRE_SIZE')
    press_summary5 = press_summary5.rename(columns={'SEGMENT': 'TYPE_CHANGE'})
    press_summary5["TYPE_CHANGE"] = np.where(press_summary5["TYPE_CHANGE"] == "MCY", 0, 1)
    press_summary5["MC_Count"] = np.where(press_summary5["TYPE_CHANGE"] == 0, press_summary5["cycles"], 0)
    press_summary5["SC_Count"] = np.where(press_summary5["TYPE_CHANGE"] == 1, press_summary5["cycles"], 0)
    press_summary5.to_csv(config_loaded['host_folder'] + 'Data/press_running_mins_South.csv', index=False)
    cursor_new.close()
    db1.close()
    return press_summary5


def mould_classify_data():
    try:
        db = pyodbc.connect(
            'Driver={SQL Server};Server=SRVNGPPRD2SQL1;Database=CT_SCRAP;Uid=LH;Pwd=Lighthouse@123;')
        cursor = db.cursor()
    except:
        print('No cursor connection')
    try:

        data_table = pd.read_sql_query("""SELECT DISTINCT Size, SEGMENT 
        FROM [CT_SCRAP].[dbo].[Masterdata-Equipmentwise]""", con=db)
        db.close()
    except Exception as e:
        print(e)
    data_table.to_csv(config_loaded['host_folder'] + 'Data/Master Datasets/mould_type.csv',index=False)

def db_insert_north(data):
    try:
        db = pyodbc.connect(
            'Driver={SQL Server};Server=SRVNGPPRD2SQL1;Database=STEAM_AI;Uid=LH;Pwd=Lighthouse@123;')
        cursor = db.cursor()
    except:
        print('No cursor connection')
    try:
        date=data['Date'][0]
        hour=data['Hour_Range'][0]
        data_check=pd.read_sql_query("""SELECT * FROM [STEAM_AI].[dbo].[STEAM_Curing] 
        where [Date]= '"""+date+"""' and [Hour_Range]='"""+hour+"""' and Press_no LIKE '%SCC%'""", con=db)
        if len(data_check)==0:
            for index, row in data.iterrows():
                print(index)
                row['Press_no'] = str(row['Press_no'])
                row['Date'] = pd.to_datetime(row['Date'])
                row['Shift'] = str(row['Shift'])
                row['Ratio'] = str(row['Ratio'])
                row['Running_mins'] = str(row['Running_mins'])
                row['Hour_Range'] = str(row['Hour_Range'])
                row['Idle Time(rounded)'] = str(row['Idle Time(rounded)'])
                row['Idle with comments'] = str(row['Idle with comments'])
                row['cycles'] = str(row['cycles'])
                row['Mould_Count'] = str(row['Mould_Count'])
                row['cycles'] = str(row['cycles'])
                row['TYPE_CHANGE'] = str(row['TYPE_CHANGE'])
                row['MC_Count'] = str(row['MC_Count'])
                row['SC_Count'] = str(row['SC_Count'])

                try:

                    cursor.execute(
                        "INSERT INTO [STEAM_AI].[dbo].[STEAM_Curing] ([Press_no],[Date],[Shift],[Ratio]"
                        ",[Running_mins],[Hour_Range],[Idle_NoComment],[Idle_with_comment],[Cycle_Count]"
                        ",[Mould_Count],[Mould_Interchange],[MC_Count],[SC_Count]) values(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        row['Press_no'], row['Date'], row['Shift'], row['Ratio'], row['Running_mins']
                        , row['Hour_Range'], row['Idle Time(rounded)'], row['Idle with comments']
                        , row['cycles'], row['Mould_Count'], row['TYPE_CHANGE'],row['MC_Count'],row['SC_Count'])
                    db.commit()
                    print(data)
                except Exception as e:
                    print("unable to edit database", e)
        #data1.replace(np.nan, '', regex=True)

        cursor.close()
    except Exception as e:
        print('issue in DB Insert', e)
def db_insert_south(data):
    try:
        db = pyodbc.connect(
            'Driver={SQL Server};Server=SRVNGPPRD2SQL1;Database=STEAM_AI;Uid=LH;Pwd=Lighthouse@123;')
        cursor = db.cursor()
    except:
        print('No cursor connection')
    try:
        date=data['Date'][0]
        hour=data['Hour_Range'][0]
        data_check=pd.read_sql_query("""SELECT * FROM [STEAM_AI].[dbo].[STEAM_Curing] 
        where [Date]= '"""+date+"""' and [Hour_Range]='"""+hour+"""' and Press_no LIKE '%MCC%'""", con=db)
        if len(data_check)==0:
            for index, row in data.iterrows():
                print(index)
                row['Press_no'] = str(row['Press_no'])
                row['Date'] = pd.to_datetime(row['Date'])
                row['Shift'] = str(row['Shift'])
                row['Ratio'] = str(row['Ratio'])
                row['Running_mins'] = str(row['Running_mins'])
                row['Hour_Range'] = str(row['Hour_Range'])
                row['Idle Time(rounded)'] = str(row['Idle Time(rounded)'])
                row['Idle with comments'] = str(row['Idle with comments'])
                row['cycles'] = str(row['cycles'])
                row['Mould_Count'] = str(row['Mould_Count'])
                row['cycles'] = str(row['cycles'])
                row['TYPE_CHANGE'] = str(row['TYPE_CHANGE'])
                row['MC_Count'] = str(row['MC_Count'])
                row['SC_Count'] = str(row['SC_Count'])

                try:

                    cursor.execute(
                        "INSERT INTO [STEAM_AI].[dbo].[STEAM_Curing] ([Press_no],[Date],[Shift],[Ratio]"
                        ",[Running_mins],[Hour_Range],[Idle_NoComment],[Idle_with_comment],[Cycle_Count]"
                        ",[Mould_Count],[Mould_Interchange],[MC_Count],[SC_Count]) values(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        row['Press_no'], row['Date'], row['Shift'], row['Ratio'], row['Running_mins']
                        , row['Hour_Range'], row['Idle Time(rounded)'], row['Idle with comments']
                        , row['cycles'], row['Mould_Count'], row['TYPE_CHANGE'],row['MC_Count'],row['SC_Count'])
                    db.commit()
                    print(data)
                except Exception as e:
                    print("unable to edit database", e)
        #data1.replace(np.nan, '', regex=True)

        cursor.close()
    except Exception as e:
        print('issue in DB Insert', e)