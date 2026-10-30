'''
filename: utils.py
functions: encode_features, get_train_model
creator: shashank.gupta
version: 1
'''

###############################################################################
# Import necessary modules
# ##############################################################################

import pandas as pd
import numpy as np

import sqlite3
from sqlite3 import Error

from constants import *

import mlflow
import mlflow.sklearn

from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from pycaret.regression import *

#from Lead_scoring_training_pipeline.constants import *


###############################################################################
# Define the function to build database
###############################################################################

def build_dbs():
    conn = None
    # opening the connection for creating the sqlite db
    try:
        conn = sqlite3.connect(DB_PATH+DB_FILE_NAME_NOTE)
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
###############################################################################

def read_db_file(DB_FILE_NAME_NOTE):
    conn = sqlite3.connect(DB_FILE_NAME_NOTE)
    
    cur = conn.cursor()
    
    # reading all table names
    table_list = [a for a in cur.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
    # here is you table list
    print(table_list)
    
    conn.close()

###############################################################################
# Define function to read Table contents in a DB
###############################################################################

def read_table_data(TAB_NAME):
    try:
        conn = sqlite3.connect(DB_FILE_NAME_NOTE)
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
# Define the function to encode features
# ##############################################################################

def encode_features():
    CLNDATA_FRAME = pd.read_csv(EFDB_PATH+EFDATA_DIRECTORY)
    
    TARGDATA_FRAME = pd.DataFrame()
    
    Column_num = 7
    
    TARGDATA_FRAME = CLNDATA_FRAME['app_complete_flag']
    
    features_to_encode = FEATURES_TO_ENCODE
    encoded_df = pd.DataFrame(columns= ['created_date', 'city_tier', 'first_platform_c', 'first_utm_medium_c', 'first_utm_source_c',
                                        'total_leads_droppped', 'referred_lead', 'app_complete_flag', 'assistance_interaction', 'career_interaction', 
                                        'payment_interaction', 'social_interaction', 'syllabus_interaction'])
    
    placeholder_df = pd.DataFrame()
    
    # One-Hot Encoding using get_dummies for the specified categorical features
    for f in features_to_encode:
        if(f in CLNDATA_FRAME.columns):
            encoded = pd.get_dummies(CLNDATA_FRAME[f])
            encoded = encoded.add_prefix(f + '_')
            placeholder_df = pd.concat([placeholder_df, encoded], axis=1)
        else:
            print('Feature not found')
            
    # Implement these steps to prevent dimension mismatch during inference
    for feature in encoded_df.columns:
        if feature in CLNDATA_FRAME.columns:
            encoded_df[feature] = CLNDATA_FRAME[feature]
        if feature in placeholder_df.columns:
            encoded_df[feature] = placeholder_df[feature]
            
    # fill all null values
    encoded_df.fillna(0, inplace=True)
    
    encoded_df = encoded_df.drop(['created_date'], axis=1)
    
    encoded_df = encoded_df.drop(['assistance_interaction'], axis=1)
    
    encoded_df = encoded_df.drop(['career_interaction'], axis=1)
    
    encoded_df = encoded_df.drop(['payment_interaction'], axis=1)
    
    encoded_df = encoded_df.drop(['social_interaction'], axis=1)
    
    encoded_df = encoded_df.drop(['syllabus_interaction'], axis=1)
    
    
    #    from sklearn import preprocessing
    # normalization
#    val = encoded_df.values 
#    min_max_normalizer = preprocessing.MinMaxScaler()
#    norm_val = min_max_normalizer.fit_transform(val)
#    df2 = pd.DataFrame(norm_val)
    
#    processed_features_data = df2.copy()

    conn = sqlite3.connect(DB_FILE_NAME_NOTE)
    encoded_df.to_sql(name="features", con=conn, if_exists='replace', index=False)
    TARGDATA_FRAME.to_sql(name="target", con=conn, if_exists='replace', index=False)
    conn.commit


    '''
    This function one hot encodes the categorical features present in our  
    training dataset. This encoding is needed for feeding categorical data 
    to many scikit-learn models.

    INPUTS
        db_file_name : Name of the database file 
        db_path : path where the db file should be
        ONE_HOT_ENCODED_FEATURES : list of the features that needs to be there in the final encoded dataframe
        FEATURES_TO_ENCODE: list of features  from cleaned data that need to be one-hot encoded
       

    OUTPUT
        1. Save the encoded features in a table - features
        2. Save the target variable in a separate table - target


    SAMPLE USAGE
        encode_features()
        
    **NOTE : You can modify the encode_featues function used in heart disease's inference
        pipeline from the pre-requisite module for this.
    '''


###############################################################################
# Define the function to train the model
# ##############################################################################

def get_trained_model():
    con = sqlite3.connect('/home/Assignment/02_training_pipeline/notebooks/lead_scoring_data_cleaning.db')
    FEATDATA_FRAME = pd.read_sql("""SELECT * from features""", con)
        
    expt_basic = setup(
    data = FEATDATA_FRAME, 
    target = 'app_complete_flag', 
    session_id=42,                      # Random seed to ensure reproducibility of the experiment with the same data
    train_size=0.8,                     # 80% training data & 20% held-out validation data
    ignore_features=[],
    numeric_imputation="median",        # "mean" by default
    categorical_imputation="mode",      # "constant" (not_available) by default
    )
    
    models()
    
    best = compare_models(sort="RMSE", exclude=['knn', 'dummy', 'svm', 'ada'], fold=5)
    
    lgbm = create_model("lightgbm", fold=10)
    
    tuned_lgbm = tune_model(lgbm, fold=5, optimize="RMSE")
    
    print(lgbm, "\n")
    print(tuned_lgbm)
    
    '''
    This function setups mlflow experiment to track the run of the training pipeline. It 
    also trains the model based on the features created in the previous function and 
    logs the train model into mlflow model registry for prediction. The input dataset is split
    into train and test data and the auc score calculated on the test data and
    recorded as a metric in mlflow run.   

    INPUTS
        db_file_name : Name of the database file
        db_path : path where the db file should be


    OUTPUT
        Tracks the run in experiment named 'Lead_Scoring_Training_Pipeline'
        Logs the trained model into mlflow model registry with name 'LightGBM'
        Logs the metrics and parameters into mlflow run
        Calculate auc from the test data and log into mlflow run  

    SAMPLE USAGE
        get_trained_model()
    '''

   
