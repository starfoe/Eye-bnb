from PIL import Image
import pylab as pl
import os
import math

def image_show(datapath,nums = 6,startImg = 0, **kwargs):
    '''
        Function: show nums of images involved in datapath folder starting from start_image or speicified by "imagelist" argument 
        Datapath: the folder containing images that to be shown
        nums: number of images that are gonna be displayed
        start_img: the index of the first picture
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
        img = Image.open(datapath+image_list[startImg+i])        
        pl.axis('off')        
        pl.imshow(img)

def gist_extraction(imgFolder,nums = 9,startImg = 0, **kwargs):
    '''
        Function: extract gist features for all the images in *imgFolder* or for *nums* of images starting from *startImg*
        Input:
            imgFolder: <string> file path of the image folder
            nums: <int> number of images that are gonna be displayed
            startImg: <int> the index of the first picture
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
        
    for i in range(startImg,startImg+nums):
        image_name = imgFolder+ image_list[i]
        im = np.array(Image.open(image_name))
        feature_for_i = gist.extract(im)
        featureX = np.concatenate((featureX,feature_for_i.reshape(1,-1)),axis = 0)
        nameList.append(image_name)
    
    return featureX[1:,:], nameList       

def show_similar_images(X,threshold,imgList,limit = 30,reverse = False):
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
        
        img = Image.open(imgList[index_small[i,0]])        
        pl.axis('off')        
        pl.imshow(img)
        
        pl.subplot(nums_for_display,2,i*2+2,title = imgList[index_small[i,1]]+'\nloc:'+\
                  str(index_small[i,:]))
        img = Image.open(imgList[index_small[i,1]])   
        pl.axis('off')
        pl.imshow(img)