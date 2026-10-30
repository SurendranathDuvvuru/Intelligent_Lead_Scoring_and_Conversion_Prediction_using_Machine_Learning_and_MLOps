##############################################################################
# Import necessary modules and files
# #############################################################################

import pandas as pd
import os
import sqlite3
from sqlite3 import Error
from constants import *
from city_tier_mapping import *
from significant_categorical_level import *

###############################################################################
# Define the function to build database
# ##############################################################################

def build_dbs():
    conn = None
    # opening the connection for creating the sqlite db
    try:
        conn = sqlite3.connect(DB_PATH+DB_FILE_NAME)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()    
    '''
    This function checks if the db file with specified name is present 
    in the /Assignment/01_data_pipeline/scripts folder. If it is not present it creates 
    the db file with the given name at the given path. 


    INPUTS
        DB_FILE_NAME : Name of the database file 'utils_output.db'
        DB_PATH : path where the db file should exist  


    OUTPUT
    The function returns the following under the given conditions:
        1. If the file exists at the specified path
                prints 'DB Already Exists' and returns 'DB Exists'

        2. If the db file is not present at the specified loction
                prints 'Creating Database' and creates the sqlite db 
                file at the specified path with the specified name and 
                once the db file is created prints 'New DB Created' and 
                returns 'DB created'


    SAMPLE USAGE
        build_dbs()
    '''
###############################################################################
# Define function to read the table names in database
# ##############################################################################

