import time
import pandas as pd
import numpy as np
import gc
import warnings
import datetime
from Scripts.Extracting_log_data import log_extraction_north, log_extraction_south
from Scripts.idling_report import excess_idling_report_north, excess_idling_report_south
from Scripts.steam_opportunity_report import generate_opp_report_north, generate_opp_report_south
import yaml
from itertools import count
from main import define_config
config_loaded = define_config()
#with open("Configuration/config.yaml", 'r') as stream: config_loaded = yaml.safe_load(stream)
warnings.filterwarnings("ignore")
trench_switch_north = config_loaded['North Trench Switch (OPC write back)']
trench_switch_south = config_loaded['South Trench Switch (OPC write back)']
log_speed = config_loaded['program_speed']
trench_distribution_north = config_loaded['North Trench Distribution']
trench_distribution_south = config_loaded['South Trench Distribution']
thres_temp = config_loaded['Associate Inputs']['Threshold temperature']
#####################New addition for heterogeneous trench##########################
hetero_list = config_loaded['Heterogeneous press']
press_list_north = config_loaded['North Trench Distribution']['North_Trench1'] + config_loaded['North Trench Distribution'][
    'North_Trench2'] + \
             config_loaded['North Trench Distribution']['North_Trench3'] + config_loaded['North Trench Distribution'][
                 'North_Trench4'] + \
             config_loaded['North Trench Distribution']['North_Trench5'] + config_loaded['North Trench Distribution'][
                 'North_Trench6']
press_list_south = config_loaded['South Trench Distribution']['South_Trench1'] + config_loaded['South Trench Distribution'][
    'South_Trench2'] + \
             config_loaded['South Trench Distribution']['South_Trench3'] + config_loaded['South Trench Distribution'][
                 'South_Trench4'] + \
             config_loaded['South Trench Distribution']['South_Trench5'] + config_loaded['South Trench Distribution'][
                 'South_Trench6']
#######################################################End#################################
# Reversing Key and value mapping to get press to trench mapping
new_distribution_south = {}
for k, v in trench_distribution_south.items():
    '''
    re-assigns presses if trench switch is kept to 1
    '''
    for x in v:
        if x in hetero_list:
            a = x +'_L'
            b = x +'_R'
            new_distribution_south.setdefault(a, []).append(k)
            new_distribution_south.setdefault(b, []).append(k)
        else:
            new_distribution_south.setdefault(x, []).append(k)

new_distribution_north = {}
for k, v in trench_distribution_north.items():
    '''
    re-assigns presses if trench switch is kept to 1
    '''
    for x in v:
        if x in hetero_list:
            a = x + '_L'
            b = x + '_R'
            new_distribution_north.setdefault(a, []).append(k)
            new_distribution_north.setdefault(b, []).append(k)
        else:
            new_distribution_north.setdefault(x, []).append(k)
i = 0
for run in count(0):
    print(run)
    try:
        press_data_fin_north = log_extraction_north()
        print("North log_extraction_completed")
        press_data_fin_south = log_extraction_south()
        print("South log_extraction_completed")
    except Exception as e:
        print(e)
        pass

    # creating steam opportunity loss report
    try:
        idling_report_north = excess_idling_report_north()
        idling_report_south = excess_idling_report_south()
        press_data_fin_north = press_data_fin_north.sort_values(['Date', 'Hour'])
        press_data_fin_south = press_data_fin_south.sort_values(['Date', 'Hour'])
    except:
        print("Issue in genete op report")
        pass


