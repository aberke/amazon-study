#!/usr/bin/env python3
import glob
import pandas as pd
from tqdm import tqdm 

files = glob.glob('../output/uploads/*.csv')
ASIN_COL = 'ASIN/ISBN (Product Code)'
product_file = '../output/all_products.txt'
product_set = set()

num_purchases = 0
for f in tqdm(files):
    df = pd.read_csv(f)
    asins = list(df[ASIN_COL].dropna())
    num_purchases += len(asins)
    product_set.update(asins)
with open(product_file, 'w') as f:
    asins = [f'{p}\n' for p in product_set]
    f.writelines(asins)

print(f"Found {num_purchases} total purchases with {len(product_set)} unique products.")
print("Wrote {} product ASINs to {}".format(len(product_set), product_file))
