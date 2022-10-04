#!/usr/bin/env python
"""AZW Survey

Usage:
  azw_survey.py --config FILE [INPUT ...]
  azw_survey.py qualtrics get_responses [--keep-upload-rows] [--start-date DATE] [--end-date DATE] (-o FILE)
  azw_survey.py mturk get_hits [--status STATUS] [-o FILE]
  azw_survey.py mturk get_assignments HIT_ID [--status STATUS] (-o FILE)
  azw_survey.py (-h | --help)
  azw_survey.py --version

Options:
  -h --help                 Show this screen.
  --version                 Show version.
  --config FILE             Path to JSON config file with keys for 'token', 'data_center', 'directory_id', and 'survey_id'. [default: ./config.json]
  -o FILE                   Filepath to save data to.
  --start-date DATE         Only get responses after this start date
  --end-date DATE           Only get responses before this end date
  --keep-upload-rows        Keep upload file rows (Q43)
  --status STATUS           Only show mturk assignments that are STATUS ('Submitted', 'Approved', or 'Rejected'). [default: Submitted]
"""
from docopt import docopt
from mturk_qualtrics import qualtrics
from mturk_qualtrics.hits import HITUtils
import pandas as pd
import json

if __name__ == '__main__':
    args = docopt(__doc__, version="AZW Survey 0.1")
    with open(args["--config"]) as f:
        config = json.load(f)

    if (args['qualtrics']):
        df = qualtrics.get_survey_responses(config = config['qualtrics'], 
                                            drop_uploads = not args['--keep-upload-rows'])
        print("> Got survey responses. Data preview:")
        print(df)
        print(f"> Writing to csv {args['-o']}...")
        df.to_csv(args['-o'])
        print("> Written to disk! Exiting.")
    elif args['mturk']:
        hits = HITUtils(config['aws'])
        # hits.initialize_client(config['aws'])
        if (args['get_hits']):
            hits = hits.get_amazon_survey_HITs()
            print("Assignments:")
            print(pd.DataFrame(hits)[['CreationTime', 'HITId', 'Title']])
            if (args['-o']):
                pd.DataFrame(hits).to_csv(args['-o'])
        elif args['get_assignments']:
            print(f"> Getting assignments for HIT {args['HIT_ID']}")
            assignments = hits.get_assignments_for_HIT(args['HIT_ID'])
            print(f"> Found {len(assignments)} Assignments:")
            print(pd.DataFrame(assignments))
            if args['-o']:
                print(f"> Saving to {args['-o']}...")
                pd.DataFrame(assignments).to_csv(args['-o'])
