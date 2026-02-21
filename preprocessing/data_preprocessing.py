import pandas as pd
import os
from preprocessing.mapping_static import team_mapping, service_mapping
from preprocessing.utils import rename_column,fillna_forward
from general.general_functions import  read_excel

def dataframe_processing(df_raw, position_df):#, result_excel_name):
    _df_raw = read_excel (df_raw, skiprows=4, header=0)
    _employee_df = read_excel(position_df)
    # _result_excel_name = result_excel_name

    # mask = ~_df_raw['Unnamed: 0'].astype(str).str.startswith('Total')
    # print(_df_raw)
    mask = ~_df_raw['Unnamed: 0'].apply(lambda x: str(x).startswith('Total'))
    _df_raw = _df_raw[mask]
    if 'Unnamed: 0' in _df_raw.columns:
        _df_raw = rename_column(_df_raw,'Unnamed: 0', 'Name')
    _df_raw = fillna_forward(_df_raw,'Name')
    _df_raw = rename_column(_df_raw,'Product/Service', 'Product_Service')
    _df_raw = rename_column(_df_raw,'Memo/Description', 'Memo_Description')
    _df_raw = rename_column(_df_raw,'Activity Date', 'Activity_Date')
    _df_raw = _df_raw[~_df_raw['Activity_Date'].isnull()]
    # cleaning the name column
    _df_raw["Name"] = _df_raw["Name"].str.replace('[^a-zA-Z0-9\s]', '', regex=True)
    _employee_df["Name"] = _employee_df["Name"].str.replace('[^a-zA-Z0-9\s]', '', regex=True)
    _df_raw['Work Items'] = _df_raw['Product_Service'].map(service_mapping)
    # _df_raw['Team'] = _df_raw['Name'].map(team_mapping)
    _df_raw["Product_Service"] = _df_raw["Product_Service"].str.replace('[^a-zA-Z0-9\s]', ' ', regex=True)
    _df_raw.replace('', pd.NA, inplace=True)
    _modified_df = pd.merge(_df_raw, _employee_df, on='Name', how='left')
    _modified_df['Category'].replace(pd.NA, 'missing', inplace=True)
    _modified_df['Team'].replace(pd.NA, 'TeamLead/Director/Left', inplace=True)

    # desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    # result_excel_path = os.path.join(desktop_path, result_excel_name + ".xlsx")
    # creating a session state to save the path of the excel file after it has been generated
    # _modified_df.to_excel(result_excel_path, index=False, engine='openpyxl')
    # columns = list(df.columns)
    return _modified_df
