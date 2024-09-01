import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta
import warnings
import math
import time
from opcua import Client, ua
import sys
from main import define_config
config_loaded = define_config()
# url1 = config_loaded['OPC Tags']['url3']
# url2 = config_loaded['OPC Tags']['url2']
# import logging
# from logging.config import fileConfig
# fileConfig(config_loaded['host_folder']+'Configuration/logging_config.ini')
# logger = logging.getLogger()
hetero_list = config_loaded['Heterogeneous press']
trigger_val=config_loaded['OPC Tags']['Output Tags']['trigger_all']
reset_val=config_loaded['OPC Tags']['Output Tags']['reset_bit']
reset_val2=config_loaded['OPC Tags']['Output Tags']['reset_bit2']
# def connection_retry(client, retry_count=1):
#     '''
#     Similar to opc read refer
#     '''
#     counter = 0
#     while 1:
#         counter += counter
#         # logger.warning("CONNECTION FAILED...RETRYING ATTEMPT..." + str(counter))
#         client_root_obj = None
#         try:
#             client_root_obj = client.get_root_node()
#         except:
#             pass
#         if client_root_obj is None:
#             time.sleep(10)
#             continue
#         else:
#             return client

def OPC_write_back(data_master, press_overwrite,trench_switch, trench_distribution, acceptable_warm_up_period, thres_temp):
    '''
    writes back 0/1 to OPC server tag based on color allocated
    :param client: client object
    :param data_master: data master file obtained form OPC_read_script
    :param press_overwrite: data file for press overwrite logic
    :param trench_switch: trench switch list from config file
    :param trench_distribution: press list from config file
    :return: Nothing. Simply write 0/1 to opc
    :return: Nothing. Simply write 0/1 to opc
    '''
    start_time = datetime.now()
    #client2=Client(url2)
    """Writes back to the OPC"""
    try:
        #client.connect()
        #logger.info("CONNECTION ESTABLISHED IN OPC_WRITE.....")
    except Exception as ce:
        try:
            import time
            #logger.error("CONNECTION FAILED IN OPC_WRITE....." + str(ce))
            #client = connection_retry(client2)
        except Exception as ce:
            print(ce)
            #logger.error("CONNECTION FAILED 2 IN OPC_WRITE....." + str(ce))
            pass
    #logger.info("INSIDE MAIN TRY IN OPC_WRITE.....")

    # Changing press overwrite column into 1/0========================================================================
    press_overwrite['Last Change To'] = np.where(press_overwrite['Last Change To'] == 'Switch Off', '1',
                                                 press_overwrite['Last Change To'])
    press_overwrite['Last Change To'] = np.where(press_overwrite['Last Change To'] == 'Switch On', '0',
                                                 press_overwrite['Last Change To'])
    press_overwrite['Last Input Time'] = pd.to_datetime(press_overwrite['Last Input Time'], format='%Y-%m-%d %H:%M:%S')

    # Collating shortlisted trenches=================================================================================
    trenches = [trench for trench in trench_switch if trench_switch[trench] == 1]
    trench_shortlist = []

    for trench in trenches:
        trench_shortlist.append(trench_distribution[trench])

    trench_shortlist = [item for sublist in trench_shortlist for item in sublist]
    hetero_list_north=[]
    for i in trench_shortlist:
        if i in hetero_list:
            hetero_list_north.append(i)
    for i in hetero_list_north:
        trench_shortlist.remove(i)
    for i in hetero_list_north:
        y = i + '_L'
        z = i + '_R'
        trench_shortlist.append(y)
        trench_shortlist.append(z)

    # Creating Write back dataset ===================================================================================
    opc_write = data_master[['Press_no', 'Color']].copy()

    opc_write = opc_write[opc_write['Press_no'].isin(trench_shortlist)]
    #####OPC Write is 1 for blue and maroon#######################
    opc_write['Color'] = np.where((opc_write['Color'] == '#3085B0') | (opc_write['Color'] == '#C76666'), '1', '0')
    # Loop to write back to OPC ====================================================================================

    for press in opc_write['Press_no'].unique():
        try:
            #logger.info("INSIDE MAIN TRY OF OPC_WRITE...")
            time = press_overwrite[press_overwrite['Press_No'] == press]['Last Input Time'].iloc[0]
            time_now = pd.to_datetime((datetime.now()).strftime("%Y-%m-%d %H:%M:%S"), format="%Y-%m-%d %H:%M:%S")
            # Press Overwrite Takes precedence over the normal logic for the warm up duration defined by the user========
            # Press Wrtie back using normal logic =======================================================================
            if (time_now >= time + timedelta(minutes=acceptable_warm_up_period)) | pd.isnull(time):
                '''
                if last input time from press overwrite is less than current system time, normal logic will be applied
                else press overwrite will be run from else part
                '''
                alarm = opc_write[opc_write['Press_no'] == press]['Color'].iloc[0]

                # Reverse situation
                if (data_master.loc[data_master['Press_no'] == press, 'PLATEN_TEMPERATURE'].iloc[0] >= thres_temp) \
                        & (alarm == '1'):
                    opc_write.loc[opc_write['Press_no'] == press, 'Color'] = '#3085B0'
                if (data_master.loc[data_master['Press_no'] == press, 'PLATEN_TEMPERATURE'].iloc[0] >= thres_temp) \
                        & (alarm == '0'):
                    opc_write.loc[opc_write['Press_no'] == press, 'Color'] = 'green'
                ##############Adding new column Idle_Alarm in data master####################
                #data_master.loc[data_master['Press_no'] == press, 'Idle_Alarm'] = alarm
                #print("In OPC writing loop for changing color",alarm,"------",press)
                try:
                    #logger.info("INSIDE SUB TRY OF OPC_WRITE...")
                    #press_phase = press + "." + press
                    if press[-2:] == '_L':
                        press_phase = press[:-2] + "." + press[:-2]
                        temp = 'NORTH_TRENCH.TCM75.sp_STEAM_IDLING_ALARM_LHS'
                        temp = temp.replace("NORTH_TRENCH.TCM75", press_phase)
                        val = client.get_node("ns=2;s=" + temp)
                        val.set_attribute(ua.AttributeIds.Value, ua.DataValue(alarm))
                    elif press[-2:] == '_R':
                        press_phase = press[:-2] + "." + press[:-2]
                        temp = 'NORTH_TRENCH.TCM75.sp_STEAM_IDLING_ALARM_RHS'
                        temp = temp.replace("NORTH_TRENCH.TCM75", press_phase)
                        val = client.get_node("ns=2;s=" + temp)
                        val.set_attribute(ua.AttributeIds.Value, ua.DataValue(alarm))
                    else:
                        press_phase = press + "." + press
                        temp = 'NORTH_TRENCH.TCM75.sp_STEAM_IDLING_ALARM'
                        temp = temp.replace("NORTH_TRENCH.TCM75", press_phase)
                        val = client.get_node("ns=2;s=" + temp)
                        val.set_attribute(ua.AttributeIds.Value, ua.DataValue(alarm))

                except Exception as e:
                    # print(press)
                    #logger.error("INSIDE SUB TRY OF OPC_WRITE..." + str(press) + " : " + str(e))
                    pass
            else:
                # Press Wrtie back using overwrite logic =======================================================================
                '''
                assigns alarm value 0/1 from last change to - switch off 1, switch on 0 from press overwrite
                refer above commented part changing press overwrite column last change to
                '''

                print("giving alarm")
                alarm = str(press_overwrite[press_overwrite['Press_No'] == press]['Last Change To'].iloc[0])
                ##########Added column in Data master###############################
                #data_master.loc[data_master['Press_no'] == press, 'Idle_Alarm'] = alarm
                if (data_master.loc[data_master['Press_no'] == press, 'PLATEN_TEMPERATURE'].iloc[0] >= thres_temp) \
                        & (alarm == '1'):
                    data_master.loc[data_master['Press_no'] == press, 'Color'] = '#3085B0'
                if (data_master.loc[data_master['Press_no'] == press, 'PLATEN_TEMPERATURE'].iloc[
                        0] >= thres_temp) & (alarm == '0'):
                    data_master.loc[data_master['Press_no'] == press, 'Color'] = 'green'
                try:
                    #logger.info("INSIDE SUB2 TRY IN OPC_WRITE.....")
                    #press_phase = press+"."+press
                    if press[-2:] == '_L':
                        press_phase = press[:-2] + "." + press[:-2]
                        temp = 'NORTH_TRENCH.TCM75.sp_STEAM_IDLING_ALARM_LHS'
                        temp = temp.replace("NORTH_TRENCH.TCM75", press_phase)
                        val = client.get_node("ns=2;s=" + temp)
                        val.set_attribute(ua.AttributeIds.Value, ua.DataValue(alarm))
                    if press[-2:] == '_R':
                        press_phase = press[:-2] + "." + press[:-2]
                        temp = 'NORTH_TRENCH.TCM75.sp_STEAM_IDLING_ALARM_RHS'
                        temp = temp.replace("NORTH_TRENCH.TCM75", press_phase)
                        val = client.get_node("ns=2;s=" + temp)
                        val.set_attribute(ua.AttributeIds.Value, ua.DataValue(alarm))
                    else:
                        press_phase = press + "." + press
                        temp = 'NORTH_TRENCH.TCM75.sp_STEAM_IDLING_ALARM'
                        temp = temp.replace("NORTH_TRENCH.TCM75", press_phase)
                        val = client.get_node("ns=2;s=" + temp)
                        val.set_attribute(ua.AttributeIds.Value, ua.DataValue(alarm))
                except:
                    #logger.error("NP : ERROR IN SETTING ATTRIBUTION INSIDE SUB2 EXCEPT IN OPC_WRITE.....")
                    # print("ERROR IN SETTING ATTRIBUTION.........................")
                    # print('NP')
                    pass
        except Exception as e:
            print(ce)
            #logger.error("INSIDE FOR EXCEPT IN OPC_WRITE....." + str(e))
            pass
    print('disconnecting write back connect')
    client.disconnect()
    end_time = datetime.now()
    #logger.info('DISCONNECTING....DURATION OF OPC WRITE....: {}'.format(end_time - start_time))

