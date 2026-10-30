'''
filename: utils.py
functions: encode_features, load_model
creator: shashank.gupta
version: 1
'''

###############################################################################
# Import necessary modules
# ##############################################################################

import mlflow
import mlflow.sklearn
import pandas as pd

import sqlite3
from constants import *
import os
import logging

from datetime import datetime

###############################################################################
# Define function to read the table names in database
###############################################################################

def read_db_file(INFDB_FILE_NAME):
    conn = sqlite3.connect(INFDB_FILE_NAME)
    
    cur = conn.cursor()
    
    # reading all table names
    table_list = [a for a in cur.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
    # here is you table list
    print(table_list)
    
    conn.close()
    
###############################################################################
# Define the function to train the model
# ##############################################################################

def encode_features():
    INFDATA_FRAME = pd.read_csv(INFDB_PATH+INFDB_FILE_NAME)
    
    features_to_encode = FEATURES_TO_ENCODE
    encoded_df = pd.DataFrame(columns= ['created_date', 'city_tier', 'first_platform_c', 'first_utm_medium_c', 'first_utm_source_c',
                                        'total_leads_droppped', 'referred_lead', 'app_complete_flag', 'assistance_interaction', 'career_interaction', 
                                        'payment_interaction', 'social_interaction', 'syllabus_interaction'])
    
    placeholder_df = pd.DataFrame()
    
    # One-Hot Encoding using get_dummies for the specified categorical features
    for f in features_to_encode:
        if(f in INFDATA_FRAME.columns):
            encoded = pd.get_dummies(INFDATA_FRAME[f])
            encoded = encoded.add_prefix(f + '_')
            placeholder_df = pd.concat([placeholder_df, encoded], axis=1)
        else:
            print('Feature not found')
            
    # Implement these steps to prevent dimension mismatch during inference
    for feature in encoded_df.columns:
        if feature in INFDATA_FRAME.columns:
            encoded_df[feature] = INFDATA_FRAME[feature]
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
    
    encoded_df = encoded_df.drop(['app_complete_flag'], axis=1)
    
    
    conn = sqlite3.connect(DB_FILE_NAME_INF)
    encoded_df.to_sql(name="features", con=conn, if_exists='replace', index=False)
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
        **NOTE : You can modify the encode_featues function used in heart disease's inference
        pipeline for this.

    OUTPUT
        1. Save the encoded features in a table - features

    SAMPLE USAGE
        encode_features()
    '''

###############################################################################
# Define the function to load the model from mlflow model registry
# ##############################################################################

def get_models_prediction():
    '''
    This function loads the model which is in production from mlflow registry and 
    uses it to do prediction on the input dataset. Please note this function will load
    the latest version of the model present in the production stage. 

    INPUTS
        db_file_name : Name of the database file
        db_path : path where the db file should be
        model from mlflow model registry
        model name: name of the model to be loaded
        stage: stage from which the model needs to be loaded i.e. production


    OUTPUT
        Store the predicted values along with input data into a table

    SAMPLE USAGE
        load_model()
    '''

###############################################################################
# Define the function to check the distribution of output column
# ##############################################################################

def prediction_ratio_check():
    '''
    This function calculates the % of 1 and 0 predicted by the model and  
    and writes it to a file named 'prediction_distribution.txt'.This file 
    should be created in the ~/airflow/dags/Lead_scoring_inference_pipeline 
    folder. 
    This helps us to monitor if there is any drift observed in the predictions 
    from our model at an overall level. This would determine our decision on 
    when to retrain our model.
    

    INPUTS
        db_file_name : Name of the database file
        db_path : path where the db file should be

    OUTPUT
        Write the output of the monitoring check in prediction_distribution.txt with 
        timestamp.

    SAMPLE USAGE
        prediction_col_check()
    '''
###############################################################################
# Define the function to check the columns of input features
# ##############################################################################
   

def input_features_check():
    '''
    This function checks whether all the input columns are present in our new
    data. This ensures the prediction pipeline doesn't break because of change in
    columns in input data.

    INPUTS
        db_file_name : Name of the database file
        db_path : path where the db file should be
        ONE_HOT_ENCODED_FEATURES: List of all the features which need to be present
        in our input data.

    OUTPUT
        It writes the output in a log file based on whether all the columns are present
        or not.
        1. If all the input columns are present then it logs - 'All the models input are present'
        2. Else it logs 'Some of the models inputs are missing'

    SAMPLE USAGE
        input_col_check()
    '''
   