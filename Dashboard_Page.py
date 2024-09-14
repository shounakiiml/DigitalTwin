import socket
import datetime
import io
import socket
import time
import os
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import numpy as np
import pandas as pd
from dash import Input, Output, State
from dash import dash_table
from dash import html
from dash.exceptions import PreventUpdate

from main import define_config

#
# """ Importing press list from the configuration file"""
# with open("C:/Users/.Pal/PycharmProjects/pythonProject/config.yaml", 'r') as stream: config_loaded = yaml.safe_load(stream)
config_loaded = define_config()
mc_list = config_loaded['Trench Distribution']['Trench1'] + config_loaded['Trench Distribution'][
    'Trench2'] + \
             config_loaded['Trench Distribution']['Trench3'] + config_loaded['Trench Distribution'][
                 'Trench4'] + \
             config_loaded['Trench Distribution']['Trench5'] + config_loaded['Trench Distribution'][
                 'Trench6']
hetero_list = config_loaded['Heterogeneous MC']
mc_adj=mc_list.copy()
mc_adj2=mc_list.copy()
for j in mc_list:
    mc_adj2.remove(j)
    mc_adj2.append(j + '_L')
    mc_adj2.append(j + '_R')
for i in mc_list:
    if i in hetero_list:
        mc_adj.remove(i)
        mc_adj.append(i+'_L')
        mc_adj.append(i + '_R')

def datetime_picker():
    """ Defining Datetime Picker to Automatically fill datetime column in table1 and table3"""
    today = str((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S"))
    today = today[:13] + ':00:00'
    # today = today[:16] + ':00'
    today = pd.to_datetime(today)
    m = 165 + datetime.datetime.now().minute
    """ Creating List of 15 sec interval for the GT loading Time Columns """
    # date_list = [today + datetime.timedelta(minutes=15 * x) for x in range(0, 100)]
    date_list = [today + datetime.timedelta(minutes=m + x) for x in range(0, 600, 15)]
    datetext = [x.strftime('%Y-%m-%d %H:%M:%S') for x in date_list]
    return datetext


""" Creating headers """
app = dash.Dash(__name__, assets_url_path=config_loaded['host_folder'] + 'assets')
Trench1 = [dbc.CardHeader(html.H5('TRENCH 1', className="text-center"))]
Trench2 = [dbc.CardHeader(html.H5('TRENCH 2', className="text-center"))]
Trench3 = [dbc.CardHeader(html.H5('TRENCH 3', className="text-center"))]
Trench4 = [dbc.CardHeader(html.H5('TRENCH 4', className="text-center"))]
Trench5 = [dbc.CardHeader(html.H5('TRENCH 5', className="text-center"))]
Trench6 = [dbc.CardHeader(html.H5('TRENCH 6', className="text-center"))]
app.title = "Digital Twin View"
"""Defines the complete layout and individual tabs of the dashbord with colors and styles as described"""
app.layout = html.Div([
    html.Div(
        html.H1(
            children='MACHINE IDLING DASHBOARD',
            style={'color': 'white',
                   'fontSize': 30, 'text-align': 'center',
                   'background': '#330099'})),
    dcc.Interval('graph_update22', interval=30 * 1000),
    html.Div(id='tab1_alert'),
    html.Div([
        dcc.Tabs(id="tabs-styled-with-inline", value='tab-1', children=[
            dcc.Tab(label='Digital View (North)', value='tab-1'),
            dcc.Tab(label='Interactive Segment', value='tab-2'),
            dcc.Tab(label='Trench-wise Report', value='tab-3'),
            dcc.Tab(label='Machine Log', value='tab-4')
        ]),
        html.Div(id='tabs-content-inline')
    ], className="create_container3 four columns"),
])

"""Call back for tab 2 - Associate input"""


@app.callback(Output('tabs-content-inline', 'children'),
              Input("tabs-styled-with-inline", 'value'))
def render_content(tab):
    if tab == 'tab-2':
        print("got into Colleague's Input")
        return html.Div([
            dcc.Interval('graph-update', interval=30 * 1000),
            dcc.Interval('graph-update2', interval=30 * 1000),
            html.Hr(),
            html.H2(
                children='Idle Machine Cases',
                style={'color': 'black',
                       'fontSize': '20px',
                       'text-align': 'center',
                       'background': '#FF5100'}),
            html.Hr(),
            html.Div(id='output1'),
            html.Div(id="modal_div"),
            html.Div(id="modal_div2"),
            # html.Div(id='output3'),

            dash_table.DataTable(

                id='table1',

                columns=[
                    {'id': 'MC_no', 'name': 'MC_no', 'editable': False},
                    {'id': 'No Material Reason', 'name': '  No Material Reason ', 'presentation': 'dropdown'},
                    # {'id': 'GT Loading Time', 'name': 'GT Loading Time', 'presentation': 'dropdown'},
                    {'id': 'Submit', 'name': 'Submit', 'presentation': 'markdown', 'editable': False},

                ],
                css=[{"selector": ".Select-menu-outer",
                      "rule": 'display : block !important',
                      #"z-index": "1111 "
                      }],
                style_cell={'textAlign': 'center'},

                editable=True,
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'lineHeight': '15px',
                    # 'width': 'auto',
                    'align': 'center'
                },
                style_header={'backgroundColor': '#e1e4eb',
                              'fontWeight': 'bold',
                              'align': 'center'
                              },
                # fill_width=True,
                dropdown={
                    'No Material Reason': {
                        'options': [
                            {'label': i, 'value': i}
                            for i in ['Reason 1', 'Reason 2', 'Reason 3', 'Reason 4','Reason 5',
                                                       'Reason 6','Reason 7','Reason 8']
        ],

                    },
                },
                fixed_rows={'headers': True},
                style_data_conditional=[
                    {
                        'if': {
                            'column_id': 'Submit',
                        },

                        "width": "240px",
                        "height": "40px",
                    },

                    {
                        'if': {
                            'column_id': 'Submit',
                            # "state": "active",
                        },
                        "width": "240px",
                        "height": "40px",
                        "color": "blue",
                        "textDecoration": "underline",
                        "fontSize": "16px",
                        "opacity": "1",
                        "cursor": "pointer",
                        "padingLeft": "20px",
                        "padingRight": "20px"
                    },

                    {
                        'if': {
                            'column_id': 'Submit',
                            "state": "active",
                        },
                        "width": "240px",
                        "height": "40px",
                        "backgroundColor": "#f4511e",
                        "border": "grey",
                        "color": "white",
                        "fontSize": "16px",
                        "opacity": "1",
                        "cursor": "pointer",
                        "padingLeft": "20px",
                        "padingRight": "20px"
                    },
                ],
                filter_action='native',
                fill_width=True,
            ),
            html.Hr(),
            html.H2(
                children='Machine Off condition',
                style={'color': 'white',
                       'fontSize': '20px',
                       'text-align': 'center',
                       'background': '#FF7F00'}),

            dash_table.DataTable(
                id='table3',
                columns=[
                    {'id': 'MC_no', 'name': 'MC_no', 'editable': False},
                    {'id': 'No Material Reason', 'name': 'No Material Reason', 'presentation': 'dropdown'},
                    {'id': 'Material Loading Time', 'name': 'Material Loading Time', 'presentation': 'dropdown'},
                    {'id': 'Next Material Loading Time', 'name': 'Next Material Loading Time'},
                    {'id': 'Submit', 'name': 'Submit', 'presentation': 'markdown', 'editable': False},

                ],
                style_cell={'textAlign': 'center'},
                css=[{"selector": ".Select-menu-outer", "rule": 'display : block !important'}],

                editable=True,
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'lineHeight': '15px',
                    # 'width': 'auto',
                    'align': 'center'
                },
                style_header={'backgroundColor': '#e1e4eb',
                              'fontWeight': 'bold',
                              'align': 'center',
                              #"z-index":"999"
                              },
                # fill_width=True,
                is_focused=True,
                dropdown={
                                        'No Material Reason': {
                        'options': [
                            {'label': i, 'value': i}
                            for i in ['Shut_Input_1', 'Shut_Input_2', 'Shut_Input_3', 'Shut_Input_4','Shut_Input_5']
        ],
                    },
                    'Material Loading Time': {
                        'options': [
                            {'label': i, 'value': i}
                            for i in datetime_picker()
                        ],

                    }
                },
                fixed_rows={'headers': False},
                style_data_conditional=[
                    {
                        # "if": {"state": "selected"},
                        'if': {
                            'column_id': 'Submit',
                        },

                        "width": "240px",
                        "height": "40px",
                    },

                    {
                        'if': {
                            'column_id': 'Submit',
                            # "state": "active",
                        },
                        "width": "240px",
                        "height": "40px",
                        # "backgroundColor": "#f4511e",
                        # "border": "grey",
                        "color": "blue",
                        "textDecoration": "underline",
                        "fontSize": "16px",
                        "opacity": "1",
                        "cursor": "pointer",
                        "padingLeft": "20px",
                        "padingRight": "20px"
                    },

                    {
                        'if': {
                            'column_id': 'Submit',
                            "state": "active",
                        },
                        "width": "240px",
                        "height": "40px",
                        "backgroundColor": "#f4511e",
                        "border": "grey",
                        "color": "white",
                        "fontSize": "16px",
                        "opacity": "1",
                        "cursor": "pointer",
                        "padingLeft": "20px",
                        "padingRight": "20px"
                    },
                ],
                filter_action='native',
                fill_width=True,
                #is_focused=True
            ),
            html.Hr(),
            html.Div(
                style={'padding':120}
            )
        ])
    # ==============================================================================================================
    if tab == 'tab-1':
        return html.Div([
            dcc.Interval('graph_update1', interval=10 * 1000),
            html.Div(id='tab1_output')
        ])
    # ==============================================================================================================
    if tab == 'tab-3':
        return html.Div([
            html.H2(
                children='Trench  view',
                style={'color': 'white',
                       'fontSize': 20, 'text-align': 'center',
                       'background': '#FF7F00'}),
            html.Hr(),
            dcc.Interval('graph_update3', interval=30 * 1000),

            html.Div(className='row', children=[
                html.Div(children=[
                    html.Label(['Trench:'], style={'font-weight': 'bold', "text-align": "center"}),
                    dcc.Dropdown(
                        id='trn',
                        options=[
                            {'label': line, 'value': line} for line in ['1', '2', '3', '4', '5', '6', 'trench_all']
                        ],
                        value='trench_all',
                    )
                ], style=dict(width='30%')),
                html.Div(children=[
                    html.Label(['Shift:'], style={'font-weight': 'bold', "text-align": "center"}),
                    dcc.Dropdown(
                        id='shift_31',
                        options=[
                            {'label': line, 'value': line} for line in ['Shift_A', 'Shift_B', 'Shift_C', "Shift_all"]
                        ],
                        value='Shift_all',
                    )
                ], style=dict(width='30%')),

                html.Div(children=[
                    html.Label(['Date:'], style={'font-weight': 'bold', "text-align": "center"}),
                    dcc.Dropdown(
                        id='date_31',
                    )
                ], style=dict(width='30%'))
            ], style=dict(display='flex')),

            dash_table.DataTable(
                id='table31',
                style_cell={'textAlign': 'center'},
                editable=True,
                page_size=100,
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'lineHeight': '15px',
                    'width': '10%', 'align': 'center'
                },
                style_header={'backgroundColor': '#e1e4eb',
                              'fontWeight': 'bold',
                              'align': 'center'
                              },
                fixed_rows={'headers': True},
                fill_width=True,
                is_focused=True,
            ),

            html.Hr(),
            dcc.Download(id="download_trench"),
            html.Button("Save",
                        id="save-button"),
            html.H2(
                children='Machine Idle Hours - Summary',
                style={'color': 'white',
                       'fontSize': 20, 'text-align': 'center',
                       'background': '#FF7F00'}),
            dash_table.DataTable(
                id='table41',
                style_cell={'textAlign': 'center'},
                editable=True,
                page_size=100,
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'lineHeight': '15px',
                    'fontSize': 16,
                    'width': '15%', 'align': 'center'
                },
                style_header={'backgroundColor': '#C53E3B',
                              'fontWeight': 'bold',
                              'fontSize': 20,
                              'color': 'white',
                              'align': 'center'
                              },
                fixed_rows={'headers': True},
                fill_width=True,
                is_focused=True,
            ),
            html.Hr(),
            html.H2(
                children='Machine Steam Savings - Summary',
                style={'color': 'white',
                       'fontSize': 20, 'text-align': 'center',
                       'background': '#FF7F00'}),
            dash_table.DataTable(
                id='table42',
                style_cell={'textAlign': 'center'},
                editable=True,
                page_size=100,
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'lineHeight': '15px',
                    'fontSize': 16,
                    'width': '15%', 'align': 'center'
                },
                style_header={'backgroundColor': '#35A6C4',
                              'fontWeight': 'bold',
                              'fontSize': 20,
                              'color': 'white',
                              'align': 'center'
                              },
                fixed_rows={'headers': True},
                fill_width=True,
                is_focused=True,
            ),
            html.Hr(),

        ])
    # =============================================================================================================
    # ==============================================================================================================
    if tab == 'tab-4':
        print('n')
        return html.Div([
            dcc.Interval('graph_update45', interval=30 * 1000),
            #html.Label(['Machine:'], style={'font-weight': 'bold', "text-align": "center"}),
            dcc.Download(id="mc_log_download"),
            html.Div(className='row', children=[
                html.Div(children=[
                    html.Label(['Machine:'], style={'font-weight': 'bold', "text-align": "center"}),
                    dcc.Dropdown(
                        id='mc_id',
                        options=[
                            {'label': line, 'value': line} for line in mc_list
                        ],
                    )
                ], style=dict(width='50%'))
            ], style=dict(display='flex')),
            dbc.Button(
                "Save Machine Log", id="mc_log_save_btn", className="ms-auto", n_clicks=0
            ),
            html.H2(
                children='Machine Condition Log',
                style={'color': 'white',
                       'fontSize': 20, 'text-align': 'center',
                       'background': '#FF7F00'}),
            dash_table.DataTable(
                id='table49',
                editable=True,
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'lineHeight': '15px',
                    'width': 'auto', 'align': 'center'
                },
                style_header={'backgroundColor': '#e1e4eb',
                              'fontWeight': 'bold',
                              'align': 'center'
                              },
                fill_width=True,
                is_focused=True,
            ),
            html.Hr(),
        ])
    # ================================================================================================