def OPC_write_back_south(client, data_master, press_overwrite,trench_switch, trench_distribution, acceptable_warm_up_period, thres_temp):
    '''
    writes back 0/1 to OPC server tag based on color allocated
    :param client: client object
    :param data_master: data master file obtained form OPC_read_script
    :param press_overwrite: data file for press overwrite logic
    :param trench_switch: trench switch list from config file
    :param trench_distribution: press list from config file
    :return: Nothing. Simply write 0/1 to opc
    '''
    start_time = datetime.now()
    client2=Client(url2)
    """Writes back to the OPC"""
    try:
        client.connect()
        #logger.info("CONNECTION ESTABLISHED IN OPC_WRITE.....")
    except Exception as ce:
        try:
            import time
            #logger.error("CONNECTION FAILED IN OPC_WRITE....." + str(ce))
            client = connection_retry(client2)
        except Exception as ce:
            print(ce)
            #logger.error("CONNECTION FAILED 2 IN OPC_WRITE....." + str(ce))
            pass
    #logger.info("INSIDE MAIN TRY IN OPC_WRITE.....")

    # Changing press overwrite column into 1/0========================================================================
    press_overwrite['Last Change To'] = np.where(press_overwrite['Last Change To'] == 'Switch Off', '1',
                                                 press_overwrite['Last Change To'])
    press_overwrite['Last Change To'] = np.where(press_overwrite['Last Change To'] == 'Switch On', '0',
                                                 press_overwrite['Last Change To'])
    press_overwrite['Last Input Time'] = pd.to_datetime(press_overwrite['Last Input Time'], format='%Y-%m-%d %H:%M:%S')

    # Collating shortlisted trenches=================================================================================
    trenches = [trench for trench in trench_switch if trench_switch[trench] == 1]
    trench_shortlist = []
    for trench in trenches:
        trench_shortlist.append(trench_distribution[trench])

    trench_shortlist = [item for sublist in trench_shortlist for item in sublist]

    hetero_list_south=[]
    for i in trench_shortlist:
        if i in hetero_list:
            hetero_list_south.append(i)
    for i in hetero_list_south:
        trench_shortlist.remove(i)
    for i in hetero_list_south:
        y = i + '_L'
        z = i + '_R'
        trench_shortlist.append(y)
        trench_shortlist.append(z)
    # Creating Write back dataset ===================================================================================
    opc_write = data_master[['Press_no', 'Color']].copy()

    opc_write = opc_write[opc_write['Press_no'].isin(trench_shortlist)]
    opc_write['Color'] = np.where((opc_write['Color'] == '#3085B0') | (opc_write['Color'] == '#C76666'), '1', '0')
    # Loop to write back to OPC ====================================================================================

    for press in opc_write['Press_no'].unique():
        try:
            #logger.info("INSIDE MAIN TRY OF OPC_WRITE...")
            time = press_overwrite[press_overwrite['Press_No'] == press]['Last Input Time'].iloc[0]
            time_now = pd.to_datetime((datetime.now()).strftime("%Y-%m-%d %H:%M:%S"), format="%Y-%m-%d %H:%M:%S")
            # Press Overwrite Takes precedence over the normal logic for the warm up duration defined by the user========
            # Press Wrtie back using normal logic =======================================================================
            if (time_now >= time + timedelta(minutes=acceptable_warm_up_period)) | pd.isnull(time):
                '''
                if last input time from press overwrite is less than current system time, normal logic will be applied
                else press overwrite will be run from else part
                '''
                alarm = opc_write[opc_write['Press_no'] == press]['Color'].iloc[0]
                # Reverse situation South
                if (data_master.loc[data_master['Press_no'] == press, 'PLATEN_TEMPERATURE'].iloc[0] >= thres_temp) \
                        & (alarm == '1'):
                    opc_write.loc[opc_write['Press_no'] == press, 'Color'] = '#3085B0'
                if (data_master.loc[data_master['Press_no'] == press, 'PLATEN_TEMPERATURE'].iloc[
                        0] >= thres_temp) & (alarm == '0'):
                    opc_write.loc[opc_write['Press_no'] == press, 'Color'] = 'green'
                #data_master.loc[data_master['Press_no'] == press, 'Idle_Alarm'] = alarm
                #print("In OPC writing loop for changing color",alarm,"------",press)
                try:
                    #logger.info("INSIDE SUB TRY OF OPC_WRITE...")
                    if press[-2:] == '_L':
                        press_phase = press[:-2] + "." + press[:-2]
                        temp = 'NORTH_TRENCH.TCM75.sp_STEAM_IDLING_ALARM_LHS'
                        temp = temp.replace("NORTH_TRENCH.TCM75", press_phase)
                        val = client.get_node("ns=2;s=" + temp)
                        val.set_attribute(ua.AttributeIds.Value, ua.DataValue(alarm))
                    elif press[-2:] == '_R':
                        press_phase = press[:-2] + "." + press[:-2]
                        temp = 'NORTH_TRENCH.TCM75.sp_STEAM_IDLING_ALARM_RHS'
                        temp = temp.replace("NORTH_TRENCH.TCM75", press_phase)
                        val = client.get_node("ns=2;s=" + temp)
                        val.set_attribute(ua.AttributeIds.Value, ua.DataValue(alarm))
                    else:
                        press_phase = press + "." + press
                        temp = 'NORTH_TRENCH.TCM75.sp_STEAM_IDLING_ALARM'
                        temp = temp.replace("NORTH_TRENCH.TCM75", press_phase)
                        val = client.get_node("ns=2;s=" + temp)
                        val.set_attribute(ua.AttributeIds.Value, ua.DataValue(alarm))
                except Exception as e:
                    print(press,ce)
                    #logger.error("INSIDE SUB TRY OF OPC_WRITE..." + str(press) + " : " + str(e))
                    pass
            else:
                # Press Wrtie back using overwrite logic =======================================================================
                '''
                assigns alarm value 0/1 from last change to - switch off 1, switch on 0 from press overwrite
                refer above commented part changing press overwrite column last change to
                '''
                print("giving alarm")
                alarm = str(press_overwrite[press_overwrite['Press_No'] == press]['Last Change To'].iloc[0])
                #data_master.loc[data_master['Press_no'] == press, 'Idle_Alarm'] = alarm
                if (data_master.loc[data_master['Press_no'] == press, 'PLATEN_TEMPERATURE'].iloc[0] >= thres_temp) & (
                        alarm == '1'):
                    data_master.loc[data_master['Press_no'] == press, 'Color'] = '#3085B0'
                if (data_master.loc[data_master['Press_no'] == press, 'PLATEN_TEMPERATURE'].iloc[0] >= thres_temp) & (
                        alarm == '0'):
                    data_master.loc[data_master['Press_no'] == press, 'Color'] = 'green'
                try:
                    #logger.info("INSIDE SUB2 TRY IN OPC_WRITE.....")
                    #press_phase = press+"."+press
                    if press[-2:] == '_L':
                        press_phase = press[:-2] + "." + press[:-2]
                        temp = 'NORTH_TRENCH.TCM75.sp_STEAM_IDLING_ALARM_LHS'
                        temp = temp.replace("NORTH_TRENCH.TCM75", press_phase)
                        val = client.get_node("ns=2;s=" + temp)
                        val.set_attribute(ua.AttributeIds.Value, ua.DataValue(alarm))
                    elif press[-2:] == '_R':
                        press_phase = press[:-2] + "." + press[:-2]
                        temp = 'NORTH_TRENCH.TCM75.sp_STEAM_IDLING_ALARM_RHS'
                        temp = temp.replace("NORTH_TRENCH.TCM75", press_phase)
                        val = client.get_node("ns=2;s=" + temp)
                        val.set_attribute(ua.AttributeIds.Value, ua.DataValue(alarm))
                    else:
                        press_phase = press + "." + press
                        temp = 'NORTH_TRENCH.TCM75.sp_STEAM_IDLING_ALARM'
                        temp = temp.replace("NORTH_TRENCH.TCM75", press_phase)
                        val = client.get_node("ns=2;s=" + temp)
                        val.set_attribute(ua.AttributeIds.Value, ua.DataValue(alarm))
                except:
                    print('error in OPC writing south')
                    #logger.error("NP : ERROR IN SETTING ATTRIBUTION INSIDE SUB2 EXCEPT IN OPC_WRITE.....")
                    # print("ERROR IN SETTING ATTRIBUTION.........................")
                    # print('NP')
                    pass
        except Exception as e:
            print(e)
            #logger.error("INSIDE FOR EXCEPT IN OPC_WRITE....." + str(e))
            pass
    print('disconnecting write back connect')
    client.disconnect()
    end_time = datetime.now()
    #logger.info('DISCONNECTING....DURATION OF OPC WRITE....: {}'.format(end_time - start_time))

