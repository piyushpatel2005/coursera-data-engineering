# Data Modeling with DBT

During this week's assignment, you will learn how to model a dataset based on two multi-dimensional data models such as the Star Schema and One Big Table (OBT).

# Table of Contents

- [ 1 - Introduction and Setup](#1)
  - [ 1.1 - Initiating dbt 101 Project](#1.1)
  - [ 1.2 - Source Configuration](#1.2)
- [ 2 - Modeling](#2)
- [ 3 - Star Schema](#3)
  - [ 3.1 - Description of the Approach](#3.1)
  - [ 3.2 - Creating the Facts Table](#3.2)
  - [ 3.3 - Creating the Customers Dimension Table](#3.3)
  - [ 3.4 - Creating the Employees Dimension Table](#3.4)
  - [ 3.5 - Creating the Office Dimension Table](#3.5)
  - [ 3.6 - Creating the Product Dimension Table](#3.6)
  - [ 3.7 - Creating the Date Dimension Table](#3.7)
  - [ 3.8 - Running the Star Schema Model](#3.8)
- [ 4 - One Big Table (OBT)](#4)
- [ 5 - Performing Tests over the Data in the New Models](#5)
- [ 6 - Upload Files for Grading](#6)

Please, load the required SQL model.


```python
%load_ext sql

LAB_PREFIX='de-c4w1a1'
```

<a name='1'></a>
## 1 - Introduction and Setup

Data modeling is one of the pillars of Data Engineering, it involves organizing bits of data into defined models with their respective data types and relationships between each other. Most of the work in data modeling involves using predefined techniques or patterns on a raw dataset based on the business's requirements. Data models like the **Star Schema** and **One Big Table (OBT)** have become popular for analytical workloads in recent years. In this lab, you will apply these models to the `classicmodels` dataset.

<a name='1.1'></a>
### 1.1 - Initiating **dbt 101** Project

**dbt** is a transformation workflow command line tool based on SQL, it consists of a compiler and a runner. A user writes `dbt` files and then can invoke `dbt` to run these files on the data warehouse of their choice. The compiler converts the `dbt` files into raw SQL scripts and runs them for you.

Let's start a `dbt` project.

*Note*:<span style="color:red"> All terminal commands in this lab should be run in the Cloud9 terminal, not Jupyter, as it may cause some issues.</span>

1.1.1. Activate the Python virtual environment for the lab. Run the following command in the Cloud9 terminal:

```bash
source lab-venv/bin/activate
```    

1.1.2. Check that `dbt` Core is installed.

```bash
dbt --version
```

1.1.3. Initiate the `classicmodels_modeling` project with the `init` command:

```bash
dbt init classicmodels_modeling
```

Select the `postgres` database by pressing `1` and then `Enter` when prompted to. After that you will be prompted to enter other values, but you should quit that with `Cmd + C` or `Ctrl + C` as you will configure the rest of the connection details later. Check that the folder `classicmodels_modeling` will be created.

1.1.4. You need to reactivate the Python virtual environment again with the command

```bash
source lab-venv/bin/activate
```

1.1.5. Copy the `packages.yml` file to the project folder:

```bash
cp ./scripts/packages.yml ./classicmodels_modeling/
```   

1.1.6. Navigate into your project's directory:

```bash
cd classicmodels_modeling
```

1.1.7. Run the following command from the `classicmodels_modeling` folder to fetch the latest stable versions of tools and libraries specified in the `packages.yml` file.

```bash
dbt deps
```

1.1.8. Open the main configuration file for the project `./classicmodels_modeling/dbt_project.yml`. Go through the comments in that file to understand its content.

<a name='1.2'></a>
### 1.2 - Source Configuration

When developing with `dbt Core`, `dbt` connects to your data warehouse using a profile, which is a `YAML` file with all the connection details to your warehouse. You are going to use a Postgres database.

1.2.1. Go to **CloudFormation** in the AWS console. You will see two stacks deployed, one associated with your Cloud9 environment (name with prefix `aws-cloud9`) and another named with an alphanumeric ID. Click on the alphanumeric ID stack and search for the **Outputs** tab. You will see the key `PostgresEndpoint`, copy the corresponding **Value**. 

1.2.2. Open the file located at `./scripts/profiles.yml`. Replace the placeholders `<DATABASE_ENDPOINT>` with the endpoint value. Save changes.

1.2.3. Assuming you are already inside the `classicmodels_modeling` folder in the terminal, run the following command to copy the `profiles.yml` file to the invisible folder `.dbt` of the project:

```bash
cp ../scripts/profiles.yml ~/.dbt/profiles.yml 
```

1.2.4. Test the connection with the following command:

```bash
dbt debug
```

It should return a `Connection test: OK connection ok` at the end of the output.

1.2.5. Load the connection configuration into the notebook with the following cell:


```python
import yaml

with open("./scripts/profiles.yml", 'r') as stream:
    data_loaded = yaml.safe_load(stream)
    
DBCONFIG = data_loaded["classicmodels_modeling"]["outputs"]["dev"]
DBHOST = DBCONFIG["host"]
DBPORT = int(DBCONFIG["port"])
DBNAME = DBCONFIG["dbname"]
DBUSER = DBCONFIG["user"]
DBPASSWORD = DBCONFIG["password"]
db_connection_url = f'postgresql+psycopg2://{DBUSER}:{DBPASSWORD}@{DBHOST}:{DBPORT}/{DBNAME}'

%sql {db_connection_url}
```

<a name='2'></a>
## 2 - Modeling

Inside the `classicmodels_modeling` project folder, you have the `models` folder, which contains an example of a model definition. Let's explore it.

2.1. Open `./classicmodels_modeling/models/example/schema.yml` file and go through its contents. The file contains a version in the header and then a list of models. For each model, you will need to give a name, a description and a list of columns. For each column, you can also add a description and some tests to verify constraints such as a unique value check and that no value is `NULL`.

2.2. Open `my_first_dbt_model.sql` file from the same folder and have a look at the SQL code. In the first line of the model's script, you could override the project 
configuration and personalize the model configuration. In this case this model will be materialized as a table instead of a view. After that a model is based on a `SELECT` statement over the source data, in this particular case it uses a `CTE` to create some sample data. But you could just write a query that uses the connector to bring data from the data warehouse.

2.3. Have a look at another example of the model:

```sql
SELECT 
    {{ dbt_utils.generate_surrogate_key(['employeeNumber']) }} as employee_key, 
    employees.lastName as employee_last_name, 
    employees.firstName as employee_first_name, 
    employees.jobTitle as job_title, 
    employees.email as email
FROM classicmodels.employees
```

This is an example of a model based on the Employees' table in `classicmodels`. Here you are using the function `generate_surrogate_key` from `dbt_utils` to create a surrogate key based on the natural key `employeeNumber`. This is a good practice in data modeling because natural keys in your production data might change, or they could cause issues with your data models. For that reason, it is better to substitute natural keys and to perform the joins between dimension tables and fact tables with surrogate keys.

<a name='2.4'></a>
2.4. Now that you have familiarized yourself with the examples, create two new subfolders in the `models` folder inside the project: `star_schema` and `obt`. You can also delete the `example` subfolder.

```bash
mkdir -p models/star_schema
mkdir -p models/obt
rm -rf models/example
```

<a name='3'></a>
## 3 - Star Schema

<a name='3.1'></a>
### 3.1 - Description of the Approach

**A star schema** is composed of **fact** tables (containing an identifier, numerical measures and foreign keys) and dimensional tables. You are going to expand upon the star schema you used back in Course 1 Week 2 and implement the improved star schema as a `dbt` model in the project. 

Let's remember the Entity Relationship Diagram (ERD) for [`classicmodels`](https://www.mysqltutorial.org/mysql-sample-database.aspx):

![erm](images/erm.png)

Verify the tables are loaded into the source database in Postgres:


```sql
%%sql
SELECT * FROM information_schema.tables 
WHERE table_schema = 'classicmodels'
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1a1-rds.cnyk6684iouz.us-east-1.rds.amazonaws.com:5432/postgres
    8 rows affected.





<table>
    <thead>
        <tr>
            <th>table_catalog</th>
            <th>table_schema</th>
            <th>table_name</th>
            <th>table_type</th>
            <th>self_referencing_column_name</th>
            <th>reference_generation</th>
            <th>user_defined_type_catalog</th>
            <th>user_defined_type_schema</th>
            <th>user_defined_type_name</th>
            <th>is_insertable_into</th>
            <th>is_typed</th>
            <th>commit_action</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>postgres</td>
            <td>classicmodels</td>
            <td>employees</td>
            <td>BASE TABLE</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>YES</td>
            <td>NO</td>
            <td>None</td>
        </tr>
        <tr>
            <td>postgres</td>
            <td>classicmodels</td>
            <td>offices</td>
            <td>BASE TABLE</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>YES</td>
            <td>NO</td>
            <td>None</td>
        </tr>
        <tr>
            <td>postgres</td>
            <td>classicmodels</td>
            <td>customers</td>
            <td>BASE TABLE</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>YES</td>
            <td>NO</td>
            <td>None</td>
        </tr>
        <tr>
            <td>postgres</td>
            <td>classicmodels</td>
            <td>orderdetails</td>
            <td>BASE TABLE</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>YES</td>
            <td>NO</td>
            <td>None</td>
        </tr>
        <tr>
            <td>postgres</td>
            <td>classicmodels</td>
            <td>productlines</td>
            <td>BASE TABLE</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>YES</td>
            <td>NO</td>
            <td>None</td>
        </tr>
        <tr>
            <td>postgres</td>
            <td>classicmodels</td>
            <td>products</td>
            <td>BASE TABLE</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>YES</td>
            <td>NO</td>
            <td>None</td>
        </tr>
        <tr>
            <td>postgres</td>
            <td>classicmodels</td>
            <td>orders</td>
            <td>BASE TABLE</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>YES</td>
            <td>NO</td>
            <td>None</td>
        </tr>
        <tr>
            <td>postgres</td>
            <td>classicmodels</td>
            <td>payments</td>
            <td>BASE TABLE</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>YES</td>
            <td>NO</td>
            <td>None</td>
        </tr>
    </tbody>
</table>



You will follow the four steps proposed in the book [The Data Warehouse Toolkit](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/books/data-warehouse-dw-toolkit/) by Ralph Kimball and Margy Ross. The steps are the following:
- Select the Business process.
- Declare the Granularity of your data.
- Identify the Dimensions Tables.
- Identify the Facts.

Let's briefly describe each of those steps:

**Select the Business process**

The original ERM of the `classicmodels` database is where the company, a specialist retailer in scale model toys, draws its data from. The most important business activity for this company is the sales of their products captured in the orders placed by customers, the business process you will model.

**Declare the Granularity of your data**

Each order contains some details that appear in the `orderdetails` table. A customer can place an order for one or more product items. The `orderNumber` field in the `orderdetails` table together with the `productCode` links a product to the order; and the granularity of your model would allow access to product information for each item on that order.

**Identify the dimensions**

It is important for a business to hold information about its customers, and the employees who serve the customer, their branches/offices and the products sold. These data would shed insights into the business’s performance. So, let’s create dimensions tables in your start schema with those aspects:

- Customers Dimension
- Employees Dimension
- Offices Dimension
- Products Dimension

**Identify the Facts**

For each order placed by a customer, the unit price and quantity of a product ordered are important as they are used to calculate the sale total of this single order. Hence, this information from the `orderdetails` table should be included as facts in the fact table.

Under the considerations stated in the four-step process to develop the star schema the idea is that you will implement the following model to your data:

![star_schema](images/star_schema.png)

In this star schema, you have identified the orders table and order details as the primary tables for modeling, as they contain a business-critical process that involves **facts** such as transaction amounts and quantities. The dimensional tables related to the fact table are customers, products, employees and offices. You can examine and perform aggregations to the fact table on either or multiples of these dimensions.

Now, it's your turn to implement the proposed data model. 

<a name='3.2'></a>
### 3.2 - Creating the Facts Table

3.2.1. Review the query that extracts the data for the fact table.


```sql
%%sql
SELECT 
    orders.orderNumber, orderdetails.orderLineNumber,
    customers.customerNumber AS customer_key, 
    employees.employeeNumber AS employee_key,
    offices.officeCode AS office_key,
    productCode AS product_key, 
    orders.orderDate AS order_date,
    orders.requiredDate AS order_required_date, 
    orders.shippedDate AS order_shipped_date,
    orderdetails.quantityOrdered AS quantity_ordered, 
    orderdetails.priceEach AS product_price
FROM classicmodels.orders
JOIN classicmodels.orderdetails ON orders.orderNumber = orderdetails.orderNumber
JOIN classicmodels.customers ON orders.customerNumber = customers.customerNumber
JOIN classicmodels.employees ON customers.salesRepEmployeeNumber = employees.employeeNumber
JOIN classicmodels.offices ON employees.officeCode = offices.officeCode
LIMIT 5
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1a1-rds.cnyk6684iouz.us-east-1.rds.amazonaws.com:5432/postgres
    5 rows affected.





<table>
    <thead>
        <tr>
            <th>ordernumber</th>
            <th>orderlinenumber</th>
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
            <td>10100</td>
            <td>3</td>
            <td>363</td>
            <td>1216</td>
            <td>2</td>
            <td>S18_1749</td>
            <td>2003-01-06 00:00:00</td>
            <td>2003-01-13 00:00:00</td>
            <td>2003-01-10 00:00:00</td>
            <td>30</td>
            <td>136</td>
        </tr>
        <tr>
            <td>10100</td>
            <td>2</td>
            <td>363</td>
            <td>1216</td>
            <td>2</td>
            <td>S18_2248</td>
            <td>2003-01-06 00:00:00</td>
            <td>2003-01-13 00:00:00</td>
            <td>2003-01-10 00:00:00</td>
            <td>50</td>
            <td>55.09</td>
        </tr>
        <tr>
            <td>10100</td>
            <td>4</td>
            <td>363</td>
            <td>1216</td>
            <td>2</td>
            <td>S18_4409</td>
            <td>2003-01-06 00:00:00</td>
            <td>2003-01-13 00:00:00</td>
            <td>2003-01-10 00:00:00</td>
            <td>22</td>
            <td>75.46</td>
        </tr>
        <tr>
            <td>10100</td>
            <td>1</td>
            <td>363</td>
            <td>1216</td>
            <td>2</td>
            <td>S24_3969</td>
            <td>2003-01-06 00:00:00</td>
            <td>2003-01-13 00:00:00</td>
            <td>2003-01-10 00:00:00</td>
            <td>49</td>
            <td>35.29</td>
        </tr>
        <tr>
            <td>10101</td>
            <td>4</td>
            <td>128</td>
            <td>1504</td>
            <td>7</td>
            <td>S18_2325</td>
            <td>2003-01-09 00:00:00</td>
            <td>2003-01-18 00:00:00</td>
            <td>2003-01-11 00:00:00</td>
            <td>25</td>
            <td>108.06</td>
        </tr>
    </tbody>
</table>



3.2.2. Now you will need to create the `dbt` model for the `fact_orders` table. Open the `./classicmodels_modeling/dbt_project.yml` file and paste the following in the new line after `version: '1.0.0'`:

```yml
vars:
  source_schema: classicmodels
  star_schema: classicmodels_star_schema
  surrogate_key_treat_nulls_as_empty_strings: true
  "dbt_date:time_zone": "America/Los_Angeles"
```

This is for creation of some [variables](https://docs.getdbt.com/reference/dbt-jinja-functions/var) that can be used throughout your `dbt` models during compilation.

3.2.3. Find the key `classicmodels_modeling` at the end of the file (nested under the `models` key). Delete the nested key `example`, which is the following two lines:

```yml
    example:
      +materialized: view
```

Then add the following nested key instead:

```yml
    star_schema:
      +materialized: table
      +schema: star_schema
```

Save changes.

3.2.4. Go to the folder `./classicmodels_modeling/models/star_schema/` (which was created at step [2.4](#2.4)) and create an SQL file named `fact_orders.sql`.

3.2.5 Copy the previous query for the fact table (without the `%%sql` and `LIMIT` clause) and paste it into a new file located at `fact_orders.sql`. Make the following changes:

- Replace every appearance of `classicmodels` with `{{var("source_schema")}}` (in 5 places). Each table reference in your query should now be in the format `{{var("source_schema")}}.<TABLE_NAME>`. This will use jinja templating to dynamically replace `source_schema` with the actual schema name, which is currently `classicmodels`.
- Replace the default key columns with surrogate keys using the `{{ dbt_utils.generate_surrogate_key(['']) }}` function. This function accepts an array of column names to generate the surrogate keys:
    * Replace `orders.orderNumber, orderdetails.orderLineNumber` with `{{ dbt_utils.generate_surrogate_key(['orders.orderNumber', 'orderdetails.orderLineNumber']) }} as fact_order_key`.
    * Replace `Replace customers.customerNumber with:` with `{{ dbt_utils.generate_surrogate_key(['customers.customerNumber']) }}`.
    * Do the same for `employees.employeeNumber`, `offices.officeCode` and `productCode`.

Save changes.

3.2.6. Copy the file located at `./scripts/schema.yml` into `./classicmodels_modeling/models/star_schema/` folder:

```bash
cp ../scripts/schema.yml ./models/star_schema/schema.yml
```

Open the `schema.yml` file. You will see that it is partially filled for you with the schema definition for the `fact_orders` and `dim_customers` tables.

With that, you have created the model for the fact table `fact_orders`. Before you run the model against the database to create the tables, you need to create the dimension tables. The process to create the models for the dimension tables will be similar to what you did.

<a name='3.3'></a>
### 3.3 - Creating the Customers Dimension Table

3.3.1. Here is the query to create the dimension table `dim_customers`. The complete output has 122 rows, you will use `LIMIT` to avoid extracting too many rows in the preview.


```sql
%%sql
SELECT 
    customerNumber as customer_key, 
    customerName as customer_name,   
    contactLastName as customer_last_name, 
    contactFirstName as customer_first_name, 
    phone as phone, 
    addressLine1 as address_line_1, 
    addressLine2 as address_line_2, 
    postalCode as postal_code, 
    city as city, 
    state as state, 
    country as country,
    creditLimit as credit_limit
FROM classicmodels.customers
LIMIT 5
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1a1-rds.cnyk6684iouz.us-east-1.rds.amazonaws.com:5432/postgres
    5 rows affected.





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
            <th>credit_limit</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>103</td>
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
            <td>112</td>
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
            <td>114</td>
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
            <td>119</td>
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
            <td>121</td>
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
    </tbody>
</table>



Follow the same process to create this part in the model. 

3.3.2. Go to the folder `./classicmodels_modeling/models/star_schema/` and create an SQL file `dim_customers.sql`.

3.3.3. Copy the previous query without the `%%sql` and `LIMIT` clause, paste it into the new file `dim_customers.sql`. Make the following changes in the file:

- Replace `classicmodels` with `{{var("source_schema")}}` (in 1 place). The table reference now is in the format `{{var("source_schema")}}.<TABLE_NAME>`. 
- Replace `customerNumber` with `{{ dbt_utils.generate_surrogate_key(['customerNumber']) }}` to generate the surrogate key.

Save changes.


3.3.4. Remember that the `schema.yml` file has been already configured for the `dim_customers` table, but notice that for this table, you will find the following:

```yml
- name: customer_key
    description: The primary key for this table
    data_tests:
      - unique
      - not_null
```

This is the syntax to create tests over your columns. You will use this later.

<a name='3.4'></a>
### 3.4 - Creating the Employees Dimension Table

3.4.1. Here is the query to create the dimension table `dim_employees`. You will use a `LIMIT` to avoid extracting too many rows. The complete output has 23 rows.


```sql
%%sql
SELECT
    employeeNumber as employee_key,
    lastName as employee_last_name, 
    firstName as employee_first_name, 
    jobTitle as job_title, 
    email as email
FROM classicmodels.employees
LIMIT 5
```

3.4.2. Go to the folder `./classicmodels_modeling/models/star_schema/` and create an SQL file `dim_employees.sql`.

3.4.3. Copy the previous query without the `%%sql` and `LIMIT` clause, and paste it into the new file `dim_employees.sql`. Make the following changes in the file:

- Replace `classicmodels` with `{{var("source_schema")}}` (in 1 place).
- Replace `employeeNumber` with `{{ dbt_utils.generate_surrogate_key(['employeeNumber']) }}` to generate the surrogate key.

Save changes.

3.4.4. Open the `schema.yml` file and based on the `dim_customers` schema, create the schema for the `dim_employees` table. The `employee_key` should be the primary key for this table, so you can set the same tests as in `dim_customers`. Make sure to use the appropriate column names.

<a name='3.5'></a>
### 3.5 - Creating the Office Dimension Table

3.5.1. This is the query to create the dimension table `dim_offices`.


```sql
%%sql
SELECT 
    officeCode as office_key, 
    postalCode as postal_code, 
    city as city, 
    state as state, 
    country as country, 
    territory as territory
FROM classicmodels.offices
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1a1-rds.cnyk6684iouz.us-east-1.rds.amazonaws.com:5432/postgres
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
            <td>1</td>
            <td>94080</td>
            <td>San Francisco</td>
            <td>CA</td>
            <td>USA</td>
            <td>NA</td>
        </tr>
        <tr>
            <td>2</td>
            <td>02107</td>
            <td>Boston</td>
            <td>MA</td>
            <td>USA</td>
            <td>NA</td>
        </tr>
        <tr>
            <td>3</td>
            <td>10022</td>
            <td>NYC</td>
            <td>NY</td>
            <td>USA</td>
            <td>NA</td>
        </tr>
        <tr>
            <td>4</td>
            <td>75017</td>
            <td>Paris</td>
            <td>None</td>
            <td>France</td>
            <td>EMEA</td>
        </tr>
        <tr>
            <td>5</td>
            <td>102-8578</td>
            <td>Tokyo</td>
            <td>Chiyoda-Ku</td>
            <td>Japan</td>
            <td>Japan</td>
        </tr>
        <tr>
            <td>6</td>
            <td>2010</td>
            <td>Sydney</td>
            <td>NSW</td>
            <td>Australia</td>
            <td>APAC</td>
        </tr>
        <tr>
            <td>7</td>
            <td>EC2N 1HN</td>
            <td>London</td>
            <td>None</td>
            <td>UK</td>
            <td>EMEA</td>
        </tr>
    </tbody>
</table>



3.5.2. Go to the folder `./classicmodels_modeling/models/star_schema/` and create an SQL file `dim_offices.sql`.

3.5.3. Copy the previous query, paste it into the new file `dim_offices.sql`. Make the following changes in the file:

- Replace `classicmodels` with `{{var("source_schema")}}` (in 1 place).
- Replace `officeCode` with `{{ dbt_utils.generate_surrogate_key(['officeCode']) }}` to generate the surrogate key.

Save changes.

3.5.4. Open the `schema.yml` file and based on the `dim_customers` schema, create the schema for the `dim_offices` table. The `office_key` should be the primary key for this table, so you can set the same tests as in `dim_customers`. Make sure to use the appropriate column names.

<a name='3.6'></a>
### 3.6 - Creating the Product Dimension Table

3.6.1. This is the query to create the dimension table `dim_products`. Use `LIMIT` as the total output has 110 rows.


```sql
%%sql
SELECT 
    productCode as product_key, 
    productName as product_name, 
    products.productLine as product_line, 
    productScale as product_scale, 
    productVendor as product_vendor,
    productDescription as product_description, 
    textDescription as product_line_description
FROM classicmodels.products
JOIN classicmodels.productlines ON products.productLine=productlines.productLine
LIMIT 3
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1a1-rds.cnyk6684iouz.us-east-1.rds.amazonaws.com:5432/postgres
    3 rows affected.





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
            <td>S10_1678</td>
            <td>1969 Harley Davidson Ultimate Chopper</td>
            <td>Motorcycles</td>
            <td>1:10</td>
            <td>Min Lin Diecast</td>
            <td>This replica features working kickstand, front suspension, gear-shift lever, footbrake lever, drive chain, wheels and steering. All parts are particularly delicate due to their precise scale and require special care and attention.</td>
            <td>Our motorcycles are state of the art replicas of classic as well as contemporary motorcycle legends such as Harley Davidson, Ducati and Vespa. Models contain stunning details such as official logos, rotating wheels, working kickstand, front suspension, gear-shift lever, footbrake lever, and drive chain. Materials used include diecast and plastic. The models range in size from 1:10 to 1:50 scale and include numerous limited edition and several out-of-production vehicles. All models come fully assembled and ready for display in the home or office. Most include a certificate of authenticity.</td>
        </tr>
        <tr>
            <td>S10_1949</td>
            <td>1952 Alpine Renault 1300</td>
            <td>Classic Cars</td>
            <td>1:10</td>
            <td>Classic Metal Creations</td>
            <td>Turnable front wheels; steering function; detailed interior; detailed engine; opening hood; opening trunk; opening doors; and detailed chassis.</td>
            <td>Attention car enthusiasts: Make your wildest car ownership dreams come true. Whether you are looking for classic muscle cars, dream sports cars or movie-inspired miniatures, you will find great choices in this category. These replicas feature superb attention to detail and craftsmanship and offer features such as working steering system, opening forward compartment, opening rear trunk with removable spare wheel, 4-wheel independent spring suspension, and so on. The models range in size from 1:10 to 1:24 scale and include numerous limited edition and several out-of-production vehicles. All models include a certificate of authenticity from their manufacturers and come fully assembled and ready for display in the home or office.</td>
        </tr>
        <tr>
            <td>S10_2016</td>
            <td>1996 Moto Guzzi 1100i</td>
            <td>Motorcycles</td>
            <td>1:10</td>
            <td>Highway 66 Mini Classics</td>
            <td>Official Moto Guzzi logos and insignias, saddle bags located on side of motorcycle, detailed engine, working steering, working suspension, two leather seats, luggage rack, dual exhaust pipes, small saddle bag located on handle bars, two-tone paint with chrome accents, superior die-cast detail , rotating wheels , working kick stand, diecast metal with plastic parts and baked enamel finish.</td>
            <td>Our motorcycles are state of the art replicas of classic as well as contemporary motorcycle legends such as Harley Davidson, Ducati and Vespa. Models contain stunning details such as official logos, rotating wheels, working kickstand, front suspension, gear-shift lever, footbrake lever, and drive chain. Materials used include diecast and plastic. The models range in size from 1:10 to 1:50 scale and include numerous limited edition and several out-of-production vehicles. All models come fully assembled and ready for display in the home or office. Most include a certificate of authenticity.</td>
        </tr>
    </tbody>
</table>



3.6.2. Create an SQL file `dim_products.sql` in the folder `./classicmodels_modeling/models/star_schema/`.

3.6.3. Copy the previous query, paste it into the new file `dim_products.sql`. Make the following changes in the file:

- Replace `classicmodels` with `{{var("source_schema")}}` (in 2 places).
- Replace `productCode` with `{{ dbt_utils.generate_surrogate_key(['productCode']) }}` to generate the surrogate key.

Save changes.

3.6.4. Open the `schema.yml` file and based on the `dim_customers` schema, create the schema for the `dim_products` table. The `product_key` should be the primary key for this table, so you can set the same tests as in `dim_customers`. Make sure to use the appropriate column names.

<a name='3.7'></a>
### 3.7 - Creating the Date Dimension Table

As you may know, time is one of the most important dimensions in star schemas, for this case, you will limit the time dimension to the dates that appear in the `orders` table. Generating this dimension can be cumbersome, so you are going to make use of the `dbt_date` package to generate the date dimension.

3.7.1. Create a `dates.sql` model file in the `./classicmodels_modeling/models/star_schema/` folder.

3.7.2. Inside of it, add the line to call the `get_date_dimension` function from the `dbt_date` package. This function takes an initial and final date, for `classicmodels` the dates are between the start of 2003 and the end of 2005. Here is the format of the function call:

```sql
{{ dbt_date.get_date_dimension("YYYY-MM-DD", "YYYY-MM-DD") }}
```

3.7.3. Create a `dim_dates.sql` model file in the `./classicmodels_modeling/models/star_schema/` folder.

3.7.4. In `dim_dates.sql` write the following SQL query to select required columns from the `date_dimension` model:

```sql
SELECT
    date_day,
    day_of_week,
    day_of_month,
    day_of_year,
    week_of_year,
    month_of_year,
    month_name,
    quarter_of_year,
    year_number
FROM
    date_dimension d
```

To access the `date` model, add a CTE statement prior to that `SELECT` statement (at the start of the file):

```sql
with date_dimension as (
    select * from {{ ref('dates') }}
)
```

Save changes to the file.

3.7.5. Open the `schema.yml` file and add the following schema for the `dim_dates` table:

```yml
  - name: dim_dates
    columns:
      - name: date_day
        description: The primary key for this table
        data_tests:
          - unique
          - not_null
      - name: day_of_week
      - name: day_of_month
      - name: day_of_year
      - name: week_of_year
      - name: month_of_year
      - name: month_name
      - name: quarter_of_year
      - name: year_number
```

<a name='3.8'></a>
### 3.8 - Running the Star Schema Model

Once you have created all the models for your star schema, it is time to run `dbt` against your database to create the proposed star schema. 

3.8.1. In the `Cloud9` terminal where you have activated the Python environment, make sure to set the `dbt` project folder as your working directory:

```bash
cd /home/ec2-user/environment/classicmodels_modeling
```

3.8.2. Once you are in the `~/environment/classicmodels_modeling` folder in Cloud9 terminal, then run `dbt` with the following command:

```bash
dbt run -s star_schema
```

This should run your models and perform the creation and population of the tables in a new database named `classicmodels_star_schema` that resides in the same RDS server. Given that you are going to create several models with `dbt`, the `-s` (or `--select`) option allows you to select the particular data model that you want to run. 

3.8.7. Now, it is time to check if the tables were created and populated. Run the next cell to change the connection to the `classicmodels_star_schema` database:


```sql
%%sql
SELECT * FROM information_schema.tables 
WHERE table_schema = 'classicmodels_star_schema'
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1a1-rds.cnyk6684iouz.us-east-1.rds.amazonaws.com:5432/postgres
    7 rows affected.





<table>
    <thead>
        <tr>
            <th>table_catalog</th>
            <th>table_schema</th>
            <th>table_name</th>
            <th>table_type</th>
            <th>self_referencing_column_name</th>
            <th>reference_generation</th>
            <th>user_defined_type_catalog</th>
            <th>user_defined_type_schema</th>
            <th>user_defined_type_name</th>
            <th>is_insertable_into</th>
            <th>is_typed</th>
            <th>commit_action</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>postgres</td>
            <td>classicmodels_star_schema</td>
            <td>dim_customers</td>
            <td>BASE TABLE</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>YES</td>
            <td>NO</td>
            <td>None</td>
        </tr>
        <tr>
            <td>postgres</td>
            <td>classicmodels_star_schema</td>
            <td>dim_employees</td>
            <td>BASE TABLE</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>YES</td>
            <td>NO</td>
            <td>None</td>
        </tr>
        <tr>
            <td>postgres</td>
            <td>classicmodels_star_schema</td>
            <td>dim_offices</td>
            <td>BASE TABLE</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>YES</td>
            <td>NO</td>
            <td>None</td>
        </tr>
        <tr>
            <td>postgres</td>
            <td>classicmodels_star_schema</td>
            <td>dim_products</td>
            <td>BASE TABLE</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>YES</td>
            <td>NO</td>
            <td>None</td>
        </tr>
        <tr>
            <td>postgres</td>
            <td>classicmodels_star_schema</td>
            <td>fact_orders</td>
            <td>BASE TABLE</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>YES</td>
            <td>NO</td>
            <td>None</td>
        </tr>
        <tr>
            <td>postgres</td>
            <td>classicmodels_star_schema</td>
            <td>dates</td>
            <td>BASE TABLE</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>YES</td>
            <td>NO</td>
            <td>None</td>
        </tr>
        <tr>
            <td>postgres</td>
            <td>classicmodels_star_schema</td>
            <td>dim_dates</td>
            <td>BASE TABLE</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>YES</td>
            <td>NO</td>
            <td>None</td>
        </tr>
    </tbody>
</table>



And count the number of rows in each table to verify that they were populated:


```python
%sql SELECT count(*) FROM classicmodels_star_schema.fact_orders;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1a1-rds.cnyk6684iouz.us-east-1.rds.amazonaws.com:5432/postgres
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



##### __Expected Output__

| **count** |
| --------- |
| 2996     |



```python
%sql SELECT count(*) FROM classicmodels_star_schema.dim_customers;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1a1-rds.cnyk6684iouz.us-east-1.rds.amazonaws.com:5432/postgres
    1 rows affected.





<table>
    <thead>
        <tr>
            <th>count</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>122</td>
        </tr>
    </tbody>
</table>



##### __Expected Output__

| **count** |
| --------- |
| 122       |


```python
%sql SELECT count(*) FROM classicmodels_star_schema.dim_employees;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1a1-rds.cnyk6684iouz.us-east-1.rds.amazonaws.com:5432/postgres
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



##### __Expected Output__

| **count** |
| --------- |
| 23        |


```python
%sql SELECT count(*) FROM classicmodels_star_schema.dim_offices;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1a1-rds.cnyk6684iouz.us-east-1.rds.amazonaws.com:5432/postgres
    1 rows affected.





<table>
    <thead>
        <tr>
            <th>count</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>7</td>
        </tr>
    </tbody>
</table>



##### __Expected Output__

| **count** |
| --------- |
| 7         |


```python
%sql SELECT count(*) FROM classicmodels_star_schema.dim_products;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1a1-rds.cnyk6684iouz.us-east-1.rds.amazonaws.com:5432/postgres
    1 rows affected.





<table>
    <thead>
        <tr>
            <th>count</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>110</td>
        </tr>
    </tbody>
</table>



##### __Expected Output__

| **count** |
| --------- |
| 110       |


```python
%sql SELECT count(*) FROM classicmodels_star_schema.dim_dates;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1a1-rds.cnyk6684iouz.us-east-1.rds.amazonaws.com:5432/postgres
    1 rows affected.





<table>
    <thead>
        <tr>
            <th>count</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>1095</td>
        </tr>
    </tbody>
</table>



##### __Expected Output__

| **count** |
| --------- |
| 1095      |

<a name='4'></a>
## 4 - One Big Table (OBT)

As the name suggests, it means a large table containing all the relevant data needed for analysis. It is similar to a fact table, but instead of using dimensional tables and foreign keys, it contains the required dimensional values for each row within. This approach ensures the data warehouse doesn't have to perform any joins to query the relevant data each time you need it. Here is an example of an OBT table focused on the orders of `classicmodels`:

![image](images/obt.png)

4.1. Create the file `orders_obt.sql` in the `./classicmodels_modeling/models/obt/` folder. Here is the SQL query to which you need to apply jinja templating like you did in [Section 3](#3). No need to create any keys there.


```sql
%%sql
SELECT
    orderdetails.orderNumber as order_number,
    orderdetails.orderLineNumber as order_line_number,
    products.productName as product_name,
    products.productScale as product_scale,
    products.productVendor as product_vendor,
    products.productDescription as product_description,
    products.buyPrice as product_buy_price,
    products.MSRP as product_msrp,
    productlines.textDescription as product_line,
    orderdetails.quantityOrdered as quantity_ordered,
    orderdetails.priceEach as product_price,
    orders.orderDate as order_date,
    orders.requiredDate as order_required_date,
    orders.shippedDate as order_shipped_date,
    customers.customerName as customer_name,
    customers.city as customer_city,
    customers.state as customer_state,
    customers.postalCode as customer_postal_code,
    customers.creditLimit as customer_credit_limit,
    employees.firstName as sales_rep_first_name,
    employees.lastName as sales_rep_last_name,
    employees.jobTitle as sales_rep_title,
    orders.status as order_status,
    orders.comments as order_comments
FROM classicmodels.orderdetails
JOIN classicmodels.orders ON orderdetails.orderNumber =  orders.orderNumber
JOIN classicmodels.products ON orderdetails.productCode =  products.productCode
JOIN classicmodels.productlines ON products.productLine =  productlines.productLine
JOIN classicmodels.customers ON orders.customerNumber =  customers.customerNumber
JOIN classicmodels.employees ON customers.salesRepEmployeeNumber =  employees.employeeNumber
LIMIT 2
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1a1-rds.cnyk6684iouz.us-east-1.rds.amazonaws.com:5432/postgres
    2 rows affected.





<table>
    <thead>
        <tr>
            <th>order_number</th>
            <th>order_line_number</th>
            <th>product_name</th>
            <th>product_scale</th>
            <th>product_vendor</th>
            <th>product_description</th>
            <th>product_buy_price</th>
            <th>product_msrp</th>
            <th>product_line</th>
            <th>quantity_ordered</th>
            <th>product_price</th>
            <th>order_date</th>
            <th>order_required_date</th>
            <th>order_shipped_date</th>
            <th>customer_name</th>
            <th>customer_city</th>
            <th>customer_state</th>
            <th>customer_postal_code</th>
            <th>customer_credit_limit</th>
            <th>sales_rep_first_name</th>
            <th>sales_rep_last_name</th>
            <th>sales_rep_title</th>
            <th>order_status</th>
            <th>order_comments</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>10100</td>
            <td>3</td>
            <td>1917 Grand Touring Sedan</td>
            <td>1:18</td>
            <td>Welly Diecast Productions</td>
            <td>This 1:18 scale replica of the 1917 Grand Touring car has all the features you would expect from museum quality reproductions: all four doors and bi-fold hood opening, detailed engine and instrument panel, chrome-look trim, and tufted upholstery, all topped off with a factory baked-enamel finish.</td>
            <td>86.7</td>
            <td>170</td>
            <td>Our Vintage Car models realistically portray automobiles produced from the early 1900s through the 1940s. Materials used include Bakelite, diecast, plastic and wood. Most of the replicas are in the 1:18 and 1:24 scale sizes, which provide the optimum in detail and accuracy. Prices range from $30.00 up to $180.00 for some special limited edition replicas. All models include a certificate of authenticity from their manufacturers and come fully assembled and ready for display in the home or office.</td>
            <td>30</td>
            <td>136</td>
            <td>2003-01-06 00:00:00</td>
            <td>2003-01-13 00:00:00</td>
            <td>2003-01-10 00:00:00</td>
            <td>Online Diecast Creations Co.</td>
            <td>Nashua</td>
            <td>NH</td>
            <td>62005</td>
            <td>114200</td>
            <td>Steve</td>
            <td>Patterson</td>
            <td>Sales Rep</td>
            <td>Shipped</td>
            <td>None</td>
        </tr>
        <tr>
            <td>10100</td>
            <td>2</td>
            <td>1911 Ford Town Car</td>
            <td>1:18</td>
            <td>Motor City Art Classics</td>
            <td>Features opening hood, opening doors, opening trunk, wide white wall tires, front door arm rests, working steering system.</td>
            <td>33.3</td>
            <td>60.54</td>
            <td>Our Vintage Car models realistically portray automobiles produced from the early 1900s through the 1940s. Materials used include Bakelite, diecast, plastic and wood. Most of the replicas are in the 1:18 and 1:24 scale sizes, which provide the optimum in detail and accuracy. Prices range from $30.00 up to $180.00 for some special limited edition replicas. All models include a certificate of authenticity from their manufacturers and come fully assembled and ready for display in the home or office.</td>
            <td>50</td>
            <td>55.09</td>
            <td>2003-01-06 00:00:00</td>
            <td>2003-01-13 00:00:00</td>
            <td>2003-01-10 00:00:00</td>
            <td>Online Diecast Creations Co.</td>
            <td>Nashua</td>
            <td>NH</td>
            <td>62005</td>
            <td>114200</td>
            <td>Steve</td>
            <td>Patterson</td>
            <td>Sales Rep</td>
            <td>Shipped</td>
            <td>None</td>
        </tr>
    </tbody>
</table>



4.2. Create the `schema.yml` file in the `./classicmodels_modeling/models/obt/` folder and develop the appropriate schemas for the `orders_obt` table. For now, you don't need to add the tests for the primary key, just make sure to list the names of the columns in the schema file. You will add the required test in the next section.

4.3. Open the `./classicmodels_modeling/dbt_project.yml` file, at the end of it, under the `classicmodels_modeling` key (which is nested inside the `models` key), add the following lines:

```yml
    obt:
      +materialized: table
      +schema: obt
```

Save changes.

4.4. Make sure you are in the `~/environment/classicmodels_modeling` folder in Cloud9 terminal. Run the following command:

```shell
dbt run --select "obt"
```

4.5. Once you run the dbt run statement, verify that the tables exist and do a record count for each table:


```sql
%%sql
SELECT * FROM information_schema.tables 
WHERE table_schema = 'classicmodels_obt'
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1a1-rds.cnyk6684iouz.us-east-1.rds.amazonaws.com:5432/postgres
    1 rows affected.





<table>
    <thead>
        <tr>
            <th>table_catalog</th>
            <th>table_schema</th>
            <th>table_name</th>
            <th>table_type</th>
            <th>self_referencing_column_name</th>
            <th>reference_generation</th>
            <th>user_defined_type_catalog</th>
            <th>user_defined_type_schema</th>
            <th>user_defined_type_name</th>
            <th>is_insertable_into</th>
            <th>is_typed</th>
            <th>commit_action</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>postgres</td>
            <td>classicmodels_obt</td>
            <td>orders_obt</td>
            <td>BASE TABLE</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>None</td>
            <td>YES</td>
            <td>NO</td>
            <td>None</td>
        </tr>
    </tbody>
</table>




```python
%sql SELECT count(*) FROM classicmodels_obt.orders_obt;
```

     * postgresql+psycopg2://postgresuser:***@de-c4w1a1-rds.cnyk6684iouz.us-east-1.rds.amazonaws.com:5432/postgres
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



##### __Expected Output__

| **count** |
| --------- |
| 2996      |

<a name='5'></a>
## 5 - Performing Tests over the Data in the New Models

You can perform some tests over the data that was populated in your new star schema model. In the `schema.yml` file you have the definition for each model and each column. You can place certain tests at the column level or at the table level. As an example of tests at the table level, you could define the following one for the `orders_obt` table:

```yml
- name: orders_obt
  description: "Orders OBT"
  columns:
    ...
  data_tests:
    - dbt_utils.unique_combination_of_columns:
        combination_of_columns:
        - order_number
        - order_line_number
```

*Note*: The indentation in `.yml` files is crucial for the correct interpretation of the file. Ensure that the indentation levels are consistent to avoid errors in processing the `YAML` file.

This test verifies that the combination of columns that form the primary key is unique. Note that this primary key is composed by a combination of 2 columns. To check for the primary key on other tables that are non composed keys, you can define the test at the column level, such as:

```yml
- name: dim_customers
  description: "Customer dimension"
  columns:
    - name: customer_key
      description: The primary key for this table
      data_tests:
        - unique
        - not_null
```

Add those tests to your model and run the `dbt test` command to check them:

```bash
dbt test -s obt
```

In this lab, you have learned about `dbt` and further your experience with data modeling, each data model has its advantages and setbacks and should be used based on the business and analytical requirements. OBT performs faster in terms of data retrieval speed when compared against a star schema, however updating OBT could be much more complex and a star schema is better in terms of conceptualizing and sharing your data while requiring less storage space. 

<a name='6'></a>
## 6 - Upload Files for Grading

Upload the notebook into S3 bucket for grading purposes. To do this, run the following commands in the terminal.

*Note*: you may need to click **Save** button before the upload.

```bash
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
aws s3 cp /home/ec2-user/environment/C4_W1_Assignment.ipynb s3://de-c4w1a1-${AWS_ACCOUNT_ID}-us-east-1-submission/C4_W1_Assignment_Learner.ipynb
```


```python

```
