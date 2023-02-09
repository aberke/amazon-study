from pathlib import Path

DATA_DIR = Path('../data')
OUTPUT_DIR = Path('../output')
UPLOAD_DIR = Path('../output/uploads')

# list of all unique product ASINs, separated by newlines
UNIQUE_PRODUCT_FILE_PATH = '../output/all_products.txt'
# glob for uploaded purchase data, downloaded directly
# from qualtrics
PURCHASE_GLOB_PATH = '../output/uploads/*.csv'
# template path for scraped page data
SCRAPED_PAGE_PATH_TEMPLATE = '../output/product_pages/{}.jsonl'

# selector file for selectorlib
PRODUCT_SELECTOR_PATH = 'productSelector.yml'
# template for jsonl files that contain product info data scraped
# from product pages
PRODUCT_INFO_PATH_TEMPLATE = '../output/product_info/{}.jsonl'

# error logs for scraping product info
PRODUCT_INFO_ERRORS_PATH = '../output/product_info_errors.jsonl'

# output path for joined purchase and demographic data
JOINED_DATA_PATH = OUTPUT_DIR / 'joined_purchase_demo.csv'

SURVEY_DATA_FILENAME = 'amazon-purchases-survey-v0_February+9,+2023_07.12 (1).zip'
SURVEY_DATA_FILE = DATA_DIR / SURVEY_DATA_FILENAME

