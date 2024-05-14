# Data

This repository contains data for the survey and experiment.

## Amazon data
The Amazon purchases histories and associated survey responses can be accessed via Harvard Dataverse: https://doi.org/10.7910/DVN/YGLYDY 

Please use and cite appropriately.
> Berke, A., Calacci, D., Mahari, R. Yabe, T., Larson, K., & Pentland, S. Open e-commerce 1.0, five years of crowdsourced U.S. Amazon purchase histories with user demographics. Sci Data 11, 491 (2024). https://doi.org/10.1038/s41597-024-03329-6



## Survey Data Files

`survey.csv` contains all cleaned survey responses that were collected, including from participants who did not choose to share their Amazon purchases data.

`survey.pub.csv` is a subset of the `survey.csv` responses, including only the responses from participants who chose to share their Amazon data (N=5027). Columns relevant to only the Qualtrics survey software and experiment setup were removed.

`fields.csv` contains all fields related to the survey including variables embedded in the Qualtrics survey software that were used for the experiment.

`fields.pub.csv` contains a subset of the fields, limited to fields that can help users of the `survey.pub.csv` data understand the columns. 


## Preprocessing for survey data and Amazon data

See preprocessing notebook `../data-analysis/preprocessing.ipynb`.

