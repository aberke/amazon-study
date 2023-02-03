"""
Utility for importing into notebooks. (Move me to a library .py file)
"""
import numpy as np
import pandas as pd

# This is a dump from the recode values exported from qualtrics Q-demos-state.
# Qualtrics put the states in alphabetical order for their recode value, did not code by FIPs
states_recode_text = '1\nAlabama\n2\nAlaska\n3\nArizona\n4\nArkansas\n5\nCalifornia\n6\nColorado\n7\nConnecticut\n8\nDelaware\n9\nDistrict of Columbia\n10\nFlorida\n11\nGeorgia\n12\nHawaii\n13\nIdaho\n14\nIllinois\n15\nIndiana\n16\nIowa\n17\nKansas\n18\nKentucky\n19\nLouisiana\n20\nMaine\n21\nMaryland\n22\nMassachusetts\n23\nMichigan\n24\nMinnesota\n25\nMississippi\n26\nMissouri\n27\nMontana\n28\nNebraska\n29\nNevada\n30\nNew Hampshire\n31\nNew Jersey\n32\nNew Mexico\n33\nNew York\n34\nNorth Carolina\n35\nNorth Dakota\n36\nOhio\n37\nOklahoma\n38\nOregon\n39\nPennsylvania\n40\nPuerto Rico\n41\nRhode Island\n42\nSouth Carolina\n43\nSouth Dakota\n44\nTennessee\n45\nTexas\n46\nUtah\n47\nVermont\n48\nVirginia\n49\nWashington\n50\nWest Virginia\n51\nWisconsin\n52\nWyoming\n53\nI do not reside in the United States'
states_recode_list = states_recode_text.split('\n')
states_choices_map = {states_recode_list[i]: states_recode_list[i+1] for i in range(0, len(states_recode_list), 2)}

# {QID: {Q: Q text, choices: map}}
codebook = {
    'q-demos-age': {
        'Q': 'How old are you?',
        'choices': {
            '1':'18 - 24 years',
            '2':'25 - 34 years',
            '3':'35 - 44 years',
            '4':'45 - 54 years',
            '5':'55 - 64 years',
            '6':'65 or older'
        },
    },
    'Q-demos-race': {
        'Q': 'Choose one or more races that you consider yourself to be',
        'choices': {
            '1':'White',
            '2':'Black or African American',
            '3':'American Indian or Alaska Native',
            '4':'Asian',
            '5':'Native Hawaiian or Pacific Islander',
            '6':'Other'
        },
    },
    'Q-demos-education': {
        'Q':'What is the highest level of education you have completed?',
        'choices': {
            '1':'Some high school or less',
            '2':'High school diploma or GED',
            '3':'Bachelor\'s degree',
            '4':'Graduate or professional degree (MA, MS, MBA, PhD, JD, MD, DDS, etc)',
            '5':'Prefer not to say'
        }
        
    },
    'Q-demos-income': {
        'Q': 'What was your total household income in the previous year before taxes?',
        'choices': {
            '1':'Less than \$25,000','2':'\$25,000 to \$49,999',
            '3':'\$50,000 to $74,999','4':'\$75,000 to \$99,999',
            '5':'\$100,000 to $149,999','6':'\$150,000 or more',
            '7':'Prefer not to say',
        },
    },
    'Q-demos-gender': {
        'Q':'How do you describe yourself?',
        'choices': {'1':'Male','2':'Female','3':'Other', '4':'Prefer not to say'},
    },
    'Q-sexual-orientation': {
      'Q':'Which best describes your sexual orientation?',
        'choices':{
            '1':'heterosexual (straight)',
            '2':'LGBTQ+',
            '3':'prefer not to say'
        },
    },
    'Q-demos-state': {
        'Q':'In which state do you currently reside?',
        'choices': states_choices_map,
    },
    'Q-amazon-use-how-oft': {
        'Q': 'How often do you (+ anyone you share your account with) order deliveries from Amazon?',
        'choices': {
            '1': 'Less than 5 times per month',
            '2': '5 - 10 times per month',
            '3': 'More than 10 times per month'
        }
    }
}

def clean_df(df):
    df = df.drop([0,1])
    # add boolean indicating share
    df['share'] = df[
        ['Q-control', 'Q-altruism', 'Q-bonus-05', 'Q-bonus-20', 'Q-bonus-50']
    ].astype(float).fillna(0).sum(axis=1)
# rename incentives
    df['incentive'] = df['incentive'].map({
        'control':'control', 'altruism':'altruism',
        'bonus-05':'bonus $.05', 'bonus-20':'bonus $.20', 'bonus-50':'bonus $.50'
    })
    df.to_csv('data/qualtrics_cleaned.csv', index=False)

