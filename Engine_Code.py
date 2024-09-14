import time
from time import sleep
import gc
from datetime import datetime
#from opcua import Client, ua
import pandas as pd
import numpy as np

from main import define_config
from itertools import count  # for infinite for loop

config_loaded = define_config()
from Scripts.OPC_reading import opc_read
from Scripts.Master_data_input_functions import master_ui_file, master_ui_clean, mc_overwrite_file
from Scripts.colour_allocation import colour_allocation_engine, retrieve_state,log_creation
# from Scripts.OPC_writing import OPC_write_back
# from Scripts.OPC_reading import opc_read_in_by
#fileConfig(config_loaded['host_folder']+'Configuration/logging_config.ini')
#logger = logging.getLogger()
start_time = datetime.now()

"""
Main Engine to extract data from OPC, allocate colours and write back to OPC
"""

# Reading config file parameters====================================================================
# url1 = config_loaded['OPC Tags']['url1']
# client1 = Client(url1)
# url2 = config_loaded['OPC Tags']['url2']
# client2 = Client(url2)
# retry_count = config_loaded['retry_count']

#phase = config_loaded['OPC Tags']['Input Tags']['Phase']
platten_temp_opc_tag = config_loaded['OPC Tags']['Input Tags']['MC_TEMPERATURE']
prod_type_opc_tag_rhs = config_loaded['OPC Tags']['Input Tags']['PROD_TYPE_RHS']
prod_type_opc_tag_lhs = config_loaded['OPC Tags']['Input Tags']['PROD_TYPE_RHS']
step_no_opc_tag_rhs = config_loaded['OPC Tags']['Input Tags']['STEP_NUMBER_RHS']
step_no_opc_tag_lhs = config_loaded['OPC Tags']['Input Tags']['STEP_NUMBER_LHS']
platten_temp_opc_tag_rhs = config_loaded['OPC Tags']['Input Tags']['MC_TEMPERATURE_RHS']
platten_temp_opc_tag_lhs = config_loaded['OPC Tags']['Input Tags']['MC_TEMPERATURE_LHS']
idle_alarm_opc_tag_rhs = config_loaded['OPC Tags']['Output Tags']['MACHINE_IDLING_ALARM_RHS']
idle_alarm_opc_tag_lhs = config_loaded['OPC Tags']['Output Tags']['MACHINE_IDLING_ALARM_LHS']
idle_alarm_opc_tag = config_loaded['OPC Tags']['Output Tags']['MACHINE_IDLING_ALARM']
MC_list = config_loaded['Trench Distribution']['Trench1'] + \
             config_loaded['Trench Distribution']['Trench2'] + \
             config_loaded['Trench Distribution']['Trench3'] + \
             config_loaded['Trench Distribution']['Trench4'] + \
             config_loaded['Trench Distribution']['Trench5'] + \
             config_loaded['Trench Distribution']['Trench6']
hetero_list = config_loaded['Heterogeneous MC']
trench_switch = config_loaded['Trench Switch (OPC write back)']
trench_distribution = config_loaded['Trench Distribution']
acceptable_idling = config_loaded['Associate Input']['Acceptable Time for Idling']
wait_time_yellow = config_loaded['Associate Input']['Wait Time (Normal)']
wait_time_red = config_loaded['Associate Input']['Wait Time (Critical)']
warm_up_period = config_loaded['Associate Input']['Warm Up period']
acceptable_warm_up_period = config_loaded['Associate Input']['Acceptable Warm Up period']
# opc_wrtie_back_tag = config_loaded['OPC Tags']['Output Tags']['steam_control']
opc_write_back_tag = config_loaded['OPC Tags']['Output Tags']['MACHINE_IDLING_ALARM']
thres_temp = config_loaded['Associate Input']['Threshold temperature']
i = 0
master_ui_overwrite_recreate_switch = \
    config_loaded['Master_UI_inputs_and_mc_overwrite']['Recreate_file']

