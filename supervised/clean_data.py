# -*- coding: utf-8 -*-
"""
Created on Fri Feb 22 14:48:48 2019

@author: Mei
"""
import sys
import numpy as np
import pandas as pd

def clean_data(df, feat_info):
    '''Processes MAILOUT data
        - Converts missing values to np.nan using loaded features table
        - Drops unwanted columns and rows
        - Perfroms feature enginerring
    
    Args:
        df (pd.Dataframe): data to be cleaned
        feat_info (pd.Dataframe): feature information
        row_threshold (int): max. number of missing values allowed for a row
    
    Returns:
        cleaned_df (pd.Dataframe): cleaned rows
        dropped_df (pd.Dataframe): dropped rows
    '''

    clean_df = df.copy()
    
    # Convert missing values to Nans
    missing_values = pd.Series(feat_info['missing_or_unknown'].values, index=feat_info.index).to_dict()
    clean_df[clean_df.isin(missing_values)] = np.nan
      
    to_drop = ['AGER_TYP', 'ALTER_HH', 'ALTER_KIND1', 'ALTER_KIND2', 'ALTER_KIND3',
       'ALTER_KIND4', 'EXTSEL992', 'GEBURTSJAHR', 'HH_DELTA_FLAG',
       'KBA05_BAUMAX', 'KK_KUNDENTYP', 'KKK', 'REGIOTYP', 'TITEL_KZ',
       'W_KEIT_KIND_HH']
    
    clean_df = clean_df.drop(to_drop, axis='columns')
        
    # Feature Re-encoding and Engineering
    # Recode 10's to 0 for D19 columns that need it
    recode = ['D19_BANKEN_DATUM', 'D19_BANKEN_OFFLINE_DATUM',
       'D19_BANKEN_ONLINE_DATUM', 'D19_GESAMT_DATUM',
       'D19_GESAMT_OFFLINE_DATUM', 'D19_GESAMT_ONLINE_DATUM',
       'D19_TELKO_DATUM', 'D19_TELKO_OFFLINE_DATUM',
       'D19_TELKO_ONLINE_DATUM', 'D19_VERSAND_DATUM',
       'D19_VERSAND_OFFLINE_DATUM', 'D19_VERSAND_ONLINE_DATUM',
       'D19_VERSI_DATUM', 'D19_VERSI_OFFLINE_DATUM',
       'D19_VERSI_ONLINE_DATUM']
    clean_df[recode] = clean_df[recode].replace(10, 0)
    
    # Drop all fine scale variables in favor of the rough scale version
    drop = ['CAMEO_DEU_2015', 'LP_FAMILIE_FEIN', 'LP_STATUS_FEIN']
    clean_df.drop(drop, axis=1, inplace=True)
    
    # convert CAMEO_DEUG_2015 from string to float
    clean_df['CAMEO_DEUG_2015'] = clean_df['CAMEO_DEUG_2015'].astype(float)
    
    # Re-encode categorical variable(s) to be kept in the analysis
    recoded = pd.get_dummies(clean_df['OST_WEST_KZ'])
    clean_df.drop('OST_WEST_KZ', axis=1, inplace=True)
    clean_df = pd.concat([clean_df, recoded], axis=1)

    # Engineer new variables
    to_replace = {1:40, 2:40, 3:50, 4:50, 5:60, 6:60, 7:60, 8:70, 9:70, 10:80, 11:80, 12:80, 13:80, 14:90, 15:90}
    clean_df['decade'] = clean_df['PRAEGENDE_JUGENDJAHRE'].replace(to_replace)

    to_replace = {1:0, 2:1, 3:0, 4:1, 5:0, 6:1, 7:1, 8:0, 9:1, 10:0, 11:1, 12:0, 13:1, 14:0, 15:1}
    clean_df['movement'] = clean_df['PRAEGENDE_JUGENDJAHRE'].replace(to_replace)    

    clean_df['wealth'] = clean_df.CAMEO_INTL_2015[clean_df.CAMEO_INTL_2015.notnull()].map(lambda x: int(str(x)[0]))
    clean_df['life_stage'] = clean_df.CAMEO_INTL_2015[clean_df.CAMEO_INTL_2015.notnull()].map(lambda x: int(str(x)[1]))
    
    # Drop unneeded variables
    clean_df.drop(['PRAEGENDE_JUGENDJAHRE', 'CAMEO_INTL_2015',
                   'LP_LEBENSPHASE_GROB', 'LP_LEBENSPHASE_FEIN',
                   'LNR', 'D19_LETZTER_KAUF_BRANCHE', 'EINGEFUEGT_AM'], axis=1, inplace=True)

    # Return the cleaned dataframe and dropped rows.
    return clean_df

# Parse missing_or_known string into a list
def parse_missing(s):
    a = s[1:-1].split(',')
    return a

    
if __name__ == '__main__':
    '''Cleans and saves data to new files. New files will have "_clean"
    and "_dropped" appended to original data filename.
    
    Args:
        data_filepath (str): filepath to data
        features_filepath (str): filepath to feature information
    '''    
    data_filepath, features_filepath = sys.argv[1:]
    
    # Load data
    print('Loading data...')
    df = pd.read_csv(data_filepath, sep=';')

    # Load feature info
    feat_info = pd.read_csv('features.csv')
    feat_info.set_index('attribute', inplace=True)
    feat_info['missing_or_unknown'] = feat_info['missing_or_unknown'].apply(parse_missing)
    
    print('Cleaning data...')
    df_clean = clean_data(df, feat_info)
    
    print('Writing clean data...')
    filepath, ext = data_filepath.split('.')
    df_clean.to_csv(filepath+'_clean.csv', sep=';')
    