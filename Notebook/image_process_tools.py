from PIL import Image
import pylab as pl
import os
import math
from boto3 import client
import boto3
import pandas as pd
import numpy as np
import requests as req
from io import BytesIO
import gist



def image_show(datapath,nums = 6,startImg = 0, local = True, **kwargs):
    '''
        Function: show nums of images involved in datapath folder starting from start_image or speicified by "imagelist" argument 
        Datapath: the folder containing images that to be shown
        nums: number of images that are gonna be displayed
        start_img: the index of the first picture
        local: whether the image is an online image or saved locally(default). 
    '''
    fig_column = 4
    
    if 'imageList' in kwargs:
        image_list = kwargs['imageList']
        nums = min(nums,len(image_list)-startImg)       
    else:
        image_list = os.listdir(datapath)
        nums = min(nums,len(image_list)-startImg)    
    
    pl.figure(figsize = (fig_column*5,math.ceil(nums/fig_column)*5) )
    
    for i in range(nums):         
        pl.subplot(math.ceil(nums/fig_column),fig_column,i+1,title = image_list[startImg+i])
        print(datapath+image_list[startImg+i])
        if local:
            img = Image.open(datapath+image_list[startImg+i])        
            pl.axis('off')        
            pl.imshow(img)
        else:
            response = req.get(datapath+image_list[startImg+i])
            img = Image.open(BytesIO(response.content))
            pl.axis('off')        
            pl.imshow(img)
       
       

def gist_extraction(imgFolder,nums = 9,startImg = 0,local = False, **kwargs):
    '''
        Function: extract gist features for all the images in *imgFolder* or for *nums* of images starting from *startImg*
        Input:
            imgFolder: <string> file path of the image folder
            nums: <int> number of images that are gonna be displayed
            startImg: <int> the index of the first picture
            local:<bool> whether images are online or saved locally
            imageList:<list> a specific list of images
        Output: 
            featureX: <matrix> a matrix of size (nums,960) where each row represents an image feature
            nameList:<list> a list of image name in accordance to the feature matrix
    '''
    nameList = []
    featureX = np.zeros((1,960))
    
    if 'imageList' in kwargs:
        image_list = kwargs['imageList']    
        nums = min(nums,len(image_list)-startImg)
        startImg = 0
    else:
        image_list = os.listdir(datapath)
        nums = min(nums,len(image_list)-startImg)
    print("Processing {} images".format(nums))
    
    if local:    
        for i in range(startImg,startImg+nums):
            print("image {} is in processing".format(i))
            image_name = imgFolder+ image_list[i]
            im = np.array(Image.open(image_name))
            feature_for_i = gist.extract(im)
            featureX = np.concatenate((featureX,feature_for_i.reshape(1,-1)),axis = 0)
            nameList.append(image_name)
    else:
        for i in range(startImg,startImg+nums):
            print("image {} is in processing".format(i))
            image_name = imgFolder + image_list[i]
            print(image_name)
            try:
                response = req.get(image_name)
                im = np.array(Image.open(BytesIO(response.content)))
                feature_for_i = gist.extract(im)
                featureX = np.concatenate((featureX,feature_for_i.reshape(1,-1)),axis = 0)
                nameList.append(image_name)
            except:
                print('{} is error'.format(image_name))
                continue
    
    return featureX[1:,:], nameList       

def show_similar_images(X,threshold,imgList,limit = 30,local = True, reverse = False):
    '''
        Function: show pairs of images between which the similarity is greater or less than threshold
        Input:
            X: <matrix> N by N similarity matrix
            imgList:<list[string]> image names corresponding rows in X
            threshold: <float> only the pairs of images having similarities greater or less than the threshold will be shown
            limit:<int> number of images will be displayed
            reverse: <bool> greater or less (the default setting is greater than)
    '''
    index = np.argwhere(X < threshold) if reverse else np.argwhere((X > threshold)*(X < 1))
    index_small_tmp = index[index[:,0]<index[:,1]]   
    
    candidate_1d =  X[index_small_tmp[:,0],index_small_tmp[:,1]]
    nums_for_display = min(limit,len(index_small_tmp))
    
    index_small_sorted = np.argsort(candidate_1d)[::-1][0:nums_for_display] if not reverse \
                else np.argsort(candidate_1d)[0:nums_for_display]

        
    index_small = index_small_tmp[index_small_sorted]    
    
   
    pl.figure(figsize = (2*5,nums_for_display*5))
    
    for i in range(nums_for_display): 
        
        pl.subplot(nums_for_display,2,i*2+1,title = imgList[index_small[i,0]]+'\nSim:'+ \
                   str(round(X[index_small[i,0],index_small[i,1]],2)))
        if local:
            img = Image.open(imgList[index_small[i,0]])        
            pl.axis('off')        
            pl.imshow(img)

            pl.subplot(nums_for_display,2,i*2+2,title = imgList[index_small[i,1]]+'\nloc:'+\
                      str(index_small[i,:]))
            img = Image.open(imgList[index_small[i,1]])   
            pl.axis('off')
            pl.imshow(img)
        else:
            response = req.get(imgList[index_small[i,0]])
            img = Image.open(BytesIO(response.content))
            pl.axis('off')        
            pl.imshow(img)
            
            pl.subplot(nums_for_display,2,i*2+2,title = imgList[index_small[i,1]]+'\nloc:'+\
                      str(index_small[i,:]))
            response = req.get(imgList[index_small[i,1]])
            img = Image.open(BytesIO(response.content)) 
            pl.axis('off')
            pl.imshow(img)
            

        