#########################################Segregating North South from this function###########################


    # Creating Trench View==============================================================================================
    press_data_fin_north['date_shift'] = press_data_fin_north['Date'] + press_data_fin_north['Hour']
    press_data_fin_north['press_date_shift'] = press_data_fin_north['Press_no'] + press_data_fin_north['Date'] + press_data_fin_north['Hour']
    #############New addition- Shounak adjusted idling#######################
    idling_report_north['press_date_shift'] = idling_report_north['Press_no'] + idling_report_north['Date'] + idling_report_north['Shift']
    idling_report_north.groupby('press_date_shift').sum()
    ###############################################
    press_data_fin_north = press_data_fin_north[~(press_data_fin_north['TYRE_SIZE_RHS'].isna()
                                                  & press_data_fin_north['TYRE_SIZE_LHS'].isna())]

    ####Calculation change for Steam saved - Ensuring that during a Shift the calculation is equally dynamic######
    # Allocating shifts =======================================================================================
    shift_b = ['15', '16', '17', '18', '19', '20', '21', '22']
    shift_c = ['23','00', '01', '02', '03', '04', '05', '06']
    shift_a = ['07', '08', '09', '10', '11', '12', '13', '14']
    # shift_c = ['16', '17', '18', '19', '20', '21', '22', '23']
    # shift_a = ['00', '01', '02', '03', '04', '05', '06', '07']
    # shift_b = ['08', '09', '10', '11', '12', '13', '14', '15']
    present_hour = str((datetime.datetime.now()).strftime("%H"))
    present_date =str((datetime.datetime.now()).strftime("%Y-%m-%d"))
    previous_date = str((datetime.datetime.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
    if present_hour in shift_a:
        shift_start_time=datetime.datetime.strptime(present_date + " "+shift_a[0]+":00:00","%Y-%m-%d %H:%M:%S")
        present_shift = 'Shift_A'
    elif present_hour in shift_b:
        shift_start_time=datetime.datetime.strptime(present_date + " " + shift_b[0] + ":00:00", "%Y-%m-%d %H:%M:%S")
        present_shift = 'Shift_B'
    else:
        if present_hour == '23':
            shift_start_time = datetime.datetime.strptime(present_date + " " + shift_c[0] + ":00:00",
                                                          "%Y-%m-%d %H:%M:%S")
        else:
            shift_start_time = datetime.datetime.strptime(present_date + " " + shift_c[1] + ":00:00", "%Y-%m-%d %H:%M:%S")
        present_shift = 'Shift_C'
    present = str((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S"))


    for x in press_data_fin_north['date_shift'].unique():
        data_date = press_data_fin_north.loc[press_data_fin_north['date_shift'] == x, 'Date']
        data_shift = press_data_fin_north.loc[press_data_fin_north['date_shift'] == x, 'Hour']
        for l in data_date.unique():
            if l == present_date:
                day_flag = '1'
            else:
                if present_hour == '23':
                    if l == previous_date:
                        day_flag='1'
                    else:
                        day_flag='0'
                else:
                    day_flag = '0'
        #press_data_fin_north.loc[press_data_fin_north['press_date_shift'] == i, 'present_day'] = day_flag
        for m in data_shift.unique():
            if day_flag == '1':
                if m == present_shift:
                    shift_flag = 1
                    if m == 'Shift_C':
                        if present_hour == '23':
                            minutes_passed = ((datetime.datetime.strptime(present, "%Y-%m-%d %H:%M:%S")
                                               - shift_start_time).seconds / 60)
                        else:
                            minutes_passed = ((datetime.datetime.strptime(present, "%Y-%m-%d %H:%M:%S")
                                               - shift_start_time).seconds / 60) + 60
                    else:
                        minutes_passed = ((datetime.datetime.strptime(present, "%Y-%m-%d %H:%M:%S")
                                           - shift_start_time).seconds / 60)

                else:
                    shift_flag = 0
                    minutes_passed = 480
            else:
                shift_flag = 0
                minutes_passed = 480
        select_date_log = press_data_fin_north.loc[press_data_fin_north['date_shift'] == x]
        max_north=0
        for a in select_date_log['Press_no'].unique():
            len1 = len(select_date_log.loc[select_date_log['Press_no'] == a])
            temp = max_north
            if (len1 > temp):
                max_north = len1
            else:
                max_north = temp
        press_data_fin_north.loc[press_data_fin_north['date_shift'] == x, 'ratio'] = (max_north * (log_speed / 60)) / minutes_passed
        #### program_minutes = (max_north * (log_speed / 60))
######################################Primary calculation end####################################
    options = ['0', np.nan, '1']
    press_data_fin_north = press_data_fin_north[press_data_fin_north.Idle_Alarm.isin(options)]
    press_data_fin_north['Saving Potential'] = press_data_fin_north['Idle_Alarm']
    press_data_fin_north['Saving Potential']=press_data_fin_north['Saving Potential'].replace('', '0')
    press_data_fin_north['Saving Potential'] = press_data_fin_north['Saving Potential'].astype(int)
    press_data_fin_north = press_data_fin_north.sort_values(['Press_no', 'Time_log'])
    press_data_fin_north.reset_index(inplace=True, drop=True)
    idle_flag = 0
    new_temp_df = press_data_fin_north['Saving Potential']
    for i in np.arange(len(press_data_fin_north)):
        if press_data_fin_north.iloc[i]['Saving Potential'] == 1 and idle_flag==0:
            idle_flag=1
            new_temp_df.iloc[i] = 1
        elif press_data_fin_north.iloc[i]['Saving Potential'] == 1 and idle_flag==1:
            new_temp_df.iloc[i] = 0
        elif press_data_fin_north.iloc[i]['Saving Potential'] == 0 and idle_flag==1:
            idle_flag= 0
            new_temp_df.iloc[i] = 0
        else:
            new_temp_df.iloc[i] = 0
            idle_flag==0
    new_temp_df.reset_index(inplace=True, drop=True)
    press_data_fin_north['Saving Potential'] = new_temp_df
    for i in press_data_fin_north['press_date_shift'].unique():
        ratio = press_data_fin_north.loc[press_data_fin_north['press_date_shift'] == i, 'ratio']
        j=i[:7]
        if j[-2:] == '_L':
            press_data_fin_north.loc[press_data_fin_north['press_date_shift'] == i, 'Idling (mins)'] = \
                round(((len(press_data_fin_north[(press_data_fin_north['STEP_NUMBER_LHS'] == 0) & (press_data_fin_north['press_date_shift'] == i) & \
                                         (press_data_fin_north['PLATEN_TEMPERATURE'] >= thres_temp)])) / ratio * (log_speed / 60)),0)
            press_data_fin_north.loc[press_data_fin_north['press_date_shift'] == i, 'Saving Potential (mins)'] = \
                idling_report_north.loc[idling_report_north['press_date_shift'] == i]['Extended Steam Mins'].sum()

            press_data_fin_north.loc[press_data_fin_north['press_date_shift'] == i, 'Cutoff_Count'] = \
                press_data_fin_north.loc[press_data_fin_north['press_date_shift'] == i]['Saving Potential'].sum()
        elif j[-2:] == '_R':
            press_data_fin_north.loc[press_data_fin_north['press_date_shift'] == i, 'Idling (mins)'] = \
                round(((len(press_data_fin_north[(press_data_fin_north['STEP_NUMBER_RHS'] == 0) & (press_data_fin_north['press_date_shift'] == i) & \
                                         (press_data_fin_north['PLATEN_TEMPERATURE'] >= thres_temp)])) / ratio * (log_speed / 60)),0)
            press_data_fin_north.loc[press_data_fin_north['press_date_shift'] == i, 'Saving Potential (mins)'] = \
                idling_report_north.loc[idling_report_north['press_date_shift'] == i]['Extended Steam Mins'].sum()

            press_data_fin_north.loc[press_data_fin_north['press_date_shift'] == i, 'Cutoff_Count'] = \
                press_data_fin_north.loc[press_data_fin_north['press_date_shift'] == i]['Saving Potential'].sum()
        else:
            press_data_fin_north.loc[press_data_fin_north['press_date_shift'] == i, 'Idling (mins)'] = \
                round(((len(press_data_fin_north[(press_data_fin_north['STEP_NUMBER_RHS'] == 0) &
                                         (press_data_fin_north['STEP_NUMBER_LHS'] == 0) &
                                         (press_data_fin_north['press_date_shift'] == i) &
                                         (press_data_fin_north['PLATEN_TEMPERATURE'] >= thres_temp)])) / ratio * (log_speed / 60)),0)
            press_data_fin_north.loc[press_data_fin_north['press_date_shift'] == i, 'Saving Potential (mins)'] =\
            idling_report_north.loc[idling_report_north['press_date_shift'] == i]['Extended Steam Mins'].sum()

            press_data_fin_north.loc[press_data_fin_north['press_date_shift'] == i, 'Cutoff_Count'] = \
            press_data_fin_north.loc[press_data_fin_north['press_date_shift'] == i]['Saving Potential'].sum()
        if j[-2:] == '_L':
            press_data_fin_north.loc[press_data_fin_north['press_date_shift'] == i, 'Non-Idling (mins)'] = \
                round(((len(press_data_fin_north[
                        (press_data_fin_north['STEP_NUMBER_LHS'] != 0) & (
                                press_data_fin_north['press_date_shift'] == i)])) / ratio * (log_speed / 60)),0)
        elif j[-2:] == '_R':
            press_data_fin_north.loc[press_data_fin_north['press_date_shift'] == i, 'Non-Idling (mins)'] = \
                round(((len(press_data_fin_north[
                        (press_data_fin_north['STEP_NUMBER_RHS'] != 0) & (
                                press_data_fin_north['press_date_shift'] == i)])) / ratio * (log_speed / 60)),0)
        else:
            press_data_fin_north.loc[press_data_fin_north['press_date_shift'] == i, 'Non-Idling (mins)'] = \
                round(((len(press_data_fin_north[
                        ((press_data_fin_north['STEP_NUMBER_RHS'] != 0) | (
                                press_data_fin_north['STEP_NUMBER_LHS'] != 0)) & (
                                press_data_fin_north['press_date_shift'] == i)])) / ratio * (log_speed / 60)),0)

    press_data_fin_north = press_data_fin_north[
        ['Press_no', 'Date', 'Hour', 'Idling (mins)', 'Saving Potential (mins)','Cutoff_Count', 'Non-Idling (mins)']].drop_duplicates()
    # Saving logs in the intermediate folder =====================================================================
    press_data_fin_north['Trench'] = press_data_fin_north['Press_no'].map(new_distribution_north)
    press_data_fin_north['Trench'] = press_data_fin_north['Trench'].astype(str)
    press_data_fin_north['Trench'] = np.where(press_data_fin_north['Trench'] == "['North_Trench1']", '1', press_data_fin_north['Trench'])
    press_data_fin_north['Trench'] = np.where(press_data_fin_north['Trench'] == "['North_Trench2']", '2', press_data_fin_north['Trench'])
    press_data_fin_north['Trench'] = np.where(press_data_fin_north['Trench'] == "['North_Trench3']", '3', press_data_fin_north['Trench'])
    press_data_fin_north['Trench'] = np.where(press_data_fin_north['Trench'] == "['North_Trench4']", '4', press_data_fin_north['Trench'])
    press_data_fin_north['Trench'] = np.where(press_data_fin_north['Trench'] == "['North_Trench5']", '5', press_data_fin_north['Trench'])
    press_data_fin_north['Trench'] = np.where(press_data_fin_north['Trench'] == "['North_Trench6']", '6', press_data_fin_north['Trench'])
    print("Steam_Idling_Report", press_data_fin_north)
    press_data_fin_north.to_pickle(config_loaded['host_folder']+'Data/Intermediate Datasets/idling_log_north.pkl')
####New addition of RHS and LHS - Shounak PWC####
    # Creating Trench View==============================================================================================
    press_data_fin_south['date_shift'] = press_data_fin_south['Date'] + press_data_fin_south['Hour']
    press_data_fin_south['press_date_shift'] = press_data_fin_south['Press_no'] + press_data_fin_south['Date'] + \
                                               press_data_fin_south['Hour']
    idling_report_south['press_date_shift'] = idling_report_south['Press_no'] + idling_report_south['Date'] + idling_report_south['Shift']
    ###############################################
    press_data_fin_south = press_data_fin_south[~(press_data_fin_south['TYRE_SIZE_RHS'].isna()
                                                  & press_data_fin_south['TYRE_SIZE_LHS'].isna())]
    ####Calculation change for Steam saved - Ensuring that during a Shift the calculation is equally dynamic######
    # Allocating shifts =======================================================================================
    shift_b = ['15', '16', '17', '18', '19', '20', '21', '22']
    shift_c = ['23','00', '01', '02', '03', '04', '05', '06']
    shift_a = ['07', '08', '09', '10', '11', '12', '13', '14']
    # shift_c = ['16', '17', '18', '19', '20', '21', '22', '23']
    # shift_a = ['00', '01', '02', '03', '04', '05', '06', '07']
    # shift_b = ['08', '09', '10', '11', '12', '13', '14', '15']
    present_hour = str((datetime.datetime.now()).strftime("%H"))
    present_date =str((datetime.datetime.now()).strftime("%Y-%m-%d"))
    previous_date = str((datetime.datetime.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
    if present_hour in shift_a:
        shift_start_time=datetime.datetime.strptime(present_date + " "+shift_a[0]+":00:00","%Y-%m-%d %H:%M:%S")
        present_shift = 'Shift_A'
    elif present_hour in shift_b:
        shift_start_time=datetime.datetime.strptime(present_date + " " + shift_b[0] + ":00:00", "%Y-%m-%d %H:%M:%S")
        present_shift = 'Shift_B'
    else:
        if present_hour == '23':
            shift_start_time = datetime.datetime.strptime(present_date + " " + shift_c[0] + ":00:00",
                                                          "%Y-%m-%d %H:%M:%S")
        else:
            shift_start_time = datetime.datetime.strptime(present_date + " " + shift_c[1] + ":00:00", "%Y-%m-%d %H:%M:%S")
        present_shift = 'Shift_C'
    present = str((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S"))


    for x in press_data_fin_south['date_shift'].unique():
        data_date = press_data_fin_south.loc[press_data_fin_south['date_shift'] == x, 'Date']
        data_shift = press_data_fin_south.loc[press_data_fin_south['date_shift'] == x, 'Hour']
        ####adjusting dates and shifts#####################
        for l in data_date.unique():
            if l == present_date:
                day_flag = '1'
            else:
                if present_hour == '23':
                    if l == previous_date:
                        day_flag='1'
                    else:
                        day_flag='0'
                else:
                    day_flag = '0'
        #press_data_fin_north.loc[press_data_fin_north['press_date_shift'] == i, 'present_day'] = day_flag
        for m in data_shift.unique():
            if day_flag == '1':
                if m == present_shift:
                    shift_flag = 1
                    if m == 'Shift_C':
                        if present_hour == '23':
                            minutes_passed = ((datetime.datetime.strptime(present, "%Y-%m-%d %H:%M:%S")
                                               - shift_start_time).seconds / 60)
                        else:
                            minutes_passed = ((datetime.datetime.strptime(present, "%Y-%m-%d %H:%M:%S")
                                               - shift_start_time).seconds / 60) + 60
                    else:
                        minutes_passed = ((datetime.datetime.strptime(present, "%Y-%m-%d %H:%M:%S")
                                           - shift_start_time).seconds / 60)
                else:
                    shift_flag=0
                    minutes_passed = 480
            else:
                shift_flag=0
                minutes_passed = 480
        select_date_log = press_data_fin_south.loc[press_data_fin_south['date_shift'] == x]
        max_south=0
        for a in select_date_log['Press_no'].unique():
            len1 = len(select_date_log.loc[select_date_log['Press_no'] == a])
            temp = max_south
            if (len1 > temp):
                max_south = len1
            else:
                max_south = temp
        press_data_fin_south.loc[press_data_fin_south['date_shift'] == x, 'ratio'] = (max_south * (log_speed / 60)) / minutes_passed
    ######################################Primary calculation end####################################
    options = ['0', np.nan, '1']
    press_data_fin_south = press_data_fin_south[press_data_fin_south.Idle_Alarm.isin(options)]
    press_data_fin_south['Saving Potential'] = press_data_fin_south['Idle_Alarm']
    press_data_fin_south['Saving Potential'] = press_data_fin_south['Saving Potential'].replace('', '0')
    press_data_fin_south['Saving Potential'] = press_data_fin_south['Saving Potential'].astype(int)
    press_data_fin_south = press_data_fin_south.sort_values(['Press_no', 'Time_log'])
    press_data_fin_south.reset_index(inplace=True, drop=True)
    idle_flag = 0
    new_temp_df = press_data_fin_south['Saving Potential']
    for i in np.arange(len(press_data_fin_south)):
        if press_data_fin_south.iloc[i]['Saving Potential'] == 1 and idle_flag == 0:
            idle_flag = 1
            new_temp_df.iloc[i] = 1
        elif press_data_fin_south.iloc[i]['Saving Potential'] == 1 and idle_flag == 1:
            new_temp_df.iloc[i] = 0
        elif press_data_fin_south.iloc[i]['Saving Potential'] == 0 and idle_flag == 1:
            idle_flag = 0
            new_temp_df.iloc[i] = 0
        else:
            new_temp_df.iloc[i] = 0
            idle_flag == 0
    new_temp_df.reset_index(inplace=True, drop=True)
    press_data_fin_south['Saving Potential'] = new_temp_df
    for i in press_data_fin_south['press_date_shift'].unique():
        ratio = press_data_fin_south.loc[press_data_fin_south['press_date_shift'] == i, 'ratio']
        j = i[:7]
        if j[-2:] == '_L':
            press_data_fin_south.loc[press_data_fin_south['press_date_shift'] == i, 'Idling (mins)'] = \
                round(((len(press_data_fin_south[(press_data_fin_south['STEP_NUMBER_LHS'] == 0) & (
                        press_data_fin_south['press_date_shift'] == i) & \
                                                 (press_data_fin_south[
                                                      'PLATEN_TEMPERATURE'] >= thres_temp)])) / ratio * (
                               log_speed / 60)), 0)
            press_data_fin_south.loc[press_data_fin_south['press_date_shift'] == i, 'Saving Potential (mins)'] = \
                idling_report_south.loc[idling_report_south['press_date_shift'] == i]['Extended Steam Mins'].sum()

            press_data_fin_south.loc[press_data_fin_south['press_date_shift'] == i, 'Cutoff_Count'] = \
                press_data_fin_south.loc[press_data_fin_south['press_date_shift'] == i]['Saving Potential'].sum()
        elif j[-2:] == '_R':
            press_data_fin_south.loc[press_data_fin_south['press_date_shift'] == i, 'Idling (mins)'] = \
                round(((len(press_data_fin_south[(press_data_fin_south['STEP_NUMBER_RHS'] == 0) & (
                        press_data_fin_south['press_date_shift'] == i) & \
                                                 (press_data_fin_south[
                                                      'PLATEN_TEMPERATURE'] >= thres_temp)])) / ratio * (
                               log_speed / 60)), 0)
            press_data_fin_south.loc[press_data_fin_south['press_date_shift'] == i, 'Saving Potential (mins)'] = \
                idling_report_south.loc[idling_report_south['press_date_shift'] == i]['Extended Steam Mins'].sum()

            press_data_fin_south.loc[press_data_fin_south['press_date_shift'] == i, 'Cutoff_Count'] = \
                press_data_fin_south.loc[press_data_fin_south['press_date_shift'] == i]['Saving Potential'].sum()
        else:
            press_data_fin_south.loc[press_data_fin_south['press_date_shift'] == i, 'Idling (mins)'] = \
                round(((len(press_data_fin_south[(press_data_fin_south['STEP_NUMBER_RHS'] == 0) &
                                                 (press_data_fin_south['STEP_NUMBER_LHS'] == 0) &
                                                 (press_data_fin_south['press_date_shift'] == i) &
                                                 (press_data_fin_south[
                                                      'PLATEN_TEMPERATURE'] >= thres_temp)])) / ratio * (
                               log_speed / 60)), 0)
            press_data_fin_south.loc[press_data_fin_south['press_date_shift'] == i, 'Saving Potential (mins)'] = \
                idling_report_south.loc[idling_report_south['press_date_shift'] == i]['Extended Steam Mins'].sum()

            press_data_fin_south.loc[press_data_fin_south['press_date_shift'] == i, 'Cutoff_Count'] = \
                press_data_fin_south.loc[press_data_fin_south['press_date_shift'] == i]['Saving Potential'].sum()
        if j[-2:] == '_L':
            press_data_fin_south.loc[press_data_fin_south['press_date_shift'] == i, 'Non-Idling (mins)'] = \
                round(((len(press_data_fin_south[
                                (press_data_fin_south['STEP_NUMBER_LHS'] != 0) & (
                                        press_data_fin_south['press_date_shift'] == i)])) / ratio * (
                               log_speed / 60)), 0)
        elif j[-2:] == '_R':
            press_data_fin_south.loc[press_data_fin_south['press_date_shift'] == i, 'Non-Idling (mins)'] = \
                round(((len(press_data_fin_south[
                                (press_data_fin_south['STEP_NUMBER_RHS'] != 0) & (
                                        press_data_fin_south['press_date_shift'] == i)])) / ratio * (
                               log_speed / 60)), 0)
        else:
            press_data_fin_south.loc[press_data_fin_south['press_date_shift'] == i, 'Non-Idling (mins)'] = \
                round(((len(press_data_fin_south[
                                ((press_data_fin_south['STEP_NUMBER_RHS'] != 0) | (
                                        press_data_fin_south['STEP_NUMBER_LHS'] != 0)) & (
                                        press_data_fin_south['press_date_shift'] == i)])) / ratio * (
                               log_speed / 60)), 0)

    press_data_fin_south = press_data_fin_south[
        ['Press_no', 'Date', 'Hour', 'Idling (mins)', 'Saving Potential (mins)', 'Cutoff_Count',
         'Non-Idling (mins)']].drop_duplicates()
    # Saving logs in the intermediate folder =====================================================================
    press_data_fin_south['Trench'] = press_data_fin_south['Press_no'].map(new_distribution_south)
    press_data_fin_south['Trench'] = press_data_fin_south['Trench'].astype(str)
    press_data_fin_south['Trench'] = np.where(press_data_fin_south['Trench'] == "['South_Trench1']", '1',
                                              press_data_fin_south['Trench'])
    press_data_fin_south['Trench'] = np.where(press_data_fin_south['Trench'] == "['South_Trench2']", '2',
                                              press_data_fin_south['Trench'])
    press_data_fin_south['Trench'] = np.where(press_data_fin_south['Trench'] == "['South_Trench3']", '3',
                                              press_data_fin_south['Trench'])
    press_data_fin_south['Trench'] = np.where(press_data_fin_south['Trench'] == "['South_Trench4']", '4',
                                              press_data_fin_south['Trench'])
    press_data_fin_south['Trench'] = np.where(press_data_fin_south['Trench'] == "['South_Trench5']", '5',
                                              press_data_fin_south['Trench'])
    press_data_fin_south['Trench'] = np.where(press_data_fin_south['Trench'] == "['South_Trench6']", '6',
                                              press_data_fin_south['Trench'])
    print("Steam_Idling_Report", press_data_fin_south)
    press_data_fin_south.to_pickle(config_loaded['host_folder'] + 'Data/Intermediate Datasets/idling_log_south.pkl')
    if run == 5 * i:
        i = i + 1
        gc.collect()
        # collected = gc.collect()
        # print("Garbage collector: collected",
        #       "%d objects." % collected)