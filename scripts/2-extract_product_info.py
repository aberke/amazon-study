#!/usr/bin/env python3
from selectorlib import Extractor
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import json 
import glob
import os

import config


e = Extractor.from_yaml_file('productSelector.yml')

errors = []

def extract_and_write_chunk_product_info(chunk_file):
    chunk_id = chunk_file.split('/')[-1].split('.')[0]
    print(f"Extracting product info from chunk {chunk_id}")
    with open(chunk_file, 'r') as f:
        lines = f.readlines()
    print(f"Found {len(lines)} lines in chunk {chunk_id}")
    products = []
    for l in lines:
        data = {}
        try:
            page_info = json.loads(l)
            data = e.extract(page_info['page_text'])
            data['asin'] = page_info['asin']
            data['chunk'] = chunk_id
        except Exception as err:
            errors.append({
                'chunk': chunk_id,
                'asin': page_info['asin'],
                'error': str(err)
            })
            continue
        products.append(data)
    print(f"Found {len(products)} products in chunk {chunk_id}")
    with open(config.PRODUCT_INFO_PATH_TEMPLATE.format(chunk_id), 'w+') as f:
        f.write(json.dumps(products))

    print(f"Found {len(errors)} errors in chunk {chunk_id}")
    with open(config.PRODUCT_INFO_ERRORS_PATH, 'w+') as f:
        f.write(json.dumps(errors))

if __name__ == "__main__":
    # Create an Extractor by reading from the YAML file
    chunk_files = glob.glob(config.SCRAPED_PAGE_PATH_TEMPLATE.format('*'))
    print(f"Found chunks {chunk_files}")
    os.makedirs(config.PRODUCT_INFO_PATH_TEMPLATE.format(''), exist_ok=True)
    process_map(extract_and_write_chunk_product_info, chunk_files, max_workers=config.NUM_WORKERS)
