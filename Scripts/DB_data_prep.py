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

def steam_total_calc(prev_string):
    try:
        db = pyodbc.connect(
            'Driver={SQL Server};Server=SRVNGPPRD2SQL1;Database=AIR;Uid=LH;Pwd=Lighthouse@123;')
        db1 = pyodbc.connect(
            'Driver={SQL Server};Server=SRVNGPPRD2SQL1;Database=STEAM_AI;Uid=LH;Pwd=Lighthouse@123;')
        cursor = db.cursor()
        cursor1 = db1.cursor()
    except:
        print('No cursor connection')
    try:

        data_table = pd.read_sql_query("""SELECT *, CAST(t._VALUE AS float) as CurrentValue, 
        Lag(CAST(t._VALUE AS float), 1,0) OVER(ORDER BY _TIMESTAMP ASC) AS PrevValue, 
        (CAST(t._VALUE AS float) - (Lag(CAST(t._VALUE AS float), 1,0) OVER(ORDER BY t._TIMESTAMP ASC))) 
        as diff from  [AIR].[dbo].[TOTALIZER] t 
        where t._NAME like '%TOTAL_STEAM%' and t._TIMESTAMP >= '"""+prev_string+"""' order by t._TIMESTAMP""",
                                       con=db)
    except Exception as e:
        print(e)
    try:

        data_table1 = pd.read_sql_query("""SELECT *, CAST(t._VALUE AS float) as CurrentValue, 
        Lag(CAST(t._VALUE AS float), 1,0) OVER(ORDER BY _TIMESTAMP ASC) AS PrevValue, 
        (CAST(t._VALUE AS float) - (Lag(CAST(t._VALUE AS float), 1,0) OVER(ORDER BY t._TIMESTAMP ASC))) 
        as diff from  [AIR].[dbo].[TOTALIZER] t 
        where t._NAME like '%LP_STEAM%' and t._TIMESTAMP >= '"""+prev_string+"""' order by t._TIMESTAMP""",
                                       con=db)
    except Exception as e:
        print(e)
    try:

        data_table2 = pd.read_sql_query("""SELECT *, CAST(t._VALUE AS float) as CurrentValue, 
        Lag(CAST(t._VALUE AS float), 1,0) OVER(ORDER BY _TIMESTAMP ASC) AS PrevValue, 
        (CAST(t._VALUE AS float) - (Lag(CAST(t._VALUE AS float), 1,0) OVER(ORDER BY t._TIMESTAMP ASC))) 
        as diff from  [AIR].[dbo].[TOTALIZER] t 
        where t._NAME like '%HP_Steam%' and t._TIMESTAMP >= '"""+prev_string+"""' order by t._TIMESTAMP""",
                                       con=db)
    except Exception as e:
        print(e)
    try:
        data_table = data_table[1:len(data_table)]
        data_table1 = data_table1[1:len(data_table1)]
        data_table2 = data_table2[1:len(data_table2)]
        data_table['_TIMESTAMP'] = data_table._TIMESTAMP.dt.ceil(freq='s')
        data_table1['_TIMESTAMP'] = data_table1._TIMESTAMP.dt.ceil(freq='s')
        data_table2['_TIMESTAMP'] = data_table2._TIMESTAMP.dt.ceil(freq='s')
        data_table.loc[(data_table['diff'] < 0), 'PrevValue'] = 0
        data_table.loc[(data_table['diff'] < 0), 'diff'] = data_table.loc[(data_table['diff'] < 0), 'CurrentValue'] \
                                                           - data_table.loc[(data_table['diff'] < 0), 'PrevValue']
        data_table1.loc[(data_table1['diff'] < 0), 'PrevValue'] = 0
        data_table1.loc[(data_table1['diff'] < 0), 'diff'] = data_table1.loc[(data_table1['diff'] < 0), 'CurrentValue'] \
                                                           - data_table1.loc[(data_table1['diff'] < 0), 'PrevValue']
        data_table2.loc[(data_table2['diff'] < 0), 'PrevValue'] = 0
        data_table2.loc[(data_table2['diff'] < 0), 'diff'] = data_table2.loc[(data_table2['diff'] < 0), 'CurrentValue'] \
                                                           - data_table2.loc[(data_table2['diff'] < 0), 'PrevValue']
        #####I have to correct timestamp
        #data_table=data_table.drop(columns=['id'],axis=1)
        data_table=data_table.sort_values(by=['_TIMESTAMP'],ascending=True)
        data_table1=data_table1.rename(columns={'diff': 'LP_Steam'})
        data_table2 = data_table2.rename(columns={'diff': 'HP_Steam'})
        data_table1 = data_table1.sort_values(by=['_TIMESTAMP'], ascending=True)
        data_table2 = data_table2.sort_values(by=['_TIMESTAMP'], ascending=True)
        data_table1 = data_table1[['_TIMESTAMP','LP_Steam']]
        data_table2 = data_table2[['_TIMESTAMP', 'HP_Steam']]
        data_table = pd.merge(data_table,data_table1,how='inner',on='_TIMESTAMP')
        data_table = pd.merge(data_table, data_table2, how='inner', on='_TIMESTAMP')
    except Exception as e:
        print(e)
    try:
        try:
            print("database extracted",len(data_table))
            check=pd.DataFrame()
            if len(data_table)>0:
                maxi_date = data_table['_TIMESTAMP'][0]
                max_date = maxi_date.strftime("%Y-%m-%d %I:%M:%S %p")
                check = pd.read_sql_query("""SELECT * FROM [STEAM_AI].[dbo].[Total_Steam_Hourly] where _TIMESTAMP >=
                '""" + max_date + """'""", con=db1)
        except Exception as e:
            print("issue in selecting,", e)
        if len(check) > 0:
            for index, row in check.iterrows():
                row['id'] = str(row['id'])
                try:
                    cursor1.execute(
                        """DELETE FROM [STEAM_AI].[dbo].[Total_Steam_Hourly] where id='""" + row['id']
                        + """'""")
                except Exception as e:
                    print(e)
            db1.commit()
        for index,row in data_table.iterrows():
            row['id']=str(row['id'])
            row['_NAME']=str(row['_NAME'])
            row['_VALUE']=str(row['_VALUE'])
            print(row)
            cursor1.execute(
                "INSERT INTO [STEAM_AI].[dbo].[Total_Steam_Hourly] ([_NAME]"
                ",[_VALUE],[_TIMESTAMP],[CurrentValue],[PrevValue],[diff],[LP_Steam],[HP_Steam]) values(?,?,?,?,?,?,?,?)",
                row['_NAME'], row['_VALUE'], row['_TIMESTAMP'], row['CurrentValue'], row['PrevValue']
                , row['diff'],row['LP_Steam'],row['HP_Steam'])
            db1.commit()
            data_table.drop(index, inplace=True)
    except Exception as e:
        print("unable to edit database", e)
    cursor1.close()
    cursor.close()
    db.close()
    db1.close()