def s3_list_files(bucket_name,prefix,layers):
    '''
        Function: find all the file names in a S3 bucket
        Input:
            bucket_name: <string> name of the bucket
            prefix:<string>  the specific file path in the bucket
            layers
        Output:<pd.df> a dataframe includes filenames and folders in the bucket
    '''
    s3_resource = boto3.resource('s3')
    bucket = s3_resource.Bucket(name=bucket_name)
    dict_parse = {}
    i = True
    for obj in bucket.objects.filter(Prefix=prefix):
        string = obj.key.split('/')
        if i:
            dict_parse['full_name'] = []
            dict_parse['full_name'].append(obj.key)            
            for x in range(1,layers):                
                dict_parse[x] = []
                dict_parse[x].append(string[-1*x])
            i = False
            
        for x in range(1,layers):            
            dict_parse['full_name'].append(obj.key)
            dict_parse[x].append(string[-1*x])  
            
    pd_return = pd.DataFrame(dict_parse)
    pd_return_1 = pd_return.drop(pd_return[pd_return[1]==''].index,axis=0)
    return pd_return_1

def feature_df_assembly(X,imgNameList,write_to_file = False, **kwargs):
    '''
        Function: assemble features and meta info into a dataframe and write to .csv file\
        Input:
            X:<array> feature matrix
            imgNameList:<list> name of the original images
            write_to_file:<bool> if true, the dataframe will be save to a csv file in the current work directory
            class_labels:<list> if known
        Output:
            dataframe
    '''
    if len(X) != len(imgNameList):
        raise Exception('imgNameList should have the same length as features')
    
    dict_tmp = {'features':X.tolist(),'img_names':imgNameList}
    df_return = pd.DataFrame(dict_tmp)
    
    if 'labels' in kwargs:
        labels = kwargs['labels']
        df_return['class_label'] = labels
    
    if write_to_file:
        df_return.to_csv(write_to_file)
    return df_return

def HSV_hist_extraction(imgFolder,nums = 9,startImg = 0,local = False, **kwargs):
    '''
        Function: extract gist features for all the images in *imgFolder* or for *nums* of images starting from *startImg*
        Input:
            imgFolder: <string> file path of the image folder
            nums: <int> number of images that are gonna be displayed
            startImg: <int> the index of the first picture
            local:<bool> whether images are online or saved locally
            imageList:<list> a specific list of images
        Output: 
            featureX: <matrix> a matrix of size (nums,960) where each row represents an image feature
            nameList:<list> a list of image name in accordance to the feature matrix
    '''
    nameList = []
    featureX = np.zeros((1,960))
    
    if 'imageList' in kwargs:
        image_list = kwargs['imageList']    
        nums = min(nums,len(image_list)-startImg)
        startImg = 0
    else:
        image_list = os.listdir(datapath)
        nums = min(nums,len(image_list)-startImg)
    print("Processing {} images".format(nums))
    
    if local:    
        for i in range(startImg,startImg+nums):
            print("image {} is in processing".format(i))
            image_name = imgFolder+ image_list[i]
            im = np.array(Image.open(image_name))
            feature_for_i = gist.extract(im)
            featureX = np.concatenate((featureX,feature_for_i.reshape(1,-1)),axis = 0)
            nameList.append(image_name)
    else:
        for i in range(startImg,startImg+nums):
            print("image {} is in processing".format(i))
            image_name = imgFolder + image_list[i]
            print(image_name)
            try:
                response = req.get(image_name)
                im = np.array(Image.open(BytesIO(response.content)))
                feature_for_i = gist.extract(im)
                featureX = np.concatenate((featureX,feature_for_i.reshape(1,-1)),axis = 0)
                nameList.append(image_name)
            except:
                print('{} is error'.format(image_name))
                continue
    
    return featureX[1:,:], nameList       

def hsv_hist_extract(img,bins=[90,90,90]):
    '''
    Function: extract HSV histogram feature from *img* with specified number of bins
    Input: 
        img: <Image>
        bins: number of bins for each channel
        output: <np.array> size of bins[0]+bins[1]+bins[2]
    '''
    hsv_image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    hist_1 = cv2.calcHist([hsv_image[:,:,0]],[0],None,[bins[0]],[0,181])
    hist_2 = cv2.calcHist([hsv_image[:,:,1]],[0],None,[bins[1]],[0,256])
    hist_3 = cv2.calcHist([hsv_image[:,:,2]],[0],None,[bins[2]],[0,256])
    hist_tmp = cv2.normalize(hist_1,hist_1,cv2.NORM_MINMAX,-1)
    hist_tmp = cv2.normalize(hist_2,hist_2,cv2.NORM_MINMAX,-1)
    hist_tmp = cv2.normalize(hist_3,hist_3,cv2.NORM_MINMAX,-1)
    return np.concatenate((hist_1,hist_2,hist_3),axis = 0)