# Running on a loop========================================================================
try:
    for run in count(0):
        #start_time = datetime.now()
        print("loop no.", run)
        time.sleep(1)
        data_master=opc_read()
        #saving a copy of data_master for internal check
        data_master.to_pickle(config_loaded['host_folder']+'Data/Master Datasets/data_master.pkl')
        mc_list_adj = data_master['MC_no'].to_list()
        print('data master created')

        # Master User Input Recreation=========================================================
        if master_ui_overwrite_recreate_switch == 1:
            master_ui_file(mc_list_adj)
            mc_overwrite_file(mc_list_adj)

        #########################Retrieving Associate Input for Just Online Machines######
        try:
            mas_ui = pd.read_pickle(
                config_loaded['host_folder'] + 'Data/Master Datasets/master_UI_data.pkl')
            if run == 0:
                prev_master_ui = mas_ui
                df = pd.DataFrame(columns=['MC_no', 'Input1', 'Input2', 'Input3'])
                df = df.fillna(method='bfill')
                df.to_pickle(
                    config_loaded['host_folder'] + 'Data/Secondary Data/offline_mc.pkl')

            mas_ui = retrieve_state(data_master, prev_master_ui, mas_ui)
        except Exception as e:
            print("issue in read/write and retrieve state",e)

        prev_master_ui = mas_ui
        #################################################End Associate Input for Just Online Machines###################


        # Master User Cleaning=============================================================
        try:
            master_ui_clean(mas_ui)
        except Exception as e:
            print("issue in mas_ui_clean:", e)
        if run == 0:
            data_master['Time'] = 0
            data_master['Color'] = 0
        if run > 0:
            data_master['Time'] = Time_list
            data_master['Color'] = Color_list

        # Creating Default values and allocating grey colour for MCes on which OPC is not responding=
        data_master['Time_to_cut_off'] = np.nan
        #data_master['Color'] = np.where(data_master['PLATEN_TEMPERATURE_RHS'].isna(), 'grey', 0)
        data_master['Color'] = np.where(data_master.MC_TEMPERATURE.astype(str)=='nan', 'grey', '0')
        #data_master['Color'] = np.where(data_master['STEP_NUMBER'].isna(), 'grey', 0)
        data_master['Color'] = np.where((data_master['STEP_NUMBER_RHS'].isna()) &
                                              (data_master['STEP_NUMBER_LHS'].isna()), 'grey', '0')


        try:
            data_master[(data_master['MC_TEMPERATURE'] >= thres_temp) &
                              ((data_master['STEP_NUMBER_RHS'] == 0) | (
                                  data_master['STEP_NUMBER_RHS'].isna())) &
                              ((data_master['STEP_NUMBER_LHS'] == 0) | (
                                  data_master['STEP_NUMBER_LHS'].isna()))] \
                .to_pickle(config_loaded['host_folder'] + 'Data/Secondary Data/idling_inv_greater0.pkl')
            data_master[(data_master['MC_TEMPERATURE'] < thres_temp)] \
                .to_pickle(config_loaded['host_folder'] + 'Data/Secondary Data/machineoff.pkl')
        except Exception as e:
            print("issue in creating idle and steam off",e)

        # Reading recent most saved master UI File===================================================
        try:
            mas_ui = pd.read_pickle(
                config_loaded['host_folder'] + 'Data/Master Datasets/master_UI_data.pkl')
            # Running the Colour allocation engine to allocate colour to MCes=========================
            data_master = colour_allocation_engine(data_master, mas_ui, acceptable_idling,
                                                               wait_time_yellow,
                                                               wait_time_red, warm_up_period, acceptable_warm_up_period,
                                                               thres_temp)
            print(data_master)
        except Exception as e:
            print("issue in color allocation in Digital Twin",e)
        # Reading recent MC overwrite log =============================-===========================
        MC_overwrite = pd.read_pickle(config_loaded['host_folder']+'Data/Master Datasets/MC_overwrite.pkl')
        pd.set_option('display.max_columns', None)

        # Creating a snapshot of the dashboard and saving it=========================================
        end_time = datetime.now()
        x = (end_time - start_time).seconds
        while (x<=28):
            print(start_time, end_time, x)
            end_time = datetime.now()
            x = (end_time - start_time).seconds
            time.sleep(1)

        start_time = datetime.now()
        # Writing back to the OPC ===================================================================
        #data_master['Idle_Alarm'] = ""
        #data_master_south['Idle_Alarm'] = ""
        log_creation(data_master, MC_overwrite)
        ######## 13 March 2024 ###########
        #opc_read_in_by()
        # OPC_write_back(data_master, MC_overwrite, trench_switch, trench_distribution,
        #                acceptable_warm_up_period, thres_temp)
        data_master.to_pickle(config_loaded['host_folder']+'Data/Secondary Data/mc_alarms_colour.pkl')
        # Saving the Time and Colour columns for the next run ========================================
        Time_list = data_master['Time'].tolist()
        Color_list = data_master['Color'].tolist()
        if run == 5*i:
            print("garbage collection in Steam Engine")
            i = i + 1
            gc.collect()
            # collected = gc.collect()
            # print("Garbage collector: collected",
            #       "%d objects." % collected)


        # while True:
        #     current_time = datetime.now()
        #
        #     if current_time.minute == 20 and current_time.second == 0:
        #         machine_status, inline_machines, bypass_machines = opc_read_in_by()
        #
        #         print("Machines in Inline condition:")
        #         for machine in inline_machines:
        #             print(machine)
        #
        #         print("Machines in Bypass condition:")
        #         for machine in bypass_machines:
        #             print(machine)
        #
        #         time.sleep(3600)
except Exception as e:
    #logger.exception('error in main engine connect',e)
    print('error in main engine connect',e)
    pass