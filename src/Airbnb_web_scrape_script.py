import sys
import json
import requests
import time
import argparse
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from urllib.request import urlretrieve 
import pymongo
import pandas as pd
import numpy as np
import random

from Airbnb_Scraping_tools import *

    
if __name__ == '__main__':
    ## Create a log file for scraping
    logfile_name = 'DataSet/'+folder+'/log_file.txt'
    apt_infos = {}
    apt_jses = {}    
    
    ## Load in listing file downloaded from "http://insideairbnb.com/get-the-data.html"
    try:
        folder = 'Austin-Texas-United States'
        file_tmp = pd.read_csv('DataSet/'+folder+'/listings.csv.gz',compression = 'gzip')
        print('Total number of apartments in ' + folder +" is: {}".format(len(file_tmp)))
    else:
        raise IOError(f"Cannot open the file {folder}")
    
    for i in range(len(file_tmp)):
        if i % 100 == 0:
            print(i)
            
        url = file_tmp.loc[i,'listing_url']
        apt_id = file_tmp.loc[i,'id']
        apt_name = file_tmp.loc[i,'name']
        try:
            return_parsed = parse_each_webpage(url)
        except CannotOpenUrl:
            with open(logfile_name,"w") as f:
                f.writelines('Cannot open '+ str(i)+ ' url.\t' + 'Id: '+ str(apt_id) + ' |  Url: '+ url)                        
            print('Failed to get access to URL, sleep for 20 secs ')
            time.sleep(20)
            return_parsed = parse_each_webpage(url)
        finally:
            scrape_info,ori_json = return_parsed[0],return_parsed[1]
            dict_apt = {'apt_name':apt_name,'url' : url, 'info': scrape_info}
            apt_jses.update({str(apt_id):ori_json})
            apt_infos.update({str(apt_id):dict_apt})
            # Save scraped data to files every 1000 times
            if i % 1000 == 0 and i != 0:
                filename = "DataSet/"+folder+"/ori_json_"+str(i)
                with open(filename,"w") as f:
                    json.dump(apt_jses,f)
                print("Wrote  down"+str(i)+"json file")
                jses = {}
            time.sleep(random.random()+2)
            
    #Save the last piece of scraped data to a file
    filename = "DataSet/"+folder+"//webscrapted"    
    with open(filename,"w") as f:
        json.dump(apt_infos,f)
        
        
    