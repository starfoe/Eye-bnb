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

def request_url( url, retries=3 ):
    """
    GET a page from url with a number of retries and exponential backoff.
    """
    print("request_url:{}".format(url))
    r = None
    wait = 2
    for i in range( retries ):
        r = requests.get( url )
        if r.status_code >= 400:
            print( "HTTP error: %d %s" % (r.status_code, r.reason) )
            print( r.text )            
            # exponential backoff
            time.sleep( wait )
            wait *= 2
        else:
            break
    if r == None:
        raise CannotOpenUrl
    else:
        return r 
    
def parse_urls_single_page(soup):
    '''
    Input: BeautifulSoup obj
    Output:list of bnb apartments webpages
    '''
    meta_info = {}
    taglist = soup.find_all('a', attrs={'class': '_15ns6vh'}) 
    for tag in taglist:
        sub_dict = {}        
        sub_dict['href'] = tag.get('href')        
        sub_dict['name'] = tag.select('div._1rths372')[0].get_text() 
        sub_dict['review_counts'] = int(tag.select('span._ulku2jm')[0].get_text())
        meta_info[tag.get('target')] = sub_dict
    return meta_info

def get_bootstrap_data_for_hypernova_key( body, hypernova_key ):
    """
    Extract bootstrap JSON data from a page body.
    No idea what hypernova is, but it sure requires some useful JSON.
    """
    soup = BeautifulSoup( body, "html.parser" )
    for tag in soup.find_all( "script", attrs={ "data-hypernova-key" : hypernova_key } ):
        s = tag.string
        if "bootstrapData" in s:
            # HACK! remove html comment just by truncating string.
            # will need to change if sting in html changes
            return json.loads( s[4:-3] )
        

def parse_each_webpage(page_url):
    """
    Extract bootstrap JSON data from a page body and parse it. Get desired information and return them in a dictionary
    """
    try:
        r = request_url(page_url)
    except CannotOpenUrl:
        raise CannotOpenUrl
    else:
        buf = r.text
        page_data = get_bootstrap_data_for_hypernova_key( buf, "spaspabundlejs" )
    
    try:
    #get photos
        photos = page_data['bootstrapData']['reduxData']['homePDP']['listingInfo']\
                                                        ['listing']['photos']
        photo_urls = []
        for pho in photos:
            if 'large' in pho:
                photo_urls.append(pho['large'])
            else:
                photo_urls.append(pho['large_cover'])


        #get Id & Canonical url & Room_type
        Id = page_data['bootstrapData']['reduxData']['homePDP']['listingInfo']['listingId'] 
        canonical_url = page_data['bootstrapData']['canonical_url']
        room_type = page_data['bootstrapData']['reduxData']['homePDP']['listingInfo']\
                ['listing']['room_type_category']
        room_capacity = page_data['bootstrapData']['reduxData']['homePDP']['listingInfo']\
                ['listing']['person_capacity']

        #get location info
        localized_city = page_data['bootstrapData']['reduxData']['homePDP']['listingInfo']\
                    ['listing']['localized_city']
        country_code = page_data['bootstrapData']['reduxData']['homePDP']['listingInfo']\
                    ['listing']['country_code']
        coordinate = [page_data['bootstrapData']['reduxData']['homePDP']['listingInfo']\
                    ['listing']['lat'],page_data['bootstrapData']['reduxData']['homePDP']['listingInfo']\
                    ['listing']['lng']]

        #get host Info
        host_about = page_data['bootstrapData']['reduxData']['homePDP']['listingInfo']['listing']\
                ['primary_host']['about']
        host_name = page_data['bootstrapData']['reduxData']['homePDP']['listingInfo']\
                ['listing']['primary_host']['host_name']
        host_id = page_data['bootstrapData']['reduxData']['homePDP']['listingInfo']\
                ['listing']['primary_host']['id']
        host_member_since = page_data['bootstrapData']['reduxData']['homePDP']['listingInfo']\
                ['listing']['primary_host']['member_since']
        host_member_profile = page_data['bootstrapData']['reduxData']['homePDP']['listingInfo']\
                ['listing']['primary_host']['profile_path']

        #get overal rating
        overall_rating = page_data['bootstrapData']['reduxData']['homePDP']['listingInfo']\
                ['listing']['star_rating']
        review_highlight = page_data['bootstrapData']['reduxData']['homePDP']['listingInfo']\
                ['listing']['review_highlight']


        #form up returns
        info_collected = {
                            'id':Id,
                            'canonical_url':canonical_url,
                            'room_type':room_type,
                            'room_capacity':room_capacity,
                            'localized_city':localized_city,
                            'country_code':country_code,
                            'coordinate':coordinate,
                            'host_about':host_about,
                            'host_name':host_name,
                            'host_id':host_id,
                            'host_member_since':host_member_since,
                            'host_member_profile':host_member_profile,
                            'overall_rating':overall_rating,
                            'review_highlight':review_highlight, 
                            'photo_urls':photo_urls
                    }
    except:
        return [], page_data
            
    return info_collected, page_data
       
    
    
    