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
import cv2

def feature_extraction(img_array,feature_name = 'all'):
    '''
    Function: extraction multiple features from an image
    Input:
        feature_name: <string> 'gist','RGB','nn'
        img_array: <array> an array converted image
    Output: array or array-like feature
    '''
    if feature_name == 'gist':
        return gist.extract(img_array)
    elif feature_name == 'HSV':
        return hsv_hist_extract(img_array)
    elif feature_name == 'all':
        gist_feature = gist.extract(img_array)
        hsv_feature = hsv_hist_extract(img_array)
        return np.concatenate((gist_feature,hsv_feature[:,0]),axis = 0)
    else:
        raise ValueError("Wrong feature type!")

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
#     percentile = [30]
    for perc in percentile:
        threshold = np.percentile(distance_vector,perc)
        # times 10 to make sure that there would be enough candidate images
        if len(np.argwhere(distance_vector > threshold)) > 10* n_selected:            
            break            
    index_filtered = np.argwhere(distance_vector > threshold)
    print('mask type is {}'.format(type(mask)))
#     current_mask_len = len(mask)
    
    rounds = 20
    while(rounds > 0):
        candidate_small = distance_vector[index_filtered[:,0],index_filtered[:,1]]
        top_similar = np.argsort(candidate_small)[::-1][0:n_selected+len(mask)]
#         top_similar = np.argsort(candidate_small)[0:n_selected+len(mask)]
        current_selected_index = [x for x in index_filtered[top_similar][:,1] \
                                  if x not in mask]
        assert(len(current_selected_index) == n_selected)
        current_feature_matrix = features_matrix[current_selected_index]
        validation_dist = cosine_similarity(current_feature_matrix)

        duplicated_index_tmp = np.argwhere(validation_dist > 0.99)
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

def hsv_hist_extract(img,bins=[90,90,90]):
    '''
    Function: extract HSV histogram feature from *img* with specified number of bins
    Input: 
        img: <np.array>
        bins: number of bins for each channel
        output: <np.array> size of bins[0]+bins[1]+bins[2]
    '''
    try:
        hsv_image = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        hist_1 = cv2.calcHist([hsv_image[:,:,0]],[0],None,[bins[0]],[0,181])
        hist_2 = cv2.calcHist([hsv_image[:,:,1]],[0],None,[bins[1]],[0,256])
        hist_3 = cv2.calcHist([hsv_image[:,:,2]],[0],None,[bins[2]],[0,256])
        hist_tmp = cv2.normalize(hist_1,hist_1,cv2.NORM_MINMAX,-1)
        hist_tmp = cv2.normalize(hist_2,hist_2,cv2.NORM_MINMAX,-1)
        hist_tmp = cv2.normalize(hist_3,hist_3,cv2.NORM_MINMAX,-1)
        return np.concatenate((hist_1,hist_2,hist_3),axis = 0)
    except:
        raise IOError(f'faile to open the input image')
                          
        


    