def update_nanvalues():
    try:
        db = pyodbc.connect(
            'Driver={SQL Server};Server=SRVNGPPRD2SQL1;Database=STEAM_AI;Uid=LH;Pwd=Lighthouse@123;')
        cursor = db.cursor()
    except:
        print('No cursor connection')
    try:
        cursor.execute("""UPDATE [STEAM_AI].[dbo].[STEAM_Curing] SET Idle_NoComment=0 where Idle_NoComment='nan'"""
            )
        cursor.execute("""UPDATE [STEAM_AI].[dbo].[STEAM_Curing] SET Idle_with_comment=0 where Idle_with_comment='nan'"""
            )
        db.commit()
    except Exception as e:
        print(e)
    cursor.close()
    db.close()

def press_total_calc(prev_string):
    try:
        db2 = pyodbc.connect(
            'Driver={SQL Server};Server=SRVNGPPRD2SQL1;Database=STEAM_AI;Uid=LH;Pwd=Lighthouse@123;')
        cursor1=db2.cursor()
    except:
        print('No cursor connection')
    try:
        prev_date=pd.to_datetime(prev_string)
        prev_hour=pd.to_datetime(prev_string).strftime("%I:%M:%S %p")

        def parse_time(q):
            return datetime.strptime(q, '%I:%M:%S %p')

        A = parse_time('7:00:00 AM')
        checked_time=parse_time(prev_hour)
        if (checked_time < A) & (checked_time >= parse_time('12:00:00 AM')):
            prev_date-=timedelta(days=1)
            prev_date=prev_date.strftime("%Y-%m-%d")
        else:
            prev_date=prev_date.strftime("%Y-%m-%d")
        data=pd.read_sql_query("""SELECT Date, Shift, Hour_Range,SUM(CAST(Running_mins As float)) as 
        Total_Running_mins, SUM(CAST(Idle_NoComment As float)) as Total_Idle_NoComment, 
        SUM(CAST(Idle_with_comment As float)) as Total_Idle_withcomment, SUM(CAST(Cycle_Count As float)) 
        as Total_Cycle_Count, SUM(CAST(Mould_Count As float)) as Total_Mould_Count, 
        COUNT(*) as Total_Press_Running, SUM(CAST(Mould_Interchange As float)) as Total_Mould_Interchange,
        SUM(CAST(MC_Count As float)) as MCTire_Count,SUM(CAST(SC_Count As float)) as SCTire_Count  
        FROM [STEAM_AI].[dbo].[STEAM_Curing] where Date>='""" + prev_date + """' 
        group by Date, Hour_Range,Shift order by Date, Hour_Range""", con=db2)
    except Exception as e:
        print(e)
    try:
        sql_Delete_query ="""DELETE FROM [STEAM_AI].[dbo].[Curing_Summary] where Date>=?"""
        cursor1.execute(sql_Delete_query,(prev_date,))
        for index, row in data.iterrows():
            cursor1.execute("INSERT INTO [STEAM_AI].[dbo].[Curing_Summary] ([Date],"
                            "[Shift],[Hour_Range],[Total_Running_mins],[Total_Idle_NoComment],"
                            "[Total_Idle_withcomment],[Total_Cycle_Count],[Total_Mould_Count]"
                            ",[Total_Press_Running],[Total_Mould_Interchange],[MCTire_Count],[SCTire_Count]) values(?,?,?,?,?,?,?,?,?,?,?,?)",
                            row['Date'], row['Shift'], row['Hour_Range'], row['Total_Running_mins'],
                            row['Total_Idle_NoComment'], row['Total_Idle_withcomment'], row['Total_Cycle_Count'],
                            row['Total_Mould_Count'], row['Total_Press_Running'], row['Total_Mould_Interchange'],
                            row['MCTire_Count'],row['SCTire_Count'])
            db2.commit()
            data.drop(index, inplace=True)
    except Exception as e:
        print(e)
    cursor1.close()
    db2.close()

