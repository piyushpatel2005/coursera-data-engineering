# Week 1

This week covers introduction to data modelling in Analytics databases along with different techniques for data modelling.

These includes normalization, star schema. This week also has labs on normalization and data modelling using DBT.


- [Lab 1 - Data Normalization](labs/lab1/C4_W1_Lab_1_Data_Normalization_Solution.md)

## Inmon Data Modelling

This is subject-oriented, integrated, non-volatile, time-variant collection of data. It organizes data into major subject areas. For each subject, it would contain all subject details. This is where data is stored as highly normalized formats. This way it supports as single source of truth. This also reduces data duplication. In data warehouse the data is stored as third normal form and then there will be department specific star schemas defined for efficient reporting queries per department. When anaysis requirements are not clearly defined and data quality is higher priority, use this approach.

## Kimball Model

- focuses more on serving department specific queries from data warehouse directly.
- You model the data as multiple star schemas in data warehouse. It stores data as star schema so data redundancy occurs. It provides quick insights and rapid implementation and iteration.


## Data Vault Model

It consists of three layers. staging, enterprise data warehouse and then information delivery layer. There is no notion of good, bad or conformed data. It only changes the structure in which data is stored. It consists of three main tables:
1. Hubs: stores unique list of business keys like customers, products, employees, vendors, suppliers
2. Link: connects two or more hubs to represent relationship, transaction or event
3. Satellite: contains attributes that provide context for hubs and links.


- [Assignment: Model the Normalized Data to Star Schema](labs/lab2/C4_W1_Assignment_Solution.md)

- [Quiz](quiz.html)