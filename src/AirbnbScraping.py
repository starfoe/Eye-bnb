import sys
import json
import requests
import time
import argparse
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from urllib.request import urlretrieve 
import pymongo

def parse_url(