from PIL import Image
# import pylab as pl
import os
import math
from boto3 import client
import boto3
import pandas as pd
import numpy as np
import requests as req
from io import BytesIO
import gist
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import cosine_distances

def feature_extraction(img_array,feature_name = 'gist'):
    '''
    Function: extraction multiple features from an image
    Input:
        feature_name: <string> 'gist','RGB','nn'
        img_array: <array> an array converted image
    Output: array or array-like feature
    '''
    if feature_name == 'gist':
        return gist.extract(img_array)
    else:
        return [] #to be extended

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
    
    distance_vector = cosine_similarity(featureX.reshape(1,-1),features_matrix)#can change to other similarity measurements
    percentile = [99,95,90,85,80,75,70,1]
    for perc in percentile:
        threshold = np.percentile(distance_vector,perc)
        # times 10 to make sure that there would be enough candidate images
        if len(np.argwhere(distance_vector > threshold)) > 10* n_selected:            
            break            
    index_filtered = np.argwhere(distance_vector > threshold)
    print('mask type is {}'.format(type(mask)))
#     current_mask_len = len(mask)
    
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

    