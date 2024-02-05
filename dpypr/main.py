# Dependencies ################################################################
import pandas as pd
import os
import time
import logging
import sqlite3
import pyarrow.feather as feather


# Data Cleaning ###############################################################
def headers_to_snakecase(df, uppercase = False):
    '''
    Converts all column headers to lower snake case by defatul and uppercase if
    'uppercase' argument is True.
    '''
    if uppercase:
        df.columns = (df.columns.str.upper().str.replace(' ', '_'))
    else:
        df.columns = (df.columns.str.lower().str.replace(' ', '_'))
    return df

def values_to_lowercase(df):
    '''
    Converts all string values in dataframe to lowercase.
    '''
    df = df.apply(lambda x: x.str.lower() if x.dtype == "object" else x)
    return df

def values_to_uppercase(df):
    '''
    Converts all string values in dataframe to uppercase.
    '''
    df = df.apply(lambda x: x.str.upper() if x.dtype == "object" else x)
    return df

def values_strip_whitespace(df):
    '''
    Converts all string values to lowercase.
    '''
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    return df

def optimise_numeric_datatypes(df):
    '''
    Optimises the data types in a pandas DataFrame by attempting to convert
    strings to numerical data where possible and to the smallest possible 
    integer datatype.
    ''' 
    for col in df.columns:
        if df[col].dtype == object:
            pass
        else:
            if all(df[col] % 1 == 0):
                df[col] = pd.to_numeric(df[col], downcast = 'integer')
            else:
                df[col] = pd.to_numeric(df[col], downcast = 'float')
    return df


# Data Loading ################################################################
def read_all_json(directory_path):
    '''
    Iteratively loads data.json from the data directory and assign to 
    dataframes. Unpacks dictionary to global variables names with the format 
    df_{filename}.
    '''
    files = os.listdir(directory_path)
    data_dictionary = {}
    for file in files:
        if file.endswith('.json'):
            df = pd.read_json(os.path.join(directory_path, file))
            filename = os.path.splitext(file)[0]
            data_dictionary[f'df_{filename}'] = df
    return data_dictionary

def read_all_csv(directory_path):
    '''
    Iteratively loads data.csv from the data directory and assign to 
    dataframes. Unpacks dictionary to global variables names with the format 
    df_{filename}.
    '''
    files = os.listdir(directory_path)
    data_dictionary = {}
    for file in files:
        if file.endswith('.csv'):
            df = pd.read_csv(os.path.join(directory_path, file))
            filename = os.path.splitext(file)[0]
            data_dictionary[f'df_{filename}'] = df
    return data_dictionary

def read_all_xlsx(directory_path):
    '''
    Iteratively loads data.xlsx from the data directory and assign to 
    dataframes. Unpacks dictionary to global variables names with the format 
    df_{filename}.
    '''
    files = os.listdir(directory_path)
    data_dictionary = {}
    for file in files:
        if file.endswith('.xlsx'):
            df = pd.read_excel(os.path.join(directory_path, file))
            filename = os.path.splitext(file)[0]
            data_dictionary[f'df_{filename}'] = df
    return data_dictionary

def read_all_feather(directory_path):
    '''
    Iteratively loads data.feather from the data directory and assign to 
    dataframes. Unpacks dictionary to global variables names with the format 
    df_{filename}.
    '''
    files = os.listdir(directory_path)
    data_dictionary = {}
    for file in files:
        if file.endswith('.feather'):
            df = pd.read_feather(os.path.join(directory_path, file))
            filename = os.path.splitext(file)[0]
            data_dictionary[f'df_{filename}'] = df
    return data_dictionary

def read_all_parquet(directory_path):
    '''
    Iteratively loads data.parquet from the data directory and assign to 
    dataframes. Unpacks dictionary to global variables names with the format 
    df_{filename}.
    '''
    files = os.listdir(directory_path)
    data_dictionary = {}
    for file in files:
        if file.endswith('.parquet'):
            df = pd.read_parquet(os.path.join(directory_path, file))
            filename = os.path.splitext(file)[0]
            data_dictionary[f'df_{filename}'] = df
    return data_dictionary

def read_all_pickle(directory_path):
    '''
    Iteratively loads data.pickle from the data directory and assign to 
    dataframes. Unpacks dictionary to global variables names with the format 
    df_{filename}.
    '''
    files = os.listdir(directory_path)
    data_dictionary = {}
    for file in files:
        if file.endswith('.pickle'):
            df = pd.read_pickle(os.path.join(directory_path, file))
            filename = os.path.splitext(file)[0]
            data_dictionary[f'df_{filename}'] = df
    return data_dictionary
              
