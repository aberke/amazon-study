# Amazon data and consumer privacy study

MIT IRB protocol # 2205000649

## Overview and motivation
Companies like Amazon possess vast amounts of user data with significant societal value. However, these firms often do not share this information with research communities and individual users have limited means to access or collectively disseminate it. 

We crowdsourced years of Amazon purchases data from thousands of US consumers using a privacy-preserving and consent driven framework. 
To better inform and support future crowdsourcing efforts, we embedded an experiment into our data collection tool, enabling us to study how different incentives and transparency treatments, as well as demographics, impact people's likelihood to share their data.


### FTC comment
We coauthored an open letter to the FTC in advance of their commercial surveillance rulemaking.  Our letter is available here: https://www.regulations.gov/comment/FTC-2022-0053-1201 
Our letter discusses how corporate data collection practices have led to power asymmetries and resulting consumer harms, and how researcher access to consumer data can help expose potential harms to help empower future policy making. Our letter argues the FTC should empower consumers to share data, with their informed consent, with researchers and consumer advocacy organizations, and prohibit corporate practices designed to prevent this. Such a change is a first step towards making more open datasets like the one we crowdsourced possible.

### Open data and data collection tooling
We crowdsourced 4-5 years of Amazon purchase histories from more than 5000 US consumers, containing more than a million purchases. The dataset includes date of purchase, price, product information, and shipping address state for each purchased item. It also includes demographics and other surveyed information about each consumer, which can enable further research insights. We are currently in the process of making this dataset openly available. All data were collected with the purposes of making an open dataset with the knowledge and explicit consent from study participants. To collect the data we developed a data collection and survey tool that prioritizes participant consent and privacy.  This tool's design offers a generalizable approach that could be adapted for various contexts, providing other researchers a convenient tool to crowdsource data and build new open datasets. 


### Study to support further crowdsourcing efforts
We built an experiment into our survey tool in order to study what impacts consumers' likelihood to share their data with researchers, in order to support future data crowdsourcing  efforts. Survey participants were randomly assigned to experimental arms, and were presented with different interfaces and incentives when asked to share their data. We found that showing users their data significantly increases sharing. We also studied the incremental impact of monetary rewards, finding a linear relationship between reward amount and likelihood to share. In addition, we uncovered how the likelihood to share differs across demographic groups. Our article describing the survey tool, experiment and results is currently pending review at the Computer-Supported Cooperative Work and Social Computing Conference. 
An unpublished draft is at [/data-collection-survey-experiment.pdf](/data-collection-survey-experiment.pdf). We believe that crowdsourcing presents a valuable approach to developing open datasets and results from our experiment can inform and improve future crowdsourcing efforts.

---
See `/instrument` for details about our data collection process.

