import time
import pandas as pd
import numpy as np
import gc
import warnings
import datetime
from Scripts.Extracting_log_data import log_extrac_hr_north,log_extrac_hr_south,\
    mould_classify_data,db_insert_north,db_insert_south
from Scripts.DB_data_prep import steam_total_calc,update_nanvalues,press_total_calc,data_combine
from Scripts.OPC_writing import opc_trigger, opc_trigger_return
from Scripts.OPC_reading import opc_read_in_by
import yaml
from itertools import count
from datetime import datetime,timedelta,date
from main import define_config
config_loaded = define_config()
warnings.filterwarnings("ignore")
step_no_opc_tag_rhs = config_loaded['OPC Tags']['Input Tags']['STEP_NUMBER_RHS']
step_no_opc_tag_lhs = config_loaded['OPC Tags']['Input Tags']['STEP_NUMBER_LHS']

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
new_distribution_south = {}
for k, v in trench_distribution_south.items():
    '''
    re-assigns presses if trench switch is kept to 1
    '''
    for x in v:
        if x not in hetero_list:
            new_distribution_south.setdefault(x, []).append(k)

new_distribution_north = {}
for k, v in trench_distribution_north.items():
    '''
    re-assigns presses if trench switch is kept to 1
    '''
    for x in v:
        if x not in hetero_list:
            new_distribution_north.setdefault(x, []).append(k)
i = 0
for run in count(0):
    print("run=",run)
    # creating steam opportunity loss report
    try:
        now = datetime.now()
        current_time = now.strftime("%I:%M:%S %p")
        current_date = now.strftime("%Y-%m-%d")
        hour=current_time[:2]
        ampm=current_time[-2:]
        if run==0:
            hour_old=str(int(hour)-1)
            counter=0
        if ampm=='AM':
            hour_full=hour+':00:00 AM'
        else:
            hour_full= hour+':00:00 PM'
        mytime = datetime.strptime(hour_full, '%I:%M:%S %p').time()
        mydatetime = datetime.combine(datetime.now(), mytime)
        prev_hour = mydatetime - timedelta(minutes=240)
        prev_string=prev_hour.strftime("%Y-%m-%d %I:%M:%S %p")
        max_time = mydatetime.strftime("%Y-%m-%d %I:%M:%S %p")
        max_time_str=mydatetime.strftime("%Y-%m-%d %H:%M:%S")
        mould_classify_data()
        opc_read_in_by()
        # if counter==0:
        #     opc_trigger_return()
        #     counter=1
        if not hour==hour_old:
            if run>0:
                print('triggering')
                opc_trigger()
                counter = 0
            try:
                start = time.time()
                north_data = log_extrac_hr_north(new_distribution_north, max_time)
                end = time.time()
                print(end-start)
                db_insert_north(north_data)
                print('North done')
                start = time.time()
                south_data = log_extrac_hr_south(new_distribution_south, max_time)
                end = time.time()
                print(end - start)
                db_insert_south(south_data)
                print('South done')
                steam_total_calc(prev_string)
                update_nanvalues()
                press_total_calc(prev_string)
                data_combine(prev_string)
                #data_transform(prev_string,prev_hour)
            except Exception as e:
                print("logs are not running",e)
            #time.sleep(60)

            #time.sleep(5)
        hour_old = hour



        ##########Maintaining hour

        #if current_date
    except:
        print("Issue in general op report")
        pass
    if run == 5 * i:
        i = i + 1
        gc.collect()