def read_all_sqlite(db_path):
    '''
    Returns all data from a sqlite database as a dictionary.
    '''
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # queries all tables in database
    cur.execute('''
        SELECT name 
        FROM sqlite_master 
        WHERE type = 'table';
    ''')
    table_names = cur.fetchall()
    
    data_dictionary = {}
    for table_name in table_names:
        # selects everything from each table.
        query = f"SELECT * FROM {table_name[0]}"
        data_dictionary[table_name[0]] = pd.read_sql_query(query, conn)
    conn.close()
    return data_dictionary

def unpack_data_dictionary(
        data_dictionary, 
        globals_dict = globals(), 
        sleep_seconds = 0, 
        messaging = False
    ):
    '''
    Loads all data from data_dictionary into global variables with record 
    counts.
    '''
    for key, value in data_dictionary.items():
        globals_dict[f'df_{key}'] = value
        if messaging:
            sleep_log(
                f'- Loaded df_{key} ({len(value):,}) records.', 
                sleep_time = sleep_seconds
                )


# Data Writing ################################################################
def write_json_global_df(path, file_prefix = 'processed'):
    '''
    Writes all objects beginning with 'df_' in global space to path as .json. 
    Modifier allows user to rename processed files with different prefix, 
    'processed' by default.
    '''
    globals_dict = globals()
    for name, data in globals_dict.items():
        if name.startswith('df_'):
            data.to_json(path + '/' + file_prefix + '_' + name[3:] + '.json')

def write_csv_global_df(path, file_prefix = 'processed'):
    '''
    Writes all objects beginning with 'df_' in global space to path as .csv. 
    Modifier allows user to rename processed files with different prefix, 
    'processed' by default.
    '''
    globals_dict = globals()
    for name, data in globals_dict.items():
        if name.startswith('df_'):
            data.to_csv(path + '/' + file_prefix + '_' + name[3:] + '.csv')
            
def write_xlsx_global_df(path, file_prefix = 'processed'):
    '''
    Writes all objects beginning with 'df_' in global space to path as .xlsx. 
    Modifier allows user to rename processed files with different prefix, 
    'processed' by default.
    '''
    globals_dict = globals()
    for name, data in globals_dict.items():
        if name.startswith('df_'):
            data.to_excel(path + '/' + file_prefix + '_' + name[3:] + '.xlsx')

def write_feather_global_df(path, file_prefix = 'processed'):
    '''
    Writes all objects beginning with 'df_' in global space to path as 
    .feather. Modifier allows user to rename processed files with different 
    prefix, 'processed' by default.
    '''
    globals_dict = globals()
    for name, data in globals_dict.items():
        if name.startswith('df_'):
            data.to_feather(
                path + '/' + file_prefix + '_' + name[3:] + '.feather'
            )
            
def write_parquet_global_df(path, file_prefix = 'processed'):
    '''
    Writes all objects beginning with 'df_' in global space to path as 
    .parquet. Modifier allows user to rename processed files with different 
    prefix, 'processed' by default.
    '''
    globals_dict = globals()
    for name, data in globals_dict.items():
        if name.startswith('df_'):
            data.to_parquet(
                path + '/' + file_prefix + '_' + name[3:] + '.parquet'
            )
            
def write_pickle_global_df(path, file_prefix = 'processed'):
    '''
    Writes all objects beginning with 'df_' in global space to path as 
    .pickle. Modifier allows user to rename processed files with different 
    prefix, 'processed' by default.
    '''
    globals_dict = globals()
    for name, data in globals_dict.items():
        if name.startswith('df_'):
            data.to_pickle(
                path + '/' + file_prefix + '_' + name[3:] + '.pickle'
            )          
                
                
# Diagnostics and Information #################################################
def fetch_all_sqlite_tables(db_path, print_names = False):
    '''
    Returns all table names present in a sqlite database.
    '''
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # queries all tables in database
    cur.execute('''
        SELECT name 
        FROM sqlite_master 
        WHERE type = 'table';
    ''')
    table_names = cur.fetchall()
    if print_names:
        print('Table names:')
        [print(f'- {table[0]}') for table in table_names]
        return table_names
    else:
        return table_names
    
def fetch_global_df():
    '''
    Lists all objects beginning with 'df_' in global space.
    '''
    globals_dict = globals()
    for name in globals_dict:
        if name.startswith('df_'):
            print(name)

def sleep_log(message, sleep_time = 0):
    '''
    Outputs info logging mesage to console with variable sleep timer.
    '''
    time.sleep(sleep_time)
    logging.info(message)