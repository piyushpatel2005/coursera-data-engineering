# Modeling and Transforming Text Data for ML

In this assignment, you will work with the Amazon Reviews dataset to generate a Machine Learning (ML) training dataset. The purpose of this dataset is to prepare the data and to create a vector database using text embeddings. You will follow the Feature Engineering steps to process the raw dataset in JSON files into datasets, then you will store the generated features in a Postgres database.

# Table of Contents

- [ 1 - Introduction](#1)
- [ 2 - Source Data Exploration](#2)
- [ 3 - Creating Functions to Process Data](#3)
  - [ 3.1 - Process Reviews](#3.1)
  - [ 3.2 - Process Metatada](#3.2)
  - [ 3.3 - Process Text Data](#3.3)
  - [ 3.4 - Process Numerical Variables](#3.4)
  - [ 3.5 - Process Categorical Variables](#3.5)
- [ 4 - Split Data and Create Text Embeddings](#4)
  - [ 4.1 - Split Data](#4.1)
  - [ 4.2 - Create Text Embeddings](#4.2)
- [ 5 - Upload Files for Grading](#5)

Load the required libraries:


```python
import re
import datetime as dt
import gzip
import json
import math
import requests
import time
import os
import subprocess
from typing import Dict, List, Union


import boto3
import numpy as np
import pandas as pd
import psycopg2 
import smart_open

from dotenv import load_dotenv
from pgvector.psycopg2 import register_vector
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder, StandardScaler, KBinsDiscretizer

pd.set_option('display.max_columns', 30)

LAB_PREFIX='de-c4w2a1'
```

<a name='1'></a>
## 1 - Introduction

Imagine you are employed as a Data Engineer at a prominent e-commerce retailer. The Machine Learning (ML) team has initiated a new research project and obtained a dataset comprising Amazon Reviews for different products. They have requested you to build a pipeline to refine the raw data in JSON format into structured datasets suitable for training ML models. To start the development, they have provided you with two sample files from the original dataset to validate the logic and develop an initial pipeline prototype within this notebook. Additionally, the Data Analysis team has requested that you generate embeddings from the reviews and product texts and then store the vectors in a vector database for future analysis; for this purpose, the ML team has enabled an API that runs a text embedder ML model for you to consume and generate the vectors.

The main requirements regarding the datasets are the following:

1. Process the text, categorical and numerical variables into features.
2. Generate text embeddings based on the review text and product information (either the description or the title)
3. Divide the original data into three tables:
   - Reviews embeddings dataset: it must contain the reviewer ID, product ASIN, the review text and the corresponding embedding vector.
   - Product embeddings dataset: it must contain the product ASIN, the product information and the corresponding embedding vector.
   - Review metadata dataset: it must contain the remaining features related to the reviews and products for each review from the original data.
4. Store the new features in the provisioned RDS Postgres instance.

<a name='2'></a>
## 2 - Source Data Exploration

The dataset is comprised of two compressed JSON files, one with the reviews and one with the metadata of the products the reviews are from. Here is an example of a review:

```json
{
  "reviewerID": "A2SUAM1J3GNN3B",
  "asin": "0000013714",
  "reviewerName": "J. McDonald",
  "helpful": [2, 3],
  "reviewText": "I bought this for my husband who plays the piano.  He is having a wonderful time playing these old hymns.  The music  is at times hard to read because we think the book was published for singing from more than playing from.  Great purchase though!",
  "overall": 5.0,
  "summary": "Heavenly Highway Hymns",
  "unixReviewTime": 1252800000,
  "reviewTime": "09 13, 2009"
}
```

Here is the description of the fields:

- `reviewerID` - ID of the reviewer, e.g. A2SUAM1J3GNN3B
- `asin` - ID of the product, e.g. 0000013714
- `reviewerName` - name of the reviewer
- `helpful` - helpfulness rating of the review, e.g. 2/3
- `reviewText` - text of the review
- `overall` - rating of the product
- `summary` - summary of the review
- `unixReviewTime` - time of the review (unix time)
- `reviewTime` - time of the review (raw)

And this is an example of the review metadata:
```json
{
  "asin": "0000031852",
  "title": "Girls Ballet Tutu Zebra Hot Pink",
  "price": 3.17,
  "imUrl": "http://ecx.images-amazon.com/images/I/51fAmVkTbyL._SY300_.jpg",
  "related":
  {
    "also_bought": ["B00JHONN1S", "B002BZX8Z6", "B00D2K1M3O", "0000031909", "B00613WDTQ", "B00D0WDS9A", "B00D0GCI8S", "0000031895", "B003AVKOP2", "B003AVEU6G", "B003IEDM9Q", "B002R0FA24", "B00D23MC6W", "B00D2K0PA0", "B00538F5OK", "B00CEV86I6", "B002R0FABA", "B00D10CLVW", "B003AVNY6I", "B002GZGI4E", "B001T9NUFS", "B002R0F7FE", "B00E1YRI4C", "B008UBQZKU", "B00D103F8U", "B007R2RM8W"],
    "also_viewed": ["B002BZX8Z6", "B00JHONN1S", "B008F0SU0Y", "B00D23MC6W", "B00AFDOPDA", "B00E1YRI4C", "B002GZGI4E", "B003AVKOP2", "B00D9C1WBM", "B00CEV8366", "B00CEUX0D8", "B0079ME3KU", "B00CEUWY8K", "B004FOEEHC", "0000031895", "B00BC4GY9Y", "B003XRKA7A", "B00K18LKX2", "B00EM7KAG6", "B00AMQ17JA", "B00D9C32NI", "B002C3Y6WG", "B00JLL4L5Y", "B003AVNY6I", "B008UBQZKU", "B00D0WDS9A", "B00613WDTQ", "B00538F5OK", "B005C4Y4F6", "B004LHZ1NY", "B00CPHX76U", "B00CEUWUZC", "B00IJVASUE", "B00GOR07RE", "B00J2GTM0W", "B00JHNSNSM", "B003IEDM9Q", "B00CYBU84G", "B008VV8NSQ", "B00CYBULSO", "B00I2UHSZA", "B005F50FXC", "B007LCQI3S", "B00DP68AVW", "B009RXWNSI", "B003AVEU6G", "B00HSOJB9M", "B00EHAGZNA", "B0046W9T8C", "B00E79VW6Q", "B00D10CLVW", "B00B0AVO54", "B00E95LC8Q", "B00GOR92SO", "B007ZN5Y56", "B00AL2569W", "B00B608000", "B008F0SMUC", "B00BFXLZ8M"],
    "bought_together": ["B002BZX8Z6"]
  },
  "salesRank": {"Toys & Games": 211836},
  "brand": "Coxlures",
  "categories": [["Sports & Outdoors", "Other Sports", "Dance"]]
}
```

With the following fields:

- `asin` - ID of the product, e.g. 0000031852
- `title` - name of the product
- `price` - price in US dollars (at time of crawl)
- `imUrl` - url of the product image
- `related` - related products (also bought, also viewed, bought together, buy after viewing)
- `salesRank` - sales rank information
- `brand` - brand name
- `categories` - list of categories the product belongs to

2.1. The ML team has provided the dataset JSON files in an S3 bucket. Go to the AWS console and click on the upper right part, where your username appears. Copy the **Account ID**. In the code below, set the variable `BUCKET_NAME` to your account ID by replacing `<AWS-ACCOUNT-ID>` placeholder with the Account ID that you copied. The Account ID should contain only numbers without hyphens between them (e.g. 123412341234, not 1234-1234-1234).

Go to **CloudFormation** in the AWS console. You will see two stacks deployed, one associated with your Cloud9 environment (name with prefix `aws-cloud9`) and another named with an alphanumeric ID. Click on the alphanumeric ID stack and search for the **Outputs** tab. You will see the key `MlModelDNS`, copy the corresponding **Value** and replace with it the placeholder `<ML_MODEL_ENDPOINT_URL>` in the cell below.


```python
BUCKET_NAME = 'de-c4w2a1-851725471174-us-east-1-data-lake'
ENDPOINT_URL = 'http://ec2-34-196-88-19.compute-1.amazonaws.com:8080/'
```

2.2. Open the `./src/env` file and replace the placeholder `<RDS-ENDPOINT>` with the `PostgresEndpoint` value from the CloudFormation outputs. Save changes. Run the following cell to load the connection credentials that will be used later.


```python
load_dotenv('./src/env', override=True)

DBHOST = os.getenv('DBHOST')
DBPORT = os.getenv('DBPORT')
DBNAME = os.getenv('DBNAME')
DBUSER = os.getenv('DBUSER')
DBPASSWORD = os.getenv('DBPASSWORD')
```

2.3. Explore the samples of the dataset. You are provided with a function to load the data into memory and perform an exploration of it. Take a look at the function defined below:


```python
def read_data_sample(bucket_name: str, s3_file_key: str) -> pd.DataFrame:
    """Reads review sample dataset

    Args:
        bucket_name (str): Bucket name
        s3_file_key (str): Dataset s3 key location

    Returns:
        pd.DataFrame: Read dataframe
    """
    s3_client = boto3.client('s3')
    source_uri = f's3://{bucket_name}/{s3_file_key}'
    json_list = []
    for json_line in smart_open.open(source_uri, transport_params={'client': s3_client}):
        json_list.append(json.loads(json_line))
    df = pd.DataFrame(json_list)
    return df
```

2.3.4. Start reading the sample datasets with the `read_data_sample()` method. The key for the main reviews file is `'staging/reviews_Toys_and_Games_sample.json.gz'` and the one for metadata is `'staging/meta_Toys_and_Games_sample.json.gz'`. Also, assign the `bucket_name` values to `BUCKET_NAME`.


```python
### START CODE HERE ### (2 lines of code)
review_sample_df = read_data_sample(bucket_name=BUCKET_NAME, s3_file_key='staging/reviews_Toys_and_Games_sample.json.gz')
metadata_sample_df = read_data_sample(bucket_name=BUCKET_NAME, s3_file_key='staging/meta_Toys_and_Games_sample.json.gz')
### END CODE HERE ###

review_sample_df.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>reviewerID</th>
      <th>asin</th>
      <th>reviewerName</th>
      <th>helpful</th>
      <th>reviewText</th>
      <th>overall</th>
      <th>summary</th>
      <th>unixReviewTime</th>
      <th>reviewTime</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>AMEVO2LY6VEJA</td>
      <td>0000191639</td>
      <td>Nicole Soeder</td>
      <td>[0, 0]</td>
      <td>Great product, thank you! Our son loved the pu...</td>
      <td>5.0</td>
      <td>Puzzles</td>
      <td>1388016000</td>
      <td>12 26, 2013</td>
    </tr>
    <tr>
      <th>1</th>
      <td>A3C9CSW3TJITGT</td>
      <td>0005069491</td>
      <td>Renee</td>
      <td>[0, 0]</td>
      <td>I love these felt nursery rhyme characters and...</td>
      <td>4.0</td>
      <td>Charming characters but busy work required</td>
      <td>1377561600</td>
      <td>08 27, 2013</td>
    </tr>
    <tr>
      <th>2</th>
      <td>A31POTIYCKSZ9G</td>
      <td>0076561046</td>
      <td>So CA Teacher</td>
      <td>[0, 0]</td>
      <td>I see no directions for its use. Therefore I h...</td>
      <td>3.0</td>
      <td>No directions for use...</td>
      <td>1404864000</td>
      <td>07 9, 2014</td>
    </tr>
    <tr>
      <th>3</th>
      <td>A2GGHHME9B6W4O</td>
      <td>0131358936</td>
      <td>Dalilah G.</td>
      <td>[0, 0]</td>
      <td>This is a great tool for any teacher using the...</td>
      <td>5.0</td>
      <td>Great CD-ROM</td>
      <td>1382400000</td>
      <td>10 22, 2013</td>
    </tr>
    <tr>
      <th>4</th>
      <td>A1FSLDH43ORWZP</td>
      <td>0133642984</td>
      <td>Dayna English</td>
      <td>[0, 0]</td>
      <td>Although not as streamlined as the Algebra I m...</td>
      <td>5.0</td>
      <td>Algebra II -- presentation materials</td>
      <td>1374278400</td>
      <td>07 20, 2013</td>
    </tr>
  </tbody>
</table>
</div>




```python
metadata_sample_df.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>asin</th>
      <th>description</th>
      <th>title</th>
      <th>price</th>
      <th>salesRank</th>
      <th>imUrl</th>
      <th>brand</th>
      <th>categories</th>
      <th>related</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0000191639</td>
      <td>Three Dr. Suess' Puzzles: Green Eggs and Ham, ...</td>
      <td>Dr. Suess 19163 Dr. Seuss Puzzle 3 Pack Bundle</td>
      <td>37.12</td>
      <td>{'Toys &amp; Games': 612379}</td>
      <td>http://ecx.images-amazon.com/images/I/414PLROX...</td>
      <td>Dr. Seuss</td>
      <td>[[Toys &amp; Games, Puzzles, Jigsaw Puzzles]]</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0005069491</td>
      <td>NaN</td>
      <td>Nursery Rhymes Felt Book</td>
      <td>NaN</td>
      <td>{'Toys &amp; Games': 576683}</td>
      <td>http://ecx.images-amazon.com/images/I/51z4JDBC...</td>
      <td>NaN</td>
      <td>[[Toys &amp; Games]]</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0076561046</td>
      <td>Learn Fractions Decimals Percents using flash ...</td>
      <td>Fraction Decimal Percent Card Deck</td>
      <td>NaN</td>
      <td>{'Toys &amp; Games': 564211}</td>
      <td>http://ecx.images-amazon.com/images/I/51ObabPu...</td>
      <td>NaN</td>
      <td>[[Toys &amp; Games, Learning &amp; Education, Flash Ca...</td>
      <td>{'also_viewed': ['0075728680']}</td>
    </tr>
    <tr>
      <th>3</th>
      <td>0131358936</td>
      <td>New, Sealed. Fast Shipping with tracking, buy ...</td>
      <td>NaN</td>
      <td>36.22</td>
      <td>{'Software': 8080}</td>
      <td>http://ecx.images-amazon.com/images/I/51%2B7Ej...</td>
      <td>NaN</td>
      <td>[[Toys &amp; Games, Learning &amp; Education, Mathemat...</td>
      <td>{'also_bought': ['0321845536', '0078787572'], ...</td>
    </tr>
    <tr>
      <th>4</th>
      <td>0133642984</td>
      <td>NaN</td>
      <td>Algebra 2 California Teacher Center</td>
      <td>731.93</td>
      <td>{'Toys &amp; Games': 1150291}</td>
      <td>http://ecx.images-amazon.com/images/I/51VK%2BL...</td>
      <td>Prentice Hall</td>
      <td>[[Toys &amp; Games, Learning &amp; Education, Mathemat...</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>



You already had experience with the Amazon Reviews dataset. In a previous course, you created some functions to perform some processing over the reviews and metadata datasets. Let's recreate those functions.

<a name='3'></a>
## 3 - Creating Functions to Process Data

<a name='3.1'></a>
### 3.1 - Process Reviews

Complete the `process_review()` function to perform some transformations. Please follow the instructions in the code.


```python
def process_review(raw_df: pd.DataFrame) -> pd.DataFrame:    
    """Transformations steps for Reviews dataset

    Args:
        raw_df (DataFrame): Raw data loaded in dataframe

    Returns:
        DataFrame: Returned transformed dataframe
    """

    ### START CODE HERE ### (5 lines of code)
    
    # Convert the `unixReviewTime` column of the dataframe `raw_df` to date with the `to_datetime()` function
    # The timestamp is defined in seconds (use `s` for the `unit` parameter)
    raw_df['reviewTime'] = pd.to_datetime(raw_df['unixReviewTime'], unit='s')

    # Extract the year and month from the `reviewTime`, and save those values in new columns named `year` and `month`
    # You can apply `.dt.year` and `.dt.month` methods to `raw_df['reviewTime']` to do that
    raw_df['year'] = raw_df['reviewTime'].dt.year
    raw_df['month'] = raw_df['reviewTime'].dt.month

    # Create a new dataframe based on converting the `helpful` column from the `raw_df` into a list with the `to_list()` method
    # Set the column names as `helpful_votes` and `total_votes`
    df_helpful = pd.DataFrame(raw_df['helpful'].to_list(), columns=['helpful_votes', 'total_votes'])

    # With the `pd.concat()` function, concatenate the `raw_df` dataframe with `df_helpful`
    # Make sure that you drop the `helpful` column from `raw_df` with the `drop()` method and  set `axis` equal to 1
    target_df = pd.concat([raw_df.drop(columns=['helpful']), df_helpful], axis=1)
    
    ### END CODE HERE ###
    
    target_df['not_helpful_votes'] = target_df['total_votes'] - target_df['helpful_votes']
    
    return target_df

transformed_review_sample_df = process_review(raw_df=review_sample_df)
transformed_review_sample_df.head(2)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>reviewerID</th>
      <th>asin</th>
      <th>reviewerName</th>
      <th>reviewText</th>
      <th>overall</th>
      <th>summary</th>
      <th>unixReviewTime</th>
      <th>reviewTime</th>
      <th>year</th>
      <th>month</th>
      <th>helpful_votes</th>
      <th>total_votes</th>
      <th>not_helpful_votes</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>AMEVO2LY6VEJA</td>
      <td>0000191639</td>
      <td>Nicole Soeder</td>
      <td>Great product, thank you! Our son loved the pu...</td>
      <td>5.0</td>
      <td>Puzzles</td>
      <td>1388016000</td>
      <td>2013-12-26</td>
      <td>2013</td>
      <td>12</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>A3C9CSW3TJITGT</td>
      <td>0005069491</td>
      <td>Renee</td>
      <td>I love these felt nursery rhyme characters and...</td>
      <td>4.0</td>
      <td>Charming characters but busy work required</td>
      <td>1377561600</td>
      <td>2013-08-27</td>
      <td>2013</td>
      <td>8</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



<a name='3.2'></a>
### 3.2 - Process Metatada

3.2.1. Let's perform some small transformations over the metadata dataset. Follow the instructions in the code to complete the `process_metadata()` function.


```python
def process_metadata(raw_df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Function in charge of the transformation of the raw data of the
    Reviews Metadata.

    Args:
        raw_df (DataFrame): Raw data loaded in dataframe
        cols (list): List of columns to select
        cols_to_clean (list): List of columns 

    Returns:
        DataFrame: Returned transformed dataframe
    """

    ### START CODE HERE ### (6 lines of code)
    
    # Remove any records that have null values for the `salesRank` column. You should apply `dropna()` method to the dataframe `raw_df`
    # The value of the parameter `how` should be equal to `"any"`
    tmp_df = raw_df.dropna(subset=["salesRank"], how="any")

    # Extract the sales rank and category from the `salesRank` column into two new columns: `sales_category` as key and `sales_rank` as value
    df_rank = pd.DataFrame([{"sales_category": key, "sales_rank": value} for d in tmp_df["salesRank"].tolist() for key, value in d.items()])

    # Concatenate dataframes `tmp_df` and `df_rank`
    target_df = pd.concat([tmp_df, df_rank], axis=1)

    # Select the columns that don't contain arrays and the new columns (this line is complete)
    target_df = target_df[cols] 
    

    # Remove any record that has null values for the `asin`, `price` and `sales_rank` column
    # You should use `dropna()` method and the value of the parameter `how` should be equal to `"any"`
    target_df = target_df.dropna(subset=["asin", "price", "sales_rank"], how="any")

    # Fill the null values of the rest of the Dataframe with an empty string `""`. Use `fillna()` method to do that
    target_df = target_df.fillna("")
    
    ### END CODE HERE ###
    
    return target_df

processed_metadata_df = process_metadata(raw_df=metadata_sample_df, 
                                         cols=['asin', 'description', 'title', 'price', 'brand','sales_category','sales_rank']
                                         )
processed_metadata_df.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>asin</th>
      <th>description</th>
      <th>title</th>
      <th>price</th>
      <th>brand</th>
      <th>sales_category</th>
      <th>sales_rank</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0000191639</td>
      <td>Three Dr. Suess' Puzzles: Green Eggs and Ham, ...</td>
      <td>Dr. Suess 19163 Dr. Seuss Puzzle 3 Pack Bundle</td>
      <td>37.12</td>
      <td>Dr. Seuss</td>
      <td>Toys &amp; Games</td>
      <td>612379.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>0131358936</td>
      <td>New, Sealed. Fast Shipping with tracking, buy ...</td>
      <td></td>
      <td>36.22</td>
      <td></td>
      <td>Software</td>
      <td>8080.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>0133642984</td>
      <td></td>
      <td>Algebra 2 California Teacher Center</td>
      <td>731.93</td>
      <td>Prentice Hall</td>
      <td>Toys &amp; Games</td>
      <td>1150291.0</td>
    </tr>
    <tr>
      <th>6</th>
      <td>0375829695</td>
      <td>A collection of six 48-piece (that is,slightly...</td>
      <td>Dr. Seuss Jigsaw Puzzle Book: With Six 48-Piec...</td>
      <td>24.82</td>
      <td>Dr. Seuss</td>
      <td>Home &amp;amp; Kitchen</td>
      <td>590975.0</td>
    </tr>
    <tr>
      <th>10</th>
      <td>0439400066</td>
      <td>Send your mind into overdrive with this mind-b...</td>
      <td>3D Puzzle Buster</td>
      <td>99.15</td>
      <td></td>
      <td>Toys &amp; Games</td>
      <td>1616332.0</td>
    </tr>
  </tbody>
</table>
</div>



3.2.2. Once you have your data with some initial preprocessing, you have to join the data according to the ID of each product (`asin`). Do an inner join in this case as you are interested only in reviews for which you have product information.


```python
reviews_product_metadata_df = transformed_review_sample_df.merge(processed_metadata_df, left_on='asin', right_on='asin', how='inner')
reviews_product_metadata_df.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>reviewerID</th>
      <th>asin</th>
      <th>reviewerName</th>
      <th>reviewText</th>
      <th>overall</th>
      <th>summary</th>
      <th>unixReviewTime</th>
      <th>reviewTime</th>
      <th>year</th>
      <th>month</th>
      <th>helpful_votes</th>
      <th>total_votes</th>
      <th>not_helpful_votes</th>
      <th>description</th>
      <th>title</th>
      <th>price</th>
      <th>brand</th>
      <th>sales_category</th>
      <th>sales_rank</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>AMEVO2LY6VEJA</td>
      <td>0000191639</td>
      <td>Nicole Soeder</td>
      <td>Great product, thank you! Our son loved the pu...</td>
      <td>5.0</td>
      <td>Puzzles</td>
      <td>1388016000</td>
      <td>2013-12-26</td>
      <td>2013</td>
      <td>12</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>Three Dr. Suess' Puzzles: Green Eggs and Ham, ...</td>
      <td>Dr. Suess 19163 Dr. Seuss Puzzle 3 Pack Bundle</td>
      <td>37.12</td>
      <td>Dr. Seuss</td>
      <td>Toys &amp; Games</td>
      <td>612379.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>A2GGHHME9B6W4O</td>
      <td>0131358936</td>
      <td>Dalilah G.</td>
      <td>This is a great tool for any teacher using the...</td>
      <td>5.0</td>
      <td>Great CD-ROM</td>
      <td>1382400000</td>
      <td>2013-10-22</td>
      <td>2013</td>
      <td>10</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>New, Sealed. Fast Shipping with tracking, buy ...</td>
      <td></td>
      <td>36.22</td>
      <td></td>
      <td>Software</td>
      <td>8080.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>A1FSLDH43ORWZP</td>
      <td>0133642984</td>
      <td>Dayna English</td>
      <td>Although not as streamlined as the Algebra I m...</td>
      <td>5.0</td>
      <td>Algebra II -- presentation materials</td>
      <td>1374278400</td>
      <td>2013-07-20</td>
      <td>2013</td>
      <td>7</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td></td>
      <td>Algebra 2 California Teacher Center</td>
      <td>731.93</td>
      <td>Prentice Hall</td>
      <td>Toys &amp; Games</td>
      <td>1150291.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>AYVR1MQCTNU5D</td>
      <td>0375829695</td>
      <td>annie</td>
      <td>What a great theme for a puzzle book. My daugh...</td>
      <td>5.0</td>
      <td>So cute!!</td>
      <td>1291939200</td>
      <td>2010-12-10</td>
      <td>2010</td>
      <td>12</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>A collection of six 48-piece (that is,slightly...</td>
      <td>Dr. Seuss Jigsaw Puzzle Book: With Six 48-Piec...</td>
      <td>24.82</td>
      <td>Dr. Seuss</td>
      <td>Home &amp;amp; Kitchen</td>
      <td>590975.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>A3CJHKFHHQJP2K</td>
      <td>0375829695</td>
      <td>Beth Sharo "bookmom"</td>
      <td>My son got this book for his birthday.  He lov...</td>
      <td>1.0</td>
      <td>Disappointing Puzzle Book</td>
      <td>1297209600</td>
      <td>2011-02-09</td>
      <td>2011</td>
      <td>2</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>A collection of six 48-piece (that is,slightly...</td>
      <td>Dr. Seuss Jigsaw Puzzle Book: With Six 48-Piec...</td>
      <td>24.82</td>
      <td>Dr. Seuss</td>
      <td>Home &amp;amp; Kitchen</td>
      <td>590975.0</td>
    </tr>
  </tbody>
</table>
</div>



3.2.3. Before starting the next processing steps, you can convert the column names to lowercase. Furthermore, some columns that are not necessary for the model can be deleted.


```python
reviews_product_metadata_df.columns = [col.lower() for col in reviews_product_metadata_df.columns]
reviews_product_metadata_df.drop(columns=['reviewername', 'summary', 'unixreviewtime', 'reviewtime'], inplace=True)
reviews_product_metadata_df.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>reviewerid</th>
      <th>asin</th>
      <th>reviewtext</th>
      <th>overall</th>
      <th>year</th>
      <th>month</th>
      <th>helpful_votes</th>
      <th>total_votes</th>
      <th>not_helpful_votes</th>
      <th>description</th>
      <th>title</th>
      <th>price</th>
      <th>brand</th>
      <th>sales_category</th>
      <th>sales_rank</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>AMEVO2LY6VEJA</td>
      <td>0000191639</td>
      <td>Great product, thank you! Our son loved the pu...</td>
      <td>5.0</td>
      <td>2013</td>
      <td>12</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>Three Dr. Suess' Puzzles: Green Eggs and Ham, ...</td>
      <td>Dr. Suess 19163 Dr. Seuss Puzzle 3 Pack Bundle</td>
      <td>37.12</td>
      <td>Dr. Seuss</td>
      <td>Toys &amp; Games</td>
      <td>612379.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>A2GGHHME9B6W4O</td>
      <td>0131358936</td>
      <td>This is a great tool for any teacher using the...</td>
      <td>5.0</td>
      <td>2013</td>
      <td>10</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>New, Sealed. Fast Shipping with tracking, buy ...</td>
      <td></td>
      <td>36.22</td>
      <td></td>
      <td>Software</td>
      <td>8080.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>A1FSLDH43ORWZP</td>
      <td>0133642984</td>
      <td>Although not as streamlined as the Algebra I m...</td>
      <td>5.0</td>
      <td>2013</td>
      <td>7</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td></td>
      <td>Algebra 2 California Teacher Center</td>
      <td>731.93</td>
      <td>Prentice Hall</td>
      <td>Toys &amp; Games</td>
      <td>1150291.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>AYVR1MQCTNU5D</td>
      <td>0375829695</td>
      <td>What a great theme for a puzzle book. My daugh...</td>
      <td>5.0</td>
      <td>2010</td>
      <td>12</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>A collection of six 48-piece (that is,slightly...</td>
      <td>Dr. Seuss Jigsaw Puzzle Book: With Six 48-Piec...</td>
      <td>24.82</td>
      <td>Dr. Seuss</td>
      <td>Home &amp;amp; Kitchen</td>
      <td>590975.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>A3CJHKFHHQJP2K</td>
      <td>0375829695</td>
      <td>My son got this book for his birthday.  He lov...</td>
      <td>1.0</td>
      <td>2011</td>
      <td>2</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>A collection of six 48-piece (that is,slightly...</td>
      <td>Dr. Seuss Jigsaw Puzzle Book: With Six 48-Piec...</td>
      <td>24.82</td>
      <td>Dr. Seuss</td>
      <td>Home &amp;amp; Kitchen</td>
      <td>590975.0</td>
    </tr>
  </tbody>
</table>
</div>



3.2.4. In the dataset, you can see that there are two possible categorical variables: `brand` and `sales_category`. Let's explore them to understand their structure and decide the type of processing that you will implement.


```python
reviews_product_metadata_df['brand'].value_counts()
```




    brand
    Wizards of the Coast                                954
    Mudpuppy                                            636
    Days of Wonder                                      619
                                                        526
    Creations by You                                    424
                                                       ... 
    Star Fleet Battles ADB                                1
    Relationship Enrichment Systems                       1
    Flames of War - WWII - Core Rules &amp; Assorted      1
    Yottoy                                                1
    Prentice Hall                                         1
    Name: count, Length: 86, dtype: int64




```python
reviews_product_metadata_df['sales_category'].value_counts()
```




    sales_category
    Toys & Games               3715
    Software                    667
    Home &amp; Kitchen           58
    Arts, Crafts & Sewing        18
    Electronics                   2
    Industrial & Scientific       2
    Sports &amp; Outdoors         2
    Name: count, dtype: int64



<a name='3.3'></a>
### 3.3 - Process Text Data

For text data, you have the following columns `reviewtext`, `description` and `title`. Although the `brand` and `sales_category` do not contain actual text and are actually categorical string variables, you can process those strings in a similar way as the text fields. 

For that, you will use the `re` python library. The processing steps to be performed over these text and string data will be more focused on cleaning:

- Lowercasing: Convert all text to lowercase to maintain consistency.
- Remove Punctuation: Strip out unnecessary punctuation.
- Remove Special Characters: Clean any special characters that are not relevant to the task.
- Remove leading, trailing or multiple spaces.

Further processing such as tokenization can be performed by some ML models.

3.3.1. Complete the `clean_text` function using the instructions in the code.


```python
def clean_text(text: str) -> str:

    """Function in charge of cleaning text data by converting to lowercase 
    and removing punctuation and special characters.

    Args:
        text (str): Raw text string to be cleaned

    Returns:
        str: Cleaned text string
    """
    
    ### START CODE HERE ### (2 lines of code)
    # Take the `text` string and convert it to lowercase with the `lower` method that Python strings have
    text = text.lower()

    # Pass the `text` to the `re.sub()` method as the third parameter. This removes punctuation and special characters
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    ### END CODE HERE ###
    
    return text

columns_to_clean = ['reviewtext', 'description', 'title', 'brand', 'sales_category']

for column in columns_to_clean:
    # Applying cleaning function
    reviews_product_metadata_df[column] = reviews_product_metadata_df[column].apply(clean_text) 

    # Deleting unnecessary spaces
    reviews_product_metadata_df[column] = reviews_product_metadata_df[column].str.strip().str.replace('\s+', ' ', regex=True)

reviews_product_metadata_df[columns_to_clean].head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>reviewtext</th>
      <th>description</th>
      <th>title</th>
      <th>brand</th>
      <th>sales_category</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>great product thank you our son loved the puzz...</td>
      <td>three dr suess puzzles green eggs and ham favo...</td>
      <td>dr suess dr seuss puzzle pack bundle</td>
      <td>dr seuss</td>
      <td>toys games</td>
    </tr>
    <tr>
      <th>1</th>
      <td>this is a great tool for any teacher using the...</td>
      <td>new sealed fast shipping with tracking buy wit...</td>
      <td></td>
      <td></td>
      <td>software</td>
    </tr>
    <tr>
      <th>2</th>
      <td>although not as streamlined as the algebra i m...</td>
      <td></td>
      <td>algebra california teacher center</td>
      <td>prentice hall</td>
      <td>toys games</td>
    </tr>
    <tr>
      <th>3</th>
      <td>what a great theme for a puzzle book my daught...</td>
      <td>a collection of six piece that isslightlychall...</td>
      <td>dr seuss jigsaw puzzle book with six piece puz...</td>
      <td>dr seuss</td>
      <td>home amp kitchen</td>
    </tr>
    <tr>
      <th>4</th>
      <td>my son got this book for his birthday he loves...</td>
      <td>a collection of six piece that isslightlychall...</td>
      <td>dr seuss jigsaw puzzle book with six piece puz...</td>
      <td>dr seuss</td>
      <td>home amp kitchen</td>
    </tr>
  </tbody>
</table>
</div>



3.3.2. As a last step to process your text data, you are asked to create a column that summarizes the product information. This information can be found between the `title` and `description` fields. You are asked to use the `title` as the primary product information field and for rows where the product's title is not available, you can use the `description`.


```python
### START CODE HERE ### (3 lines of code)

# Take `title` column of the dataframe `reviews_product_metadata_df` and use `replace()` method to replace empty strings with NaN
reviews_product_metadata_df['title'] = reviews_product_metadata_df['title'].replace('', np.nan)

# Fill NaN values in title with the description
# Use the `fillna()` dataframe method to fill the missing values from the `title` with those from `description` column of the dataframe `reviews_product_metadata_df`
reviews_product_metadata_df['product_information'] = reviews_product_metadata_df['title'].fillna(reviews_product_metadata_df['description'])

# Drop `title` and `description` columns of the dataframe `reviews_product_metadata_df`
reviews_product_metadata_df.drop(columns=['title', 'description'], inplace=True)

### END CODE HERE ###

reviews_product_metadata_df.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>reviewerid</th>
      <th>asin</th>
      <th>reviewtext</th>
      <th>overall</th>
      <th>year</th>
      <th>month</th>
      <th>helpful_votes</th>
      <th>total_votes</th>
      <th>not_helpful_votes</th>
      <th>price</th>
      <th>brand</th>
      <th>sales_category</th>
      <th>sales_rank</th>
      <th>product_information</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>AMEVO2LY6VEJA</td>
      <td>0000191639</td>
      <td>great product thank you our son loved the puzz...</td>
      <td>5.0</td>
      <td>2013</td>
      <td>12</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>37.12</td>
      <td>dr seuss</td>
      <td>toys games</td>
      <td>612379.0</td>
      <td>dr suess dr seuss puzzle pack bundle</td>
    </tr>
    <tr>
      <th>1</th>
      <td>A2GGHHME9B6W4O</td>
      <td>0131358936</td>
      <td>this is a great tool for any teacher using the...</td>
      <td>5.0</td>
      <td>2013</td>
      <td>10</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>36.22</td>
      <td></td>
      <td>software</td>
      <td>8080.0</td>
      <td>new sealed fast shipping with tracking buy wit...</td>
    </tr>
    <tr>
      <th>2</th>
      <td>A1FSLDH43ORWZP</td>
      <td>0133642984</td>
      <td>although not as streamlined as the algebra i m...</td>
      <td>5.0</td>
      <td>2013</td>
      <td>7</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>731.93</td>
      <td>prentice hall</td>
      <td>toys games</td>
      <td>1150291.0</td>
      <td>algebra california teacher center</td>
    </tr>
    <tr>
      <th>3</th>
      <td>AYVR1MQCTNU5D</td>
      <td>0375829695</td>
      <td>what a great theme for a puzzle book my daught...</td>
      <td>5.0</td>
      <td>2010</td>
      <td>12</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>24.82</td>
      <td>dr seuss</td>
      <td>home amp kitchen</td>
      <td>590975.0</td>
      <td>dr seuss jigsaw puzzle book with six piece puz...</td>
    </tr>
    <tr>
      <th>4</th>
      <td>A3CJHKFHHQJP2K</td>
      <td>0375829695</td>
      <td>my son got this book for his birthday he loves...</td>
      <td>1.0</td>
      <td>2011</td>
      <td>2</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>24.82</td>
      <td>dr seuss</td>
      <td>home amp kitchen</td>
      <td>590975.0</td>
      <td>dr seuss jigsaw puzzle book with six piece puz...</td>
    </tr>
  </tbody>
</table>
</div>



Other types of processing steps for text data may include deleting stop words, lemmatization or tokenization, but the utility of those steps may depend on the type of ML model to use or can directly be done by the model itself. For this lab, you are not required to implement further processing steps.

<a name='3.4'></a>
### 3.4 - Process Numerical Variables

3.4.1. You can see that the joined dataset has, apart from the label `overall`, two numerical variables: `price` and `sales_rank`. You have already processed this type of data in the previous lab, so you will implement a similar approach by performing a standardization over those two variables using `scikit-learn`.


```python
reviews_num_columns = ["price", "sales_rank"]

### START CODE HERE ### (3 lines of code)

# Create a `StandardScaler` instance
reviews_num_std_scaler = StandardScaler()

# Compute the mean and standard deviation statistics over the `reviews_num_columns` of the dataframe `reviews_product_metadata_df`
# Use `fit()` method applied to the `reviews_num_std_scaler`
reviews_num_std_scaler.fit(reviews_product_metadata_df[reviews_num_columns])

# Perform the transformation over the `reviews_num_columns` of the datafram `reviews_product_metadata_df` 
# with the `transform()` method applied to the `reviews_num_std_scaler`
scaled_price_sales_rank = reviews_num_std_scaler.transform(reviews_product_metadata_df[reviews_num_columns])

### END CODE HERE ###

# Convert to pandas DF
scaled_price_sales_rank_df = pd.DataFrame(scaled_price_sales_rank, columns=reviews_num_columns, index=reviews_product_metadata_df.index)

scaled_price_sales_rank_df.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>price</th>
      <th>sales_rank</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0.103559</td>
      <td>0.730212</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0.089188</td>
      <td>-0.716717</td>
    </tr>
    <tr>
      <th>2</th>
      <td>11.197485</td>
      <td>2.018184</td>
    </tr>
    <tr>
      <th>3</th>
      <td>-0.092834</td>
      <td>0.678962</td>
    </tr>
    <tr>
      <th>4</th>
      <td>-0.092834</td>
      <td>0.678962</td>
    </tr>
  </tbody>
</table>
</div>



3.4.2. Add the `scaled_price_sales_rank_df` to the `reviews_product_metadata_df` dataframe.


```python
# Drop the original column values
reviews_product_metadata_df.drop(columns=reviews_num_columns, inplace=True)

# Add the scaled values
reviews_product_metadata_df = pd.concat([reviews_product_metadata_df, scaled_price_sales_rank_df], axis=1)

reviews_product_metadata_df.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>reviewerid</th>
      <th>asin</th>
      <th>reviewtext</th>
      <th>overall</th>
      <th>year</th>
      <th>month</th>
      <th>helpful_votes</th>
      <th>total_votes</th>
      <th>not_helpful_votes</th>
      <th>brand</th>
      <th>sales_category</th>
      <th>product_information</th>
      <th>price</th>
      <th>sales_rank</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>AMEVO2LY6VEJA</td>
      <td>0000191639</td>
      <td>great product thank you our son loved the puzz...</td>
      <td>5.0</td>
      <td>2013</td>
      <td>12</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>dr seuss</td>
      <td>toys games</td>
      <td>dr suess dr seuss puzzle pack bundle</td>
      <td>0.103559</td>
      <td>0.730212</td>
    </tr>
    <tr>
      <th>1</th>
      <td>A2GGHHME9B6W4O</td>
      <td>0131358936</td>
      <td>this is a great tool for any teacher using the...</td>
      <td>5.0</td>
      <td>2013</td>
      <td>10</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td></td>
      <td>software</td>
      <td>new sealed fast shipping with tracking buy wit...</td>
      <td>0.089188</td>
      <td>-0.716717</td>
    </tr>
    <tr>
      <th>2</th>
      <td>A1FSLDH43ORWZP</td>
      <td>0133642984</td>
      <td>although not as streamlined as the algebra i m...</td>
      <td>5.0</td>
      <td>2013</td>
      <td>7</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>prentice hall</td>
      <td>toys games</td>
      <td>algebra california teacher center</td>
      <td>11.197485</td>
      <td>2.018184</td>
    </tr>
    <tr>
      <th>3</th>
      <td>AYVR1MQCTNU5D</td>
      <td>0375829695</td>
      <td>what a great theme for a puzzle book my daught...</td>
      <td>5.0</td>
      <td>2010</td>
      <td>12</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>dr seuss</td>
      <td>home amp kitchen</td>
      <td>dr seuss jigsaw puzzle book with six piece puz...</td>
      <td>-0.092834</td>
      <td>0.678962</td>
    </tr>
    <tr>
      <th>4</th>
      <td>A3CJHKFHHQJP2K</td>
      <td>0375829695</td>
      <td>my son got this book for his birthday he loves...</td>
      <td>1.0</td>
      <td>2011</td>
      <td>2</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>dr seuss</td>
      <td>home amp kitchen</td>
      <td>dr seuss jigsaw puzzle book with six piece puz...</td>
      <td>-0.092834</td>
      <td>0.678962</td>
    </tr>
  </tbody>
</table>
</div>



3.4.3. As a last step, you are going to create a pair of new features based on the `helpful_votes`, `total_votes` and `not_helpful_votes`. The meaning of those three fields is the following: 
- `helpful_votes` represents the number of users who found the review helpful.
- `total_votes` represents the total number of users who voted on the review's helpfulness.
- `not_helpful_votes` represents the number of users who didn't find the review helpful.

Create two new features based on the ratios between these columns, named `helpful_ratio` and `not_helpful_ratio`:


```python
# Helpful ratio
reviews_product_metadata_df['helpful_ratio'] = reviews_product_metadata_df[['helpful_votes', 'total_votes']].apply(lambda x: x['helpful_votes']/x['total_votes'] if x['total_votes'] != 0 else 0, axis=1)

# Not helpful ratio
reviews_product_metadata_df['not_helpful_ratio'] = reviews_product_metadata_df[['not_helpful_votes', 'total_votes']].apply(lambda x: x['not_helpful_votes']/x['total_votes'] if x['total_votes'] != 0 else 0, axis=1)

reviews_product_metadata_df.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>reviewerid</th>
      <th>asin</th>
      <th>reviewtext</th>
      <th>overall</th>
      <th>year</th>
      <th>month</th>
      <th>helpful_votes</th>
      <th>total_votes</th>
      <th>not_helpful_votes</th>
      <th>brand</th>
      <th>sales_category</th>
      <th>product_information</th>
      <th>price</th>
      <th>sales_rank</th>
      <th>helpful_ratio</th>
      <th>not_helpful_ratio</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>AMEVO2LY6VEJA</td>
      <td>0000191639</td>
      <td>great product thank you our son loved the puzz...</td>
      <td>5.0</td>
      <td>2013</td>
      <td>12</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>dr seuss</td>
      <td>toys games</td>
      <td>dr suess dr seuss puzzle pack bundle</td>
      <td>0.103559</td>
      <td>0.730212</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>A2GGHHME9B6W4O</td>
      <td>0131358936</td>
      <td>this is a great tool for any teacher using the...</td>
      <td>5.0</td>
      <td>2013</td>
      <td>10</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td></td>
      <td>software</td>
      <td>new sealed fast shipping with tracking buy wit...</td>
      <td>0.089188</td>
      <td>-0.716717</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>A1FSLDH43ORWZP</td>
      <td>0133642984</td>
      <td>although not as streamlined as the algebra i m...</td>
      <td>5.0</td>
      <td>2013</td>
      <td>7</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>prentice hall</td>
      <td>toys games</td>
      <td>algebra california teacher center</td>
      <td>11.197485</td>
      <td>2.018184</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>AYVR1MQCTNU5D</td>
      <td>0375829695</td>
      <td>what a great theme for a puzzle book my daught...</td>
      <td>5.0</td>
      <td>2010</td>
      <td>12</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>dr seuss</td>
      <td>home amp kitchen</td>
      <td>dr seuss jigsaw puzzle book with six piece puz...</td>
      <td>-0.092834</td>
      <td>0.678962</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>A3CJHKFHHQJP2K</td>
      <td>0375829695</td>
      <td>my son got this book for his birthday he loves...</td>
      <td>1.0</td>
      <td>2011</td>
      <td>2</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>dr seuss</td>
      <td>home amp kitchen</td>
      <td>dr seuss jigsaw puzzle book with six piece puz...</td>
      <td>-0.092834</td>
      <td>0.678962</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
  </tbody>
</table>
</div>



<a name='3.5'></a>
### 3.5 - Process Categorical Variables

You can find two categorical variables in the dataset: `brand` and `sales_category`. When you explore the sample data, you can see that the `sales_category` column has 7 nominal categories, while the `brand` column has 86 categories. Using a categorical variable with a large number of unique categories can pose challenges for some ML models, in terms of memory and computational complexity. Although the strategies to deal with this type of variable are out of the scope of this course, you will use an approach named frequency encoding or count encoding. This is a technique that encodes categorical features based on the frequency of each category. 

3.5.1. In the following cell, you will compute the frequency of each category of the `brand` column with the `value_counts` method, then, those categories are mapped back to the dataframe so instead of having the string categories, you will have the frequency of each category.


```python
# Frequency encoding
frequency_encoding_brand = reviews_product_metadata_df['brand'].value_counts().to_dict()
reviews_product_metadata_df['encoded_brand'] = reviews_product_metadata_df['brand'].map(frequency_encoding_brand)

# Dropping the brand column
reviews_product_metadata_df.drop(columns=["brand"], inplace=True)

reviews_product_metadata_df.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>reviewerid</th>
      <th>asin</th>
      <th>reviewtext</th>
      <th>overall</th>
      <th>year</th>
      <th>month</th>
      <th>helpful_votes</th>
      <th>total_votes</th>
      <th>not_helpful_votes</th>
      <th>sales_category</th>
      <th>product_information</th>
      <th>price</th>
      <th>sales_rank</th>
      <th>helpful_ratio</th>
      <th>not_helpful_ratio</th>
      <th>encoded_brand</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>AMEVO2LY6VEJA</td>
      <td>0000191639</td>
      <td>great product thank you our son loved the puzz...</td>
      <td>5.0</td>
      <td>2013</td>
      <td>12</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>toys games</td>
      <td>dr suess dr seuss puzzle pack bundle</td>
      <td>0.103559</td>
      <td>0.730212</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>10</td>
    </tr>
    <tr>
      <th>1</th>
      <td>A2GGHHME9B6W4O</td>
      <td>0131358936</td>
      <td>this is a great tool for any teacher using the...</td>
      <td>5.0</td>
      <td>2013</td>
      <td>10</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>software</td>
      <td>new sealed fast shipping with tracking buy wit...</td>
      <td>0.089188</td>
      <td>-0.716717</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>526</td>
    </tr>
    <tr>
      <th>2</th>
      <td>A1FSLDH43ORWZP</td>
      <td>0133642984</td>
      <td>although not as streamlined as the algebra i m...</td>
      <td>5.0</td>
      <td>2013</td>
      <td>7</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>toys games</td>
      <td>algebra california teacher center</td>
      <td>11.197485</td>
      <td>2.018184</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>3</th>
      <td>AYVR1MQCTNU5D</td>
      <td>0375829695</td>
      <td>what a great theme for a puzzle book my daught...</td>
      <td>5.0</td>
      <td>2010</td>
      <td>12</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>home amp kitchen</td>
      <td>dr seuss jigsaw puzzle book with six piece puz...</td>
      <td>-0.092834</td>
      <td>0.678962</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>10</td>
    </tr>
    <tr>
      <th>4</th>
      <td>A3CJHKFHHQJP2K</td>
      <td>0375829695</td>
      <td>my son got this book for his birthday he loves...</td>
      <td>1.0</td>
      <td>2011</td>
      <td>2</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>home amp kitchen</td>
      <td>dr seuss jigsaw puzzle book with six piece puz...</td>
      <td>-0.092834</td>
      <td>0.678962</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>10</td>
    </tr>
  </tbody>
</table>
</div>



3.5.2. For the `sales_category` column, you can use the `OneHotEncoder` class given that the number of categories is not that large.


```python
### START CODE HERE ### (5 lines of code)

# Create an instance of the `OneHotEncoder` class. Use the `"ignore"` value for the `handle_unknown` parameter
sales_category_ohe = OneHotEncoder(handle_unknown="ignore")

# Copy the column `sales_category` of the dataframe `reviews_product_metadata_df` with the method `copy()`
# You will need to use double square brackets to output it as a dataframe, not a series
sales_category_df = reviews_product_metadata_df[["sales_category"]].copy()

# Convert string categories into lowercase (the code line is complete)
sales_category_df = sales_category_df.map(lambda x: x.strip().lower()) 


# Fit your encoder `sales_category_ohe` to the `sales_category_df` dataframe with the `fit()` method
sales_category_ohe.fit(sales_category_df)

# Apply the transformation using the same encoder over the same column. You will need to use the `transform()` method
# Chain `todense()` method to create a dense matrix for the encoded data
encoded_sales_category = sales_category_ohe.transform(sales_category_df).todense()

### END CODE HERE ###

# Convert the result to DataFrame
encoded_sales_category_df = pd.DataFrame(
    encoded_sales_category, 
    columns=sales_category_ohe.get_feature_names_out(["sales_category"]),
    index=reviews_product_metadata_df.index
)

encoded_sales_category_df.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>sales_category_arts crafts sewing</th>
      <th>sales_category_electronics</th>
      <th>sales_category_home amp kitchen</th>
      <th>sales_category_industrial scientific</th>
      <th>sales_category_software</th>
      <th>sales_category_sports amp outdoors</th>
      <th>sales_category_toys games</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
  </tbody>
</table>
</div>



3.5.3. Add the new dataset with the transformed values to the original dataset.


```python
# Drop the original column values
reviews_product_metadata_df.drop(columns=["sales_category"], inplace=True)

# Add the scaled values
reviews_product_metadata_df = pd.concat([reviews_product_metadata_df, encoded_sales_category_df], axis=1)

reviews_product_metadata_df.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>reviewerid</th>
      <th>asin</th>
      <th>reviewtext</th>
      <th>overall</th>
      <th>year</th>
      <th>month</th>
      <th>helpful_votes</th>
      <th>total_votes</th>
      <th>not_helpful_votes</th>
      <th>product_information</th>
      <th>price</th>
      <th>sales_rank</th>
      <th>helpful_ratio</th>
      <th>not_helpful_ratio</th>
      <th>encoded_brand</th>
      <th>sales_category_arts crafts sewing</th>
      <th>sales_category_electronics</th>
      <th>sales_category_home amp kitchen</th>
      <th>sales_category_industrial scientific</th>
      <th>sales_category_software</th>
      <th>sales_category_sports amp outdoors</th>
      <th>sales_category_toys games</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>AMEVO2LY6VEJA</td>
      <td>0000191639</td>
      <td>great product thank you our son loved the puzz...</td>
      <td>5.0</td>
      <td>2013</td>
      <td>12</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>dr suess dr seuss puzzle pack bundle</td>
      <td>0.103559</td>
      <td>0.730212</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>10</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>A2GGHHME9B6W4O</td>
      <td>0131358936</td>
      <td>this is a great tool for any teacher using the...</td>
      <td>5.0</td>
      <td>2013</td>
      <td>10</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>new sealed fast shipping with tracking buy wit...</td>
      <td>0.089188</td>
      <td>-0.716717</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>526</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>A1FSLDH43ORWZP</td>
      <td>0133642984</td>
      <td>although not as streamlined as the algebra i m...</td>
      <td>5.0</td>
      <td>2013</td>
      <td>7</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>algebra california teacher center</td>
      <td>11.197485</td>
      <td>2.018184</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>AYVR1MQCTNU5D</td>
      <td>0375829695</td>
      <td>what a great theme for a puzzle book my daught...</td>
      <td>5.0</td>
      <td>2010</td>
      <td>12</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>dr seuss jigsaw puzzle book with six piece puz...</td>
      <td>-0.092834</td>
      <td>0.678962</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>10</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>A3CJHKFHHQJP2K</td>
      <td>0375829695</td>
      <td>my son got this book for his birthday he loves...</td>
      <td>1.0</td>
      <td>2011</td>
      <td>2</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>dr seuss jigsaw puzzle book with six piece puz...</td>
      <td>-0.092834</td>
      <td>0.678962</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>10</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
  </tbody>
</table>
</div>



<a name='4'></a>
## 4 - Split Data and Create Text Embeddings

<a name='4.1'></a>
### 4.1 - Split Data

Now, that you have your dataset processed, you are going to split it into three subdatasets. The first one will contain all the information about the user's review and product features, except the `reviewtext` and `product_information` columns; those two columns will be stored in two different datasets and you will refer to them through the `reviewerid` and `asin` identifiers to join with the main table. You will make this split to process reviews and product information only once for each unique review or product value.


```python
# Creating reviews dataset
reviews_text_df = reviews_product_metadata_df[["reviewerid", "asin", "reviewtext"]].copy()
reviews_text_df.drop_duplicates(inplace=True)

# Creating products dataset
product_information_df = reviews_product_metadata_df[["asin", "product_information"]].copy()
product_information_df.drop_duplicates(inplace=True)

# Dropping unnecessary columns from the original DataFrame
reviews_product_metadata_df.drop(columns=["reviewtext", "product_information"], inplace=True)
```


```python
reviews_text_df.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>reviewerid</th>
      <th>asin</th>
      <th>reviewtext</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>AMEVO2LY6VEJA</td>
      <td>0000191639</td>
      <td>great product thank you our son loved the puzz...</td>
    </tr>
    <tr>
      <th>1</th>
      <td>A2GGHHME9B6W4O</td>
      <td>0131358936</td>
      <td>this is a great tool for any teacher using the...</td>
    </tr>
    <tr>
      <th>2</th>
      <td>A1FSLDH43ORWZP</td>
      <td>0133642984</td>
      <td>although not as streamlined as the algebra i m...</td>
    </tr>
    <tr>
      <th>3</th>
      <td>AYVR1MQCTNU5D</td>
      <td>0375829695</td>
      <td>what a great theme for a puzzle book my daught...</td>
    </tr>
    <tr>
      <th>4</th>
      <td>A3CJHKFHHQJP2K</td>
      <td>0375829695</td>
      <td>my son got this book for his birthday he loves...</td>
    </tr>
  </tbody>
</table>
</div>




```python
product_information_df.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>asin</th>
      <th>product_information</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0000191639</td>
      <td>dr suess dr seuss puzzle pack bundle</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0131358936</td>
      <td>new sealed fast shipping with tracking buy wit...</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0133642984</td>
      <td>algebra california teacher center</td>
    </tr>
    <tr>
      <th>3</th>
      <td>0375829695</td>
      <td>dr seuss jigsaw puzzle book with six piece puz...</td>
    </tr>
    <tr>
      <th>12</th>
      <td>0439400066</td>
      <td>d puzzle buster</td>
    </tr>
  </tbody>
</table>
</div>




```python
reviews_product_metadata_df.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>reviewerid</th>
      <th>asin</th>
      <th>overall</th>
      <th>year</th>
      <th>month</th>
      <th>helpful_votes</th>
      <th>total_votes</th>
      <th>not_helpful_votes</th>
      <th>price</th>
      <th>sales_rank</th>
      <th>helpful_ratio</th>
      <th>not_helpful_ratio</th>
      <th>encoded_brand</th>
      <th>sales_category_arts crafts sewing</th>
      <th>sales_category_electronics</th>
      <th>sales_category_home amp kitchen</th>
      <th>sales_category_industrial scientific</th>
      <th>sales_category_software</th>
      <th>sales_category_sports amp outdoors</th>
      <th>sales_category_toys games</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>AMEVO2LY6VEJA</td>
      <td>0000191639</td>
      <td>5.0</td>
      <td>2013</td>
      <td>12</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0.103559</td>
      <td>0.730212</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>10</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>A2GGHHME9B6W4O</td>
      <td>0131358936</td>
      <td>5.0</td>
      <td>2013</td>
      <td>10</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0.089188</td>
      <td>-0.716717</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>526</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>A1FSLDH43ORWZP</td>
      <td>0133642984</td>
      <td>5.0</td>
      <td>2013</td>
      <td>7</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>11.197485</td>
      <td>2.018184</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>AYVR1MQCTNU5D</td>
      <td>0375829695</td>
      <td>5.0</td>
      <td>2010</td>
      <td>12</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>-0.092834</td>
      <td>0.678962</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>10</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>A3CJHKFHHQJP2K</td>
      <td>0375829695</td>
      <td>1.0</td>
      <td>2011</td>
      <td>2</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>-0.092834</td>
      <td>0.678962</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>10</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
  </tbody>
</table>
</div>




```python
reviews_product_metadata_df.shape
```




    (4464, 20)



<a name='4.2'></a>
### 4.2 - Create Text Embeddings

Now that the data has been separated into three different datasets, let's create embeddings for the text data. You will create embeddings for the `product_information` field in the `product_information_df` dataframe and the `reviewtext` field in the `reviews_text_df` dataframe.

Just as a refresher, an **embedding** is a numerical representation of text, documents, images, or audio. This representation captures the semantic meaning of the embedded content while representing the data in a more compact form. The ML team has provided an API with the Sentence Transformer library, running the [`all-MiniLM-L6-v2`](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) model, this is a multipurpose and lightweight sentence transformer model that can map sentences and paragraphs to a 384-dimensional vector. The model has been provisioned in an EC2 instance, we will not go into the details about the ML model and how it was deployed, as this is out of the scope of this course. All you need to know is that you can interact with this model through API calls, which is the standard nowadays to consume some LLM services.

4.2.1. The `ENDPOINT_URL` variable that you defined at the beginning of the lab is the endpoint that you will use to interact with the API. Furthermore, you are provided with a function to make API requests for the model to return the embeddings of a provided text. You should already be familiar with requests to REST APIs, so you can see that this particular call is a POST call in which you also send data to the endpoint through the `payload` dictionary.


```python
def get_text_embeddings(endpoint_url: str , text: Union[str, List[str]]): 
    
    payload = {"text": text}

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(endpoint_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
  
        return response.json()
    
    except Exception as err:
        print(f"Error: {err}")
```

4.2.2. As an example of the result of the API call, you can execute the following cell:


```python
# Text to send to the API call
text = product_information_df.iloc[0]['product_information']

# Performing API call and getting the result
embedding_response = get_text_embeddings(endpoint_url=ENDPOINT_URL, text=text)
embeddings = embedding_response['body']

print(f"Text sent to the API: {text}")
print(f"Length of the embedding from the response: {len(embeddings)}")
print(f"A subset of the returned embeddings with the first 10 elements: {embeddings[:10]}")

```

    Text sent to the API: dr suess dr seuss puzzle pack bundle
    Length of the embedding from the response: 384
    A subset of the returned embeddings with the first 10 elements: [-0.03424278646707535, 0.022777101024985313, -0.0032790950499475002, -0.030152201652526855, 0.003919770009815693, 0.03298501297831535, 0.05947704613208771, 0.06927525252103806, -0.0616498626768589, 0.02031721919775009]


You can see that the size of the returned embedding is of 384 elements. This size will be the same for all vector embeddings that will be returned. 

4.2.3. Let's process the text for the `product_information_df` DataFrame and get the corresponding embeddings. You are going to divide the dataframe in chunks to be more manageable; for that, use the `split_dataframe` function provided below.


```python
def split_dataframe(df, chunk_size=20):
    chunks = list()
    num_chunks = (len(df) + chunk_size - 1) // chunk_size 
    
    for i in range(num_chunks):
        chunk = df[i*chunk_size:(i+1)*chunk_size]
        if not chunk.empty:
            chunks.append(chunk)
    return chunks

# Split the `product_information_df` with the default chunk size of 20 rows per chunk
list_df = split_dataframe(df=product_information_df)
```

4.2.4. Given that you need to perform several API calls and the dimension of your embeddings is 384 elements, to avoid exceeding the usage of RAM of your development environment, you will perform API calls to get the embeddings of a chunk of data and then insert the corresponding data directly into the database. Let's create the connection to the database through the `psycopg2` package. Then, in a similar way as you did in the Course 1 Week 4 Assignment, you need to enable the `vector` extension in your PostgreSQL database. 


```python
conn = psycopg2.connect( 
    database=DBNAME, user=DBUSER, 
    password=DBPASSWORD, host=DBHOST, port=DBPORT
) 

# Set autocommit to true
conn.autocommit = True

# Create cursor
cursor = conn.cursor()
cursor.execute('CREATE EXTENSION IF NOT EXISTS vector')
```

4.2.5. You are going to work with a [package](https://github.com/pgvector/pgvector-python?tab=readme-ov-file#psycopg-2) that provides `pgvector` support for Python. Once you have enabled the `vector` extension, you need to register the vector type with your connection.


```python
register_vector(conn)
```

4.2.6. Then, you can create the `product_embeddings` table. In that table, you will insert the `asin` (product ID), the product information (either the product title or description) and the embedding from the product information.


```python
cursor.execute('DROP TABLE IF EXISTS product_embeddings')
cursor.execute('CREATE TABLE product_embeddings (asin VARCHAR(15) PRIMARY KEY, product_information TEXT, product_embedding vector(384))')
```

4.2.7. Complete the code in the next cell to call the API with a chunk of text and then insert it into the vector database. The insertion process code has already been provided to you. It is created as a string with the `INSERT` statement and the values to be inserted are appended through the `value_array` list.


```python
for id, df_chunk in enumerate(list_df):
    
    ### START CODE HERE ### (3 lines of code)
    
    # Convert the `asin` column from the `df_chunk` dataframe into a list with the `to_list()` method
    asin_list = df_chunk['asin'].to_list()

    # Convert the `product_information` column from the `df_chunk` dataframe into a list with the `to_list()` method
    text_list = df_chunk['product_information'].to_list()

    # Perform an API call through the `get_text_embeddings` function
    # Pass the `ENDPOINT_URL` variable and the chunk of texts stored in the list `text_list` as parameters to that function
    embedding_response = get_text_embeddings(endpoint_url=ENDPOINT_URL, text=text_list)

    ### END CODE HERE ###
    
    # Inserting the data    
    insert_statement = f'INSERT INTO product_embeddings (asin, product_information, product_embedding) VALUES'
    
    value_array = [] 
    for asin, text, embedding in zip(asin_list, text_list, embedding_response['body']):
        value_array.append(f"('{asin}', '{text}', '{embedding}')")
                
    value_str = ",".join(value_array)
    insert_statement = f"{insert_statement} {value_str};"
    
    cursor.execute(insert_statement)

    if id % 5 == 0:
        print(f"Data inserted for batch with id {id}")
        time.sleep(5)

```

    Data inserted for batch with id 0
    Data inserted for batch with id 5
    Data inserted for batch with id 10
    Data inserted for batch with id 15


4.2.8. Check that data has been inserted:


```python
cursor.execute('SELECT COUNT(*) FROM product_embeddings')
cursor.fetchall()
```




    [(400,)]



4.2.9. Use the following cell to get the embeddings from the product information of a particular product.


```python
text = product_information_df.iloc[11]['product_information']

# Performing API call and getting the result
embedding_response = get_text_embeddings(endpoint_url=ENDPOINT_URL, text=text)
embeddings = embedding_response['body']

print(f"Text: {text}")
```

    Text: watercolor painting for dummies


4.2.10. In a vector database, you can perform searches for the most similar elements. In [`pgvector`](https://github.com/pgvector/pgvector) you can use the `<->` operator to get the nearest neighbors by L2 distance. Extract the 5 nearest products according to the L2 distance.


```python
select_statement = f"SELECT asin, product_information FROM product_embeddings ORDER BY product_embedding <-> '{embeddings}' LIMIT 5"
cursor.execute(select_statement)
cursor.fetchall()
```




    [('0470182318', 'watercolor painting for dummies'),
     ('048645195X', 'dover publicationsdecorative tile designs coloring book'),
     ('0486430502', 'i love america stained glass coloring book'),
     ('0735335788', 'mudpuppy mermaids colorin crowns'),
     ('073532753X', 'mudpuppy wooden magnetic painters palette letters')]



4.2.11. You can play with the text of the product information to find some similar products. For example, create a custom text to find similar products. Given that you have used the `classicmodels` dataset previously, let's search for similar products to this or similar descriptions: "scale car toy".


```python
text = "scale car toy"

# Performing API call and getting the result
embedding_response = get_text_embeddings(endpoint_url=ENDPOINT_URL, text=text)
embeddings = embedding_response['body']

select_statement = f"SELECT asin, product_information FROM product_embeddings ORDER BY product_embedding <-> '{embeddings}' LIMIT 5"
cursor.execute(select_statement)
cursor.fetchall()
```




    [('0786953306',
      'star wars masters of the force a star wars miniatures booster expansion star wars miniatures product'),
     ('0786949864',
      'demonweb a dampd miniatures booster expansion dampd miniatures product'),
     ('0786938919', 'star wars cmg miniatures game universe huge booster pack'),
     ('0786941006', 'starship battles huge booster star wars miniatures'),
     ('0439843073', 'magalina dog quot soft toy')]



Although no information about cars can be found in the sample dataset, the embeddings were able to relate the word `scale` with `miniature`. 

4.2.12. Once the embeddings from the product's information have been stored, compute and store the embeddings for the reviews. Follow the same procedure as the one done for the product information in the next three cells. Create the `review_embeddings` table.


```python
cursor.execute('DROP TABLE IF EXISTS review_embeddings')
cursor.execute('CREATE TABLE review_embeddings (reviewerid VARCHAR(30), asin VARCHAR(15), reviewtext TEXT, review_embedding vector(384), PRIMARY KEY(reviewerid, asin))')
```

4.2.13. Use `split_dataframe()` function to split the `reviews_text_df` dataframe with the default chunk size of 20 rows per chunk.


```python
### START CODE HERE ### (1 line of code)
list_df = split_dataframe(df=reviews_text_df, chunk_size=20)
### END CODE HERE ###
```

4.2.14. Complete the code in the next cell to call the API with a chunk of text and then insert it into the vector database. Execute the insertion cell; this **should take less than 10 minutes**.


```python
# Call the API and insert the data 
start_time = time.time()

for id, df_chunk in enumerate(list_df):
    
    ### START CODE HERE ### (4 lines of code)

    # Convert the `reviewerid`, `asin` and `reviewtext` columns from the `df_chunk` dataframe into a list with the `to_list()` method
    reviewer_list = df_chunk['reviewerid'].to_list()
    asin_list = df_chunk['asin'].to_list()
    text_list = df_chunk['reviewtext'].to_list()

    # Perform an API call through the `get_text_embeddings` function
    # Pass the `ENDPOINT_URL` variable and the chunk of texts stored in the list `text_list` as parameters to that function
    embedding_response = get_text_embeddings(endpoint_url=ENDPOINT_URL, text=text_list)

    ### END CODE HERE ###
    
    # Insert the data
    insert_statement = f'INSERT INTO review_embeddings (reviewerid, asin, reviewtext, review_embedding) VALUES'
    value_array = [] 
    
    for reviewer, asin, text, embedding in zip(reviewer_list, asin_list, text_list, embedding_response['body']):
        value_array.append(f"('{reviewer}', '{asin}', '{text}', '{embedding}')")
        
    value_str = ",".join(value_array)
    insert_statement = f"{insert_statement} {value_str};"
    
    cursor.execute(insert_statement)    

    if id % 50 == 0:
        print(f"Data inserted for batch with id {id}")
        time.sleep(10)

end_time = time.time()
print(f"Total time spent {end_time - start_time} seconds")
```

    Data inserted for batch with id 0
    Data inserted for batch with id 50
    Data inserted for batch with id 100
    Data inserted for batch with id 150
    Data inserted for batch with id 200
    Total time spent 361.6811239719391 seconds


4.2.15. Check that the data has been properly inserted.


```python
cursor.execute('SELECT count(*) FROM review_embeddings')
cursor.fetchall()
```




    [(4464,)]



4.2.16. Finally, you can take a text and search for the more similar reviews using the L2 distance. Change the text for a custom message to experiment with the results! As an example, explore the results from this message: "I didn't like this toy, it was broken!"


```python
text=reviews_text_df.iloc[0]['reviewtext']
embedding_response = get_text_embeddings(endpoint_url=ENDPOINT_URL, text=text)
embeddings = embedding_response['body']
print(f"Text: {text}")
```

    Text: great product thank you our son loved the puzzles they have large pieces yet they are still challenging for a year old



```python
select_statement = f"SELECT reviewerid, asin, reviewtext FROM review_embeddings ORDER BY review_embedding <-> '{embeddings}' LIMIT 5"
cursor.execute(select_statement)
cursor.fetchall()
```




    [('AMEVO2LY6VEJA',
      '0000191639',
      'great product thank you our son loved the puzzles they have large pieces yet they are still challenging for a year old'),
     ('ABZLHQGQS7U9V',
      '0735331146',
      'such great quality easy to put together because of the thick well made pieces my year old loves them and can do these piece puzzles by herself'),
     ('A5N978MBDMG8T',
      '0735331111',
      'love these puzzlesi have them all now my year old loves the big pieces and the map to show her the picture big hit'),
     ('A2R4O4128P54Y5',
      '0735329605',
      'i love these puzzles in a tin no cardboard boxes that bend and fall apart losing piecesi buy them for my five year old granddaughter she loves the challenge of a piece puzzle it is a nice activity for us to do togetheralthough i have to admit that she is faster than i am at finding all the right pieces'),
     ('A3SU2PP1NXVYEE',
      '0867343125',
      'my year old loves this puzzle the large thick pieces are easy to manipulate great for teaching numbers up to')]



4.2.17. The last step consists of inserting the data from the `reviews_product_metadata_df` dataframe, which contains the other transformed variables that can be used to train another ML model.


```python
ddl_statement = """CREATE TABLE review_product_transformed (
    reviewerid VARCHAR(25) NOT NULL,
    asin VARCHAR(15) NOT NULL,
    overall FLOAT,
    year INTEGER,
    month INTEGER,
    helpful_votes INTEGER,
    total_votes INTEGER,
    not_helpful_votes INTEGER,
    price FLOAT,
    sales_rank FLOAT,
    helpful_ratio FLOAT,
    not_helpful_ratio FLOAT,
    encoded_brand INTEGER,
    sales_category_arts_crafts_sewing FLOAT,
    sales_category_electronics FLOAT,
    sales_category_home_amp_kitchen FLOAT,
    sales_category_industrial_scientific FLOAT,
    sales_category_software FLOAT,
    sales_category_sports_amp_outdoors FLOAT,
    sales_category_toys_games FLOAT,
    PRIMARY KEY (reviewerid, asin)
);
"""

cursor.execute('DROP TABLE IF EXISTS review_product_transformed')
cursor.execute(ddl_statement)
```


```python
insert_query = """
    INSERT INTO review_product_transformed (
        reviewerid, asin, overall, year, month, helpful_votes, total_votes, 
        not_helpful_votes, price, sales_rank, helpful_ratio, not_helpful_ratio, 
        encoded_brand, sales_category_arts_crafts_sewing, sales_category_electronics, 
        sales_category_home_amp_kitchen, sales_category_industrial_scientific, 
        sales_category_software, sales_category_sports_amp_outdoors, sales_category_toys_games
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

# Iterate over the DataFrame rows and insert each row into the database
for i, row in reviews_product_metadata_df.iterrows():
    cursor.execute(insert_query, tuple(row))

```


```python
cursor.execute('SELECT COUNT(*) FROM review_product_transformed')
cursor.fetchall()
```




    [(4464,)]



4.2.18. Finally, you are required to close the connection to the vector database.


```python
cursor.close()
conn.close()
```

In this lab, you successfully transformed a dataset provided in JSON format into a structured format suitable for machine learning (ML) applications. This process involved three critical steps of feature engineering: data extraction, feature creation, and data storage. In addition, you processed text data and interacted with an NLP model to generate text embeddings. You integrated your process with a vector database in PostgreSQL which facilitates the efficient storage and retrieval of high-dimensional vector data. With the embeddings stored in your vector database, you are also able to find similar items or reviews through the usage of an L2 Euclidean distance to measure similarity between vectors. This approach allowed you to retrieve items or reviews with embeddings that were closest to the query embedding.

<a name='5'></a>
## 5 - Upload Files for Grading

Upload the notebook into S3 bucket for grading purposes.

*Note*: you may need to click **Save** button before the upload.


```python
# Retrieve the AWS account ID
result = subprocess.run(['aws', 'sts', 'get-caller-identity', '--query', 'Account', '--output', 'text'], capture_output=True, text=True)
AWS_ACCOUNT_ID = result.stdout.strip()

SUBMISSION_BUCKET = f"{LAB_PREFIX}-{AWS_ACCOUNT_ID}-us-east-1-submission"

!aws s3 cp ./C4_W2_Assignment.ipynb s3://$SUBMISSION_BUCKET/C4_W2_Assignment_Learner.ipynb
```

    upload: ./C4_W2_Assignment.ipynb to s3://de-c4w2a1-851725471174-us-east-1-submission/C4_W2_Assignment_Learner.ipynb



```python

```
