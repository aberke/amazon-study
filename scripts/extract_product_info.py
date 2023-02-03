#!/usr/bin/env python3
from multiprocessing import Lock
from scrapingbee import ScrapingBeeClient
from selectorlib import Extractor
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
from itertools import cycle
import requests 
from lxml.html import fromstring
import json 
import os

# output file for JSON of scraped product data
scraped_file = '../output/product_pages.jsonl'

product_info_file = '../output/product_info.jsonl'
# Create an Extractor by reading from the YAML file
e = Extractor.from_yaml_file('productSelector.yml')

lock = Lock()

def extract_product_info(data):
    product_info = e.extract(data['page_text'])
    product_info['asin'] = data['asin']
    with lock:
        with open(product_info_file, 'a') as f:
            f.write(json.dumps(product_info))
            f.write("\n")
    return product_info

if __name__ == "__main__":
    with open(scraped_file, 'r') as f:
        lines = f.readlines()
    r = process_map(extract_product_info, [json.loads(l) for l in lines], max_workers=12, chunksize=10)