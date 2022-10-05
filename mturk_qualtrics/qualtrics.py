from . import config

from QualtricsAPI.Setup import Credentials
from QualtricsAPI.Survey import Responses


# Credentials().qualtrics_api_credentials(
#     token = config.QUALTRICS['token'],
#     data_center = config.QUALTRICS['data_center'],
#     directory_id = config.QUALTRICS['directory_id'])

        
def get_survey_responses(config=config.QUALTRICS, drop_uploads=True):
    """get survey responses. config is a dict with the keys:

    - survey_id
    - token
    - data_center
    - directory_id
    """
    survey_id=config['survey_id']
    token=config['token'] 
    data_center=config['data_center'] 
    directory_id=config['directory_id'] 

    Credentials().qualtrics_api_credentials(token, data_center, directory_id)
    responses = Responses().get_survey_responses(
        survey=survey_id, 
        useLabels=False)
    if (drop_uploads):
        responses = responses[responses['Q43_Id'].isna()]
    return (responses.drop(blacklist_fields, axis=1))


blacklist_fields = [
    'API_TOKEN',
    'BATCH',
    'DistributionChannel',
    'EndDate',
    'ExternalReference',
    'FQID',
    'Finished',
    'IPAddress',
    'LocationLatitude',
    'LocationLongitude',
    'Progress',
    'SurveyID',
    'ResponseID',
    'API_TOKEN',
    'Q-comments',
#    'Q-fast-completion',
    'Q43_Id',
    'Q43_Name',
    'Q43_Size',
    'Q43_Type',
    'StartDate',
    'EndDate',
    'Status',
    'IPAddress',
    'Progress',
    'RecipientLastName',
    'RecipientFirstName',
    'RecipientEmail',
    'ExternalReference',
    'LocationLatitude',
    'LocationLongitude',
    'DistributionChannel',
    'UserLanguage'
]

cleaned_fields = [
    # Fields created by Qualtrics that we *DO NOT keep*
    #'StartDate', 'EndDate', 'Status', 'IPAddress', 'Progress',
    #'RecipientLastName', 'RecipientFirstName', 'RecipientEmail',
    #'ExternalReference', 'LocationLatitude', 'LocationLongitude',
    #'DistributionChannel', 'UserLanguage', 
    
    # Fields created by Qualtrics that we *DO keep*
    'Duration (in seconds)', 'Finished', 'RecordedDate', 'ResponseId',
    
    # Fields to handle the uploaded file -- do not keep
    # 'Q43_Id', 'Q43_Name', 'Q43_Size', 'Q43_Type', 
    
    # Fields for setup that have consent and continue vs exit Qs
    'intro-1', 'intro-2', 
    
    # Fields for guiding the participant through the download process
    'download', 
    # Fields for download process failure
    'download-fail-expl', 'download-fail-screen_Id', 'download-fail-screen_Name',
    'download-fail-screen_Size', 'download-fail-screen_Type', 
    
    # Fields for personal Qs. e.g. demographics data, amazon usage, life changes
    'q-demos-age', 'Q-demos-hispanic', 'Q-demos-race', 'Q-demos-education',
    'Q-demos-income', 'Q-demos-gender', 'Q-sexual-orientation', 'Q-demos-state', 
    'Q-amazon-use-howmany', 'Q-amazon-use-hh-size', 'Q-amazon-use-how-oft', 
    'Q-substance-use_1', 'Q-substance-use_2', 'Q-substance-use_3', 
    'Q-personal_1', 'Q-personal_2', 
    'Q-life-changes',
    
    # Fields for Q asking if they will share data -- specific to experiment arm
    # 'Q-fast-completion', unused
    'Q-control', 'Q-altruism', 'Q-bonus-05',
    'Q-bonus-20', 'Q-bonus-50', 
    
    # Fields for Qs about perceived data value
    'Q-data-value-05', 'Q-data-value-20', 'Q-data-value-50', 'Q-data-value-100', 
    'Q-data-value-any', 'Q-data-value-any_1_TEXT', 
    
    # Fields for Qs about how your data should be used
    'Q-sell-YOUR-data', 'Q-sell-consumer-data', 'Q-small-biz-use', 
    'Q-census-use', 'Q-research-society', 'Q-attn-check',
    
    # Comments are not clean
    # 'Q-comments',
    
    # Fields for important embedded data set set
    # Used to indicate experiment arm:
    'showdata',
    'incentive', 
    # We set this to connect responses to mturk workers we pay
    'RandomID',
    # We set these to make the API hacks work -- do not need for analysis
    # 'SurveyID', 'ResponseID', 'FQID', 'API_TOKEN',
]
