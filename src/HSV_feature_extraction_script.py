from PIL import Image
from io import BytesIO
from boto3 import client
from image_process_tools import *
import boto3
import time
import random
import json
import os
import pandas as pd
import random
import requests as req
import numpy as np
import gist
import cv2
"""
This script will load in images saved on S3 bucket with "prefix", extract gist feature from each of the images and save the feature file to *feature_folder* in pickle format. A log file will be generated to record the feature extraction process and saved to *logfile_name*
"""
if __name__ == '__main__':
    area = 'Boston-Massachusetts-US/'
    bucket_name = "chen-gal-test"
    
    prefix = "AirbnbImages/"+area
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(name=bucket_name)
    images_valid = list(bucket.objects.filter(Prefix=prefix))
    
    filenames = []
    apt_list = []
    full_filenames = []
    counter = 0
    featureX = np.zeros((1,270))

    logfile_name = '../Logs/HSV_feature_extraction_Boston-Massachusetts.txt'
    feature_folder = '../'+'features/'+ area + 'HSV/'
    
    if not os.path.exists(feature_folder):
            os.makedirs(feature_folder)
   

    for obj in images_valid[1:]:
    count += 1
    print("Processing image {} of {}\n ,{}..................".format(counter,len(images_valid),obj.key))
    string = obj.key.split('/')  
    
    try:
        #Change this part if you are using your own s3 bucket
        full_path_name = 'https://s3-us-west-2.amazonaws.com/'\
                                +bucket_name+'/'+ str(obj.key)         
        response = req.get(full_path_name)
        img_temp = np.array(Image.open(BytesIO(response.content)))
        feature_tmp = hsv_hist_extract(img_temp,count)
        
    except:
        print('Error at img {}'.format(obj.key))
        with open(logfile_name,'a') as f:
            f.write('!!!!!!Failed at image {} ||{}\n'.format(counter,full_path_name) )       
        continue
        
    else:
        counter += 1
        full_filenames.append(full_path_name)
        apt_list.append(string[-1].split('_')[-2])
        filenames.append(string[-1])
        featureX = np.concatenate((featureX,feature_tmp.reshape(1,-1)),axis = 0)
        
        with open(logfile_name,'a') as f:
            f.write('---------------------\n \
                            successfully extracted the feature of image {} ||{}'.format(counter,full_path_name) )
       
    if counter % 5000 == 0:
        columns1 = list(range(featureX.shape[1]))
        df_return = pd.DataFrame(featureX[1:,:],columns = columns1)
        
        df_return['apt'] = apt_list
        df_return['full_filename'] = full_filenames
        df_return['filename'] = filenames

        if not os.path.exists(feature_folder):
            os.makedirs(feature_folder)        
        filename = feature_folder + 'featureture_'+str(counter)+'.pickle'
        df_return.to_pickle(filename)
        filenames,apt_list,full_filenames = [],[],[]
        featureX = np.zeros((1,270))
             
    columns1 = list(range(featureX.shape[1]))
    df_return = pd.DataFrame(featureX[1:,:],columns = columns1)

    df_return['apt'] = apt_list
    df_return['full_filename'] = full_filenames
    df_return['filename'] = filenames
    filename = feature_folder + 'featureure_'+str(counter)+'.pickle'
    df_return.to_pickle(filename)
    
    feature_folder = '../'+'features/'+ area #set it to the folder where pickle files save
    feature_files = os.listdir(feature_folder)
    
    dfs = []
    for file in feature_files:
        if os.path.splitext(file)[1] == '.pickle':
            dfs.append(pd.read_pickle(feature_folder+file))
    
    df_feature_hsv = pd.concat(dfs)
    
    # Change the file name if need
    df_feature_hsv.to_pickle(feature_folder+'Boston_hsv_new_all.pickle')
