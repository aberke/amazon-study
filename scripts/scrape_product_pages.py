#!/usr/bin/env python3
from scrapingbee import ScrapingBeeClient
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import glob
import json
import os

CHUNKSIZE = 100
# this is the max # of concurrent connections to scrapingbee our subscription allows
N_WORKERS = 50

# location of unique product ASIN list, separated by newlines:
product_file = '../output/all_products.txt'
# we split products into chunks. each file will contain a list of JSON objects
# with the page text and ASIN for each product in the chunk
page_file_template = '../output/product_pages/{}.jsonl'

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
    [x.extract() for x in soup.find_all(text=lambda text:isinstance(text, Comment))]
    return str(soup)

def scrape(url):
    r = client.get(url, params = { 
        'render_js': 'False'
        }
    )
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



if __name__ == "__main__":
    with open(product_file,'r') as f:
        asins = [asin.strip() for asin in f.readlines()]
    asin_chunks = [(i, asins[i:i + CHUNKSIZE]) for i in range(0, len(asins), CHUNKSIZE)]
    completed_chunks = [fname.split('.jsonl')[0] for fname in glob.glob(page_file_template.format('*'))]
    [asin_chunks.remove(chunk) for chunk in asin_chunks if str(chunk[0]) in completed_chunks]

    # for chunk in asin_chunks:
        # scrape_chunk(chunk)
    r = process_map(scrape_chunk, asin_chunks, max_workers=N_WORKERS, chunksize=1)
 