###callback functions start
######September 27 change################
@app.callback(Output('tab1_alert', 'children'),
              Input("graph_update22", "n_intervals"))
def toggle_alert(nclick):
    print("hello",nclick)

    if nclick is None:
        raise dash.exceptions.PreventUpdate
    elif nclick > 0:
        try:
            #alert_table=alert_generate()
            #print("Alert Table is: \n",alert_table)
            #get_alert_insert(alert_table)
            path = config_loaded['host_folder'] + "Data/Historical Logs North"
            creation_time = os.path.getmtime(path)
            current_time = time.time()
            minutes_past = (current_time - creation_time) // (60)
            text = html.Div(className='row', children=[
                html.H2('SID Engine has stopped working. Please contact Lighthouse Team!!!',
                        style={'color': 'red', 'fontSize': '16px', 'text-align': 'center', 'fontWeight': 'bold'})
            ])
            if minutes_past>=4.0:
                feedback_Success = dbc.Alert(text,
                                             id="alert-fade",
                                             is_open=True,
                                             dismissable=True,
                                             className="alert-success",
                                             color="danger"
                                             # duration=6000
                                             ),

                return feedback_Success
                # deviceInfo = check_data.iloc[len(check_data):]
                # deviceInfo.to_csv(config_loaded['host_folder'] + '/data/current_data.csv',index=False)
            else:
                return None
                # table = dbc.Table.from_dataframe(alert_table, striped=True, bordered=True, hover=True,
                #                                  )

        except:
            return None

#######################September 27 change for steam engine stop alert############

@app.callback(Output('table41', 'data'), Output('table41', 'columns'),
               Output('table42', 'data'), Output('table42', 'columns'),
              [Input("graph_update3", "n_intervals"), Input("date_31", "value")])
