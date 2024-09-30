# Week 2 Lab: Feature Engineering for ML

In this lab, you will implement a model to transform the data, creating a dataset ready for training a Machine Learning (ML) model. You will perform basic transformations useful for numerical and categorical variables, preparing the data to train a recommender system. This process involves feature engineering to enhance the predictive power of the model.

# Table of Contents

- [ 1 - Introduction and Setup](#1)
  - [ 1.1 - Introduction to Feature Engineering](#1.1)
  - [ 1.2 - Source Data Connection](#1.2)
- [ 2 - Data Extraction](#2)
- [ 3 - Train and Test Split](#3)
- [ 4 - Feature Creation for Training Dataset](#4)
  - [ 4.1 - Feature Engineering for Numerical Variables](#4.1)
  - [ 4.2 - Feature Engineering for Categorical Variables](#4.2)
  - [ 4.3 - Feature Storage](#4.3)
- [ 5 - Feature Creation for Test Dataset](#5)
  - [ 5.1 - Feature Engineering for Numerical Variables](#5.1)
  - [ 5.2 - Feature Engineering for Categorical Variables](#5.2)
  - [ 5.3 - Feature Storage](#5.3)

<a name='1'></a>
## 1 - Introduction and Setup

<a name='1.1'></a>
### 1.1 - Introduction to Feature Engineering

A **feature** is a numerical representation of a phenomenon. Choosing or creating the most appropriate features is a process called **Feature Engineering**. Feature Engineering is a crucial step in the data preparation process for machine learning and data analysis. It involves the creation, transformation, and selection of features (variables, attributes, or columns) from raw data to improve the performance of machine learning models. Effective feature engineering can significantly enhance the predictive power of the model.

The Feature Engineering you will be working on this lab involves three steps: 

- **Data extraction**: Collecting data and then extracting the required dataset to train the ML model. This involves connecting to different data sources and handling large data volumes to search for the initial dataset.
- **Feature creation**: This involves the creation of numerical features from the initial dataset. Some examples are:
    - *Data labelling*: Designating labels to each record to later train a model to predict the label on new data.
    - *Text embeddings*: Creating vector embeddings based on text, is done to create a representation of text data that an ML model can learn from. 
    - *Categorical data encoding*: Encoding categorical data to a numerical representation.
- **Feature storage**: After the data is cleaned and transformed, the final dataset should be stored in a system that the ML team has access to, where they can explore the dataset and run the training for the ML model. Here you will split the final dataset into a training and testing dataset and store each in an S3 bucket.

You will reexamine the assignment for Course 1 Week 4, in which you build a comprehensive pipeline to feed a Machine Learning model, specifically a content-based filtering recommender system based on the `classicmodels` database. Here you will be provided with the model and the scripts required to train it, but you will be modelling and implementing the required transformations to deliver the datasets for training and testing the ML model. In this lab, you will replicate steps of the pipeline using just this notebook, mainly for testing the logic of a machine learning pipeline in just one place.

<a name='1.2'></a>
### 1.2 - Source Data Connection

1.2.1. First, load the required packages:


```python
import os
import io
import datetime as dt
import pickle

import awswrangler as wr
import boto3
from dotenv import load_dotenv
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder, StandardScaler, KBinsDiscretizer

%load_ext sql
```

1.2.2. Go to the AWS console and click on the upper right part, where your username appears. Copy the **Account ID**. In the code below, set the variable `BUCKET_NAME` to your account ID by replacing `<AWS-ACCOUNT-ID>` placeholder with the Account ID that you copied. The Account ID should contain only numbers without hyphens between them (e.g. 123412341234, not 1234-1234-1234, and the bucket name should look like `de-c4w2lab1-123412341234-us-east-1-data-bucket`).


```python
BUCKET_NAME = 'de-c4w2lab1-730335180803-us-east-1-data-bucket'
```

1.2.3. The Source RDS is a modified version of the [`classicmodels` database](https://www.mysqltutorial.org/mysql-sample-database.aspx) used in Course 1 Week 4, in which there was an additional table called ratings. That table relates the users with the products they have bought and will add a column `productRating` that indicates, on a scale between 1 and 5, the rating that the user gave to a particular item. You will configure the connection for this notebook to connect with the database.

Get the endpoint of the database instance with the following command in Cloud9 or Jupyter terminal:

```bash
aws rds describe-db-instances --db-instance-identifier de-c4w2lab1-rds --output text --query "DBInstances[].Endpoint.Address"
```

1.2.4. Open the `./src/env` file and fill the placeholder `<RDS-ENDPOINT>` with the RDS Endpoint that you found with the previous command (please, replace the whole placeholder including the `<>` brackets). Save changes.

1.2.5. Then execute the following cell to load the environment variables and connect to the database:


```python
load_dotenv('./src/env', override=True)

DBHOST = os.getenv('DBHOST')
DBPORT = os.getenv('DBPORT')
DBNAME = os.getenv('DBNAME')
DBUSER = os.getenv('DBUSER')
DBPASSWORD = os.getenv('DBPASSWORD')

connection_url = f"mysql+pymysql://{DBUSER}:{DBPASSWORD}@{DBHOST}:{DBPORT}/{DBNAME}"

%sql {connection_url}
```

1.2.6. To verify the connection, run the following cell to list the available tables using the `%sql` magic:


```sql
%%sql
use classicmodels;
show tables;
```

     * mysql+pymysql://admin:***@de-c4w2lab1-rds.c32ks4ogwmiy.us-east-1.rds.amazonaws.com:3306/classicmodels
    0 rows affected.
    9 rows affected.





<table>
    <thead>
        <tr>
            <th>Tables_in_classicmodels</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>customers</td>
        </tr>
        <tr>
            <td>employees</td>
        </tr>
        <tr>
            <td>offices</td>
        </tr>
        <tr>
            <td>orderdetails</td>
        </tr>
        <tr>
            <td>orders</td>
        </tr>
        <tr>
            <td>payments</td>
        </tr>
        <tr>
            <td>productlines</td>
        </tr>
        <tr>
            <td>products</td>
        </tr>
        <tr>
            <td>ratings</td>
        </tr>
    </tbody>
</table>



1.2.7. Examine the `ratings` table:


```sql
%%sql
SELECT * 
FROM ratings
LIMIT 10;
```

     * mysql+pymysql://admin:***@de-c4w2lab1-rds.c32ks4ogwmiy.us-east-1.rds.amazonaws.com:3306/classicmodels
    10 rows affected.





<table>
    <thead>
        <tr>
            <th>customerNumber</th>
            <th>productCode</th>
            <th>productRating</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>103</td>
            <td>S10_2016</td>
            <td>3</td>
        </tr>
        <tr>
            <td>103</td>
            <td>S18_1589</td>
            <td>3</td>
        </tr>
        <tr>
            <td>103</td>
            <td>S18_2625</td>
            <td>1</td>
        </tr>
        <tr>
            <td>103</td>
            <td>S18_2870</td>
            <td>5</td>
        </tr>
        <tr>
            <td>103</td>
            <td>S18_3685</td>
            <td>4</td>
        </tr>
        <tr>
            <td>103</td>
            <td>S24_1628</td>
            <td>3</td>
        </tr>
        <tr>
            <td>103</td>
            <td>S24_2022</td>
            <td>5</td>
        </tr>
        <tr>
            <td>112</td>
            <td>S18_1129</td>
            <td>5</td>
        </tr>
        <tr>
            <td>112</td>
            <td>S18_1342</td>
            <td>5</td>
        </tr>
        <tr>
            <td>112</td>
            <td>S18_1589</td>
            <td>3</td>
        </tr>
    </tbody>
</table>



<a name='2'></a>
## 2 - Data Extraction

As a first step in the process of feature engineering, you will create a new base dataset for the ML model. You will extract the required data from different tables and, based on that initial dataset, add more features or improve the ones that were selected. You will use the schema from the transformed table to create a new table. An AWS Glue job was used for that in Course 1 Week 4 Assignment, but for the prototype, you will do the required transformations in this notebook.

![schema_after_ETL](./images/schema_after_ETL.png)

2.1. Open the file `./src/de-c4w2lab1-etl-glue-job.py`. This is the code from the AWS Glue Job where a node was created to bring the required data from each table in `classicmodels` using the Glue Catalog, then a SQL query was used to perform a join between the tables and the result from the join was stored in S3. This code was used in the C1W4 Assignment. Briefly go through the script reading the comments.

2.2. For this notebook, as you have already established a connection to the source database, just replicate the logic with a SQL query and using the `%sql` magic bring the transformed data as a `pandas` dataframe. Copy the SQL query `sql_join_query` from the script and paste it into the cell below. Additionally, in your query add the column `customerSince` to be selected. It will be coming from the `customer` table named as `c`.


```python
sql_join_query = """
select r.customerNumber
, c.city
, c.state
, c.postalCode
, c.country
, c.creditLimit
, c.customerSince
, r.productCode
, p.productLine
, p.productScale
, p.quantityInStock
, p.buyPrice
, p.MSRP
, r.productRating
from ratings r 
join products p on p.productCode = r.productCode 
join customers c on c.customerNumber = r.customerNumber;
"""

result = %sql {sql_join_query}

model_df = result.DataFrame()

model_df.head()
```

     * mysql+pymysql://admin:***@de-c4w2lab1-rds.c32ks4ogwmiy.us-east-1.rds.amazonaws.com:3306/classicmodels
    2532 rows affected.





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
      <th>customerNumber</th>
      <th>city</th>
      <th>state</th>
      <th>postalCode</th>
      <th>country</th>
      <th>creditLimit</th>
      <th>customerSince</th>
      <th>productCode</th>
      <th>productLine</th>
      <th>productScale</th>
      <th>quantityInStock</th>
      <th>buyPrice</th>
      <th>MSRP</th>
      <th>productRating</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>103</td>
      <td>Nantes</td>
      <td>None</td>
      <td>44000</td>
      <td>France</td>
      <td>21000.00</td>
      <td>2014-06-21</td>
      <td>S10_2016</td>
      <td>Motorcycles</td>
      <td>1:10</td>
      <td>6625</td>
      <td>68.99</td>
      <td>118.94</td>
      <td>3</td>
    </tr>
    <tr>
      <th>1</th>
      <td>103</td>
      <td>Nantes</td>
      <td>None</td>
      <td>44000</td>
      <td>France</td>
      <td>21000.00</td>
      <td>2014-06-21</td>
      <td>S18_1589</td>
      <td>Classic Cars</td>
      <td>1:18</td>
      <td>9042</td>
      <td>65.96</td>
      <td>124.44</td>
      <td>3</td>
    </tr>
    <tr>
      <th>2</th>
      <td>103</td>
      <td>Nantes</td>
      <td>None</td>
      <td>44000</td>
      <td>France</td>
      <td>21000.00</td>
      <td>2014-06-21</td>
      <td>S18_2625</td>
      <td>Motorcycles</td>
      <td>1:18</td>
      <td>4357</td>
      <td>24.23</td>
      <td>60.57</td>
      <td>1</td>
    </tr>
    <tr>
      <th>3</th>
      <td>103</td>
      <td>Nantes</td>
      <td>None</td>
      <td>44000</td>
      <td>France</td>
      <td>21000.00</td>
      <td>2014-06-21</td>
      <td>S18_2870</td>
      <td>Classic Cars</td>
      <td>1:18</td>
      <td>8164</td>
      <td>56.76</td>
      <td>132.00</td>
      <td>5</td>
    </tr>
    <tr>
      <th>4</th>
      <td>103</td>
      <td>Nantes</td>
      <td>None</td>
      <td>44000</td>
      <td>France</td>
      <td>21000.00</td>
      <td>2014-06-21</td>
      <td>S18_3685</td>
      <td>Classic Cars</td>
      <td>1:18</td>
      <td>8990</td>
      <td>62.16</td>
      <td>141.28</td>
      <td>4</td>
    </tr>
  </tbody>
</table>
</div>



<a name='3'></a>
## 3 - Train and Test Split

Although the best practices to generate a train and test split of your dataset are out of the scope of this course, you will perform a basic splitting of the `model_df` dataframe. This is done with the help of the [`scikit-learn`](https://scikit-learn.org/) library. `scikit-learn` is an open-source ML library which, among other features, allows you to transform and prepare your dataset for ML models. In particular, you will use the `train_test_split()` method. You will choose a test size of 20% of the rows from the original dataframe. The `random_state` parameter allows replicating the process, so avoid changing its value.


```python
model_train_df, model_test_df = train_test_split(
                model_df,
                test_size=0.2,
                random_state=42
            )
```


```python
model_train_df.head()
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
      <th>customerNumber</th>
      <th>city</th>
      <th>state</th>
      <th>postalCode</th>
      <th>country</th>
      <th>creditLimit</th>
      <th>customerSince</th>
      <th>productCode</th>
      <th>productLine</th>
      <th>productScale</th>
      <th>quantityInStock</th>
      <th>buyPrice</th>
      <th>MSRP</th>
      <th>productRating</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>157</th>
      <td>124</td>
      <td>San Rafael</td>
      <td>CA</td>
      <td>97562</td>
      <td>USA</td>
      <td>210500.00</td>
      <td>2021-09-06</td>
      <td>S18_1097</td>
      <td>Trucks and Buses</td>
      <td>1:18</td>
      <td>2613</td>
      <td>58.33</td>
      <td>116.67</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2028</th>
      <td>386</td>
      <td>Reggio Emilia</td>
      <td>None</td>
      <td>42100</td>
      <td>Italy</td>
      <td>121400.00</td>
      <td>2015-01-07</td>
      <td>S12_3891</td>
      <td>Classic Cars</td>
      <td>1:12</td>
      <td>1049</td>
      <td>83.05</td>
      <td>173.02</td>
      <td>3</td>
    </tr>
    <tr>
      <th>790</th>
      <td>181</td>
      <td>NYC</td>
      <td>NY</td>
      <td>10022</td>
      <td>USA</td>
      <td>76400.00</td>
      <td>2014-06-20</td>
      <td>S18_2319</td>
      <td>Trucks and Buses</td>
      <td>1:18</td>
      <td>8258</td>
      <td>74.86</td>
      <td>122.73</td>
      <td>3</td>
    </tr>
    <tr>
      <th>2077</th>
      <td>398</td>
      <td>Minato-ku</td>
      <td>Tokyo</td>
      <td>106-0032</td>
      <td>Japan</td>
      <td>94400.00</td>
      <td>2016-04-21</td>
      <td>S24_1578</td>
      <td>Motorcycles</td>
      <td>1:24</td>
      <td>7003</td>
      <td>60.86</td>
      <td>112.70</td>
      <td>3</td>
    </tr>
    <tr>
      <th>135</th>
      <td>121</td>
      <td>Stavern</td>
      <td>None</td>
      <td>4110</td>
      <td>Norway</td>
      <td>81700.00</td>
      <td>2019-05-23</td>
      <td>S24_4048</td>
      <td>Classic Cars</td>
      <td>1:24</td>
      <td>6582</td>
      <td>69.78</td>
      <td>118.28</td>
      <td>2</td>
    </tr>
  </tbody>
</table>
</div>



For the first part of the lab, you will work on performing transformations over the `model_train_df` dataframe. Then, those transformations will be applied to the `model_test_df` later on.

<a name='4'></a>
## 4 - Feature Creation for Training Dataset

To create the required features based on the initial sub-datasets, you have to distinguish between numerical and categorical variables. **Numerical variables** are quantitative and can be classified as discrete or continuous. **Categorical variables** are qualitative data such as names or labels. For each type of variable, you have different Feature Engineering techniques.

For the feature creation you are also going to use the methods from the `scikit-learn` library. 

Before you start with the Feature Engineering, to avoid future issues when working with the column names, you are going to convert the column names to lowercase.


```python
model_train_df.columns = [col.lower() for col in model_train_df.columns]
```

Given that the model being trained with this dataset is a content-based recommender system, you are required to process the features from the customers (users) and the products (items) separately. Those subsets although processed independently, both will be used to train the model. Now, you will split the users' features from the items' features and process each one as an independent `pandas` dataframe. Let's create a pair of lists with the column names for each sub-dataset.


```python
# Creating the users dataframe
user_columns = ["customernumber", "city", "country", "creditlimit", "customersince"]
users_df = model_train_df[user_columns].copy()

# Creating the items dataframe
item_columns = ["productcode", "productline", "productscale", "quantityinstock", "buyprice", "msrp"]
items_df = model_train_df[item_columns].copy()
```


```python
users_df.head()
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
      <th>customernumber</th>
      <th>city</th>
      <th>country</th>
      <th>creditlimit</th>
      <th>customersince</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>157</th>
      <td>124</td>
      <td>San Rafael</td>
      <td>USA</td>
      <td>210500.00</td>
      <td>2021-09-06</td>
    </tr>
    <tr>
      <th>2028</th>
      <td>386</td>
      <td>Reggio Emilia</td>
      <td>Italy</td>
      <td>121400.00</td>
      <td>2015-01-07</td>
    </tr>
    <tr>
      <th>790</th>
      <td>181</td>
      <td>NYC</td>
      <td>USA</td>
      <td>76400.00</td>
      <td>2014-06-20</td>
    </tr>
    <tr>
      <th>2077</th>
      <td>398</td>
      <td>Minato-ku</td>
      <td>Japan</td>
      <td>94400.00</td>
      <td>2016-04-21</td>
    </tr>
    <tr>
      <th>135</th>
      <td>121</td>
      <td>Stavern</td>
      <td>Norway</td>
      <td>81700.00</td>
      <td>2019-05-23</td>
    </tr>
  </tbody>
</table>
</div>




```python
items_df.head()
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
      <th>productcode</th>
      <th>productline</th>
      <th>productscale</th>
      <th>quantityinstock</th>
      <th>buyprice</th>
      <th>msrp</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>157</th>
      <td>S18_1097</td>
      <td>Trucks and Buses</td>
      <td>1:18</td>
      <td>2613</td>
      <td>58.33</td>
      <td>116.67</td>
    </tr>
    <tr>
      <th>2028</th>
      <td>S12_3891</td>
      <td>Classic Cars</td>
      <td>1:12</td>
      <td>1049</td>
      <td>83.05</td>
      <td>173.02</td>
    </tr>
    <tr>
      <th>790</th>
      <td>S18_2319</td>
      <td>Trucks and Buses</td>
      <td>1:18</td>
      <td>8258</td>
      <td>74.86</td>
      <td>122.73</td>
    </tr>
    <tr>
      <th>2077</th>
      <td>S24_1578</td>
      <td>Motorcycles</td>
      <td>1:24</td>
      <td>7003</td>
      <td>60.86</td>
      <td>112.70</td>
    </tr>
    <tr>
      <th>135</th>
      <td>S24_4048</td>
      <td>Classic Cars</td>
      <td>1:24</td>
      <td>6582</td>
      <td>69.78</td>
      <td>118.28</td>
    </tr>
  </tbody>
</table>
</div>



Although you split the original dataframe into two independent subsets, you can use the `pandas` indexing to relate each row of the two datasets. This will be useful later on when creating the final datasets and to relate with your label variable which in this case is the product ratings.

<a name='4.1'></a>
### 4.1 - Feature Engineering for Numerical Variables

The objective of Feature Engineering for a numerical variable is to identify a more effective method of representing the variable within the model. "Effective" implies enhanced validity, stronger predictive power, and improved interpretability. For continuous numerical variables, you will usually perform a Standardization process. Sometimes for other numerical variables, depending on the context you can create ranges or bins. In this particular case you can see that for the user's age it will make more sense to create buckets with ranges of ages instead of scaling this variable, as this can help you to provide more accurate recommendations to the user depending on their age range.

**Standardization** refers to removing the mean of a numerical dataset and then scale it to unit variance. Standardization of a dataset is a common requirement for ML models as they might not behave the best if the individual features do not look similar to standard normally distributed data. In `scikit-learn` the standardization process happens independently for each feature.

Let's review the continuous numerical variables in each of the datasets:
- The `users_df` only has one continuous numerical variable which corresponds to the `creditlimit` that each customer has.
- The `items_df` has several continuous numerical variables: `quantityinstock`, `buyprice`, `msrp`.

The process of standardizing your data with `scikit-learn` can be divided into the following steps:
- Create a `StandardScaler` instance.
- Fit the scaler to the data.
- Transform the data.

Let's perform the three steps shown above on the two datasets. 

4.1.1. Start by instantiating the `StandardScaler` object and assign it to a variable:


```python
# StandardScaler instance for the user numerical data
user_num_standard_scaler = StandardScaler()

# StandardScaler instance for the item numerical data
item_num_standard_scaler = StandardScaler()
```

4.1.2. With the instantiated objects, you will use the `fit()` method over your data. This method computes the mean and standard deviation of the data; those statistics will be used to transform the data to have a mean 0 and a standard deviation of 1. You will have to select only the columns to which the `fit()` will be applied first.

- Create a list `user_num_columns_std` that contains the column names for the continuous numerical variables for the `users_df` DataFrame. In this case, the only element is `creditlimit`.
- Create a second list `item_num_columns_std` with the values: `quantityinstock`, `buyprice`, and `msrp` which correspond to the continuous numerical values of the `items_df` dataframe.
- Call the scaler object `user_num_standard_scaler` and use the `fit()` method over the `users_df` dataframe. Make sure to only select the columns at `user_num_columns_std`.
- Repeat the same for the `items_df` dataframe taking only `item_num_columns_std`. You will need to call the `fit()` method of the scaler object `item_num_standard_scaler`.


```python
### START CODE HERE ### (4 lines of code)
# Choosing the numerical columns to apply the standard scaler in the two datasets
user_num_columns_std = ["creditlimit"] # @REPLACE EQUALS ["None"]
item_num_columns_std = ["quantityinstock", "buyprice", "msrp"] # @REPLACE EQUALS ["None", "None", "None"]

# Computing mean and standard deviation of each feature with the fit method
user_num_standard_scaler.fit(users_df[user_num_columns_std]); # @REPLACE None.None(None[None])
item_num_standard_scaler.fit(items_df[item_num_columns_std]); # @REPLACE None.None(None[None])
### END CODE HERE ###
```

4.1.3. From the code above, you can see that the `fit()` method takes the data that you want to standardize, which can be a `numpy` array or a `pandas` dataframe. This method performs the computation of the mean and standard deviation of each of the selected features of the dataset and stores it in the standard scaler object's properties for transforming the dataset in the future. After fitting, use the `transform()` method of your instantiated scaler; this method performs the standardization based on the computed mean and standard deviation from the `fit()` method. 

Apply `transform()` to `user_num_standard_scaler` and `item_num_standard_scaler`, passing the same dataframes `users_df` and `items_df` with the selected columns lists `user_num_columns_std` and `item_num_columns_std`. Results are `numpy` arrays. You will transform them into `pandas` dataframes.


```python
### START CODE HERE ### (2 lines of code)
# Applying transform
user_num_vars_std = user_num_standard_scaler.transform(users_df[user_num_columns_std]) # @REPLACE EQUALS None.None(None[None])
item_num_vars_std = item_num_standard_scaler.transform(items_df[item_num_columns_std]) # @REPLACE EQUALS None.None(None[None])
### END CODE HERE ###

# Results are numpy arrays. Transform them into pandas dataframes.
user_num_vars_std_df = pd.DataFrame(user_num_vars_std, columns=user_num_columns_std, index=users_df.index)
item_num_vars_std_df = pd.DataFrame(item_num_vars_std, columns=item_num_columns_std, index=items_df.index)
```


```python
item_num_vars_std_df.head()
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
      <th>quantityinstock</th>
      <th>buyprice</th>
      <th>msrp</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>157</th>
      <td>-0.834999</td>
      <td>0.145057</td>
      <td>0.366777</td>
    </tr>
    <tr>
      <th>2028</th>
      <td>-1.370416</td>
      <td>1.265376</td>
      <td>1.774066</td>
    </tr>
    <tr>
      <th>790</th>
      <td>1.097503</td>
      <td>0.894202</td>
      <td>0.518120</td>
    </tr>
    <tr>
      <th>2077</th>
      <td>0.667868</td>
      <td>0.259717</td>
      <td>0.267630</td>
    </tr>
    <tr>
      <th>135</th>
      <td>0.523744</td>
      <td>0.663975</td>
      <td>0.406985</td>
    </tr>
  </tbody>
</table>
</div>




```python
user_num_vars_std_df.head()
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
      <th>creditlimit</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>157</th>
      <td>2.679240</td>
    </tr>
    <tr>
      <th>2028</th>
      <td>0.548794</td>
    </tr>
    <tr>
      <th>790</th>
      <td>-0.527188</td>
    </tr>
    <tr>
      <th>2077</th>
      <td>-0.096795</td>
    </tr>
    <tr>
      <th>135</th>
      <td>-0.400462</td>
    </tr>
  </tbody>
</table>
</div>



<a name='4.2'></a>
### 4.2 - Feature Engineering for Categorical Variables

Categorical variables denote groupings or classifications. Although they might be represented by numbers, these numbers symbolize categories instead of quantitative values. There are three categories of categorical variables: binary, nominal, and ordinal.

- Binary categories: Represent yes/no, true/false or 1/0 outcomes such as if a person has a license or not or a coin flip result.
- Nominal categories: Represent categories with no intrinsic order or ranking. Those categories are mutually exclusive and do not have a meaningful numerical relationship. Some examples could be the hair color of a group of people: black, brown, blonde, red, etc or here, the product categories and the user's locations.
- Ordinal variables: Ordinal variables represent categories with a meaningful order or ranking, but the intervals between the ranks are not necessarily equal or known. They indicate a relative position or order. An example could be the ratings of the data.

For categorical data there are several types of transformations such as label encoding, one hot encoding, binary encoding, among others. For this dataset you are going to focus only on the One-hot Encoding transformations for the categorical features. One-hot encoding is a popular method for converting categorical variables into a format that can be provided to ML algorithms to do a better job in prediction. It creates a binary column for each category and returns a matrix where each column represents one possible category of the original data. Each original value is replaced with a binary vector indicating the presence of the value.

4.2.1. Before you encode the categorical variables, let's extract the features from the dataset and perform some cleansing process. In the following cell, create the following two lists:
- `user_cat_cols` with the column names for the categorical variables in the `users_df` dataframe. The categorical variables correspond to the user's location: `city` and `country`.
- `item_cat_cols` with the `productline` and `productscale` features from the items dataframe. The first feature corresponds to the product category (classic cars, trains, etc.) and the second is the scale of the product.


```python
### START CODE HERE ### (2 lines of code)
# Column names for the categorical variables
user_cat_cols = ["city", "country"] # @REPLACE EQUALS ["None", "None"]
item_cat_cols = ["productline", "productscale"] # @REPLACE EQUALS ["None", "None"]
### END CODE HERE ###
```

4.2.2. Based on the lists of column names, create two dataframes containing only the categorical variables of each users and items dataset. Then, to each of the datasets, you will transform all the categorical variables that are strings into lowercase.


```python
# Creating the datasets with only categorical features
users_cat_df = users_df[user_cat_cols].copy()
items_cat_df = items_df[item_cat_cols].copy()

# Converting string categories into lowercase
users_cat_df = users_cat_df.map(lambda x: x.strip().lower())
items_cat_df = items_cat_df.map(lambda x: x.strip().lower())
```

4.2.3. Note that the features that you have selected correspond to nominal categories. In `scikit-learn` you can use the `OneHotEncoder` class to create the one-hot numerical array. By default, the encoder derives the categories from the unique values in each feature, but the categories can also be passed manually. As done in previous transformations, the first step is to instantiate the object from the `OneHotEncoder` class. For that, you will also use the `handle_unknown="ignore"` option; this option specifies how to handle an unknown category. The `ignore` option will make the resulting one-hot encoded column for an unknown category full of zeros.


```python
### START CODE HERE ### (2 lines of code)
# Create the instance of the one-hot encoder object for each dataset.
user_cat_ohe = OneHotEncoder(handle_unknown="ignore") # @REPLACE EQUALS None(handle_unknown="None")
item_cat_ohe = OneHotEncoder(handle_unknown="ignore") # @REPLACE EQUALS None(handle_unknown="None")
### END CODE HERE ###
```

4.2.4. The next steps correspond to apply the usual `fit()` method to the dataset from which you want to extract the categories and the `transform()` method to actually create the binary vectors over the specified dataset. Note that you are chaining the `todense()` method after the transformation. The result of the `transform` method is a sparse matrix, which is efficient for storing large datasets with many zeros. The `todense()` method converts this sparse matrix into a dense matrix (a regular matrix without sparse representation).

Pass the dataframes `users_cat_df` and `items_cat_df` to perform the transformation and then convert it into the dense matrix with the `todense()` method.


```python
# Using the encoder object to find the categories of each feature
user_cat_ohe.fit(users_cat_df)
item_cat_ohe.fit(items_cat_df)

### START CODE HERE ### (2 lines of code)
# Transform with the encoder objects
encoded_user_cat_features = user_cat_ohe.transform(users_cat_df).todense() # @REPLACE EQUALS user_cat_ohe.None(None).None()
encoded_item_cat_features = item_cat_ohe.transform(items_cat_df).todense() # @REPLACE EQUALS item_cat_ohe.None(None).None()
### END CODE HERE ###
```


```python
encoded_user_cat_df = pd.DataFrame(
    encoded_user_cat_features, 
    columns=user_cat_ohe.get_feature_names_out(user_cat_cols),
    index=users_df.index
)

encoded_item_cat_df = pd.DataFrame(
    encoded_item_cat_features, 
    columns=item_cat_ohe.get_feature_names_out(item_cat_cols),
    index=items_df.index
)
```


```python
encoded_user_cat_df.head()
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
      <th>city_allentown</th>
      <th>city_auckland</th>
      <th>city_barcelona</th>
      <th>city_bergamo</th>
      <th>city_bergen</th>
      <th>city_boston</th>
      <th>city_brickhaven</th>
      <th>city_bridgewater</th>
      <th>city_brisbane</th>
      <th>city_bruxelles</th>
      <th>...</th>
      <th>country_japan</th>
      <th>country_new zealand</th>
      <th>country_norway</th>
      <th>country_philippines</th>
      <th>country_singapore</th>
      <th>country_spain</th>
      <th>country_sweden</th>
      <th>country_switzerland</th>
      <th>country_uk</th>
      <th>country_usa</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>157</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>2028</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>790</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>2077</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>135</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 98 columns</p>
</div>




```python
encoded_item_cat_df.head()
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
      <th>productline_classic cars</th>
      <th>productline_motorcycles</th>
      <th>productline_planes</th>
      <th>productline_ships</th>
      <th>productline_trains</th>
      <th>productline_trucks and buses</th>
      <th>productline_vintage cars</th>
      <th>productscale_1:10</th>
      <th>productscale_1:12</th>
      <th>productscale_1:18</th>
      <th>productscale_1:24</th>
      <th>productscale_1:32</th>
      <th>productscale_1:50</th>
      <th>productscale_1:700</th>
      <th>productscale_1:72</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>157</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>2028</th>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>790</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>2077</th>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>135</th>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
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



4.2.5. **Ranges.** There are some numerical values that can be binned. For example, the `customersince` column which is a date, can be converted to an integer such as years or months. Although this value can be standardized, in the context of a recommender system, it can be more useful to create bins of year or month ranges. This can be done with a `KBinsDiscretizer` object. 

For the context of your business, you are asked to create bins for the customers given their antiquity with the company in the following way:
- A bin for the most recent customers, with 1 year or less of antiquity.
- A bin for customers with an antiquity greater than 1 but less than 3 years.
- A bin for customers with antiquity of 3-5 years.
- A bin for customers with more than 5 years of antiquity.

In order to generate the binning process, first you need to create the `loyalty_program_years` column based on the date provided in the `customersince` column. Follow the instructions to create the bins.


```python
# Define the bin edges
bin_edges = [0, 1, 3, 5, float('inf')]

### START CODE HERE ### (7 lines of code)

# Convert the `customersince` column of the dataframe `users_df` to datetime data type with `pd.to_datetime()` method
users_df['customersince'] = pd.to_datetime(users_df['customersince']) # @REPLACE EQUALS pd.None(None['None'])

# Compute the current timestamp with `pd.Timestamp.now()`
current_date = pd.Timestamp.now() # @REPLACE EQUALS pd.None.None()

# Create the column with the difference between the `current_date` value and the `customersince` column of the `users_df` dataframe
# Convert the value in days by applying `dt.days` method and make an integer division by 365
users_df['loyalty_program_years'] = (current_date - users_df['customersince']).dt.days // 365 # @REPLACE EQUALS (None - None['None']).None.None // None

# Initialize the `KBinsDiscretizer` class with the following parameters:
# Set `n_bins` as `len(bin_edges) - 1` because the number of bins is always one less than the number of edges.
# Set `encode` equal to `'onehot-dense'`. This specifies how to encode the transformed result. Here the strategy is to apply to the bins a one-hot encoding.
# Set `strategy` parameter equal to `'uniform'` which is a binning strategy where bins are of equal width.
# Leave `subsample` equal to `None` as it is; this option means that all the training samples are used when computing the quantiles that determine the binning thresholds.
kbins = KBinsDiscretizer(n_bins=len(bin_edges) - 1, encode='onehot-dense', strategy='uniform', subsample=None) # @REPLACE EQUALS None(n_bins=None(None) - 1, encode='None', strategy='None', subsample=None)

# Select `loyalty_program_years` from the dataframe `users_df`. Use double brackets to output it as a dataframe, not a series
loyalty_program_years = users_df[['loyalty_program_years']] # @REPLACE EQUALS None[['None']]

# Apply `fit()` method to the dataframe `loyalty_program_years`
kbins.fit(loyalty_program_years) # @REPLACE kbins.None(None)

# Apply `transform()` method to transform to the dataframe `loyalty_program_years`
loyalty_program_years_binned = kbins.transform(loyalty_program_years) # @REPLACE EQUALS kbins.None(None)

### END CODE HERE ###

# Convert the binned data to a DataFrame with appropriate column names
bin_labels = ['0-1 years', '1-3 years', '3-5 years', '5+ years']
loyalty_program_years_binned_df = pd.DataFrame(loyalty_program_years_binned, columns=bin_labels, index=users_df.index)

loyalty_program_years_binned_df.head()
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
      <th>0-1 years</th>
      <th>1-3 years</th>
      <th>3-5 years</th>
      <th>5+ years</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>157</th>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>2028</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>790</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>2077</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>135</th>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
  </tbody>
</table>
</div>



*Note*: In `scikit-learn`, you can use the `fit_transform()` method to combine the fit and transform steps into one line of code, making your code more concise and readable. However, it won't be used in this lab.

You can see that you created a new numerical variable named `loyalty_program_years` that has also been turned into a categorical variable represented as ranges. After the binning and one-hot encoding process, the `loyalty_program_years` variable is no longer treated as a continuous variable but as a categorical variable with 4 categories.

4.2.6. You have transformed all the features that will feed the recommendation system but you are missing an important part, the label. In the recommendation system, the label is the rating that a user has provided for each of the products that this customer has bought. The ratings are numerical values from 1 to 5 but can be treated as categories. For this nominal category, you will map the values from the range [1, 5] to a range more suitable for ML models. You will scale this range to [-1, 1] with the help of the `MinMaxScaler` class. 

Create an instance of `MinMaxScaler` scaler and set the `feature_range` parameter to `(-1, 1)`.


```python
### START CODE HERE ### (1 line of code)

# Creating an instance of MinMaxScaler for ratings
rating_scaler = MinMaxScaler(feature_range=(-1, 1)) # @REPLACE EQUALS None(feature_range=(None, None))

### END CODE HERE ###
```

4.2.7. To compute and transform the ratings from the [1, 5] to the [-1, 1] range, use the `fit()` and `transform()` methods for the column `productrating` of the dataframe  `model_train_df`.


```python
### START CODE HERE ### (2 lines of code)
# Apply `fit()` method
rating_scaler.fit(model_train_df[["productrating"]]) # @REPLACE rating_scaler.None(None[["None"]])

# Perform transformation
ratings = rating_scaler.transform(model_train_df[["productrating"]]) # @REPLACE EQUALS rating_scaler.None(None[["None"]])
### END CODE HERE ###

scaled_ratings_df = pd.DataFrame(ratings, columns=["scaled_productrating"], index=model_train_df.index)
scaled_ratings_df.head()
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
      <th>scaled_productrating</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>157</th>
      <td>-0.5</td>
    </tr>
    <tr>
      <th>2028</th>
      <td>0.0</td>
    </tr>
    <tr>
      <th>790</th>
      <td>0.0</td>
    </tr>
    <tr>
      <th>2077</th>
      <td>0.0</td>
    </tr>
    <tr>
      <th>135</th>
      <td>-0.5</td>
    </tr>
  </tbody>
</table>
</div>



<a name='4.3'></a>
### 4.3 - Feature Storage

Once you have performed all the transformations and created the new features over your dataset, it is time to safely store them. Note that until this moment you have divided your user's dataset into a subset containing only the numerical tranformed features and another containing only the categorical transformed features. The same applies to the items and ratings. As an initial step, you need to join all of these datasets into one that will be stored. It is particularly easy to join all those datasets as you have been using the `pandas` index to identify each row and you haven't shuffled rows in any moment. 

4.3.1. To create the dataset of transformed features from your training data, use the panda's `concat()` method over the `axis=1`.


```python
transformed_train_df = pd.concat([
                                    users_df[["customernumber"]],
                                    user_num_vars_std_df, 
                                    encoded_user_cat_df,
                                    items_df[["productcode"]],
                                    item_num_vars_std_df, 
                                    encoded_item_cat_df,
                                    loyalty_program_years_binned_df,
                                    scaled_ratings_df
                                ], 
                                axis=1
                                )

transformed_train_df.head()
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
      <th>customernumber</th>
      <th>creditlimit</th>
      <th>city_allentown</th>
      <th>city_auckland</th>
      <th>city_barcelona</th>
      <th>city_bergamo</th>
      <th>city_bergen</th>
      <th>city_boston</th>
      <th>city_brickhaven</th>
      <th>city_bridgewater</th>
      <th>...</th>
      <th>productscale_1:24</th>
      <th>productscale_1:32</th>
      <th>productscale_1:50</th>
      <th>productscale_1:700</th>
      <th>productscale_1:72</th>
      <th>0-1 years</th>
      <th>1-3 years</th>
      <th>3-5 years</th>
      <th>5+ years</th>
      <th>scaled_productrating</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>157</th>
      <td>124</td>
      <td>2.679240</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>-0.5</td>
    </tr>
    <tr>
      <th>2028</th>
      <td>386</td>
      <td>0.548794</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>790</th>
      <td>181</td>
      <td>-0.527188</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>2077</th>
      <td>398</td>
      <td>-0.096795</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>135</th>
      <td>121</td>
      <td>-0.400462</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>-0.5</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 124 columns</p>
</div>



4.3.2. With this joined dataset, you can safely store it. You will upload this dataset into an S3 bucket. In addition to storing this dataset, you are also required to store the artifacts from your scaler and encoder objects. This is because those objects have been applied over the training dataset and you need the computed values to transform the data from your test set or even when you are using the model for inference.

Start by uploading the artifacts and then you will insert the data.


```python
s3 = boto3.client('s3')

artifacts_folder = 'preprocessing/artifacts'

# Standard scaler for users
user_num_std_scaler_pkl = pickle.dumps(user_num_standard_scaler)
s3.put_object(Bucket=BUCKET_NAME, Key=f'{artifacts_folder}/user_std_scaler.pkl', Body=user_num_std_scaler_pkl)

# Standard scaler for items
item_num_std_scaler_pkl = pickle.dumps(item_num_standard_scaler)
s3.put_object(Bucket=BUCKET_NAME, Key=f'{artifacts_folder}/item_std_scaler.pkl', Body=item_num_std_scaler_pkl)

# Binnerizer for user's years with company
kbins_pkl = pickle.dumps(kbins)
s3.put_object(Bucket=BUCKET_NAME, Key=f'{artifacts_folder}/user_kbins.pkl', Body=kbins_pkl)

# Standard scaler for users
user_cat_ohe_pkl = pickle.dumps(user_cat_ohe)
s3.put_object(Bucket=BUCKET_NAME, Key=f'{artifacts_folder}/user_cat_ohe.pkl', Body=user_cat_ohe_pkl)

# Standard scaler for items
item_cat_ohe_pkl = pickle.dumps(item_cat_ohe)
s3.put_object(Bucket=BUCKET_NAME, Key=f'{artifacts_folder}/item_cat_ohe.pkl', Body=item_cat_ohe_pkl)

# Scaler for ratings
rating_scaler_pkl = pickle.dumps(rating_scaler)
s3.put_object(Bucket=BUCKET_NAME, Key=f'{artifacts_folder}/ratings_min_max_scaler.pkl', Body=rating_scaler_pkl)

```




    {'ResponseMetadata': {'RequestId': 'H8806PYFG0Q7QK0D',
      'HostId': 'B5w87VT4Dtzmmapawm8NLeASlElNXCTEUHNYTxRtvCMhyMd/ScQE57XBiLdDnwTnF4q3/dfWcTUf9N/7JTvnYQ==',
      'HTTPStatusCode': 200,
      'HTTPHeaders': {'x-amz-id-2': 'B5w87VT4Dtzmmapawm8NLeASlElNXCTEUHNYTxRtvCMhyMd/ScQE57XBiLdDnwTnF4q3/dfWcTUf9N/7JTvnYQ==',
       'x-amz-request-id': 'H8806PYFG0Q7QK0D',
       'date': 'Sun, 29 Sep 2024 19:14:21 GMT',
       'x-amz-server-side-encryption': 'AES256',
       'etag': '"f21ea338c494562f9a97ee5a0917468c"',
       'server': 'AmazonS3',
       'content-length': '0'},
      'RetryAttempts': 0},
     'ETag': '"f21ea338c494562f9a97ee5a0917468c"',
     'ServerSideEncryption': 'AES256'}



4.3.3. Now, let's save the data. Remember that one of the best practices when saving data into an object storage is to manage partitions. Your dataset does not contain any `date` data type. Other options for partition keys could be the users or the items. A user can purchase one or several items, and an item can be purchased by several users. Given that users might only purchase one type of product, a more effective key could be the item identifier (product code) as it can distribute rows more evenly.


```python
data_s3_url = f's3://{BUCKET_NAME}/preprocessing/data/ratings_for_ml/train'

transformed_train_df.to_parquet(data_s3_url,
                                compression='snappy',
                                engine='pyarrow',
                                partition_cols=['productcode'],
                                existing_data_behavior='delete_matching'                                
                            )

```

4.3.4. Then you can see the result in your S3 bucket


```python
!aws s3 ls s3://$BUCKET_NAME/preprocessing/data/ratings_for_ml/train/
```

                               PRE productcode=S10_1678/
                               PRE productcode=S10_1949/
                               PRE productcode=S10_2016/
                               PRE productcode=S10_4698/
                               PRE productcode=S10_4757/
                               PRE productcode=S10_4962/
                               PRE productcode=S12_1099/
                               PRE productcode=S12_1108/
                               PRE productcode=S12_1666/
                               PRE productcode=S12_2823/
                               PRE productcode=S12_3148/
                               PRE productcode=S12_3380/
                               PRE productcode=S12_3891/
                               PRE productcode=S12_3990/
                               PRE productcode=S12_4473/
                               PRE productcode=S12_4675/
                               PRE productcode=S18_1097/
                               PRE productcode=S18_1129/
                               PRE productcode=S18_1342/
                               PRE productcode=S18_1367/
                               PRE productcode=S18_1589/
                               PRE productcode=S18_1662/
                               PRE productcode=S18_1749/
                               PRE productcode=S18_1889/
                               PRE productcode=S18_1984/
                               PRE productcode=S18_2238/
                               PRE productcode=S18_2248/
                               PRE productcode=S18_2319/
                               PRE productcode=S18_2325/
                               PRE productcode=S18_2432/
                               PRE productcode=S18_2581/
                               PRE productcode=S18_2625/
                               PRE productcode=S18_2795/
                               PRE productcode=S18_2870/
                               PRE productcode=S18_2949/
                               PRE productcode=S18_2957/
                               PRE productcode=S18_3029/
                               PRE productcode=S18_3136/
                               PRE productcode=S18_3140/
                               PRE productcode=S18_3232/
                               PRE productcode=S18_3259/
                               PRE productcode=S18_3278/
                               PRE productcode=S18_3320/
                               PRE productcode=S18_3482/
                               PRE productcode=S18_3685/
                               PRE productcode=S18_3782/
                               PRE productcode=S18_3856/
                               PRE productcode=S18_4027/
                               PRE productcode=S18_4409/
                               PRE productcode=S18_4522/
                               PRE productcode=S18_4600/
                               PRE productcode=S18_4668/
                               PRE productcode=S18_4721/
                               PRE productcode=S18_4933/
                               PRE productcode=S24_1046/
                               PRE productcode=S24_1444/
                               PRE productcode=S24_1578/
                               PRE productcode=S24_1628/
                               PRE productcode=S24_1785/
                               PRE productcode=S24_1937/
                               PRE productcode=S24_2000/
                               PRE productcode=S24_2011/
                               PRE productcode=S24_2022/
                               PRE productcode=S24_2300/
                               PRE productcode=S24_2360/
                               PRE productcode=S24_2766/
                               PRE productcode=S24_2840/
                               PRE productcode=S24_2841/
                               PRE productcode=S24_2887/
                               PRE productcode=S24_2972/
                               PRE productcode=S24_3151/
                               PRE productcode=S24_3191/
                               PRE productcode=S24_3371/
                               PRE productcode=S24_3420/
                               PRE productcode=S24_3432/
                               PRE productcode=S24_3816/
                               PRE productcode=S24_3856/
                               PRE productcode=S24_3949/
                               PRE productcode=S24_3969/
                               PRE productcode=S24_4048/
                               PRE productcode=S24_4258/
                               PRE productcode=S24_4278/
                               PRE productcode=S24_4620/
                               PRE productcode=S32_1268/
                               PRE productcode=S32_1374/
                               PRE productcode=S32_2206/
                               PRE productcode=S32_2509/
                               PRE productcode=S32_3207/
                               PRE productcode=S32_3522/
                               PRE productcode=S32_4289/
                               PRE productcode=S32_4485/
                               PRE productcode=S50_1341/
                               PRE productcode=S50_1392/
                               PRE productcode=S50_1514/
                               PRE productcode=S50_4713/
                               PRE productcode=S700_1138/
                               PRE productcode=S700_1691/
                               PRE productcode=S700_1938/
                               PRE productcode=S700_2047/
                               PRE productcode=S700_2466/
                               PRE productcode=S700_2610/
                               PRE productcode=S700_2824/
                               PRE productcode=S700_2834/
                               PRE productcode=S700_3167/
                               PRE productcode=S700_3505/
                               PRE productcode=S700_3962/
                               PRE productcode=S700_4002/
                               PRE productcode=S72_1253/
                               PRE productcode=S72_3212/
    2024-09-29 19:14:23          0 


4.3.5. In case you want to read back the data, you can do it with the following code. Take into account that the order will change due to the usage of a partition column.


```python
train_data = pd.read_parquet(data_s3_url)
train_data.head()
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
      <th>customernumber</th>
      <th>creditlimit</th>
      <th>city_allentown</th>
      <th>city_auckland</th>
      <th>city_barcelona</th>
      <th>city_bergamo</th>
      <th>city_bergen</th>
      <th>city_boston</th>
      <th>city_brickhaven</th>
      <th>city_bridgewater</th>
      <th>...</th>
      <th>productscale_1:32</th>
      <th>productscale_1:50</th>
      <th>productscale_1:700</th>
      <th>productscale_1:72</th>
      <th>0-1 years</th>
      <th>1-3 years</th>
      <th>3-5 years</th>
      <th>5+ years</th>
      <th>scaled_productrating</th>
      <th>productcode</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2340</th>
      <td>462</td>
      <td>-0.302428</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>S10_1678</td>
    </tr>
    <tr>
      <th>2487</th>
      <td>496</td>
      <td>0.276212</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>S10_1678</td>
    </tr>
    <tr>
      <th>690</th>
      <td>171</td>
      <td>-0.371769</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>-0.5</td>
      <td>S10_1678</td>
    </tr>
    <tr>
      <th>71</th>
      <td>119</td>
      <td>0.472280</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>S10_1678</td>
    </tr>
    <tr>
      <th>305</th>
      <td>141</td>
      <td>3.088113</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>S10_1678</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 124 columns</p>
</div>



<a name='5'></a>
## 5 - Feature Creation for Test Dataset

Until now, you worked only on the transformations of your training data. When you need to test your model or perform inference, you should transform the incoming data using the same steps you followed for the training data. The only step that you do not have to apply is the `fit()` of the scalers or encoders; you only apply the `transform()` method over the test or inference data. The `fit()` method is used to compute the statistics from your training data, and those don't need to be recalculated to test the model.

Replicate the steps that you followed for training data to transform your test DataFrame `model_test_df`. Follow the instructions to do it.


```python
### START CODE HERE ### (5 lines of code)

# Convert the column names from the `model_test_df` dataframe into lowercase
model_test_df.columns = [col.lower() for col in model_test_df.columns] # @REPLACE EQUALS [col.None() for col in None.None]

# Creating the users dataframe from `model_test_df` with the `copy()` method
user_columns = ["customernumber", "city", "country", "creditlimit", "customersince"] # @KEEP

users_test_df = model_test_df[user_columns].copy() # @REPLACE EQUALS None[None].None()

# Creating the items dataframe from `model_test_df` with the `copy()` method
item_columns = ["productcode", "productline", "productscale", "quantityinstock", "buyprice", "msrp"] # @KEEP

items_test_df = model_test_df[item_columns].copy() # @REPLACE EQUALS None[None].None()

### END CODE HERE ###
```

<a name='5.1'></a>
### 5.1 - Feature Engineering for Numerical Variables

**Standardization.** You already have the `StandardScaler` objects that you fit over the training data. Use the `transform()` method of those objects and apply them to the test data (`users_test_df` and `items_test_df`). Below, you can see the numerical columns for the users and items dataframes.


```python
# Choosing the numerical columns to apply the standard scaler in the two datasets
user_num_columns_std = ["creditlimit"]
item_num_columns_std = ["quantityinstock", "buyprice", "msrp"]

### START CODE HERE ### (2 lines of code)

# Transforming the test data
user_test_num_vars_std = user_num_standard_scaler.transform(users_test_df[user_num_columns_std]) # @REPLACE EQUALS user_num_standard_scaler.None(None[None])
item_test_num_vars_std = item_num_standard_scaler.transform(items_test_df[item_num_columns_std]) # @REPLACE EQUALS item_num_standard_scaler.None(None[None])

### END CODE HERE ###

# Results are numpy arrays. Transform them into pandas dataframes
user_test_num_vars_std_df = pd.DataFrame(user_test_num_vars_std, columns=user_num_columns_std, index=users_test_df.index)
item_test_num_vars_std_df = pd.DataFrame(item_test_num_vars_std, columns=item_num_columns_std, index=items_test_df.index)

```


```python
user_test_num_vars_std_df.head()
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
      <th>creditlimit</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2309</th>
      <td>-1.402321</td>
    </tr>
    <tr>
      <th>2057</th>
      <td>0.548794</td>
    </tr>
    <tr>
      <th>194</th>
      <td>2.679240</td>
    </tr>
    <tr>
      <th>1393</th>
      <td>0.603789</td>
    </tr>
    <tr>
      <th>764</th>
      <td>-0.412417</td>
    </tr>
  </tbody>
</table>
</div>




```python
item_test_num_vars_std_df.head()
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
      <th>quantityinstock</th>
      <th>buyprice</th>
      <th>msrp</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2309</th>
      <td>-1.017123</td>
      <td>-1.512763</td>
      <td>-1.522262</td>
    </tr>
    <tr>
      <th>2057</th>
      <td>-1.166382</td>
      <td>-0.799420</td>
      <td>-1.083967</td>
    </tr>
    <tr>
      <th>194</th>
      <td>-0.925034</td>
      <td>-0.357093</td>
      <td>-0.277554</td>
    </tr>
    <tr>
      <th>1393</th>
      <td>0.181405</td>
      <td>1.626580</td>
      <td>2.289531</td>
    </tr>
    <tr>
      <th>764</th>
      <td>-0.368733</td>
      <td>1.286224</td>
      <td>0.987882</td>
    </tr>
  </tbody>
</table>
</div>



<a name='5.2'></a>
### 5.2 - Feature Engineering for Categorical Variables

5.2.1. Select the categorical features from the test dataframes based on the column names provided below. Then, convert all the strings into lowercase. After that, use the `transform()` method to compute the one-hot encodings and chain with the `todense()` method to get the complete matrix.


```python
# Column names for the categorical variables
user_cat_cols = ["city", "country"]
item_cat_cols = ["productline", "productscale"]

# Creating the datasets with only categorical features
users_test_cat_df = users_test_df[user_cat_cols].copy()
items_test_cat_df = items_test_df[item_cat_cols].copy()

# Converting string categories into lowercase
users_test_cat_df = users_test_cat_df.map(lambda x: x.strip().lower())
items_test_cat_df = items_test_cat_df.map(lambda x: x.strip().lower())

# Transform with the encoder objects
encoded_user_test_cat_features = user_cat_ohe.transform(users_test_cat_df).todense()
encoded_item_test_cat_features = item_cat_ohe.transform(items_test_cat_df).todense()

encoded_user_test_cat_df = pd.DataFrame(
    encoded_user_test_cat_features, 
    columns=user_cat_ohe.get_feature_names_out(user_cat_cols),
    index=users_test_df.index
)

encoded_item_test_cat_df = pd.DataFrame(
    encoded_item_test_cat_features, 
    columns=item_cat_ohe.get_feature_names_out(item_cat_cols),
    index=items_test_df.index
)

```


```python
encoded_user_test_cat_df.head()
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
      <th>city_allentown</th>
      <th>city_auckland</th>
      <th>city_barcelona</th>
      <th>city_bergamo</th>
      <th>city_bergen</th>
      <th>city_boston</th>
      <th>city_brickhaven</th>
      <th>city_bridgewater</th>
      <th>city_brisbane</th>
      <th>city_bruxelles</th>
      <th>...</th>
      <th>country_japan</th>
      <th>country_new zealand</th>
      <th>country_norway</th>
      <th>country_philippines</th>
      <th>country_singapore</th>
      <th>country_spain</th>
      <th>country_sweden</th>
      <th>country_switzerland</th>
      <th>country_uk</th>
      <th>country_usa</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2309</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>2057</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>194</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>1393</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>764</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 98 columns</p>
</div>




```python
encoded_item_test_cat_df.head()
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
      <th>productline_classic cars</th>
      <th>productline_motorcycles</th>
      <th>productline_planes</th>
      <th>productline_ships</th>
      <th>productline_trains</th>
      <th>productline_trucks and buses</th>
      <th>productline_vintage cars</th>
      <th>productscale_1:10</th>
      <th>productscale_1:12</th>
      <th>productscale_1:18</th>
      <th>productscale_1:24</th>
      <th>productscale_1:32</th>
      <th>productscale_1:50</th>
      <th>productscale_1:700</th>
      <th>productscale_1:72</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2309</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>2057</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>194</th>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>1393</th>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>764</th>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
  </tbody>
</table>
</div>



5.2.2. **Ranges.** Apply the `transform()` method of the `KBinsDiscretizer` objects to the test data. Again, you need to create the `loyalty_program_years` column to create the bins from it. You don't have to compute again the `current_date`.


```python
# Define the bin edges
bin_edges = [0, 1, 3, 5, float('inf')]

### START CODE HERE ### (4 lines of code)

# Convert the `customersince` column of the dataframe `users_test_df` to datetime data type with `pd.to_datetime()` method
users_test_df['customersince'] = pd.to_datetime(users_test_df['customersince'])  # @REPLACE EQUALS pd.None(None['None'])

# Create the column with the difference between the `current_date` value and the `customersince` column of the `users_test_df` dataframe
# Convert the value in days by applying `dt.days` method and make an integer division by 365
users_test_df['loyalty_program_years'] = (current_date - users_test_df['customersince']).dt.days // 365 # @REPLACE EQUALS (None - None['None']).None.None // None

# Select `loyalty_program_years` from the dataframe `users_test_df`. Use double brackets to output it as a dataframe, not a series
loyalty_program_years_test = users_test_df[['loyalty_program_years']] # @REPLACE EQUALS None[['None']]

# Apply `transform()` method to transform to the dataframe `loyalty_program_years_test`
loyalty_program_years_test_binned = kbins.transform(loyalty_program_years_test) # @REPLACE EQUALS kbins.None(None)

### END CODE HERE ###

# Convert the binned data to a dataframe with appropriate column names
bin_labels = ['0-1 years', '1-3 years', '3-5 years', '5+ years']
loyalty_program_years_test_binned_df = pd.DataFrame(loyalty_program_years_test_binned, columns=bin_labels, index=users_test_df.index)

loyalty_program_years_test_binned_df.head()
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
      <th>0-1 years</th>
      <th>1-3 years</th>
      <th>3-5 years</th>
      <th>5+ years</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2309</th>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>2057</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>194</th>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>1393</th>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>764</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
    </tr>
  </tbody>
</table>
</div>



5.2.3. Finally, perform the transformation over the ratings. Take into account that at inference time you will not have access to the labels but when you are validating the performance of your model, you need the ground truth to compare with the model's prediction. That's the reason why you will also transform the ratings from the test set.


```python
ratings_test = rating_scaler.transform(model_test_df[["productrating"]])

scaled_ratings_test_df = pd.DataFrame(ratings_test, columns=["scaled_productrating"], index=model_test_df.index)
scaled_ratings_test_df.head()
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
      <th>scaled_productrating</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2309</th>
      <td>1.0</td>
    </tr>
    <tr>
      <th>2057</th>
      <td>0.5</td>
    </tr>
    <tr>
      <th>194</th>
      <td>-0.5</td>
    </tr>
    <tr>
      <th>1393</th>
      <td>0.5</td>
    </tr>
    <tr>
      <th>764</th>
      <td>-0.5</td>
    </tr>
  </tbody>
</table>
</div>



<a name='5.3'></a>
### 5.3 - Feature Storage

It is time to collect all your transformed dataframes into one that will be saved into the S3 bucket.


```python
transformed_test_df = pd.concat([
                                    users_test_df[["customernumber"]],
                                    user_test_num_vars_std_df, 
                                    encoded_user_test_cat_df,
                                    items_test_df[["productcode"]],
                                    item_test_num_vars_std_df, 
                                    encoded_item_test_cat_df,
                                    scaled_ratings_test_df
                                ], 
                                axis=1
                                )

transformed_test_df.head()
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
      <th>customernumber</th>
      <th>creditlimit</th>
      <th>city_allentown</th>
      <th>city_auckland</th>
      <th>city_barcelona</th>
      <th>city_bergamo</th>
      <th>city_bergen</th>
      <th>city_boston</th>
      <th>city_brickhaven</th>
      <th>city_bridgewater</th>
      <th>...</th>
      <th>productline_vintage cars</th>
      <th>productscale_1:10</th>
      <th>productscale_1:12</th>
      <th>productscale_1:18</th>
      <th>productscale_1:24</th>
      <th>productscale_1:32</th>
      <th>productscale_1:50</th>
      <th>productscale_1:700</th>
      <th>productscale_1:72</th>
      <th>scaled_productrating</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2309</th>
      <td>456</td>
      <td>-1.402321</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>2057</th>
      <td>386</td>
      <td>0.548794</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.5</td>
    </tr>
    <tr>
      <th>194</th>
      <td>124</td>
      <td>2.679240</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>-0.5</td>
    </tr>
    <tr>
      <th>1393</th>
      <td>286</td>
      <td>0.603789</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.5</td>
    </tr>
    <tr>
      <th>764</th>
      <td>177</td>
      <td>-0.412417</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>-0.5</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 120 columns</p>
</div>



Then, you need to save the `transformed_test_df` dataframe into the S3 bucket. Use the provided path and remember to partition the data by the `productcode` column.


```python
data_s3_url = f's3://{BUCKET_NAME}/preprocessing/data/ratings_for_ml/test'

transformed_test_df.to_parquet(data_s3_url,
                                compression='snappy',
                                engine='pyarrow',
                                partition_cols=['productcode'],
                                existing_data_behavior='delete_matching'                                
                            )
```

In this lab, you gained practical experience in feature engineering for both numerical and categorical data, a vital step in the ML process.

You started with numerical data, focusing on standardization. By using tools like `StandardScaler` from `scikit-learn`, you learned how to standardize numerical features to have a mean of zero and a standard deviation of one. This transformation is crucial for many ML algorithms that are sensitive to the scale of input data.

Next, you addressed categorical data by transforming it into a format suitable for ML models. Using techniques like one-hot encoding, you converted categorical variables into binary vectors. This method allows ML algorithms, which typically require numerical input, to effectively utilize categorical data. One-hot encoding ensures that no ordinal relationship is implied among the categories, preserving the integrity of the categorical data.

Finally, you combined the standardized numerical data and the encoded categorical data into a unified dataset.

Throughout this lab, you developed a solid foundation in Feature Engineering and gained an understanding of the critical role of Data Engineering in this process. The ability to preprocess and transform raw data into a suitable format is essential for building high-performing models and deriving meaningful insights from your data.


```python

```
