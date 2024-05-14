# Open e-commerce 1.0: Five years of crowdsourced US Amazon purchase histories with user demographics

MIT IRB protocol # 2205000649

## Overview

We crowdsourced a first-of-its-kind open dataset of purchase histories from more than 5000 Amazon.com users, along with user demographics, spanning 5 years. 
To collect the data we developed a tool using a a privacy-preserving and consent driven framework. 
To help support future crowdsourcing efforts, we embedded an experiment into our data collection tool, enabling us to study how different incentives and transparency treatments, as well as demographics, impact people's likelihood to share their data.

This repository contains the related data collection tooling and data prepreprocessing and analysis code.


## Access the data


See `/data` to access the open dataset.

Please cite appropriately.

> Berke, A., Calacci, D., Mahari, R. Yabe, T., Larson, K., & Pentland, S. Open e-commerce 1.0, five years of crowdsourced U.S. Amazon purchase histories with user demographics. Sci Data 11, 491 (2024). https://doi.org/10.1038/s41597-024-03329-6


## Data Descriptor

The Amazon purchase histories include date of purchase, price, product information (title, ASIN, category), and shipping address state for each purchased item. The dataset also includes demographics and other surveyed information about each consumer, which can enable further research insights. 

Our [Nature Scientific Data](https://doi.org/10.1038/s41597-024-03329-6) article describes the dataset and includes example uses and analyses validating the data. 

See:
> Berke, A., Calacci, D., Mahari, R. Yabe, T., Larson, K., & Pentland, S. Open e-commerce 1.0, five years of crowdsourced U.S. Amazon purchase histories with user demographics. Sci Data 11, 491 (2024). https://doi.org/10.1038/s41597-024-03329-6

We published this dataset in an effort towards democratizing access to rich data sources routinely used by companies. We call this dataset "open e-commerce 1.0" because it is the first of its kind and we hope that publishing the data will catalyze future work in this area. Namely, while this dataset can serve a variety of research purposes, its utility will be enhanced when future researchers further collect datasets to complement it.



## Data collection and experiment

The data collection process, experiment, and results are described in [our CSCW paper](https://arxiv.org/pdf/2404.13172) (Computer-Supported Cooperative Work and Social Computing Conference).

See:
> Berke, A., Mahari, R., Pentland, S., Larson, K., & Calacci, D. (2024). Insights from an experiment crowdsourcing data from thousands of US Amazon users: The importance of transparency, money, and data use. CSCW 2024. https://arxiv.org/pdf/2404.13172 

### Data collection instrument

We built a tool to simultaneously collect the Amazon data, study participant survey data, and conduct an experiment.
The tool was built such that no Amazon data left participant machines without their informed consent. Study participants were paid for their time, whether or not they chose to share their data. 

See `/instrument` for implementation details.

### An experiment in crowdsourcing

We built an experiment into our survey tool in order to study what impacts consumers' likelihood to share their data with researchers, in order to support future data crowdsourcing  efforts. 

Survey participants were randomly assigned to experimental arms, and were presented with different interfaces and incentives when asked to share their data. 
We found that showing users their data significantly increases sharing. In addition, we uncovered how the likelihood to share differs across demographic groups.

We also studied the incremental impact of monetary rewards, finding a linear relationship between reward amount and likelihood to share.  In addition, our study design enabled a unique empirical evaluation of the “privacy paradox”, where users claim to value their privacy more than they do in practice. We were able to measure how much more impact real monetary rewards had on users' likelihood to share versus hypothetical rewards.


### FTC comment
We coauthored an open letter to the FTC in advance of their commercial surveillance rulemaking.  
Our letter is available here: https://www.regulations.gov/comment/FTC-2022-0053-1201.

Our letter discusses how corporate data collection practices have led to power asymmetries and resulting consumer harms, and how researcher access to consumer data can help expose potential harms to help empower future policy making. Our letter argues the FTC should empower consumers to share data, with their informed consent, with researchers and consumer advocacy organizations, and prohibit corporate practices designed to prevent this. Such a change is a first step towards making more open datasets like the one we crowdsourced possible.


