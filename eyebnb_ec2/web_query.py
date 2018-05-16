import os
import json
import requests
import pymongo
import requests as req
import pandas as pd
import numpy as pd
import gist

from PIL import Image
from io import BytesIO
from sklearn.metrics.pairwise import cosine_similarity

def load_features(path):
    feature_matrix = np.loadtxt(path)
    apt_name = n
    
#     features_cf = pd.read_excel(path)
#     features = features_cf['features'].values
#     cleaned_feature = []
#     for i,x in enumerate(features):
#         tmp_cleaned = clean_feature_data(x)
#         if not tmp_cleaned:
#             break
#         else:
#             assert(len(tmp_cleaned)==960)
#             cleaned_feature.append(np.array(tmp_cleaned))
#     assert(len(cleaned_feature) == len(features_cf))
#     features_cf.drop('features',axis = 1)   
#     features_cf['features'] = cleaned_feature
#     return features_cf

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
    feature_matrix,apt_id,filepath = load_features(feature_path)
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
    
    
    
    
    
     
    
    