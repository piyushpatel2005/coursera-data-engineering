# Capstone Project Part 1 - ETL and Data Modeling

During this capstone project, you will develop a data pipeline as part of a new project in the company DeFtunes. You will showcase the abilities and tools you have been using during the whole specialization.

# Table of Contents

- [ 1 - Introduction](#1)
- [ 2 - Data Sources](#2)
- [ 3 - Exploratory Data Analysis](#3)
- [ 4 - ETL Pipeline with AWS Glue and Terraform](#4)
  - [ 4.1 - Landing Zone](#4.1)
  - [ 4.2 - Transformation Zone](#4.2)
  - [ 4.3 - Serving Zone](#4.3)
- [ 5 - Data Modeling with dbt and Redshift Spectrum](#5)
  - [ 5.1 - Redshift Setup](#5.1)
  - [ 5.2 - Redshift Test](#5.2)
  - [ 5.3 - dbt Setup](#5.3)
  - [ 5.4 - Data Modeling](#5.4)
- [ 6 - Upload Files for Grading](#6)

<a name='1'></a>
## 1 - Introduction

DeFtunes is a new company in the music industry, offering a subscription-based app for streaming songs. Recently, they have expanded their services to include digital song purchases. With this new retail feature, DeFtunes requires a data pipeline to extract purchase data from their new API and operational database, enrich and model this data, and ultimately deliver the comprehensive data model for the Data Analysis team to review and gain insights. Your task is to develop this pipeline, ensuring the data is accurately processed and ready for in-depth analysis.

Here is the diagram with the main requirements for this project:

![Capstone_Diagram](images/Capstone-diagram.png)

1. The pipeline has to follow a medallion architecture with a landing, transform and serving zone.
2. The data generated in the pipeline will be stored in the company's data lake, in this case, an S3 bucket.
3. The silver layer should use Iceberg tables, and the gold layer should be inside Redshift.
4. The pipeline should be reproducible, you will have to implement it using Terraform.
5. The data should be modelled into a star schema in the serving layer, you should use dbt for the modelling part.

Before starting, you will need to import some required libraries and modules for the capstone development.


```python
import json
import requests
import pandas as pd
import subprocess

%load_ext sql

LAB_PREFIX='de-c4w4a1'
```

<a name='2'></a>
## 2 - Data Sources

The first data source you will be using is the DeFtunes operational database, which is running in RDS with a Postgres engine. This database contains a table with all the relevant information for the available songs that you can purchase. Let's connect to the table using the `%sql` magic. 

2.1. To define the connection string, go to CloudFormation Outputs in the AWS console. You will see the key `PostgresEndpoint`, copy the corresponding **Value** and replace with it the placeholder `<POSTGRES_ENDPOINT>` in the cell below (please, replace the whole placeholder including the brackets `<>`). Then run the cell code.


```python
RDSDBHOST = 'de-c4w4a1-rds.clgg68y6ow15.us-east-1.rds.amazonaws.com'
RDSDBPORT = '5432'
RDSDBNAME = 'postgres'
RDSDBUSER = 'postgresuser'
RDSDBPASSWORD = 'adminpwrd'

postgres_connection_url = f'postgresql+psycopg2://{RDSDBUSER}:{RDSDBPASSWORD}@{RDSDBHOST}:{RDSDBPORT}/{RDSDBNAME}'
%sql {postgres_connection_url}
```

2.2. Test that the connection works by running the following query.


```sql
%%sql
SELECT schema_name
FROM information_schema.schemata;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w4a1-rds.clgg68y6ow15.us-east-1.rds.amazonaws.com:5432/postgres
    6 rows affected.





<table>
    <tr>
        <th>schema_name</th>
    </tr>
    <tr>
        <td>public</td>
    </tr>
    <tr>
        <td>aws_s3</td>
    </tr>
    <tr>
        <td>aws_commons</td>
    </tr>
    <tr>
        <td>deftunes</td>
    </tr>
    <tr>
        <td>information_schema</td>
    </tr>
    <tr>
        <td>pg_catalog</td>
    </tr>
</table>



2.3. Inside the `deftunes` schema there is a table `songs` which was mentioned before. Let's query a sample from it:

*Note:* The `songs` table is based on the Million Song Dataset, more information can be found [here](http://millionsongdataset.com/).


```sql
%%sql
SELECT *
FROM deftunes.songs
LIMIT 5;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w4a1-rds.clgg68y6ow15.us-east-1.rds.amazonaws.com:5432/postgres
    5 rows affected.





<table>
    <tr>
        <th>track_id</th>
        <th>title</th>
        <th>song_id</th>
        <th>release</th>
        <th>artist_id</th>
        <th>artist_mbid</th>
        <th>artist_name</th>
        <th>duration</th>
        <th>artist_familiarity</th>
        <th>artist_hotttnesss</th>
        <th>year</th>
        <th>track_7digitalid</th>
        <th>shs_perf</th>
        <th>shs_work</th>
    </tr>
    <tr>
        <td>TRMBFJC12903CE2A89</td>
        <td>Mystery Babylon</td>
        <td>SOGOPFY12AB018E5B1</td>
        <td>Healing of All Nations</td>
        <td>ARP06GY1187B98B0F0</td>
        <td>106e0414-95a7-45e9-8176-bbc938deed68</td>
        <td>Yami Bolo</td>
        <td>146.49425</td>
        <td>0.4955022</td>
        <td>0.3224826</td>
        <td>2001</td>
        <td>8562838</td>
        <td>-1</td>
        <td>0</td>
    </tr>
    <tr>
        <td>TRMBFTN128F42665EA</td>
        <td>Världen É Din</td>
        <td>SOKFZOR12A8C1306B0</td>
        <td>Omérta</td>
        <td>ARZ6UKQ1187B9B0E35</td>
        <td>a432b2e7-7598-419b-8760-e8accff3c725</td>
        <td>The Latin Kings</td>
        <td>268.22485</td>
        <td>0.54002666</td>
        <td>0.42142987</td>
        <td>0</td>
        <td>3164205</td>
        <td>-1</td>
        <td>0</td>
    </tr>
    <tr>
        <td>TRMBFUD128F9318502</td>
        <td>Working Underground</td>
        <td>SOAVROI12AB0183312</td>
        <td>My Land is Your Land</td>
        <td>ARTOD2W1187B99FC16</td>
        <td>41b79e6f-9621-45c9-836c-9f08bedba4eb</td>
        <td>Ashley Hutchings_ Ernesto De Pascale</td>
        <td>226.42892</td>
        <td>0.4131989</td>
        <td>0.33407375</td>
        <td>0</td>
        <td>3957236</td>
        <td>-1</td>
        <td>0</td>
    </tr>
    <tr>
        <td>TRMBFNG12903CEA2A8</td>
        <td>Alien Bzzing</td>
        <td>SOCWCQV12AC3DF9B21</td>
        <td>Uomini D&#x27;onore</td>
        <td>ARUE65J1187B9AB4D9</td>
        <td>644feeb5-0ad9-457f-9d29-98474d42d9d3</td>
        <td>Fireside</td>
        <td>345.96527</td>
        <td>0.48547184</td>
        <td>0.3672936</td>
        <td>1997</td>
        <td>8593681</td>
        <td>-1</td>
        <td>0</td>
    </tr>
    <tr>
        <td>TRMBFSN128F4259499</td>
        <td>Repente</td>
        <td>SOGWDNA12A8C139BFC</td>
        <td>Limite das Aguas</td>
        <td>ARS8WH31187B9B8B04</td>
        <td>e02d67b8-b581-478e-be33-c988627e4050</td>
        <td>Edu Lobo</td>
        <td>269.47873</td>
        <td>0.34406215</td>
        <td>0.0</td>
        <td>0</td>
        <td>2775420</td>
        <td>-1</td>
        <td>0</td>
    </tr>
</table>



2.4. The second data source is a new API designed for the song purchase process. This API contains information on the purchases done by the users of the App and also contains relevant information about each user. Copy the endpoint value from the CloudFormation outputs tab and replace the placeholder `<API_ENDPOINT>` with it.


```python
API_ENDPOINT = "3.231.170.39:8080"
```

You can also access the documentation to the API by opening the new browser tab, pasting the API endpoint value and adding `/docs` to it. You will see an interactive interface to test the API.

2.5. The first endpoint is to the `sessions` path in the API, which retrieves the transactional sessions. Let's test the API by performing a GET request to the endpoint with the next cell. If everything works you should get a `200` status code from the `sessions_response` object.


```python
request_start_date = "2020-01-01"
request_end_date = "2020-03-01"
sessions_response = requests.get(f'http://{API_ENDPOINT}/sessions?start_date={request_start_date}&end_date={request_end_date}')
print(sessions_response.status_code)
```

    200


2.6. You can get the content of the response in JSON format using the `.json()` method, let's print the first record with the following cell.


```python
sessions_json = sessions_response.json()
print(json.dumps(sessions_json[0], indent=4))
```

    {
        "user_id": "6b287203-7cab-4f1a-b1a4-2b5076294682",
        "session_id": "04a5e8ac-1acd-48dc-88b9-651c4ddf489c",
        "session_items": [
            {
                "song_id": "TRXKAGX128F9342DD7",
                "song_name": "3 Cards",
                "artist_id": "AR475MP1187B9A5449",
                "artist_name": "The Balancing Act",
                "price": 1.03,
                "currency": "USD",
                "liked": true,
                "liked_since": "2023-01-27T08:29:54.970697"
            },
            {
                "song_id": "TRUKGBT128F4292C9B",
                "song_name": "Parisian Walls (gband Version_ Barcelona)",
                "artist_id": "ARP9HJX1187FB4E5DA",
                "artist_name": "Apostle Of Hustle",
                "price": 1.31,
                "currency": "USD",
                "liked": true,
                "liked_since": "2023-06-14T00:27:55.876873"
            },
            {
                "song_id": "TRCPHWV128F4228647",
                "song_name": "Los Sabanales",
                "artist_id": "ARRLMTZ1187B9AB6DD",
                "artist_name": "Los Corraleros De Majagual",
                "price": 0.69,
                "currency": "USD",
                "liked": false,
                "liked_since": null
            },
            {
                "song_id": "TRMHNOY12903CDD075",
                "song_name": "Earth Messiah",
                "artist_id": "ARHS5PJ1187FB3C50D",
                "artist_name": "Cathedral",
                "price": 0.52,
                "currency": "USD",
                "liked": false,
                "liked_since": null
            },
            {
                "song_id": "TRIBGDZ128F425A019",
                "song_name": "Eu sei que vou te amar",
                "artist_id": "ARJK24L1187B9AFF5E",
                "artist_name": "Quarteto Em Cy",
                "price": 1.74,
                "currency": "USD",
                "liked": false,
                "liked_since": null
            },
            {
                "song_id": "TROJSDS128F146E6E2",
                "song_name": "Write My Ticket",
                "artist_id": "AR227JP1187FB375BC",
                "artist_name": "Tift Merritt",
                "price": 0.76,
                "currency": "USD",
                "liked": true,
                "liked_since": "2023-10-18T21:54:16.351564"
            }
        ],
        "user_agent": "Mozilla/5.0 (Windows NT 11.0) AppleWebKit/531.2 (KHTML, like Gecko) Chrome/19.0.859.0 Safari/531.2",
        "session_start_time": "2020-02-07T18:05:25.824461"
    }


2.7. The second endpoint is to the `users` path in the API, it retrieves the transactional sessions. Perform a GET request to the endpoint with the next cell, then print a sample with the cell after that one.


```python
users_request = requests.get(f'http://{API_ENDPOINT}/users')
print(users_request.status_code)
```

    200



```python
users_json = users_request.json()
print(json.dumps(users_json[0], indent=4))
```

    {
        "user_id": "a3141825-3a8c-4968-a3af-5362011ef7d5",
        "user_name": "Elizabeth",
        "user_lastname": "Carey",
        "user_location": [
            "46.32313",
            "-0.45877",
            "Niort",
            "FR",
            "Europe/Paris"
        ],
        "user_since": "2020-12-22T14:15:35.936090"
    }


<a name='3'></a>
## 3 - Exploratory Data Analysis

To better understand the data sources, start analyzing the data types and values that come from each source. You can use the pandas library to perform Exploratory Data Analysis (EDA) on samples of data.

3.1. Let's begin with the `songs` table in the source RDS database, we will take advantage of the `%sql` magic to bring a sample with SQL and convert it into a pandas dataframe.


```python
songs_result = %sql SELECT *FROM deftunes.songs LIMIT 5
songs_df = songs_result.DataFrame()
songs_df.head()
```

     * postgresql+psycopg2://postgresuser:***@de-c4w4a1-rds.clgg68y6ow15.us-east-1.rds.amazonaws.com:5432/postgres
    5 rows affected.





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
      <th>track_id</th>
      <th>title</th>
      <th>song_id</th>
      <th>release</th>
      <th>artist_id</th>
      <th>artist_mbid</th>
      <th>artist_name</th>
      <th>duration</th>
      <th>artist_familiarity</th>
      <th>artist_hotttnesss</th>
      <th>year</th>
      <th>track_7digitalid</th>
      <th>shs_perf</th>
      <th>shs_work</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>TRMBFJC12903CE2A89</td>
      <td>Mystery Babylon</td>
      <td>SOGOPFY12AB018E5B1</td>
      <td>Healing of All Nations</td>
      <td>ARP06GY1187B98B0F0</td>
      <td>106e0414-95a7-45e9-8176-bbc938deed68</td>
      <td>Yami Bolo</td>
      <td>146.49425</td>
      <td>0.495502</td>
      <td>0.322483</td>
      <td>2001</td>
      <td>8562838</td>
      <td>-1</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>TRMBFTN128F42665EA</td>
      <td>Världen É Din</td>
      <td>SOKFZOR12A8C1306B0</td>
      <td>Omérta</td>
      <td>ARZ6UKQ1187B9B0E35</td>
      <td>a432b2e7-7598-419b-8760-e8accff3c725</td>
      <td>The Latin Kings</td>
      <td>268.22485</td>
      <td>0.540027</td>
      <td>0.421430</td>
      <td>0</td>
      <td>3164205</td>
      <td>-1</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>TRMBFUD128F9318502</td>
      <td>Working Underground</td>
      <td>SOAVROI12AB0183312</td>
      <td>My Land is Your Land</td>
      <td>ARTOD2W1187B99FC16</td>
      <td>41b79e6f-9621-45c9-836c-9f08bedba4eb</td>
      <td>Ashley Hutchings_ Ernesto De Pascale</td>
      <td>226.42892</td>
      <td>0.413199</td>
      <td>0.334074</td>
      <td>0</td>
      <td>3957236</td>
      <td>-1</td>
      <td>0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>TRMBFNG12903CEA2A8</td>
      <td>Alien Bzzing</td>
      <td>SOCWCQV12AC3DF9B21</td>
      <td>Uomini D'onore</td>
      <td>ARUE65J1187B9AB4D9</td>
      <td>644feeb5-0ad9-457f-9d29-98474d42d9d3</td>
      <td>Fireside</td>
      <td>345.96527</td>
      <td>0.485472</td>
      <td>0.367294</td>
      <td>1997</td>
      <td>8593681</td>
      <td>-1</td>
      <td>0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>TRMBFSN128F4259499</td>
      <td>Repente</td>
      <td>SOGWDNA12A8C139BFC</td>
      <td>Limite das Aguas</td>
      <td>ARS8WH31187B9B8B04</td>
      <td>e02d67b8-b581-478e-be33-c988627e4050</td>
      <td>Edu Lobo</td>
      <td>269.47873</td>
      <td>0.344062</td>
      <td>0.000000</td>
      <td>0</td>
      <td>2775420</td>
      <td>-1</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



3.1. Use Pandas info() method to print out a summary of information about the dataframe, including information about the columns such as their data types.


```python
print(songs_df.info())
```

    <class 'pandas.core.frame.DataFrame'>
    RangeIndex: 5 entries, 0 to 4
    Data columns (total 14 columns):
     #   Column              Non-Null Count  Dtype  
    ---  ------              --------------  -----  
     0   track_id            5 non-null      object 
     1   title               5 non-null      object 
     2   song_id             5 non-null      object 
     3   release             5 non-null      object 
     4   artist_id           5 non-null      object 
     5   artist_mbid         5 non-null      object 
     6   artist_name         5 non-null      object 
     7   duration            5 non-null      float64
     8   artist_familiarity  5 non-null      float64
     9   artist_hotttnesss   5 non-null      float64
     10  year                5 non-null      int64  
     11  track_7digitalid    5 non-null      int64  
     12  shs_perf            5 non-null      int64  
     13  shs_work            5 non-null      int64  
    dtypes: float64(3), int64(4), object(7)
    memory usage: 688.0+ bytes
    None


3.2. Use the describe() method to generate a summary of statistics about the numerical and object columns in the dataframe.


```python
songs_df.describe()
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
      <th>duration</th>
      <th>artist_familiarity</th>
      <th>artist_hotttnesss</th>
      <th>year</th>
      <th>track_7digitalid</th>
      <th>shs_perf</th>
      <th>shs_work</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>count</th>
      <td>5.000000</td>
      <td>5.000000</td>
      <td>5.000000</td>
      <td>5.000000</td>
      <td>5.000000e+00</td>
      <td>5.0</td>
      <td>5.0</td>
    </tr>
    <tr>
      <th>mean</th>
      <td>251.318404</td>
      <td>0.455652</td>
      <td>0.289056</td>
      <td>799.600000</td>
      <td>5.410676e+06</td>
      <td>-1.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>std</th>
      <td>72.768888</td>
      <td>0.077219</td>
      <td>0.166088</td>
      <td>1094.898306</td>
      <td>2.922813e+06</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>min</th>
      <td>146.494250</td>
      <td>0.344062</td>
      <td>0.000000</td>
      <td>0.000000</td>
      <td>2.775420e+06</td>
      <td>-1.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>25%</th>
      <td>226.428920</td>
      <td>0.413199</td>
      <td>0.322483</td>
      <td>0.000000</td>
      <td>3.164205e+06</td>
      <td>-1.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>50%</th>
      <td>268.224850</td>
      <td>0.485472</td>
      <td>0.334074</td>
      <td>0.000000</td>
      <td>3.957236e+06</td>
      <td>-1.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>75%</th>
      <td>269.478730</td>
      <td>0.495502</td>
      <td>0.367294</td>
      <td>1997.000000</td>
      <td>8.562838e+06</td>
      <td>-1.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>max</th>
      <td>345.965270</td>
      <td>0.540027</td>
      <td>0.421430</td>
      <td>2001.000000</td>
      <td>8.593681e+06</td>
      <td>-1.0</td>
      <td>0.0</td>
    </tr>
  </tbody>
</table>
</div>



3.3. Convert JSON objects `sessions_json` and `users_json` into pandas dataframes, and display the first few rows.


```python
session_df = pd.json_normalize(sessions_json)
session_df.head()
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
      <th>user_id</th>
      <th>session_id</th>
      <th>session_items</th>
      <th>user_agent</th>
      <th>session_start_time</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>6b287203-7cab-4f1a-b1a4-2b5076294682</td>
      <td>04a5e8ac-1acd-48dc-88b9-651c4ddf489c</td>
      <td>[{'song_id': 'TRXKAGX128F9342DD7', 'song_name'...</td>
      <td>Mozilla/5.0 (Windows NT 11.0) AppleWebKit/531....</td>
      <td>2020-02-07T18:05:25.824461</td>
    </tr>
    <tr>
      <th>1</th>
      <td>958ba0c2-cfc0-405e-a037-e644a4f34981</td>
      <td>143e7ad2-e172-4590-aeaa-b50ee449e7b3</td>
      <td>[{'song_id': 'TRTHVBF128F935584D', 'song_name'...</td>
      <td>Mozilla/5.0 (compatible; MSIE 5.0; Windows NT ...</td>
      <td>2020-02-18T04:07:14.676057</td>
    </tr>
    <tr>
      <th>2</th>
      <td>7d13cf48-d80e-4cbe-8581-cce0fd301acf</td>
      <td>6817fe3c-dd7f-4885-936b-dbbbb40923f2</td>
      <td>[{'song_id': 'TRJOSHE12903CDBA6F', 'song_name'...</td>
      <td>Opera/9.90.(X11; Linux i686; cv-RU) Presto/2.9...</td>
      <td>2020-02-21T22:25:56.407581</td>
    </tr>
    <tr>
      <th>3</th>
      <td>c06a8f89-4d88-4d71-83db-d567a69ef902</td>
      <td>0383ce58-b47d-4923-abdd-d58d583d7bb2</td>
      <td>[{'song_id': 'TRSXSSK128F146EB46', 'song_name'...</td>
      <td>Mozilla/5.0 (iPod; U; CPU iPhone OS 3_1 like M...</td>
      <td>2020-02-19T04:27:31.957162</td>
    </tr>
    <tr>
      <th>4</th>
      <td>7118b8ac-75fe-426a-bf6c-09044ed64011</td>
      <td>579ef099-ffed-410c-916a-05c222d7a734</td>
      <td>[{'song_id': 'TRRKCXY128F42B08EC', 'song_name'...</td>
      <td>Opera/8.77.(X11; Linux x86_64; lb-LU) Presto/2...</td>
      <td>2020-01-28T20:10:19.161986</td>
    </tr>
  </tbody>
</table>
</div>




```python
user_df = pd.json_normalize(users_json)
user_df.head()
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
      <th>user_id</th>
      <th>user_name</th>
      <th>user_lastname</th>
      <th>user_location</th>
      <th>user_since</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>a3141825-3a8c-4968-a3af-5362011ef7d5</td>
      <td>Elizabeth</td>
      <td>Carey</td>
      <td>[46.32313, -0.45877, Niort, FR, Europe/Paris]</td>
      <td>2020-12-22T14:15:35.936090</td>
    </tr>
    <tr>
      <th>1</th>
      <td>923d55a6-26e9-4a61-b3e1-9c010e5db2cc</td>
      <td>Joshua</td>
      <td>Bishop</td>
      <td>[46.75451, 33.34864, Nova Kakhovka, UA, Europe...</td>
      <td>2023-09-20T02:26:02.939528</td>
    </tr>
    <tr>
      <th>2</th>
      <td>ff728e8b-0c5b-48f7-a133-a30bf86c25e3</td>
      <td>Joseph</td>
      <td>Mcclain</td>
      <td>[32.57756, 71.52847, Mianwali, PK, Asia/Karachi]</td>
      <td>2023-12-05T17:59:27.933557</td>
    </tr>
    <tr>
      <th>3</th>
      <td>9ae4d3aa-8cc8-42ac-beb4-5c9c799a392d</td>
      <td>Jasmine</td>
      <td>White</td>
      <td>[35.6803, 51.0193, Shahre Jadide Andisheh, IR,...</td>
      <td>2024-06-18T17:56:45.626088</td>
    </tr>
    <tr>
      <th>4</th>
      <td>043010aa-9aad-4f63-8932-45eddada7856</td>
      <td>Tyler</td>
      <td>Ibarra</td>
      <td>[51.168, 7.973, Finnentrop, DE, Europe/Berlin]</td>
      <td>2023-11-13T10:27:32.854497</td>
    </tr>
  </tbody>
</table>
</div>



<a name='4'></a>
## 4 - ETL Pipeline with AWS Glue and Terraform

Now you will start creating the required resources and infrastructure for your data pipeline. Remember that you will use a medallion architecture.

The pipeline will be composed by the following steps:
- An extraction job to get the data from the PostgreSQL Database. This data will be stored in the landing zone of your Data Lake.
- An extraction job to get the data from the two API endpoints. This data will be stored in the landing zone of your Data Lake in JSON format.
- A transformation job that takes the raw data extracted from the PostgreSQL Database, casts some fields to the correct data types, adds some metadata and stores the dataset in Iceberg format.
- A transformation that takes the JSON data extracted from the API endpoints, normalizes some nested fields, adds metadata and stores the dataset in Iceberg format.
- The creation of some schemas in your Data Warehouse hosted in Redshift.

<a name='4.1'></a>
### 4.1 - Landing Zone

For the landing zone, you are going to create three Glue Jobs: one to extract the data from the PostgreSQL database and two to get the data from each API's endpoint. You are going to create those jobs using Terraform to guarantee that the infrastructure for each job will be always the same and changes can be tracked easily. Let's start by creating the jobs and then creating the infrastructure.

4.1.1. Go to the `terraform/assets/extract_jobs` folder. You will find two scripts

- `de-c4w4a1-extract-songs-job.py`: this script extracts data from the PostgreSQL source database.
- `de-c4w4a1-api-extract-job.py`: this script extracts data from the API. Endpoints can be provided through parameters.

Open each of them and follow the instructions in the comments to complete the scripts. Save changes to both of the files.

In a later section, you will run those Glue Jobs. Take into account that in the landing zone of your Data Lake you will see that the data will be stored in subfolders named according to the date of ingestion, which by default is your current date.

4.1.2. You will need to complete the terraform module `extract_job`. Given that you already created the scripts for the Glue Jobs, let's start by uploading them to an S3 bucket. Open the `terraform/modules/extract_job/s3.tf` file. You are already provided with some resources such as the scripts bucket and its permissions. Complete the code in the file following the instructions. Make sure that you save changes.

4.1.3. Open the `terraform/modules/extract_job/glue.tf` file. In this file you will set all the required resources to create the Glue Jobs. Complete the code following the instructions and save changes.

4.1.4. Explore the rest of the files of the `extract_job` module to understand the whole infrastructure. Avoid performing further changes to other files. Here is the summary of what you can find in those files:
- In `terraform/modules/extract_job/iam.tf` file you can find the creation of the role used to execute the Glue Jobs. There is also the attachment of a policy holding the permissions. Those permissions can be found directly in the `terraform/modules/extract_job/policies.tf` file.
- The `terraform/modules/extract_job/network.tf` has the definition of the private subnet and the source database security group used to create the Glue Connection used to allow the Glue Jobs to connect to the source PostgreSQL database.
- The `terraform/modules/extract_job/variables.tf` contains the necessary input parameters for this module, while the `terraform/modules/extract_job/outputs.tf` sets the possible outputs that terraform will show in the console from this module.

4.1.5. You are ready to deploy the first module of your infrastructure. Open the `terraform/main.tf` file and uncomment the lines associated with the module named `extract_job` (lines 1 to 14); make sure to keep the rest of modules commented. Open the `terraform/outputs.tf` file and uncomment the outputs associated with the extract module (lines 5 to 20). Save changes in both of the files.

4.1.6. In the VSCode terminal, go to the `terraform` folder and deploy the infrastructure with the following commands.

*Note*:<span style="color:red"> All terminal commands in this lab should be run in the VSCode terminal, not Jupyter, as it may cause some issues.</span>

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

*Note*: Remember that the command `terraform apply` will prompt you to reply `yes`.

4.1.7. You will get some outputs, in particular, you require the following three: `glue_api_users_extract_job`, `glue_sessions_users_extract_job` and `glue_rds_extract_job`. Those outputs correspond to the three glue jobs that will extract the data from the API endpoints and the database respectively. Use the following command in the terminal to execute each job based on its name. Replace `<JOB-NAME>` with the value of the terraform outputs (`de-c4w4a1-api-users-extract-job`, `de-c4w4a1-api-sessions-extract-job` and `de-c4w4a1-rds-extract-job`) respectively. You can run those three jobs in parallel.

```bash
aws glue start-job-run --job-name <JOB-NAME> | jq -r '.JobRunId'
```

You should get `JobRunID` in the output. Use this job run ID to track each job status by using this command, replacing the `<JOB-NAME>` and `<JobRunID>` placeholders.

```bash
aws glue get-job-run --job-name <JOB-NAME> --run-id <JobRunID> --output text --query "JobRun.JobRunState"
```

Wait until the statuses of those three jobs change to `SUCCEEDED` (each job should take around 3 mins).

<a name='4.2'></a>
### 4.2 - Transformation Zone

Once you have run the jobs that feed the first layer of your Data Lake three-tier architecture, it is time to generate the jobs to transform the data and store it in the second layer. The methodology will be similar to the previous zone: you will create the Glue Job scripts to take the data out of the landing layer, transform it and put it into the transformation zone layer. Then you will create the necessary resources in AWS using Terraform.

4.2.1. Go to the `terraform/assets/transform_jobs` folder. You will find two scripts:
- `de-c4w4a1-transform-songs-job.py`
- `de-c4w4a1-transform-json-job.py`

The two scripts will take the data out of the `landing_zone` layer in the Data Lake and, after some transformations, will store the data into the `transform_zone` layer in Apache Iceberg format.

Open each of them and follow the instructions in the comments to complete the scripts. Save changes to both of the files.

If you want to know more about saving data into Apache Iceberg format using the Glue Catalog, you can check the [documentation](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-etl-format-iceberg.html#aws-glue-programming-etl-format-iceberg-insert).

4.2.2. Time to complete the terraform module `transform_job`. Open the `terraform/modules/transform_job/s3.tf` file. Complete the script following the instructions and save changes.

4.2.3. Open the `terraform/modules/transform_job/glue.tf` file. Complete the code following the instructions and save changes.

4.2.4. Open the `terraform/main.tf` file and uncomment the lines associated with the module named `transform_job` (lines 16 to 30). 

4.2.5. Open the `terraform/outputs.tf` file and uncomment the lines 22 to 34. 

4.2.6. In the terminal, go to the `terraform` folder and deploy the infrastructure with the following commands:

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

*Note*: Remember that the command `terraform apply` will prompt you to reply `yes`.

4.2.7. You will get some additional outputs, in particular, you require the following two: `glue_json_transformation_job` and `glue_songs_transformation_job`. Execute the two glue jobs, based on the name (`de-c4w4a1-json-transform-job` or `de-c4w4a1-songs-transform-job`). You can run those two jobs in parallel. Use the following command in the VSCode terminal:

```bash
aws glue start-job-run --job-name <JOB-NAME> | jq -r '.JobRunId'
```

And based on the job run ID track each job status by using this command:

```bash
aws glue get-job-run --job-name <JOB-NAME> --run-id <JobRunID> --output text --query "JobRun.JobRunState"
```

Wait until the jobs statuses change to `SUCCEEDED` (each job should take around 3 mins).

<a name='4.3'></a>
### 4.3 - Serving Zone

For the last layer of your Three-tier Data Lake architecture, you are going to use AWS Redshift as a Data Warehouse solution. The transformations will be performed directly inside Redshift, but you need to make the data available in that storage solution. For that, you will use Redshift Spectrum, which is a feature that allows you to run queries against data stored in S3 without having to load the data into Redshift tables. For that, you are required to use a Glue Catalog which was already created in the `transform` module.

Follow the instructions below to finish setting up your resources for the `serving` module.

4.3.1. Open the file located at `terraform/modules/serving/iam.tf`. Complete the code and save changes.

4.3.2. Open the file `terraform/modules/serving/redshift.tf`. Complete the code and save changes.

4.3.4. Open the `terraform/main.tf` file and uncomment the lines associated with the module named `serving` (lines 32 to 48). 

4.3.5. Uncomment the corresponding lines in the `terraform/outputs.tf` file (lines 37 to 44).  

4.3.6. Deploy the infrastructure for the last layer. In the terminal, go to the `terraform` folder and run the commands:

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

*Note*: Remember that the command `terraform apply` will prompt you to reply `yes`.

With that, you have deployed the required infrastructure for your three-tier data lake. The next step consists of modelling the data in your Redshift Data Warehouse to serve it.

<a name='5'></a>
## 5 - Data Modeling with dbt and Redshift Spectrum

<a name='5.1'></a>
### 5.1 - Redshift Setup

Before working with DBT to model the data in the transformation layer into the serving layer, you need to use **Redshift Spectrum** to connect Redshift with the Iceberg tables. Spectrum allows you to query files from S3 directly from Redshift, it also has a special feature that allows us to read directly from Iceberg tables just by creating an external schema that points to the Glue database containing the tables. For this initial setup, you will use Terraform to set up the external schema and a normal schema for the serving layer.

5.1.1. Navigate to the `terraform` folder and run the serving module with the following command:

```bash
terraform apply -target=module.serving
```

<a name='5.2'></a>
### 5.2 - Redshift Test

To verify that the schemas were set up successfully, you will connect to the target Redshift cluster using the `%sql` magic. 

5.2.1. Let's start by configuring the credentials, you can obtain the Redshift's cluster endpoint in the CloudFormation stack's outputs and replace the placeholder `<REDSHIFT_ENDPOINT>` with it.


```python
REDSHIFTDBHOST = 'de-c4w4a1-redshift-cluster.c8litbcoeedd.us-east-1.redshift.amazonaws.com'
REDSHIFTDBPORT = 5439
REDSHIFTDBNAME = 'dev'
REDSHIFTDBUSER = 'defaultuser'
REDSHIFTDBPASSWORD = 'Defaultuserpwrd1234+'

redshift_connection_url = f'postgresql+psycopg2://{REDSHIFTDBUSER}:{REDSHIFTDBPASSWORD}@{REDSHIFTDBHOST}:{REDSHIFTDBPORT}/{REDSHIFTDBNAME}'
%sql {redshift_connection_url}
```

5.2.2. Test the connection and the setup, this query will return the list of available schemas for the `dev` database, and the external schema and gold layer schema should appear.


```python
%sql SHOW SCHEMAS FROM DATABASE dev 
```

     * postgresql+psycopg2://defaultuser:***@de-c4w4a1-redshift-cluster.c8litbcoeedd.us-east-1.redshift.amazonaws.com:5439/dev
       postgresql+psycopg2://postgresuser:***@de-c4w4a1-rds.clgg68y6ow15.us-east-1.rds.amazonaws.com:5432/postgres
    5 rows affected.





<table>
    <tr>
        <th>database_name</th>
        <th>schema_name</th>
        <th>schema_owner</th>
        <th>schema_type</th>
        <th>schema_acl</th>
        <th>source_database</th>
        <th>schema_option</th>
    </tr>
    <tr>
        <td>dev</td>
        <td>deftunes_serving</td>
        <td>100</td>
        <td>local</td>
        <td>None</td>
        <td>None</td>
        <td>None</td>
    </tr>
    <tr>
        <td>dev</td>
        <td>deftunes_transform</td>
        <td>100</td>
        <td>external</td>
        <td>None</td>
        <td>de_c4w4a1_silver_db</td>
        <td>{&quot;IAM_ROLE&quot;:&quot;arn:aws:iam::590183885028:role/de-c4w4a1-load-role&quot;}</td>
    </tr>
    <tr>
        <td>dev</td>
        <td>information_schema</td>
        <td>1</td>
        <td>local</td>
        <td>rdsdb=UCA/rdsdb~=U/rdsdb</td>
        <td>None</td>
        <td>None</td>
    </tr>
    <tr>
        <td>dev</td>
        <td>pg_catalog</td>
        <td>1</td>
        <td>local</td>
        <td>rdsdb=UCA/rdsdb~=U/rdsdb</td>
        <td>None</td>
        <td>None</td>
    </tr>
    <tr>
        <td>dev</td>
        <td>public</td>
        <td>1</td>
        <td>local</td>
        <td>rdsdb=UCA/rdsdb~=UC/rdsdb</td>
        <td>None</td>
        <td>None</td>
    </tr>
</table>



5.2.3. Now, let's verify that the Iceberg tables where automatically imported into the external schema, let's query the tables available inside the external schema.


```python
%sql SHOW TABLES FROM SCHEMA dev.deftunes_transform
```

     * postgresql+psycopg2://defaultuser:***@de-c4w4a1-redshift-cluster.c8litbcoeedd.us-east-1.redshift.amazonaws.com:5439/dev
       postgresql+psycopg2://postgresuser:***@de-c4w4a1-rds.clgg68y6ow15.us-east-1.rds.amazonaws.com:5432/postgres
    3 rows affected.





<table>
    <tr>
        <th>database_name</th>
        <th>schema_name</th>
        <th>table_name</th>
        <th>table_type</th>
        <th>table_acl</th>
        <th>remarks</th>
    </tr>
    <tr>
        <td>dev</td>
        <td>deftunes_transform</td>
        <td>sessions</td>
        <td>EXTERNAL TABLE</td>
        <td>None</td>
        <td>None</td>
    </tr>
    <tr>
        <td>dev</td>
        <td>deftunes_transform</td>
        <td>songs</td>
        <td>EXTERNAL TABLE</td>
        <td>None</td>
        <td>None</td>
    </tr>
    <tr>
        <td>dev</td>
        <td>deftunes_transform</td>
        <td>users</td>
        <td>EXTERNAL TABLE</td>
        <td>None</td>
        <td>None</td>
    </tr>
</table>



Query the Iceberg tables in the external schema to verify that Redshift can read from them.


```python
%sql select * from deftunes_transform.songs limit 10
```

     * postgresql+psycopg2://defaultuser:***@de-c4w4a1-redshift-cluster.c8litbcoeedd.us-east-1.redshift.amazonaws.com:5439/dev
       postgresql+psycopg2://postgresuser:***@de-c4w4a1-rds.clgg68y6ow15.us-east-1.rds.amazonaws.com:5432/postgres
    10 rows affected.





<table>
    <tr>
        <th>track_id</th>
        <th>title</th>
        <th>song_id</th>
        <th>release</th>
        <th>artist_id</th>
        <th>artist_mbid</th>
        <th>artist_name</th>
        <th>duration</th>
        <th>artist_familiarity</th>
        <th>artist_hotttnesss</th>
        <th>year</th>
        <th>track_7digitalid</th>
        <th>shs_perf</th>
        <th>shs_work</th>
        <th>ingest_on</th>
        <th>source_from</th>
    </tr>
    <tr>
        <td>TRPXBXP128F146C064</td>
        <td>Weeyeya</td>
        <td>SOMFWJW12A6D4F9D28</td>
        <td>The Famous Years Compiled</td>
        <td>ARN0AR31187FB5367D</td>
        <td>d634f58c-aa2c-4430-9c85-b8e0d1c66878</td>
        <td>Kraan</td>
        <td>271.281</td>
        <td>0.559683</td>
        <td>0.361413</td>
        <td>1998</td>
        <td>328867</td>
        <td>-1</td>
        <td>0</td>
        <td>2024-09-30</td>
        <td>postgres_rds</td>
    </tr>
    <tr>
        <td>TRMZGNW128E0782D5A</td>
        <td>What In The World (1999 Digital Remaster)</td>
        <td>SOBMJTV12A6310F31A</td>
        <td>Low</td>
        <td>ARJA1841187FB3A029</td>
        <td>5441c29d-3602-4898-b1a1-b77fa23b8e50</td>
        <td>David Bowie</td>
        <td>142.759</td>
        <td>0.86597</td>
        <td>0.594734</td>
        <td>1977</td>
        <td>13064</td>
        <td>-1</td>
        <td>0</td>
        <td>2024-09-30</td>
        <td>postgres_rds</td>
    </tr>
    <tr>
        <td>TRLOGUY12903CB3E60</td>
        <td>Vishwanathashtakam</td>
        <td>SOLWZZZ12AB0186714</td>
        <td>Sacred Chants Vol. 2</td>
        <td>ARD02S71187B993B0A</td>
        <td>e0d34377-74a1-4a0c-80ff-96e60175fe56</td>
        <td>Seven</td>
        <td>288.574</td>
        <td>0.640726</td>
        <td>0.396923</td>
        <td>0</td>
        <td>7882723</td>
        <td>-1</td>
        <td>0</td>
        <td>2024-09-30</td>
        <td>postgres_rds</td>
    </tr>
    <tr>
        <td>TRPULLJ128F429083C</td>
        <td>Rescue Me Now</td>
        <td>SOYWOFT12A8C13A36C</td>
        <td>Prologue - Best Of The Early Years 1996-2002</td>
        <td>ARI49UF1187B9B7438</td>
        <td>99e9b8ff-b8ea-4019-a073-acc9fbc93bbe</td>
        <td>Jay-Jay Johanson</td>
        <td>299.572</td>
        <td>0.577374</td>
        <td>0.387365</td>
        <td>2004</td>
        <td>3349100</td>
        <td>-1</td>
        <td>0</td>
        <td>2024-09-30</td>
        <td>postgres_rds</td>
    </tr>
    <tr>
        <td>TREVTQG128F9312034</td>
        <td>Disgrace (Unholy Remix)</td>
        <td>SOELZNT12AB017F3E0</td>
        <td>Sacrament</td>
        <td>ARPVGD81187FB4BD3D</td>
        <td>af0a34fd-f127-4b43-93be-e98fa04cd233</td>
        <td>Unter Null</td>
        <td>238.759</td>
        <td>0.652143</td>
        <td>0.455393</td>
        <td>0</td>
        <td>5962785</td>
        <td>-1</td>
        <td>0</td>
        <td>2024-09-30</td>
        <td>postgres_rds</td>
    </tr>
    <tr>
        <td>TRTITUS12903CE43F4</td>
        <td>O</td>
        <td>SOOLBAA12AB0189EB5</td>
        <td>Escape From Heaven</td>
        <td>ARIUOGM1187B9A8F9F</td>
        <td>d5a41cd3-a365-452e-9af3-c9dc276c18d5</td>
        <td>Niko Skorpio</td>
        <td>383.973</td>
        <td>0.433426</td>
        <td>0.335693</td>
        <td>2006</td>
        <td>9044893</td>
        <td>-1</td>
        <td>0</td>
        <td>2024-09-30</td>
        <td>postgres_rds</td>
    </tr>
    <tr>
        <td>TRJXWAV128F93130F3</td>
        <td>The Rite of Spring_ Part One - The Adoration of the Earth: The Adoration of the Earth - The Sage</td>
        <td>SOOATBT12AB017EFA0</td>
        <td>Prokofiev - Scythian Suite_ Stravinsky - The Rite of Spring</td>
        <td>ARQVLRE1187FB46F1D</td>
        <td>e7636d63-65e4-492d-bc57-2ab552df4d57</td>
        <td>Dallas Symphony Orchestra</td>
        <td>22.7261</td>
        <td>0.413414</td>
        <td>0.316483</td>
        <td>0</td>
        <td>5482486</td>
        <td>-1</td>
        <td>0</td>
        <td>2024-09-30</td>
        <td>postgres_rds</td>
    </tr>
    <tr>
        <td>TRBMIML128F4238C4D</td>
        <td>Never Expected Me</td>
        <td>SOAOZQM12A8AE463A8</td>
        <td>Riddim Driven: Adrenaline</td>
        <td>AR48JC31187B9A1049</td>
        <td>9602602f-37a7-4c7b-8ebc-a2960054e54a</td>
        <td>Mr. Easy</td>
        <td>207.386</td>
        <td>0.576375</td>
        <td>0.38872</td>
        <td>0</td>
        <td>2013669</td>
        <td>-1</td>
        <td>0</td>
        <td>2024-09-30</td>
        <td>postgres_rds</td>
    </tr>
    <tr>
        <td>TRKDMOW128EF3533C8</td>
        <td>Two Happy People</td>
        <td>SOHGGDK12A6D4F472A</td>
        <td>The Sweethearts Of The Blues 1</td>
        <td>ARCG6TX1187FB5BDAE</td>
        <td>edd9fb9d-949f-4a4c-a057-485a75baf935</td>
        <td>Shirley &amp; Lee</td>
        <td>119.823</td>
        <td>0.499265</td>
        <td>0.350709</td>
        <td>0</td>
        <td>803416</td>
        <td>-1</td>
        <td>0</td>
        <td>2024-09-30</td>
        <td>postgres_rds</td>
    </tr>
    <tr>
        <td>TRNQHOC128F92C6055</td>
        <td>Jungle Fever</td>
        <td>SORNOOE12A8C14455F</td>
        <td>The Best Of The Klingonz</td>
        <td>ARQFIMH1187B99D9D8</td>
        <td>fa1a3155-d889-48f4-854b-cf580b80717c</td>
        <td>The Klingonz</td>
        <td>125.309</td>
        <td>0.575674</td>
        <td>0.372041</td>
        <td>1996</td>
        <td>3550110</td>
        <td>-1</td>
        <td>0</td>
        <td>2024-09-30</td>
        <td>postgres_rds</td>
    </tr>
</table>




```python
%sql select * from deftunes_transform.sessions limit 10
```

     * postgresql+psycopg2://defaultuser:***@de-c4w4a1-redshift-cluster.c8litbcoeedd.us-east-1.redshift.amazonaws.com:5439/dev
       postgresql+psycopg2://postgresuser:***@de-c4w4a1-rds.clgg68y6ow15.us-east-1.rds.amazonaws.com:5432/postgres
    5 rows affected.





<table>
    <tr>
        <th>user_id</th>
        <th>session_id</th>
        <th>song_id</th>
        <th>song_name</th>
        <th>artist_id</th>
        <th>artist_name</th>
        <th>price</th>
        <th>currency</th>
        <th>liked</th>
        <th>liked_since</th>
        <th>user_agent</th>
        <th>session_start_time</th>
        <th>ingest_on</th>
    </tr>
    <tr>
        <td>7118b8ac-75fe-426a-bf6c-09044ed64011</td>
        <td>579ef099-ffed-410c-916a-05c222d7a734</td>
        <td>TRRKCXY128F42B08EC</td>
        <td>Majestic</td>
        <td>ARPNILO1187B9B59BB</td>
        <td>Journey</td>
        <td>0.89</td>
        <td>USD</td>
        <td>True</td>
        <td>2021-04-18T22:54:45.137434</td>
        <td>Opera/8.77.(X11; Linux x86_64; lb-LU) Presto/2.9.170 Version/11.00</td>
        <td>2020-01-28T20:10:19.161986</td>
        <td>2024-09-30</td>
    </tr>
    <tr>
        <td>7118b8ac-75fe-426a-bf6c-09044ed64011</td>
        <td>579ef099-ffed-410c-916a-05c222d7a734</td>
        <td>TRACVFS128F424CF67</td>
        <td>We Cry As One</td>
        <td>ARIGHFP1187B9A4467</td>
        <td>The Old Dead Tree</td>
        <td>1.85</td>
        <td>USD</td>
        <td>False</td>
        <td>None</td>
        <td>Opera/8.77.(X11; Linux x86_64; lb-LU) Presto/2.9.170 Version/11.00</td>
        <td>2020-01-28T20:10:19.161986</td>
        <td>2024-09-30</td>
    </tr>
    <tr>
        <td>7118b8ac-75fe-426a-bf6c-09044ed64011</td>
        <td>579ef099-ffed-410c-916a-05c222d7a734</td>
        <td>TRWWMUJ128F932FAFF</td>
        <td>Thugz Of War</td>
        <td>ARJNOOU11F4C845A6A</td>
        <td>Riviera Regime</td>
        <td>1.44</td>
        <td>USD</td>
        <td>False</td>
        <td>None</td>
        <td>Opera/8.77.(X11; Linux x86_64; lb-LU) Presto/2.9.170 Version/11.00</td>
        <td>2020-01-28T20:10:19.161986</td>
        <td>2024-09-30</td>
    </tr>
    <tr>
        <td>7118b8ac-75fe-426a-bf6c-09044ed64011</td>
        <td>579ef099-ffed-410c-916a-05c222d7a734</td>
        <td>TRYQJNT128F429B976</td>
        <td>Last Train</td>
        <td>AREJC2N1187FB555F9</td>
        <td>Dare</td>
        <td>1.85</td>
        <td>USD</td>
        <td>True</td>
        <td>2023-06-10T11:22:42.309662</td>
        <td>Opera/8.77.(X11; Linux x86_64; lb-LU) Presto/2.9.170 Version/11.00</td>
        <td>2020-01-28T20:10:19.161986</td>
        <td>2024-09-30</td>
    </tr>
    <tr>
        <td>7118b8ac-75fe-426a-bf6c-09044ed64011</td>
        <td>579ef099-ffed-410c-916a-05c222d7a734</td>
        <td>TRXWVQV12903CE7B2E</td>
        <td>Self Doubt Gun</td>
        <td>ARN4IYF1187FB49D76</td>
        <td>Pagan Wanderer Lu</td>
        <td>0.33</td>
        <td>USD</td>
        <td>False</td>
        <td>None</td>
        <td>Opera/8.77.(X11; Linux x86_64; lb-LU) Presto/2.9.170 Version/11.00</td>
        <td>2020-01-28T20:10:19.161986</td>
        <td>2024-09-30</td>
    </tr>
</table>




```python
%sql select * from deftunes_transform.users limit 10
```

     * postgresql+psycopg2://defaultuser:***@de-c4w4a1-redshift-cluster.c8litbcoeedd.us-east-1.redshift.amazonaws.com:5439/dev
       postgresql+psycopg2://postgresuser:***@de-c4w4a1-rds.clgg68y6ow15.us-east-1.rds.amazonaws.com:5432/postgres
    10 rows affected.





<table>
    <tr>
        <th>user_id</th>
        <th>user_lastname</th>
        <th>user_name</th>
        <th>user_since</th>
        <th>ingest_on</th>
        <th>latitude</th>
        <th>longitude</th>
        <th>place_name</th>
        <th>country_code</th>
        <th>timezone</th>
        <th>processing_timestamp</th>
    </tr>
    <tr>
        <td>90b33325-f5bd-4c43-a90b-168836b16d49</td>
        <td>Ferguson</td>
        <td>Katherine</td>
        <td>2020-01-29T17:55:57.719494</td>
        <td>2024-09-30</td>
        <td>50.598427</td>
        <td>13.610242</td>
        <td>Litvínov</td>
        <td>CZ</td>
        <td>Europe/Prague</td>
        <td>2024-09-30 15:10:55</td>
    </tr>
    <tr>
        <td>9d458d10-0b5d-4426-9d01-993e9597226b</td>
        <td>Gardner</td>
        <td>Christopher</td>
        <td>2020-01-09T17:29:36.635959</td>
        <td>2024-09-30</td>
        <td>13.51825</td>
        <td>99.95469</td>
        <td>Damnoen Saduak</td>
        <td>TH</td>
        <td>Asia/Bangkok</td>
        <td>2024-09-30 15:10:55</td>
    </tr>
    <tr>
        <td>43eafcf6-620a-4eea-b8c5-0cb5cef29e34</td>
        <td>Chavez</td>
        <td>James</td>
        <td>2020-01-28T19:44:57.976367</td>
        <td>2024-09-30</td>
        <td>45.47885</td>
        <td>133.42825</td>
        <td>Lesozavodsk</td>
        <td>RU</td>
        <td>Asia/Vladivostok</td>
        <td>2024-09-30 15:10:55</td>
    </tr>
    <tr>
        <td>7246fbc0-d1fd-4de3-b4d3-fbd7a884b8e9</td>
        <td>Mejia</td>
        <td>Kelly</td>
        <td>2020-01-21T21:32:55.223506</td>
        <td>2024-09-30</td>
        <td>48.98693</td>
        <td>2.44892</td>
        <td>Gonesse</td>
        <td>FR</td>
        <td>Europe/Paris</td>
        <td>2024-09-30 15:10:55</td>
    </tr>
    <tr>
        <td>80aab7ab-48a2-4476-ae87-41ce40f71c25</td>
        <td>Lewis</td>
        <td>Barry</td>
        <td>2020-01-26T19:00:15.272554</td>
        <td>2024-09-30</td>
        <td>53.16167</td>
        <td>6.76111</td>
        <td>Hoogezand</td>
        <td>NL</td>
        <td>Europe/Amsterdam</td>
        <td>2024-09-30 15:10:55</td>
    </tr>
    <tr>
        <td>f1fcedc0-0b78-45e1-a4c4-06cb5fac3370</td>
        <td>Peck</td>
        <td>Kenneth</td>
        <td>2020-01-30T21:33:08.448189</td>
        <td>2024-09-30</td>
        <td>43.31667</td>
        <td>-2.68333</td>
        <td>Gernika-Lumo</td>
        <td>ES</td>
        <td>Europe/Madrid</td>
        <td>2024-09-30 15:10:55</td>
    </tr>
    <tr>
        <td>2072178f-5ff1-46be-b3ad-0288fe705da3</td>
        <td>Warren</td>
        <td>Jo</td>
        <td>2020-01-30T03:45:56.479523</td>
        <td>2024-09-30</td>
        <td>-19.32556</td>
        <td>-41.25528</td>
        <td>Resplendor</td>
        <td>BR</td>
        <td>America/Sao_Paulo</td>
        <td>2024-09-30 15:10:55</td>
    </tr>
    <tr>
        <td>221ec393-6d1b-4047-9b5d-647b6ecaca3d</td>
        <td>Callahan</td>
        <td>Kathryn</td>
        <td>2020-01-24T07:04:50.825472</td>
        <td>2024-09-30</td>
        <td>39.09112</td>
        <td>-94.41551</td>
        <td>Independence</td>
        <td>US</td>
        <td>America/Chicago</td>
        <td>2024-09-30 15:10:55</td>
    </tr>
    <tr>
        <td>e55206f6-47b7-4d32-8b03-253089853de2</td>
        <td>Harris</td>
        <td>Brendan</td>
        <td>2020-01-26T13:51:00.911375</td>
        <td>2024-09-30</td>
        <td>35.50056</td>
        <td>117.63083</td>
        <td>Pingyi</td>
        <td>CN</td>
        <td>Asia/Shanghai</td>
        <td>2024-09-30 15:10:55</td>
    </tr>
    <tr>
        <td>4372a6a9-8336-4f80-8252-f43643881161</td>
        <td>Howell</td>
        <td>Emily</td>
        <td>2020-01-28T07:40:50.915585</td>
        <td>2024-09-30</td>
        <td>9.91861</td>
        <td>-68.30472</td>
        <td>Tinaquillo</td>
        <td>VE</td>
        <td>America/Caracas</td>
        <td>2024-09-30 15:10:55</td>
    </tr>
</table>



<a name='5.3'></a>
### 5.3 - dbt Setup

Now that you have set up the target database in Redshift, you will create a dbt project that connects to Redshift and allows you to model the transform layer tables into the final data model in the serving layer. 

5.3.1. Create the new project using the following commands in the VSCode terminal.

*Note*:<span style="color:red"> All terminal commands in this lab should be run in the VSCode terminal, not Jupyter, as it may cause some issues. Always check that the virtual environment is active.</span>

```bash
cd ..
source jupyterlab-venv/bin/activate
dbt init dbt_modeling
```

After running the command, dbt will ask you the engine to run the project on, select the option for Redshift. The CLI will ask you for the connection details, use the same connection values you used before to configure the `%sql` magic (step 5.2.1), when asked for the `dbname` input `dev`, for `schema` input `deftunes_serving`, for `threads` input `1`. 

![dbt setup](images/dbt_config.png)

5.3.2. To test the connection, run the following commands:

```bash
cd dbt_modeling
dbt debug
```

If everything was correctly configured, you should see the following text at the end of the output:

```bash
Connection test: [OK connection ok]
```

*Note*: If you had issues defining the connection details, you can use the `profiles.yml` file in the scripts folder as a guide to define the connection details, change the placeholder in the file with the Redshift cluster endpoint and then copy it to the following path `~/.dbt/profiles.yml ` with this command:

```bash
cp ../scripts/profiles.yml ~/.dbt/profiles.yml 
```

<a name='5.4'></a>
### 5.4 - Data Modeling

*Note*: This section is optional and not graded.

5.4.1. Now that the dbt project has the initial setup, create a new folder named `serving_layer` in the models folder, this subfolder will contain the models associated with the star schema.
```bash
cd models
mkdir serving_layer
```

5.4.2. In the `./dbt_modeling/dbt_project.yml`, change the `models` block to the following one:

```yaml
models:
  dbt_modeling:
    serving_layer:
      +materialized: table
```

Save changes to the file.

5.4.3. Now you can prepare files for data modeling into the star schema. You will need to identify fact and dimensional tables, then create an SQL model file for each. Finally, inside the new folder, create a `schema.yml` file. You can look at the `example` folder if needed. Once you are done modelling the data, use the following command to run the models you created (make sure you are in the `dbt_modeling` project folder):

```bash
dbt run -s serving_layer
```

If all the model runs were successful, you should see an output like this one, where N is the number of models you created.
```bash
Completed successfully

Done. PASS=X WARN=0 ERROR=0 SKIP=0 TOTAL=X
```

5.4.4. The final test for your models will be for you to query them using the `%sql` magic. Run the following query for each table to get a sample and verify that the model definition was correct (replace the placeholder `<TABLE_NAME>`).


```python
%sql SHOW TABLES FROM SCHEMA dev.deftunes_serving
```


```python
%sql SELECT * FROM deftunes_serving.<TABLE_NAME> limit 10
```


```python
%sql DROP SCHEMA deftunes_serving CASCADE;
```

During the first part of the capstone, you set up a data architecture for the new business operation of DeFtunes, you implemented a basic data pipeline that can be improved later on with an iterative approach. In the second part of the capstone, you will improve upon the existing data architecture adding orchestration, data visualization and data quality checks. 

<a name='6'></a>
## 6 - Upload Files for Grading

Upload the notebook into S3 bucket for grading purposes.

*Note*: you may need to click **Save** button before the upload.


```python
# Retrieve the AWS account ID
result = subprocess.run(['aws', 'sts', 'get-caller-identity', '--query', 'Account', '--output', 'text'], capture_output=True, text=True)
AWS_ACCOUNT_ID = result.stdout.strip()

SUBMISSION_BUCKET = f"{LAB_PREFIX}-{AWS_ACCOUNT_ID}-us-east-1-submission"

!aws s3 cp ./C4_W4_Assignment_1.ipynb s3://$SUBMISSION_BUCKET/C4_W4_Assignment_1_Learner.ipynb
```

    upload: ./C4_W4_Assignment_1.ipynb to s3://de-c4w4a1-590183885028-us-east-1-submission/C4_W4_Assignment_1_Learner.ipynb



```python

```
