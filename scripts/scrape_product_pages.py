#!/usr/bin/env python3
from multiprocessing import Lock
from scrapingbee import ScrapingBeeClient
from tqdm.contrib.concurrent import process_map
import json
import os

CHUNKSIZE = 1000

# location of unique product ASIN list, separated by newlines:
product_file = '../output/all_products.txt'
# output file for JSON of scraped product data
scraped_file = '../output/product_pages.jsonl'

# process lock for writing to file
lock = Lock()

if 'SCRAPINGBEE_API_KEY' not in os.environ:
    print("Please set the environment variable SCRAPINGBEE_API_KEY to your ScrapingBee API key.")
    exit(1)
client = ScrapingBeeClient(api_key=os.environ['SCRAPINGBEE_API_KEY'])


def scrape(url):
    # Download the page using scrapingbee
    # print("Downloading %s" % url)
    # headers=headers, proxies={"http": proxy, "https": proxy})
    r = client.get(url)
    # Simple check to check if page was blocked (Usually 503)
    if r.status_code > 500:
        if "To discuss automated access to Amazon data please contact" in r.text:
            print(
                "Page %s was blocked by Amazon. Please try using better proxies\n" % url)
        else:
            print("Page %s must have been blocked by Amazon as the status code was %d" % (
                url, r.status_code))
        return None
    # Pass the HTML of the page and create
    return r.text

def scrape_product(asin):
    url = f'https://www.amazon.com/dp/product/{asin}'
    data = {
        'page_text': scrape(url),
        'asin': asin
    }
    if data['page_text']:
        # print(f'Writing for ASIN {asin} ...')
        with lock:
            with open(scraped_file, 'a') as f:
                json.dump(data,f)
                f.write("\n")

if __name__ == "__main__":
    # keep track of already scraped ASINs
    already_scraped = set()
    if os.path.exists(scraped_file):
        with open(scraped_file, 'r') as f:
            lines = f.readlines()
        if len(lines) > 0:
            already_scraped.update([json.loads(l)['asin'] for l in lines])
    print(f'Ignoring {len(already_scraped)} already scraped ASINs...')
        
    with open(product_file,'r') as asinlist:
        asins = [asin.strip() for asin in asinlist.readlines()]
        asins = [asin for asin in asins if asin not in already_scraped]
    r = process_map(scrape_product, asins, max_workers=50, chunksize=1000)
 