def data_combine(prev_string):
    try:
        db = pyodbc.connect(
            'Driver={SQL Server};Server=SRVNGPPRD2SQL1;Database=STEAM_AI;Uid=LH;Pwd=Lighthouse@123;')
        cursor1 = db.cursor()
    except:
        print('No cursor connection')
    prev_date = pd.to_datetime(prev_string)
    prev_date2 = prev_date - timedelta(minutes=8 * 60)
    prev_time=prev_date.strftime("%I:%M:%S %p")
    prev_date = prev_date.strftime("%Y-%m-%d")
    prev_date2 = prev_date2.strftime("%Y-%m-%d")
    if prev_date>prev_date2:
        prev_date=prev_date2
    try:
        press_data=pd.read_sql_query("""SELECT * FROM [STEAM_AI].[dbo].[Curing_Summary] where Date >='"""
                                     +prev_date2+"""'""",con=db)
        steam_data=pd.read_sql_query("""SELECT * FROM [STEAM_AI].[dbo].[Total_Steam_Hourly] where _TIMESTAMP >='"""
                                     +prev_date+"""'""",con=db)
    except Exception as e:
        print(e)
    steam_data['time'] = steam_data['_TIMESTAMP'] - timedelta(minutes=8 * 60)
    steam_data['Date'] = steam_data['time'].astype(str).str.strip().str[:10]
    steam_data['Shift'] = steam_data['time'].astype(str).str.strip().str[11:13]
    # Allocating shifts =======================================================================================

    shift_c = ['15','16', '17', '18', '19', '20', '21', '22', '23']
    shift_a = ['00','01', '02', '03', '04', '05', '06', '07']
    shift_b = ['08','09', '10', '11', '12', '13', '14', '15']
    steam_data['Hour_Range']=steam_data['_TIMESTAMP']
    steam_data['Hour_Range']=steam_data['Hour_Range'].dt.strftime('%I:00:00 %p')
    steam_data['Shift'] = np.where(steam_data['Shift'].isin(shift_a), 'Shift_A',
                                            steam_data['Shift'])
    steam_data['Shift'] = np.where(steam_data['Shift'].isin(shift_b), 'Shift_B',
                                            steam_data['Shift'])
    steam_data['Shift'] = np.where(steam_data['Shift'].isin(shift_c), 'Shift_C',
                                            steam_data['Shift'])
    steam_summary=steam_data[['Date','Hour_Range','diff','LP_Steam','HP_Steam']]
    data_summary=pd.merge(press_data,steam_summary,how='inner',on=['Date','Hour_Range'])
    try:
        sql_Delete_query = """DELETE FROM [STEAM_AI].[dbo].[Data_Prepared] where Date>=?"""
        cursor1.execute(sql_Delete_query, (prev_date,))
        for index, row in data_summary.iterrows():
            if str(row['LP_Steam']) == 'nan':
                row['LP_Steam'] = ''
            if str(row['HP_Steam']) == 'nan':
                row['HP_Steam'] = ''
            cursor1.execute("INSERT INTO [STEAM_AI].[dbo].[Data_Prepared] ([Date],"
                            "[Shift],[Hour_Range],[Total_Running_mins],[Total_Idle_NoComment],"
                            "[Total_Idle_withcomment],[Total_Cycle_Count],[Total_Mould_Count]"
                            ",[Total_Press_Running],[MCTire_Count],[SCTire_Count],[Total_Mould_Interchange],[diff],"
                            "[LP_Steam],[HP_Steam]) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                            row['Date'], row['Shift'], row['Hour_Range'], row['Total_Running_mins'],
                            row['Total_Idle_NoComment'], row['Total_Idle_withcomment'], row['Total_Cycle_Count'],
                            row['Total_Mould_Count'], row['Total_Press_Running'], row['MCTire_Count'],
                            row['SCTire_Count'],row['Total_Mould_Interchange'],row['diff'],row['LP_Steam'],row['HP_Steam'])
            db.commit()
            print(index, row)
            data_summary.drop(index, inplace=True)
    except Exception as e:
        print(e)
    cursor1.close()
    db.close()

