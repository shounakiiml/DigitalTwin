import pandas as pd
import numpy as np
import datetime
import warnings
import math
import time
from main import define_config

config_loaded = define_config()


def master_ui_file(mc_list):
    """Recreates master user input file with all presses mentioned in the config.yaml."""
    print(mc_list)
    mas_ui = pd.DataFrame(columns=['MC_no', 'Input1', 'Input2', 'Input3'])
    mas_ui['MC_no'] = mc_list
    mas_ui.to_pickle(config_loaded['host_folder'] + 'Data/Master Datasets/master_UI_data.pkl')


def master_ui_clean(mas_ui):
    """Cleans dataset of presses which have missing associate entries thereby requesting for a rentry"""
    for press in mas_ui['MC_no'].unique():
        if pd.isnull(mas_ui.loc[mas_ui['MC_no'] == press, 'Input1']).iloc[0] | \
                pd.isnull(mas_ui.loc[mas_ui['MC_no'] == press, 'Input2']).iloc[0] | \
                pd.isnull(mas_ui.loc[mas_ui['MC_no'] == press, 'Input3']).iloc[0]:
            mas_ui.loc[mas_ui['MC_no'] == press, 'Input1'] = np.nan
            mas_ui.loc[mas_ui['MC_no'] == press, 'Input2'] = np.nan
            mas_ui.loc[mas_ui['MC_no'] == press, 'Input3'] = np.nan
    mas_ui.to_pickle(config_loaded['host_folder'] + 'Data/Master Datasets/master_UI_data.pkl')


def mc_overwrite_file(mc_list):
    """Recreates master user input file with all presses mentioned in the config.yaml."""
    press_overwrite = pd.DataFrame(columns=['MC_no', 'Current Condition', 'Change To', 'Submit',
                                            'Last Input Time', 'Last Change To'])
    press_overwrite['MC_no'] = mc_list
    press_overwrite.to_pickle(config_loaded['host_folder'] + 'Data/Master Datasets/mc_overwrite.pkl')