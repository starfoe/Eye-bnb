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

def feature_extraction(feature_name = 'gist', img_array):
    '''
    Function: extraction multiple features from an image
    Input:
        feature_name: <string> 'gist','RGB','nn'
        img_array: <array> an array converted image
    Output: array or array-like feature
    '''
    if feature_name = 'gist':
        return gist.extract(im)
    else:
        return [] #to be extended

def feature_distance(metric ='cosine',feature1,feature2):
    '''
    Function:calculate feature distance of feature1 and feature 2
    Input:
        feature1,feature2: <vector-like> two features
        metric: <string> 'cosine','cor','euclidean' 
    Output:
        dis:<float> the distance of the two features based on the metric
    
    
    

    