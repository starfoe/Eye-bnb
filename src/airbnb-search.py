#!/usr/bin/env python 

#########################
# airbnb-search.py
#########################
# by prehensile, 18/07/17
#########################
# Crawl airbnb search results (descriptions and reviews) for keywords.
# A quick, dirty and brittle set of hacks.
# Very likely to break the next time anything changes in airbnb's HTML. 
# Essentially, if it works for you, be pleasantly surprised.
##########################
# Written for python 2.7
# Requires:
#  requests
#  http://docs.python-requests.org/en/master/
#  beautifulsoup
#  https://www.crummy.com/software/BeautifulSoup/bs4/doc/
##########################

import sys
import json
import requests
import time
import argparse
from urllib.parse import urlparse
from bs4 import BeautifulSoup


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
            print_error( "HTTP error: %d %s" % (r.status_code, r.reason) )
            print_error( r.text )
            
            # exponential backoff
            time.sleep( wait )
            wait *= 2
        else:
            break
    return r 


def print_error( message ):
    """
    Print an error to stderr.
    """
    print(message.encode('utf-8'), file=sys.stderr)
#     print >> sys.stderr, message.encode('utf-8')


def room_url_for_id( room_id, airbnb_host="www.airbnb.com" ):
    """
    Construct an airbnb url for a listing with room_id.
    """
    return "https://%s/rooms/%d" % (airbnb_host, room_id)


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


def fetch_listing_data( room_id, airbnb_host="www.airbnb.com" ):
    """
    Fetch a listing page and extract embedded JSON representation.
    """
    room_url = room_url_for_id( room_id, airbnb_host=airbnb_host )
    r = request_url( room_url )
    return get_bootstrap_data_for_hypernova_key( r.text, "p3indexbundlejs" )


def get_context( text, term, n ):
    """
    Return the first occurence of term in text with n characters either side.
    """
    idx = text.index( term )
    start = max( 0, idx-n )
    end = min( len(text), idx+len(term)+n )
    return text[start:end]


def search_text_for_terms( text, search_terms ):
    """
    Search some text for a set of search_terms.
    """
    has_hits = False
    for search_term in search_terms:
        if search_term in text:
            has_hits = True
            print(">> Found search term: {}".format(search_term))
            # print text
            context = get_context( text, search_term, 30 )
            print (">>> ...{}...".format(context))
    return has_hits


def search_reviews( listing_data, search_terms ):
    """
    Search through reviews contained in listing_data for search_terms.
    """
    has_hits = False
    try:
        reviews = listing_data[ "bootstrapData" ][ "listing" ][ "sorted_reviews" ]
        for review in reviews:
            comments = review[ "comments" ]
            if comments is not None:
                has_hits = has_hits or search_text_for_terms( comments, search_terms )
                # print comments.encode('utf-8')
    except Exception as e:
        print_error( repr(e) )
        print_error( repr( listing_data ).encode('utf-8') )

    return has_hits


def search_description( listing_data, search_terms ):
    """
    Search through description fields contained in listing_data for search_terms.
    """
    has_hits = False
    try:
        sectioned_description = listing_data[ "bootstrapData" ][ "listing" ][ "sectioned_description" ]
        for k in sectioned_description:
            section = sectioned_description[k]
            if section is not None:
                try:
                    has_hits = has_hits or search_text_for_terms( section, search_terms )
                    # print section.encode('utf-8')
                except Exception as e:
                    print_error( repr(e) )
                    print_error( section.encode('utf-8') )
    except Exception as e:
        print_error( repr(e) )
        print_error( repr( listing_data ).encode('utf-8') )
    return has_hits


def parse_args():
    """
    Parse commandline args using argparse.
    """
    parser = argparse.ArgumentParser(
        description='Crawl airbnb search results (descriptions and reviews) for keywords.'
    )
    parser.add_argument(
        'keywords',
        nargs = '+',
        help = 'Keywords to search for in listings.',
        default = [ "kids", "baby", "cot", "babies" ]
    )
    parser.add_argument(
        '--search-url',
        "-u",
        help = 'URL for an airbnb search. For example: https://www.airbnb.com/s/New-York--NY--United-States',
        default = 'https://www.airbnb.com/s/New-York--NY--United-States'
    )
    return parser.parse_args()


if __name__ == '__main__':
    
    # parse commandline args
    args = parse_args()

    # set up some working vars
    search_terms = args.keywords
    print(args.keywords)
    base_url = args.search_url
    print(args.search_url)
    page_url = base_url
    host = urlparse(base_url).hostname
    i = 0
    items_offset = 0

    print("Crawling search results at{} for keywords:{}".format(base_url, ",".join(search_terms)))

    while True:

        print("> Fetch search page #{}: {}\n".format(i, page_url ))
        # fetch search page text
        r = request_url( page_url )
        buf = r.text

        # get page, section & listing data
        listings = None
        page_data = None

        try:
            # pull JSON data from page
            page_data = get_bootstrap_data_for_hypernova_key( buf, "spaspabundlejs" )
            x = page_data
            
            print(list(x))
            section = page_data["bootstrapData"]["reduxData"]["exploreTab"]["response"]["explore_tabs"][0]["sections"][0]
            listings = section["listings"]
            items_offset = page_data["bootstrapData"]["reduxData"]["exploreTab"]["response"]["explore_tabs"][0]["pagination_metadata"]["items_offset"]
        
        except Exception as e:
            print_error( repr(e) )
            if page_data is not None:
                print_error( page_data.encode( 'utf-8' ) )
            else:
                print_error( "HTTP response: %d %s" % (r.status_code, r.reason) )
                print_error( buf )

        if listings is not None:
            # cycle through listings
            for listing in listings:
                
                room_id = listing["listing"][ "id" ]
                
                listing_data = fetch_listing_data( room_id, airbnb_host=host )
                
                if search_description( listing_data, search_terms ):
                    print(">>>> Found search terms in description for room:{}".format(room_url_for_id(room_id, airbnb_host=host)))
                    print("\n")

                if search_reviews( listing_data, search_terms ):
                    print (">>>> Found search terms in reviews for room: {}".format(room_url_for_id(room_id, airbnb_host=host)))
                    print ("\n")

        # find link to next search page
        soup = BeautifulSoup( buf, "html.parser" )
        link_next = soup.find( "link", rel="next" )
        
        if link_next:
            page_url = link_next.get( "href" )
        
        elif i < items_offset:
            # HACK - if we fail to get next link, use items_offset to construct it
            page_url = "%s?section_offset=%d" % (base_url,i+1)
            print_error( "Failed to get next_link from page, constructed it: %s" % page_url )
        
        else:
            print_error( buf )
            break

        i += 1 

    print("Done!")
    
