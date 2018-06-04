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
from eyebnb_ec2.image_web_tools import *

import pymongo as pm
import boto3
import json
import sys
from pymongo import MongoClient

def load_features(path):
    df_file = pd.read_pickle(path)
    apt_name = df_file['apt'].values
    img_file_path = df_file['full_filename'].values
    feature_matrix = df_file[list(range(960))].values
    return feature_matrix,img_file_path,apt_name

def load_features_all(path):
    df_file = pd.read_pickle(path)
    apt_name = df_file['apt']
    img_file_path = df_file['full_filename']
    columns_gist = [str(x)+'_x' for x in range(960)]
    columns_hsv = [str(y)+'_y' for y in range(270)]
    columns_com = columns_gist+columns_hsv
    feature_matrix = df_file[columns_com].values    
    return feature_matrix,img_file_path,apt_name

"""
The following code serves for mongoDB interaction which is running on an EC2 instance
Currently it is shutdown and a json file which contains the same data is used here
"""

# def web_query(url_input,feature_path,return_top = 20):
#     feature_matrix,img_file_path,apt_id = load_features_all(feature_path)

#     response = req.get(url_input)

#     img_tmp = Image.open(BytesIO(response.content))
#     im = np.asarray(img_tmp.resize((600,400)))

    
#     feature_input = feature_extraction(im,feature_name = 'all')
#     print('feature_extracted successfully')

#     selected_index =  find_closest_img(feature_input,feature_matrix,{},return_top)[0]
#     selected_apt_id = apt_id[selected_index].values
#     selected_image_path = img_file_path[selected_index].values
    
#     ######Temporary searching from Json File#######
#     conn = MongoClient('35.164.239.112', 27017)
#     db = conn['eyebnb_1']
#     books = db.eye_1
#     #####Extract data from the fake database#######
    
#     for i,idx in enumerate(selected_apt_id):
#         tmp = {}
#         x =  books.find_one({'Id_1':idx})
#         tmp['apt_name'] = x['apt_name']
#         tmp['canonical_url'] =  x['info']['canonical_url']
#         tmp['room_type'] = x['info']['room_type']
#         tmp['room_capacity'] = x['info']['room_capacity']
#         tmp['host_about'] = x['info']['host_about']
#         tmp['overall_rating']=x['info']['overall_rating']
#         tmp['room_type'] = x['info']['room_type']
# #         print('current file name is {}'.format(selected_image_path[i]))
#         tmp['which_one'] = list(selected_image_path)[i]
#         yield tmp
    


def web_query(url_input,feature_path,return_top = 20):
    feature_matrix,img_file_path,apt_id = load_features_all(feature_path)

    response = req.get(url_input)

    img_tmp = Image.open(BytesIO(response.content))
    im = np.asarray(img_tmp.resize((600,400)))

    
    feature_input = feature_extraction(im,feature_name = 'all')
    print('feature_extracted successfully')

    selected_index =  find_closest_img(feature_input,feature_matrix,{},return_top)[0]
    selected_apt_id = apt_id[selected_index].values
    selected_image_path = img_file_path[selected_index].values
    
    ######Temporary searching from Json File#######
    bucket_name = "chen-gal-test"
    s3 = boto3.client("s3")
    database_json_short = 'AirbnbData/Boston-Massachusetts-US/ws_data/webscrapted.json'
    response = s3.get_object(Bucket=bucket_name,
                             Key=database_json_short)
    fake_database= json.loads(response['Body'].read())
    #####Extract data from the fake database#######
    
    for i,idx in enumerate(selected_apt_id):
        tmp = {}
        x = fake_database[str(idx)]
        tmp['apt_name'] = x['apt_name']
        tmp['canonical_url'] = x['info']['canonical_url']
        tmp['room_type'] = x['info']['room_type']
        tmp['room_capacity'] = x['info']['room_capacity']
        tmp['host_about'] = x['info']['host_about']
        tmp['overall_rating']=x['info']['overall_rating']
        tmp['room_type'] = x['info']['room_type']
#         print('current file name is {}'.format(selected_image_path[i]))
        tmp['which_one'] = list(selected_image_path)[i]
        yield tmp
    
#     result = json.dumps(fake_result)

    ######
    #if there are duplicated aparts in the recommending results, then keep only one of them    
    ######
#     return result
    
    
    
    
     
    
    