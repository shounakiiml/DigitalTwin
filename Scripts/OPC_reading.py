import pandas as pd
import numpy as np
from datetime import datetime
import time
from opcua import Client, ua
import copy
import os
import subprocess
import re
import socket, sys
#import logging
#from logging.config import fileConfig
from opcua.ua.uaerrors import BadNodeIdUnknown
import multiprocessing
from multiprocessing import Pool, Manager
import os


from main import define_config
config_loaded = define_config()
#fileConfig(config_loaded['host_folder']+'Configuration/logging_config.ini')

#logger = logging.getLogger()

# with open("Configuration/config.yaml", 'r') as stream:
#     config_loaded = yaml.safe_load(stream)
# url1 = config_loaded['OPC Tags']['url1']
# url2 = config_loaded['OPC Tags']['url2']
# client_local1 = Client(url1)
# client_local2 = Client(url2)

# error handling function to prevention connection time out
# def connection_retry(client, retry_count=1):
#     '''
#     :param client: client object
#     :param retry_count: value can be set in config file and invoked
#     :return: returns client upon successful get root node value
#     '''
#     counter = 0
#     while 1:
#         counter += counter
#         #logger.warning("CONNECTION FAILED...RETRYING ATTEMPT..." + str(counter))
#         client_root_obj = None
#         try:
#             client_root_obj = client.get_root_node()
#         except:
#             pass
#         if client_root_obj is None:
#             time.sleep(1)
#             continue
#         else:
#             return client

# def opc_read(url1, press_list, hetero_list, platten_temp_opc_tag, platten_temp_opc_tag_rhs, platten_temp_opc_tag_lhs, tyre_size_opc_tag_rhs, tyre_size_opc_tag_lhs, step_no_opc_tag_rhs,
#              step_no_opc_tag_lhs, idle_alarm_opc_tag, idle_alarm_opc_tag_rhs, idle_alarm_opc_tag_lhs):
def opc_read():
    '''
    Reads from OPC and returns a consolidated dataset with all selected presses
    :param press_list: Press list from config file
    :param platten_temp_opc_tag: temperature tag from config file
    :param tyre_size_opc_tag: sku tag from config time
    :param step_no_opc_tag: step number from config file
    :return:
    '''
    start_time=datetime.now()
    data_final=pd.read_csv(config_loaded['host_folder']+'Data/data_final.csv')
    return data_final
