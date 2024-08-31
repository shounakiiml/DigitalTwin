import time
import pandas as pd
import numpy as np
import gc
import warnings
import datetime
from Scripts.Extracting_log_data import log_extraction_north, log_extraction_south
from Scripts.steam_opportunity_report import generate_opp_report_north, generate_opp_report_south
from Scripts.idling_report import idle_time_report_north,idle_time_report_south
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
new_distribution_south = {}
for k, v in trench_distribution_south.items():
    '''
    re-assigns presses if trench switch is kept to 1
    '''
    for x in v:
        # a = x + '_L'
        # b = x + '_R'
        # new_distribution_south.setdefault(a, []).append(k)
        # new_distribution_south.setdefault(b, []).append(k)
        if x not in hetero_list:
            new_distribution_south.setdefault(x, []).append(k)

new_distribution_north = {}
for k, v in trench_distribution_north.items():
    '''
    re-assigns presses if trench switch is kept to 1
    '''
    for x in v:
        # a = x + '_L'
        # b = x + '_R'
        # new_distribution_north.setdefault(a, []).append(k)
        # new_distribution_north.setdefault(b, []).append(k)
        if x not in hetero_list:
            new_distribution_north.setdefault(x, []).append(k)
i = 0
for run in count(0):
    print("run=",run)
    # creating steam opportunity loss report
    try:
        idle_time_report_north(new_distribution_north)
        idle_time_report_south(new_distribution_south)
        generate_opp_report_north()
        generate_opp_report_south()
    except:
        print("Issue in genete op report")
        pass
    if run == 5 * i:
        i = i + 1
        gc.collect()