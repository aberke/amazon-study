#!/usr/bin/env python3
import pandas as pd
import numpy as np
from tqdm import tqdm
from pathlib import Path
import glob
import os

import config

demo_cols = [
    "q-demos-age",
    "Q-demos-hispanic",
    "Q-demos-race",
    "Q-demos-education",
    "Q-demos-income",
    "Q-demos-gender",
    "Q-sexual-orientation",
    "Q-demos-state",
    "Q-amazon-use-howmany",
    "Q-amazon-use-hh-size",
    "Q-amazon-use-how-oft",
    "Q-substance-use_1",
    "Q-substance-use_2",
    "Q-substance-use_3",
    "Q-personal_1",
    "Q-personal_2",
    "Q-life-changes",
]

print(f"> Reading data file: {config.SURVEY_DATA_FILE}...")
sdf = pd.read_csv(config.SURVEY_DATA_FILE)
# save question texts
question_text = sdf.iloc[0]
# remove metadata rows
sdf = sdf[2:]


sdf["Q-attn-check-passed"] = sdf["Q-attn-check"] == "Yes,No,I don't know"
all_resp_length = len(sdf)
sdf = sdf[sdf["Q-attn-check-passed"]]
print(f"> {len(sdf)} / {all_resp_length} passed attention checks.")

attn_check_passed_length = len(sdf)
sdf = sdf[~pd.isna(sdf["Q-prolific"])]
sdf = sdf[~sdf["Q-prolific"].str.contains("test")]
print(f"> {len(sdf)} / {attn_check_passed_length} have prolific IDs")


df_demo = sdf[demo_cols + ["ResponseId"]].set_index("ResponseId")


print(f"> Reading purchase data from {config.PURCHASE_GLOB_PATH}...")
df_products = [pd.read_csv(f) for f in tqdm(glob.glob(config.PURCHASE_GLOB_PATH))]
df_products = pd.concat(df_products)
df_products = df_products.set_index("Survey ResponseID")

print(f"> Joining with survey data...")
df_joined = df_products.join(df_demo, how="left")


print(f"> Writing to {config.JOINED_DATA_PATH}...")
df_joined.to_csv(config.JOINED_DATA_PATH)
print(f"> Wrote to {config.JOINED_DATA_PATH}")
