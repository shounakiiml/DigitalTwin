import pandas as pd
import numpy as np
import datetime
import warnings
import math
import time
import os, time
from main import define_config

config_loaded = define_config()

def colour_allocation_engine(data_master, mas_ui, acceptable_idling, wait_time_yellow, wait_time_red, warm_up_period, acceptable_warm_up_period, thres_temp):
    """Engine for allocating colour for individual presses
            parameter:
                data_master: table obtained form opc read
                mas_ui: table obtained from master user inputs
                acceptable_idling : idling value from config file
                wait_time_yellow: waiting time for warning
                wait_time_red: wait time for critical warning
                warm_up_period: warm up time from config
            returns:
                    master_data with color and timestamp to cut. Saves master user inputs


    """


    Total_response_time_allocated = acceptable_idling + wait_time_yellow + wait_time_red

    # Restoring null values for Master UI entries for presses which have passed the input time
    for press in mas_ui['MC_no'].unique():
        if pd.isnull(mas_ui.loc[mas_ui['MC_no'] == press, 'Input2'].iloc[0]):
            mas_ui.loc[mas_ui['MC_no'] == press, 'Input3'] = np.nan
        time_log = mas_ui.loc[mas_ui['MC_no'] == press, 'Input3'].iloc[0]
        time_input = mas_ui.loc[mas_ui['MC_no'] == press, 'Input2'].iloc[0]
        if not pd.isnull(time_log):
            time_log = pd.to_datetime(time_log)
            time_input = pd.to_datetime(time_input)

            time_log = time_log + datetime.timedelta(minutes=acceptable_warm_up_period)
            curr_time = pd.to_datetime((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
                                       format="%Y-%m-%d %H:%M:%S")
            if time_log >= time_input:
                time = 'Less than 1.5 Hrs'
            if time_log < time_input:
                time = 'Greater than 1.5 Hrs'

            if (curr_time >= time_input) & (time == 'Less than 1.5 Hrs'):
                mas_ui.loc[mas_ui['MC_no'] == press, 'Input1'] = np.nan
                mas_ui.loc[mas_ui['MC_no'] == press, 'Input2'] = np.nan
                mas_ui.loc[mas_ui['MC_no'] == press, 'Input3'] = np.nan
                data_master.loc[data_master['MC_no'] == press, 'Color'] = 'green'
                data_master.loc[data_master['MC_no'] == press, 'Time'] = 0
    mas_ui.to_pickle(config_loaded['host_folder']+'Data/Master Datasets/master_UI_data.pkl')
    # Looping through all presses ==================================================================================
    for press in data_master['MC_no'].unique():
        print("color allocation", press)
        # Allocating green colour to presses which do not have step number as 0 and resetting time of idling start to 0
        if press[-2:] == '_L':
            if (data_master.loc[data_master['MC_no'] == press, 'STEP_NUMBER_LHS'].iloc[0] != 0) \
                    and (pd.isnull(data_master.loc[data_master['MC_no'] == press, 'STEP_NUMBER_RHS'])).values[0] \
                    and (data_master.loc[data_master['MC_no'] == press, 'Color'].iloc[0] != 'grey'):  ##change done-Shounak
                data_master.loc[data_master['MC_no'] == press, 'Color'] = 'green'
                data_master.loc[data_master['MC_no'] == press, 'Time'] = 0
                mas_ui.loc[mas_ui['MC_no'] == press, 'Input1'] = np.nan
                mas_ui.loc[mas_ui['MC_no'] == press, 'Input2'] = np.nan
                mas_ui.loc[mas_ui['MC_no'] == press, 'Input3'] = np.nan
        elif press[-2:] == '_R':
            if (data_master.loc[data_master['MC_no'] == press, 'STEP_NUMBER_RHS'].iloc[0] != 0) \
                    and (pd.isnull(data_master.loc[data_master['MC_no'] == press, 'STEP_NUMBER_LHS'])).values[0] and (
                    data_master.loc[data_master['MC_no'] == press, 'Color'].iloc[
                        0] != 'grey'):  ##change done-Shounak
                data_master.loc[data_master['MC_no'] == press, 'Color'] = 'green'
                data_master.loc[data_master['MC_no'] == press, 'Time'] = 0
                mas_ui.loc[mas_ui['MC_no'] == press, 'Input1'] = np.nan
                mas_ui.loc[mas_ui['MC_no'] == press, 'Input2'] = np.nan
                mas_ui.loc[mas_ui['MC_no'] == press, 'Input3'] = np.nan
        else:
            if (data_master.loc[data_master['MC_no'] == press, 'STEP_NUMBER_RHS'].iloc[0] != 0) \
                    and (data_master.loc[data_master['MC_no'] == press, 'STEP_NUMBER_LHS'].iloc[0] != 0) and (
                    data_master.loc[data_master['MC_no'] == press, 'Color'].iloc[
                        0] != 'grey'):  ##change done-Shounak
                data_master.loc[data_master['MC_no'] == press, 'Color'] = 'green'
                data_master.loc[data_master['MC_no'] == press, 'Time'] = 0
                mas_ui.loc[mas_ui['MC_no'] == press, 'Input1'] = np.nan
                mas_ui.loc[mas_ui['MC_no'] == press, 'Input2'] = np.nan
                mas_ui.loc[mas_ui['MC_no'] == press, 'Input3'] = np.nan
            # Allocating green colour to presses which do not have step number RHS as 0 and resetting time of idling start to 0
            if (data_master.loc[data_master['MC_no'] == press, 'STEP_NUMBER_RHS'].iloc[0] == 0) \
                    and (data_master.loc[data_master['MC_no'] == press, 'STEP_NUMBER_LHS'].iloc[0] != 0) and (
                    data_master.loc[data_master['MC_no'] == press, 'Color'].iloc[
                        0] != 'grey'):  ##change done-Shounak
                data_master.loc[data_master['MC_no'] == press, 'Color'] = 'green'
                data_master.loc[data_master['MC_no'] == press, 'Time'] = 0
                mas_ui.loc[mas_ui['MC_no'] == press, 'Input1'] = np.nan
                mas_ui.loc[mas_ui['MC_no'] == press, 'Input2'] = np.nan
                mas_ui.loc[mas_ui['MC_no'] == press, 'Input3'] = np.nan
            # Allocating green colour to presses which do not have step number LHS as 0 and resetting time of idling start to 0
            if (data_master.loc[data_master['MC_no'] == press, 'STEP_NUMBER_RHS'].iloc[0] != 0) \
                    and (data_master.loc[data_master['MC_no'] == press, 'STEP_NUMBER_LHS'].iloc[0] == 0) and (
                    data_master.loc[data_master['MC_no'] == press, 'Color'].iloc[
                        0] != 'grey'):  ##change done-Shounak
                data_master.loc[data_master['MC_no'] == press, 'Color'] = 'green'
                data_master.loc[data_master['MC_no'] == press, 'Time'] = 0
                mas_ui.loc[mas_ui['MC_no'] == press, 'Input1'] = np.nan
                mas_ui.loc[mas_ui['MC_no'] == press, 'Input2'] = np.nan
                mas_ui.loc[mas_ui['MC_no'] == press, 'Input3'] = np.nan

        # Logging time for presses which have step number 0 and temperature greater than threshold temperature =====================
        if (data_master.loc[data_master['MC_no'] == press, 'STEP_NUMBER_RHS'].iloc[0] == 0) \
                and (data_master.loc[data_master['MC_no'] == press, 'STEP_NUMBER_LHS'].iloc[0] == 0) and (
                data_master.loc[data_master['MC_no'] == press, 'MC_TEMPERATURE'].iloc[0] >= thres_temp) and (
                data_master.loc[data_master['MC_no'] == press, 'Time'].iloc[0] == 0):##change done-Shounak
            data_master.loc[data_master['MC_no'] == press, 'Time'] = pd.to_datetime(
                (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S"), format="%Y-%m-%d %H:%M:%S")
            ###for hetero machines -- 1
        if ((data_master.loc[data_master['MC_no'] == press, 'STEP_NUMBER_RHS'].iloc[0] == 0)
            or (pd.isnull(data_master.loc[data_master['MC_no'] == press, 'STEP_NUMBER_RHS'].iloc[0]))) \
                and ((data_master.loc[data_master['MC_no'] == press, 'STEP_NUMBER_LHS'].iloc[0] == 0)
                     or (pd.isnull(data_master.loc[data_master['MC_no'] == press, 'STEP_NUMBER_LHS'].iloc[0]))) \
                and (data_master.loc[data_master['MC_no'] == press, 'MC_TEMPERATURE'].iloc[0] >= thres_temp) \
                and (data_master.loc[data_master['MC_no'] == press, 'Time'].iloc[0] == 0):
            data_master.loc[data_master['MC_no'] == press, 'Time'] = pd.to_datetime(
                (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S"), format="%Y-%m-%d %H:%M:%S")

        # Allocating Colour for presses which are Idling =========================================================
        if ((data_master.loc[data_master['MC_no'] == press, 'STEP_NUMBER_RHS'].iloc[0] == 0) or pd.isnull(data_master.loc[data_master['MC_no'] == press, 'STEP_NUMBER_RHS'].iloc[0])) \
                and ((data_master.loc[data_master['MC_no'] == press, 'STEP_NUMBER_LHS'].iloc[0] == 0) or pd.isnull(data_master.loc[data_master['MC_no'] == press, 'STEP_NUMBER_LHS'].iloc[0])) \
                and (data_master.loc[data_master['MC_no'] == press, 'MC_TEMPERATURE'].iloc[0] >= thres_temp) \
                and (data_master.loc[data_master['MC_no'] == press, 'Time'].iloc[0] != 0):

                 ##change done-Shounak

            op_in_time = mas_ui[mas_ui['MC_no'] == press]['Input3'].iloc[0]
            print("color allocation op_in_time", op_in_time)
            # Default logic applied for presses for which there are no User Inputs==================================
            # BASED ON CHENNAI PLANT INPUTS
            # First 5 minutes of Idling  - Green
            # Next 25 minutes of Idling  - Yellow
            # Next 5 minutes of Idling   - Red
            if pd.isnull(op_in_time):
                data_master.loc[data_master['MC_no'] == press, 'Time_to_cut_off'] = \
                    data_master.loc[data_master['MC_no'] == press, 'Time'].iloc[0] + datetime.timedelta(
                        minutes=Total_response_time_allocated)
                time_to_cutoff = (data_master.loc[data_master['MC_no'] == press, 'Time_to_cut_off'].iloc[
                                      0] - pd.to_datetime((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
                                                          format="%Y-%m-%d %H:%M:%S")).total_seconds()
                if time_to_cutoff >= 0:

                    if (time_to_cutoff / 60 < (Total_response_time_allocated - acceptable_idling - wait_time_yellow)) \
                            and (time_to_cutoff / 60 >= 0):
                        data_master.loc[data_master['MC_no'] == press, 'Color'] = 'red'

                    if (time_to_cutoff / 60 >= (Total_response_time_allocated - wait_time_yellow - wait_time_red)) and (
                            time_to_cutoff / 60 <= (Total_response_time_allocated - acceptable_idling)):
                        data_master.loc[data_master['MC_no'] == press, 'Color'] = 'yellow'

                    if (time_to_cutoff / 60 > (Total_response_time_allocated - acceptable_idling)) and (
                            time_to_cutoff / 60 <= Total_response_time_allocated):
                        data_master.loc[data_master['MC_no'] == press, 'Color'] = 'green'
                if time_to_cutoff < 0:
                    data_master.loc[data_master['MC_no'] == press, 'Color'] = '#3085B0'

            # If User Input is present then colours are allocated based on User Inputs=================================
            else:
                if pd.isnull(mas_ui.loc[mas_ui['MC_no'] == press, 'Input2'].iloc[0]):
                    mas_ui.loc[mas_ui['MC_no'] == press, 'Input3'] = np.nan
                time_log = mas_ui.loc[mas_ui['MC_no'] == press, 'Input3'].iloc[0]
                time_input = mas_ui.loc[mas_ui['MC_no'] == press, 'Input2'].iloc[0]
                # If User Input is present then colours are allocated based on User Inputs==============================
                if not pd.isnull(time_log):
                    time_log = pd.to_datetime(time_log)
                    time_input = pd.to_datetime(time_input)
                    time_log = time_log + datetime.timedelta(minutes=acceptable_warm_up_period)
                    curr_time = pd.to_datetime((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
                                               format="%Y-%m-%d %H:%M:%S")
                    if time_log >= time_input:
                        time = 'Less than 1.5 Hrs'
                    if time_log < time_input:
                        time = 'Greater than 1.5 Hrs'
                # If User Input is less than warm up period then warm up is started==============================
                if time == 'Less than 1.5 Hrs':
                    data_master.loc[data_master['MC_no'] == press, 'Time_to_cut_off'] = np.nan
                    data_master.loc[data_master['MC_no'] == press, 'Color'] = 'yellow' #'#FF9333'
                # If User Input is greater than warm up period then by default steam is stopped===================
                elif time == 'Greater than 1.5 Hrs':
                    data_master.loc[data_master['MC_no'] == press, 'Color'] = '#C76666'
                if time == 'Greater than 1.5 Hrs':
                    time_input = mas_ui.loc[mas_ui['MC_no'] == press, 'Input2'].iloc[0]
                    time_input = pd.to_datetime(time_input)
                    curr_time = pd.to_datetime((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
                                               format="%Y-%m-%d %H:%M:%S")
                    remaining_time = ((time_input - curr_time).total_seconds()) / 60
                    # If Current Time is greater than warm up period then warm up is started=====================
                    if (remaining_time <= warm_up_period) & (remaining_time >= 0):
                        ###if condition added - Shounak PWC######################
                        if data_master.loc[data_master['MC_no'] == press, 'MC_TEMPERATURE'].iloc[0] < thres_temp:
                            data_master.loc[data_master['MC_no'] == press, 'Color'] = '#FF9333'
                        else:
                            data_master.loc[data_master['MC_no'] == press, 'Color'] = 'yellow'
                    # If Current Time is past the warm up period then press is allocated green===================
                    if remaining_time < 0:
                        data_master.loc[data_master['MC_no'] == press, 'Color'] = 'green'
                        data_master.loc[data_master['MC_no'] == press, 'Time'] = 0
                        mas_ui.loc[mas_ui['MC_no'] == press, 'Input1'] = np.nan
                        mas_ui.loc[mas_ui['MC_no'] == press, 'Input2'] = np.nan
                        mas_ui.loc[mas_ui['MC_no'] == press, 'Input3'] = np.nan


        # Loop for Presses which are in steam off condition======================================================
        if data_master.loc[data_master['MC_no'] == press, 'MC_TEMPERATURE'].iloc[0] < thres_temp: ##change to make code dynamic-Shounak
            op_in_time = mas_ui[mas_ui['MC_no'] == press]['Input3'].iloc[0]
            # Similar logic commented above=========================================================================
            if pd.isnull(op_in_time):
                data_master.loc[data_master['MC_no'] == press, 'Color'] = '#C76666'
                mas_ui.loc[mas_ui['MC_no'] == press, 'Input1'] = np.nan
                mas_ui.loc[mas_ui['MC_no'] == press, 'Input2'] = np.nan
                mas_ui.loc[mas_ui['MC_no'] == press, 'Input3'] = np.nan
            else:
                if pd.isnull(mas_ui.loc[mas_ui['MC_no'] == press, 'Input2'].iloc[0]):
                    mas_ui.loc[mas_ui['MC_no'] == press, 'Input3'] = np.nan
                time_log = mas_ui.loc[mas_ui['MC_no'] == press, 'Input3'].iloc[0]
                time_input = mas_ui.loc[mas_ui['MC_no'] == press, 'Input2'].iloc[0]
                # Similar logic commented above=========================================================================
                if not pd.isnull(time_log):
                    time_log = pd.to_datetime(time_log)
                    time_input = pd.to_datetime(time_input)

                    time_log = time_log + datetime.timedelta(minutes=acceptable_warm_up_period)
                    curr_time = pd.to_datetime((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
                                               format="%Y-%m-%d %H:%M:%S")
                    if time_log >= time_input:
                        time = 'Less than 1.5 Hrs'
                    if time_log < time_input:
                        time = 'Greater than 1.5 Hrs'
                # Similar logic commented above=========================================================================
                if time == 'Less than 1.5 Hrs':
                    data_master.loc[data_master['MC_no'] == press, 'Time_to_cut_off'] = np.nan
                    data_master.loc[data_master['MC_no'] == press, 'Color'] = '#FF9333'
                elif time == 'Greater than 1.5 Hrs':
                    data_master.loc[data_master['MC_no'] == press, 'Color'] = '#C76666'
                # Similar logic commented above=========================================================================

                if time == 'Greater than 1.5 Hrs':
                    time_input = mas_ui.loc[mas_ui['MC_no'] == press, 'Input2'].iloc[0]
                    time_input = pd.to_datetime(time_input)
                    curr_time = pd.to_datetime((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
                                               format="%Y-%m-%d %H:%M:%S")
                    remaining_time = ((time_input - curr_time).total_seconds()) / 60
                    if (remaining_time <= warm_up_period) & (remaining_time >= 0):
                        data_master.loc[data_master['MC_no'] == press, 'Color'] = '#FF9333'
                    if remaining_time < 0:
                        data_master.loc[data_master['MC_no'] == press, 'Color'] = 'green'
                        data_master.loc[data_master['MC_no'] == press, 'Time'] = 0
                        mas_ui.loc[mas_ui['MC_no'] == press, 'Input1'] = np.nan
                        mas_ui.loc[mas_ui['MC_no'] == press, 'Input2'] = np.nan
                        mas_ui.loc[mas_ui['MC_no'] == press, 'Input3'] = np.nan
    mas_ui.to_pickle(config_loaded['host_folder']+'Data/Master Datasets/master_UI_data.pkl')
    return data_master


def log_creation(data_master, MC_overwrite):
    """Creates a log of recent most colour allocation and User inputs"""
    # Saving recent most log with the current timestamp==========================================
    mas_ui = pd.read_pickle(config_loaded['host_folder']+'Data/Master Datasets/master_UI_data.pkl')
    today = str((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S"))
    today = today.replace(':', '_')
    # Consolidating colour, user inputs and press overwrite into one file==================================

    temp_n = data_master[
        ['MC_no', 'Time', 'Color', 'MC_TEMPERATURE', 'STEP_NUMBER_RHS', 'STEP_NUMBER_LHS', 'PROD_TYPE_RHS',
         'PROD_TYPE_LHS', 'Time_to_cut_off', 'Idle_Alarm']].copy()

    temp_n = pd.merge(temp_n, MC_overwrite.drop(['Change To', 'Submit'], axis=1), left_on='MC_no',
                      right_on='MC_no', how='left')
    #temp_n = temp_n.drop('MC_no', axis=1)
    temp_n = pd.merge(temp_n, mas_ui, left_on='MC_no', right_on='MC_no',
                      how='left')
    temp_n['Time_log'] = str((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S"))
    temp_n.to_pickle(config_loaded['host_folder']+'Data/Historical Logs/log' + '_' + today + '.pkl')


    # Removing logs older than 7 days==========================================
    import os
    path = config_loaded['host_folder']+"Data/Historical Logs"
    current_time = time.time()
    for f in os.listdir(path):
        f = os.path.join(path, f)
        creation_time = os.path.getctime(f)
        if (current_time - creation_time) // (24 * 3600) >= 5:
            os.unlink(f)
            print('{} removed'.format(f))
    #return temp_n

def retrieve_state(data_master, prev_master_ui, mas_ui):
    side=''
    offline_press = data_master[data_master.MC_TEMPERATURE.isnull()]
    online_press = data_master[data_master.MC_TEMPERATURE.notnull()]

    #####putting previous mas_ui value##
    ######end###########################
    df = pd.DataFrame(columns=['MC_no', 'Input1', 'Input2', 'Input3'])
    df = df.fillna(method='bfill')
    idle_press_input = prev_master_ui[prev_master_ui.Input2.notnull()]

    ###################for press that turned offline now#######################
    for press in offline_press['MC_no']:
        for press1 in idle_press_input['MC_no']:
            if press == press1:
                new_df = idle_press_input.loc[idle_press_input['MC_no'] == press1]
                #df = df.append(new_df)
                df=pd.concat([df,new_df])
                df.to_pickle(
                    config_loaded['host_folder'] + 'Data/Secondary Data/offline_press'+side+'.pkl')
        ###################for press that has turned online now#########################
    prev_input = pd.read_pickle(
        config_loaded['host_folder'] + 'Data/Secondary Data/offline_mc'+side+'.pkl')
    for press2 in prev_input['MC_no']:
        for press3 in online_press['MC_no']:
            if press3 == press2:
                mas_ui.loc[mas_ui['MC_no'] == press2] = prev_input
                prev_input.drop(prev_input.index[prev_input['MC_no'] == press2], inplace=True)
                prev_input.to_pickle(
                    config_loaded['host_folder'] + 'Data/Secondary Data/offline_mc'+side+'.pkl')
    return mas_ui