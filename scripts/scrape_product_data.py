#!/usr/bin/env python3
from scrapingbee import ScrapingBeeClient
from selectorlib import Extractor
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
from itertools import cycle
import requests 
from lxml.html import fromstring
import json 
import os

# location of unique product ASIN list, separated by newlines:
product_file = '../output/all_products.txt'
scraped_file = '../output/search_results_output.jsonl'

# Create an Extractor by reading from the YAML file
e = Extractor.from_yaml_file('productSelector.yml')


if 'SCRAPINGBEE_API_KEY' not in os.environ:
    print("Please set the environment variable SCRAPINGBEE_API_KEY to your ScrapingBee API key.")
    exit(1)

client = ScrapingBeeClient(api_key=os.environ['SCRAPINGBEE_API_KEY'])

user_agents = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
]

def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:10]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            #Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies



def scrape(url):  

    headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.amazon.com/',
        'accept-language': 'en-US, en;q=0.5',
    }

    # randomize user agent to help not get blocked
    # headers['user_agent'] = random.choice(user_agents)

    # Download the page using requests
    print("Downloading %s"%url)
    r = client.get(url) #headers=headers, proxies={"http": proxy, "https": proxy})
    # Simple check to check if page was blocked (Usually 503)
    if r.status_code > 500:
        if "To discuss automated access to Amazon data please contact" in r.text:
            print("Page %s was blocked by Amazon. Please try using better proxies\n"%url)
        else:
            print("Page %s must have been blocked by Amazon as the status code was %d"%(url,r.status_code))
        return None
    # Pass the HTML of the page and create 
    return e.extract(r.text)


def scrape_product(asin):
    url = f'https://www.amazon.com/dp/product/{asin}'
    data = scrape(url) 
    if data:
        print(f'Writing data to {scraped_file} for {asin} {data["title"] and data["title"][:40]}...')
        data['ASIN'] = asin
        with open(scraped_file, 'a') as f:
            json.dump(data,f)
            f.write("\n")

if __name__ == "__main__":
    proxies = get_proxies()
    proxy_pool = cycle(proxies)
# keep track of already scraped ASINs
    already_scraped = set()
    if os.path.exists(scraped_file):
        with open(scraped_file, 'r') as f:
            lines = f.readlines()
            if len(lines) > 0:
                asins = [json.loads(l)['ASIN'] for l in lines]
                already_scraped.update(asins)
    print(f'Ignoring {len(already_scraped)} already scraped ASINs...')
        

# product_data = []
    with open(product_file,'r') as asinlist, open(scraped_file, 'a') as outfile:
        asins = [asin.strip() for asin in asinlist.readlines()]
        asins = [asin for asin in asins if asin not in already_scraped]
    r = process_map(scrape_product, asins, max_workers=5, chunksize=4)
        # for asin in tqdm(asins[:100]):
        #     proxy = next(proxy_pool)
        #     scrape_product(asin, proxy)
        # for asin in tqdm(asinlist.read().splitlines()):
                        # for product in data['products']:
                #     product['search_url'] = url
                #     
