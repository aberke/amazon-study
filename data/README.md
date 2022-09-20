# Data

## Preprocessing for the responses data

###### Note: This is for the responses data, not the uploaded transactions data

Processes the raw responses data that was exported from Qualtrics. Creates a "cleaned" version.

Cleaned version can be committed to the repository; raw vesion is not.



### Handle comments

As per the IRB protocol, comments connected to survey participants are not published. They are removed from the cleaned data. 

### Drop extra rows

When participants consent to share their data, the data file is uploaded to the same survey as a separate response. This generates an extra row of data for just that response, where only the fields for the data file (special hidden Qualtrics question) are filled.

We drop these from the cleaned data.
Note this does not lose the ability to link the data -- the uploaded files are named as the ResponseId of the participant who uploaded the file.


### Drops unused columns

Columns automatically added by Qualtrics, not used by us

Fields we added in order to hack on the Qualtrics APIs
