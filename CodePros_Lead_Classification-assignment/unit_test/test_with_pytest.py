##############################################################################
# Import the necessary modules
# #############################################################################

import pandas as pd
import os
import sqlite3
from sqlite3 import Error
from constants import *
from city_tier_mapping import *
from significant_categorical_level import *


###############################################################################
# Write test cases for load_data_into_db() function
# ##############################################################################

def test_load_data_into_db():
    LDDATA_FRAME = pd.read_csv(LDDATA_DIRECTORY+LDDB_FILE_NAME, index_col=[0])
    #   df_lead_scoring = pd.read_csv('Data/leadscoring.csv', index_col=[0])
    conn = sqlite3.connect(DB_FILE_NAME)
    LDDATA_FRAME.to_sql(name="loaded_data_test_case", con=conn, if_exists='replace', index=False)
    conn.commit
    print("success")
    
    """_summary_
    This function checks if the load_data_into_db function is working properly by
    comparing its output with test cases provided in the db in a table named
    'loaded_data_test_case'

    INPUTS
        DB_FILE_NAME : Name of the database file 'utils_output.db'
        DB_PATH : path where the db file should be present
        UNIT_TEST_DB_FILE_NAME: Name of the test database file 'unit_test_cases.db'

    SAMPLE USAGE
        output=test_get_data()

    """

###############################################################################
# Write test cases for map_city_tier() function
# ##############################################################################

def test_map_city_tier():
    MCTDATA_FRAME = pd.read_csv(MCTDB_PATH+MCTDB_FILE_NAME, index_col=[0])
    MCTDATA_FRAME["city_tier"] = MCTDATA_FRAME["city_mapped"].map(city_tier_mapping)
    MCTDATA_FRAME["city_tier"] = MCTDATA_FRAME["city_tier"].fillna(3.0)
    print("success")
    
    conn = sqlite3.connect(DB_FILE_NAME)
    MCTDATA_FRAME.to_sql(name="city_tier_mapped_test_case", con=conn, if_exists='replace', index=False)
    conn.commit
    print("Updated city_tier_mapped_test_case data loaded in to DB, success")
    
    
    """_summary_
    This function checks if map_city_tier function is working properly by
    comparing its output with test cases provided in the db in a table named
    'city_tier_mapped_test_case'

    INPUTS
        DB_FILE_NAME : Name of the database file 'utils_output.db'
        DB_PATH : path where the db file should be present
        UNIT_TEST_DB_FILE_NAME: Name of the test database file 'unit_test_cases.db'

    SAMPLE USAGE
        output=test_map_city_tier()

    """

###############################################################################
# Write test cases for map_categorical_vars() function
# ##############################################################################    

def test_map_categorical_vars():
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
    MCV_CFDATA_FRAME.to_sql(name="categorical_variables_mapped_test_case", con=conn, if_exists='replace', index=False)
    conn.commit
    print("Updated categorical_variables_mapped_test_case data loaded in to DB, success")

    """_summary_
    This function checks if map_cat_vars function is working properly by
    comparing its output with test cases provided in the db in a table named
    'categorical_variables_mapped_test_case'

    INPUTS
        DB_FILE_NAME : Name of the database file 'utils_output.db'
        DB_PATH : path where the db file should be present
        UNIT_TEST_DB_FILE_NAME: Name of the test database file 'unit_test_cases.db'
    
    SAMPLE USAGE
        output=test_map_cat_vars()

    """    

###############################################################################
# Write test cases for interactions_mapping() function
# ##############################################################################    

def test_interactions_mapping():
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
    
#    INTERIMDATA_FRAME.loc[(INTERIMDATA_FRAME['created_date'] == '2021-11-04 06:34:10')
#    print("success-8")
    
    # unpivot the interaction columns and put the values in rows
    df_unpivot = pd.melt(INTERIMDATA_FRAME, id_vars=['created_date', 'first_platform_c',
                                                     'first_utm_medium_c', 'first_utm_source_c', 'total_leads_droppped', 'city_tier',
                                                     'referred_lead', 'app_complete_flag'], var_name='interaction_type', value_name='interaction_value')
    
    #df_unpivot.shape
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
    df_pivot.to_sql(name="interactions_mapped_test_case", con=conn, if_exists='replace', index=False)
    conn.commit
    print("Updated Interactions mapping dataframe is loaded to DB into interactions_mapped_test_case table, success")

    """_summary_
    This function checks if test_column_mapping function is working properly by
    comparing its output with test cases provided in the db in a table named
    'interactions_mapped_test_case'

    INPUTS
        DB_FILE_NAME : Name of the database file 'utils_output.db'
        DB_PATH : path where the db file should be present
        UNIT_TEST_DB_FILE_NAME: Name of the test database file 'unit_test_cases.db'

    SAMPLE USAGE
        output=test_column_mapping()

    """ 
   
