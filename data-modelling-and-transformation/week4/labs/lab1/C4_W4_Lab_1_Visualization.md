# Week 4 Lab: Data Visualization with DBT and Superset

During this week's lab, you will learn how to create analytical views and a dashboard.

# Table of Contents

- [ 1 - Introduction and Setup](#1)
- [ 2 - Views with dbt](#2)
  - [ 2.1 - Annual Sales per Office](#2.1)
  - [ 2.2 - Average Sales per Product Line](#2.2)
  - [ 2.3 - Running Analytical Views](#2.3)
  - [ 2.4 - Creating Materialized View](#2.4)
- [ 3 - Dashboard with Apache Superset](#3)

Load the SQL extension.


```python
%load_ext sql
```

<a name='1'></a>
## 1 - Introduction and Setup

Data visualization is a critical skill for a Data Engineer, enabling you to transform complex data sets into insightful, actionable visuals. Effective visual communication can enhance understanding of the insights you gained while processing data, uncover trends, and drive strategic actions in any data-centric organization. In this lab, you will use a star schema model created on top of the `classicmodels` dataset, you will create analytical views on top of this model and then display the results in a dashboard using Apache Superset.

**dbt** is a transformation workflow command line tool based on SQL, you have worked with dbt before and the initial project is similar to the one done for the assignment of the first week of this course.

Let's start the `dbt` project called `classicmodels_modeling`.

*Note*:<span style="color:red"> All terminal commands in this lab should be run in the VSCode terminal, not Jupyter, as it may cause some issues. Always check that the virtual environment is active.</span>

1.1.1. Activate the Python virtual environment for the lab. Run the following command in the VSCode terminal:
```bash
source jupyterlab-venv/bin/activate
```

1.1.2. Check that `dbt` Core is installed.

```bash
dbt --version
```

1.1.3. Go to AWS console, and in the CloudFormation Outputs tab find the key `PostgresEndpoint`. Copy the corresponding **Value**. 

1.1.4. Open the file located at `./scripts/profiles.yml`. Replace the placeholders `<DATABASE_ENDPOINT>` with the endpoint value. Save changes.

1.1.5. Run the following command to copy the `profiles.yml` file to the invisible folder `.dbt` of the project:

```bash
cp ./scripts/profiles.yml $HOME/.dbt/profiles.yml 
```

1.1.6. Navigate into your project's directory:

```bash
cd classicmodels_modeling
```

1.1.7. Run the following command to test the connection:

```bash
dbt debug
```

It should return a `Connection test: OK connection ok` at the end of the output.

1.1.8. Run the following command to fetch the latest stable versions of tools and libraries specified in the `packages.yml` file.

```bash
dbt deps
```

1.1.9. Load the source configuration into the notebook with the following code:


```python
import yaml

with open("./scripts/profiles.yml", 'r') as stream:
    data_loaded = yaml.safe_load(stream)
    
DBCONFIG = data_loaded["classicmodels_modeling"]["outputs"]["source"]
DBHOST = DBCONFIG["host"]
DBPORT = int(DBCONFIG["port"])
DBNAME = DBCONFIG["dbname"]
DBUSER = DBCONFIG["user"]
DBPASSWORD = DBCONFIG["password"]
db_connection_url = f'postgresql+psycopg2://{DBUSER}:{DBPASSWORD}@{DBHOST}:{DBPORT}/{DBNAME}'

%sql {db_connection_url}
```

1.1.10. Test the connection from the Notebook to the Postgres database. You should see the schemas of the database in the output.


```sql
%%sql

SELECT schema_name
FROM information_schema.schemata;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w4lab1-rds.cd044wq8gkrk.us-east-1.rds.amazonaws.com:5432/postgres
    4 rows affected.





<table>
    <thead>
        <tr>
            <th>schema_name</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>public</td>
        </tr>
        <tr>
            <td>classicmodels</td>
        </tr>
        <tr>
            <td>information_schema</td>
        </tr>
        <tr>
            <td>pg_catalog</td>
        </tr>
    </tbody>
</table>



1.1.11. Run the star schema models in the VSCode terminal (make sure that you are still in the project directory `classicmodels_modeling`):

```bash
dbt run
```

You should see a similar output to the run command:

```bash
Finished running 7 table models in 0 hours 0 minutes and 1.xx seconds (1.xx s).

Completed successfully

Done. PASS=7 WARN=0 ERROR=0 SKIP=0 TOTAL=7
```

1.1.12. Verify that the star schema was added to the Postgres database, the new schema should be called `classicmodels_star_schema`:


```sql
%%sql

SELECT schema_name
FROM information_schema.schemata;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w4lab1-rds.cd044wq8gkrk.us-east-1.rds.amazonaws.com:5432/postgres
    5 rows affected.





<table>
    <thead>
        <tr>
            <th>schema_name</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>public</td>
        </tr>
        <tr>
            <td>classicmodels_star_schema</td>
        </tr>
        <tr>
            <td>classicmodels</td>
        </tr>
        <tr>
            <td>information_schema</td>
        </tr>
        <tr>
            <td>pg_catalog</td>
        </tr>
    </tbody>
</table>



1.1.13. Now, let's verify that the star schema fact and dimensional tables are available in the new schema. Run the following cell:


```sql
%%sql
SELECT table_catalog, table_schema, table_name, table_type  FROM information_schema.tables 
WHERE table_schema = 'classicmodels_star_schema'
```

     * postgresql+psycopg2://postgresuser:***@de-c4w4lab1-rds.cd044wq8gkrk.us-east-1.rds.amazonaws.com:5432/postgres
    7 rows affected.





<table>
    <thead>
        <tr>
            <th>table_catalog</th>
            <th>table_schema</th>
            <th>table_name</th>
            <th>table_type</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>postgres</td>
            <td>classicmodels_star_schema</td>
            <td>dim_dates</td>
            <td>BASE TABLE</td>
        </tr>
        <tr>
            <td>postgres</td>
            <td>classicmodels_star_schema</td>
            <td>dates</td>
            <td>BASE TABLE</td>
        </tr>
        <tr>
            <td>postgres</td>
            <td>classicmodels_star_schema</td>
            <td>dim_customers</td>
            <td>BASE TABLE</td>
        </tr>
        <tr>
            <td>postgres</td>
            <td>classicmodels_star_schema</td>
            <td>dim_employees</td>
            <td>BASE TABLE</td>
        </tr>
        <tr>
            <td>postgres</td>
            <td>classicmodels_star_schema</td>
            <td>dim_offices</td>
            <td>BASE TABLE</td>
        </tr>
        <tr>
            <td>postgres</td>
            <td>classicmodels_star_schema</td>
            <td>dim_products</td>
            <td>BASE TABLE</td>
        </tr>
        <tr>
            <td>postgres</td>
            <td>classicmodels_star_schema</td>
            <td>fact_orders</td>
            <td>BASE TABLE</td>
        </tr>
    </tbody>
</table>



Verify that each table has data and their columns names and types.


```python
%sql SELECT * FROM classicmodels_star_schema.fact_orders LIMIT 10
```

     * postgresql+psycopg2://postgresuser:***@de-c4w4lab1-rds.cd044wq8gkrk.us-east-1.rds.amazonaws.com:5432/postgres
    10 rows affected.





<table>
    <thead>
        <tr>
            <th>fact_order_key</th>
            <th>customer_key</th>
            <th>employee_key</th>
            <th>office_key</th>
            <th>product_key</th>
            <th>order_date</th>
            <th>order_required_date</th>
            <th>order_shipped_date</th>
            <th>quantity_ordered</th>
            <th>product_price</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>1f8f31c7d43a69e00bff8264109eeb4c</td>
            <td>00411460f7c92d2124a67ea0f4cb5f85</td>
            <td>3948ead63a9f2944218de038d8934305</td>
            <td>c81e728d9d4c2f636f067f89cc14862c</td>
            <td>f95ed59fd3313855e03af1b96334e685</td>
            <td>2003-01-06 00:00:00</td>
            <td>2003-01-13 00:00:00</td>
            <td>2003-01-10 00:00:00</td>
            <td>30</td>
            <td>136</td>
        </tr>
        <tr>
            <td>98242fbce3c533a4ae5827f13142af23</td>
            <td>00411460f7c92d2124a67ea0f4cb5f85</td>
            <td>3948ead63a9f2944218de038d8934305</td>
            <td>c81e728d9d4c2f636f067f89cc14862c</td>
            <td>e99d5f4747d9abb3e4148d0317dac3df</td>
            <td>2003-01-06 00:00:00</td>
            <td>2003-01-13 00:00:00</td>
            <td>2003-01-10 00:00:00</td>
            <td>50</td>
            <td>55.09</td>
        </tr>
        <tr>
            <td>3b73bc66e4119eacbc3c63eaf4608548</td>
            <td>00411460f7c92d2124a67ea0f4cb5f85</td>
            <td>3948ead63a9f2944218de038d8934305</td>
            <td>c81e728d9d4c2f636f067f89cc14862c</td>
            <td>429d1bfa2660c76daf6d27f99e10c40e</td>
            <td>2003-01-06 00:00:00</td>
            <td>2003-01-13 00:00:00</td>
            <td>2003-01-10 00:00:00</td>
            <td>22</td>
            <td>75.46</td>
        </tr>
        <tr>
            <td>969259c8f1be79a73de9014d18c56827</td>
            <td>00411460f7c92d2124a67ea0f4cb5f85</td>
            <td>3948ead63a9f2944218de038d8934305</td>
            <td>c81e728d9d4c2f636f067f89cc14862c</td>
            <td>62b141855439f4ba3f52036409a9fd14</td>
            <td>2003-01-06 00:00:00</td>
            <td>2003-01-13 00:00:00</td>
            <td>2003-01-10 00:00:00</td>
            <td>49</td>
            <td>35.29</td>
        </tr>
        <tr>
            <td>85fc329e6a3e29d44ae81fd0f0809edf</td>
            <td>76dc611d6ebaafc66cc0879c71b5db5c</td>
            <td>49b8b4f95f02e055801da3b4f58e28b7</td>
            <td>8f14e45fceea167a5a36dedd4bea2543</td>
            <td>ef8e0274836db61155b2f6329206ffb6</td>
            <td>2003-01-09 00:00:00</td>
            <td>2003-01-18 00:00:00</td>
            <td>2003-01-11 00:00:00</td>
            <td>25</td>
            <td>108.06</td>
        </tr>
        <tr>
            <td>ba8b8ce928e516b27b249b7ab87d7eb7</td>
            <td>76dc611d6ebaafc66cc0879c71b5db5c</td>
            <td>49b8b4f95f02e055801da3b4f58e28b7</td>
            <td>8f14e45fceea167a5a36dedd4bea2543</td>
            <td>9bdf7d6aaeffea97a4ab0f562fe54026</td>
            <td>2003-01-09 00:00:00</td>
            <td>2003-01-18 00:00:00</td>
            <td>2003-01-11 00:00:00</td>
            <td>26</td>
            <td>167.06</td>
        </tr>
        <tr>
            <td>18d5bb62b3a7d1e610f32b0b06f5c900</td>
            <td>76dc611d6ebaafc66cc0879c71b5db5c</td>
            <td>49b8b4f95f02e055801da3b4f58e28b7</td>
            <td>8f14e45fceea167a5a36dedd4bea2543</td>
            <td>7e1421596451e8efe4ac99cf6fc783be</td>
            <td>2003-01-09 00:00:00</td>
            <td>2003-01-18 00:00:00</td>
            <td>2003-01-11 00:00:00</td>
            <td>45</td>
            <td>32.53</td>
        </tr>
        <tr>
            <td>8272d88bcb8ca0786f887b9b31e903a6</td>
            <td>76dc611d6ebaafc66cc0879c71b5db5c</td>
            <td>49b8b4f95f02e055801da3b4f58e28b7</td>
            <td>8f14e45fceea167a5a36dedd4bea2543</td>
            <td>fb74c462a79ab6342c1a81bfb0bbd8d8</td>
            <td>2003-01-09 00:00:00</td>
            <td>2003-01-18 00:00:00</td>
            <td>2003-01-11 00:00:00</td>
            <td>46</td>
            <td>44.35</td>
        </tr>
        <tr>
            <td>c5ee31aea3ebb5f4e85821ac18f1ab2d</td>
            <td>fc221309746013ac554571fbd180e1c8</td>
            <td>c0a271bc0ecb776a094786474322cb82</td>
            <td>eccbc87e4b5ce2fe28308fd9f2a7baf3</td>
            <td>2f1940aaee16632276d6ba6b5b709615</td>
            <td>2003-01-10 00:00:00</td>
            <td>2003-01-18 00:00:00</td>
            <td>2003-01-14 00:00:00</td>
            <td>39</td>
            <td>95.55</td>
        </tr>
        <tr>
            <td>47a313d1eb63620f42d485ac2e4da78d</td>
            <td>fc221309746013ac554571fbd180e1c8</td>
            <td>c0a271bc0ecb776a094786474322cb82</td>
            <td>eccbc87e4b5ce2fe28308fd9f2a7baf3</td>
            <td>cd0f60c4410a9de77da04fb01e74c504</td>
            <td>2003-01-10 00:00:00</td>
            <td>2003-01-18 00:00:00</td>
            <td>2003-01-14 00:00:00</td>
            <td>41</td>
            <td>43.13</td>
        </tr>
    </tbody>
</table>




```python
%sql SELECT * FROM classicmodels_star_schema.dim_customers LIMIT 10
```

     * postgresql+psycopg2://postgresuser:***@de-c4w4lab1-rds.cd044wq8gkrk.us-east-1.rds.amazonaws.com:5432/postgres
    10 rows affected.





<table>
    <thead>
        <tr>
            <th>customer_key</th>
            <th>customer_name</th>
            <th>customer_last_name</th>
            <th>customer_first_name</th>
            <th>phone</th>
            <th>address_line_1</th>
            <th>address_line_2</th>
            <th>postal_code</th>
            <th>city</th>
            <th>state</th>
            <th>country</th>
            <th>creditlimit</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>6974ce5ac660610b44d9b9fed0ff9548</td>
            <td>Atelier graphique</td>
            <td>Schmitt</td>
            <td>Carine </td>
            <td>40.32.2555</td>
            <td>54, rue Royale</td>
            <td>None</td>
            <td>44000</td>
            <td>Nantes</td>
            <td>None</td>
            <td>France</td>
            <td>21000</td>
        </tr>
        <tr>
            <td>7f6ffaa6bb0b408017b62254211691b5</td>
            <td>Signal Gift Stores</td>
            <td>King</td>
            <td>Jean</td>
            <td>7025551838</td>
            <td>8489 Strong St.</td>
            <td>None</td>
            <td>83030</td>
            <td>Las Vegas</td>
            <td>NV</td>
            <td>USA</td>
            <td>71800</td>
        </tr>
        <tr>
            <td>5fd0b37cd7dbbb00f97ba6ce92bf5add</td>
            <td>Australian Collectors, Co.</td>
            <td>Ferguson</td>
            <td>Peter</td>
            <td>03 9520 4555</td>
            <td>636 St Kilda Road</td>
            <td>Level 3</td>
            <td>3004</td>
            <td>Melbourne</td>
            <td>Victoria</td>
            <td>Australia</td>
            <td>117300</td>
        </tr>
        <tr>
            <td>07e1cd7dca89a1678042477183b7ac3f</td>
            <td>La Rochelle Gifts</td>
            <td>Labrune</td>
            <td>Janine </td>
            <td>40.67.8555</td>
            <td>67, rue des Cinquante Otages</td>
            <td>None</td>
            <td>44000</td>
            <td>Nantes</td>
            <td>None</td>
            <td>France</td>
            <td>118200</td>
        </tr>
        <tr>
            <td>4c56ff4ce4aaf9573aa5dff913df997a</td>
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
            <td>81700</td>
        </tr>
        <tr>
            <td>c8ffe9a587b126f152ed3d89a146b445</td>
            <td>Mini Gifts Distributors Ltd.</td>
            <td>Nelson</td>
            <td>Susan</td>
            <td>4155551450</td>
            <td>5677 Strong St.</td>
            <td>None</td>
            <td>97562</td>
            <td>San Rafael</td>
            <td>CA</td>
            <td>USA</td>
            <td>210500</td>
        </tr>
        <tr>
            <td>3def184ad8f4755ff269862ea77393dd</td>
            <td>Havel &amp; Zbyszek Co</td>
            <td>Piestrzeniewicz</td>
            <td>Zbyszek </td>
            <td>(26) 642-7555</td>
            <td>ul. Filtrowa 68</td>
            <td>None</td>
            <td>01-012</td>
            <td>Warszawa</td>
            <td>None</td>
            <td>Poland</td>
            <td>0</td>
        </tr>
        <tr>
            <td>76dc611d6ebaafc66cc0879c71b5db5c</td>
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
            <td>59700</td>
        </tr>
        <tr>
            <td>d1f491a404d6854880943e5c3cd9ca25</td>
            <td>Mini Wheels Co.</td>
            <td>Murphy</td>
            <td>Julie</td>
            <td>6505555787</td>
            <td>5557 North Pendale Street</td>
            <td>None</td>
            <td>94217</td>
            <td>San Francisco</td>
            <td>CA</td>
            <td>USA</td>
            <td>64600</td>
        </tr>
        <tr>
            <td>1afa34a7f984eeabdbb0a7d494132ee5</td>
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
            <td>114900</td>
        </tr>
    </tbody>
</table>




```python
%sql SELECT * FROM classicmodels_star_schema.dim_employees LIMIT 10
```

     * postgresql+psycopg2://postgresuser:***@de-c4w4lab1-rds.cd044wq8gkrk.us-east-1.rds.amazonaws.com:5432/postgres
    10 rows affected.





<table>
    <thead>
        <tr>
            <th>employee_key</th>
            <th>employee_last_name</th>
            <th>employee_first_name</th>
            <th>job_title</th>
            <th>email</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>fba9d88164f3e2d9109ee770223212a0</td>
            <td>Murphy</td>
            <td>Diane</td>
            <td>President</td>
            <td>dmurphy@classicmodelcars.com</td>
        </tr>
        <tr>
            <td>4ca82782c5372a547c104929f03fe7a9</td>
            <td>Patterson</td>
            <td>Mary</td>
            <td>VP Sales</td>
            <td>mpatterso@classicmodelcars.com</td>
        </tr>
        <tr>
            <td>8a1e808b55fde9455cb3d8857ed88389</td>
            <td>Firrelli</td>
            <td>Jeff</td>
            <td>VP Marketing</td>
            <td>jfirrelli@classicmodelcars.com</td>
        </tr>
        <tr>
            <td>b1563a78ec59337587f6ab6397699afc</td>
            <td>Patterson</td>
            <td>William</td>
            <td>Sales Manager (APAC)</td>
            <td>wpatterson@classicmodelcars.com</td>
        </tr>
        <tr>
            <td>c667d53acd899a97a85de0c201ba99be</td>
            <td>Bondur</td>
            <td>Gerard</td>
            <td>Sale Manager (EMEA)</td>
            <td>gbondur@classicmodelcars.com</td>
        </tr>
        <tr>
            <td>208e43f0e45c4c78cafadb83d2888cb6</td>
            <td>Bow</td>
            <td>Anthony</td>
            <td>Sales Manager (NA)</td>
            <td>abow@classicmodelcars.com</td>
        </tr>
        <tr>
            <td>a3fb4fbf9a6f9cf09166aa9c20cbc1ad</td>
            <td>Jennings</td>
            <td>Leslie</td>
            <td>Sales Rep</td>
            <td>ljennings@classicmodelcars.com</td>
        </tr>
        <tr>
            <td>0f2c9a93eea6f38fabb3acb1c31488c6</td>
            <td>Thompson</td>
            <td>Leslie</td>
            <td>Sales Rep</td>
            <td>lthompson@classicmodelcars.com</td>
        </tr>
        <tr>
            <td>c44e503833b64e9f27197a484f4257c0</td>
            <td>Firrelli</td>
            <td>Julie</td>
            <td>Sales Rep</td>
            <td>jfirrelli@classicmodelcars.com</td>
        </tr>
        <tr>
            <td>3948ead63a9f2944218de038d8934305</td>
            <td>Patterson</td>
            <td>Steve</td>
            <td>Sales Rep</td>
            <td>spatterson@classicmodelcars.com</td>
        </tr>
    </tbody>
</table>




```python
%sql SELECT * FROM classicmodels_star_schema.dim_offices LIMIT 10
```

     * postgresql+psycopg2://postgresuser:***@de-c4w4lab1-rds.cd044wq8gkrk.us-east-1.rds.amazonaws.com:5432/postgres
    7 rows affected.





<table>
    <thead>
        <tr>
            <th>office_key</th>
            <th>postal_code</th>
            <th>city</th>
            <th>state</th>
            <th>country</th>
            <th>territory</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>c4ca4238a0b923820dcc509a6f75849b</td>
            <td>94080</td>
            <td>San Francisco</td>
            <td>CA</td>
            <td>USA</td>
            <td>NA</td>
        </tr>
        <tr>
            <td>c81e728d9d4c2f636f067f89cc14862c</td>
            <td>02107</td>
            <td>Boston</td>
            <td>MA</td>
            <td>USA</td>
            <td>NA</td>
        </tr>
        <tr>
            <td>eccbc87e4b5ce2fe28308fd9f2a7baf3</td>
            <td>10022</td>
            <td>NYC</td>
            <td>NY</td>
            <td>USA</td>
            <td>NA</td>
        </tr>
        <tr>
            <td>a87ff679a2f3e71d9181a67b7542122c</td>
            <td>75017</td>
            <td>Paris</td>
            <td>None</td>
            <td>France</td>
            <td>EMEA</td>
        </tr>
        <tr>
            <td>e4da3b7fbbce2345d7772b0674a318d5</td>
            <td>102-8578</td>
            <td>Tokyo</td>
            <td>Chiyoda-Ku</td>
            <td>Japan</td>
            <td>Japan</td>
        </tr>
        <tr>
            <td>1679091c5a880faf6fb5e6087eb1b2dc</td>
            <td>2010</td>
            <td>Sydney</td>
            <td>NSW</td>
            <td>Australia</td>
            <td>APAC</td>
        </tr>
        <tr>
            <td>8f14e45fceea167a5a36dedd4bea2543</td>
            <td>EC2N 1HN</td>
            <td>London</td>
            <td>None</td>
            <td>UK</td>
            <td>EMEA</td>
        </tr>
    </tbody>
</table>




```python
%sql SELECT * FROM classicmodels_star_schema.dim_products LIMIT 10
```

     * postgresql+psycopg2://postgresuser:***@de-c4w4lab1-rds.cd044wq8gkrk.us-east-1.rds.amazonaws.com:5432/postgres
    10 rows affected.





<table>
    <thead>
        <tr>
            <th>product_key</th>
            <th>product_name</th>
            <th>product_line</th>
            <th>product_scale</th>
            <th>product_vendor</th>
            <th>product_description</th>
            <th>product_line_description</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>c57855c679250d9702f2557f9f8c44df</td>
            <td>1969 Harley Davidson Ultimate Chopper</td>
            <td>Motorcycles</td>
            <td>1:10</td>
            <td>Min Lin Diecast</td>
            <td>This replica features working kickstand, front suspension, gear-shift lever, footbrake lever, drive chain, wheels and steering. All parts are particularly delicate due to their precise scale and require special care and attention.</td>
            <td>Our motorcycles are state of the art replicas of classic as well as contemporary motorcycle legends such as Harley Davidson, Ducati and Vespa. Models contain stunning details such as official logos, rotating wheels, working kickstand, front suspension, gear-shift lever, footbrake lever, and drive chain. Materials used include diecast and plastic. The models range in size from 1:10 to 1:50 scale and include numerous limited edition and several out-of-production vehicles. All models come fully assembled and ready for display in the home or office. Most include a certificate of authenticity.</td>
        </tr>
        <tr>
            <td>0a113318bee26a2722998d59eaabd280</td>
            <td>1952 Alpine Renault 1300</td>
            <td>Classic Cars</td>
            <td>1:10</td>
            <td>Classic Metal Creations</td>
            <td>Turnable front wheels; steering function; detailed interior; detailed engine; opening hood; opening trunk; opening doors; and detailed chassis.</td>
            <td>Attention car enthusiasts: Make your wildest car ownership dreams come true. Whether you are looking for classic muscle cars, dream sports cars or movie-inspired miniatures, you will find great choices in this category. These replicas feature superb attention to detail and craftsmanship and offer features such as working steering system, opening forward compartment, opening rear trunk with removable spare wheel, 4-wheel independent spring suspension, and so on. The models range in size from 1:10 to 1:24 scale and include numerous limited edition and several out-of-production vehicles. All models include a certificate of authenticity from their manufacturers and come fully assembled and ready for display in the home or office.</td>
        </tr>
        <tr>
            <td>ff0f004a2bd95bc5437fda6accd38e4c</td>
            <td>1996 Moto Guzzi 1100i</td>
            <td>Motorcycles</td>
            <td>1:10</td>
            <td>Highway 66 Mini Classics</td>
            <td>Official Moto Guzzi logos and insignias, saddle bags located on side of motorcycle, detailed engine, working steering, working suspension, two leather seats, luggage rack, dual exhaust pipes, small saddle bag located on handle bars, two-tone paint with chrome accents, superior die-cast detail , rotating wheels , working kick stand, diecast metal with plastic parts and baked enamel finish.</td>
            <td>Our motorcycles are state of the art replicas of classic as well as contemporary motorcycle legends such as Harley Davidson, Ducati and Vespa. Models contain stunning details such as official logos, rotating wheels, working kickstand, front suspension, gear-shift lever, footbrake lever, and drive chain. Materials used include diecast and plastic. The models range in size from 1:10 to 1:50 scale and include numerous limited edition and several out-of-production vehicles. All models come fully assembled and ready for display in the home or office. Most include a certificate of authenticity.</td>
        </tr>
        <tr>
            <td>325a76ec55097780dea7210114a8f2fd</td>
            <td>2003 Harley-Davidson Eagle Drag Bike</td>
            <td>Motorcycles</td>
            <td>1:10</td>
            <td>Red Start Diecast</td>
            <td>Model features, official Harley Davidson logos and insignias, detachable rear wheelie bar, heavy diecast metal with resin parts, authentic multi-color tampo-printed graphics, separate engine drive belts, free-turning front fork, rotating tires and rear racing slick, certificate of authenticity, detailed engine, display stand\r\n, precision diecast replica, baked enamel finish, 1:10 scale model, removable fender, seat and tank cover piece for displaying the superior detail of the v-twin engine</td>
            <td>Our motorcycles are state of the art replicas of classic as well as contemporary motorcycle legends such as Harley Davidson, Ducati and Vespa. Models contain stunning details such as official logos, rotating wheels, working kickstand, front suspension, gear-shift lever, footbrake lever, and drive chain. Materials used include diecast and plastic. The models range in size from 1:10 to 1:50 scale and include numerous limited edition and several out-of-production vehicles. All models come fully assembled and ready for display in the home or office. Most include a certificate of authenticity.</td>
        </tr>
        <tr>
            <td>590a952a0d5589b7c925844818a4648a</td>
            <td>1972 Alfa Romeo GTA</td>
            <td>Classic Cars</td>
            <td>1:10</td>
            <td>Motor City Art Classics</td>
            <td>Features include: Turnable front wheels; steering function; detailed interior; detailed engine; opening hood; opening trunk; opening doors; and detailed chassis.</td>
            <td>Attention car enthusiasts: Make your wildest car ownership dreams come true. Whether you are looking for classic muscle cars, dream sports cars or movie-inspired miniatures, you will find great choices in this category. These replicas feature superb attention to detail and craftsmanship and offer features such as working steering system, opening forward compartment, opening rear trunk with removable spare wheel, 4-wheel independent spring suspension, and so on. The models range in size from 1:10 to 1:24 scale and include numerous limited edition and several out-of-production vehicles. All models include a certificate of authenticity from their manufacturers and come fully assembled and ready for display in the home or office.</td>
        </tr>
        <tr>
            <td>504d67645cc129e92161e29d6f2fbd24</td>
            <td>1962 LanciaA Delta 16V</td>
            <td>Classic Cars</td>
            <td>1:10</td>
            <td>Second Gear Diecast</td>
            <td>Features include: Turnable front wheels; steering function; detailed interior; detailed engine; opening hood; opening trunk; opening doors; and detailed chassis.</td>
            <td>Attention car enthusiasts: Make your wildest car ownership dreams come true. Whether you are looking for classic muscle cars, dream sports cars or movie-inspired miniatures, you will find great choices in this category. These replicas feature superb attention to detail and craftsmanship and offer features such as working steering system, opening forward compartment, opening rear trunk with removable spare wheel, 4-wheel independent spring suspension, and so on. The models range in size from 1:10 to 1:24 scale and include numerous limited edition and several out-of-production vehicles. All models include a certificate of authenticity from their manufacturers and come fully assembled and ready for display in the home or office.</td>
        </tr>
        <tr>
            <td>ec93374992862f071a8ade8d69da3c64</td>
            <td>1968 Ford Mustang</td>
            <td>Classic Cars</td>
            <td>1:12</td>
            <td>Autoart Studio Design</td>
            <td>Hood, doors and trunk all open to reveal highly detailed interior features. Steering wheel actually turns the front wheels. Color dark green.</td>
            <td>Attention car enthusiasts: Make your wildest car ownership dreams come true. Whether you are looking for classic muscle cars, dream sports cars or movie-inspired miniatures, you will find great choices in this category. These replicas feature superb attention to detail and craftsmanship and offer features such as working steering system, opening forward compartment, opening rear trunk with removable spare wheel, 4-wheel independent spring suspension, and so on. The models range in size from 1:10 to 1:24 scale and include numerous limited edition and several out-of-production vehicles. All models include a certificate of authenticity from their manufacturers and come fully assembled and ready for display in the home or office.</td>
        </tr>
        <tr>
            <td>b3e8b79be1911a1f5f07d06c1a6f8d81</td>
            <td>2001 Ferrari Enzo</td>
            <td>Classic Cars</td>
            <td>1:12</td>
            <td>Second Gear Diecast</td>
            <td>Turnable front wheels; steering function; detailed interior; detailed engine; opening hood; opening trunk; opening doors; and detailed chassis.</td>
            <td>Attention car enthusiasts: Make your wildest car ownership dreams come true. Whether you are looking for classic muscle cars, dream sports cars or movie-inspired miniatures, you will find great choices in this category. These replicas feature superb attention to detail and craftsmanship and offer features such as working steering system, opening forward compartment, opening rear trunk with removable spare wheel, 4-wheel independent spring suspension, and so on. The models range in size from 1:10 to 1:24 scale and include numerous limited edition and several out-of-production vehicles. All models include a certificate of authenticity from their manufacturers and come fully assembled and ready for display in the home or office.</td>
        </tr>
        <tr>
            <td>3d79931afbc0f719d77cf2039dd2454b</td>
            <td>1958 Setra Bus</td>
            <td>Trucks and Buses</td>
            <td>1:12</td>
            <td>Welly Diecast Productions</td>
            <td>Model features 30 windows, skylights &amp; glare resistant glass, working steering system, original logos</td>
            <td>The Truck and Bus models are realistic replicas of buses and specialized trucks produced from the early 1920s to present. The models range in size from 1:12 to 1:50 scale and include numerous limited edition and several out-of-production vehicles. Materials used include tin, diecast and plastic. All models include a certificate of authenticity from their manufacturers and are a perfect ornament for the home and office.</td>
        </tr>
        <tr>
            <td>a2cea97b93875997fdaf88fde1e3c2d8</td>
            <td>2002 Suzuki XREO</td>
            <td>Motorcycles</td>
            <td>1:12</td>
            <td>Unimax Art Galleries</td>
            <td>Official logos and insignias, saddle bags located on side of motorcycle, detailed engine, working steering, working suspension, two leather seats, luggage rack, dual exhaust pipes, small saddle bag located on handle bars, two-tone paint with chrome accents, superior die-cast detail , rotating wheels , working kick stand, diecast metal with plastic parts and baked enamel finish.</td>
            <td>Our motorcycles are state of the art replicas of classic as well as contemporary motorcycle legends such as Harley Davidson, Ducati and Vespa. Models contain stunning details such as official logos, rotating wheels, working kickstand, front suspension, gear-shift lever, footbrake lever, and drive chain. Materials used include diecast and plastic. The models range in size from 1:10 to 1:50 scale and include numerous limited edition and several out-of-production vehicles. All models come fully assembled and ready for display in the home or office. Most include a certificate of authenticity.</td>
        </tr>
    </tbody>
</table>




```python
%sql SELECT * FROM classicmodels_star_schema.dim_dates LIMIT 10
```

     * postgresql+psycopg2://postgresuser:***@de-c4w4lab1-rds.cd044wq8gkrk.us-east-1.rds.amazonaws.com:5432/postgres
    10 rows affected.





<table>
    <thead>
        <tr>
            <th>date_day</th>
            <th>day_of_week</th>
            <th>day_of_month</th>
            <th>day_of_year</th>
            <th>week_of_year</th>
            <th>month_of_year</th>
            <th>month_name</th>
            <th>quarter_of_year</th>
            <th>year_number</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>2003-01-01</td>
            <td>3</td>
            <td>1.0</td>
            <td>1.0</td>
            <td>1</td>
            <td>1</td>
            <td>January</td>
            <td>1</td>
            <td>2003</td>
        </tr>
        <tr>
            <td>2003-01-02</td>
            <td>4</td>
            <td>2.0</td>
            <td>2.0</td>
            <td>1</td>
            <td>1</td>
            <td>January</td>
            <td>1</td>
            <td>2003</td>
        </tr>
        <tr>
            <td>2003-01-03</td>
            <td>5</td>
            <td>3.0</td>
            <td>3.0</td>
            <td>1</td>
            <td>1</td>
            <td>January</td>
            <td>1</td>
            <td>2003</td>
        </tr>
        <tr>
            <td>2003-01-04</td>
            <td>6</td>
            <td>4.0</td>
            <td>4.0</td>
            <td>1</td>
            <td>1</td>
            <td>January</td>
            <td>1</td>
            <td>2003</td>
        </tr>
        <tr>
            <td>2003-01-05</td>
            <td>7</td>
            <td>5.0</td>
            <td>5.0</td>
            <td>1</td>
            <td>1</td>
            <td>January</td>
            <td>1</td>
            <td>2003</td>
        </tr>
        <tr>
            <td>2003-01-06</td>
            <td>1</td>
            <td>6.0</td>
            <td>6.0</td>
            <td>1</td>
            <td>1</td>
            <td>January</td>
            <td>1</td>
            <td>2003</td>
        </tr>
        <tr>
            <td>2003-01-07</td>
            <td>2</td>
            <td>7.0</td>
            <td>7.0</td>
            <td>1</td>
            <td>1</td>
            <td>January</td>
            <td>1</td>
            <td>2003</td>
        </tr>
        <tr>
            <td>2003-01-08</td>
            <td>3</td>
            <td>8.0</td>
            <td>8.0</td>
            <td>2</td>
            <td>1</td>
            <td>January</td>
            <td>1</td>
            <td>2003</td>
        </tr>
        <tr>
            <td>2003-01-09</td>
            <td>4</td>
            <td>9.0</td>
            <td>9.0</td>
            <td>2</td>
            <td>1</td>
            <td>January</td>
            <td>1</td>
            <td>2003</td>
        </tr>
        <tr>
            <td>2003-01-10</td>
            <td>5</td>
            <td>10.0</td>
            <td>10.0</td>
            <td>2</td>
            <td>1</td>
            <td>January</td>
            <td>1</td>
            <td>2003</td>
        </tr>
    </tbody>
</table>



<a name='2'></a>
## 2 - Views with dbt

Let's review the star schema that you just created, which corresponds to the same schema you created in the first `dbt` lab.
![star_schema](images/star_schema.png)

Based on this schema, you are going to create some views and materialized views to serve your data by answering some business questions and generate a dashboard to visualize the results. First, let's review the definition of views and materialized views.

A **view** is a virtual table based on the result of a SQL query. It does not store the data physically; instead, it provides a way to look at the data from one or more tables. When you query a view, the underlying query is executed, and the result is returned. This means that you will always see up to date data from a view.

A **materialized view** is a database object that contains the results of a query and stores them physically. Unlike regular views, materialized views store the data, and therefore, do not need to query the base tables every time they are accessed. They need to be refreshed periodically to reflect changes in the underlying data. 

In this lab you are going to create 2 views and in order to compare views and materialized views, one of those views will be recreated as a materialized view. Check the following diagram corresponding to the two views that you are going to create:

![views](./images/views.png)

<a name='2.1'></a>
### 2.1 - Annual Sales per Office

The first business query that you will create should answer the question about the annual sales per office in terms of quantity of items sold and the total sales income received.

2.1.1. This is the query which should answer that question. Review the query and run it:


```sql
%%sql 
SELECT 
    DISTINCT fct.office_key
    , dof.city 
    , dof.state 
    , dof.country
    , dof.territory
    , SUM(fct.quantity_ordered) AS total_quantity 
    , sum(fct.quantity_ordered*fct.product_price) as total_price
    , EXTRACT(YEAR FROM fct.order_date) as year
FROM classicmodels_star_schema.fact_orders AS fct
JOIN classicmodels_star_schema.dim_offices AS dof ON dof.office_key=fct.office_key
GROUP BY fct.office_key
    , dof.city
    , dof.state
    , dof.country
    , dof.territory
    , EXTRACT(YEAR FROM fct.order_date)
ORDER BY fct.office_key ASC, year ASC
```

     * postgresql+psycopg2://postgresuser:***@de-c4w4lab1-rds.cd044wq8gkrk.us-east-1.rds.amazonaws.com:5432/postgres
    21 rows affected.





<table>
    <thead>
        <tr>
            <th>office_key</th>
            <th>city</th>
            <th>state</th>
            <th>country</th>
            <th>territory</th>
            <th>total_quantity</th>
            <th>total_price</th>
            <th>year</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>1679091c5a880faf6fb5e6087eb1b2dc</td>
            <td>Sydney</td>
            <td>NSW</td>
            <td>Australia</td>
            <td>APAC</td>
            <td>3529</td>
            <td>304949.11</td>
            <td>2003</td>
        </tr>
        <tr>
            <td>1679091c5a880faf6fb5e6087eb1b2dc</td>
            <td>Sydney</td>
            <td>NSW</td>
            <td>Australia</td>
            <td>APAC</td>
            <td>5938</td>
            <td>542996.02</td>
            <td>2004</td>
        </tr>
        <tr>
            <td>1679091c5a880faf6fb5e6087eb1b2dc</td>
            <td>Sydney</td>
            <td>NSW</td>
            <td>Australia</td>
            <td>APAC</td>
            <td>3411</td>
            <td>299231.22</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>8f14e45fceea167a5a36dedd4bea2543</td>
            <td>London</td>
            <td>None</td>
            <td>UK</td>
            <td>EMEA</td>
            <td>6017</td>
            <td>549551.94</td>
            <td>2003</td>
        </tr>
        <tr>
            <td>8f14e45fceea167a5a36dedd4bea2543</td>
            <td>London</td>
            <td>None</td>
            <td>UK</td>
            <td>EMEA</td>
            <td>7659</td>
            <td>706014.52</td>
            <td>2004</td>
        </tr>
        <tr>
            <td>8f14e45fceea167a5a36dedd4bea2543</td>
            <td>London</td>
            <td>None</td>
            <td>UK</td>
            <td>EMEA</td>
            <td>2015</td>
            <td>181384.24</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>a87ff679a2f3e71d9181a67b7542122c</td>
            <td>Paris</td>
            <td>None</td>
            <td>France</td>
            <td>EMEA</td>
            <td>10694</td>
            <td>969959.90</td>
            <td>2003</td>
        </tr>
        <tr>
            <td>a87ff679a2f3e71d9181a67b7542122c</td>
            <td>Paris</td>
            <td>None</td>
            <td>France</td>
            <td>EMEA</td>
            <td>15971</td>
            <td>1465229.84</td>
            <td>2004</td>
        </tr>
        <tr>
            <td>a87ff679a2f3e71d9181a67b7542122c</td>
            <td>Paris</td>
            <td>None</td>
            <td>France</td>
            <td>EMEA</td>
            <td>7222</td>
            <td>648571.84</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>c4ca4238a0b923820dcc509a6f75849b</td>
            <td>San Francisco</td>
            <td>CA</td>
            <td>USA</td>
            <td>NA</td>
            <td>6151</td>
            <td>532681.13</td>
            <td>2003</td>
        </tr>
        <tr>
            <td>c4ca4238a0b923820dcc509a6f75849b</td>
            <td>San Francisco</td>
            <td>CA</td>
            <td>USA</td>
            <td>NA</td>
            <td>5697</td>
            <td>517408.62</td>
            <td>2004</td>
        </tr>
        <tr>
            <td>c4ca4238a0b923820dcc509a6f75849b</td>
            <td>San Francisco</td>
            <td>CA</td>
            <td>USA</td>
            <td>NA</td>
            <td>4062</td>
            <td>378973.82</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>c81e728d9d4c2f636f067f89cc14862c</td>
            <td>Boston</td>
            <td>MA</td>
            <td>USA</td>
            <td>NA</td>
            <td>3298</td>
            <td>301781.38</td>
            <td>2003</td>
        </tr>
        <tr>
            <td>c81e728d9d4c2f636f067f89cc14862c</td>
            <td>Boston</td>
            <td>MA</td>
            <td>USA</td>
            <td>NA</td>
            <td>5101</td>
            <td>467177.07</td>
            <td>2004</td>
        </tr>
        <tr>
            <td>c81e728d9d4c2f636f067f89cc14862c</td>
            <td>Boston</td>
            <td>MA</td>
            <td>USA</td>
            <td>NA</td>
            <td>1389</td>
            <td>123580.17</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>e4da3b7fbbce2345d7772b0674a318d5</td>
            <td>Tokyo</td>
            <td>Chiyoda-Ku</td>
            <td>Japan</td>
            <td>Japan</td>
            <td>2851</td>
            <td>267249.40</td>
            <td>2003</td>
        </tr>
        <tr>
            <td>e4da3b7fbbce2345d7772b0674a318d5</td>
            <td>Tokyo</td>
            <td>Chiyoda-Ku</td>
            <td>Japan</td>
            <td>Japan</td>
            <td>1692</td>
            <td>151761.45</td>
            <td>2004</td>
        </tr>
        <tr>
            <td>e4da3b7fbbce2345d7772b0674a318d5</td>
            <td>Tokyo</td>
            <td>Chiyoda-Ku</td>
            <td>Japan</td>
            <td>Japan</td>
            <td>380</td>
            <td>38099.22</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>eccbc87e4b5ce2fe28308fd9f2a7baf3</td>
            <td>NYC</td>
            <td>NY</td>
            <td>USA</td>
            <td>NA</td>
            <td>3899</td>
            <td>391175.53</td>
            <td>2003</td>
        </tr>
        <tr>
            <td>eccbc87e4b5ce2fe28308fd9f2a7baf3</td>
            <td>NYC</td>
            <td>NY</td>
            <td>USA</td>
            <td>NA</td>
            <td>7429</td>
            <td>665317.99</td>
            <td>2004</td>
        </tr>
        <tr>
            <td>eccbc87e4b5ce2fe28308fd9f2a7baf3</td>
            <td>NYC</td>
            <td>NY</td>
            <td>USA</td>
            <td>NA</td>
            <td>1111</td>
            <td>101096.20</td>
            <td>2005</td>
        </tr>
    </tbody>
</table>



2.1.2. Create a new folder `analytical_views` located at `./classicmodels_modeling/models/`. Then in that folder create a new file `annual_sells_per_office_view.sql`. Copy the query from the previous step into that file (do not include the `%%sql` line).

2.1.3. At the beginning of this file right before your query, add the following jinja configuration that creates views instead of physical tables:

```
{{
config(
    materialized='view'
    )
}}
```

Don't be confused by the `materialized` key, in this case, this is a `dbt` [concept](https://docs.getdbt.com/docs/build/materializations) regarding the strategy on how the models will be persisted into the destination database. In this particular case, this specifies that the model should be materialized as a view (different from a materialized view) in the database.

2.1.4. Exchange the `classicmodels_star_schema` with the jinja templating string `{{var("star_schema")}}` (in two places). You will end with `{{var("star_schema")}}.<TABLE_NAME>` for each table in your query. This line will use jinja templating to take the value stored in the `star_schema` variable and will replace it with the value `classicmodels_star_schema` which is the database that hosts your new star schema data model.

Save changes to the file.

2.1.5. Create a new `schema.yml` file in the `./classicmodels_modeling/models/analytical_views/`folder. To set the schema for the view `annual_sells_per_office_view`, copy the following into the file and save changes:

```yml
version: 2

models:
  - name: annual_sells_per_office_view
    description: "Annual sells per office view"
    columns:
      - name: office_code        
      - name: city
      - name: state
      - name: country
      - name: territory
      - name: total_quantity
      - name: total_price
      - name: year
```

2.1.6. Open the `./classicmodels_modeling/dbt_project.yml` file, and at the bottom of the file add the following key:

```yml
analytical_views:
  +materialized: view
  +schema: star_schema
```

This also ensures that no physical tables are created but only materialized views and that they will be created in the schema named `star_schema`.

<a name='2.2'></a>
### 2.2 - Average Sales per Product Line

Now you've got a business question about the average sales (in terms of units and price) of each product line per month and year. 

2.2.1. This is the query which should answer that question. Review the query and run it:


```sql
%%sql 
SELECT 
    dp.product_line
    , AVG(fct.quantity_ordered) AS avg_quantity 
    , AVG(fct.quantity_ordered*fct.product_price) AS avg_price
    , EXTRACT(MONTH FROM fct.order_date) AS month
    , EXTRACT(YEAR FROM fct.order_date) AS year 
FROM classicmodels_star_schema.fact_orders AS fct
JOIN classicmodels_star_schema.dim_products AS dp ON dp.product_key = fct.product_key
GROUP BY dp.product_line
    , EXTRACT(MONTH FROM fct.order_date)
    , EXTRACT(YEAR FROM fct.order_date)
ORDER BY
    dp.product_line ASC    
    , month ASC
    , year ASC
LIMIT 10
```

     * postgresql+psycopg2://postgresuser:***@de-c4w4lab1-rds.cd044wq8gkrk.us-east-1.rds.amazonaws.com:5432/postgres
    10 rows affected.





<table>
    <thead>
        <tr>
            <th>product_line</th>
            <th>avg_quantity</th>
            <th>avg_price</th>
            <th>month</th>
            <th>year</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Classic Cars</td>
            <td>33.4000000000000000</td>
            <td>3655.2330000000000000</td>
            <td>1</td>
            <td>2003</td>
        </tr>
        <tr>
            <td>Classic Cars</td>
            <td>35.7666666666666667</td>
            <td>3892.1016666666666667</td>
            <td>1</td>
            <td>2004</td>
        </tr>
        <tr>
            <td>Classic Cars</td>
            <td>35.0789473684210526</td>
            <td>3703.4450000000000000</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Classic Cars</td>
            <td>40.0000000000000000</td>
            <td>6313.6800000000000000</td>
            <td>2</td>
            <td>2003</td>
        </tr>
        <tr>
            <td>Classic Cars</td>
            <td>34.7878787878787879</td>
            <td>3775.2809090909090909</td>
            <td>2</td>
            <td>2004</td>
        </tr>
        <tr>
            <td>Classic Cars</td>
            <td>35.5789473684210526</td>
            <td>3913.0457894736842105</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Classic Cars</td>
            <td>35.7307692307692308</td>
            <td>3734.1607692307692308</td>
            <td>3</td>
            <td>2003</td>
        </tr>
        <tr>
            <td>Classic Cars</td>
            <td>40.8823529411764706</td>
            <td>4802.2782352941176471</td>
            <td>3</td>
            <td>2004</td>
        </tr>
        <tr>
            <td>Classic Cars</td>
            <td>35.4814814814814815</td>
            <td>3833.0974074074074074</td>
            <td>3</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Classic Cars</td>
            <td>38.7500000000000000</td>
            <td>4795.4350000000000000</td>
            <td>4</td>
            <td>2003</td>
        </tr>
    </tbody>
</table>



2.2.2. In the folder `./classicmodels_modeling/models/analytical_views/` create a new file `avg_sells_per_product_line_view.sql`. Copy the query from the previous step into that file (do not include the lines `%%sql` and `LIMIT 10`).

2.2.3. At the beginning of this file right before your query, add the following jinja configuration that creates views instead of physical tables:

```
{{
config(
    materialized='view'
    )
}}
```

2.2.4. Exchange the `classicmodels_star_schema` with the jinja templating string `{{var("star_schema")}}` (in two places). Save changes.

2.2.5. In the `./classicmodels_modeling/models/analytical_views/schema.yml` file add the schema for the view `avg_sells_per_product_line_view`:

```yml
  - name: avg_sells_per_product_line_view
    description: "Average sells per product lind view"
    columns:
      - name: product_line        
      - name: avg_quantity
      - name: avg_price
      - name: month
      - name: year
```

Save changes.

<a name='2.3'></a>
### 2.3 - Running Analytical Views

In order to run the analytical views that you just created.

2.3.1. Get back to your `dbt` project folder `classicmodels_modeling` run the analytical view:

*Note*: You may need to reactivate the environment:

```bash
source jupyterlab-venv/bin/activate
```

```bash
cd classicmodels_modeling
dbt run -s analytical_views
```

You should see an output similar to this one:

![dbt_create_views](./images/dbt_create_views.png)

2.3.2. The views will be created at the `classicmodels_star_schema` database, so you can use the following scripts to check that they were populated:


```sql
%%sql
SELECT COUNT(*) FROM classicmodels_star_schema.annual_sells_per_office_view;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w4lab1-rds.cd044wq8gkrk.us-east-1.rds.amazonaws.com:5432/postgres
    1 rows affected.





<table>
    <thead>
        <tr>
            <th>count</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>21</td>
        </tr>
    </tbody>
</table>




```sql
%%sql
SELECT * FROM classicmodels_star_schema.annual_sells_per_office_view order by year desc;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w4lab1-rds.cd044wq8gkrk.us-east-1.rds.amazonaws.com:5432/postgres
    21 rows affected.





<table>
    <thead>
        <tr>
            <th>office_key</th>
            <th>city</th>
            <th>state</th>
            <th>country</th>
            <th>territory</th>
            <th>total_quantity</th>
            <th>total_price</th>
            <th>year</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>eccbc87e4b5ce2fe28308fd9f2a7baf3</td>
            <td>NYC</td>
            <td>NY</td>
            <td>USA</td>
            <td>NA</td>
            <td>1111</td>
            <td>101096.20</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>a87ff679a2f3e71d9181a67b7542122c</td>
            <td>Paris</td>
            <td>None</td>
            <td>France</td>
            <td>EMEA</td>
            <td>7222</td>
            <td>648571.84</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>c81e728d9d4c2f636f067f89cc14862c</td>
            <td>Boston</td>
            <td>MA</td>
            <td>USA</td>
            <td>NA</td>
            <td>1389</td>
            <td>123580.17</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>c4ca4238a0b923820dcc509a6f75849b</td>
            <td>San Francisco</td>
            <td>CA</td>
            <td>USA</td>
            <td>NA</td>
            <td>4062</td>
            <td>378973.82</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>1679091c5a880faf6fb5e6087eb1b2dc</td>
            <td>Sydney</td>
            <td>NSW</td>
            <td>Australia</td>
            <td>APAC</td>
            <td>3411</td>
            <td>299231.22</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>8f14e45fceea167a5a36dedd4bea2543</td>
            <td>London</td>
            <td>None</td>
            <td>UK</td>
            <td>EMEA</td>
            <td>2015</td>
            <td>181384.24</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>e4da3b7fbbce2345d7772b0674a318d5</td>
            <td>Tokyo</td>
            <td>Chiyoda-Ku</td>
            <td>Japan</td>
            <td>Japan</td>
            <td>380</td>
            <td>38099.22</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>c4ca4238a0b923820dcc509a6f75849b</td>
            <td>San Francisco</td>
            <td>CA</td>
            <td>USA</td>
            <td>NA</td>
            <td>5697</td>
            <td>517408.62</td>
            <td>2004</td>
        </tr>
        <tr>
            <td>1679091c5a880faf6fb5e6087eb1b2dc</td>
            <td>Sydney</td>
            <td>NSW</td>
            <td>Australia</td>
            <td>APAC</td>
            <td>5938</td>
            <td>542996.02</td>
            <td>2004</td>
        </tr>
        <tr>
            <td>8f14e45fceea167a5a36dedd4bea2543</td>
            <td>London</td>
            <td>None</td>
            <td>UK</td>
            <td>EMEA</td>
            <td>7659</td>
            <td>706014.52</td>
            <td>2004</td>
        </tr>
        <tr>
            <td>a87ff679a2f3e71d9181a67b7542122c</td>
            <td>Paris</td>
            <td>None</td>
            <td>France</td>
            <td>EMEA</td>
            <td>15971</td>
            <td>1465229.84</td>
            <td>2004</td>
        </tr>
        <tr>
            <td>c81e728d9d4c2f636f067f89cc14862c</td>
            <td>Boston</td>
            <td>MA</td>
            <td>USA</td>
            <td>NA</td>
            <td>5101</td>
            <td>467177.07</td>
            <td>2004</td>
        </tr>
        <tr>
            <td>e4da3b7fbbce2345d7772b0674a318d5</td>
            <td>Tokyo</td>
            <td>Chiyoda-Ku</td>
            <td>Japan</td>
            <td>Japan</td>
            <td>1692</td>
            <td>151761.45</td>
            <td>2004</td>
        </tr>
        <tr>
            <td>eccbc87e4b5ce2fe28308fd9f2a7baf3</td>
            <td>NYC</td>
            <td>NY</td>
            <td>USA</td>
            <td>NA</td>
            <td>7429</td>
            <td>665317.99</td>
            <td>2004</td>
        </tr>
        <tr>
            <td>c4ca4238a0b923820dcc509a6f75849b</td>
            <td>San Francisco</td>
            <td>CA</td>
            <td>USA</td>
            <td>NA</td>
            <td>6151</td>
            <td>532681.13</td>
            <td>2003</td>
        </tr>
        <tr>
            <td>e4da3b7fbbce2345d7772b0674a318d5</td>
            <td>Tokyo</td>
            <td>Chiyoda-Ku</td>
            <td>Japan</td>
            <td>Japan</td>
            <td>2851</td>
            <td>267249.40</td>
            <td>2003</td>
        </tr>
        <tr>
            <td>8f14e45fceea167a5a36dedd4bea2543</td>
            <td>London</td>
            <td>None</td>
            <td>UK</td>
            <td>EMEA</td>
            <td>6017</td>
            <td>549551.94</td>
            <td>2003</td>
        </tr>
        <tr>
            <td>a87ff679a2f3e71d9181a67b7542122c</td>
            <td>Paris</td>
            <td>None</td>
            <td>France</td>
            <td>EMEA</td>
            <td>10694</td>
            <td>969959.90</td>
            <td>2003</td>
        </tr>
        <tr>
            <td>1679091c5a880faf6fb5e6087eb1b2dc</td>
            <td>Sydney</td>
            <td>NSW</td>
            <td>Australia</td>
            <td>APAC</td>
            <td>3529</td>
            <td>304949.11</td>
            <td>2003</td>
        </tr>
        <tr>
            <td>c81e728d9d4c2f636f067f89cc14862c</td>
            <td>Boston</td>
            <td>MA</td>
            <td>USA</td>
            <td>NA</td>
            <td>3298</td>
            <td>301781.38</td>
            <td>2003</td>
        </tr>
        <tr>
            <td>eccbc87e4b5ce2fe28308fd9f2a7baf3</td>
            <td>NYC</td>
            <td>NY</td>
            <td>USA</td>
            <td>NA</td>
            <td>3899</td>
            <td>391175.53</td>
            <td>2003</td>
        </tr>
    </tbody>
</table>




```sql
%%sql
SELECT COUNT(*) FROM classicmodels_star_schema.avg_sells_per_product_line_view;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w4lab1-rds.cd044wq8gkrk.us-east-1.rds.amazonaws.com:5432/postgres
    1 rows affected.





<table>
    <thead>
        <tr>
            <th>count</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>182</td>
        </tr>
    </tbody>
</table>




```sql
%%sql
SELECT * FROM classicmodels_star_schema.avg_sells_per_product_line_view order by year desc, month asc LIMIT 20;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w4lab1-rds.cd044wq8gkrk.us-east-1.rds.amazonaws.com:5432/postgres
    20 rows affected.





<table>
    <thead>
        <tr>
            <th>product_line</th>
            <th>avg_quantity</th>
            <th>avg_price</th>
            <th>month</th>
            <th>year</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Trucks and Buses</td>
            <td>30.6363636363636364</td>
            <td>2961.0381818181818182</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Ships</td>
            <td>35.5555555555555556</td>
            <td>2695.2244444444444444</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Planes</td>
            <td>35.0000000000000000</td>
            <td>2569.7620000000000000</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Classic Cars</td>
            <td>35.0789473684210526</td>
            <td>3703.4450000000000000</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Vintage Cars</td>
            <td>35.1818181818181818</td>
            <td>2841.6240909090909091</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Trains</td>
            <td>26.3333333333333333</td>
            <td>1753.6266666666666667</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Motorcycles</td>
            <td>34.2727272727272727</td>
            <td>2686.5681818181818182</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Motorcycles</td>
            <td>33.0000000000000000</td>
            <td>2985.6361538461538462</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Classic Cars</td>
            <td>35.5789473684210526</td>
            <td>3913.0457894736842105</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Ships</td>
            <td>34.0000000000000000</td>
            <td>2743.3666666666666667</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Planes</td>
            <td>38.5714285714285714</td>
            <td>3219.5900000000000000</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Trains</td>
            <td>36.0000000000000000</td>
            <td>2161.5600000000000000</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Trucks and Buses</td>
            <td>32.3636363636363636</td>
            <td>3011.4427272727272727</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Vintage Cars</td>
            <td>35.2727272727272727</td>
            <td>2695.6990909090909091</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Trucks and Buses</td>
            <td>36.0000000000000000</td>
            <td>3239.5972727272727273</td>
            <td>3</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Trains</td>
            <td>33.0000000000000000</td>
            <td>2163.2300000000000000</td>
            <td>3</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Motorcycles</td>
            <td>39.4615384615384615</td>
            <td>3386.0776923076923077</td>
            <td>3</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Classic Cars</td>
            <td>35.4814814814814815</td>
            <td>3833.0974074074074074</td>
            <td>3</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Planes</td>
            <td>36.7916666666666667</td>
            <td>2846.5420833333333333</td>
            <td>3</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Ships</td>
            <td>36.3333333333333333</td>
            <td>2702.4400000000000000</td>
            <td>3</td>
            <td>2005</td>
        </tr>
    </tbody>
</table>



<a name='2.4'></a>
### 2.4 - Creating Materialized View

Up to this moment, you have created views. Remember that those views are virtual tables that do not store data physically. Let's take the last view and create a materialized view so we can compare how these two materialization strategies work in a database. 

2.4.1. Take the file `./classicmodels_modeling/models/analytical_views/avg_sells_per_product_line_view.sql`, copy it and rename as `avg_sells_per_product_line_mv.sql`. Open this new file and change the configuration to 

```
{{
    config(
        materialized='materialized_view',
        on_configuration_change = 'apply',
    )
}}
```

Take a look at the value of the `materialized` key. This value indicates that the materialization strategy will create an actual materialized view, which actually stores data physically. 

Save changes.

2.4.2. Open the `./classicmodels_modeling/models/analytical_views/schema.yml` file and add a schema named `avg_sells_per_product_line_mv` for this materialized view:

```yml
  - name: avg_sells_per_product_line_mv
    description: "Average sells per product line materialized view"
    columns:
      - name: product_line        
      - name: avg_quantity
      - name: avg_price
      - name: month
      - name: year
```

Save changes.

2.4.3. Finally, run again your `dbt` process with 

```
dbt run -s analytical_views
```

*Note:* Remember that in the `dbt_project` file, you set this configuration:

```
analytical_views:
    +materialized: view
    +schema: star_schema
```

Although this configuration specifies that the materialization strategy is a `view`, the configuration that you set at the `avg_sells_per_product_line_mv.sql` file overwrites this configuration to create a materialized view.

2.4.4. Run this command to check that the data has been successfully loaded into the materialized view:


```sql
%%sql
SELECT COUNT(*) FROM classicmodels_star_schema.avg_sells_per_product_line_mv;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w4lab1-rds.cd044wq8gkrk.us-east-1.rds.amazonaws.com:5432/postgres
    1 rows affected.





<table>
    <thead>
        <tr>
            <th>count</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>182</td>
        </tr>
    </tbody>
</table>




```sql
%%sql
SELECT * FROM classicmodels_star_schema.avg_sells_per_product_line_mv order by year desc, month asc LIMIT 20;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w4lab1-rds.cd044wq8gkrk.us-east-1.rds.amazonaws.com:5432/postgres
    20 rows affected.





<table>
    <thead>
        <tr>
            <th>product_line</th>
            <th>avg_quantity</th>
            <th>avg_price</th>
            <th>month</th>
            <th>year</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Trucks and Buses</td>
            <td>30.6363636363636364</td>
            <td>2961.0381818181818182</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Ships</td>
            <td>35.5555555555555556</td>
            <td>2695.2244444444444444</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Planes</td>
            <td>35.0000000000000000</td>
            <td>2569.7620000000000000</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Classic Cars</td>
            <td>35.0789473684210526</td>
            <td>3703.4450000000000000</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Vintage Cars</td>
            <td>35.1818181818181818</td>
            <td>2841.6240909090909091</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Trains</td>
            <td>26.3333333333333333</td>
            <td>1753.6266666666666667</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Motorcycles</td>
            <td>34.2727272727272727</td>
            <td>2686.5681818181818182</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Motorcycles</td>
            <td>33.0000000000000000</td>
            <td>2985.6361538461538462</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Classic Cars</td>
            <td>35.5789473684210526</td>
            <td>3913.0457894736842105</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Ships</td>
            <td>34.0000000000000000</td>
            <td>2743.3666666666666667</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Planes</td>
            <td>38.5714285714285714</td>
            <td>3219.5900000000000000</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Trains</td>
            <td>36.0000000000000000</td>
            <td>2161.5600000000000000</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Trucks and Buses</td>
            <td>32.3636363636363636</td>
            <td>3011.4427272727272727</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Vintage Cars</td>
            <td>35.2727272727272727</td>
            <td>2695.6990909090909091</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Trucks and Buses</td>
            <td>36.0000000000000000</td>
            <td>3239.5972727272727273</td>
            <td>3</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Trains</td>
            <td>33.0000000000000000</td>
            <td>2163.2300000000000000</td>
            <td>3</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Motorcycles</td>
            <td>39.4615384615384615</td>
            <td>3386.0776923076923077</td>
            <td>3</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Classic Cars</td>
            <td>35.4814814814814815</td>
            <td>3833.0974074074074074</td>
            <td>3</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Planes</td>
            <td>36.7916666666666667</td>
            <td>2846.5420833333333333</td>
            <td>3</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Ships</td>
            <td>36.3333333333333333</td>
            <td>2702.4400000000000000</td>
            <td>3</td>
            <td>2005</td>
        </tr>
    </tbody>
</table>



Now, it is the time to actually understand the difference between views and materialized views. Given that materialized views store data physically, they need to be refreshed when the underlying tables are updated. On the other hand, as views require the execution of the underlying query, they will always present up-to-date data.

2.4.5. Let's insert some mock data into the `fact_orders` table and see how it affects the views and materialized views. Execute the following cell to insert the data. Take a look at the dates, as all of them are in the year `2006` while the maximum year we have in our database currently is `2005`.


```sql
%%sql
SELECT MAX(EXTRACT(YEAR FROM fct.order_date))
FROM classicmodels_star_schema.fact_orders fct;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w4lab1-rds.cd044wq8gkrk.us-east-1.rds.amazonaws.com:5432/postgres
    1 rows affected.





<table>
    <thead>
        <tr>
            <th>max</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>2005</td>
        </tr>
    </tbody>
</table>




```sql
%%sql
INSERT INTO classicmodels_star_schema.fact_orders (fact_order_key, customer_key, employee_key, office_key, product_key, order_date, order_required_date, order_shipped_date, quantity_ordered, product_price) VALUES ('9eec411e690b55dafeb3ec3393aa6d57', '7d04bbbe5494ae9d2f5a76aa1c00fa2f', '4671aeaf49c792689533b00664a5c3ef', 'eccbc87e4b5ce2fe28308fd9f2a7baf3', '296efc252c7855537b5d9e6015bf42b8', '2006-06-01 00:00:00', '2006-07-01 00:00:00', '2006-06-15 00:00:00', 41, 83.79);
INSERT INTO classicmodels_star_schema.fact_orders (fact_order_key, customer_key, employee_key, office_key, product_key, order_date, order_required_date, order_shipped_date, quantity_ordered, product_price) VALUES ('f485cfdd94901e9e237dcc3f644f7edc', '7d04bbbe5494ae9d2f5a76aa1c00fa2f', '4671aeaf49c792689533b00664a5c3ef', 'eccbc87e4b5ce2fe28308fd9f2a7baf3', '8bff119b349bf271ef0684a15808ea18', '2006-06-01 00:00:00', '2006-07-01 00:00:00', '2006-06-15 00:00:00', 11, 50.32);
INSERT INTO classicmodels_star_schema.fact_orders (fact_order_key, customer_key, employee_key, office_key, product_key, order_date, order_required_date, order_shipped_date, quantity_ordered, product_price) VALUES ('7eecd924b84c4a03fcb69d5ec6df4670', '0f28b5d49b3020afeecd95b4009adf4c', 'd1ee59e20ad01cedc15f5118a7626099', 'a87ff679a2f3e71d9181a67b7542122c', '99733605e1ea651ec564248e05f77741', '2006-06-02 00:00:00', '2006-06-21 00:00:00', '2006-06-07 00:00:00', 18, 94.92 );
```

     * postgresql+psycopg2://postgresuser:***@de-c4w4lab1-rds.cd044wq8gkrk.us-east-1.rds.amazonaws.com:5432/postgres
    1 rows affected.
    1 rows affected.
    1 rows affected.





    []



2.4.6. Now that you have inserted the data, query again the views. Remember that `annual_sells_per_office_view` had 21 rows while `avg_sells_per_product_line_view` had 182 rows before the update.


```sql
%%sql
SELECT COUNT(*) FROM classicmodels_star_schema.annual_sells_per_office_view;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w4lab1-rds.cd044wq8gkrk.us-east-1.rds.amazonaws.com:5432/postgres
    1 rows affected.





<table>
    <thead>
        <tr>
            <th>count</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>23</td>
        </tr>
    </tbody>
</table>




```sql
%%sql
SELECT * FROM classicmodels_star_schema.annual_sells_per_office_view order by year desc;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w4lab1-rds.cd044wq8gkrk.us-east-1.rds.amazonaws.com:5432/postgres
    23 rows affected.





<table>
    <thead>
        <tr>
            <th>office_key</th>
            <th>city</th>
            <th>state</th>
            <th>country</th>
            <th>territory</th>
            <th>total_quantity</th>
            <th>total_price</th>
            <th>year</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>eccbc87e4b5ce2fe28308fd9f2a7baf3</td>
            <td>NYC</td>
            <td>NY</td>
            <td>USA</td>
            <td>NA</td>
            <td>52</td>
            <td>3988.91</td>
            <td>2006</td>
        </tr>
        <tr>
            <td>a87ff679a2f3e71d9181a67b7542122c</td>
            <td>Paris</td>
            <td>None</td>
            <td>France</td>
            <td>EMEA</td>
            <td>18</td>
            <td>1708.56</td>
            <td>2006</td>
        </tr>
        <tr>
            <td>c81e728d9d4c2f636f067f89cc14862c</td>
            <td>Boston</td>
            <td>MA</td>
            <td>USA</td>
            <td>NA</td>
            <td>1389</td>
            <td>123580.17</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>c4ca4238a0b923820dcc509a6f75849b</td>
            <td>San Francisco</td>
            <td>CA</td>
            <td>USA</td>
            <td>NA</td>
            <td>4062</td>
            <td>378973.82</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>1679091c5a880faf6fb5e6087eb1b2dc</td>
            <td>Sydney</td>
            <td>NSW</td>
            <td>Australia</td>
            <td>APAC</td>
            <td>3411</td>
            <td>299231.22</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>8f14e45fceea167a5a36dedd4bea2543</td>
            <td>London</td>
            <td>None</td>
            <td>UK</td>
            <td>EMEA</td>
            <td>2015</td>
            <td>181384.24</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>eccbc87e4b5ce2fe28308fd9f2a7baf3</td>
            <td>NYC</td>
            <td>NY</td>
            <td>USA</td>
            <td>NA</td>
            <td>1111</td>
            <td>101096.20</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>a87ff679a2f3e71d9181a67b7542122c</td>
            <td>Paris</td>
            <td>None</td>
            <td>France</td>
            <td>EMEA</td>
            <td>7222</td>
            <td>648571.84</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>e4da3b7fbbce2345d7772b0674a318d5</td>
            <td>Tokyo</td>
            <td>Chiyoda-Ku</td>
            <td>Japan</td>
            <td>Japan</td>
            <td>380</td>
            <td>38099.22</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>c4ca4238a0b923820dcc509a6f75849b</td>
            <td>San Francisco</td>
            <td>CA</td>
            <td>USA</td>
            <td>NA</td>
            <td>5697</td>
            <td>517408.62</td>
            <td>2004</td>
        </tr>
        <tr>
            <td>1679091c5a880faf6fb5e6087eb1b2dc</td>
            <td>Sydney</td>
            <td>NSW</td>
            <td>Australia</td>
            <td>APAC</td>
            <td>5938</td>
            <td>542996.02</td>
            <td>2004</td>
        </tr>
        <tr>
            <td>8f14e45fceea167a5a36dedd4bea2543</td>
            <td>London</td>
            <td>None</td>
            <td>UK</td>
            <td>EMEA</td>
            <td>7659</td>
            <td>706014.52</td>
            <td>2004</td>
        </tr>
        <tr>
            <td>a87ff679a2f3e71d9181a67b7542122c</td>
            <td>Paris</td>
            <td>None</td>
            <td>France</td>
            <td>EMEA</td>
            <td>15971</td>
            <td>1465229.84</td>
            <td>2004</td>
        </tr>
        <tr>
            <td>c81e728d9d4c2f636f067f89cc14862c</td>
            <td>Boston</td>
            <td>MA</td>
            <td>USA</td>
            <td>NA</td>
            <td>5101</td>
            <td>467177.07</td>
            <td>2004</td>
        </tr>
        <tr>
            <td>e4da3b7fbbce2345d7772b0674a318d5</td>
            <td>Tokyo</td>
            <td>Chiyoda-Ku</td>
            <td>Japan</td>
            <td>Japan</td>
            <td>1692</td>
            <td>151761.45</td>
            <td>2004</td>
        </tr>
        <tr>
            <td>eccbc87e4b5ce2fe28308fd9f2a7baf3</td>
            <td>NYC</td>
            <td>NY</td>
            <td>USA</td>
            <td>NA</td>
            <td>7429</td>
            <td>665317.99</td>
            <td>2004</td>
        </tr>
        <tr>
            <td>e4da3b7fbbce2345d7772b0674a318d5</td>
            <td>Tokyo</td>
            <td>Chiyoda-Ku</td>
            <td>Japan</td>
            <td>Japan</td>
            <td>2851</td>
            <td>267249.40</td>
            <td>2003</td>
        </tr>
        <tr>
            <td>a87ff679a2f3e71d9181a67b7542122c</td>
            <td>Paris</td>
            <td>None</td>
            <td>France</td>
            <td>EMEA</td>
            <td>10694</td>
            <td>969959.90</td>
            <td>2003</td>
        </tr>
        <tr>
            <td>c4ca4238a0b923820dcc509a6f75849b</td>
            <td>San Francisco</td>
            <td>CA</td>
            <td>USA</td>
            <td>NA</td>
            <td>6151</td>
            <td>532681.13</td>
            <td>2003</td>
        </tr>
        <tr>
            <td>eccbc87e4b5ce2fe28308fd9f2a7baf3</td>
            <td>NYC</td>
            <td>NY</td>
            <td>USA</td>
            <td>NA</td>
            <td>3899</td>
            <td>391175.53</td>
            <td>2003</td>
        </tr>
        <tr>
            <td>c81e728d9d4c2f636f067f89cc14862c</td>
            <td>Boston</td>
            <td>MA</td>
            <td>USA</td>
            <td>NA</td>
            <td>3298</td>
            <td>301781.38</td>
            <td>2003</td>
        </tr>
        <tr>
            <td>8f14e45fceea167a5a36dedd4bea2543</td>
            <td>London</td>
            <td>None</td>
            <td>UK</td>
            <td>EMEA</td>
            <td>6017</td>
            <td>549551.94</td>
            <td>2003</td>
        </tr>
        <tr>
            <td>1679091c5a880faf6fb5e6087eb1b2dc</td>
            <td>Sydney</td>
            <td>NSW</td>
            <td>Australia</td>
            <td>APAC</td>
            <td>3529</td>
            <td>304949.11</td>
            <td>2003</td>
        </tr>
    </tbody>
</table>




```sql
%%sql
SELECT COUNT(*) FROM classicmodels_star_schema.avg_sells_per_product_line_view;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w4lab1-rds.cd044wq8gkrk.us-east-1.rds.amazonaws.com:5432/postgres
    1 rows affected.





<table>
    <thead>
        <tr>
            <th>count</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>183</td>
        </tr>
    </tbody>
</table>




```sql
%%sql
SELECT * FROM classicmodels_star_schema.avg_sells_per_product_line_view order by year desc, month asc LIMIT 20;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w4lab1-rds.cd044wq8gkrk.us-east-1.rds.amazonaws.com:5432/postgres
    20 rows affected.





<table>
    <thead>
        <tr>
            <th>product_line</th>
            <th>avg_quantity</th>
            <th>avg_price</th>
            <th>month</th>
            <th>year</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Trucks and Buses</td>
            <td>23.3333333333333333</td>
            <td>1899.1566666666666667</td>
            <td>6</td>
            <td>2006</td>
        </tr>
        <tr>
            <td>Trains</td>
            <td>26.3333333333333333</td>
            <td>1753.6266666666666667</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Vintage Cars</td>
            <td>35.1818181818181818</td>
            <td>2841.6240909090909091</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Planes</td>
            <td>35.0000000000000000</td>
            <td>2569.7620000000000000</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Classic Cars</td>
            <td>35.0789473684210526</td>
            <td>3703.4450000000000000</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Trucks and Buses</td>
            <td>30.6363636363636364</td>
            <td>2961.0381818181818182</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Ships</td>
            <td>35.5555555555555556</td>
            <td>2695.2244444444444444</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Motorcycles</td>
            <td>34.2727272727272727</td>
            <td>2686.5681818181818182</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Classic Cars</td>
            <td>35.5789473684210526</td>
            <td>3913.0457894736842105</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Planes</td>
            <td>38.5714285714285714</td>
            <td>3219.5900000000000000</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Ships</td>
            <td>34.0000000000000000</td>
            <td>2743.3666666666666667</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Vintage Cars</td>
            <td>35.2727272727272727</td>
            <td>2695.6990909090909091</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Trains</td>
            <td>36.0000000000000000</td>
            <td>2161.5600000000000000</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Motorcycles</td>
            <td>33.0000000000000000</td>
            <td>2985.6361538461538462</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Trucks and Buses</td>
            <td>32.3636363636363636</td>
            <td>3011.4427272727272727</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Trucks and Buses</td>
            <td>36.0000000000000000</td>
            <td>3239.5972727272727273</td>
            <td>3</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Trains</td>
            <td>33.0000000000000000</td>
            <td>2163.2300000000000000</td>
            <td>3</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Motorcycles</td>
            <td>39.4615384615384615</td>
            <td>3386.0776923076923077</td>
            <td>3</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Classic Cars</td>
            <td>35.4814814814814815</td>
            <td>3833.0974074074074074</td>
            <td>3</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Planes</td>
            <td>36.7916666666666667</td>
            <td>2846.5420833333333333</td>
            <td>3</td>
            <td>2005</td>
        </tr>
    </tbody>
</table>



2.4.7. Finally, let's query the materialized view. What can you see?


```sql
%%sql
SELECT COUNT(*) FROM classicmodels_star_schema.avg_sells_per_product_line_mv;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w4lab1-rds.cd044wq8gkrk.us-east-1.rds.amazonaws.com:5432/postgres
    1 rows affected.





<table>
    <thead>
        <tr>
            <th>count</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>182</td>
        </tr>
    </tbody>
</table>




```sql
%%sql
SELECT * FROM classicmodels_star_schema.avg_sells_per_product_line_mv order by year desc, month asc LIMIT 20;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w4lab1-rds.cd044wq8gkrk.us-east-1.rds.amazonaws.com:5432/postgres
    20 rows affected.





<table>
    <thead>
        <tr>
            <th>product_line</th>
            <th>avg_quantity</th>
            <th>avg_price</th>
            <th>month</th>
            <th>year</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Trucks and Buses</td>
            <td>30.6363636363636364</td>
            <td>2961.0381818181818182</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Ships</td>
            <td>35.5555555555555556</td>
            <td>2695.2244444444444444</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Planes</td>
            <td>35.0000000000000000</td>
            <td>2569.7620000000000000</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Classic Cars</td>
            <td>35.0789473684210526</td>
            <td>3703.4450000000000000</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Vintage Cars</td>
            <td>35.1818181818181818</td>
            <td>2841.6240909090909091</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Trains</td>
            <td>26.3333333333333333</td>
            <td>1753.6266666666666667</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Motorcycles</td>
            <td>34.2727272727272727</td>
            <td>2686.5681818181818182</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Motorcycles</td>
            <td>33.0000000000000000</td>
            <td>2985.6361538461538462</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Classic Cars</td>
            <td>35.5789473684210526</td>
            <td>3913.0457894736842105</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Ships</td>
            <td>34.0000000000000000</td>
            <td>2743.3666666666666667</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Planes</td>
            <td>38.5714285714285714</td>
            <td>3219.5900000000000000</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Trains</td>
            <td>36.0000000000000000</td>
            <td>2161.5600000000000000</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Trucks and Buses</td>
            <td>32.3636363636363636</td>
            <td>3011.4427272727272727</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Vintage Cars</td>
            <td>35.2727272727272727</td>
            <td>2695.6990909090909091</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Trucks and Buses</td>
            <td>36.0000000000000000</td>
            <td>3239.5972727272727273</td>
            <td>3</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Trains</td>
            <td>33.0000000000000000</td>
            <td>2163.2300000000000000</td>
            <td>3</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Motorcycles</td>
            <td>39.4615384615384615</td>
            <td>3386.0776923076923077</td>
            <td>3</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Classic Cars</td>
            <td>35.4814814814814815</td>
            <td>3833.0974074074074074</td>
            <td>3</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Planes</td>
            <td>36.7916666666666667</td>
            <td>2846.5420833333333333</td>
            <td>3</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Ships</td>
            <td>36.3333333333333333</td>
            <td>2702.4400000000000000</td>
            <td>3</td>
            <td>2005</td>
        </tr>
    </tbody>
</table>



When querying the materialized view, you can see that you get the same number of rows as before the update to the `fact_orders` table. In order to refresh this materialized view, you should run again the `dbt` model. Do it with the command

```
dbt run -s analytical_views
```

You will see that the materialized view has been refreshed:

![dbt_refresh_views](./images/dbt_refresh_views.png)

Finally, query again your materialized view to see the difference. 



```sql
%%sql
SELECT COUNT(*) FROM classicmodels_star_schema.avg_sells_per_product_line_mv;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w4lab1-rds.cd044wq8gkrk.us-east-1.rds.amazonaws.com:5432/postgres
    1 rows affected.





<table>
    <thead>
        <tr>
            <th>count</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>183</td>
        </tr>
    </tbody>
</table>




```sql
%%sql
SELECT * FROM classicmodels_star_schema.avg_sells_per_product_line_mv order by year desc, month asc LIMIT 20;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w4lab1-rds.cd044wq8gkrk.us-east-1.rds.amazonaws.com:5432/postgres
    20 rows affected.





<table>
    <thead>
        <tr>
            <th>product_line</th>
            <th>avg_quantity</th>
            <th>avg_price</th>
            <th>month</th>
            <th>year</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Trucks and Buses</td>
            <td>23.3333333333333333</td>
            <td>1899.1566666666666667</td>
            <td>6</td>
            <td>2006</td>
        </tr>
        <tr>
            <td>Trains</td>
            <td>26.3333333333333333</td>
            <td>1753.6266666666666667</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Vintage Cars</td>
            <td>35.1818181818181818</td>
            <td>2841.6240909090909091</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Planes</td>
            <td>35.0000000000000000</td>
            <td>2569.7620000000000000</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Classic Cars</td>
            <td>35.0789473684210526</td>
            <td>3703.4450000000000000</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Trucks and Buses</td>
            <td>30.6363636363636364</td>
            <td>2961.0381818181818182</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Ships</td>
            <td>35.5555555555555556</td>
            <td>2695.2244444444444444</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Motorcycles</td>
            <td>34.2727272727272727</td>
            <td>2686.5681818181818182</td>
            <td>1</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Classic Cars</td>
            <td>35.5789473684210526</td>
            <td>3913.0457894736842105</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Planes</td>
            <td>38.5714285714285714</td>
            <td>3219.5900000000000000</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Ships</td>
            <td>34.0000000000000000</td>
            <td>2743.3666666666666667</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Vintage Cars</td>
            <td>35.2727272727272727</td>
            <td>2695.6990909090909091</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Trains</td>
            <td>36.0000000000000000</td>
            <td>2161.5600000000000000</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Motorcycles</td>
            <td>33.0000000000000000</td>
            <td>2985.6361538461538462</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Trucks and Buses</td>
            <td>32.3636363636363636</td>
            <td>3011.4427272727272727</td>
            <td>2</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Trucks and Buses</td>
            <td>36.0000000000000000</td>
            <td>3239.5972727272727273</td>
            <td>3</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Trains</td>
            <td>33.0000000000000000</td>
            <td>2163.2300000000000000</td>
            <td>3</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Motorcycles</td>
            <td>39.4615384615384615</td>
            <td>3386.0776923076923077</td>
            <td>3</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Classic Cars</td>
            <td>35.4814814814814815</td>
            <td>3833.0974074074074074</td>
            <td>3</td>
            <td>2005</td>
        </tr>
        <tr>
            <td>Planes</td>
            <td>36.7916666666666667</td>
            <td>2846.5420833333333333</td>
            <td>3</td>
            <td>2005</td>
        </tr>
    </tbody>
</table>



With that exercise, you can notice the difference between a view and a materialized view. You may be wondering when you should use one or the other and you can use these paragraphs as a hint:

- Views: Use when you need a simple way to encapsulate complex queries, enhance security by exposing only certain data, or provide a simplified interface to the underlying tables. Ideal for frequently changing data where up-to-the-moment accuracy is essential.

- Materialized Views: Use when you need to improve performance for complex, resource-intensive queries. Ideal for reporting and data warehousing scenarios where data does not need to be up-to-the-second accurate, and where the performance gain from precomputed results outweighs the need for real-time data.

<a name='3'></a>
## 3 - Dashboard with Apache Superset

*Note*:Apache Superset takes around 15 to 20 minutes to load from the start of the lab, if you don't see the interface when entering the URL in a new tab, wait a while and refresh the page.

3.1. The EC2 instance has been set up for you to work with Apache Superset, the URL is among the CloudFormation Outputs. Access the Superset UI using the URL provided in the CloudFormation Outputs (take the value for the key `SupersetEndpoint`), you should see a login screen like this:

![superset_ui](images/superset_ui.png)

3.2. Login using the following credentials:

- user: `admin`
- password: `admin`

3.3. Configure the Postgres connection. Click on the dropdown **Settings** menu in the top right, and under the Data section select **Database Connections**. Click on the top right `+ Database` button, a new menu should appear to configure the new connection:

![superset_conf](images/superset_conf.png)

Select `PostgreSQL` and click Next. Fill out the details using the same connection parameters as the ones found in the `./scripts/profiles.yml`. The details for the connection are also can be printed out:


```python
print(DBCONFIG)
```

After filling out the details, click on **Connect** button, this should have created a new connection in the `Data Connections` section. Click on **Finish** button.

3.4. Now, select the **Datasets** tab in the top header menu. You will be directed to a page with various example datasets. Click on `+ DATASET` button on the top right, a new screen will appear, you can use the connection that you just configured for Postgres, then select the `classicmodels_star_schema` and finally one of the views:

![superset_dataset](images/superset_dataset.png)

3.5. Click on the `CREATE DATASET AND CREATE CHART` button (in the bottom right), you will be directed to a new page to create a chart based on the dataset. You can select the type of chart and what variable is used for each dimension.

![superset_chart](images/superset_chart.png)

Once you are done with the chart, hit the **Save** button on the top right, it will ask you to give the chart a name and then save it. Create a chart for each view then create a new dashboard in the **Dashboards** section of the top navigational header, using the `+ Dashboard` button. Enter a name (in the top left part) for your dashboard and then drag and drop the charts you created earlier onto the dashboard canvas, Resize and arrange the charts as desired to create your dashboard layout and finally click Save to save your dashboard layout.

![superset_dashboard](images/superset_dashboard.png)

In this lab, you focused on data visualization using various types of views and a dashboard tool. Effective visual communication is crucial for presenting your findings and the results of your data pipelines to potential stakeholders. Although this task aligns more with the role of a data analyst, it is essential to understand their responsibilities and how we can supply them with the necessary data for their work.
