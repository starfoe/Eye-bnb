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
    fig_column = 3
    
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
        imshow(img)