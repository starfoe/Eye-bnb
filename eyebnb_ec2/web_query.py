import os
import json
import requests
import pymongo
import requests as req
import pandas as pd
import numpy as np
import gist
import boto3

from PIL import Image
from io import BytesIO
from sklearn.metrics.pairwise import cosine_similarity

def load_features(path):
    df_file = pd.read_pickle(path)
    apt_name = df_file['apt_id_1']
    img_file_path = df_file['full_file_name']
    feature_matrix = df_file[list(range(960))].values
    return feature_matrix,img_file_path,apt_name
    

def find_closest_img(featureX,features_matrix,mask = {}, n_selected = 20):
    '''
    Function: find top *n_selected* of apts based on image similarities
    Input:
        featureX: <array> an image feature
        feature_matrix: database image features
        n_selected: number of similar images
        mask: <set> customized image indice that need to be filtered out 
    Output:
        index:<int> index of images that are selected
    '''
   
    distance_vector = cosine_similarity(featureX,features_matrix)#can change to other similarity measurements
    percentile = [99,95,90,85,80,75,70,1]
    for perc in percentile:
        threshold = np.percentile(distance_vector,perc)
        # times 10 to make sure that there would be enough candidate images
        if len(np.argwhere(distance_vector > threshold)) > 10* n_selected:            
            break            
    index_filtered = np.argwhere(distance_vector > threshold)
    current_mask_len = len(mask)
    rounds = 10
    while(rounds > 0):
        candidate_small = distance_vector[index_filtered[:,0],index_filtered[:,1]]
        top_similar = np.argsort(candidate_small)[::-1][0:n_selected+len(mask)]
        current_selected_index = [x for x in index_filtered[top_similar][:,1] \
                                  if x not in mask]
        assert(len(current_selected_index) == n_selected)
        current_feature_matrix = features_matrix[current_selected_index]
        validation_dist = cosine_similarity(current_feature_matrix)

        duplicated_index_tmp = np.argwhere(validation_dist > 0.9999)
        duplicated_index = duplicated_index_tmp[np.argwhere(duplicated_index_tmp[:,0]\
                                                    <duplicated_index_tmp[:,1])[:,0]][:,1]
        if len(duplicated_index) == 0:
            break
            
        if len(mask) == 0:
            mask = set(np.array(current_selected_index)[duplicated_index])
        else:
            mask.update(np.array(current_selected_index)[duplicated_index])
        rounds -= 1
        
    return current_selected_index,mask 

def web_query(url_input,return_top = 20,feature_path):
    feature_matrix,img_file_path,apt_name = load_features(feature_path)
    try:
        response = req.get(url_input)
        im = np.array(Image.open(BytesIO(response.content)))
        feature_input = feature_extraction(feature_name = 'gist',im)
    except:
        break
        #raise error
    selected_index =  find_closest_img(feature_input,feature_matrix,return_top)[0]
    selected_apt_id = apt_id[selected_index]
    selected_image_path = filepath[selected_index]
    ######Temporary searching from Json File#######
    bucket_name = "chen-gal-test"
    s3 = boto3.client("s3")
    database_json_short = 'AirbnbData/Boston-Massachusetts-US/ws_data/webscrapted.json'
    response = s3.get_object(Bucket=bucket_name,
                             Key=database_json_short)
    fake_database= json.loads(response['Body'].read())
    #####Extract data from the fake database#######
    
    ######
    #if there are duplicated aparts in the recommending results, then keep only one of them    
    ######
    return selected_apt_id,selected_image_path
    
    
    
    
     
    
    