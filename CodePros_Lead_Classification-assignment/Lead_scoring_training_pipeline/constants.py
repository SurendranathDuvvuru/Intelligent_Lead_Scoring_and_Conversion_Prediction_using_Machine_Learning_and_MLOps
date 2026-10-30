DB_PATH = '/home/Assignment/02_training_pipeline/notebooks/'
DB_FILE_NAME_NOTE = 'lead_scoring_data_cleaning.db'
DB_FILE_NAME_EXP = 'lead_scoring_model_experimentation.db'

EFDB_PATH = '/home/Assignment/02_training_pipeline/notebooks/Data/'
EFDATA_DIRECTORY = 'cleaned_data.csv'
EFDB_FILE_NAME = ''

FEAT_TAB_NAME = 'features'
TARG_TAB_NAME = 'target'

#DB_FILE_MLFLOW = 

#TRACKING_URI = 
#EXPERIMENT = 


# model config imported from pycaret experimentation
#model_config = 

# list of the features that needs to be there in the final encoded dataframe
#ONE_HOT_ENCODED_FEATURES = 
# list of features that need to be one-hot encoded
FEATURES_TO_ENCODE = ['total_leads_droppped', 'city_tier', 'referred_lead', 'app_complete_flag', 'first_platform_c', 'first_utm_medium_c', 'first_utm_source_c']