#     start_time = datetime.now()  # for check the time used for reading data
#     all_press_params_df = pd.DataFrame()
#     client_local = Client(url1)
#     try:
#         #logger.info("INSIDE MAIN TRY IN OPC_READ.....")
#         client_local.connect()
#         data_fin = pd.DataFrame(
#             columns=['Press_no', 'PLATEN_TEMPERATURE',  'TYRE_SIZE_RHS',
#                      'TYRE_SIZE_LHS', 'STEP_NUMBER_RHS', 'STEP_NUMBER_LHS', 'Idle_Alarm'])
#         k = 0
#         for i in press_list:
#             if i in hetero_list:
#                 yi = i + '.' + i
#                 sku_rhs = client_local.get_node("ns=2;s=" + tyre_size_opc_tag_rhs.replace("NORTH_TRENCH.TCM75", yi))
#                 sku_lhs = client_local.get_node("ns=2;s=" + tyre_size_opc_tag_lhs.replace("NORTH_TRENCH.TCM75", yi))
#                 sno_rhs = client_local.get_node("ns=2;s=" + step_no_opc_tag_rhs.replace("NORTH_TRENCH.TCM75", yi))
#                 sno_lhs = client_local.get_node("ns=2;s=" + step_no_opc_tag_lhs.replace("NORTH_TRENCH.TCM75", yi))
#                 plt_rhs = client_local.get_node("ns=2;s=" + platten_temp_opc_tag_rhs.replace("NORTH_TRENCH.TCM75", yi))
#                 plt_lhs = client_local.get_node("ns=2;s=" + platten_temp_opc_tag_lhs.replace("NORTH_TRENCH.TCM75", yi))
#                 cutoff_rhs = client_local.get_node("ns=2;s=" + idle_alarm_opc_tag_rhs.replace("NORTH_TRENCH.TCM75", yi))
#                 cutoff_lhs = client_local.get_node("ns=2;s=" + idle_alarm_opc_tag_lhs.replace("NORTH_TRENCH.TCM75", yi))
#                 cutoff = client_local.get_node("ns=2;s=" + idle_alarm_opc_tag.replace("NORTH_TRENCH.TCM75", yi))
#                 try:
#                     segment = ['L', 'R']
#                     sku_rhs = sku_rhs.get_value()
#                     sku_lhs = sku_lhs.get_value()
#                     sno_rhs = sno_rhs.get_value()
#                     sno_lhs = sno_lhs.get_value()
#                     plt_rhs = plt_rhs.get_value()
#                     plt_lhs = plt_lhs.get_value()
#                     cutoff_rhs = cutoff_rhs.get_value()
#                     cutoff_lhs = cutoff_lhs.get_value()
#                     for j in segment:
#                         if j == "R":
#                             #print("in try loop R", i)
#                             data_fin.loc[0, 'Press_no'] = i + '_' + j
#                             data_fin.loc[0, 'PLATEN_TEMPERATURE'] = plt_rhs
#                             data_fin.loc[0, 'TYRE_SIZE_RHS'] = sku_rhs
#                             data_fin.loc[0, 'TYRE_SIZE_LHS'] = np.nan
#                             data_fin.loc[0, 'STEP_NUMBER_RHS'] = sno_rhs
#                             data_fin.loc[0, 'STEP_NUMBER_LHS'] = np.nan
#                             data_fin.loc[0, 'Idle_Alarm'] = cutoff_rhs
#
#                             # data_fin.loc[0, 'PLATEN_TEMPERATURE_RHS'] = plt_rhs
#                             # data_fin.loc[0, 'PLATEN_TEMPERATURE_LHS'] = np.nan
#                         else:
#                             #print("in try loop L", i)
#                             data_fin.loc[0, 'Press_no'] = i + '_'+ j
#                             data_fin.loc[0, 'PLATEN_TEMPERATURE'] = plt_lhs
#                             data_fin.loc[0, 'TYRE_SIZE_RHS'] = np.nan
#                             data_fin.loc[0, 'TYRE_SIZE_LHS'] = sku_lhs
#                             data_fin.loc[0, 'STEP_NUMBER_RHS'] = np.nan
#                             data_fin.loc[0, 'STEP_NUMBER_LHS'] = sno_lhs
#                             data_fin.loc[0, 'Idle_Alarm'] = cutoff_lhs
#                             # data_fin.loc[0, 'PLATEN_TEMPERATURE_RHS'] = np.nan
#                             # data_fin.loc[0, 'PLATEN_TEMPERATURE_LHS'] = plt_lhs
#                         if k == 0:
#                             data_final = data_fin.copy()
#                             k = k + 1
#                         else:
#                             data_final = pd.concat([data_final, data_fin], axis=0)
#                 except:
#                     #print('issue here-data_fin.loc=nan')
#                     segment = ['L', 'R']
#                     for j in segment:
#                         data_fin.loc[0, 'Press_no'] = i + '_'+ j
#                         data_fin.loc[0, 'PLATEN_TEMPERATURE'] = np.nan
#                         data_fin.loc[0, 'TYRE_SIZE_RHS'] = np.nan
#                         data_fin.loc[0, 'TYRE_SIZE_LHS'] = np.nan
#                         data_fin.loc[0, 'STEP_NUMBER_RHS'] = np.nan
#                         data_fin.loc[0, 'STEP_NUMBER_LHS'] = np.nan
#                         data_fin.loc[0, 'Idle_Alarm'] = np.nan
#                         # data_fin.loc[0, 'PLATEN_TEMPERATURE_RHS'] = np.nan
#                         # data_fin.loc[0, 'PLATEN_TEMPERATURE_LHS'] = np.nan
#                         if k == 0:
#                             data_final = data_fin.copy()
#                             k = k + 1
#                         else:
#                             data_final = pd.concat([data_final, data_fin], axis=0)
#             else:
#                 yi = i + '.' + i
#                 plt = client_local.get_node("ns=2;s=" + platten_temp_opc_tag.replace("NORTH_TRENCH.TCM75", yi))
#                 # plt_rhs = np.nan
#                 # plt_lhs = np.nan
#                 sku_rhs = client_local.get_node("ns=2;s=" + tyre_size_opc_tag_rhs.replace("NORTH_TRENCH.TCM75", yi))
#                 sku_lhs = client_local.get_node("ns=2;s=" + tyre_size_opc_tag_lhs.replace("NORTH_TRENCH.TCM75", yi))
#                 sno_rhs = client_local.get_node("ns=2;s=" + step_no_opc_tag_rhs.replace("NORTH_TRENCH.TCM75", yi))
#                 sno_lhs = client_local.get_node("ns=2;s=" + step_no_opc_tag_lhs.replace("NORTH_TRENCH.TCM75", yi))
#                 cutoff = client_local.get_node("ns=2;s=" + idle_alarm_opc_tag.replace("NORTH_TRENCH.TCM75", yi))
#                 try:
#                     plt = plt.get_value()
#                     # plt_rhs = plt_rhs
#                     # plt_lhs = plt_lhs
#                     sku_rhs = sku_rhs.get_value()
#                     sku_lhs = sku_lhs.get_value()
#                     sno_rhs = sno_rhs.get_value()
#                     sno_lhs = sno_lhs.get_value()
#                     cutoff = cutoff.get_value()
#                     data_fin.loc[0, 'Press_no'] = i
#                     data_fin.loc[0, 'PLATEN_TEMPERATURE'] = plt
#                     data_fin.loc[0, 'TYRE_SIZE_RHS'] = sku_rhs
#                     data_fin.loc[0, 'TYRE_SIZE_LHS'] = sku_lhs
#                     data_fin.loc[0, 'STEP_NUMBER_RHS'] = sno_rhs
#                     data_fin.loc[0, 'STEP_NUMBER_LHS'] = sno_lhs
#                     data_fin.loc[0, 'Idle_Alarm'] = cutoff
#                     # data_fin.loc[0, 'PLATEN_TEMPERATURE_RHS'] = plt_rhs
#                     # data_fin.loc[0, 'PLATEN_TEMPERATURE_LHS'] = plt_lhs
#                     if k == 0:
#                         print("issue in k==0")
#                         data_final = data_fin.copy()
#                         k = k + 1
#                     else:
#                         data_final = pd.concat([data_final, data_fin], axis=0)
#                     # if "1" in data_fin.index:
#                     #     data_fin.drop('1')
#
#                 except:
#                     #print('issue here-data_fin.loc=nan')
#                     data_fin.loc[0, 'Press_no'] = i
#                     data_fin.loc[0, 'PLATEN_TEMPERATURE'] = np.nan
#                     data_fin.loc[0, 'TYRE_SIZE_RHS'] = np.nan
#                     data_fin.loc[0, 'TYRE_SIZE_LHS'] = np.nan
#                     data_fin.loc[0, 'STEP_NUMBER_RHS'] = np.nan
#                     data_fin.loc[0, 'STEP_NUMBER_LHS'] = np.nan
#                     data_fin.loc[0, 'Idle_Alarm'] = np.nan
#                     # data_fin.loc[0, 'PLATEN_TEMPERATURE_RHS'] = np.nan
#                     # data_fin.loc[0, 'PLATEN_TEMPERATURE_LHS'] = np.nan
#                     #print("========In exception========")
#                     #print(data_fin)
#                     if k == 0:
#                         data_final = data_fin.copy()
#                         k = k + 1
#                     else:
#                         data_final = pd.concat([data_final, data_fin], axis=0)
#
#                 #print("issue in getting value",sno_rhs)
#
#
#
#     except Exception as e:
#         print(e)
#         #print('issue here-finalexpection')
#         #logger.error("GENERAL : INSIDE SUB TRY IN OPC_READ....." + str(e))
#
#         connection_retry(client_local2)
#     client_local.disconnect()
#     return data_final
#
#
# # def define_config():
# #     with open("D:/opc_connection/config.yaml", 'r') as stream:
# #         config_loaded = yaml.safe_load(stream)
# #     return config_loaded
#
# ####### 13 March 2024 ########
#
# def opc_read_in_by():
#     config = define_config()
#     machine_status = {}
#     inline_machines = []
#     bypass_machines = []
#
#     try:
#         client_local = Client(url1)
#         client_local.connect()
#         # # Get the current time
#         # current_time = datetime.now()
#         #
#         # # Check if the current time is a round hour (e.g., 18:00:00, 19:00:00, etc.)
#         # if current_time.minute == 0 and current_time.second == 0:
#         for machine in config['Machines']:
#             try:
#                 if machine in config['Heterogeneous press']:
#                     node_path_rhs = f"ns=2;s={machine}.{machine}.STEAM_IDLING_INLINE_RHS"
#                     node_rhs = client_local.get_node(node_path_rhs)
#                     value_rhs = node_rhs.get_value()
#
#                     node_path_lhs = f"ns=2;s={machine}.{machine}.STEAM_IDLING_INLINE_LHS"
#                     node_lhs = client_local.get_node(node_path_lhs)
#                     value_lhs = node_lhs.get_value()
#
#                     if value_rhs == 1:
#                         inline_machines.append(f"{machine}_RHS")
#                     else:
#                         bypass_machines.append(f"{machine}_RHS")
#
#                     if value_lhs == 1:
#                         inline_machines.append(f"{machine}_LHS")
#                     else:
#                         bypass_machines.append(f"{machine}_LHS")
#                 else:
#                     node_path = f"ns=2;s={machine}.{machine}.STEAM IDLING INLINE"
#                     node = client_local.get_node(node_path)
#                     value = node.get_value()
#                     machine_status[machine] = value
#
#                     if value == 1:
#                         inline_machines.append(machine)
#                     else:
#                         bypass_machines.append(machine)
#             except Exception as ex:
#                 print(f"Error getting values for machine {machine}: {ex}")
#         bypass_df = pd.DataFrame({'Bypass': bypass_machines})
#         # machine_status_df = pd.concat([inline_df, bypass_df], axis=1)
#         bypass_df.to_csv(config_loaded['host_folder'] + 'Data/machine_data.csv', index=False)
#
#         # if not os.path.isfile(config_loaded['host_folder'] + 'Data/machine_data.csv'):
#         #     # inline_df = pd.DataFrame({'Inline': inline_machines})
#         #
#         # else:
#         #     # inline_df = pd.DataFrame({'Inline': inline_machines})
#         #     bypass_df = pd.DataFrame({'Bypass': bypass_machines})
#         #     # machine_status_df = pd.concat([inline_df, bypass_df], axis=1)
#         #     bypass_df.to_csv(config_loaded['host_folder'] + 'Data/machine_data.csv', index=False)
#
#         return None
#
#     except Exception as e:
#         print('connection issue', e)
#     finally:
#         client_local.disconnect()

    # return machine_status, inline_machines, bypass_machines