def machine_view_new(n, date):
    try:
        data = pd.read_pickle(config_loaded['host_folder']+'Data/Secondary Data/idling_log.pkl')
        data['Steam Saved (mins)'] = 60 * 8 - data['Idling (mins)'] - data['Non-Idling (mins)']
    except:
        time.sleep(5)
        data = pd.read_pickle(config_loaded['host_folder'] + 'Data/Secondary Data/idling_log.pkl')
        data['Steam Saved (mins)'] = 60 * 8 - data['Idling (mins)'] - data['Non-Idling (mins)']
    try:
        data['date_shift'] = data['Date'] + data['Hour']
        data2 = data.groupby('date_shift',as_index=False).sum()
        data2['Date'] = data2['date_shift'].str[:-7]
        data2['Hour'] = data2['date_shift'].str[-7:]
        data2['Month'] = np.nan
        for i in np.arange(len(data2)):
            data2['Month'][i]=datetime.datetime.strptime(data2['Date'][i], "%Y-%m-%d").month
        df = pd.DataFrame(np.nan, index=[0], columns=['Date','A_shift', 'B_shift', 'C_shift', 'FTD', 'MTD'])
        df1 = pd.DataFrame(np.nan, index=[0], columns=['Date', 'A_shift', 'B_shift', 'C_shift', 'FTD', 'MTD'])
        df2 = pd.DataFrame(np.nan, index=[0], columns=['Date','A_shift', 'B_shift', 'C_shift', 'FTD', 'MTD'])
        df3 = pd.DataFrame(np.nan, index=[0], columns=['Date', 'A_shift', 'B_shift', 'C_shift', 'FTD', 'MTD'])
        df4 = pd.DataFrame(np.nan, index=[0], columns=['A_shift', 'B_shift', 'C_shift', 'FTD', 'MTD'])
        df5 = pd.DataFrame(np.nan, index=[0], columns=['A_shift', 'B_shift', 'C_shift', 'FTD', 'MTD'])
        if date != 'all_date':
            #print(x)
            df['Date'] = date
            df1['Date'] = date
            for i in data2.loc[data2['Date'] == date, 'Hour']:
                y=date+i
                if (i == 'Shift_A'):
                    df.loc[df['Date'] == date, 'A_shift'] = data2[data2['date_shift'] == y]['Idling (mins)'].iloc[0]
                    df1.loc[df['Date'] == date, 'A_shift'] = data2[data2['date_shift'] == y]['Steam Saved (mins)'].iloc[0]
                elif (i == 'Shift_B'):
                    df.loc[df['Date'] == date, 'B_shift'] = data2[data2['date_shift'] == y]['Idling (mins)'].iloc[0]
                    df1.loc[df['Date'] == date, 'B_shift'] = data2[data2['date_shift'] == y]['Steam Saved (mins)'].iloc[0]
                else:
                    df.loc[df['Date'] == date, 'C_shift'] = data2[data2['date_shift'] == y]['Idling (mins)'].iloc[0]
                    df1.loc[df['Date'] == date, 'C_shift'] = data2[data2['date_shift'] == y]['Steam Saved (mins)'].iloc[0]
            df2 = df2.append(df, ignore_index = True)
            df3 = df3.append(df1, ignore_index=True)
            df2 = df2.loc[df2.index.drop([0])]
            df3 = df3.loc[df3.index.drop([0])]
        else:
            df2['Date'] = date
            df3['Date'] = date
            for i in data2['Hour']:
                if (i == 'Shift_A'):
                    df2.loc[df2['Date'] == date, 'A_shift'] = data2[data2['Hour'] == i]['Idling (mins)'].sum()
                    df3.loc[df2['Date'] == date, 'A_shift'] = data2[data2['Hour'] == i]['Steam Saved (mins)'].sum()
                if (i == 'Shift_B'):
                    df2.loc[df2['Date'] == date, 'B_shift'] = data2[data2['Hour'] == i]['Idling (mins)'].sum()
                    df3.loc[df2['Date'] == date, 'B_shift'] = data2[data2['Hour'] == i]['Steam Saved (mins)'].sum()
                if (i == 'Shift_C'):
                    df2.loc[df2['Date'] == date, 'C_shift'] = data2[data2['Hour'] == i]['Idling (mins)'].sum()
                    df3.loc[df2['Date'] == date, 'C_shift'] = data2[data2['Hour'] == i]['Steam Saved (mins)'].sum()
        col_list = ['A_shift','B_shift','C_shift']
        df2['FTD'] = df2[col_list].sum(axis=1)
        df3['FTD'] = df3[col_list].sum(axis=1)
        if date != 'all_date':
            date_date = datetime.datetime.strptime(df2['Date'][1], "%Y-%m-%d").month
            for i in data2['Month']:
                if i == date_date:
                    df2['MTD'] = data2[data2['Month'] == i]['Idling (mins)'].sum()
                    df3['MTD'] = data2[data2['Month'] == i]['Steam Saved (mins)'].sum()
        else:
            date_date = datetime.datetime.now().month
            for i in data2['Month']:
                if date_date == i:
                    df2['MTD'] = data2[data2['Month'] == i]['Idling (mins)'].sum()
                    df3['MTD'] = data2[data2['Month'] == i]['Steam Saved (mins)'].sum()

            #for date in data['Date'].unique():
    except:
        print ("Issue faced in new tabs in trench-wise")
    del df2['Date'], df3['Date']
    ###########################Idling Hourse######################################
    if df2['A_shift'].notnull().any():
        df4['A_shift']="%02d:%02d" % ((df2['A_shift']//60),(df2['A_shift']%60))
    if df2['B_shift'].notnull().any():
        df4['B_shift'] = "%02d:%02d" % ((df2['B_shift'] // 60), (df2['B_shift'] % 60))
    if df2['C_shift'].notnull().any():
        df4['C_shift'] = "%02d:%02d" % ((df2['C_shift'] // 60), (df2['C_shift'] % 60))
    if df2['FTD'].notnull().any():
        df4['FTD'] = "%02d:%02d" % ((df2['FTD'] // 60), (df2['FTD'] % 60))
    if df2['MTD'].notnull().any():
        df4['MTD'] = "%02d:%02d" % ((df2['MTD'] // 60), (df2['MTD'] % 60))
    ##################################End##########################################

    #######################Steam Saved########################
    if df3['A_shift'].notnull().any():
        df5['A_shift'] = "%02d:%02d" % ((df3['A_shift'] // 60), (df3['A_shift'] % 60))
    if df3['B_shift'].notnull().any():
        df5['B_shift'] = "%02d:%02d" % ((df3['B_shift'] // 60), (df3['B_shift'] % 60))
    if df3['C_shift'].notnull().any():
        df5['C_shift'] = "%02d:%02d" % ((df3['C_shift'] // 60), (df3['C_shift'] % 60))
    if df3['FTD'].notnull().any():
        df5['FTD'] = "%02d:%02d" % ((df3['FTD'] // 60), (df3['FTD'] % 60))
    if df3['MTD'].notnull().any():
        df5['MTD'] = "%02d:%02d" % ((df3['MTD'] // 60), (df3['MTD'] % 60))
    #########################End###################
    df4_columns = [{"name": i, "id": i} for i in df4.columns]
    df5_columns = [{"name": i, "id": i} for i in df5.columns]
    return df4.to_dict('records'), df4_columns, df5.to_dict('records'), df5_columns

# call back for tab 3 steam save trenchwise download

@app.callback(Output("download_trench", "data"), Input("save-button",
                                                       "n_clicks"))
def download_as_csv(n_clicks):
    df = pd.read_pickle(config_loaded['host_folder']+'Data/Secondary Data/idling_log.pkl')
    df['Steam Saved (mins)'] = 60 * 8 - df['Idling (mins)'] - df['Non-Idling (mins)']

    if not n_clicks:
        raise PreventUpdate
    download_buffer = io.StringIO()
    df.to_csv(download_buffer, index=False)
    download_buffer.seek(0)
    today = str((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S"))
    return dict(content=download_buffer.getvalue(), filename="Idling_log_mc_" + today + "_North.csv")

@app.callback(Output("mc_log_download", "data"), Input("mc_log_save_btn","n_clicks"))
def download_mc_log(n_clicks):
    df = pd.read_pickle(config_loaded['host_folder']+'Data/Machine log/mc_data.pkl')
    ##color coding
    df.loc[df["Color"] == "#C76666", "Color"]="maroon"
    df.loc[df["Color"] == "#FF9333", "Color"] = "orange"
    df.loc[df["Color"] == "#3085B0", "Color"] = "blue"

    if not n_clicks:
        raise PreventUpdate
    download_buffer=io.StringIO()
    df.to_csv(download_buffer, index=False)
    download_buffer.seek(0)
    today=str((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S"))
    return dict(content=download_buffer.getvalue(),filename="Machine_log"+today+".csv")


@app.callback([Output('table1', 'data'),
               Output('table3', 'data')],
              Input("graph-update2", "n_intervals"))
def machine_view(n):
    mas_ui = pd.read_pickle(config_loaded['host_folder'] + 'Data/Master Datasets/master_UI_data.pkl')
    data1 = pd.read_pickle(config_loaded['host_folder'] + 'Data/Secondary Data/idling_inv_greater0.pkl')
    data3 = pd.read_pickle(config_loaded['host_folder'] + 'Data/Secondary Data/machineoff.pkl')
    try:
        for mc in data1['MC_no'].unique():
            print("getting in Associate Input table 1 loop")
            try:
                data1.loc[data1['MC_no'] == mc, 'No Material Reason'] = \
                    mas_ui.loc[mas_ui['MC_no'] == mc, 'Input1'].iloc[0]
                data1.loc[data1['MC_no'] == mc, 'Material Loading Time'] = \
                    mas_ui.loc[mas_ui['MC_no'] == mc, 'Input2'].iloc[0]
            except:
                data1.loc[data1['MC_no'] == mc, 'No Material Reason'] = np.nan
                data1.loc[data1['MC_no'] == mc, 'Material Loading Time'] = np.nan
    except:
        data1 = pd.DataFrame(
            columns=['MC_no', 'No Material Reason', 'Material Loading Time'])

    if data1.empty == True:
        data1 = pd.DataFrame(
            columns=['MC_no', 'No Material Reason', 'Material Loading Time'])
    data1 = data1[['MC_no', 'No Material Reason', 'Material Loading Time']].reset_index(drop=True)
    data1['Submit'] = 'Submit'

    try:
        for mc in data3['MC_no'].unique():  ###changed from data1 to data3 to check - User
            try:
                data3.loc[data3['MC_no'] == mc, 'No Material Reason'] = \
                    mas_ui.loc[mas_ui['MC_no'] == mc, 'Input1'].iloc[0]
                data3.loc[data3['MC_no'] == mc, 'Next Material Loading Time'] = \
                    mas_ui.loc[mas_ui['MC_no'] == mc, 'Input2'].iloc[0]
                data3.loc[data3['MC_no'] == mc, 'Material Loading Time'] = \
                    mas_ui.loc[mas_ui['MC_no'] == mc, 'Input2'].iloc[0]
            except:
                data3.loc[data3['MC_no'] == mc, 'No Material Reason'] = np.nan
                data3.loc[data3['MC_no'] == mc, 'Next Material Loading Time'] = np.nan
                data3.loc[data3['MC_no'] == mc, 'Material Loading Time'] = np.nan
    except:
        data3 = pd.DataFrame(
            columns=['MC_no', 'No Material Reason', 'Material Loading Time', 'Next Material Loading Time'])
    if data3.empty == True:
        data3 = pd.DataFrame(
            columns=['MC_no', 'No Material Reason', 'Material Loading Time', 'Next Material Loading Time'])

    data3 = data3[['MC_no', 'No Material Reason', 'Material Loading Time', 'Next Material Loading Time']].reset_index(drop=True)
    data3['Submit'] = 'Submit'

    return data1.to_dict('records'), data3.to_dict('records')
    #return data3.to_dict('records')

    # ===================================================================================================================
    # call back for tab 2 Associate input, submit button acknowledge
def associate_cond(x,y):
    y = pd.to_datetime(y, format='%Y-%m-%d %H:%M:%S')
    if x == 'Reason 1':
        return str(y+pd.to_timedelta(5, unit='m'))
    elif x == 'Reason 2':
        return str(y+pd.to_timedelta(10, unit='m'))
    elif x == 'Reason 3':
        return str(y+pd.to_timedelta(84, unit='m'))
    elif x == 'Reason 4':
        return str(y+pd.to_timedelta(35, unit='m'))
    elif x == 'Reason 5':
        return str(y+pd.to_timedelta(15, unit='m'))
    elif x == 'Reason 6':
        return str(y+pd.to_timedelta(84, unit='m'))
    elif x == 'Reason 7':
        return str(y+pd.to_timedelta(65, unit='m'))
    elif x == 'Reason 8':
        return str(y+pd.to_timedelta(5, unit='m'))

def associate_cond1(x,y):
    y = pd.to_datetime(y, format='%Y-%m-%d %H:%M:%S')
    if x == 'Shut_Input_1':
        return str(y+pd.to_timedelta(30, unit='m'))
    elif x == 'Shut_Input_2':
        return str(y+pd.to_timedelta(35, unit='m'))
    elif x == 'Shut_Input_3':
        return str(y+pd.to_timedelta(109, unit='m'))
    elif x == 'Shut_Input_4':
        return str(y+pd.to_timedelta(60, unit='m'))
    elif x == 'Shut_Input_5':
        return str(y+pd.to_timedelta(129, unit='m'))

@app.callback(Output("modal_div", "children"),
              Input("table1", "active_cell"), State("table1", "derived_viewport_data"))
def cell_clicked(cell, data):
    if cell is None:
        raise PreventUpdate
    mas_ui = pd.read_pickle(config_loaded['host_folder'] + '/Data/Master Datasets/master_UI_data.pkl')
    mas_ui_temp = pd.read_pickle(config_loaded['host_folder'] + '/Data/Master Datasets/master_UI_data_1.pkl')
    mas_ui_temp['Input4'] = mas_ui_temp['Input4'].replace(np.nan, '0')
    # mas_ui_temp['Input4'] = mas_ui_temp['Input4'].replace('nan', '0')
    colortemp = pd.read_pickle(
        config_loaded['host_folder'] + '/Data/Secondary Data/mc_alarms_colour.pkl')
    #### to update the mas_ui_temp file when machine is added####
    if len(mas_ui)>len(mas_ui_temp):
        df_result = mas_ui.copy()
        df_result['Input4'] = 'nan'
        mas_ui_temp = pd.concat([mas_ui_temp, df_result]).drop_duplicates(subset='MC_no')
    mas_ui_temp['Input4'] = mas_ui_temp['Input4'].replace('nan', '0')
    #### to end of update the mas_ui_temp file##############
    curr_time = pd.to_datetime((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S"), format="%Y-%m-%d %H:%M:%S")
    print(cell)

    if cell:
        selected = data[cell["row"]][cell["column_id"]]
        #print(selected,cell["row"],cell["column_id"])
        if selected == 'Submit':
            print(".........", [data[cell["row"]]])
            # x=pd.DataFrame([data[cell["row"]]])
            # x.to_csv(config_loaded['host_folder'] + '/Data/Master Datasets/cell_Value.csv', index=False)
            data_temp = pd.DataFrame([data[cell["row"]]])
            input=mas_ui.loc[mas_ui['MC_no'] == data_temp.iloc[0, 0], 'Input1'].iloc[0]
            # print("data_temp", data_temp)
            # print("data_temp['Reason for no GT'] ...", data_temp['Reason for no GT'])
            if data_temp.iloc[0, 1] is None:  # or data_temp.iloc[0, 2] is None:

                return [
                    # dbc.Button("Open modal", id="open", n_clicks=0),
                    dbc.Modal(
                        [
                            dbc.ModalHeader(dbc.ModalTitle("Error"), close_button=False),
                            dbc.ModalBody("Please fill in the values before submitting"),
                            dbc.ModalFooter(
                                dbc.Button(
                                    "Close", id="close", className="ms-auto", n_clicks=0,
                                    style={'width': '80px', 'height': '40px', 'fontSize': '15px '}
                                )
                            ),
                        ],
                        id="modal",
                        is_open=True,
                        centered=True,
                        backdrop="static",
                    )
                ]
            elif (str(mas_ui_temp.loc[mas_ui_temp['MC_no'] == data_temp.iloc[0, 0], 'Input4'].iloc[0]) >= str(
                    curr_time) and str(mas_ui.loc[mas_ui['MC_no'] == data_temp.iloc[0, 0], 'Input1'].iloc[
                0])!='nan') or colortemp.loc[colortemp['MC_no'] == data_temp.iloc[0, 0], 'Color'].iloc[0] == '#3085B0':
                return [
                    # dbc.Button("Open modal", id="open", n_clicks=0),
                    dbc.Modal(
                        [
                            dbc.ModalHeader(dbc.ModalTitle("Error"), close_button=False),
                            dbc.ModalBody("Data already Entered"),
                            dbc.ModalFooter(
                                dbc.Button(
                                    "Close", id="close", className="ms-auto", n_clicks=0,
                                    style={'width': '80px', 'height': '40px', 'fontSize': '15px '}
                                )
                            ),
                        ],
                        id="modal",
                        is_open=True,
                        centered=True,
                        backdrop="static",
                    )
                ]
            #elif colortemp.loc[colortemp['MC_no'] == data_temp.iloc[0, 0], 'Color'].iloc[0] == '#3085B0':

            else:
                data_temp['Time_of_opin'] = str(
                    pd.to_datetime(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), format='%d-%m-%Y %H:%M:%S'))
                # print("data_temp", data_temp)
                mas_ui.loc[mas_ui['MC_no'] == data_temp['MC_no'].iloc[0], 'Input1'] = data_temp.iloc[0, 1]
                # mas_ui.loc[mas_ui['MC_no'] == data_temp['MC_no'].iloc[0], 'Input2'] = data_temp.iloc[0, 2]
                mas_ui.loc[mas_ui['MC_no'] == data_temp['MC_no'].iloc[0], 'Input2'] = associate_cond1(
                    data_temp.iloc[0, 1], data_temp.iloc[0, 4])
                mas_ui.loc[mas_ui['MC_no'] == data_temp['MC_no'].iloc[0], 'Input3'] = data_temp.iloc[0, 4]

                mas_ui_temp.loc[mas_ui_temp['MC_no'] == data_temp['MC_no'].iloc[0], 'Input1'] = data_temp.iloc[
                    0, 1]
                mas_ui_temp.loc[mas_ui_temp['MC_no'] == data_temp['MC_no'].iloc[0], 'Input2'] = associate_cond1(
                    data_temp.iloc[0, 1], data_temp.iloc[0, 4])
                mas_ui_temp.loc[mas_ui_temp['MC_no'] == data_temp['MC_no'].iloc[0], 'Input3'] = data_temp.iloc[
                    0, 4]
                mas_ui_temp.loc[mas_ui_temp['MC_no'] == data_temp['MC_no'].iloc[0], 'Input4'] = associate_cond1(
                    data_temp.iloc[0, 1], data_temp.iloc[0, 4])

                # mas_ui = mas_ui.replace(np.nan, '', regex=True)
                mas_ui.to_pickle(config_loaded['host_folder'] + '/Data/Master Datasets/master_UI_data.pkl')
                mas_ui_temp.to_pickle(
                        config_loaded['host_folder'] + '/Data/Master Datasets/master_UI_data_1.pkl')
                # print(mas_ui)
                return [
                    # dbc.Button("Open modal", id="open", n_clicks=0),
                    dbc.Modal(
                        [
                            dbc.ModalHeader(dbc.ModalTitle("Success"), close_button=False),
                            dbc.ModalBody("Associate input updated"),
                            dbc.ModalFooter(
                                dbc.Button(
                                    "Close", id="close", className="ms-auto", n_clicks=0,
                                    style={'width': '80px', 'height': '40px', 'fontSize': '15px '}
                                )
                            ),
                        ],
                        id="modal",
                        is_open=True,
                        centered=True,
                        backdrop="static",
                    ),
                ]
    # ===================================================================================================================
    # call back for tab 2 Associate input, sumit acknowledgement for table 3 - steam off


@app.callback(
    Output("modal_div2", "children"),
    Input("table3", "active_cell"),
    State("table3", "derived_viewport_data"),
)
def cell_clicked2(cell, data):
    mas_ui = pd.read_pickle(config_loaded['host_folder']+'Data/Master Datasets/master_UI_data.pkl')
    #print(mas_ui)
    if cell is None:
        raise PreventUpdate
    if cell:
        selected = data[cell["row"]][cell["column_id"]]
        #print(selected)
        if selected == 'Submit':
            print([data[cell["row"]]])
            data_temp = pd.DataFrame([data[cell["row"]]])
            if data_temp.iloc[0, 1] is None or data_temp.iloc[0, 2] is None:

                return [
                    # dbc.Button("Open modal", id="open", n_clicks=0),
                    dbc.Modal(
                        [
                            dbc.ModalHeader(dbc.ModalTitle("Error"), close_button=False),
                            dbc.ModalBody("Please fill in the values before submitting"),
                            dbc.ModalFooter(
                                dbc.Button(
                                    "Close", id="close2", className="ms-auto", n_clicks=0,
                                    style={'width': '80px', 'height': '40px', 'fontSize': '15px '}
                                )
                            ),
                        ],
                        id="modal2",
                        is_open=True,
                        centered=True,
                        backdrop="static",
                    )
                ]
            else:

                data_temp['Time_of_opin'] = str(
                    pd.to_datetime(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), format='%d-%m-%Y %H:%M:%S'))
                mas_ui.loc[mas_ui['MC_no'] == data_temp['MC_no'].iloc[0], 'Input1'] = data_temp.iloc[0, 1]
                mas_ui.loc[mas_ui['MC_no'] == data_temp['MC_no'].iloc[0], 'Input2'] = data_temp.iloc[0, 2]
                mas_ui.loc[mas_ui['MC_no'] == data_temp['MC_no'].iloc[0], 'Input3'] = data_temp.iloc[0, 5]
                mas_ui.to_pickle(config_loaded['host_folder']+'Data/Master Datasets/master_UI_data.pkl')
                mas_ui.head(50)
                return [
                    # dbc.Button("Open modal", id="open", n_clicks=0),
                    dbc.Modal(
                        [
                            dbc.ModalHeader(dbc.ModalTitle("Success"),close_button=False),
                            dbc.ModalBody("Associate input updated"),
                            dbc.ModalFooter(
                                dbc.Button(
                                    "Close", id="close2", className="ms-auto", n_clicks=0,
                                    style={'width': '80px', 'height': '40px', 'fontSize': '15px '}
                                )
                            ),
                        ],
                        id="modal2",
                        is_open=True,
                        centered=True,
                        backdrop="static",
                    ),
                ]

    # ===================================================================================================================
    # call back for tab 2 Associate input table 2,4 to prevent update if no clicked

@app.callback(
    Output("modal", "is_open"),
    [Input("close", "n_clicks"),
     Input("modal", "is_open"), ]
)
def modal_close_button_clicked(n_clicks, is_open):
    print("n_clicks==================", n_clicks)
    print("is_open==================", is_open)
    if n_clicks == 0:
        raise PreventUpdate
    elif n_clicks > 0:
        return False
    else:
        dash.no_update

@app.callback(
    Output("modal2", "is_open"),
    [Input("close2", "n_clicks"),
     Input("modal2", "is_open"), ]
)
def modal2_close_button_clicked(n_clicks, is_open):
    print("n_clicks==================", n_clicks)
    print("is_open==================", is_open)
    if n_clicks == 0:
        raise PreventUpdate
    elif n_clicks > 0:
        return False
    else:
        dash.no_update


"""Call back for summary output"""


# ===================================================================================
@app.callback(Output('tab1_output', 'children'),
              Input("graph_update1", "n_intervals"))
def update_screen(n):
    data = pd.read_pickle(config_loaded['host_folder']+'Data/Secondary Data/mc_alarms_colour.pkl')
    data['Color'] = data['Color'].fillna('grey')

    for mc in data['MC_no'].unique():
        """ creating a temporary variable as an identifier to retrieve Machine colors dynamically
        this will be used to dynamically allocate card colors"""
        # temp_var = 'color_' + mc
        temp_var = 'color_N' + mc[2:]
        #temp_var = temp_var.replace('.', '_')
        globals()[temp_var] = data[data['MC_no'] == mc]['Color'].iloc[0]

    # allocating color according to the len of the data

    green_sum = len(data[data['Color'] == 'green'])
    yellow_sum = len(data[data['Color'] == 'yellow'])
    red_sum = len(data[data['Color'] == 'red'])
    black_sum = len(data[data['Color'] == '#C76666']) ##C76666 - maroon
    grey_sum = len(data[data['Color'] == 'grey'])
    tostop_sum = len(data[data['Color'] == '#3085B0']) ##3085B0 - Blue
    orange_sum = len(data[data['Color'] == '#FF9333']) ##FF9333' - orange

    ct = str(pd.to_datetime(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), format='%d-%m-%Y %H:%M:%S'))
    ###this is because SCC-51 to SCC-60 is not available
    for mc in np.arange(51, 61):
        temp_var = 'color_N' + str(mc)
        #temp_var = temp_var.replace('.','_')
        # print(temp_var)
        globals()[temp_var] = 'grey'
    ###this is because anything beyond SCC-65 is not available
    for mc in np.arange(86, 121):
        dir = ['L','R']
        for j in dir:
            temp_var = 'color_N' + str(mc)+'_'+j
            # print(temp_var)
            globals()[temp_var] = 'grey'


    def parse_time(q):
        return datetime.datetime.strptime(q, '%I:%M %p')

    A = parse_time('7:00 AM')
    B = parse_time('3:00 PM')
    C = parse_time('11:00 PM')

    now = datetime.datetime.now()
    current_time = now.strftime("%I:%M %p")
    checked_time = parse_time(current_time)

    if (A <= checked_time < B):
        s = 'Shift A'

    if (B <= checked_time < C):
        s = 'Shift B'

    if (checked_time < A) & (checked_time >= parse_time('12:00 AM')):
        s = 'Shift C'

    if (checked_time >= parse_time('11:00 PM')) & (checked_time <= parse_time('11:59 PM')):
        s = 'Shift C'
        A += datetime.timedelta(days=1)


    for i in np.arange(1, 10):
        a = ''.join(['card_00', str(i)])
        b = ''.join(['MC', str(i)])
        globals()[a] = [dbc.CardHeader(b, style={'color': 'black', 'fontSize': '16px', 'text-align': 'center',
                                                 'fontWeight': 'bold', 'padding': '5px'})]

    for i in np.arange(10, 51):  ####till 99 if machines get added change this portion-1
        a = ''.join(['card_0', str(i)])
        b = ''.join(['MC', str(i)])
        globals()[a] = [dbc.CardHeader(b, style={'color': 'black', 'fontSize': '16px', 'text-align': 'center',
                                                 'fontWeight': 'bold', 'padding': '5px'})]
    for i in np.arange(61, 86):  ####till 99 if machines get added change this portion-1
        dir = ['L','R']
        for j in dir:
            a = ''.join(['card_0', str(i), j])
            b = ''.join(['MC', str(i), '.', j])
            globals()[a] = [dbc.CardHeader(b, style={'color': 'black', 'fontSize': '12px', 'text-align': 'center',
                                                     'fontWeight': 'bold', 'padding': '0%','padding-bottom': '9px',
                                                     'padding-top': '9px', 'word-break':'break-all'})]


    for i in np.arange(51, 61):  ####till 99 if machines get added change this portion-2
        a = ''.join(['card_0', str(i)])
        # b = ''.join(['PCP', str(i)])
        b = ''.join("-")
        globals()[a] = [dbc.CardHeader(b, style={'color': 'black', 'fontSize': '16px', 'text-align': 'center',
                                                 'fontWeight': 'bold', 'padding': '5px'})]

    for i in np.arange(86, 100):  ####till 99 if machines get added change this portion-2
        dir = ['L','R']
        for j in dir:
            a = ''.join(['card_0', str(i),j])
            b = ''.join("-")
            globals()[a] = [dbc.CardHeader(b, style={'color': 'black', 'fontSize': '12px', 'text-align': 'center',
                                                     'fontWeight': 'bold', 'padding': '0%','padding-bottom': '9px',
                                                     'padding-top': '9px', 'word-break':'break-all'})]

    for i in np.arange(100, 121):
        dir = ['L','R']
        for j in dir:
            a = ''.join(['card_', str(i),j])
            b = ''.join("-")
            globals()[a] = [dbc.CardHeader(b, style={'color': 'black', 'fontSize': '12px', 'text-align': 'center',
                                                     'fontWeight': 'bold', 'padding': '0%','padding-bottom': '9px',
                                                     'padding-top': '9px', 'word-break':'break-all'})]


    Navbar = dbc.Navbar(id='navbar', children=
    [html.Div(children=[dbc.Row([
        dbc.Col([
            dbc.NavbarBrand("LEGEND :", style={'color': 'black', 'fontSize': '20px', 'fontFamily': 'Arial'}),
            dbc.Button("Machine switched off",
                       style={'background-color': '#C76666', 'color': 'black', 'font-weight': 'bold',
                              'border-color': 'rgba(0, 0, 0, 0)', 'margin-bottom': '20px', 'margin-right': '5px'}),
            dbc.NavbarBrand(":", style={'color': 'black', 'fontSize': '0px', 'fontFamily': 'Arial'}),
            dbc.NavbarBrand(black_sum,
                            style={'color': 'black', 'fontSize': '20px', 'fontFamily': 'Arial', 'margin-right': '5px'}),
            dbc.Button("Warning", style={'background-color': 'yellow', 'color': 'black', 'font-weight': 'bold',
                                         'border-color': 'rgba(0, 0, 0, 0)', 'margin-bottom': '20px',
                                         'margin-right': '5px'}),
            dbc.NavbarBrand(":", style={'color': 'black', 'fontSize': '0px', 'fontFamily': 'Arial'}),
            dbc.NavbarBrand(yellow_sum,
                            style={'color': 'black', 'fontSize': '20px', 'fontFamily': 'Arial', 'margin-right': '5px'}),
            dbc.Button("Critical Warning!", style={'background-color': 'red', 'color': 'black', 'font-weight': 'bold',
                                                   'border-color': 'rgba(0, 0, 0, 0)', 'margin-bottom': '20px',
                                                   'margin-right': '5px'}),
            dbc.NavbarBrand(":", style={'color': 'black', 'fontSize': '0px', 'fontFamily': 'Arial'}),
            dbc.NavbarBrand(red_sum,
                            style={'color': 'black', 'fontSize': '20px', 'fontFamily': 'Arial', 'margin-right': '5px'}),
            dbc.Button("Running", style={'background-color': 'green', 'color': 'black', 'font-weight': 'bold',
                                         'border-color': 'rgba(0, 0, 0, 0)', 'margin-bottom': '20px',
                                         'margin-right': '5px'}),
            dbc.NavbarBrand(":", style={'color': 'black', 'fontSize': '0px', 'fontFamily': 'Arial'}),
            dbc.NavbarBrand(green_sum,
                            style={'color': 'black', 'fontSize': '20px', 'fontFamily': 'Arial', 'margin-right': '5px'}),

            dbc.Button("Machine off started",
                       style={'background-color': '#3085B0', 'color': 'black', 'font-weight': 'bold',
                              'border-color': 'rgba(0, 0, 0, 0)', 'margin-bottom': '20px', 'margin-right': '5px'}),
            dbc.NavbarBrand(":", style={'color': 'black', 'fontSize': '0px', 'fontFamily': 'Arial'}),
            dbc.NavbarBrand(tostop_sum,
                            style={'color': 'black', 'fontSize': '20px', 'fontFamily': 'Arial', 'margin-right': '5px'}),
            dbc.Button("Machine started", style={'background-color': '#FF9333', 'color': 'black', 'font-weight': 'bold',
                                               'border-color': 'rgba(0, 0, 0, 0)', 'margin-bottom': '20px',
                                               'margin-right': '5px'}),
            dbc.NavbarBrand(":", style={'color': 'black', 'fontSize': '0px', 'fontFamily': 'Arial'}),
            dbc.NavbarBrand(orange_sum,
                            style={'color': 'black', 'fontSize': '20px', 'fontFamily': 'Arial', 'margin-right': '5px'}),
            dbc.Button("Not Connected", style={'background-color': 'grey', 'color': 'black', 'font-weight': 'bold',
                                               'border-color': 'rgba(0, 0, 0, 0)', 'margin-bottom': '20px',
                                               'margin-right': '5px'}),
            dbc.NavbarBrand(":", style={'color': 'black', 'fontSize': '0px', 'fontFamily': 'Arial'}),
            dbc.NavbarBrand(grey_sum,
                            style={'color': 'black', 'fontSize': '20px', 'fontFamily': 'Arial', 'margin-right': '5px'}),

            dbc.NavbarBrand("TIME :",
                            style={'color': 'black', 'fontSize': '20px', 'fontFamily': 'Arial', 'margin-right': '5px'}),
            dbc.NavbarBrand(ct,
                            style={'color': 'black', 'fontSize': '15px', 'fontFamily': 'Arial', 'margin-right': '5px'}),
            dbc.NavbarBrand(s,
                            style={'color': 'black', 'fontSize': '15px', 'fontFamily': 'Arial', 'margin-right': '5px'}),

        ])])], className='mx-2')

    ])
    return_block = html.Div(children=[
        Navbar,
        html.Div(children=[
            dbc.Container([
                dbc.Row([
                    dbc.Col(dbc.Card(Trench1, color='dark', inverse=True, className="border border-1",
                                     ), width=2,
                            style={'color': 'white', 'background-color':'#35383A','text-align': 'center',
                                   'width': '15%', 'float': 'left'}),
                    dbc.Col(dbc.Card(Trench2, color='dark', inverse=True, className="border border-1",
                                     ), width=2,
                            style={'color': 'white', 'text-align': 'center', 'background-color':'#35383A',
                                   'width': '15%', 'float': 'left','margin-left':'1%'}),
                    dbc.Col(dbc.Card(Trench3, color='dark', inverse=True, className="border border-1",
                                     ), width=2,
                            style={'color': 'white', 'color': 'white','text-align': 'center', 'background-color':'#35383A',
                                   'width': '15%','float': 'left','margin-left':'1%'}),
                    dbc.Col(dbc.Card(Trench4, color='dark', inverse=True, className="border border-1",
                                     ), width=2,
                            style={'color': 'white', 'text-align': 'center','background-color':'#35383A',
                                   'width': '15.5%', 'float': 'left','margin-left':'1%'}),
                    dbc.Col(dbc.Card(Trench5, color='dark', inverse=True, className="border border-1",
                                     ), width=2,
                            style={'color': 'white', 'text-align': 'center','background-color':'#35383A',
                                   'width': '15.5%', 'float': 'left','margin-left':'1%'}),
                    dbc.Col(dbc.Card(Trench6, color='dark', inverse=True, className="border border-1",
                                     ), width=2,
                            style={'color': 'white', 'text-align': 'center','background-color':'#35383A',
                                   'width': '15.5%', 'float': 'left','margin-left':'1%'})
                ]),

                ################Row1######################
                dbc.Row([
                    dbc.Col(dbc.Card(card_001, color=color_N1, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','padding': '0%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_020, color=color_N20, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_021, color=color_N21, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_040, color=color_N40, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_041, color=color_N41, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_060, color=color_N60, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_120L, color=color_N120_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.4%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_120R, color=color_N120_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_061L, color=color_N61_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_061R, color=color_N61_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_075L, color=color_N75_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.4%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_075R, color=color_N75_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_076L, color=color_N76_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_076R, color=color_N76_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_095L, color=color_N95_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.4%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_095R, color=color_N95_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_096L, color=color_N96_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_096R, color=color_N96_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'})
                ]),
                ################Row2######################
                dbc.Row([

                    dbc.Col(dbc.Card(card_002, color=color_N2, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','padding': '0%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_019, color=color_N19, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_022, color=color_N22, inverse=True), width=1,
                            style={'text-align': 'center','width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_039, color=color_N39, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_042, color=color_N42, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_059, color=color_N59, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_119L, color=color_N119_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.4%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_119R, color=color_N119_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_062L, color=color_N62_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_062R, color=color_N62_R, inverse=True), width=1,
                            style={'text-align': 'center','width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_074L, color=color_N74_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.4%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_074R, color=color_N74_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_077L, color=color_N77_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_077R, color=color_N77_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_094L, color=color_N94_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.4%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_094R, color=color_N94_R, inverse=True), width=1,
                            style={'text-align': 'center','width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_097L, color=color_N97_L, inverse=True), width=1,
                            style={'text-align': 'center','width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_097R, color=color_N97_R, inverse=True), width=1,
                            style={'text-align': 'center','width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'})
                ]),
                ################Row3######################
                dbc.Row([
                    dbc.Col(dbc.Card(card_003, color=color_N3, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','padding': '0%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_018, color=color_N18, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_023, color=color_N23, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_038, color=color_N38, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_043, color=color_N43, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_058, color=color_N58, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_118L, color=color_N118_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.4%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_118R, color=color_N118_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_063L, color=color_N63_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_063R, color=color_N63_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_073L, color=color_N73_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.4%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_073R, color=color_N73_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_078L, color=color_N78_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_078R, color=color_N78_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_093L, color=color_N93_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.4%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_093R, color=color_N93_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_098L, color=color_N98_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_098R, color=color_N98_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'})
                ]),
                ################Row4######################
                dbc.Row([
                    dbc.Col(dbc.Card(card_004, color=color_N4, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0%','padding': '0%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_017, color=color_N17, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_024, color=color_N24, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_037, color=color_N37, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_044, color=color_N44, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_057, color=color_N57, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_117L, color=color_N117_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.4%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_117R, color=color_N117_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_064L, color=color_N64_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_064R, color=color_N64_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_072L, color=color_N72_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.4%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_072R, color=color_N72_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_079L, color=color_N79_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_079R, color=color_N79_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_092L, color=color_N92_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.4%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_092R, color=color_N92_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_099L, color=color_N92_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_099R, color=color_N99_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'})
                ]),
                ################Row5######################
                dbc.Row([
                    dbc.Col(dbc.Card(card_005, color=color_N5, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0%','padding': '0%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_016, color=color_N16, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_025, color=color_N25, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_036, color=color_N36, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_045, color=color_N45, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_056, color=color_N56, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_116L, color=color_N116_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.4%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_116R, color=color_N116_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_065L, color=color_N65_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_065R, color=color_N65_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_071L, color=color_N71_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.4%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_071R, color=color_N71_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_080L, color=color_N80_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_080R, color=color_N80_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_091L, color=color_N91_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.4%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_091R, color=color_N91_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_100L, color=color_N100_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_100R, color=color_N100_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'})
                ]),
                ################Row6######################
                dbc.Row([
                    dbc.Col(dbc.Card(card_006, color=color_N6, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0%','padding': '0%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_015, color=color_N15, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_026, color=color_N26, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_035, color=color_N35, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_046, color=color_N46, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_055, color=color_N55, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_115L, color=color_N115_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.4%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_115R, color=color_N115_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_106L, color=color_N106_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_106R, color=color_N106_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_070L, color=color_N70_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.4%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_070R, color=color_N70_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_081L, color=color_N81_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_081R, color=color_N81_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_090L, color=color_N90_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.4%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_090R, color=color_N90_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_101L, color=color_N101_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_101R, color=color_N101_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'})
                ]),
                ################Row7######################
                dbc.Row([
                    dbc.Col(dbc.Card(card_007, color=color_N7, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0%','padding': '0%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_014, color=color_N14, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_027, color=color_N27, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_034, color=color_N34, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_047, color=color_N47, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_054, color=color_N54, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_112L, color=color_N112_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.4%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_112R, color=color_N112_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_107L, color=color_N107_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_107R, color=color_N107_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_069L, color=color_N69_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.4%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_069R, color=color_N69_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_082L, color=color_N94_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_082R, color=color_N82_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_089L, color=color_N89_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.4%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_089R, color=color_N89_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_102L, color=color_N102_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_102R, color=color_N102_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'})
                ]),
                ################Row8######################
                dbc.Row([
                    dbc.Col(dbc.Card(card_008, color=color_N8, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0%','padding': '0%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_013, color=color_N13, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_028, color=color_N28, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_033, color=color_N33, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_048, color=color_N48, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_053, color=color_N53, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_113L, color=color_N113_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.4%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_113R, color=color_N113_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_108L, color=color_N108_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_108R, color=color_N108_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_068L, color=color_N68_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.4%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_068R, color=color_N68_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_083L, color=color_N83_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_083R, color=color_N83_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_088L, color=color_N88_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.4%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_088R, color=color_N88_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_103L, color=color_N103_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_103R, color=color_N103_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'})
                ]),
                ################Row9######################
                dbc.Row([
                    dbc.Col(dbc.Card(card_009, color=color_N9, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0%','padding': '0%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_012, color=color_N12, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_029, color=color_N29, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_032, color=color_N32, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_049, color=color_N49, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_052, color=color_N52, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_114L, color=color_N114_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.4%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_114R, color=color_N114_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_109L, color=color_N109_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_109R, color=color_N109_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_067L, color=color_N67_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.4%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_067R, color=color_N67_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_084L, color=color_N84_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_084R, color=color_N84_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_087L, color=color_N87_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.4%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_087R, color=color_N87_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_104L, color=color_N104_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_104R, color=color_N104_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'})
                ]),
                ################Row10######################
                dbc.Row([
                    dbc.Col(dbc.Card(card_010, color=color_N10, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0%','padding': '0%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_011, color=color_N11, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_030, color=color_N30, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_031, color=color_N31, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_050, color=color_N50, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_051, color=color_N51, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '7%', 'float': 'left','margin-left': '0.5%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_110L, color=color_N110_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.4%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_110R, color=color_N110_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_111L, color=color_N111_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_111R, color=color_N111_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_066L, color=color_N66_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.4%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_066R, color=color_N66_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_085L, color=color_N85_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_085R, color=color_N85_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_086L, color=color_N86_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.4%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_086R, color=color_N86_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_105L, color=color_N105_L, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'}),
                    dbc.Col(dbc.Card(card_105R, color=color_N105_R, inverse=True), width=1,
                            style={'text-align': 'center', 'width': '3.5%', 'float': 'left','margin-left': '0.05%','padding': '0%','padding-left': '0.5%','padding-top': '5px'})

                ])
            ], fluid=True)
        ], className="hstack gap-3")
    ], style={"margin-left": "0rem", "margin-right": "0rem", "padding": "0rem 1rem"})

    return return_block

###################################################################z
# ==========================================================================
# call back to populate date in table 3 trench filter
@app.callback(Output('date_31', 'options'),
              Input('graph_update3', 'n_intervals'))
def update_options(n_intervals, dir4):
    try:
        data = pd.read_pickle(config_loaded['host_folder']+'Data/Secondary Data/idling_log.pkl')
    except:
        time.sleep(5)
        data = pd.read_pickle(config_loaded['host_folder'] + 'Data/Secondary Data/idling_log.pkl')
    data['Date'].unique()
    options = [{'label': line, 'value': line} for line in list(data['Date'].unique())]
    x ={'label': 'all_date', 'value': 'all_date'}
    options.append(x)
    return options


@app.callback(Output('table31', 'data'), Output('table31', 'columns'),
              [Input("graph_update3", "n_intervals"), Input("date_31", "value"),
               Input("trn", "value"), Input("shift_31", "value")])
def machine_view_new(n, date, trn, shift):
    print("===============")
    d1 = pd.read_pickle(config_loaded['host_folder']+'Data/Secondary Data/idling_log.pkl')
    #print("before", d1.head())
    d1['Steam Saved (mins)'] = 60 * 8 - d1['Idling (mins)'] - d1['Non-Idling (mins)']
    if (trn == 'trench_all') & (shift != 'Shift_all') & (date != 'all_date'):
        d1 = d1[(d1['Date'] == date) & (d1['Hour'] == shift)]
    elif (shift == 'Shift_all') & (trn != 'trench_all') & (date != 'all_date'):
        d1 = d1[(d1['Date'] == date) & (d1['Trench'] == trn)]
    elif (shift == 'Shift_all') & (trn == 'trench_all') & (date != 'all_date'):
        d1 = d1[(d1['Date'] == date)]
    elif (trn == 'trench_all') & (shift != 'Shift_all') & (date == 'all_date'):
        d1 = d1[(d1['Hour'] == shift)]
    elif (shift == 'Shift_all') & (trn != 'trench_all') & (date == 'all_date'):
        d1 = d1[(d1['Trench'] == trn)]
    elif (shift == 'Shift_all') & (trn == 'trench_all') & (date == 'all_date'):
        print("Entire page")
    elif (shift != 'Shift_all') & (trn != 'trench_all') & (date == 'all_date'):
        d1 = d1[(d1['Hour'] == shift) & (d1['Trench'] == trn)]
    else:
        d1 = d1[(d1['Date'] == date) & (d1['Trench'] == trn) & (d1['Hour'] == shift)]

    d1 = d1.sort_values(['Idling (mins)'], ascending=False)
    # d1 = d1[(d1['Date'] == date) & (d1['Trench'] == trn) & (d1['Hour'] == shift)]

    d1.reset_index(inplace=True, drop=True)
    dsku_columns = [{"name": i, "id": i} for i in d1.columns]

    # ============================================================================================================================
    return d1.to_dict('records'), dsku_columns


@app.callback(Output('mc_id', 'options'),Input("graph_update45", "n_intervals"))
def update_options(n):
    try:
        options = [{'label': line, 'value': line} for line in mc_adj]
        options = sorted(options, key=lambda x: x['label'])
    except:
        options = []
    #options = [{'label': line, 'value': line} for line in list(data['Date'].unique())]
    return options
####################################################################

#=====================================================
# call back to populate tab-6 press condition log table
@app.callback([Output('table49', 'data'), Output('table49', 'columns')],
              [Input("graph_update45", "n_intervals"), Input("press_id", "value")])
def machine_view_new21(n, press_id):
    esc_set = config_loaded['host_folder']+"Data/Historical Logs North/log" + "*" + ".pkl"
    import glob
    list_of_files = glob.glob(esc_set)
    list_of_files.sort()
    df = []
    for file in list_of_files[-100:]:
        try:
            df.append(pd.read_pickle(file))
            mc_data_fin = pd.concat(df, ignore_index=True)
        except:
            time.sleep(5)
            df.append(pd.read_pickle(file))
            mc_data_fin = pd.concat(df, ignore_index=True)

    #changing color codes to color names
    mc_data_fin.loc[mc_data_fin["Color"]=="#C76666", "Color"] = "maroon"
    mc_data_fin.loc[mc_data_fin["Color"] =="#FF9333", "Color"] = "orange"
    mc_data_fin.loc[mc_data_fin["Color"] == "#3085B0", "Color"] = "blue"

    dsku = mc_data_fin[mc_data_fin['MC_no'] == mc_id]
    dsku = dsku.sort_values('Time_log', ascending=False)
    dsku['MC_TEMPERATURE'] = dsku['MC_TEMPERATURE'].apply(lambda x: round(x, 2))
    # dsku_columns = [{"name": i, "id": i} for i in list(press_data_fin.columns)]
    dsku_columns = [{'name': 'MC_no', 'id': 'MC_no'}, {'name': 'Time', 'id': 'Time'},
                    {'name': 'Color', 'id': 'Color'},
                    {'name': 'Idle_Alarm', 'id': 'Idle_Alarm'},
                    {'name': 'MC_TEMPERATURE', 'id': 'PLATEN_TEMPERATURE'},
                    {'name': 'STEP_NUMBER_RHS', 'id': 'STEP_NUMBER_RHS'},
                    {'name': 'STEP_NUMBER_LHS', 'id': 'STEP_NUMBER_LHS'},
                    {'name': 'PROD_TYPE_RHS', 'id': 'PROD_TYPE_RHS'},
                    {'name': 'PROD_TYPE_LHS', 'id': 'PROD_TYPE_LHS'},
                    {'name': 'Time_to_cut_off', 'id': 'Time_to_cut_off'},
                    {'name': 'Reason', 'id': 'Input1'},
                    {'name': 'Expected Start Time', 'id': 'Input2'}, {'name': 'Reason Entered Time', 'id': 'Input3'},
                    {'name': 'Time_log', 'id': 'Time_log'}]
    # ============================================================================================================================
    return dsku.to_dict('records'), dsku_columns


# setting the port

host = socket.gethostbyname(socket.gethostname())
host = '127.0.0.1'
if __name__ == '__main__':
    app.run_server(debug=False, host=host, port=8050)
    #app.run_server(debug=False)
# app.run_server(debug=True, host=host, port=9898)