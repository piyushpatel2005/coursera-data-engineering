# Week 1 Lab: Data Normalization

In this lab, you will learn how to transform a database table from the "One Big Table" (OBT) form into the First Normal Form (1NF), Second Normal Form (2NF), and Third Normal Form (3NF). This process is fundamental to database normalization, which helps reduce data redundancy and improve data integrity.

# Table of Contents

- [ 1 - Introduction](#1)
  - [ 1.1 - Data Normalization](#1.1)
  - [ 1.2 - Dataset](#1.2)
- [ 2 - First Normal Form (1NF)](#2)
- [ 3 - Second Normal Form (2NF)](#3)
- [ 4 - Third Normal Form (3NF)](#4)

<a name='1'></a>
## 1 - Introduction

As a Data Engineer, you may not frequently need to perform data normalization from scratch, but understanding the steps involved in this process is crucial. Typically, you will encounter source databases that are already normalized, and your task will often involve denormalizing this data to make it useful for extracting insights or solving business questions. This lab focuses on the opposite process: taking a dataset that has been loaded as a One Big Table and normalizing it up to the third normal form, which is common in transactional systems.

<a name='1.1'></a>
### 1.1 - Data Normalization

Normalization is a database design technique that organizes tables to minimize redundancy and dependency. It involves dividing large tables into smaller, less redundant tables and defining relationships between them. The goal is to isolate data so that additions, deletions, and modifications can be made in a single table and then propagated through the rest of the database using defined relationships.

Some of the benefits of having a normalized set of tables are the following: 
- Reduce Data Redundancy: Eliminating duplicate data, which helps in saving storage space and ensures consistency across the database.
- Improve Data Integrity: Ensuring that each piece of data is stored in only one place, reducing the likelihood of data anomalies and maintaining the accuracy of the data.
- Enhance Query Performance: By organizing data into related tables, you have made it easier to query and manage the data, leading to better performance and easier maintenance.

<a name='1.2'></a>
### 1.2 - Dataset

The dataset that you are going to use is related to the typical [`classicmodels`](https://www.mysqltutorial.org/mysql-sample-database.aspx) dataset that you have used but has been transformed to generate One Big Table. The original data comes in a multiline JSON file where each JSON object has the following structure:

```json
{
  "orderNumber": 10100,
  "orderDate": "2003-01-06",
  "requiredDate": "2003-01-13",
  "shippedDate": "2003-01-10",
  "status": "Shipped",
  "comments": null,
  "orderDetails": [
    {
      "productCode": "S18_1749",
      "quantityOrdered": 30,
      "priceEach": 136.00
    },
    {
      "productCode": "S18_2248",
      "quantityOrdered": 50,
      "priceEach": 55.09
    },
    {
      "productCode": "S18_4409",
      "quantityOrdered": 22,
      "priceEach": 75.46
    },
    {
      "productCode": "S24_3969",
      "quantityOrdered": 49,
      "priceEach": 35.29
    }
  ],
  "customer": {
    "customerName": "Online Diecast Creations Co.",
    "contactLastName": "Young",
    "contactFirstName": "Dorothy",
    "phone": "6035558647",
    "addressLine1": "2304 Long Airport Avenue",
    "addressLine2": null,
    "city": "Nashua",
    "state": "NH",
    "postalCode": "62005",
    "country": "USA",
    "salesRepEmployeeNumber": 1216.00,
    "creditLimit": 114200.00
  }
}
```

This dataset has already been uploaded into the database that you are going to use by following this schema:

![ERD_OBT](./images/ERD_OBT.png)

As you can see, a schema named `classicmodels_obt` with a table named `orders` was added. Notice, that the `orderDetails` and `customer` fields have been saved as JSON objects directly in the database, they are structured as a dictionary with key-value pairs holding information about each order and customer.

To explore the data, let's import all the necessary packages and SQL extensions for running the `%sql` magic commands used in this notebook:


```python
import os 
import json

import pandas as pd
import psycopg2

from dotenv import load_dotenv
from sqlalchemy import create_engine

pd.set_option('display.max_columns', 30)
```


```python
%load_ext sql
```

In the AWS console, go to **CloudFormation** where two stacks have already been deployed. One is associated with your Cloud environment with a name prefix `aws-cloud9`; and another with an alphanumeric ID. Click on the alphanumeric ID stack and it will take you to another screen page with details about this stack. In the **Outputs** tab, you will see the key `PostgresEndpoint` and its corresponding **Value** column. Copy the value and edit the `./src/env` file, replacing the placeholder `<RDS-ENDPOINT>` with the endpoint value. Save changes to the file.

Execute the following cell to load the environment variables and connect to the database:


```python
load_dotenv('./src/env', override=True)

DBHOST = os.getenv('DBHOST')
DBPORT = os.getenv('DBPORT')
DBNAME = os.getenv('DBNAME')
DBUSER = os.getenv('DBUSER')
DBPASSWORD = os.getenv('DBPASSWORD')

connection_url = f"postgresql+psycopg2://{DBUSER}:{DBPASSWORD}@{DBHOST}:{DBPORT}/{DBNAME}"

%sql {connection_url}
     
```

Explore the loaded data:


```sql
%%sql
select count(*) from classicmodels_obt.orders;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1lab1-rds.c9g6s0k8ogtn.us-east-1.rds.amazonaws.com:5432/postgres
    1 rows affected.





<table>
    <thead>
        <tr>
            <th>count</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>326</td>
        </tr>
    </tbody>
</table>




```sql
%%sql
select * from classicmodels_obt.orders limit 3;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1lab1-rds.c9g6s0k8ogtn.us-east-1.rds.amazonaws.com:5432/postgres
    3 rows affected.





<table>
    <thead>
        <tr>
            <th>ordernumber</th>
            <th>orderdate</th>
            <th>requireddate</th>
            <th>shippeddate</th>
            <th>status</th>
            <th>comments</th>
            <th>orderdetails</th>
            <th>customer</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>10100</td>
            <td>2003-01-06</td>
            <td>2003-01-13</td>
            <td>2003-01-10</td>
            <td>Shipped</td>
            <td>None</td>
            <td>[{&#x27;priceEach&#x27;: 136.0, &#x27;productCode&#x27;: &#x27;S18_1749&#x27;, &#x27;quantityOrdered&#x27;: 30}, {&#x27;priceEach&#x27;: 55.09, &#x27;productCode&#x27;: &#x27;S18_2248&#x27;, &#x27;quantityOrdered&#x27;: 50}, {&#x27;priceEach&#x27;: 75.46, &#x27;productCode&#x27;: &#x27;S18_4409&#x27;, &#x27;quantityOrdered&#x27;: 22}, {&#x27;priceEach&#x27;: 35.29, &#x27;productCode&#x27;: &#x27;S24_3969&#x27;, &#x27;quantityOrdered&#x27;: 49}]</td>
            <td>{&#x27;city&#x27;: &#x27;Nashua&#x27;, &#x27;phone&#x27;: &#x27;6035558647&#x27;, &#x27;state&#x27;: &#x27;NH&#x27;, &#x27;country&#x27;: &#x27;USA&#x27;, &#x27;postalCode&#x27;: &#x27;62005&#x27;, &#x27;creditLimit&#x27;: 114200.0, &#x27;addressLine1&#x27;: &#x27;2304 Long Airport Avenue&#x27;, &#x27;addressLine2&#x27;: None, &#x27;customerName&#x27;: &#x27;Online Diecast Creations Co.&#x27;, &#x27;contactLastName&#x27;: &#x27;Young&#x27;, &#x27;contactFirstName&#x27;: &#x27;Dorothy&#x27;, &#x27;salesRepEmployeeNumber&#x27;: 1216.0}</td>
        </tr>
        <tr>
            <td>10101</td>
            <td>2003-01-09</td>
            <td>2003-01-18</td>
            <td>2003-01-11</td>
            <td>Shipped</td>
            <td>Check on availability.</td>
            <td>[{&#x27;priceEach&#x27;: 108.06, &#x27;productCode&#x27;: &#x27;S18_2325&#x27;, &#x27;quantityOrdered&#x27;: 25}, {&#x27;priceEach&#x27;: 167.06, &#x27;productCode&#x27;: &#x27;S18_2795&#x27;, &#x27;quantityOrdered&#x27;: 26}, {&#x27;priceEach&#x27;: 32.53, &#x27;productCode&#x27;: &#x27;S24_1937&#x27;, &#x27;quantityOrdered&#x27;: 45}, {&#x27;priceEach&#x27;: 44.35, &#x27;productCode&#x27;: &#x27;S24_2022&#x27;, &#x27;quantityOrdered&#x27;: 46}]</td>
            <td>{&#x27;city&#x27;: &#x27;Frankfurt&#x27;, &#x27;phone&#x27;: &#x27;+49 69 66 90 2555&#x27;, &#x27;state&#x27;: None, &#x27;country&#x27;: &#x27;Germany&#x27;, &#x27;postalCode&#x27;: &#x27;60528&#x27;, &#x27;creditLimit&#x27;: 59700.0, &#x27;addressLine1&#x27;: &#x27;Lyonerstr. 34&#x27;, &#x27;addressLine2&#x27;: None, &#x27;customerName&#x27;: &#x27;Blauer See Auto, Co.&#x27;, &#x27;contactLastName&#x27;: &#x27;Keitel&#x27;, &#x27;contactFirstName&#x27;: &#x27;Roland&#x27;, &#x27;salesRepEmployeeNumber&#x27;: 1504.0}</td>
        </tr>
        <tr>
            <td>10102</td>
            <td>2003-01-10</td>
            <td>2003-01-18</td>
            <td>2003-01-14</td>
            <td>Shipped</td>
            <td>None</td>
            <td>[{&#x27;priceEach&#x27;: 95.55, &#x27;productCode&#x27;: &#x27;S18_1342&#x27;, &#x27;quantityOrdered&#x27;: 39}, {&#x27;priceEach&#x27;: 43.13, &#x27;productCode&#x27;: &#x27;S18_1367&#x27;, &#x27;quantityOrdered&#x27;: 41}]</td>
            <td>{&#x27;city&#x27;: &#x27;NYC&#x27;, &#x27;phone&#x27;: &#x27;2125551500&#x27;, &#x27;state&#x27;: &#x27;NY&#x27;, &#x27;country&#x27;: &#x27;USA&#x27;, &#x27;postalCode&#x27;: &#x27;10022&#x27;, &#x27;creditLimit&#x27;: 76400.0, &#x27;addressLine1&#x27;: &#x27;2678 Kingston Rd.&#x27;, &#x27;addressLine2&#x27;: &#x27;Suite 101&#x27;, &#x27;customerName&#x27;: &#x27;Vitachrome Inc.&#x27;, &#x27;contactLastName&#x27;: &#x27;Frick&#x27;, &#x27;contactFirstName&#x27;: &#x27;Michael&#x27;, &#x27;salesRepEmployeeNumber&#x27;: 1286.0}</td>
        </tr>
    </tbody>
</table>



The dataset has been generated into a One Big Table (OBT) from a multiline JSON file, consolidating all data into a single dataset for query processing. The `orderdetails` and `customer` fields are not basic data types, they are dictionaries with the following structure:

- `orderdetails` is a list of dictionaries/JSON objects about all the products under an individual order. Each entry on the list refers to a product, with keys on its product code, the quantity ordered and the unitary price.

- `customer` field contains a dictionary/JSON object where each key corresponds to a feature of the customer that placed the order, this includes information on personal details, contact, and location.

Now you will perform some basic transformations to the dataset to achieve the three different normal forms and separate the data in each form in a different schema.

<a name='2'></a>
## 2 - First Normal Form (1NF)

Your first task is to create a First Normal Form (1NF) of this dataset and insert it into the database. For that, you will read the data using an SQL query and will transform the data using `pandas` package. 

The feature of the First Normal Form is that a relation in this form does not contain any multi-valued field. That means that each attribute/field/column contains only atomic or single values.

Given the current form that our dataset has, in order to achieve a 1NF you need to unnest the `orderdetails` list and for each element, you will create a row. In addition, as each element is a JSON object or dictionary (which is a multi-valued field), you also have to unnest the data and create a new field or column for each key inside this dictionary. This last step needs to be replicated in the `customer` JSON object field.

The final schema after the 1NF will look like the following image 

![ERD_1NF_orders](./images/ERD_1NF_Orders.png)

2.1. Create the schema in which the relations in 1NF will be stored and then read the OBT dataset and save it as a `pandas` dataframe.


```sql
%%sql
CREATE SCHEMA IF NOT EXISTS classicmodels_1nf;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1lab1-rds.c9g6s0k8ogtn.us-east-1.rds.amazonaws.com:5432/postgres
    Done.





    []



Have a look again at the original data:


```python
result = %sql select * from classicmodels_obt.orders

df = result.DataFrame()

df.head()
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1lab1-rds.c9g6s0k8ogtn.us-east-1.rds.amazonaws.com:5432/postgres
    326 rows affected.





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
      <th>ordernumber</th>
      <th>orderdate</th>
      <th>requireddate</th>
      <th>shippeddate</th>
      <th>status</th>
      <th>comments</th>
      <th>orderdetails</th>
      <th>customer</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>10100</td>
      <td>2003-01-06</td>
      <td>2003-01-13</td>
      <td>2003-01-10</td>
      <td>Shipped</td>
      <td>None</td>
      <td>[{'priceEach': 136.0, 'productCode': 'S18_1749...</td>
      <td>{'city': 'Nashua', 'phone': '6035558647', 'sta...</td>
    </tr>
    <tr>
      <th>1</th>
      <td>10101</td>
      <td>2003-01-09</td>
      <td>2003-01-18</td>
      <td>2003-01-11</td>
      <td>Shipped</td>
      <td>Check on availability.</td>
      <td>[{'priceEach': 108.06, 'productCode': 'S18_232...</td>
      <td>{'city': 'Frankfurt', 'phone': '+49 69 66 90 2...</td>
    </tr>
    <tr>
      <th>2</th>
      <td>10102</td>
      <td>2003-01-10</td>
      <td>2003-01-18</td>
      <td>2003-01-14</td>
      <td>Shipped</td>
      <td>None</td>
      <td>[{'priceEach': 95.55, 'productCode': 'S18_1342...</td>
      <td>{'city': 'NYC', 'phone': '2125551500', 'state'...</td>
    </tr>
    <tr>
      <th>3</th>
      <td>10103</td>
      <td>2003-01-29</td>
      <td>2003-02-07</td>
      <td>2003-02-02</td>
      <td>Shipped</td>
      <td>None</td>
      <td>[{'priceEach': 214.3, 'productCode': 'S10_1949...</td>
      <td>{'city': 'Stavern', 'phone': '07-98 9555', 'st...</td>
    </tr>
    <tr>
      <th>4</th>
      <td>10104</td>
      <td>2003-01-31</td>
      <td>2003-02-09</td>
      <td>2003-02-01</td>
      <td>Shipped</td>
      <td>None</td>
      <td>[{'priceEach': 131.44, 'productCode': 'S12_314...</td>
      <td>{'city': 'Madrid', 'phone': '(91) 555 94 44', ...</td>
    </tr>
  </tbody>
</table>
</div>



2.2. Create a new flat table with the dictionaries extracted from the `customer` field of the `df` dataframe. You can use the `pandas` [`json_normalize()` method](https://pandas.pydata.org/docs/reference/api/pandas.json_normalize.html) over the `customer` field for this purpose. This function will return a dataframe with the key-value pairs as columns of the new table.

*Note*: In the cells where you see the comments `### START CODE HERE ###` and `### END CODE HERE ###` you need to complete the code replacing all `None`. The rest of the cells are already complete, you just need to review and run the code.


```python
### START CODE HERE ### (1 line of code)
customers_df = pd.json_normalize(df['customer']) # @REPLACE EQUALS pd.None(None['None'])
### END CODE HERE ###

customers_df.head()
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
      <th>city</th>
      <th>phone</th>
      <th>state</th>
      <th>country</th>
      <th>postalCode</th>
      <th>creditLimit</th>
      <th>addressLine1</th>
      <th>addressLine2</th>
      <th>customerName</th>
      <th>contactLastName</th>
      <th>contactFirstName</th>
      <th>salesRepEmployeeNumber</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Nashua</td>
      <td>6035558647</td>
      <td>NH</td>
      <td>USA</td>
      <td>62005</td>
      <td>114200.0</td>
      <td>2304 Long Airport Avenue</td>
      <td>None</td>
      <td>Online Diecast Creations Co.</td>
      <td>Young</td>
      <td>Dorothy</td>
      <td>1216.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Frankfurt</td>
      <td>+49 69 66 90 2555</td>
      <td>None</td>
      <td>Germany</td>
      <td>60528</td>
      <td>59700.0</td>
      <td>Lyonerstr. 34</td>
      <td>None</td>
      <td>Blauer See Auto, Co.</td>
      <td>Keitel</td>
      <td>Roland</td>
      <td>1504.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>NYC</td>
      <td>2125551500</td>
      <td>NY</td>
      <td>USA</td>
      <td>10022</td>
      <td>76400.0</td>
      <td>2678 Kingston Rd.</td>
      <td>Suite 101</td>
      <td>Vitachrome Inc.</td>
      <td>Frick</td>
      <td>Michael</td>
      <td>1286.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Stavern</td>
      <td>07-98 9555</td>
      <td>None</td>
      <td>Norway</td>
      <td>4110</td>
      <td>81700.0</td>
      <td>Erling Skakkes gate 78</td>
      <td>None</td>
      <td>Baane Mini Imports</td>
      <td>Bergulfsen</td>
      <td>Jonas</td>
      <td>1504.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Madrid</td>
      <td>(91) 555 94 44</td>
      <td>None</td>
      <td>Spain</td>
      <td>28034</td>
      <td>227600.0</td>
      <td>C/ Moralzarzal, 86</td>
      <td>None</td>
      <td>Euro+ Shopping Channel</td>
      <td>Freyre</td>
      <td>Diego</td>
      <td>1370.0</td>
    </tr>
  </tbody>
</table>
</div>



##### __Expected Output__

| **city**    | **phone**         | **state** | **country** | **postalCode** | **creditLimit** | **addressLine1**           | **addressLine2** | **customerName**              | **contactLastName** | **contactFirstName** | **salesRepEmployeeNumber** |
| ----------- | ----------------- | --------- | ----------- | -------------- | --------------- | -------------------------- | ---------------- | ----------------------------- | ------------------- | ------------------- | ------------------------ |
| Nashua      | 6035558647        | NH        | USA         | 62005          | 114200.0        | 2304 Long Airport Avenue   | None             | Online Diecast Creations Co.  | Young               | Dorothy              | 1216.0                   |
| Frankfurt   | +49 69 66 90 2555 | None      | Germany     | 60528          | 59700.0         | Lyonerstr. 34              | None             | Blauer See Auto, Co.          | Keitel              | Roland               | 1504.0                   |
| NYC         | 2125551500        | NY        | USA         | 10022          | 76400.0         | 2678 Kingston Rd.          | Suite 101        | Vitachrome Inc.               | Frick               | Michael              | 1286.0                   |
| Stavern     | 07-98 9555        | None      | Norway      | 4110           | 81700.0         | Erling Skakkes gate 78     | None             | Baane Mini Imports            | Bergulfsen          | Jonas                | 1504.0                   |
| Madrid      | (91) 555 94 44    | None      | Spain       | 28034          | 227600.0        | C/ Moralzarzal, 86         | None             | Euro+ Shopping Channel        | Freyre              | Diego                | 1370.0                  |


`pd.json_normalize` creates a DataFrame where each dictionary in the `customer` column is flattened into a row. The index of the original DataFrame is preserved, which is crucial for maintaining the correct relationship between the original rows and the new flattened rows. It is time to concatenate the two datasets. 

2.3. You need to drop the `customer` column from the original dataframe, using `drop()` method and specifying the column. You should keep `inplace` argument equal to `True`. 

Then concatenate the dataframe `df` with `customers_df`. For that, you will use `pd.concat` method with the `axis` parameter set as 1. Using `pd.concat` with `axis=1` joins the DataFrames column-wise, aligning rows by their index. Since the index is preserved, each row in the flattened `customers_df` dataframe aligns correctly with its corresponding row in the original dataframe.


```python
### START CODE HERE ### (2 lines of code)
df.drop(columns='customer', inplace=True) # @REPLACE df.None(columns='None', inplace=True)
df = pd.concat([df, customers_df], axis=1) # @REPLACE EQUALS pd.None([df, None], axis=1)
### END CODE HERE ###

df.head()
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
      <th>ordernumber</th>
      <th>orderdate</th>
      <th>requireddate</th>
      <th>shippeddate</th>
      <th>status</th>
      <th>comments</th>
      <th>orderdetails</th>
      <th>city</th>
      <th>phone</th>
      <th>state</th>
      <th>country</th>
      <th>postalCode</th>
      <th>creditLimit</th>
      <th>addressLine1</th>
      <th>addressLine2</th>
      <th>customerName</th>
      <th>contactLastName</th>
      <th>contactFirstName</th>
      <th>salesRepEmployeeNumber</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>10100</td>
      <td>2003-01-06</td>
      <td>2003-01-13</td>
      <td>2003-01-10</td>
      <td>Shipped</td>
      <td>None</td>
      <td>[{'priceEach': 136.0, 'productCode': 'S18_1749...</td>
      <td>Nashua</td>
      <td>6035558647</td>
      <td>NH</td>
      <td>USA</td>
      <td>62005</td>
      <td>114200.0</td>
      <td>2304 Long Airport Avenue</td>
      <td>None</td>
      <td>Online Diecast Creations Co.</td>
      <td>Young</td>
      <td>Dorothy</td>
      <td>1216.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>10101</td>
      <td>2003-01-09</td>
      <td>2003-01-18</td>
      <td>2003-01-11</td>
      <td>Shipped</td>
      <td>Check on availability.</td>
      <td>[{'priceEach': 108.06, 'productCode': 'S18_232...</td>
      <td>Frankfurt</td>
      <td>+49 69 66 90 2555</td>
      <td>None</td>
      <td>Germany</td>
      <td>60528</td>
      <td>59700.0</td>
      <td>Lyonerstr. 34</td>
      <td>None</td>
      <td>Blauer See Auto, Co.</td>
      <td>Keitel</td>
      <td>Roland</td>
      <td>1504.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>10102</td>
      <td>2003-01-10</td>
      <td>2003-01-18</td>
      <td>2003-01-14</td>
      <td>Shipped</td>
      <td>None</td>
      <td>[{'priceEach': 95.55, 'productCode': 'S18_1342...</td>
      <td>NYC</td>
      <td>2125551500</td>
      <td>NY</td>
      <td>USA</td>
      <td>10022</td>
      <td>76400.0</td>
      <td>2678 Kingston Rd.</td>
      <td>Suite 101</td>
      <td>Vitachrome Inc.</td>
      <td>Frick</td>
      <td>Michael</td>
      <td>1286.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>10103</td>
      <td>2003-01-29</td>
      <td>2003-02-07</td>
      <td>2003-02-02</td>
      <td>Shipped</td>
      <td>None</td>
      <td>[{'priceEach': 214.3, 'productCode': 'S10_1949...</td>
      <td>Stavern</td>
      <td>07-98 9555</td>
      <td>None</td>
      <td>Norway</td>
      <td>4110</td>
      <td>81700.0</td>
      <td>Erling Skakkes gate 78</td>
      <td>None</td>
      <td>Baane Mini Imports</td>
      <td>Bergulfsen</td>
      <td>Jonas</td>
      <td>1504.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>10104</td>
      <td>2003-01-31</td>
      <td>2003-02-09</td>
      <td>2003-02-01</td>
      <td>Shipped</td>
      <td>None</td>
      <td>[{'priceEach': 131.44, 'productCode': 'S12_314...</td>
      <td>Madrid</td>
      <td>(91) 555 94 44</td>
      <td>None</td>
      <td>Spain</td>
      <td>28034</td>
      <td>227600.0</td>
      <td>C/ Moralzarzal, 86</td>
      <td>None</td>
      <td>Euro+ Shopping Channel</td>
      <td>Freyre</td>
      <td>Diego</td>
      <td>1370.0</td>
    </tr>
  </tbody>
</table>
</div>



##### __Expected Output__

*Note*: Some text is omitted.

| **ordernumber** | **orderdate** | **requireddate** | **shippeddate** | **status** | **comments**             | **orderdetails** | **city**    | **phone**         | **state** | **country** | **postalCode** | **creditLimit** | **addressLine1**           | **addressLine2** | **customerName**              | **contactLastName** | **contactFirstName** | **salesRepEmployeeNumber** |
| --------------- | ------------- | ---------------- | --------------- | ---------- | ----------------------- | ---------------- | ----------- | ----------------- | --------- | ----------- | -------------- | --------------- | -------------------------- | ---------------- | ----------------------------- | ------------------- | ------------------- | ------------------------ |
| 10100           | 2003-01-06    | 2003-01-13       | 2003-01-10      | Shipped    | None                    | text...          | Nashua      | 6035558647        | NH        | USA         | 62005          | 114200.0        | 2304 Long Airport Avenue   | None             | Online Diecast Creations Co.  | Young               | Dorothy              | 1216.0                   |
| 10101           | 2003-01-09    | 2003-01-18       | 2003-01-11      | Shipped    | Check on availability.  | text...          | Frankfurt   | +49 69 66 90 2555 | None      | Germany     | 60528          | 59700.0         | Lyonerstr. 34              | None             | Blauer See Auto, Co.          | Keitel              | Roland               | 1504.0                   |
| 10102           | 2003-01-10    | 2003-01-18       | 2003-01-14      | Shipped    | None                    | text...          | NYC         | 2125551500        | NY        | USA         | 10022          | 76400.0         | 2678 Kingston Rd.          | Suite 101        | Vitachrome Inc.               | Frick               | Michael              | 1286.0                   |
| 10103           | 2003-01-29    | 2003-02-07       | 2003-02-02      | Shipped    | None                    | text...          | Stavern     | 07-98 9555        | None      | Norway      | 4110           | 81700.0         | Erling Skakkes gate 78     | None             | Baane Mini Imports            | Bergulfsen          | Jonas                | 1504.0                   |
| 10104           | 2003-01-31    | 2003-02-09       | 2003-02-01      | Shipped    | None                    | text...          | Madrid      | (91) 555 94 44    | None      | Spain       | 28034          | 227600.0        | C/ Moralzarzal, 86         | None             | Euro+ Shopping Channel        | Freyre              | Diego                | 1370.0                  |


2.4. Add an ID column with each entry holding a unique identifier for each customer in addition to the customer's name. (The code below is complete; no change is required).


```python
df['customerNumber'] = pd.factorize(df['customerName'])[0] + 1
df.head()
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
      <th>ordernumber</th>
      <th>orderdate</th>
      <th>requireddate</th>
      <th>shippeddate</th>
      <th>status</th>
      <th>comments</th>
      <th>orderdetails</th>
      <th>city</th>
      <th>phone</th>
      <th>state</th>
      <th>country</th>
      <th>postalCode</th>
      <th>creditLimit</th>
      <th>addressLine1</th>
      <th>addressLine2</th>
      <th>customerName</th>
      <th>contactLastName</th>
      <th>contactFirstName</th>
      <th>salesRepEmployeeNumber</th>
      <th>customerNumber</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>10100</td>
      <td>2003-01-06</td>
      <td>2003-01-13</td>
      <td>2003-01-10</td>
      <td>Shipped</td>
      <td>None</td>
      <td>[{'priceEach': 136.0, 'productCode': 'S18_1749...</td>
      <td>Nashua</td>
      <td>6035558647</td>
      <td>NH</td>
      <td>USA</td>
      <td>62005</td>
      <td>114200.0</td>
      <td>2304 Long Airport Avenue</td>
      <td>None</td>
      <td>Online Diecast Creations Co.</td>
      <td>Young</td>
      <td>Dorothy</td>
      <td>1216.0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>10101</td>
      <td>2003-01-09</td>
      <td>2003-01-18</td>
      <td>2003-01-11</td>
      <td>Shipped</td>
      <td>Check on availability.</td>
      <td>[{'priceEach': 108.06, 'productCode': 'S18_232...</td>
      <td>Frankfurt</td>
      <td>+49 69 66 90 2555</td>
      <td>None</td>
      <td>Germany</td>
      <td>60528</td>
      <td>59700.0</td>
      <td>Lyonerstr. 34</td>
      <td>None</td>
      <td>Blauer See Auto, Co.</td>
      <td>Keitel</td>
      <td>Roland</td>
      <td>1504.0</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>10102</td>
      <td>2003-01-10</td>
      <td>2003-01-18</td>
      <td>2003-01-14</td>
      <td>Shipped</td>
      <td>None</td>
      <td>[{'priceEach': 95.55, 'productCode': 'S18_1342...</td>
      <td>NYC</td>
      <td>2125551500</td>
      <td>NY</td>
      <td>USA</td>
      <td>10022</td>
      <td>76400.0</td>
      <td>2678 Kingston Rd.</td>
      <td>Suite 101</td>
      <td>Vitachrome Inc.</td>
      <td>Frick</td>
      <td>Michael</td>
      <td>1286.0</td>
      <td>3</td>
    </tr>
    <tr>
      <th>3</th>
      <td>10103</td>
      <td>2003-01-29</td>
      <td>2003-02-07</td>
      <td>2003-02-02</td>
      <td>Shipped</td>
      <td>None</td>
      <td>[{'priceEach': 214.3, 'productCode': 'S10_1949...</td>
      <td>Stavern</td>
      <td>07-98 9555</td>
      <td>None</td>
      <td>Norway</td>
      <td>4110</td>
      <td>81700.0</td>
      <td>Erling Skakkes gate 78</td>
      <td>None</td>
      <td>Baane Mini Imports</td>
      <td>Bergulfsen</td>
      <td>Jonas</td>
      <td>1504.0</td>
      <td>4</td>
    </tr>
    <tr>
      <th>4</th>
      <td>10104</td>
      <td>2003-01-31</td>
      <td>2003-02-09</td>
      <td>2003-02-01</td>
      <td>Shipped</td>
      <td>None</td>
      <td>[{'priceEach': 131.44, 'productCode': 'S12_314...</td>
      <td>Madrid</td>
      <td>(91) 555 94 44</td>
      <td>None</td>
      <td>Spain</td>
      <td>28034</td>
      <td>227600.0</td>
      <td>C/ Moralzarzal, 86</td>
      <td>None</td>
      <td>Euro+ Shopping Channel</td>
      <td>Freyre</td>
      <td>Diego</td>
      <td>1370.0</td>
      <td>5</td>
    </tr>
  </tbody>
</table>
</div>



Now that the `customer` field has been transformed into atomic-valued fields, you need to do the same for the `orderdetails` column. 

2.5. Create a new row for each product in the same order using the `pandas` [`explode()` method](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.explode.html) on `orderdetails` column of the original `df` dataframe. Make sure to set the `ignore_index` parameter to `True`.


```python
### START CODE HERE ### (1 line of code)
df_exploded = df.explode('orderdetails', ignore_index=True) # @REPLACE EQUALS df.None('None', ignore_index=None)
### END CODE HERE ###

df_exploded.head()
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
      <th>ordernumber</th>
      <th>orderdate</th>
      <th>requireddate</th>
      <th>shippeddate</th>
      <th>status</th>
      <th>comments</th>
      <th>orderdetails</th>
      <th>city</th>
      <th>phone</th>
      <th>state</th>
      <th>country</th>
      <th>postalCode</th>
      <th>creditLimit</th>
      <th>addressLine1</th>
      <th>addressLine2</th>
      <th>customerName</th>
      <th>contactLastName</th>
      <th>contactFirstName</th>
      <th>salesRepEmployeeNumber</th>
      <th>customerNumber</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>10100</td>
      <td>2003-01-06</td>
      <td>2003-01-13</td>
      <td>2003-01-10</td>
      <td>Shipped</td>
      <td>None</td>
      <td>{'priceEach': 136.0, 'productCode': 'S18_1749'...</td>
      <td>Nashua</td>
      <td>6035558647</td>
      <td>NH</td>
      <td>USA</td>
      <td>62005</td>
      <td>114200.0</td>
      <td>2304 Long Airport Avenue</td>
      <td>None</td>
      <td>Online Diecast Creations Co.</td>
      <td>Young</td>
      <td>Dorothy</td>
      <td>1216.0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>10100</td>
      <td>2003-01-06</td>
      <td>2003-01-13</td>
      <td>2003-01-10</td>
      <td>Shipped</td>
      <td>None</td>
      <td>{'priceEach': 55.09, 'productCode': 'S18_2248'...</td>
      <td>Nashua</td>
      <td>6035558647</td>
      <td>NH</td>
      <td>USA</td>
      <td>62005</td>
      <td>114200.0</td>
      <td>2304 Long Airport Avenue</td>
      <td>None</td>
      <td>Online Diecast Creations Co.</td>
      <td>Young</td>
      <td>Dorothy</td>
      <td>1216.0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2</th>
      <td>10100</td>
      <td>2003-01-06</td>
      <td>2003-01-13</td>
      <td>2003-01-10</td>
      <td>Shipped</td>
      <td>None</td>
      <td>{'priceEach': 75.46, 'productCode': 'S18_4409'...</td>
      <td>Nashua</td>
      <td>6035558647</td>
      <td>NH</td>
      <td>USA</td>
      <td>62005</td>
      <td>114200.0</td>
      <td>2304 Long Airport Avenue</td>
      <td>None</td>
      <td>Online Diecast Creations Co.</td>
      <td>Young</td>
      <td>Dorothy</td>
      <td>1216.0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>3</th>
      <td>10100</td>
      <td>2003-01-06</td>
      <td>2003-01-13</td>
      <td>2003-01-10</td>
      <td>Shipped</td>
      <td>None</td>
      <td>{'priceEach': 35.29, 'productCode': 'S24_3969'...</td>
      <td>Nashua</td>
      <td>6035558647</td>
      <td>NH</td>
      <td>USA</td>
      <td>62005</td>
      <td>114200.0</td>
      <td>2304 Long Airport Avenue</td>
      <td>None</td>
      <td>Online Diecast Creations Co.</td>
      <td>Young</td>
      <td>Dorothy</td>
      <td>1216.0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>4</th>
      <td>10101</td>
      <td>2003-01-09</td>
      <td>2003-01-18</td>
      <td>2003-01-11</td>
      <td>Shipped</td>
      <td>Check on availability.</td>
      <td>{'priceEach': 108.06, 'productCode': 'S18_2325...</td>
      <td>Frankfurt</td>
      <td>+49 69 66 90 2555</td>
      <td>None</td>
      <td>Germany</td>
      <td>60528</td>
      <td>59700.0</td>
      <td>Lyonerstr. 34</td>
      <td>None</td>
      <td>Blauer See Auto, Co.</td>
      <td>Keitel</td>
      <td>Roland</td>
      <td>1504.0</td>
      <td>2</td>
    </tr>
  </tbody>
</table>
</div>



##### __Expected Output__

| **ordernumber** | **orderdate** | **requireddate** | **shippeddate** | **status** | **comments**            | **orderdetails** | **city**    | **phone**         | **state** | **country** | **postalCode** | **creditLimit** | **addressLine1**           | **addressLine2** | **customerName**              | **contactLastName** | **contactFirstName** | **salesRepEmployeeNumber** | **customerNumber** |
| --------------- | ------------- | ---------------- | --------------- | ---------- | ---------------------- | ---------------- | ----------- | ----------------- | --------- | ----------- | -------------- | --------------- | -------------------------- | ---------------- | ----------------------------- | ------------------- | ------------------- | ------------------------ | ------------------ |
| 10100           | 2003-01-06    | 2003-01-13       | 2003-01-10      | Shipped    | None                   | text...          | Nashua      | 6035558647        | NH        | USA         | 62005          | 114200.0        | 2304 Long Airport Avenue   | None             | Online Diecast Creations Co.  | Young               | Dorothy              | 1216.0                   | 1                  |
| 10100           | 2003-01-06    | 2003-01-13       | 2003-01-10      | Shipped    | None                   | text...          | Nashua      | 6035558647        | NH        | USA         | 62005          | 114200.0        | 2304 Long Airport Avenue   | None             | Online Diecast Creations Co.  | Young               | Dorothy              | 1216.0                   | 1                  |
| 10100           | 2003-01-06    | 2003-01-13       | 2003-01-10      | Shipped    | None                   | text...          | Nashua      | 6035558647        | NH        | USA         | 62005          | 114200.0        | 2304 Long Airport Avenue   | None             | Online Diecast Creations Co.  | Young               | Dorothy              | 1216.0                   | 1                  |
| 10100           | 2003-01-06    | 2003-01-13       | 2003-01-10      | Shipped    | None                   | text...          | Nashua      | 6035558647        | NH        | USA         | 62005          | 114200.0        | 2304 Long Airport Avenue   | None             | Online Diecast Creations Co.  | Young               | Dorothy              | 1216.0                   | 1                  |
| 10101           | 2003-01-09    | 2003-01-18       | 2003-01-11      | Shipped    | Check on availability. | text...          | Frankfurt   | +49 69 66 90 2555 | None      | Germany     | 60528          | 59700.0         | Lyonerstr. 34              | None             | Blauer See Auto, Co.          | Keitel              | Roland               | 1504.0                   | 2                  |


The `explode` function is used to transform each element of a list-like column into a separate row. Setting `ignore_index=True` resets the index of the resulting dataframe, creating a new integer index that starts from 0. 

2.6. Use again the `json_normalize` over the `orderdetails` column of the dataframe `df_exploded`.


```python
### START CODE HERE ### (1 line of code)
orderdetails_normalized = pd.json_normalize(df_exploded['orderdetails']) # @REPLACE EQUALS pd.None(None['None'])
### END CODE HERE ###

orderdetails_normalized.head()
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
      <th>priceEach</th>
      <th>productCode</th>
      <th>quantityOrdered</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>136.00</td>
      <td>S18_1749</td>
      <td>30</td>
    </tr>
    <tr>
      <th>1</th>
      <td>55.09</td>
      <td>S18_2248</td>
      <td>50</td>
    </tr>
    <tr>
      <th>2</th>
      <td>75.46</td>
      <td>S18_4409</td>
      <td>22</td>
    </tr>
    <tr>
      <th>3</th>
      <td>35.29</td>
      <td>S24_3969</td>
      <td>49</td>
    </tr>
    <tr>
      <th>4</th>
      <td>108.06</td>
      <td>S18_2325</td>
      <td>25</td>
    </tr>
  </tbody>
</table>
</div>



##### __Expected Output__

| **priceEach** | **productCode** | **quantityOrdered** |
| ------------- | --------------- | ------------------- |
| 136.00        | S18_1749        | 30                  |
| 55.09         | S18_2248        | 50                  |
| 75.46         | S18_4409        | 22                  |
| 35.29         | S24_3969        | 49                  |
| 108.06        | S18_2325        | 25                 |


2.7. Finally, `drop()` the `orderdetails` column from the original `df_exploded` dataframe keeping `inplace` argument equal to `True`.  Then `concat()` `df_exploded` dataframe with the `orderdetails_normalized` dataframe.


```python
### START CODE HERE ### (2 lines of code)
df_exploded.drop(columns='orderdetails', inplace=True) # @REPLACE df_exploded.None(columns='None', inplace=True)
df_normalized = pd.concat([df_exploded, orderdetails_normalized], axis=1) # @REPLACE EQUALS pd.None([df_exploded, None], axis=1)
### END CODE HERE ###

# First Normal Form
df_normalized.head()
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
      <th>ordernumber</th>
      <th>orderdate</th>
      <th>requireddate</th>
      <th>shippeddate</th>
      <th>status</th>
      <th>comments</th>
      <th>city</th>
      <th>phone</th>
      <th>state</th>
      <th>country</th>
      <th>postalCode</th>
      <th>creditLimit</th>
      <th>addressLine1</th>
      <th>addressLine2</th>
      <th>customerName</th>
      <th>contactLastName</th>
      <th>contactFirstName</th>
      <th>salesRepEmployeeNumber</th>
      <th>customerNumber</th>
      <th>priceEach</th>
      <th>productCode</th>
      <th>quantityOrdered</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>10100</td>
      <td>2003-01-06</td>
      <td>2003-01-13</td>
      <td>2003-01-10</td>
      <td>Shipped</td>
      <td>None</td>
      <td>Nashua</td>
      <td>6035558647</td>
      <td>NH</td>
      <td>USA</td>
      <td>62005</td>
      <td>114200.0</td>
      <td>2304 Long Airport Avenue</td>
      <td>None</td>
      <td>Online Diecast Creations Co.</td>
      <td>Young</td>
      <td>Dorothy</td>
      <td>1216.0</td>
      <td>1</td>
      <td>136.00</td>
      <td>S18_1749</td>
      <td>30</td>
    </tr>
    <tr>
      <th>1</th>
      <td>10100</td>
      <td>2003-01-06</td>
      <td>2003-01-13</td>
      <td>2003-01-10</td>
      <td>Shipped</td>
      <td>None</td>
      <td>Nashua</td>
      <td>6035558647</td>
      <td>NH</td>
      <td>USA</td>
      <td>62005</td>
      <td>114200.0</td>
      <td>2304 Long Airport Avenue</td>
      <td>None</td>
      <td>Online Diecast Creations Co.</td>
      <td>Young</td>
      <td>Dorothy</td>
      <td>1216.0</td>
      <td>1</td>
      <td>55.09</td>
      <td>S18_2248</td>
      <td>50</td>
    </tr>
    <tr>
      <th>2</th>
      <td>10100</td>
      <td>2003-01-06</td>
      <td>2003-01-13</td>
      <td>2003-01-10</td>
      <td>Shipped</td>
      <td>None</td>
      <td>Nashua</td>
      <td>6035558647</td>
      <td>NH</td>
      <td>USA</td>
      <td>62005</td>
      <td>114200.0</td>
      <td>2304 Long Airport Avenue</td>
      <td>None</td>
      <td>Online Diecast Creations Co.</td>
      <td>Young</td>
      <td>Dorothy</td>
      <td>1216.0</td>
      <td>1</td>
      <td>75.46</td>
      <td>S18_4409</td>
      <td>22</td>
    </tr>
    <tr>
      <th>3</th>
      <td>10100</td>
      <td>2003-01-06</td>
      <td>2003-01-13</td>
      <td>2003-01-10</td>
      <td>Shipped</td>
      <td>None</td>
      <td>Nashua</td>
      <td>6035558647</td>
      <td>NH</td>
      <td>USA</td>
      <td>62005</td>
      <td>114200.0</td>
      <td>2304 Long Airport Avenue</td>
      <td>None</td>
      <td>Online Diecast Creations Co.</td>
      <td>Young</td>
      <td>Dorothy</td>
      <td>1216.0</td>
      <td>1</td>
      <td>35.29</td>
      <td>S24_3969</td>
      <td>49</td>
    </tr>
    <tr>
      <th>4</th>
      <td>10101</td>
      <td>2003-01-09</td>
      <td>2003-01-18</td>
      <td>2003-01-11</td>
      <td>Shipped</td>
      <td>Check on availability.</td>
      <td>Frankfurt</td>
      <td>+49 69 66 90 2555</td>
      <td>None</td>
      <td>Germany</td>
      <td>60528</td>
      <td>59700.0</td>
      <td>Lyonerstr. 34</td>
      <td>None</td>
      <td>Blauer See Auto, Co.</td>
      <td>Keitel</td>
      <td>Roland</td>
      <td>1504.0</td>
      <td>2</td>
      <td>108.06</td>
      <td>S18_2325</td>
      <td>25</td>
    </tr>
  </tbody>
</table>
</div>



##### __Expected Output__

| **ordernumber** | **orderdate** | **requireddate** | **shippeddate** | **status** | **comments**            | **city**    | **phone**         | **state** | **country** | **postalCode** | **creditLimit** | **addressLine1**           | **addressLine2** | **customerName**              | **contactLastName** | **contactFirstName** | **salesRepEmployeeNumber** | **customerNumber** | **priceEach** | **productCode** | **quantityOrdered** |
| --------------- | ------------- | ---------------- | --------------- | ---------- | ---------------------- | ----------- | ----------------- | --------- | ----------- | -------------- | --------------- | -------------------------- | ---------------- | ----------------------------- | ------------------- | ------------------- | ------------------------ | ------------------ | ------------ | --------------- | ------------------- |
| 10100           | 2003-01-06    | 2003-01-13       | 2003-01-10      | Shipped    | None                   | Nashua      | 6035558647        | NH        | USA         | 62005          | 114200.0        | 2304 Long Airport Avenue   | None             | Online Diecast Creations Co.  | Young               | Dorothy              | 1216.0                   | 1                  | 136.00        | S18_1749        | 30                  |
| 10100           | 2003-01-06    | 2003-01-13       | 2003-01-10      | Shipped    | None                   | Nashua      | 6035558647        | NH        | USA         | 62005          | 114200.0        | 2304 Long Airport Avenue   | None             | Online Diecast Creations Co.  | Young               | Dorothy              | 1216.0                   | 1                  | 55.09         | S18_2248        | 50                  |
| 10100           | 2003-01-06    | 2003-01-13       | 2003-01-10      | Shipped    | None                   | Nashua      | 6035558647        | NH        | USA         | 62005          | 114200.0        | 2304 Long Airport Avenue   | None             | Online Diecast Creations Co.  | Young               | Dorothy              | 1216.0                   | 1                  | 75.46         | S18_4409        | 22                  |
| 10100           | 2003-01-06    | 2003-01-13       | 2003-01-10      | Shipped    | None                   | Nashua      | 6035558647        | NH        | USA         | 62005          | 114200.0        | 2304 Long Airport Avenue   | None             | Online Diecast Creations Co.  | Young               | Dorothy              | 1216.0                   | 1                  | 35.29         | S24_3969        | 49                  |
| 10101           | 2003-01-09    | 2003-01-18       | 2003-01-11      | Shipped    | Check on availability. | Frankfurt   | +49 69 66 90 2555 | None      | Germany     | 60528          | 59700.0         | Lyonerstr. 34              | None             | Blauer See Auto, Co.          | Keitel              | Roland               | 1504.0                   | 2                  | 108.06        | S18_2325        | 25                  |


The resulting dataframe `df_normalized` should be in the Frist Normal Form now.

2.8. Now that you have atomic values in your dataset, let's create an additional identifier for each product in each order. You will call it Order Line Number (`orderlinenumber`) and in combination with the `ordernumber` column, they will create a composite primary key.


```python
df_normalized['orderlinenumber'] = df_normalized.groupby('ordernumber').cumcount() + 1
df_normalized.head()
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
      <th>ordernumber</th>
      <th>orderdate</th>
      <th>requireddate</th>
      <th>shippeddate</th>
      <th>status</th>
      <th>comments</th>
      <th>city</th>
      <th>phone</th>
      <th>state</th>
      <th>country</th>
      <th>postalCode</th>
      <th>creditLimit</th>
      <th>addressLine1</th>
      <th>addressLine2</th>
      <th>customerName</th>
      <th>contactLastName</th>
      <th>contactFirstName</th>
      <th>salesRepEmployeeNumber</th>
      <th>customerNumber</th>
      <th>priceEach</th>
      <th>productCode</th>
      <th>quantityOrdered</th>
      <th>orderlinenumber</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>10100</td>
      <td>2003-01-06</td>
      <td>2003-01-13</td>
      <td>2003-01-10</td>
      <td>Shipped</td>
      <td>None</td>
      <td>Nashua</td>
      <td>6035558647</td>
      <td>NH</td>
      <td>USA</td>
      <td>62005</td>
      <td>114200.0</td>
      <td>2304 Long Airport Avenue</td>
      <td>None</td>
      <td>Online Diecast Creations Co.</td>
      <td>Young</td>
      <td>Dorothy</td>
      <td>1216.0</td>
      <td>1</td>
      <td>136.00</td>
      <td>S18_1749</td>
      <td>30</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>10100</td>
      <td>2003-01-06</td>
      <td>2003-01-13</td>
      <td>2003-01-10</td>
      <td>Shipped</td>
      <td>None</td>
      <td>Nashua</td>
      <td>6035558647</td>
      <td>NH</td>
      <td>USA</td>
      <td>62005</td>
      <td>114200.0</td>
      <td>2304 Long Airport Avenue</td>
      <td>None</td>
      <td>Online Diecast Creations Co.</td>
      <td>Young</td>
      <td>Dorothy</td>
      <td>1216.0</td>
      <td>1</td>
      <td>55.09</td>
      <td>S18_2248</td>
      <td>50</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>10100</td>
      <td>2003-01-06</td>
      <td>2003-01-13</td>
      <td>2003-01-10</td>
      <td>Shipped</td>
      <td>None</td>
      <td>Nashua</td>
      <td>6035558647</td>
      <td>NH</td>
      <td>USA</td>
      <td>62005</td>
      <td>114200.0</td>
      <td>2304 Long Airport Avenue</td>
      <td>None</td>
      <td>Online Diecast Creations Co.</td>
      <td>Young</td>
      <td>Dorothy</td>
      <td>1216.0</td>
      <td>1</td>
      <td>75.46</td>
      <td>S18_4409</td>
      <td>22</td>
      <td>3</td>
    </tr>
    <tr>
      <th>3</th>
      <td>10100</td>
      <td>2003-01-06</td>
      <td>2003-01-13</td>
      <td>2003-01-10</td>
      <td>Shipped</td>
      <td>None</td>
      <td>Nashua</td>
      <td>6035558647</td>
      <td>NH</td>
      <td>USA</td>
      <td>62005</td>
      <td>114200.0</td>
      <td>2304 Long Airport Avenue</td>
      <td>None</td>
      <td>Online Diecast Creations Co.</td>
      <td>Young</td>
      <td>Dorothy</td>
      <td>1216.0</td>
      <td>1</td>
      <td>35.29</td>
      <td>S24_3969</td>
      <td>49</td>
      <td>4</td>
    </tr>
    <tr>
      <th>4</th>
      <td>10101</td>
      <td>2003-01-09</td>
      <td>2003-01-18</td>
      <td>2003-01-11</td>
      <td>Shipped</td>
      <td>Check on availability.</td>
      <td>Frankfurt</td>
      <td>+49 69 66 90 2555</td>
      <td>None</td>
      <td>Germany</td>
      <td>60528</td>
      <td>59700.0</td>
      <td>Lyonerstr. 34</td>
      <td>None</td>
      <td>Blauer See Auto, Co.</td>
      <td>Keitel</td>
      <td>Roland</td>
      <td>1504.0</td>
      <td>2</td>
      <td>108.06</td>
      <td>S18_2325</td>
      <td>25</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>



2.9. With those transformations, you have finished your normalization up to 1NF. Let's insert this dataset into your database. Drop the table if it has been loaded before to avoid an error.


```sql
%%sql
DROP TABLE IF EXISTS classicmodels_1nf.orders
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1lab1-rds.c9g6s0k8ogtn.us-east-1.rds.amazonaws.com:5432/postgres
    Done.





    []



Create table named `orders` in the schema `classicmodels_1nf`.


```python
engine = create_engine(connection_url)

df_normalized.to_sql('orders', engine, schema='classicmodels_1nf', index=False)
```




    996



Inspect the data that you just loaded.


```sql
%%sql 
SELECT COUNT(*) FROM classicmodels_1nf.orders;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1lab1-rds.c9g6s0k8ogtn.us-east-1.rds.amazonaws.com:5432/postgres
    1 rows affected.





<table>
    <thead>
        <tr>
            <th>count</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>2996</td>
        </tr>
    </tbody>
</table>




```sql
%%sql 
SELECT * FROM classicmodels_1nf.orders LIMIT 10;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1lab1-rds.c9g6s0k8ogtn.us-east-1.rds.amazonaws.com:5432/postgres
    10 rows affected.





<table>
    <thead>
        <tr>
            <th>ordernumber</th>
            <th>orderdate</th>
            <th>requireddate</th>
            <th>shippeddate</th>
            <th>status</th>
            <th>comments</th>
            <th>city</th>
            <th>phone</th>
            <th>state</th>
            <th>country</th>
            <th>postalCode</th>
            <th>creditLimit</th>
            <th>addressLine1</th>
            <th>addressLine2</th>
            <th>customerName</th>
            <th>contactLastName</th>
            <th>contactFirstName</th>
            <th>salesRepEmployeeNumber</th>
            <th>customerNumber</th>
            <th>priceEach</th>
            <th>productCode</th>
            <th>quantityOrdered</th>
            <th>orderlinenumber</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>10100</td>
            <td>2003-01-06</td>
            <td>2003-01-13</td>
            <td>2003-01-10</td>
            <td>Shipped</td>
            <td>None</td>
            <td>Nashua</td>
            <td>6035558647</td>
            <td>NH</td>
            <td>USA</td>
            <td>62005</td>
            <td>114200.0</td>
            <td>2304 Long Airport Avenue</td>
            <td>None</td>
            <td>Online Diecast Creations Co.</td>
            <td>Young</td>
            <td>Dorothy</td>
            <td>1216.0</td>
            <td>1</td>
            <td>136.0</td>
            <td>S18_1749</td>
            <td>30</td>
            <td>1</td>
        </tr>
        <tr>
            <td>10100</td>
            <td>2003-01-06</td>
            <td>2003-01-13</td>
            <td>2003-01-10</td>
            <td>Shipped</td>
            <td>None</td>
            <td>Nashua</td>
            <td>6035558647</td>
            <td>NH</td>
            <td>USA</td>
            <td>62005</td>
            <td>114200.0</td>
            <td>2304 Long Airport Avenue</td>
            <td>None</td>
            <td>Online Diecast Creations Co.</td>
            <td>Young</td>
            <td>Dorothy</td>
            <td>1216.0</td>
            <td>1</td>
            <td>55.09</td>
            <td>S18_2248</td>
            <td>50</td>
            <td>2</td>
        </tr>
        <tr>
            <td>10100</td>
            <td>2003-01-06</td>
            <td>2003-01-13</td>
            <td>2003-01-10</td>
            <td>Shipped</td>
            <td>None</td>
            <td>Nashua</td>
            <td>6035558647</td>
            <td>NH</td>
            <td>USA</td>
            <td>62005</td>
            <td>114200.0</td>
            <td>2304 Long Airport Avenue</td>
            <td>None</td>
            <td>Online Diecast Creations Co.</td>
            <td>Young</td>
            <td>Dorothy</td>
            <td>1216.0</td>
            <td>1</td>
            <td>75.46</td>
            <td>S18_4409</td>
            <td>22</td>
            <td>3</td>
        </tr>
        <tr>
            <td>10100</td>
            <td>2003-01-06</td>
            <td>2003-01-13</td>
            <td>2003-01-10</td>
            <td>Shipped</td>
            <td>None</td>
            <td>Nashua</td>
            <td>6035558647</td>
            <td>NH</td>
            <td>USA</td>
            <td>62005</td>
            <td>114200.0</td>
            <td>2304 Long Airport Avenue</td>
            <td>None</td>
            <td>Online Diecast Creations Co.</td>
            <td>Young</td>
            <td>Dorothy</td>
            <td>1216.0</td>
            <td>1</td>
            <td>35.29</td>
            <td>S24_3969</td>
            <td>49</td>
            <td>4</td>
        </tr>
        <tr>
            <td>10101</td>
            <td>2003-01-09</td>
            <td>2003-01-18</td>
            <td>2003-01-11</td>
            <td>Shipped</td>
            <td>Check on availability.</td>
            <td>Frankfurt</td>
            <td>+49 69 66 90 2555</td>
            <td>None</td>
            <td>Germany</td>
            <td>60528</td>
            <td>59700.0</td>
            <td>Lyonerstr. 34</td>
            <td>None</td>
            <td>Blauer See Auto, Co.</td>
            <td>Keitel</td>
            <td>Roland</td>
            <td>1504.0</td>
            <td>2</td>
            <td>108.06</td>
            <td>S18_2325</td>
            <td>25</td>
            <td>1</td>
        </tr>
        <tr>
            <td>10101</td>
            <td>2003-01-09</td>
            <td>2003-01-18</td>
            <td>2003-01-11</td>
            <td>Shipped</td>
            <td>Check on availability.</td>
            <td>Frankfurt</td>
            <td>+49 69 66 90 2555</td>
            <td>None</td>
            <td>Germany</td>
            <td>60528</td>
            <td>59700.0</td>
            <td>Lyonerstr. 34</td>
            <td>None</td>
            <td>Blauer See Auto, Co.</td>
            <td>Keitel</td>
            <td>Roland</td>
            <td>1504.0</td>
            <td>2</td>
            <td>167.06</td>
            <td>S18_2795</td>
            <td>26</td>
            <td>2</td>
        </tr>
        <tr>
            <td>10101</td>
            <td>2003-01-09</td>
            <td>2003-01-18</td>
            <td>2003-01-11</td>
            <td>Shipped</td>
            <td>Check on availability.</td>
            <td>Frankfurt</td>
            <td>+49 69 66 90 2555</td>
            <td>None</td>
            <td>Germany</td>
            <td>60528</td>
            <td>59700.0</td>
            <td>Lyonerstr. 34</td>
            <td>None</td>
            <td>Blauer See Auto, Co.</td>
            <td>Keitel</td>
            <td>Roland</td>
            <td>1504.0</td>
            <td>2</td>
            <td>32.53</td>
            <td>S24_1937</td>
            <td>45</td>
            <td>3</td>
        </tr>
        <tr>
            <td>10101</td>
            <td>2003-01-09</td>
            <td>2003-01-18</td>
            <td>2003-01-11</td>
            <td>Shipped</td>
            <td>Check on availability.</td>
            <td>Frankfurt</td>
            <td>+49 69 66 90 2555</td>
            <td>None</td>
            <td>Germany</td>
            <td>60528</td>
            <td>59700.0</td>
            <td>Lyonerstr. 34</td>
            <td>None</td>
            <td>Blauer See Auto, Co.</td>
            <td>Keitel</td>
            <td>Roland</td>
            <td>1504.0</td>
            <td>2</td>
            <td>44.35</td>
            <td>S24_2022</td>
            <td>46</td>
            <td>4</td>
        </tr>
        <tr>
            <td>10102</td>
            <td>2003-01-10</td>
            <td>2003-01-18</td>
            <td>2003-01-14</td>
            <td>Shipped</td>
            <td>None</td>
            <td>NYC</td>
            <td>2125551500</td>
            <td>NY</td>
            <td>USA</td>
            <td>10022</td>
            <td>76400.0</td>
            <td>2678 Kingston Rd.</td>
            <td>Suite 101</td>
            <td>Vitachrome Inc.</td>
            <td>Frick</td>
            <td>Michael</td>
            <td>1286.0</td>
            <td>3</td>
            <td>95.55</td>
            <td>S18_1342</td>
            <td>39</td>
            <td>1</td>
        </tr>
        <tr>
            <td>10102</td>
            <td>2003-01-10</td>
            <td>2003-01-18</td>
            <td>2003-01-14</td>
            <td>Shipped</td>
            <td>None</td>
            <td>NYC</td>
            <td>2125551500</td>
            <td>NY</td>
            <td>USA</td>
            <td>10022</td>
            <td>76400.0</td>
            <td>2678 Kingston Rd.</td>
            <td>Suite 101</td>
            <td>Vitachrome Inc.</td>
            <td>Frick</td>
            <td>Michael</td>
            <td>1286.0</td>
            <td>3</td>
            <td>43.13</td>
            <td>S18_1367</td>
            <td>41</td>
            <td>2</td>
        </tr>
    </tbody>
</table>



<a name='3'></a>
## 3 - Second Normal Form (2NF)

In the second normal form (2NF), data must already be in the first normal form (1NF), and all non-key attributes must be fully functionally dependent on the primary key.
 
Here, by using the `ordernumber` and `orderlinenumber` columns as a composite primary key, you will create a unique identifier for each order line. 
Additionally, you have a separate identifier for customers along with their complete information. Since it's unnecessary to include all customer details in the same row as the order, you only need the customer identifier in the order table. The complete customer information can be moved to a separate table that is fully functional and dependent only on the customer identifier. 

The final schema after the 2NF transformations will look like this:

![ERD_2NF](./images/ERD_2NF.png)

3.1. Create the `classicmodels_2nf` schema to store our tables and then read the 1NF dataset and transform it to create a 2NF version.


```sql
%%sql
CREATE SCHEMA IF NOT EXISTS classicmodels_2nf;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1lab1-rds.c9g6s0k8ogtn.us-east-1.rds.amazonaws.com:5432/postgres
    Done.





    []



Have a look again at the data in the 1NF:


```python
result = %sql select * from classicmodels_1nf.orders
df_orders = result.DataFrame()

df_orders.head()
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1lab1-rds.c9g6s0k8ogtn.us-east-1.rds.amazonaws.com:5432/postgres
    2996 rows affected.





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
      <th>ordernumber</th>
      <th>orderdate</th>
      <th>requireddate</th>
      <th>shippeddate</th>
      <th>status</th>
      <th>comments</th>
      <th>city</th>
      <th>phone</th>
      <th>state</th>
      <th>country</th>
      <th>postalCode</th>
      <th>creditLimit</th>
      <th>addressLine1</th>
      <th>addressLine2</th>
      <th>customerName</th>
      <th>contactLastName</th>
      <th>contactFirstName</th>
      <th>salesRepEmployeeNumber</th>
      <th>customerNumber</th>
      <th>priceEach</th>
      <th>productCode</th>
      <th>quantityOrdered</th>
      <th>orderlinenumber</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>10100</td>
      <td>2003-01-06</td>
      <td>2003-01-13</td>
      <td>2003-01-10</td>
      <td>Shipped</td>
      <td>None</td>
      <td>Nashua</td>
      <td>6035558647</td>
      <td>NH</td>
      <td>USA</td>
      <td>62005</td>
      <td>114200.0</td>
      <td>2304 Long Airport Avenue</td>
      <td>None</td>
      <td>Online Diecast Creations Co.</td>
      <td>Young</td>
      <td>Dorothy</td>
      <td>1216.0</td>
      <td>1</td>
      <td>136.00</td>
      <td>S18_1749</td>
      <td>30</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>10100</td>
      <td>2003-01-06</td>
      <td>2003-01-13</td>
      <td>2003-01-10</td>
      <td>Shipped</td>
      <td>None</td>
      <td>Nashua</td>
      <td>6035558647</td>
      <td>NH</td>
      <td>USA</td>
      <td>62005</td>
      <td>114200.0</td>
      <td>2304 Long Airport Avenue</td>
      <td>None</td>
      <td>Online Diecast Creations Co.</td>
      <td>Young</td>
      <td>Dorothy</td>
      <td>1216.0</td>
      <td>1</td>
      <td>55.09</td>
      <td>S18_2248</td>
      <td>50</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>10100</td>
      <td>2003-01-06</td>
      <td>2003-01-13</td>
      <td>2003-01-10</td>
      <td>Shipped</td>
      <td>None</td>
      <td>Nashua</td>
      <td>6035558647</td>
      <td>NH</td>
      <td>USA</td>
      <td>62005</td>
      <td>114200.0</td>
      <td>2304 Long Airport Avenue</td>
      <td>None</td>
      <td>Online Diecast Creations Co.</td>
      <td>Young</td>
      <td>Dorothy</td>
      <td>1216.0</td>
      <td>1</td>
      <td>75.46</td>
      <td>S18_4409</td>
      <td>22</td>
      <td>3</td>
    </tr>
    <tr>
      <th>3</th>
      <td>10100</td>
      <td>2003-01-06</td>
      <td>2003-01-13</td>
      <td>2003-01-10</td>
      <td>Shipped</td>
      <td>None</td>
      <td>Nashua</td>
      <td>6035558647</td>
      <td>NH</td>
      <td>USA</td>
      <td>62005</td>
      <td>114200.0</td>
      <td>2304 Long Airport Avenue</td>
      <td>None</td>
      <td>Online Diecast Creations Co.</td>
      <td>Young</td>
      <td>Dorothy</td>
      <td>1216.0</td>
      <td>1</td>
      <td>35.29</td>
      <td>S24_3969</td>
      <td>49</td>
      <td>4</td>
    </tr>
    <tr>
      <th>4</th>
      <td>10101</td>
      <td>2003-01-09</td>
      <td>2003-01-18</td>
      <td>2003-01-11</td>
      <td>Shipped</td>
      <td>Check on availability.</td>
      <td>Frankfurt</td>
      <td>+49 69 66 90 2555</td>
      <td>None</td>
      <td>Germany</td>
      <td>60528</td>
      <td>59700.0</td>
      <td>Lyonerstr. 34</td>
      <td>None</td>
      <td>Blauer See Auto, Co.</td>
      <td>Keitel</td>
      <td>Roland</td>
      <td>1504.0</td>
      <td>2</td>
      <td>108.06</td>
      <td>S18_2325</td>
      <td>25</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>



3.2. Extract all the information related to customers and create a table with the unique values for each customer. 
- Take only customer related columns from your `df_orders` dataframe (see the list in the cell below) and make a copy of it with the `copy()` method naming it `df_customers`.
- Take the dataframe that you just have copied and drop the duplicated rows using the method `drop_duplicates`. Make sure that you put argument `inplace` equal to `True`.


```python
customer_columns = ['customerNumber', 
                    'customerName', 
                    'contactLastName', 
                    'contactFirstName', 
                    'phone', 
                    'addressLine1', 
                    'addressLine2',
                    'postalCode',                     
                    'city', 
                    'state', 
                    'country', 
                    'creditLimit',
                    'salesRepEmployeeNumber',
                   ] 

### START CODE HERE ### (2 lines of code)
df_customers = df_orders[customer_columns].copy() # @REPLACE EQUALS None[None].None()
df_customers.drop_duplicates(inplace=True) # @REPLACE None.None(inplace=None)
### END CODE HERE ###

df_customers.head()
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
      <th>customerName</th>
      <th>contactLastName</th>
      <th>contactFirstName</th>
      <th>phone</th>
      <th>addressLine1</th>
      <th>addressLine2</th>
      <th>postalCode</th>
      <th>city</th>
      <th>state</th>
      <th>country</th>
      <th>creditLimit</th>
      <th>salesRepEmployeeNumber</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>Online Diecast Creations Co.</td>
      <td>Young</td>
      <td>Dorothy</td>
      <td>6035558647</td>
      <td>2304 Long Airport Avenue</td>
      <td>None</td>
      <td>62005</td>
      <td>Nashua</td>
      <td>NH</td>
      <td>USA</td>
      <td>114200.0</td>
      <td>1216.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2</td>
      <td>Blauer See Auto, Co.</td>
      <td>Keitel</td>
      <td>Roland</td>
      <td>+49 69 66 90 2555</td>
      <td>Lyonerstr. 34</td>
      <td>None</td>
      <td>60528</td>
      <td>Frankfurt</td>
      <td>None</td>
      <td>Germany</td>
      <td>59700.0</td>
      <td>1504.0</td>
    </tr>
    <tr>
      <th>8</th>
      <td>3</td>
      <td>Vitachrome Inc.</td>
      <td>Frick</td>
      <td>Michael</td>
      <td>2125551500</td>
      <td>2678 Kingston Rd.</td>
      <td>Suite 101</td>
      <td>10022</td>
      <td>NYC</td>
      <td>NY</td>
      <td>USA</td>
      <td>76400.0</td>
      <td>1286.0</td>
    </tr>
    <tr>
      <th>10</th>
      <td>4</td>
      <td>Baane Mini Imports</td>
      <td>Bergulfsen</td>
      <td>Jonas</td>
      <td>07-98 9555</td>
      <td>Erling Skakkes gate 78</td>
      <td>None</td>
      <td>4110</td>
      <td>Stavern</td>
      <td>None</td>
      <td>Norway</td>
      <td>81700.0</td>
      <td>1504.0</td>
    </tr>
    <tr>
      <th>26</th>
      <td>5</td>
      <td>Euro+ Shopping Channel</td>
      <td>Freyre</td>
      <td>Diego</td>
      <td>(91) 555 94 44</td>
      <td>C/ Moralzarzal, 86</td>
      <td>None</td>
      <td>28034</td>
      <td>Madrid</td>
      <td>None</td>
      <td>Spain</td>
      <td>227600.0</td>
      <td>1370.0</td>
    </tr>
  </tbody>
</table>
</div>



##### __Expected Output__

| **customerNumber** | **customerName**                | **contactLastName** | **contactFirstName** | **phone**         | **addressLine1**           | **addressLine2** | **postalCode** | **city**  | **state** | **country** | **creditLimit** | **salesRepEmployeeNumber** |
| ------------------ | -------------------------------- | ------------------- | ------------------- | ----------------- | -------------------------- | ---------------- | -------------- | -------- | --------- | ----------- | --------------- | ------------------------- |
| 1                  | Online Diecast Creations Co.   | Young               | Dorothy             | 6035558647        | 2304 Long Airport Avenue   | None             | 62005          | Nashua   | NH        | USA         | 114200.0        | 1216.0                    |
| 2                  | Blauer See Auto, Co.            | Keitel              | Roland              | +49 69 66 90 2555 | Lyonerstr. 34              | None             | 60528          | Frankfurt | None      | Germany     | 59700.0         | 1504.0                    |
| 3                  | Vitachrome Inc.                 | Frick                | Michael             | 2125551500        | 2678 Kingston Rd.         | Suite 101        | 10022          | NYC      | NY        | USA         | 76400.0         | 1286.0                    |
| 4                  | Baane Mini Imports              | Bergulfsen           | Jonas               | 07-98 9555        | Erling Skakkes gate 78    | None             | 4110           | Stavern  | None      | Norway      | 81700.0         | 1504.0                    |
| 5                  | Euro+ Shopping Channel         | Freyre              | Diego               | (91) 555 94 44   | C/ Moralzarzal, 86        | None             | 28034          | Madrid  | None      | Spain       | 227600.0        | 1370.0                    |


3.3. Now that you have your customers' dataset, that information can be dropped from the original dataframe. The only necessary column to keep is the `customerNumber` as it helps to relate the orders with customers' information. Create a list of the columns which you need to drop from the `df_orders` dataframe:


```python
customer_columns.pop(0)
customer_columns
```




    ['customerName',
     'contactLastName',
     'contactFirstName',
     'phone',
     'addressLine1',
     'addressLine2',
     'postalCode',
     'city',
     'state',
     'country',
     'creditLimit',
     'salesRepEmployeeNumber']



3.4. Drop the `customer_columns` from the dataframe `df_orders`. The `inplace` argument should be equal to `True`.


```python
### START CODE HERE ### (1 line of code)
df_orders.drop(columns=customer_columns, inplace=True) # @REPLACE None.None(columns=None, inplace=None)
### END CODE HERE ###

df_orders.head()
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
      <th>ordernumber</th>
      <th>orderdate</th>
      <th>requireddate</th>
      <th>shippeddate</th>
      <th>status</th>
      <th>comments</th>
      <th>customerNumber</th>
      <th>priceEach</th>
      <th>productCode</th>
      <th>quantityOrdered</th>
      <th>orderlinenumber</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>10100</td>
      <td>2003-01-06</td>
      <td>2003-01-13</td>
      <td>2003-01-10</td>
      <td>Shipped</td>
      <td>None</td>
      <td>1</td>
      <td>136.00</td>
      <td>S18_1749</td>
      <td>30</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>10100</td>
      <td>2003-01-06</td>
      <td>2003-01-13</td>
      <td>2003-01-10</td>
      <td>Shipped</td>
      <td>None</td>
      <td>1</td>
      <td>55.09</td>
      <td>S18_2248</td>
      <td>50</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>10100</td>
      <td>2003-01-06</td>
      <td>2003-01-13</td>
      <td>2003-01-10</td>
      <td>Shipped</td>
      <td>None</td>
      <td>1</td>
      <td>75.46</td>
      <td>S18_4409</td>
      <td>22</td>
      <td>3</td>
    </tr>
    <tr>
      <th>3</th>
      <td>10100</td>
      <td>2003-01-06</td>
      <td>2003-01-13</td>
      <td>2003-01-10</td>
      <td>Shipped</td>
      <td>None</td>
      <td>1</td>
      <td>35.29</td>
      <td>S24_3969</td>
      <td>49</td>
      <td>4</td>
    </tr>
    <tr>
      <th>4</th>
      <td>10101</td>
      <td>2003-01-09</td>
      <td>2003-01-18</td>
      <td>2003-01-11</td>
      <td>Shipped</td>
      <td>Check on availability.</td>
      <td>2</td>
      <td>108.06</td>
      <td>S18_2325</td>
      <td>25</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>



##### __Expected Output__

| **ordernumber** | **orderdate** | **requireddate** | **shippeddate** | **status** | **comments**             | **customerNumber** | **priceEach** | **productCode** | **quantityOrdered** | **orderlinenumber** |
| ---------------- | ------------- | ---------------- | --------------- | ---------- | ------------------------ | ------------------- | ------------ | --------------- | ------------------- | ------------------- |
| 10100            | 2003-01-06    | 2003-01-13       | 2003-01-10      | Shipped    | None                     | 1                   | 136.00       | S18_1749        | 30                  | 1                   |
| 10100            | 2003-01-06    | 2003-01-13       | 2003-01-10      | Shipped    | None                     | 1                   | 55.09        | S18_2248        | 50                  | 2                   |
| 10100            | 2003-01-06    | 2003-01-13       | 2003-01-10      | Shipped    | None                     | 1                   | 75.46        | S18_4409        | 22                  | 3                   |
| 10100            | 2003-01-06    | 2003-01-13       | 2003-01-10      | Shipped    | None                     | 1                   | 35.29        | S24_3969        | 49                  | 4                   |
| 10101            | 2003-01-09    | 2003-01-18       | 2003-01-11      | Shipped    | Check on availability.  | 2                   | 108.06       | S18_2325        | 25                  | 1                   |


You have created 2NF version of the relations. The result of this normalization step is two datasets or entities:
- `orders`: Containing only the information about each order.
- `customers`: Containing only the complete information about the customers.

3.5. The two previous entities can be related through the `customerNumber` field. Insert the two previous tables into the `classicmodels_2nf` schema. You will need to drop the tables before that in case they have been added before.


```sql
%%sql
DROP TABLE IF EXISTS classicmodels_2nf.orders
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1lab1-rds.c9g6s0k8ogtn.us-east-1.rds.amazonaws.com:5432/postgres
    Done.





    []




```sql
%%sql
DROP TABLE IF EXISTS classicmodels_2nf.customers
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1lab1-rds.c9g6s0k8ogtn.us-east-1.rds.amazonaws.com:5432/postgres
    Done.





    []




```python
df_orders.to_sql('orders', engine, schema='classicmodels_2nf', index=False)
```




    996




```python
df_customers.to_sql('customers', engine, schema='classicmodels_2nf', index=False)
```




    98



Explore the tables.


```sql
%%sql
SELECT COUNT(*) FROM classicmodels_2nf.orders;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1lab1-rds.c9g6s0k8ogtn.us-east-1.rds.amazonaws.com:5432/postgres
    1 rows affected.





<table>
    <thead>
        <tr>
            <th>count</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>2996</td>
        </tr>
    </tbody>
</table>




```sql
%%sql
SELECT COUNT(*) FROM classicmodels_2nf.customers;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1lab1-rds.c9g6s0k8ogtn.us-east-1.rds.amazonaws.com:5432/postgres
    1 rows affected.





<table>
    <thead>
        <tr>
            <th>count</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>98</td>
        </tr>
    </tbody>
</table>




```sql
%%sql
SELECT * FROM classicmodels_2nf.customers limit 10;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1lab1-rds.c9g6s0k8ogtn.us-east-1.rds.amazonaws.com:5432/postgres
    10 rows affected.





<table>
    <thead>
        <tr>
            <th>customerNumber</th>
            <th>customerName</th>
            <th>contactLastName</th>
            <th>contactFirstName</th>
            <th>phone</th>
            <th>addressLine1</th>
            <th>addressLine2</th>
            <th>postalCode</th>
            <th>city</th>
            <th>state</th>
            <th>country</th>
            <th>creditLimit</th>
            <th>salesRepEmployeeNumber</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>1</td>
            <td>Online Diecast Creations Co.</td>
            <td>Young</td>
            <td>Dorothy</td>
            <td>6035558647</td>
            <td>2304 Long Airport Avenue</td>
            <td>None</td>
            <td>62005</td>
            <td>Nashua</td>
            <td>NH</td>
            <td>USA</td>
            <td>114200.0</td>
            <td>1216.0</td>
        </tr>
        <tr>
            <td>2</td>
            <td>Blauer See Auto, Co.</td>
            <td>Keitel</td>
            <td>Roland</td>
            <td>+49 69 66 90 2555</td>
            <td>Lyonerstr. 34</td>
            <td>None</td>
            <td>60528</td>
            <td>Frankfurt</td>
            <td>None</td>
            <td>Germany</td>
            <td>59700.0</td>
            <td>1504.0</td>
        </tr>
        <tr>
            <td>3</td>
            <td>Vitachrome Inc.</td>
            <td>Frick</td>
            <td>Michael</td>
            <td>2125551500</td>
            <td>2678 Kingston Rd.</td>
            <td>Suite 101</td>
            <td>10022</td>
            <td>NYC</td>
            <td>NY</td>
            <td>USA</td>
            <td>76400.0</td>
            <td>1286.0</td>
        </tr>
        <tr>
            <td>4</td>
            <td>Baane Mini Imports</td>
            <td>Bergulfsen</td>
            <td>Jonas </td>
            <td>07-98 9555</td>
            <td>Erling Skakkes gate 78</td>
            <td>None</td>
            <td>4110</td>
            <td>Stavern</td>
            <td>None</td>
            <td>Norway</td>
            <td>81700.0</td>
            <td>1504.0</td>
        </tr>
        <tr>
            <td>5</td>
            <td>Euro+ Shopping Channel</td>
            <td>Freyre</td>
            <td>Diego </td>
            <td>(91) 555 94 44</td>
            <td>C/ Moralzarzal, 86</td>
            <td>None</td>
            <td>28034</td>
            <td>Madrid</td>
            <td>None</td>
            <td>Spain</td>
            <td>227600.0</td>
            <td>1370.0</td>
        </tr>
        <tr>
            <td>6</td>
            <td>Danish Wholesale Imports</td>
            <td>Petersen</td>
            <td>Jytte </td>
            <td>31 12 3555</td>
            <td>Vinbæltet 34</td>
            <td>None</td>
            <td>1734</td>
            <td>Kobenhavn</td>
            <td>None</td>
            <td>Denmark</td>
            <td>83400.0</td>
            <td>1401.0</td>
        </tr>
        <tr>
            <td>7</td>
            <td>Down Under Souveniers, Inc</td>
            <td>Graham</td>
            <td>Mike</td>
            <td>+64 9 312 5555</td>
            <td>162-164 Grafton Road</td>
            <td>Level 2</td>
            <td>None</td>
            <td>Auckland  </td>
            <td>None</td>
            <td>New Zealand</td>
            <td>88000.0</td>
            <td>1612.0</td>
        </tr>
        <tr>
            <td>8</td>
            <td>Rovelli Gifts</td>
            <td>Rovelli</td>
            <td>Giovanni </td>
            <td>035-640555</td>
            <td>Via Ludovico il Moro 22</td>
            <td>None</td>
            <td>24100</td>
            <td>Bergamo</td>
            <td>None</td>
            <td>Italy</td>
            <td>119600.0</td>
            <td>1401.0</td>
        </tr>
        <tr>
            <td>9</td>
            <td>Land of Toys Inc.</td>
            <td>Lee</td>
            <td>Kwai</td>
            <td>2125557818</td>
            <td>897 Long Airport Avenue</td>
            <td>None</td>
            <td>10022</td>
            <td>NYC</td>
            <td>NY</td>
            <td>USA</td>
            <td>114900.0</td>
            <td>1323.0</td>
        </tr>
        <tr>
            <td>10</td>
            <td>Cruz &amp; Sons Co.</td>
            <td>Cruz</td>
            <td>Arnold</td>
            <td>+63 2 555 3587</td>
            <td>15 McCallum Street</td>
            <td>NatWest Center #13-03</td>
            <td>1227 MM</td>
            <td>Makati City</td>
            <td>None</td>
            <td>Philippines</td>
            <td>81500.0</td>
            <td>1621.0</td>
        </tr>
    </tbody>
</table>




```sql
%%sql
SELECT * FROM classicmodels_2nf.orders limit 10;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1lab1-rds.c9g6s0k8ogtn.us-east-1.rds.amazonaws.com:5432/postgres
    10 rows affected.





<table>
    <thead>
        <tr>
            <th>ordernumber</th>
            <th>orderdate</th>
            <th>requireddate</th>
            <th>shippeddate</th>
            <th>status</th>
            <th>comments</th>
            <th>customerNumber</th>
            <th>priceEach</th>
            <th>productCode</th>
            <th>quantityOrdered</th>
            <th>orderlinenumber</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>10100</td>
            <td>2003-01-06</td>
            <td>2003-01-13</td>
            <td>2003-01-10</td>
            <td>Shipped</td>
            <td>None</td>
            <td>1</td>
            <td>136.0</td>
            <td>S18_1749</td>
            <td>30</td>
            <td>1</td>
        </tr>
        <tr>
            <td>10100</td>
            <td>2003-01-06</td>
            <td>2003-01-13</td>
            <td>2003-01-10</td>
            <td>Shipped</td>
            <td>None</td>
            <td>1</td>
            <td>55.09</td>
            <td>S18_2248</td>
            <td>50</td>
            <td>2</td>
        </tr>
        <tr>
            <td>10100</td>
            <td>2003-01-06</td>
            <td>2003-01-13</td>
            <td>2003-01-10</td>
            <td>Shipped</td>
            <td>None</td>
            <td>1</td>
            <td>75.46</td>
            <td>S18_4409</td>
            <td>22</td>
            <td>3</td>
        </tr>
        <tr>
            <td>10100</td>
            <td>2003-01-06</td>
            <td>2003-01-13</td>
            <td>2003-01-10</td>
            <td>Shipped</td>
            <td>None</td>
            <td>1</td>
            <td>35.29</td>
            <td>S24_3969</td>
            <td>49</td>
            <td>4</td>
        </tr>
        <tr>
            <td>10101</td>
            <td>2003-01-09</td>
            <td>2003-01-18</td>
            <td>2003-01-11</td>
            <td>Shipped</td>
            <td>Check on availability.</td>
            <td>2</td>
            <td>108.06</td>
            <td>S18_2325</td>
            <td>25</td>
            <td>1</td>
        </tr>
        <tr>
            <td>10101</td>
            <td>2003-01-09</td>
            <td>2003-01-18</td>
            <td>2003-01-11</td>
            <td>Shipped</td>
            <td>Check on availability.</td>
            <td>2</td>
            <td>167.06</td>
            <td>S18_2795</td>
            <td>26</td>
            <td>2</td>
        </tr>
        <tr>
            <td>10101</td>
            <td>2003-01-09</td>
            <td>2003-01-18</td>
            <td>2003-01-11</td>
            <td>Shipped</td>
            <td>Check on availability.</td>
            <td>2</td>
            <td>32.53</td>
            <td>S24_1937</td>
            <td>45</td>
            <td>3</td>
        </tr>
        <tr>
            <td>10101</td>
            <td>2003-01-09</td>
            <td>2003-01-18</td>
            <td>2003-01-11</td>
            <td>Shipped</td>
            <td>Check on availability.</td>
            <td>2</td>
            <td>44.35</td>
            <td>S24_2022</td>
            <td>46</td>
            <td>4</td>
        </tr>
        <tr>
            <td>10102</td>
            <td>2003-01-10</td>
            <td>2003-01-18</td>
            <td>2003-01-14</td>
            <td>Shipped</td>
            <td>None</td>
            <td>3</td>
            <td>95.55</td>
            <td>S18_1342</td>
            <td>39</td>
            <td>1</td>
        </tr>
        <tr>
            <td>10102</td>
            <td>2003-01-10</td>
            <td>2003-01-18</td>
            <td>2003-01-14</td>
            <td>Shipped</td>
            <td>None</td>
            <td>3</td>
            <td>43.13</td>
            <td>S18_1367</td>
            <td>41</td>
            <td>2</td>
        </tr>
    </tbody>
</table>



<a name='4'></a>
## 4 - Third Normal Form (3NF)

The features of 3NF are the following:
- Already in 2NF: The table must already be in Second Normal Form (2NF).
- No Transitive Dependencies: There should be no transitive dependencies between non-prime attributes. In other words, non-prime attributes (attributes that are not part of any candidate key should not depend on other non-prime attributes).

In the `orders` table you have the following columns: `ordernumber`, `orderdate`, `requireddate`, `shippeddate`, `status`, `comments`, `customerNumber`, `priceEach`, `productCode`, `quantityOrdered`, and `orderlinenumber`.

Let's identify Transitive Dependencies:

- Columns `orderdate`, `requireddate`, `shippeddate`, `status`, `comments`, `salesRepEmployeeNumber`, and `customerNumber` are dependent on `ordernumber`.
- Columns `productCode`, `priceEach`, and `quantityOrdered` depend on the composite key (`ordernumber`, `orderlinenumber`).

You can see that columns related with order-level information such as dates, `comments` or even `customerNumber` depend only on `ordernumber`, which given that is part of the composite key (`ordernumber`, `orderlinenumber`), make those order-level fields to also depend on the composite key, and in particular on the `orderlinenumber` field. This is a transitive relationship that you should get rid of to achieve 3NF.

To transform the relations into 3NF, you need to separate the table into two: one for order-level information and another for order line items or order details.

- **Order Table:**
    * Primary Key: `ordernumber`
    * Attributes: `orderdate`, `requireddate`, `shippeddate`, `status`, `comments`, `salesRepEmployeeNumber`, `customerNumber`.

- **Order Details Table:**
    * Composite Primary Key: (`ordernumber`, `orderlinenumber`)
    * Attributes: `productCode`, `priceEach`, `quantityOrdered`

By organizing the data this way, you can ensure that each non-prime attribute depends only on the primary key, achieving 3NF. Let's do it and upload our tables in the third normal form. 

The final result of the 3NF normalization is the following

![ERD_3NF](./images/ERD_3NF.png)

4.1. Create the `classicmodels_3nf` schema to store your transformed tables there.


```sql
%%sql
CREATE SCHEMA IF NOT EXISTS classicmodels_3nf;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1lab1-rds.c9g6s0k8ogtn.us-east-1.rds.amazonaws.com:5432/postgres
    Done.





    []



4.2. You will need to read the `orders` and `customers` tables from the `classicmodels_2nf` schema. Although you will not make any further changes to the `customers` table in this step, you will upload it into the 3NF schema to keep all your datasets in the same place.

Read the `orders` table into the `df_orders` pandas dataframe:


```python
result = %sql select * from classicmodels_2nf.orders
df_orders = result.DataFrame()

df_orders.head()
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1lab1-rds.c9g6s0k8ogtn.us-east-1.rds.amazonaws.com:5432/postgres
    2996 rows affected.





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
      <th>ordernumber</th>
      <th>orderdate</th>
      <th>requireddate</th>
      <th>shippeddate</th>
      <th>status</th>
      <th>comments</th>
      <th>customerNumber</th>
      <th>priceEach</th>
      <th>productCode</th>
      <th>quantityOrdered</th>
      <th>orderlinenumber</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>10100</td>
      <td>2003-01-06</td>
      <td>2003-01-13</td>
      <td>2003-01-10</td>
      <td>Shipped</td>
      <td>None</td>
      <td>1</td>
      <td>136.00</td>
      <td>S18_1749</td>
      <td>30</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>10100</td>
      <td>2003-01-06</td>
      <td>2003-01-13</td>
      <td>2003-01-10</td>
      <td>Shipped</td>
      <td>None</td>
      <td>1</td>
      <td>55.09</td>
      <td>S18_2248</td>
      <td>50</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>10100</td>
      <td>2003-01-06</td>
      <td>2003-01-13</td>
      <td>2003-01-10</td>
      <td>Shipped</td>
      <td>None</td>
      <td>1</td>
      <td>75.46</td>
      <td>S18_4409</td>
      <td>22</td>
      <td>3</td>
    </tr>
    <tr>
      <th>3</th>
      <td>10100</td>
      <td>2003-01-06</td>
      <td>2003-01-13</td>
      <td>2003-01-10</td>
      <td>Shipped</td>
      <td>None</td>
      <td>1</td>
      <td>35.29</td>
      <td>S24_3969</td>
      <td>49</td>
      <td>4</td>
    </tr>
    <tr>
      <th>4</th>
      <td>10101</td>
      <td>2003-01-09</td>
      <td>2003-01-18</td>
      <td>2003-01-11</td>
      <td>Shipped</td>
      <td>Check on availability.</td>
      <td>2</td>
      <td>108.06</td>
      <td>S18_2325</td>
      <td>25</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>



Read the `customers` table into `df_customers`:


```python
result = %sql select * from classicmodels_2nf.customers
df_customers = result.DataFrame()

df_customers.head()
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1lab1-rds.c9g6s0k8ogtn.us-east-1.rds.amazonaws.com:5432/postgres
    98 rows affected.





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
      <th>customerName</th>
      <th>contactLastName</th>
      <th>contactFirstName</th>
      <th>phone</th>
      <th>addressLine1</th>
      <th>addressLine2</th>
      <th>postalCode</th>
      <th>city</th>
      <th>state</th>
      <th>country</th>
      <th>creditLimit</th>
      <th>salesRepEmployeeNumber</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>Online Diecast Creations Co.</td>
      <td>Young</td>
      <td>Dorothy</td>
      <td>6035558647</td>
      <td>2304 Long Airport Avenue</td>
      <td>None</td>
      <td>62005</td>
      <td>Nashua</td>
      <td>NH</td>
      <td>USA</td>
      <td>114200.0</td>
      <td>1216.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>Blauer See Auto, Co.</td>
      <td>Keitel</td>
      <td>Roland</td>
      <td>+49 69 66 90 2555</td>
      <td>Lyonerstr. 34</td>
      <td>None</td>
      <td>60528</td>
      <td>Frankfurt</td>
      <td>None</td>
      <td>Germany</td>
      <td>59700.0</td>
      <td>1504.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>Vitachrome Inc.</td>
      <td>Frick</td>
      <td>Michael</td>
      <td>2125551500</td>
      <td>2678 Kingston Rd.</td>
      <td>Suite 101</td>
      <td>10022</td>
      <td>NYC</td>
      <td>NY</td>
      <td>USA</td>
      <td>76400.0</td>
      <td>1286.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>Baane Mini Imports</td>
      <td>Bergulfsen</td>
      <td>Jonas</td>
      <td>07-98 9555</td>
      <td>Erling Skakkes gate 78</td>
      <td>None</td>
      <td>4110</td>
      <td>Stavern</td>
      <td>None</td>
      <td>Norway</td>
      <td>81700.0</td>
      <td>1504.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
      <td>Euro+ Shopping Channel</td>
      <td>Freyre</td>
      <td>Diego</td>
      <td>(91) 555 94 44</td>
      <td>C/ Moralzarzal, 86</td>
      <td>None</td>
      <td>28034</td>
      <td>Madrid</td>
      <td>None</td>
      <td>Spain</td>
      <td>227600.0</td>
      <td>1370.0</td>
    </tr>
  </tbody>
</table>
</div>



4.3. In order to separate the `classicmodels_2nf.orders` table into the `orderdetails` and the `order` table for the 3NF, let's extract the columns `columns_order_details` creating the `orderdetails` dataframe as a copy from `df_orders`:


```python
columns_order_details = ["ordernumber",  "orderlinenumber", "productCode", "quantityOrdered", "priceEach"]

### START CODE HERE ### (1 line of code)
df_orderdetails = df_orders[columns_order_details].copy() # @REPLACE EQUALS None[None].None()
### END CODE HERE ###

df_orderdetails.head()
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
      <th>ordernumber</th>
      <th>orderlinenumber</th>
      <th>productCode</th>
      <th>quantityOrdered</th>
      <th>priceEach</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>10100</td>
      <td>1</td>
      <td>S18_1749</td>
      <td>30</td>
      <td>136.00</td>
    </tr>
    <tr>
      <th>1</th>
      <td>10100</td>
      <td>2</td>
      <td>S18_2248</td>
      <td>50</td>
      <td>55.09</td>
    </tr>
    <tr>
      <th>2</th>
      <td>10100</td>
      <td>3</td>
      <td>S18_4409</td>
      <td>22</td>
      <td>75.46</td>
    </tr>
    <tr>
      <th>3</th>
      <td>10100</td>
      <td>4</td>
      <td>S24_3969</td>
      <td>49</td>
      <td>35.29</td>
    </tr>
    <tr>
      <th>4</th>
      <td>10101</td>
      <td>1</td>
      <td>S18_2325</td>
      <td>25</td>
      <td>108.06</td>
    </tr>
  </tbody>
</table>
</div>



##### __Expected Output__

| **ordernumber** | **orderlinenumber** | **productCode** | **quantityOrdered** | **priceEach** |
| --------------- | -------------------- | --------------- | -------------------- | ------------ |
| 10100           | 1                    | S18_1749        | 30                   | 136.00       |
| 10100           | 2                    | S18_2248        | 50                   | 55.09        |
| 10100           | 3                    | S18_4409        | 22                   | 75.46        |
| 10100           | 4                    | S24_3969        | 49                   | 35.29        |
| 10101           | 1                    | S18_2325        | 25                   | 108.06      |


4.4. Create a list of the columns which you need to drop from the `df_orders` dataframe - the ones associated with the `orderdetails` table. You will keep the `ordernumber` field as it is the key to relating the two tables:


```python
columns_order_details.pop(0)
columns_order_details
```




    ['orderlinenumber', 'productCode', 'quantityOrdered', 'priceEach']



4.5. Create the `df_orders` table with only the necessary columns, dropping the columns specified in the list `columns_order_details`. Then drop the duplicated rows with the method `drop_duplicates()`. You should keep `inplace` argument equal to `True`.


```python
### START CODE HERE ### (2 lines of code)
df_orders.drop(columns=columns_order_details, inplace=True) # @REPLACE None.None(columns=None, inplace=None)
df_orders.drop_duplicates(inplace=True) # @REPLACE None.None(inplace=None)
### END CODE HERE ###

df_orders.head()
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
      <th>ordernumber</th>
      <th>orderdate</th>
      <th>requireddate</th>
      <th>shippeddate</th>
      <th>status</th>
      <th>comments</th>
      <th>customerNumber</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>10100</td>
      <td>2003-01-06</td>
      <td>2003-01-13</td>
      <td>2003-01-10</td>
      <td>Shipped</td>
      <td>None</td>
      <td>1</td>
    </tr>
    <tr>
      <th>4</th>
      <td>10101</td>
      <td>2003-01-09</td>
      <td>2003-01-18</td>
      <td>2003-01-11</td>
      <td>Shipped</td>
      <td>Check on availability.</td>
      <td>2</td>
    </tr>
    <tr>
      <th>8</th>
      <td>10102</td>
      <td>2003-01-10</td>
      <td>2003-01-18</td>
      <td>2003-01-14</td>
      <td>Shipped</td>
      <td>None</td>
      <td>3</td>
    </tr>
    <tr>
      <th>10</th>
      <td>10103</td>
      <td>2003-01-29</td>
      <td>2003-02-07</td>
      <td>2003-02-02</td>
      <td>Shipped</td>
      <td>None</td>
      <td>4</td>
    </tr>
    <tr>
      <th>26</th>
      <td>10104</td>
      <td>2003-01-31</td>
      <td>2003-02-09</td>
      <td>2003-02-01</td>
      <td>Shipped</td>
      <td>None</td>
      <td>5</td>
    </tr>
  </tbody>
</table>
</div>



##### __Expected Output__

| **ordernumber** | **orderdate** | **requireddate** | **shippeddate** | **status** | **comments**             | **customerNumber** |
| --------------- | ------------- | ---------------- | ---------------- | ---------- | ----------------------- | ------------------ |
| 10100           | 2003-01-06    | 2003-01-13       | 2003-01-10       | Shipped    | None                     | 1                  |
| 10101           | 2003-01-09    | 2003-01-18       | 2003-01-11       | Shipped    | Check on availability.  | 2                  |
| 10102           | 2003-01-10    | 2003-01-18       | 2003-01-14       | Shipped    | None                     | 3                  |
| 10103           | 2003-01-29    | 2003-02-07       | 2003-02-02       | Shipped    | None                     | 4                  |
| 10104           | 2003-01-31    | 2003-02-09       | 2003-02-01       | Shipped    | None                     | 5                  |


Great! With those transformations you have achieved a 3NF from your initial OBT. 

4.6. Let's upload the data into the `classicmodels_3nf` schema. Remember that you have three tables: `customers`, `orders` and `orderdetails`. 


```sql
%%sql
DROP TABLE IF EXISTS classicmodels_3nf.customers
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1lab1-rds.c9g6s0k8ogtn.us-east-1.rds.amazonaws.com:5432/postgres
    Done.





    []




```sql
%%sql
DROP TABLE IF EXISTS classicmodels_3nf.orders
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1lab1-rds.c9g6s0k8ogtn.us-east-1.rds.amazonaws.com:5432/postgres
    Done.





    []




```sql
%%sql
DROP TABLE IF EXISTS classicmodels_3nf.orderdetails
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1lab1-rds.c9g6s0k8ogtn.us-east-1.rds.amazonaws.com:5432/postgres
    Done.





    []




```python
df_customers.to_sql('customers', engine, schema='classicmodels_3nf', index=False)
```




    98




```python
df_orders.to_sql('orders', engine, schema='classicmodels_3nf', index=False)
```




    326




```python
df_orderdetails.to_sql('orderdetails', engine, schema='classicmodels_3nf', index=False)
```




    996



Finally, you can take a look to each of the tables that have been stored in your database.


```sql
%%sql
select count(*) from classicmodels_3nf.customers;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1lab1-rds.c9g6s0k8ogtn.us-east-1.rds.amazonaws.com:5432/postgres
    1 rows affected.





<table>
    <thead>
        <tr>
            <th>count</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>98</td>
        </tr>
    </tbody>
</table>




```sql
%%sql
select count(*) from classicmodels_3nf.orders;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1lab1-rds.c9g6s0k8ogtn.us-east-1.rds.amazonaws.com:5432/postgres
    1 rows affected.





<table>
    <thead>
        <tr>
            <th>count</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>326</td>
        </tr>
    </tbody>
</table>




```sql
%%sql
select count(*) from classicmodels_3nf.orderdetails;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1lab1-rds.c9g6s0k8ogtn.us-east-1.rds.amazonaws.com:5432/postgres
    1 rows affected.





<table>
    <thead>
        <tr>
            <th>count</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>2996</td>
        </tr>
    </tbody>
</table>



In this lab, you have successfully transformed a One Big Table (OBT) into First Normal Form (1NF), Second Normal Form (2NF), and Third Normal Form (3NF). This process of normalization is crucial in designing efficient and reliable databases.

Throughout the lab, you have learned the importance of each normal form and the specific steps required to achieve them:

* 1NF: Ensuring that each table cell contains only atomic (indivisible) values and each record is unique.
* 2NF: Building on 1NF by removing partial dependencies, ensuring that non-key attributes are fully dependent on the primary key.
* 3NF: Further refining the table structure by removing transitive dependencies, ensuring that non-key attributes are dependent only on the primary key.

This lab has provided you with hands-on experience in transforming a dataset into a normalized form, highlighting the practical steps and considerations involved in database normalization. As you progress in your work as a Data Engineer, these skills will be invaluable in ensuring the quality and efficiency of the databases you design and maintain. 


```python

```
