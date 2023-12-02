# Data

## Preprocessing for survey data and Amazon data

See preprocessing notebook.

## Files

`survey.csv` contains all cleaned survey responses that were collected, including from participants who did not choose to share their Amazon purchases data.

`survey.pub.csv` is a subset of the `survey.csv` responses, including only the responses from participants who chose to share their Amazon data (N=5027). Columns relevant to only the Qualtrics survey software and experiment setup were removed.

`fields.csv` contains all fields related to the survey including variables embedded in the Qualtrics survey software that were used for the experiment.

`fields.pub.csv` contains a subset of the fields, limited to fields that can help users of the `survey.pub.csv` data understand the columns. 
