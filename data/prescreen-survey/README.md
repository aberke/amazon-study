# Prescreen Survey Data

See `/instrument` for information on the data collection and tool.

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
