import json
import os
import pandas as pd
import numpy as np



if __name__ == '__main__':
    """
    Load in two kind of features and combine together
    Run Gist_feature_extraction_script.py and HSV_feature_extraction_script.py beforehand to get two set of features 
    """
    
    feature_folder = '../'+'features/'+ area 
    df_feature_gist = pd.read_pickle(feature_folder+'/Boston_gist_new_all.pickle')
    df_feature_HSV = pd.read_pickle(feature_folder+'/Boston_HSV_new_all.pickle')
    
    file1 = df_feature_gist['full_filename'].values
    file2 = df_feature_HSV['full_filename'].values
    
    x = list(range(960))
    columns_1 = [str(i)+'_x' for i in x ]
    y = list(range(270))
    columns_2 = [str(i)+'_y' for i in y ]

    combined_features = pd.merge(df_feature_gist,df_feature_HSV, on = ['full_filename'])
    combined_features_new = combined_features.drop(['apt_x','short_filename_x'],axis=1)
    combined_features_new.to_pickle('../'+'features/'+ area+'/'+'Boston_feature_new_all.pickle')
    
    
    