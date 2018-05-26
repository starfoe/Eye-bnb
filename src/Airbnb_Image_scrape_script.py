from PIL import Image
from io import BytesIO
import requests
import boto3
import time
import random
import json
import os
import pandas as pd

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

    return pd.DataFrame(dict_parse)


if __name__ == '__main__':
    """
        This script will parse all json files generate by Airbnb_web_scrape_script.py to get image urls of each apartment, scrape the images and save to *filename*. Alongside the scraping, *logfile_name* will record the process in case of unexpected breaking point
    """
##############################################
#Fetch the json files and parse out image urls 
##############################################

    bucket_name = "chen-gal-test"
    s3 = boto3.client("s3")
    remote_foler = 'AirbnbData/'
    folder = 'Seattle-washington-US'
    
    prefix = remote_foler+folder+'/'+'ws_data'
    json_df = s3_list_files(bucket_name,prefix,2)
    json_files = json_df.drop([0,1],axis = 0)    
    jsons_full = json_files['full_name'].values
    
    logfile_name = '../Logs/'+'logfile_image_'+folder+'.txt'
    print(f'Logfile name is {logfile_name}')
    
    for z in range(0,len(jsons_full)):

    response = s3.get_object(Bucket=bucket_name,
                             Key=jsons_full[z])
    apt_info = json.loads(response['Body'].read())

    i = 0
    num_of_aps = len(apt_info.keys())
    
    with open(logfile_name,'a') as f:
            f.write(f'---------------------Parsing file{jsons_full[z]} ')
    print(f'---------------------Parsing file{jsons_full[z]} ')
    print('Total number of apartments in file{} is {}'.format(jsons_full[z],len(apt_info)))

################
#Scraping images
################

    for j in range(0,num_of_aps):

        k = list(apt_info.keys())[j]
        v = apt_info[k]
        with open(logfile_name,'a') as f:
            f.write(f'---------------------\nApartment{j} | {k}')

        if len(v['info']) == 0:
            with open(logfile_name,'a') as f:
                    f.writelines('No image info for this apt \n')
            continue
        print(f"Processing {j} apartment---------------------------------------------------")    
        image_list = v['info']['photo_urls']
        print(f"Processing the image {k}...")
        print(f" Url: {v['url']}")
        
        for i,img_url in enumerate(image_list):

            try:
                r = requests.get(img_url,allow_redirects=True)
                image = Image.open(BytesIO(r.content))
                image_resized = image.resize((int(image.size[0]//1.2),int(image.size[1]//1.2)))
                filename = 'image/'+folder+ '/'+ k +'_'+str(i)+'.jpg'
                image_resized.save(filename)
                time.sleep(0.2+random.random())
                
            except:
                with open(logfile_name,'a') as f:
                    f.writelines(f'Cannot open {i} apt images!\n')
                    
        with open(logfile_name,'a') as f:
                    f.writelines(f'Download {i} images for the apt!\n')

    with open(logfile_name,'a') as f:
        f.writelines(f'Downloading Finished!\n')

        
    

