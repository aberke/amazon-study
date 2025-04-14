## Scripts for data processing

### Requirements
- set the `SCRAPINGBEE_API_KEY` env variable to the scraping bee api key you're using
- install the conda env defined in `/ENV.yml`

### Instructions
- `0-get_unique_products.py`: extracts a list of all unique products ordered by users from the `data/uploads/*.csv` files.
- `1-scrape_product_pages.py`: uses [scrapingbee](https://app.scrapingbee.com/dashboard) to scrape product pages from amazon, in parallel. Takes a very long time. This saves the full HTML of each product page in `output/product_pages/*.jsonl`. Each file is a 'chunk' of products. Each line is a json object with the `asin` of the product and the full text of the scraped page.
- `2-extract_product_info.py`: uses `selectorlib` and the `productSelector.yml` to scrape specific product info. Produces a directory of matched `jsonl` files in `output/product_info` that contains specific entities, such as average reviews, current price, length on the site, etc. Each object in each `jsonl` file corresponds to one product.
- `3-merge-survey_and_purchase_data.py`: merges the survey and purchase data, adding demographic info to each purchase's basic information (ASIN, product title, category, etc.). Does not include data from `output/product_info/*`. Produces a csv file, defined in `config.JOINED_DATA_PATH`.
