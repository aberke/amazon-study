#!/usr/bin/env python3
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import json
import glob

import config


if __name__ == "__main__":
    chunk_filenames = glob.glob(config.PRODUCT_INFO_PATH_TEMPLATE.replace("{}", "*"))
    print(
        f"> Reading {len(chunk_filenames)} chunks from {config.PRODUCT_INFO_PATH_TEMPLATE}"
    )
    all_objs = []
    for cf in tqdm(chunk_filenames):
        with open(cf, "r") as f:
            objs = json.load(f)
            all_objs.extend(objs)
    print(f"> Collected {len(all_objs)} ASINs, turning into single file...")

    with open(config.PRODUCT_INFO_DATA_FILE_PATH, "w+") as f:
        f.writelines([f"{json.dumps(obj)}\n" for obj in all_objs])

    print(f"> Wrote all ASIN data to {config.PRODUCT_INFO_DATA_FILE_PATH} !")
    # all_df = pd.DataFrame(all_objs)