def read_db_file(DB_FILE):
    conn = sqlite3.connect(DB_FILE)
    
    cur = conn.cursor()
    
    # reading all table names
    table_list = [a for a in cur.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
    # here is you table list
    print(table_list)
    
    conn.close()

###############################################################################
# Define function to load the csv file to the database
# ##############################################################################

def load_data_into_db():
    LDDATA_FRAME = pd.read_csv(LDDATA_DIRECTORY+LDDB_FILE_NAME, index_col=[0])
#    df_lead_scoring = pd.read_csv('Data/leadscoring.csv', index_col=[0])
    conn = sqlite3.connect(DB_FILE_NAME)
    LDDATA_FRAME.to_sql(name="loaded_data", con=conn, if_exists='replace', index=False)
    conn.commit
    print("success")
    
    '''
    This function loads the data present in data directory into the db
    which was created previously.
    It also replaces any null values present in 'toal_leads_dropped' and
    'referred_lead' columns with 0.


    INPUTS
        DB_FILE_NAME : Name of the database file
        DB_PATH : path where the db file should be
        DATA_DIRECTORY : path of the directory where 'leadscoring.csv' 
                        file is present
        

    OUTPUT
        Saves the processed dataframe in the db in a table named 'loaded_data'.
        If the table with the same name already exsists then the function 
        replaces it.


    SAMPLE USAGE
        load_data_into_db()
    '''

###############################################################################
# Define function to read Table contents in a DB
# ##############################################################################

def read_table_data(TAB_NAME):
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        print("Connected to "+TAB_NAME+" table")
        
        sqlite_select_query = """SELECT * from """+TAB_NAME
        cur.execute(sqlite_select_query)
        records = cur.fetchone()
        print("First row in Table: ", records)
#        print("Total rows are:  ", len(records))
#        for row in records:
#            print("created_date:", row[0])
#            print("city_mapped:", row[1])
#            print("first_platform_c:", row[2])
        
        conn.close()
        
    except sqlite3.Error as error:
        print("Failed to read data from "+TAB_NAME+" table", error)
    
    finally:
        if conn:
            conn.close()

###############################################################################
# Define function to map cities to their respective tiers
# ##############################################################################

def map_city_tier():
    MCTDATA_FRAME = pd.read_csv(MCTDB_PATH+MCTDB_FILE_NAME, index_col=[0])
    MCTDATA_FRAME["city_tier"] = MCTDATA_FRAME["city_mapped"].map(city_tier_mapping)
    MCTDATA_FRAME["city_tier"] = MCTDATA_FRAME["city_tier"].fillna(3.0)
    print("success")
    
    conn = sqlite3.connect(DB_FILE_NAME)
    MCTDATA_FRAME.to_sql(name="city_tier_mapped", con=conn, if_exists='replace', index=False)
    conn.commit
    print("Updated map_city_tier data loaded in to DB, success")
       
    '''
    This function maps all the cities to their respective tier as per the
    mappings provided in the city_tier_mapping.py file. If a
    particular city's tier isn't mapped(present) in the city_tier_mapping.py 
    file then the function maps that particular city to 3.0 which represents
    tier-3.


    INPUTS
        DB_FILE_NAME : Name of the database file
        DB_PATH : path where the db file should be
        city_tier_mapping : a dictionary that maps the cities to their tier

    
    OUTPUT
        Saves the processed dataframe in the db in a table named
        'city_tier_mapped'. If the table with the same name already 
        exsists then the function replaces it.

    
    SAMPLE USAGE
        map_city_tier()

    '''
###############################################################################
# Define function to map insignificant categorial variables to "others"
# ##############################################################################
def map_categorical_vars():
    MCVDATA_FRAME = pd.read_csv(MCVDB_PATH+MCVDB_FILE_NAME, index_col=[0])
    
    # cumulative percetage is calculated for all the three columns - first_platform_c, first_utm_medium_c, first_utm_source_c
    for column in ['first_platform_c', 'first_utm_medium_c', 'first_utm_source_c']:
        MCV_CFDATA_FRAME = MCVDATA_FRAME[column].value_counts()
        MCV_CFDATA_FRAME = pd.DataFrame({'column':MCV_CFDATA_FRAME.index, 'value':MCV_CFDATA_FRAME.values})
        MCV_CFDATA_FRAME['perc'] = MCV_CFDATA_FRAME['value'].cumsum()/MCV_CFDATA_FRAME['value'].sum()
        print(column,)
        print(list(MCV_CFDATA_FRAME.loc[MCV_CFDATA_FRAME['perc']<=0.9].column))
        print('\n')
        
    conn = sqlite3.connect(DB_FILE_NAME)
    MCV_CFDATA_FRAME.to_sql(name="categorical_variables_mapped", con=conn, if_exists='replace', index=False)
    conn.commit
    print("Updated categorical_variables_mapped data loaded in to DB, success")
            
    '''
    This function maps all the insignificant variables present in 'first_platform_c'
    'first_utm_medium_c' and 'first_utm_source_c'. The list of significant variables
    should be stored in a python file in the 'significant_categorical_level.py' 
    so that it can be imported as a variable in utils file.
    

    INPUTS
        DB_FILE_NAME : Name of the database file
        DB_PATH : path where the db file should be present
        list_platform : list of all the significant platform.
        list_medium : list of all the significat medium
        list_source : list of all rhe significant source

        **NOTE : list_platform, list_medium & list_source are all constants and
                 must be stored in 'significant_categorical_level.py'
                 file. The significant levels are calculated by taking top 90
                 percentils of all the levels. For more information refer
                 'data_cleaning.ipynb' notebook.
  

    OUTPUT
        Saves the processed dataframe in the db in a table named
        'categorical_variables_mapped'. If the table with the same name already 
        exsists then the function replaces it.

    
    SAMPLE USAGE
        map_categorical_vars()
    '''

##############################################################################
# Define function that maps interaction columns into 4 types of interactions
# #############################################################################
def interactions_mapping():
#    IMDATA_FRAME = pd.read_csv(IMDB_PATH+IMDB_FILE_NAME, index_col=[0])
    
    con = sqlite3.connect('/home/Assignment/01_data_pipeline/scripts/utils_output.db')
    IMDATA_FRAME = pd.read_sql("""SELECT * from city_tier_mapped""", con)
    
    # all the levels below 90 percentage are assgined to a single level called others
#    new_df = MCTDATA_FRAME[~MCTDATA_FRAME['first_platform_c'].isin(list_platform)] # get rows for levels which are not present in list_platform
    new_df = IMDATA_FRAME[~IMDATA_FRAME['first_platform_c'].isin(list_platform)] # get rows for levels which are not present in list_platform
    new_df['first_platform_c'] = "others" # replace the value of these levels to others
    old_df = IMDATA_FRAME[IMDATA_FRAME['first_platform_c'].isin(list_platform)] # get rows for levels which are present in list_platform
    INTERIMDATA_FRAME = pd.concat([new_df, old_df]) # concatenate new_df and old_df to get the final dataframe
    print("All the levels below 90 percentage are assgined to a single level called others for 'first_platform_c' column")
    
    # all the levels below 90 percentage are assgined to a single level called others
    new_df = INTERIMDATA_FRAME[~INTERIMDATA_FRAME['first_utm_medium_c'].isin(list_medium)] # get rows for levels which are not present in list_medium
    new_df['first_utm_medium_c'] = "others" # replace the value of these levels to others
    old_df = INTERIMDATA_FRAME[INTERIMDATA_FRAME['first_utm_medium_c'].isin(list_medium)] # get rows for levels which are present in list_medium
    INTERIMDATA_FRAME = pd.concat([new_df, old_df]) # concatenate new_df and old_df to get the final dataframe
    print("All the levels below 90 percentage are assgined to a single level called others for 'first_utm_medium_c' column")
    
    # all the levels below 90 percentage are assgined to a single level called others
    new_df = INTERIMDATA_FRAME[~INTERIMDATA_FRAME['first_utm_source_c'].isin(list_source)] # get rows for levels which are not present in list_source
    new_df['first_utm_source_c'] = "others" # replace the value of these levels to others
    old_df = INTERIMDATA_FRAME[INTERIMDATA_FRAME['first_utm_source_c'].isin(list_source)] # get rows for levels which are present in list_source
    INTERIMDATA_FRAME = pd.concat([new_df, old_df]) # concatenate new_df and old_df to get the final dataframe
    print("All the levels below 90 percentage are assgined to a single level called others for 'first_utm_source_c' column")
    
#    INTERIMDATA_FRAME.head()
    
    INTERIMDATA_FRAME['total_leads_droppped'] = INTERIMDATA_FRAME['total_leads_droppped'].fillna(0)
    INTERIMDATA_FRAME['referred_lead'] = INTERIMDATA_FRAME['referred_lead'].fillna(0)
    print("Nan values in column 'total_leads_droppped' and column 'referred_lead' are filled with 0")
    
    INTERIMDATA_FRAME = INTERIMDATA_FRAME.drop(['city_mapped'], axis = 1)
    print("'city_mapped' column dropped")
    
    INTERIMDATA_FRAME = INTERIMDATA_FRAME.drop_duplicates()
    print("Duplicate rows are dropped from Table")
    
    INTERACTION_MAPPING = pd.read_csv(IMDB_PATH_NOTE+IMDB_FILE_NAME_NOTE, index_col=[0])
    print("Reading INTERACTION_MAPPING .csv file to DataFrame")
    
#    INTERIMDATA_FRAME.loc[(INTERIMDATA_FRAME['created_date'] == '2021-11-04 06:34:10')]
#    print("success-8")
    
    # unpivot the interaction columns and put the values in rows
    df_unpivot = pd.melt(INTERIMDATA_FRAME, id_vars=['created_date', 'first_platform_c',
                                      'first_utm_medium_c', 'first_utm_source_c', 'total_leads_droppped', 'city_tier',
                                      'referred_lead', 'app_complete_flag'], var_name='interaction_type', value_name='interaction_value')
    
#    df_unpivot.shape
    print("Unpivot done for interaction columns of df_lead_scoring dataframe and values filled in rows")
    
    # example of single row converted into 37 rows
#    df_unpivot.loc[(df_unpivot['created_date'] == '2021-11-04 06:34:10')]
    
    # handle the nulls in the interaction value column
    df_unpivot['interaction_value'] = df_unpivot['interaction_value'].fillna(0)
    print("Nulls in the 'interaction value' column handled")
    
    # map interaction type column with the mapping file to get interaction mapping
    INTERIMDATA_FRAME = pd.merge(df_unpivot, INTERACTION_MAPPING, on='interaction_type', how='left')
    print("Mapped 'interaction type' column with the mapping file to get interaction mapping")
    
#    INTERIMDATA_FRAME.head()
    
#    INTERIMDATA_FRAME.shape
#    print("success-11")
    
    #dropping the interaction type column as it is not needed
    INTERIMDATA_FRAME = INTERIMDATA_FRAME.drop(['interaction_type'], axis=1)
    print("Dropped the 'interaction type' column as it is not needed")
    
    # interaction type column has been removed and replaced by interaction mapping column
    INTERIMDATA_FRAME.loc[(INTERIMDATA_FRAME['created_date'] == '2021-11-04 06:34:10')]
    
    # pivoting the interaction mapping column values to individual columns in the dataset
    df_pivot = INTERIMDATA_FRAME.pivot_table(
        values='interaction_value', index=['created_date', 'city_tier', 'first_platform_c',
                                           'first_utm_medium_c', 'first_utm_source_c', 'total_leads_droppped',
                                           'referred_lead', 'app_complete_flag'], columns='interaction_mapping', aggfunc='sum')
    
    print("Pivot done for interaction mapping column values to individual columns in the dataset")
    
    df_pivot = df_pivot.reset_index()
    print("Index has been reset")
    
    # the rows are again converted back to columns. 37 rows gets converted to a single row.
#    df_pivot.shape
    
#    df_pivot.head()
    
    # the above rows have been reduced back to a single row
#    df_pivot.loc[(INTERIMDATA_FRAME['created_date'] == '2021-11-04 06:34:10')]
#    print("success-15")
    
    conn = sqlite3.connect(DB_FILE_NAME)
    df_pivot.to_sql(name="interactions_mapped", con=conn, if_exists='replace', index=False)
    conn.commit
    print("Updated Interactions mapping dataframe is loaded to DB into interactions_mapped table, success")

    
    '''
    This function maps the interaction columns into 4 unique interaction columns
    These mappings are present in 'interaction_mapping.csv' file. 


    INPUTS
        DB_FILE_NAME: Name of the database file
        DB_PATH : path where the db file should be present
        INTERACTION_MAPPING : path to the csv file containing interaction's
                                   mappings
        INDEX_COLUMNS_TRAINING : list of columns to be used as index while pivoting and
                                 unpivoting during training
        INDEX_COLUMNS_INFERENCE: list of columns to be used as index while pivoting and
                                 unpivoting during inference
        NOT_FEATURES: Features which have less significance and needs to be dropped
                                 
        NOTE : Since while inference we will not have 'app_complete_flag' which is
        our label, we will have to exculde it from our features list. It is recommended 
        that you use an if loop and check if 'app_complete_flag' is present in 
        'categorical_variables_mapped' table and if it is present pass a list with 
        'app_complete_flag' column, or else pass a list without 'app_complete_flag'
        column.

    
    OUTPUT
        Saves the processed dataframe in the db in a table named 
        'interactions_mapped'. If the table with the same name already exsists then 
        the function replaces it.
        
        It also drops all the features that are not requried for training model and 
        writes it in a table named 'model_input'

    
    SAMPLE USAGE
        interactions_mapping()
    '''
    
   
