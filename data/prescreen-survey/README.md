# Prescreen Survey Data

## Background info

There was a prescreen survey. Participants who "passed" the prescreen were invited to participate in the main survey.

Participants "passed" the prescreen if they:
- Have an Amazon account
- Passed the attention check(s)
- Verify they can log into their Amazon account during the study
Later version: 
- Indicate they want to participate in the main survey after being told it asks them to log into their account.

We verified with Prolific that the prescreen and its use of attention checks adhered to their guidelines.

There were multiple versions of the prescreen. And some versions were run within different batches on the survey platforms used.

The final version of the Prolific prescreen was then copied to a version to use on CloudResearch.
We used CloudResearch after it seemed we were exhausting the sample pool on Prolific.
There are two platforms within CloudResearch. One is built ontop of Amazom MTurk, "mturk toolkit". The other is called "connect".
We used both platforms. 
Surveys taken via connect have an additional parameter "connect" that is inserted as embedded data in the survey results.
They used the same cloudresearch version of the prescreen.
We initially tested on both connect and mturk toolkit. Then used mturk toolkit. But they mturk billing broke and we couldn't complete more surveys there and moved to connect.


## Data preprocessing

Notebook: 
data-anlysis/prescreen-survey/preprocessing.ipynb

Inputs (raw/private):
- Raw Qualtrics survey data (multiple surveys)
- Prolific participant data downloads (multiple batches)

Output (public):
- Cleaned, preprocessed, merged dataset

We merge the data from the prescreens for efficient processing.

There are multiple Qualtrics prescreen surveys, and multiple Prolific study batches. 
Prolific provides some demographic data about most participants, which is merged in as well.

The raw prescreen data is private because it contains Prolific/Worker IDs that could be used to reidentify participants and open comments text.

The preprocessing does:
- Deduplicates by Prolific/Worker IDs (there could have been some multiple submissions)

- Merges survey datasets across Qualtrics prescreen surveys

- Merges Qualtrics data with Prolific demographic data

- Inserts column indicating data source & survey version

- Strips out Prolific / Worker IDs and separates comments from IDs (for privacy)

## Survey versions & Data notes


### Qualtrics:

#### Qualtrics for Prolific

qualtrics-prescreen-v1
- Preview link: https://mit.co1.qualtrics.com/jfe/preview/previewId/73b5445c-ac7f-4c16-b030-99cd0da40689/SV_5j48hcy4jQvLSM6?Q_CHL=preview&Q_SurveyVersionID=current

qualtrics-prescreen-v2
- Preview link: https://mit.co1.qualtrics.com/jfe/preview/previewId/c67d148f-0c5a-4424-9a40-5826c2b8de22/SV_9L9LwHbVlnyYgfQ?Q_CHL=preview&Q_SurveyVersionID=current

#### Qualtrics for CloudResearch

qualtrics-prescreen-cloudresearch
Preview link: https://mit.co1.qualtrics.com/jfe/preview/previewId/6916bf6f-5abb-4975-95c8-8a2d885580f6/SV_6iowEnQ0RNcMeYC?Q_CHL=preview&Q_SurveyVersionID=current



