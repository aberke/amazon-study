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

# lock = Lock()

if 'SCRAPINGBEE_API_KEY' not in os.environ:
    print("Please set the environment variable SCRAPINGBEE_API_KEY to your ScrapingBee API key.")
    exit(1)
client = ScrapingBeeClient(api_key=os.environ['SCRAPINGBEE_API_KEY'])


def clean(html):
    from bs4 import BeautifulSoup
    from bs4 import Comment
    soup = BeautifulSoup(html, "html5lib")    
    [x.extract() for x in soup.find_all('script')]
    [x.extract() for x in soup.find_all('style')]
    [x.extract() for x in soup.find_all('meta')]
    [x.extract() for x in soup.find_all('noscript')]
    [x.extract() for x in soup.find_all(string=lambda text:isinstance(text, Comment))]
    return str(soup)

def scrape(url):

    # Loop to request using client.get until an exception is not raised
    r = None
    while r is None:
        try:
            r = client.get(url, params = { 
                'render_js': 'False'
                }
            )
            break
        except Exception as e:
            print(f'Error scraping {url}: {e}')
            continue


    # Simple check to check if page was blocked (Usually 503)
    if r.status_code > 500:
        if "To discuss automated access to Amazon data please contact" in r.text:
            print(
                "Page %s was blocked by Amazon. Please try using better proxies\n" % url)
        else:
            print("Page %s must have been blocked by Amazon as the status code was %d" % (
                url, r.status_code))
        return None
    return clean(r.text)


def scrape_chunk(asin_chunk):
    """writes a chunk of scraped ASIN pages to a file"""
    i, asins = asin_chunk
    chunk_data = []
    for asin in tqdm(asins, desc=f'chunk {i}'):
        url = f'https://www.amazon.com/dp/product/{asin}'
        data = {
            'page_text': scrape(url),
            'asin': asin,
            'chunk': i
        }
        chunk_data.append(data)
    outfile = page_file_template.format(i)
    print(f'writing chunk {i} to {outfile}')
    with open(outfile, 'a') as f:
        for data in chunk_data:
            json.dump(data, f)
            f.write("\n")

def scrape_asin(c):
    i, asin = c[0], c[1]
    url = f'https://www.amazon.com/dp/product/{asin}'
    data = {
        'page_text': scrape(url),
        'asin': asin,
        'chunk': i
    }
    return data
    



if __name__ == "__main__":
    with open(product_file,'r') as f:
        asins = [asin.strip() for asin in f.readlines()]
    # determine which chunks to complete
    asin_chunks = [(i, asins[i:i + CHUNKSIZE]) for i in range(0, len(asins), CHUNKSIZE)]
    print(f'found {len(asin_chunks)} chunks')
    completed_chunks = [fname.split('.jsonl')[0].split('/')[-1] for fname in glob.glob(page_file_template.format('*'))]
    print(f'found {len(completed_chunks)} completed chunks: {completed_chunks}')
    chunks_to_scrape = [chunk for chunk in asin_chunks if str(chunk[0]) not in completed_chunks]
    # [asin_chunks.remove(chunk) for chunk in asin_chunks if str(chunk[0]) in completed_chunks]
    print(f'will scrape {len(chunks_to_scrape)} chunks')

    # for chunk in asin_chunks:
        # scrape_chunk(chunk)
    for chunk in chunks_to_scrape:
        print(f'scraping chunk {chunk[0]}')
        asins = [(chunk[0], asin) for asin in chunk[1]]
        chunk_results = process_map(scrape_asin, asins, max_workers=50, chunksize=1)
        outfile = page_file_template.format(chunk[0])
        # write just once instead of using locks
        for data in chunk_results:
            with open(outfile, 'a') as f:
                json.dump(data, f)
                f.write("\n")

        print(f'wrote {len(chunk_results)} results to {page_file_template.format(chunk[0])}')

    # r = process_map(scrape_chunk, asin_chunks, max_workers=N_WORKERS, chunksize=1)
 