#####Steam AI part######
def opc_trigger():
    import time
    def parse_time(q):
        return datetime.strptime(q, '%I:%M %p')
    present_time = datetime.now()
    start_time='07:00 AM'
    end_time = datetime.strptime(start_time, '%I:%M %p') + timedelta(minutes=3)
    client = Client(url1)
    check_present_time=parse_time(present_time.strftime("%I:%M %p"))
    check_start_time = parse_time(start_time)
    check_end_time = parse_time(end_time.strftime("%I:%M %p"))
    """Writes back to the OPC"""
    try:
        client.connect()
    except Exception as ce:
        try:
            import time
            #logger.error("CONNECTION FAILED IN OPC_WRITE....." + str(ce))
            client = connection_retry(client)
        except Exception as ce:
            print(ce)
            #logger.error("CONNECTION FAILED 2 IN OPC_WRITE....." + str(ce))
            pass
    try:
        val = client.get_node("ns=2;s=" + trigger_val)
        val_value=val.get_value()
        if val_value==False:
            val.set_attribute(ua.AttributeIds.Value, ua.DataValue(True))
    except Exception as e:
        print(e)
    time.sleep(4)
    try:
        val = client.get_node("ns=2;s=" + trigger_val)
        val_value=val.get_value()
        if val_value==True:
            val.set_attribute(ua.AttributeIds.Value, ua.DataValue(False))
    except Exception as e:
        print(e)
    time.sleep(2)
    try:
        i = 0
        reset = client.get_node("ns=2;s=" + reset_val)
        reset_value = reset.get_value()
        reset2 = client.get_node("ns=2;s=" + reset_val2)
        reset_value2 = reset2.get_value()
        while (i <= 13):
            print(i)
            i = i + 1
            ###for reset 1###
            if reset_value == False and check_present_time >= check_start_time and check_present_time <= check_end_time:
                reset.set_attribute(ua.AttributeIds.Value, ua.DataValue(True))
            reset_value = reset.get_value()
            print(i, reset_value)
            #time.sleep(1)
            if reset_value == True:  # and check_present_time >= check_start_time and check_present_time <= check_end_time:
                reset.set_attribute(ua.AttributeIds.Value, ua.DataValue(False))
            ######################################
            ##########reset value 2 - Scada 2##########################################
            if reset_value2 == False and check_present_time >= check_start_time and check_present_time <= check_end_time:
                reset2.set_attribute(ua.AttributeIds.Value, ua.DataValue(True))
            reset_value2 = reset2.get_value()
            print(i, reset_value2)
            time.sleep(1)
            if reset_value2 == True:  # and check_present_time >= check_start_time and check_present_time <= check_end_time:
                reset2.set_attribute(ua.AttributeIds.Value, ua.DataValue(False))
    except Exception as e:
        print(e)
    client.disconnect()
def opc_trigger_return():
    start_time = datetime.now()
    client = Client(url1)
    """Writes back to the OPC"""
    try:
        client.connect()
        #logger.info("CONNECTION ESTABLISHED IN OPC_WRITE.....")
    except Exception as ce:
        try:
            import time
            #logger.error("CONNECTION FAILED IN OPC_WRITE....." + str(ce))
            client = connection_retry(client)
        except Exception as ce:
            print(ce)
            #logger.error("CONNECTION FAILED 2 IN OPC_WRITE....." + str(ce))
            pass
    try:
        val = client.get_node("ns=2;s=" + trigger_val)
        val_value=val.get_value()
        if val_value==True:
            val.set_attribute(ua.AttributeIds.Value, ua.DataValue(False))
    except Exception as e:
        print(e)
    client.disconnect()