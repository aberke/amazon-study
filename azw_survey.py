#!/usr/bin/env python
"""AZW Survey

Usage:
  azw_survey.py --config FILE [INPUT ...]
  azw_survey.py qualtrics get_responses [--keep-upload-rows] [--start-date DATE] [--end-date DATE] (-o FILE)
  azw_survey.py mturk get_hits [--status STATUS] [-o FILE]
  azw_survey.py mturk get_assignments HIT_ID [--status STATUS] (-o FILE)
  azw_survey.py mturk pay_turkers HIT_ID [--dry-run|--autopay] [-o FILE]
  azw_survey.py (-h | --help)
  azw_survey.py --version

Options:
  -h --help                 Show this screen.
  --version                 Show version.
  --config FILE             Path to JSON config file with keys for 'token', 'data_center', 'directory_id', and 'survey_id'. [default: ./config.json]
  -o FILE                   Filepath to save data to.
  --start-date DATE         (not implemented) Only get responses after this start date
  --end-date DATE           (not implemented) Only get responses before this end date
  --keep-upload-rows        Keep upload file rows (Q43)
  --status STATUS           (not implemented) Only show mturk assignments that are STATUS ('Submitted', 'Approved', or 'Rejected'). [default: Submitted]
  --dry-run                 Dry run payment. Returns amounts for review.
  --autopay                 Actually pay / approve assignments

Examples:

Get all qualtrics responses and save to file:
    ./azw_survey.py qualtrics get_responses -o qualtrics_export.csv

Pay turkers for HIT_ID and save record to `pay_record.csv`:
    ./azw_survey.py mturk pay_turkers HIT_ID -o pay_record.csv --autopay
"""
from docopt import docopt
from mturk_qualtrics import qualtrics
from mturk_qualtrics.hits import HITUtils
import pandas as pd
import json

if __name__ == "__main__":
    args = docopt(__doc__, version="AZW Survey 0.1")
    with open(args["--config"]) as f:
        config = json.load(f)

    if args["qualtrics"]:
        df = qualtrics.get_survey_responses(
            config=config["qualtrics"], drop_uploads=not args["--keep-upload-rows"]
        )
        print("> Got survey responses. Data preview:")
        print(df)
        print(f"> Writing to csv {args['-o']}...")
        df.to_csv(args["-o"])
        print("> Written to disk! Exiting.")
    elif args["mturk"]:
        hits = HITUtils(config["aws"])
        # hits.initialize_client(config['aws'])
        if args["get_hits"]:
            hits = hits.get_amazon_survey_HITs()
            print("Assignments:")
            print(pd.DataFrame(hits)[["CreationTime", "HITId", "Title"]])
            if args["-o"]:
                pd.DataFrame(hits).to_csv(args["-o"])
        elif args["get_assignments"]:
            print(f"> Getting assignments for HIT {args['HIT_ID']}")
            assignments = hits.get_assignments_for_HIT(args["HIT_ID"])
            print(f"> Found {len(assignments)} Assignments:")
            print(pd.DataFrame(assignments))
            if args["-o"]:
                print(f"> Saving to {args['-o']}...")
                pd.DataFrame(assignments).to_csv(args["-o"])
        elif args["pay_turkers"]:
            print(f"> Getting qualtrics responses...")
            qualtrics_df = qualtrics.get_survey_responses(
                config=config["qualtrics"], drop_uploads=not args["--keep-upload-rows"]
            )
            print(f"> Getting assignments for HIT {args['HIT_ID']}")
            worker_assignments = hits.get_worker_assignment_data(
                args["HIT_ID"], qualtrics_df
            )
            assn_df = pd.DataFrame(worker_assignments)
            print("> Got matched worker assignments and bonus info:")
            print(assn_df)
            if args["-o"] and not args["--dry-run"] and not args["--autopay"]:
                print(f"> Saving to file {args['-o']}")
                assn_df.to_csv(args["-o"])
            if args["--dry-run"]:
                pay_record = hits.pay_workers(worker_assignments, dry_run=True)
                pay_df = pd.DataFrame(pay_record)
                print("> Dry Run Payment:")
                print(pay_df)
                pay_df.to_csv(args["-o"])
            elif args["--autopay"]:
                print("> Paying workers for real...")
                pay_record = hits.pay_workers(worker_assignments, dry_run=False)
                pay_df = pd.DataFrame(pay_record)
                print("> REAL Payment record:")
                print(pay_df)
                pay_df.to_csv(args["-o"])
