#!/usr/bin/env python3
from multiprocessing import Lock
from scrapingbee import ScrapingBeeClient
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import glob
import json
import os

import config

CHUNKSIZE = 1000
# this is the max # of concurrent connections to scrapingbee our subscription allows

# location of unique product ASIN list, separated by newlines:
product_file = config.UNIQUE_PRODUCT_FILE_PATH
# we split products into chunks. each file will contain a list of JSON objects
# with the page text and ASIN for each product in the chunk
page_file_template = config.SCRAPED_PAGE_PATH_TEMPLATE

prints = lambda s: print(s, end='\r')

# finds all missing ASINs from current scraping results and writes to config.SCRAPED_PAGE_ERROR_PATH

if __name__ == "__main__":
    with open(product_file,'r') as f:
        asins = [asin.strip() for asin in f.readlines()]
    # determine which chunks to complete

    print(f'> Looking at {page_file_template} for jsonl files with scraped product page data...')
    asin_chunks = [(i, asins[i:i + CHUNKSIZE]) for i in range(0, len(asins), CHUNKSIZE)]
    print(f'> found {len(asin_chunks)} chunks')
    completed_chunks = [fname.split('.jsonl')[0].split('/')[-1] for fname in glob.glob(page_file_template.format('*'))]
    print(f'> found {len(completed_chunks)} completed chunks.')
    chunks_to_scrape = [chunk for chunk in asin_chunks if str(chunk[0]) not in completed_chunks]
    # [asin_chunks.remove(chunk) for chunk in asin_chunks if str(chunk[0]) in completed_chunks]
    print(f'> Heads up -- {len(chunks_to_scrape)} chunks were not scraped')


    chunks_with_errors = []
    all_missing_asins = []

    prints(f'> starting processing...')
    for chunkfile in tqdm(glob.glob(page_file_template.format('*'))):
        num_lines = sum(1 for line in open(chunkfile))
        if num_lines < 1000:
            chunk_id = chunkfile.split('.jsonl')[0].split('/')[-1]
            # append chunk ID to error tracker
            chunks_with_errors.extend(chunk_id)
            chunk_asins = [c for c in asin_chunks if str(c[0]) == chunk_id]
            with open(chunkfile, 'r') as f:
                scraped_asins = [json.loads(l)['asin'] for l in f.readlines()]
            missing_asins = [asin for asin in chunk_asins if not scraped_asins.contains(asin)]
            all_missing_asins.extend(missing_asins)

    print(f'> These chunks had missing asins: {chunks_with_errors}')

    prints(f'> Writing {len(all_missing_asins)} missing asins to: {config.SCRAPED_PAGE_ERROR_PATH}')
    with open(config.SCRAPED_PAGE_ERROR_PATH, 'w') as f:
        for asin in missing_asins:
            f.write(f'{asin}\n')