# def data_transform(prev_string,prev_hour):
#     try:
#         db = pyodbc.connect(
#             'Driver={SQL Server};Server=SRVNGPPRD2SQL1;Database=STEAM_AI;Uid=LH;Pwd=Lighthouse@123;')
#         cursor1 = db.cursor()
#     except:
#         print('No cursor connection')
#     prev_date = prev_string[:10]
#     prev_string_date=datetime.strptime(prev_date,'%Y-%m-%d')
#     two_yrs_ago = prev_string_date - timedelta(days=2*365)
#     #target_date=two_yrs_ago.strftime('%Y-%m-%d')
#     threshold_date=datetime.strptime('2024-03-04','%Y-%m-%d')
#     if two_yrs_ago>=threshold_date:
#         target_date=two_yrs_ago.strftime('%Y-%m-%d')
#     else:
#         target_date = threshold_date.strftime('%Y-%m-%d')
#     try:
#         data_preped=pd.read_sql_query("""SELECT * FROM [STEAM_AI].[dbo].[Data_Prepared] where Date >='"""
#                                      +target_date+"""' order by Date,Hour_Range""",con=db)
#     except Exception as e:
#         print(e)
#     prev_time=prev_hour.strftime("%Y-%m-%d %I:%M:%S %p")[:10]
#     Date_check = datetime.strptime(prev_time,'%Y-%m-%d') - timedelta(days=1)
#     description=data_preped.describe()
#     description.to_csv(config_loaded['host_folder'] + 'Data/Intelligent_data/Data_description.csv')
#     data_preped1=data_preped.copy()
#     dummy=pd.get_dummies(data_preped['Shift'])
#     data_preped=pd.concat([data_preped,dummy],axis=1)
#     hour_ind_master=pd.read_csv(config_loaded['host_folder'] + 'Data/Intelligent_data/Hour_indicator_master.csv')
#     data_preped2=pd.merge(data_preped,hour_ind_master,how='inner',on=['Shift','Hour_Range']).sort_values(by=['Date']).reset_index(drop=True)
#     dummy2 = pd.get_dummies(data_preped2['Indicator'])
#     dummy2.rename(columns={1: 'Hour1', 2: 'Hour2', 3: 'Hour3', 4: 'Hour4', 5: 'Hour5', 6: 'Hour6'
#         , 7: 'Hour7', 8: 'Hour8'}, inplace=True)
#     data_preped2 = pd.concat([data_preped2, dummy2], axis=1)
#     # calculate IQR for column Height
#     Q1 = data_preped2['diff'].quantile(0.20)
#     Q3 = data_preped2['diff'].quantile(0.80)
#     IQR = Q3 - Q1
#
#     # identify outliers
#     low_threshold = 4
#     high_threshold=4
#     outliers = data_preped2[(data_preped2['diff'] < Q1 - low_threshold * IQR) |
#                             (data_preped2['diff'] > Q3 + high_threshold * IQR)]
#     data_preped3 = data_preped2.drop(outliers.index)
#     data_preped4=data_preped3.drop(columns=['Shift','Indicator'],axis=1)
#     data_preped4['Date1']=pd.to_datetime(data_preped4['Date'])
#     data_preped5=data_preped4[data_preped4['Date1']>=Date_check]
#     try:
#         sql_Delete_query = """DELETE FROM [STEAM_AI].[dbo].[Transform_Data] where Date>=?"""
#         cursor1.execute(sql_Delete_query, (Date_check,))
#         for index, row in data_preped5.iterrows():
#             cursor1.execute("INSERT INTO [STEAM_AI].[dbo].[Transform_Data] ([Date],[Hour_Range],"
#                             "[Total_Running_Mins],[Total_Idle_NoComment],[Total_Idle_withComment],[Total_Cycle_Count]"
#                             ",[Total_Mould_Count],[Total_Press_Running],[Total_Mould_Interchange],[Shift_A],[Shift_B]"
#                             ",[Shift_C],[Hour1],[Hour2],[Hour3],[Hour4],[Hour5],[Hour6],[Hour7],[Hour8],"
#                             "[Steam_Consumed],[LP_Steam],[HP_Steam]) "
#                             "values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
#                             row['Date'], row['Hour_Range'], row['Total_Running_mins'],
#                             row['Total_Idle_NoComment'], row['Total_Idle_withcomment'], row['Total_Cycle_Count'],
#                             row['Total_Mould_Count'], row['Total_Press_Running'], row['Total_Mould_Interchange'],
#                             row['Shift_A'],row['Shift_B'],row['Shift_C'],row['Hour1'],row['Hour2'],row['Hour3'],
#                             row['Hour4'], row['Hour5'], row['Hour6'],row['Hour7'],row['Hour8'],row['diff'],
#                             row['LP_Steam'],row['HP_Steam'])
#             db.commit()
#             print(index, row)
#             data_preped5.drop(index, inplace=True)
#     except Exception as e:
#         print(e)
#     cursor1.close()
#     db.close()
#     return None