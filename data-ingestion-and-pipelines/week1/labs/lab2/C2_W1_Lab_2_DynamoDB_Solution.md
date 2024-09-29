# Interacting With Amazon DynamoDB NoSQL Database

In this lab, you will work with DynamoDB as a key-value database and apply some Create, Read, Update and Delete (CRUD) operations on this NoSQL database.

**Note**: 
- The lab contains links to external resources. You can always skim through these resources during the lab session, but you're not expected to open and read each link during the lab session. If you'd like to deepen your understanding, you can check the linked resources after you're done with the lab.
- The lab contains 4 optional parts that you can choose to skip.

# Table of Contents
- [ 1 - Import Packages](#1)
- [ 2 - Explore the Data](#2)
- [ 3 - Create the DynamoDB Tables](#3)
  - [ Exercise 1](#ex01)
- [ 4 - Load Data into the Tables](#4)
  - [ 4.1 - Load Data Item by Item](#4.1)
    - [ Exercise 2](#ex02)
  - [ 4.2 - Load Data as a Batch of Items](#4.2)
    - [ Exercise 3](#ex03)
- [ 5 - Read Data from the Tables](#5)
  - [ 5.1 - Scan the Full Table](#5.1)
    - [ Exercise 4](#ex04)
  - [ 5.2 - Read a Single Item](#5.2)
    - [ Exercise 5](#ex05)
  - [ 5.3 - Query Items that Share the Same Partition Key](#5.3)
    - [ Exercise 6](#ex06)
    - [ Exercise 7](#ex07)
  - [ 5.4 - Filtering the Table Scans](#5.4)
- [ 6 - Insert and Update Data](#6)
  - [ 6.1 - Insert Data](#6.1)
  - [ 6.2 - Update Data](#6.2)
    - [ Exercise 8](#ex08)
    - [ Exercise 9](#ex09)
- [ 7 - Delete Data](#7)
  - [ Exercise 10](#ex10)
- [ 8 - Transactions - Optional](#8)
  - [ Exercise 11](#ex11)
- [ 9 - Cleanup](#9)

<a name='1'></a>
## 1 - Import Packages

First, let's import some packages. Among these packages, you can find `boto3`, which is the AWS Software Development Kit (SDK) for Python that allows you to interact with various AWS services using Python code. With `boto3`, you can programmatically access AWS resources such as EC2 instances, S3 buckets, Amazon DynamoDB tables, and more. It provides you with a simple and intuitive interface for managing and integrating AWS services into your Python applications efficiently.

For more information on each of the methods that you will use throughout this lab, you can check out [boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html).


```python
import decimal
import json
import logging
from typing import Any, Dict, List

import boto3
from botocore.exceptions import ClientError
```

Let's define the following variable that you will use throughout this lab.


```python
COURSE_PREFIX = 'de-c2w1-dynamodb'
```

<a name='2'></a>
## 2 - Explore the Data

The dataset that you will use in this lab is the sample data from the [Amazon DynamoDB Developer Guide](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/AppendixSampleTables.html#AppendixSampleData) ([dataset zip file](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/samples/sampledata.zip)). The sample data consists of 4 JSON files that you can find in the folder `data/aws_sample_data`:
- `ProductCatalog`: Catalog of products that contains information about some products such as the product ID and its characteristics.
- `Forum`: Information about some AWS forums where users post questions or start a thread (i.e., conversation) about AWS services. The information includes the name of the forum and the total number of threads, messages, and views in each forum.
- `Thread`: Information about each forum thread (i.e., conversation), such as the thread subject, the thread message, the total number of views and replies to the given thread, and who lastly posted on the thread.
- `Reply`: Information about the replies of each thread, such as the time of the reply, the reply message, and the user who posted the reply.

In this lab, you will create 4 DynamoDB tables (`de-c2w1-dynamodb-ProductCatalog`, `de-c2w1-dynamodb-Forum`, `de-c2w1-dynamodb-Thread`, `de-c2w1-dynamodb-Reply`) and load in each the data from the corresponding JSON file. 

**Note**: if you check the content of each JSON file, you will notice the use of letters such as N, S, B. These are known as [*Data type descriptors*](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.NamingRulesDataTypes.html#HowItWorks.DataTypeDescriptors) that tell DynamoDB how to interpret the type of each field. We will talk more about it later in this lab.

<a name='3'></a>
## 3 - Create the DynamoDB Tables

**What is a DynamoDB table?**

DynamoDB database is a key-value store that stores a set of key-value pairs. Let's say you have a set of key-value items where each item represents a product. Each item is characterized by a unique key (product ID) and has a set of corresponding attributes (the value of the key). DynamoDB stores this key-value data in a table where each row contains the attributes of one product and it uses the key to uniquely identify each row. This table is different from relational tables because it's schemaless, which means that neither the attributes nor their data types need to be defined beforehand. Each item can have its own distinct attributes. For example in the product table that you will create in this section, you will have one item that represents a book (Title, Authors, ISBN, Price) and another item that represents a bicycle (BicycleType, Brand, Price, Color) both stored in the same DynamoDB table.

**What is DynamoDB table's primary key?**

When you create a dynamoDB table, you need to specify the primary key which is the key that uniquely identifies each item. The primary key could be a simple key - partition key - or a composite primary key - partition key and sort key.
- partition key (simple key):  For example, in the product tables, you will use the product ID as the primary key since it uniquely identifies each product. For dynamoDB, this simple primary key is called a partition key because dynamoDB uses it as an input to a hash function. The output of the hash function determines the partition (internal physical storage) in which the item will be stored.
- partition key and sort key (composite key): In this composite key, two items can have the same partition key but they should have different sort keys so that the composite key can still uniquely identify each item. DynamoDB will use the partition key to determine in which partition the item will be stored. All items with the same partition key value are stored together, in sorted order by sort key value.

You can learn more about the core components of DynamoDB [here](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.CoreComponents.html).

**How will you create the tables?**

You will use the [DyanmoDB create_table()](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/create_table.html) method. This method expects 3 required parameters:
* `TableName`: the name of the table.
* `KeySchema`: an array of the attributes that make up the primary key for a table. For each element in this array, you need to specify: `AttributeName`: the name of the attribute, and `KeyType`: the role that the key attribute will assume (`HASH` if it is a partition key and `RANGE` if it is a sort key). For example,
  ```
  'KeySchema'= [
      {'AttributeName': 'ForumName', 'KeyType': 'HASH'}, 
      {'AttributeName': 'Subject', 'KeyType': 'RANGE'}
  ]
  ```
* `AttributeDefinitions`: an array that describes the attributes that make up the primary key. For each element in this array, you need to specify `AttributeName` and `AttributeType`: the data type for the attribute (S: String, N: Number, B: Binary,...). For example, 
  ```
  'AttributeDefinitions': [
      {'AttributeName': 'ForumName', 'AttributeType': 'S'},
      {'AttributeName': 'Subject', 'AttributeType': 'S'}
  ]
  ```
There is an additional parameter that you can specify if you don't wish to pay for DynamoDB based on demand and you want to choose the provisioned mode:
* `ProvisionedThroughput`: a dictionary that specifies the read/write capacity (or throughput) for a specified table. It consists of two items:
  - `ReadCapacityUnits`: the maximum number of strongly consistent reads consumed per second;
  - `WriteCapacityUnits`: the maximum number of writes consumed per second. 

In this lab, you will create 4 tables, and for each table, you need to specify the parameters that we just listed here. To make it easy for you to access the properties of each table throughout this notebook, we created the following dictionaries that specify the properties for each table.


```python
capacity_units = {'ReadCapacityUnits': 10, 'WriteCapacityUnits': 5}

product_catalog_table = {'table_name': f'{COURSE_PREFIX}-ProductCatalog',
                         'kwargs': {
                             'KeySchema': [{'AttributeName': 'Id', 'KeyType': 'HASH'}],
                             'AttributeDefinitions': [{'AttributeName': 'Id', 'AttributeType': 'N'}],
                             'ProvisionedThroughput': capacity_units
                         }
                        }

forum_table = {'table_name': f'{COURSE_PREFIX}-Forum',
                'kwargs': {
                    'KeySchema': [{'AttributeName': 'Name', 'KeyType': 'HASH'}],
                    'AttributeDefinitions': [{'AttributeName': 'Name', 'AttributeType': 'S'}],
                    'ProvisionedThroughput': capacity_units
                }
              }

thread_table = {'table_name': f'{COURSE_PREFIX}-Thread',
                'kwargs': {
                    'KeySchema': [{'AttributeName': 'ForumName', 'KeyType': 'HASH'}, 
                                  {'AttributeName': 'Subject', 'KeyType': 'RANGE'}],
                    'AttributeDefinitions': [{'AttributeName': 'ForumName', 'AttributeType': 'S'},
                                             {'AttributeName': 'Subject', 'AttributeType': 'S'}],
                    'ProvisionedThroughput': capacity_units
                }
               }

reply_table = {'table_name': f'{COURSE_PREFIX}-Reply',
                'kwargs': {
                    'KeySchema': [{'AttributeName': 'Id', 'KeyType': 'HASH'}, 
                                  {'AttributeName': 'ReplyDateTime', 'KeyType': 'RANGE'}],
                    'AttributeDefinitions': [{'AttributeName': 'Id', 'AttributeType': 'S'},
                                             {'AttributeName': 'ReplyDateTime', 'AttributeType': 'S'}],
                    'ProvisionedThroughput': capacity_units
                }
              }
```

Note that the thread and reply tables will both use a composite primary key, and that the product and forum tables will use a simple primary key.

**Note:** To interact with AmazonDynamoDB throughout this notebook, you are going to create a `boto3` client object. This object allows you to make API requests directly to AWS services to create, delete, or modify resources. When you create a `boto3` client object, you will need to specify the AWS services you want to interact with, and then, with the created client object, you can call methods to perform various operations on that resource.

<a name='ex01'></a>
### Exercise 1

To create the 4 tables, you will use the function `create_table_db()` provided in the following cell. This function calls the `DynamoDB create_table()` method, and takes in two arguments:
* `table_name`: the name of the table;
* `kwargs`: A dictionary that specifies the additional arguments for `DynamoDB create_table()` such as `KeySchema`, `AttributeDefinitions`and `ProvisionedThroughput` as shown in the previous cell. `**kwargs` means that the elements in the dictionary are unpacked into a sequence of arguments.

In this first exercise, you will need to replace `None` with the appropriate values.


```python
def create_table_db(table_name: str, **kwargs):
    client = boto3.client("dynamodb")
    ### START CODE HERE ### (~ 1 line of code)
    response = client.create_table(TableName=table_name, **kwargs)
    ### END CODE HERE ###

    waiter = client.get_waiter("table_exists")
    waiter.wait(TableName=table_name)

    return response
```

Now that the `create_table_db()` function is ready, you can test it by creating the `ProductCatalog` table. The execution should take less than a minute.


```python
response = create_table_db(table_name=product_catalog_table['table_name'], **product_catalog_table["kwargs"]) 
print(response)
```

    {'TableDescription': {'AttributeDefinitions': [{'AttributeName': 'Id', 'AttributeType': 'N'}], 'TableName': 'de-c2w1-dynamodb-ProductCatalog', 'KeySchema': [{'AttributeName': 'Id', 'KeyType': 'HASH'}], 'TableStatus': 'CREATING', 'CreationDateTime': datetime.datetime(2024, 9, 23, 4, 9, 45, 788000, tzinfo=tzlocal()), 'ProvisionedThroughput': {'NumberOfDecreasesToday': 0, 'ReadCapacityUnits': 10, 'WriteCapacityUnits': 5}, 'TableSizeBytes': 0, 'ItemCount': 0, 'TableArn': 'arn:aws:dynamodb:us-east-1:322144634018:table/de-c2w1-dynamodb-ProductCatalog', 'TableId': '8ca9426b-fae8-43d8-a39a-5ab8026ffb4e', 'DeletionProtectionEnabled': False}, 'ResponseMetadata': {'RequestId': 'DAM05E2JTB5JQM2BO4BJBVB2QJVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 23 Sep 2024 04:09:45 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '557', 'connection': 'keep-alive', 'x-amzn-requestid': 'DAM05E2JTB5JQM2BO4BJBVB2QJVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '3979629113'}, 'RetryAttempts': 0}}


##### __Expected Output__ 
```
{'TableDescription': {'AttributeDefinitions': [{'AttributeName': 'Id', 'AttributeType': 'N'}], 'TableName': 'de-c2w1-dynamodb-ProductCatalog', 'KeySchema': [{'AttributeName': 'Id', 'KeyType': 'HASH'}], 'TableStatus': 'CREATING', 'CreationDateTime': datetime.datetime(2024, 2, 14, 6, 42, 38, 872000, tzinfo=tzlocal()), 'ProvisionedThroughput': {'NumberOfDecreasesToday': 0, 'ReadCapacityUnits': 10, 'WriteCapacityUnits': 5}, 'TableSizeBytes': 0, 'ItemCount': 0, 'TableArn': 'arn:aws:dynamodb:us-east-1:631295702609:table/de-c2w1-dynamodb-ProductCatalog', 'TableId': '639df373-f498-4a2d-9851-6c6f6c26d908', 'DeletionProtectionEnabled': False}, 'ResponseMetadata': {'RequestId': 'OJ9GC0U10JH5ILK020C4PM094VVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Wed, 14 Feb 2024 06:42:38 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '557', 'connection': 'keep-alive', 'x-amzn-requestid': 'OJ9GC0U10JH5ILK020C4PM094VVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '1500356689'}, 'RetryAttempts': 0}}
```

Execute the following command to create the other three tables. The creation of all tables can take around 2 minutes.


```python
for dynamodb_tab in [forum_table, thread_table, reply_table]:
    response = create_table_db(dynamodb_tab["table_name"], **dynamodb_tab["kwargs"])
    print(response)
```

    {'TableDescription': {'AttributeDefinitions': [{'AttributeName': 'Name', 'AttributeType': 'S'}], 'TableName': 'de-c2w1-dynamodb-Forum', 'KeySchema': [{'AttributeName': 'Name', 'KeyType': 'HASH'}], 'TableStatus': 'CREATING', 'CreationDateTime': datetime.datetime(2024, 9, 23, 4, 11, 8, 283000, tzinfo=tzlocal()), 'ProvisionedThroughput': {'NumberOfDecreasesToday': 0, 'ReadCapacityUnits': 10, 'WriteCapacityUnits': 5}, 'TableSizeBytes': 0, 'ItemCount': 0, 'TableArn': 'arn:aws:dynamodb:us-east-1:322144634018:table/de-c2w1-dynamodb-Forum', 'TableId': 'ee19182e-a625-429f-8c90-829a90ec2c19', 'DeletionProtectionEnabled': False}, 'ResponseMetadata': {'RequestId': 'RI3NNPURAG0JKTHI6NRJ3AKUIBVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 23 Sep 2024 04:11:08 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '543', 'connection': 'keep-alive', 'x-amzn-requestid': 'RI3NNPURAG0JKTHI6NRJ3AKUIBVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '702040401'}, 'RetryAttempts': 0}}
    {'TableDescription': {'AttributeDefinitions': [{'AttributeName': 'ForumName', 'AttributeType': 'S'}, {'AttributeName': 'Subject', 'AttributeType': 'S'}], 'TableName': 'de-c2w1-dynamodb-Thread', 'KeySchema': [{'AttributeName': 'ForumName', 'KeyType': 'HASH'}, {'AttributeName': 'Subject', 'KeyType': 'RANGE'}], 'TableStatus': 'CREATING', 'CreationDateTime': datetime.datetime(2024, 9, 23, 4, 11, 28, 456000, tzinfo=tzlocal()), 'ProvisionedThroughput': {'NumberOfDecreasesToday': 0, 'ReadCapacityUnits': 10, 'WriteCapacityUnits': 5}, 'TableSizeBytes': 0, 'ItemCount': 0, 'TableArn': 'arn:aws:dynamodb:us-east-1:322144634018:table/de-c2w1-dynamodb-Thread', 'TableId': '9f3c5685-8f81-427f-bc03-b05399ef6804', 'DeletionProtectionEnabled': False}, 'ResponseMetadata': {'RequestId': '9FK93PUFDT7Q4T7DJGJKNMNFKNVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 23 Sep 2024 04:11:28 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '649', 'connection': 'keep-alive', 'x-amzn-requestid': '9FK93PUFDT7Q4T7DJGJKNMNFKNVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '2195994683'}, 'RetryAttempts': 0}}
    {'TableDescription': {'AttributeDefinitions': [{'AttributeName': 'Id', 'AttributeType': 'S'}, {'AttributeName': 'ReplyDateTime', 'AttributeType': 'S'}], 'TableName': 'de-c2w1-dynamodb-Reply', 'KeySchema': [{'AttributeName': 'Id', 'KeyType': 'HASH'}, {'AttributeName': 'ReplyDateTime', 'KeyType': 'RANGE'}], 'TableStatus': 'CREATING', 'CreationDateTime': datetime.datetime(2024, 9, 23, 4, 11, 48, 646000, tzinfo=tzlocal()), 'ProvisionedThroughput': {'NumberOfDecreasesToday': 0, 'ReadCapacityUnits': 10, 'WriteCapacityUnits': 5}, 'TableSizeBytes': 0, 'ItemCount': 0, 'TableArn': 'arn:aws:dynamodb:us-east-1:322144634018:table/de-c2w1-dynamodb-Reply', 'TableId': '8556a55a-9bd0-426e-af19-dcc179d4e9d5', 'DeletionProtectionEnabled': False}, 'ResponseMetadata': {'RequestId': '1B0C2P146076P3D04360UC0N5NVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 23 Sep 2024 04:11:48 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '645', 'connection': 'keep-alive', 'x-amzn-requestid': '1B0C2P146076P3D04360UC0N5NVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '2267847364'}, 'RetryAttempts': 0}}


Go to the AWS Console, search for **DynamoDB**, click on Tables on the left, and check that the tables have been created.

<a name='4'></a>
## 4 - Load Data into the Tables

You will now load data into each table from the following JSON files:
* `Forum.json`
* `ProductCatalog.json`
* `Reply.json`
* `Thread.json`

You can load data item by item or as a batch of items. Let's explore each option.

<a name='4.1'></a>
### 4.1 - Load Data Item by Item

To load data item by item, you will use the method: [DynamoDB put_item()](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/put_item.html). This method expects two required arguments (1) the table name and (2) the item you need to add. The item should be a dictionary that contains the attributes of the item (and most importantly the value of its primary key), for example, here's the format of what the item should look like (an item in the reply table):
```
item = {
        "Id": {
            "S": "Amazon DynamoDB#DynamoDB Thread 1"
            },
        "ReplyDateTime": {
             "S": "2015-09-15T19:58:22.947Z"
             },
        "Message": {
            "S": "DynamoDB Thread 1 Reply 1 text"
        },
        "PostedBy": {
            "S": "User A"
        }
}
```
This JSON structure that looks as follows:

```JSON
{
    "<AttributeName>": {
        "<DataType>": "<Value>"
    },
    "<ListAttribute>": {
        "<DataType>": [
            {
                "<DataType>": "<Value1>"
            },
            {
                "<DataType>": "<Value2>"
            }]
    }    
}
```
is called Marshal JSON. This is similar to a regular JSON file but it also includes the types of each value. The `<DataType>` placeholders specify the data type of the corresponding value; you can learn more about the Data type conventions for DynamoDB in the [documentation](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.NamingRulesDataTypes.html#HowItWorks.DataTypeDescriptors). The good news is that all of the items provided in the sample JSON files are already in this expected format for `DynamoDB put_item()`. 

In this section, you are provided with two functions:
- `read_data()`: reads a sample JSON file and returns the items as a Python dictionary;
- `put_item_db()`: This function takes in as arguments the table name and the details of the item as a Python dictionary, calls `DynamoDB put_item()` and passes to it the table name and the item.


In the exercise of this section, you just need to replace `None` inside the function `put_item_db()`. You don't need to modify anything inside `read_data()`. You will use the `read_data()` function to read all items from the JSON file, and then you will use the function `put_item_db()` to load each item to a given DynamoDB table.  


```python
def read_data(file_path: str) -> Dict[str, Any]:
    with open(file_path, "r") as json_file:
        items = json.load(json_file)
    return items
```

<a name='ex02'></a>
### Exercise 2

In this exercise, you need to replace `None` with the appropriate values:
1. Create a Client object (see the code in the previous exercise).
2. Use the `client.put_item()` method of the object `client` to load the data, which expects three arguments: `TableName`, the `Item` to be loaded, and some keyword arguments.


```python
def put_item_db( table_name: str, item: Dict[str, Any], **kwargs):
    ### START CODE HERE ### (~ 2 lines of code)
    client = boto3.client("dynamodb")
    response = client.put_item(TableName=table_name, Item=item, **kwargs)
    ### END CODE HERE ###

    return response
```

Now, let's load the items from `ProductCatalog` and `Thread` files one by one to the corresponding tables.


```python
for dynamodb_tab in [product_catalog_table, thread_table]:
    file_name = dynamodb_tab['table_name'].split('-')[-1]    
    items = read_data(file_path=f'./data/aws_sample_data/{file_name}.json')
    
    for item in items[dynamodb_tab["table_name"]]:
        put_item_db(table_name=dynamodb_tab["table_name"], item=item['PutRequest']['Item'])
```

<a name='4.2'></a>
### 4.2 - Load Data as a Batch of Items

Now, you will create the `batch_write_item_db()` function which calls the [DynamoDB batch_write_item()](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/batch_write_item.html). This later method allows you to put or delete multiple items in one or more tables. 

Again, you will have to read the two JSON files `Reply` and `Forum` and then load the items into the tables. Let's load the data into the `Reply` and `Forum` tables.

<a name='ex03'></a>
### Exercise 3

In this exercise, you need to replace `None` with the appropriate values:
1. Create the Client object;
2. Call the `client.batch_write_item()` method of the `client` object. It should receive the items that need to be loaded and some keyword arguments. Assume that the input `items` is in the right format that `batch_write_item()` (the format of the items stored in the sample JSON files is exactly the format that `batch_write_item()` expects. For more info, you can check the documentation [here](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/batch_write_item.html)).


```python
def batch_write_item_db(items: Dict[str, Any], **kwargs):
    ### START CODE HERE ### (~ 2 lines of code)
    client = boto3.client("dynamodb")
    response = client.batch_write_item(RequestItems=items, **kwargs)
    ### END CODE HERE ###
    
    return response
```

Now, let's read the data from the JSON sample files: `Reply` and `Forum` and then load the items as a batch into the corresponding tables.


```python
for dynamodb_tab in [reply_table, forum_table]:
    file_name = dynamodb_tab['table_name'].split('-')[-1]    
    items = read_data(file_path=f'./data/aws_sample_data/{file_name}.json')
    response = batch_write_item_db(items=items)
    print(response)
```

    {'UnprocessedItems': {}, 'ResponseMetadata': {'RequestId': '000045D81B5VRT7H6CQREDNENFVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 23 Sep 2024 04:18:29 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '23', 'connection': 'keep-alive', 'x-amzn-requestid': '000045D81B5VRT7H6CQREDNENFVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '4185382651'}, 'RetryAttempts': 0}}
    {'UnprocessedItems': {}, 'ResponseMetadata': {'RequestId': 'S1FMCT8BADAURF0Q6C8RH5SB9RVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 23 Sep 2024 04:18:30 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '23', 'connection': 'keep-alive', 'x-amzn-requestid': 'S1FMCT8BADAURF0Q6C8RH5SB9RVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '4185382651'}, 'RetryAttempts': 0}}


##### __Expected Output__ 

```
{'UnprocessedItems': {}, 'ResponseMetadata': {'RequestId': '4P678E81BOHRCUN82FFREOTC8NVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Wed, 14 Feb 2024 06:44:36 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '23', 'connection': 'keep-alive', 'x-amzn-requestid': '4P678E81BOHRCUN82FFREOTC8NVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '4185382651'}, 'RetryAttempts': 0}}
{'UnprocessedItems': {}, 'ResponseMetadata': {'RequestId': 'R53NDPHFEH0UEL0MG6PFG8FEJRVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Wed, 14 Feb 2024 06:44:36 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '23', 'connection': 'keep-alive', 'x-amzn-requestid': 'R53NDPHFEH0UEL0MG6PFG8FEJRVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '4185382651'}, 'RetryAttempts': 0}
}```

<a name='5'></a>
## 5 - Read Data from the Tables

In this section, you will experiment with various approaches to read data from the DynamoDB tables.

<a name='5.1'></a>
### 5.1 - Scan the Full Table

You can perform a `DynamoDB scan()` operation on a DynamoDB table that fully scans the table and returns the items in 1MB chunks. Scanning is the slowest and most expensive way to get data out of DynamoDB. Let's first explore this approach.

<a name='ex04'></a>
### Exercise 4

In this exercise, you need to replace `None` with the appropriate values:
1. Create the Client object `client`.
2. Call the `client.scan()` method of the `client` object. It should receive the table name and keyword arguments. In the [DynamoDB boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html), search for the `scan` method to check what it takes as parameters.


```python
def scan_db(table_name: str, **kwargs):
    ### START CODE HERE ### (~ 2 lines of code)
    client = boto3.client("dynamodb")
    response = client.scan(TableName=table_name, **kwargs)
    ### END CODE HERE ###
    
    return response
```

Let's make a full scan on the `ProductCatalog` table:


```python
response = scan_db(product_catalog_table['table_name'])
print(f"Queried data for table {product_catalog_table['table_name']}:\n{response}")
```

    Queried data for table de-c2w1-dynamodb-ProductCatalog:
    {'Items': [{'Title': {'S': '18-Bike-204'}, 'Price': {'N': '500'}, 'Brand': {'S': 'Brand-Company C'}, 'Description': {'S': '205 Description'}, 'Color': {'L': [{'S': 'Red'}, {'S': 'Black'}]}, 'ProductCategory': {'S': 'Bicycle'}, 'Id': {'N': '205'}, 'BicycleType': {'S': 'Hybrid'}}, {'Title': {'S': '19-Bike-203'}, 'Price': {'N': '300'}, 'Brand': {'S': 'Brand-Company B'}, 'Description': {'S': '203 Description'}, 'Color': {'L': [{'S': 'Red'}, {'S': 'Green'}, {'S': 'Black'}]}, 'ProductCategory': {'S': 'Bicycle'}, 'Id': {'N': '203'}, 'BicycleType': {'S': 'Road'}}, {'Title': {'S': '21-Bike-202'}, 'Price': {'N': '200'}, 'Brand': {'S': 'Brand-Company A'}, 'Description': {'S': '202 Description'}, 'Color': {'L': [{'S': 'Green'}, {'S': 'Black'}]}, 'ProductCategory': {'S': 'Bicycle'}, 'Id': {'N': '202'}, 'BicycleType': {'S': 'Road'}}, {'Title': {'S': '18-Bike-201'}, 'Price': {'N': '100'}, 'Brand': {'S': 'Mountain A'}, 'Description': {'S': '201 Description'}, 'Color': {'L': [{'S': 'Red'}, {'S': 'Black'}]}, 'ProductCategory': {'S': 'Bicycle'}, 'Id': {'N': '201'}, 'BicycleType': {'S': 'Road'}}, {'Title': {'S': '18-Bike-204'}, 'Price': {'N': '400'}, 'Brand': {'S': 'Brand-Company B'}, 'Description': {'S': '204 Description'}, 'Color': {'L': [{'S': 'Red'}]}, 'ProductCategory': {'S': 'Bicycle'}, 'Id': {'N': '204'}, 'BicycleType': {'S': 'Mountain'}}, {'Title': {'S': 'Book 102 Title'}, 'InPublication': {'BOOL': True}, 'PageCount': {'N': '600'}, 'Dimensions': {'S': '8.5 x 11.0 x 0.8'}, 'ISBN': {'S': '222-2222222222'}, 'Authors': {'L': [{'S': 'Author1'}, {'S': 'Author2'}]}, 'Price': {'N': '20'}, 'ProductCategory': {'S': 'Book'}, 'Id': {'N': '102'}}, {'Title': {'S': 'Book 103 Title'}, 'InPublication': {'BOOL': False}, 'PageCount': {'N': '600'}, 'Dimensions': {'S': '8.5 x 11.0 x 1.5'}, 'ISBN': {'S': '333-3333333333'}, 'Authors': {'L': [{'S': 'Author1'}, {'S': 'Author2'}]}, 'Price': {'N': '2000'}, 'ProductCategory': {'S': 'Book'}, 'Id': {'N': '103'}}, {'Title': {'S': 'Book 101 Title'}, 'InPublication': {'BOOL': True}, 'PageCount': {'N': '500'}, 'Dimensions': {'S': '8.5 x 11.0 x 0.5'}, 'ISBN': {'S': '111-1111111111'}, 'Authors': {'L': [{'S': 'Author1'}]}, 'Price': {'N': '2'}, 'ProductCategory': {'S': 'Book'}, 'Id': {'N': '101'}}], 'Count': 8, 'ScannedCount': 8, 'ResponseMetadata': {'RequestId': '6ADEF83A3G8JFMEQFJA38MKBUVVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 23 Sep 2024 04:19:53 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '2043', 'connection': 'keep-alive', 'x-amzn-requestid': '6ADEF83A3G8JFMEQFJA38MKBUVVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '873234463'}, 'RetryAttempts': 0}}


You can that the returned data has the same input structure that the method `DynamoDB put_item()` expects, which is the Marshal JSON. Marshal JSON is different from the usual JSON format that looks like the following:

```JSON
{
    "AttributeName": "Value",
    "ListAttribute": [
        "Value1",
        "Value2"
    ]
}
```

The usual JSON format is the typical format you will find in real life, as it can be easily parsed into Python Dictionaries. So you may need to convert the output returned by the `DynamoDB scan()` method into the usual JSON format, or you may need to convert data that is in the usual JSON format into Marshal JSON before inserting it into a DynamoDB table. The next optional part shows you how you can convert data in Marshal JSON into the usual JSON format. You can try the optional part or feel free to skip it.
 

#### Optional Part - 1 (Deserializing Marshal JSON)

Now, if you want to process data returned from DynamoDB operations with Python, you have to convert the data format to the usual JSON. `boto3` provides some utilities to help you with this process.
To convert the `ProductCatalog` data returned by the scan method into a regular JSON format to be used in Python dictionaries, you can use the `data_deserializer()` function provided below that takes in as input the data in Marshal JSON. This function consists of the following:

1. A `boto3` resource instantiation: [Resources](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/resources.html) is a higher-level abstraction class built on top of Client that is used to represent AWS resources as Python objects, providing in this way a Pythonic and Object Oriented interface. With that resource, you can create a deserializer object by calling the method `TypeDeserializer()`.
2. You can then use the `deserializer` object to call the `deserializer.deserialize()` method and apply it to each value to convert it into its deserialized version. (Note: if the returned value from `deserializer.deserialize(v)` is an instance of `decimal.Decimal`, you should convert it to float. This process of checking if the returned value is an instance of `decimal.Decimal` should be done because, by default, numerical values in DynamoDB are deserialized as decimals, which need to be handled properly if you want to work with the result; the easiest way is to convert them directly to float data type).

The below function uses dictionary comprehension to iterate through the dictionary items. 


```python
def data_deserializer(data: Dict[str, Any]):
    boto3.resource("dynamodb")

    deserializer = boto3.dynamodb.types.TypeDeserializer()

    deserialized_data = {
        k: (
            float(deserializer.deserialize(v))
            if isinstance(deserializer.deserialize(v), decimal.Decimal)
            else deserializer.deserialize(v)
        )
        for k, v in data.items()
    }

    return deserialized_data
```

Execute the method over the previous response to see the difference in the format.


```python
for item in response['Items']:
    print(f"DynamoDB returned Marshal JSON:\n{item}")
    print(f"Deserialized python dictionary:\n {data_deserializer(item)}")
```

    DynamoDB returned Marshal JSON:
    {'Title': {'S': '18-Bike-204'}, 'Price': {'N': '500'}, 'Brand': {'S': 'Brand-Company C'}, 'Description': {'S': '205 Description'}, 'Color': {'L': [{'S': 'Red'}, {'S': 'Black'}]}, 'ProductCategory': {'S': 'Bicycle'}, 'Id': {'N': '205'}, 'BicycleType': {'S': 'Hybrid'}}
    Deserialized python dictionary:
     {'Title': '18-Bike-204', 'Price': 500.0, 'Brand': 'Brand-Company C', 'Description': '205 Description', 'Color': ['Red', 'Black'], 'ProductCategory': 'Bicycle', 'Id': 205.0, 'BicycleType': 'Hybrid'}
    DynamoDB returned Marshal JSON:
    {'Title': {'S': '19-Bike-203'}, 'Price': {'N': '300'}, 'Brand': {'S': 'Brand-Company B'}, 'Description': {'S': '203 Description'}, 'Color': {'L': [{'S': 'Red'}, {'S': 'Green'}, {'S': 'Black'}]}, 'ProductCategory': {'S': 'Bicycle'}, 'Id': {'N': '203'}, 'BicycleType': {'S': 'Road'}}
    Deserialized python dictionary:
     {'Title': '19-Bike-203', 'Price': 300.0, 'Brand': 'Brand-Company B', 'Description': '203 Description', 'Color': ['Red', 'Green', 'Black'], 'ProductCategory': 'Bicycle', 'Id': 203.0, 'BicycleType': 'Road'}
    DynamoDB returned Marshal JSON:
    {'Title': {'S': '21-Bike-202'}, 'Price': {'N': '200'}, 'Brand': {'S': 'Brand-Company A'}, 'Description': {'S': '202 Description'}, 'Color': {'L': [{'S': 'Green'}, {'S': 'Black'}]}, 'ProductCategory': {'S': 'Bicycle'}, 'Id': {'N': '202'}, 'BicycleType': {'S': 'Road'}}
    Deserialized python dictionary:
     {'Title': '21-Bike-202', 'Price': 200.0, 'Brand': 'Brand-Company A', 'Description': '202 Description', 'Color': ['Green', 'Black'], 'ProductCategory': 'Bicycle', 'Id': 202.0, 'BicycleType': 'Road'}
    DynamoDB returned Marshal JSON:
    {'Title': {'S': '18-Bike-201'}, 'Price': {'N': '100'}, 'Brand': {'S': 'Mountain A'}, 'Description': {'S': '201 Description'}, 'Color': {'L': [{'S': 'Red'}, {'S': 'Black'}]}, 'ProductCategory': {'S': 'Bicycle'}, 'Id': {'N': '201'}, 'BicycleType': {'S': 'Road'}}
    Deserialized python dictionary:
     {'Title': '18-Bike-201', 'Price': 100.0, 'Brand': 'Mountain A', 'Description': '201 Description', 'Color': ['Red', 'Black'], 'ProductCategory': 'Bicycle', 'Id': 201.0, 'BicycleType': 'Road'}
    DynamoDB returned Marshal JSON:
    {'Title': {'S': '18-Bike-204'}, 'Price': {'N': '400'}, 'Brand': {'S': 'Brand-Company B'}, 'Description': {'S': '204 Description'}, 'Color': {'L': [{'S': 'Red'}]}, 'ProductCategory': {'S': 'Bicycle'}, 'Id': {'N': '204'}, 'BicycleType': {'S': 'Mountain'}}
    Deserialized python dictionary:
     {'Title': '18-Bike-204', 'Price': 400.0, 'Brand': 'Brand-Company B', 'Description': '204 Description', 'Color': ['Red'], 'ProductCategory': 'Bicycle', 'Id': 204.0, 'BicycleType': 'Mountain'}
    DynamoDB returned Marshal JSON:
    {'Title': {'S': 'Book 102 Title'}, 'InPublication': {'BOOL': True}, 'PageCount': {'N': '600'}, 'Dimensions': {'S': '8.5 x 11.0 x 0.8'}, 'ISBN': {'S': '222-2222222222'}, 'Authors': {'L': [{'S': 'Author1'}, {'S': 'Author2'}]}, 'Price': {'N': '20'}, 'ProductCategory': {'S': 'Book'}, 'Id': {'N': '102'}}
    Deserialized python dictionary:
     {'Title': 'Book 102 Title', 'InPublication': True, 'PageCount': 600.0, 'Dimensions': '8.5 x 11.0 x 0.8', 'ISBN': '222-2222222222', 'Authors': ['Author1', 'Author2'], 'Price': 20.0, 'ProductCategory': 'Book', 'Id': 102.0}
    DynamoDB returned Marshal JSON:
    {'Title': {'S': 'Book 103 Title'}, 'InPublication': {'BOOL': False}, 'PageCount': {'N': '600'}, 'Dimensions': {'S': '8.5 x 11.0 x 1.5'}, 'ISBN': {'S': '333-3333333333'}, 'Authors': {'L': [{'S': 'Author1'}, {'S': 'Author2'}]}, 'Price': {'N': '2000'}, 'ProductCategory': {'S': 'Book'}, 'Id': {'N': '103'}}
    Deserialized python dictionary:
     {'Title': 'Book 103 Title', 'InPublication': False, 'PageCount': 600.0, 'Dimensions': '8.5 x 11.0 x 1.5', 'ISBN': '333-3333333333', 'Authors': ['Author1', 'Author2'], 'Price': 2000.0, 'ProductCategory': 'Book', 'Id': 103.0}
    DynamoDB returned Marshal JSON:
    {'Title': {'S': 'Book 101 Title'}, 'InPublication': {'BOOL': True}, 'PageCount': {'N': '500'}, 'Dimensions': {'S': '8.5 x 11.0 x 0.5'}, 'ISBN': {'S': '111-1111111111'}, 'Authors': {'L': [{'S': 'Author1'}]}, 'Price': {'N': '2'}, 'ProductCategory': {'S': 'Book'}, 'Id': {'N': '101'}}
    Deserialized python dictionary:
     {'Title': 'Book 101 Title', 'InPublication': True, 'PageCount': 500.0, 'Dimensions': '8.5 x 11.0 x 0.5', 'ISBN': '111-1111111111', 'Authors': ['Author1'], 'Price': 2.0, 'ProductCategory': 'Book', 'Id': 101.0}


If you want to understand more about the transformation process between Marshall JSON and JSON/Python dictionaries, you can find tools like this one that will let you practice with them. You can also take a look at the `boto3`'s documentation to see how TypeSerializer and TypeDeserializer are implemented.

#### End of Optional Part - 1

<a name='5.2'></a>
### 5.2 - Read a Single Item

The `DynamoDB scan()` method returns all items in a table. If you want to read a single item, you could use the `DynamoDB get_item()` method. This method expects the name of the table and the primary key of the requested item. It is the cheapest and fastest way to get data from DynamoDB.

<a name='ex05'></a>
### Exercise 5

In the following function, call the `client.get_item()` method of the `client` object. It should receive the table name, key and keyword arguments. For more information about this method, you can search for the `get_item`in the [documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html).


```python
def get_item_db(table_name, key: Dict[str, Any], **kwargs):
    client = boto3.client("dynamodb")

    try:
        ### START CODE HERE ### (~ 1 line of code)
        response = client.get_item(TableName=table_name, Key=key, **kwargs)
        ### END CODE HERE ###
        
    except ClientError as e:
        error = e.response.get("Error", {})
        logging.error(
            f"Failed to query DynamoDB. Error: {error.get('Message')}"
        )
        response = {}
    
    return response
```

Get the item with Id 101 from the `ProductCatalog` table.


```python
response = get_item_db(table_name=product_catalog_table['table_name'], 
                    key={'Id': {'N': '101'}})
print(response)
```

    {'Item': {'Title': {'S': 'Book 101 Title'}, 'InPublication': {'BOOL': True}, 'PageCount': {'N': '500'}, 'Dimensions': {'S': '8.5 x 11.0 x 0.5'}, 'ISBN': {'S': '111-1111111111'}, 'Authors': {'L': [{'S': 'Author1'}]}, 'Price': {'N': '2'}, 'ProductCategory': {'S': 'Book'}, 'Id': {'N': '101'}}, 'ResponseMetadata': {'RequestId': 'FU95D5B56JKK4H8CJ62OTCR5VBVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 23 Sep 2024 04:21:37 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '263', 'connection': 'keep-alive', 'x-amzn-requestid': 'FU95D5B56JKK4H8CJ62OTCR5VBVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '3181387427'}, 'RetryAttempts': 0}}


##### __Expected Output__ 

```
{'Item': {'Title': {'S': 'Book 101 Title'}, 'InPublication': {'BOOL': True}, 'PageCount': {'N': '500'}, 'Dimensions': {'S': '8.5 x 11.0 x 0.5'}, 'ISBN': {'S': '111-1111111111'}, 'Authors': {'L': [{'S': 'Author1'}]}, 'Price': {'N': '2'}, 'ProductCategory': {'S': 'Book'}, 'Id': {'N': '101'}}, 'ResponseMetadata': {'RequestId': '08VIS0M7LH396M766IOPU54E9JVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Wed, 14 Feb 2024 06:44:53 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '263', 'connection': 'keep-alive', 'x-amzn-requestid': '08VIS0M7LH396M766IOPU54E9JVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '3181387427'}, 'RetryAttempts': 0}}
```

#### Optional Part - 2 (More options for the read methods)

By default, a read from DynamoDB will use eventual consistency. A consistent read in DynamoDB is cheaper than a strongly consistent read. Several options can be added to the read methods, some of the regularly used ones are:
- `ConsistentRead`: specifies that a strongly consistent read of the table is required;
- `ProjectionExpression`: specifies what attributes should be returned;
- `ReturnConsumedCapacity`: determines what level of detail about the consumed capacity the response should return.

You can find more information about the parameters that the `DynamoDB.Client.get_item()` accepts by reading the [documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/get_item.html).

In the following code, you will:
1. Set the attribute `ConsistentRead` to `True` to ensure strongly consistent reads.
2. Specify that you only want to retrieve the following fields: `ProductCategory`, `Price`, and `Title` using the `ProjectionExpression` attribute.
3. Set the attribute `ReturnConsumedCapacity` to `'TOTAL'`.
4. Query the item with `Id=101` from the `ProductCatalog` table.


```python
kwargs = {'ConsistentRead': True,
          'ProjectionExpression': 'ProductCategory, Price, Title',
          'ReturnConsumedCapacity': 'TOTAL'}

response = get_item_db(table_name=product_catalog_table['table_name'], key={'Id': {'N': '101'}}, **kwargs)
print(response)
```

    {'Item': {'Price': {'N': '2'}, 'Title': {'S': 'Book 101 Title'}, 'ProductCategory': {'S': 'Book'}}, 'ConsumedCapacity': {'TableName': 'de-c2w1-dynamodb-ProductCatalog', 'CapacityUnits': 1.0}, 'ResponseMetadata': {'RequestId': 'FL2GOVEBK5DB701N31NT6F89FBVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 23 Sep 2024 04:21:48 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '177', 'connection': 'keep-alive', 'x-amzn-requestid': 'FL2GOVEBK5DB701N31NT6F89FBVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '2450922370'}, 'RetryAttempts': 0}}


The previous request consumed 1.0 RCU because this item is less than 4KB. (RCU stands for Read Capacity Unit: "One read capacity unit represents one strongly consistent read per second, or two eventually consistent reads per second, for an item up to 4 KB in size", [reference](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/provisioned-capacity-mode.html)).

If you run again the command but remove the ConsistentRead option, you can see that eventually consistent reads consume half as much capacity:


```python
kwargs = {'ReturnConsumedCapacity': 'TOTAL', 
          'ProjectionExpression': 'ProductCategory, Price, Title'
         }

response = get_item_db(table_name=product_catalog_table['table_name'], 
                    key={'Id': {'N': '101'}}, **kwargs
                    )
print(response)
```

    {'Item': {'Price': {'N': '2'}, 'Title': {'S': 'Book 101 Title'}, 'ProductCategory': {'S': 'Book'}}, 'ConsumedCapacity': {'TableName': 'de-c2w1-dynamodb-ProductCatalog', 'CapacityUnits': 0.5}, 'ResponseMetadata': {'RequestId': 'JHD3INLPGG15LUL05NF1PB6SRRVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 23 Sep 2024 04:21:53 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '177', 'connection': 'keep-alive', 'x-amzn-requestid': 'JHD3INLPGG15LUL05NF1PB6SRRVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '685575682'}, 'RetryAttempts': 0}}


#### End of Optional Part - 2

<a name='5.3'></a>
### 5.3 - Query Items that Share the Same Partition Key

In DynamoDB, an item collection is a group of items that share the same partition key value, which means that items are related. You can query the items that belong to an item collection (i.e., that have the same partition key) using [DynamoDB query()](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/query.html) method. In this method, you need to specify the particular value of the partition key of the items in interest.

Item Collections only exist in tables that have both a Partition Key and a Sort Key. Optionally, you can provide the query method a sort key attribute and use a comparison operator to refine the search results.

In the following exercise, you will use the `Reply` table as it has both a Partition and a Sort key. Let's first check its content.


```python
response = scan_db(reply_table['table_name'])
print(response)
```

    {'Items': [{'ReplyDateTime': {'S': '2015-09-15T19:58:22.947Z'}, 'Message': {'S': 'DynamoDB Thread 1 Reply 1 text'}, 'PostedBy': {'S': 'User A'}, 'Id': {'S': 'Amazon DynamoDB#DynamoDB Thread 1'}}, {'ReplyDateTime': {'S': '2015-09-22T19:58:22.947Z'}, 'Message': {'S': 'DynamoDB Thread 1 Reply 2 text'}, 'PostedBy': {'S': 'User B'}, 'Id': {'S': 'Amazon DynamoDB#DynamoDB Thread 1'}}, {'ReplyDateTime': {'S': '2015-09-29T19:58:22.947Z'}, 'Message': {'S': 'DynamoDB Thread 2 Reply 1 text'}, 'PostedBy': {'S': 'User A'}, 'Id': {'S': 'Amazon DynamoDB#DynamoDB Thread 2'}}, {'ReplyDateTime': {'S': '2015-10-05T19:58:22.947Z'}, 'Message': {'S': 'DynamoDB Thread 2 Reply 2 text'}, 'PostedBy': {'S': 'User A'}, 'Id': {'S': 'Amazon DynamoDB#DynamoDB Thread 2'}}], 'Count': 4, 'ScannedCount': 4, 'ResponseMetadata': {'RequestId': 'DHP6GEQCSE36BF7RLDSAR5S2AFVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 23 Sep 2024 04:22:08 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '730', 'connection': 'keep-alive', 'x-amzn-requestid': 'DHP6GEQCSE36BF7RLDSAR5S2AFVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '1330173439'}, 'RetryAttempts': 0}}


Each reply in this table has an `Id` (Partition Key) that specifies in which thread the given reply appeared. The data consists of two threads in total that belong to the forum "Amazon DynamoDB", and each thread has 2 replies. Let's query the replies that belong to Thread 1. 

You will use the `query_db()` function defined below. This function calls the method `DynamoDB query()` which expects the particular value of the partition key and returns all items that have the specified partition key value. You can assume that the `kwargs` input of `query_db()` method contains the needed information (particular primary key value) for the `DynamoDB query()` method.


```python
def query_db(table_name: str,**kwargs,):
        client = boto3.client("dynamodb")

        try:
            response = client.query(
                TableName=table_name,
                **kwargs,
            )
            logging.info(f"Response {response}")
        except ClientError as e:
            error = e.response.get("Error", {})
            logging.error(
                f"Failed to query DynamoDB. Error: {error.get('Message')}"
            )
            raise
        else:
            logging.info(f"Query result {response.get('Items', {})}")
            return response
```

Now let's get into the details of the dictionary `kwargs` that is passed to `client.query()`.

The following cell shows an example of what `kwargs` should contain, as expected by the `DynamoDB query()` method:

`KeyConditionExpression`: is the condition that specifies the partition key value of the items that need to be retrieved; you can see in this syntax the name of the partition key which is `Id` and its particular value is denoted with another parameter `:Id` which is defined in the next argument `ExpressionAttributeValues`. To understand more about this syntax, you can always check the [documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/query.html). The parameter: `ReturnedConsumedCapacity` determines what level of detail about the consumed capacity the response should return.


```python
kwargs = {'ReturnConsumedCapacity': 'TOTAL', 
          'KeyConditionExpression': 'Id = :Id',
          'ExpressionAttributeValues': {':Id': {'S': 'Amazon DynamoDB#DynamoDB Thread 1'}}
          } 

# returns the items that has ID = 'Amazon DynamoDB#DynamoDB Thread 1'
response = query_db(table_name=reply_table['table_name'], **kwargs) 
               
print(response)
```

    {'Items': [{'ReplyDateTime': {'S': '2015-09-15T19:58:22.947Z'}, 'Message': {'S': 'DynamoDB Thread 1 Reply 1 text'}, 'PostedBy': {'S': 'User A'}, 'Id': {'S': 'Amazon DynamoDB#DynamoDB Thread 1'}}, {'ReplyDateTime': {'S': '2015-09-22T19:58:22.947Z'}, 'Message': {'S': 'DynamoDB Thread 1 Reply 2 text'}, 'PostedBy': {'S': 'User B'}, 'Id': {'S': 'Amazon DynamoDB#DynamoDB Thread 1'}}], 'Count': 2, 'ScannedCount': 2, 'ConsumedCapacity': {'TableName': 'de-c2w1-dynamodb-Reply', 'CapacityUnits': 0.5}, 'ResponseMetadata': {'RequestId': 'UPCPJTA04R22TEA23V7MP2TCQVVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 23 Sep 2024 04:22:37 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '462', 'connection': 'keep-alive', 'x-amzn-requestid': 'UPCPJTA04R22TEA23V7MP2TCQVVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '584739435'}, 'RetryAttempts': 0}}


You can also query the items that share the same partition key and also satisfy a certain condition on the sort key. Since the sort key of the Reply table is a timestamp, you can add a condition to `KeyConditionExpression` to get the replies of a particular thread that were posted after a certain time. Take a closer look at how the sort key is compared with the `:ts` parameter and how this parameter is defined in the `ExpressionAttributeValues`.


```python
kwargs = {'ReturnConsumedCapacity': 'TOTAL', 
          'KeyConditionExpression': 'Id = :Id and ReplyDateTime > :ts',
          'ExpressionAttributeValues': {':Id': {'S': 'Amazon DynamoDB#DynamoDB Thread 1'}, 
                               ':ts' : {'S':"2015-09-21"}
                               }
          }

response = query_db(table_name=reply_table['table_name'], **kwargs)

print(response)
```

    {'Items': [{'ReplyDateTime': {'S': '2015-09-22T19:58:22.947Z'}, 'Message': {'S': 'DynamoDB Thread 1 Reply 2 text'}, 'PostedBy': {'S': 'User B'}, 'Id': {'S': 'Amazon DynamoDB#DynamoDB Thread 1'}}], 'Count': 1, 'ScannedCount': 1, 'ConsumedCapacity': {'TableName': 'de-c2w1-dynamodb-Reply', 'CapacityUnits': 0.5}, 'ResponseMetadata': {'RequestId': 'V3OP7U9HHDPEVHG558QFAP947JVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 23 Sep 2024 04:22:41 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '289', 'connection': 'keep-alive', 'x-amzn-requestid': 'V3OP7U9HHDPEVHG558QFAP947JVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '4120834871'}, 'RetryAttempts': 0}}


In addition to `keyConditionExpression`, you can also use `FilterExpression` to filter the results based on non-key attributes. For example, to find all the replies to Thread 1 that were posted by User B, you can do:


```python
kwargs = {'ReturnConsumedCapacity': 'TOTAL', 
          'KeyConditionExpression': 'Id = :Id ',
          'FilterExpression': 'PostedBy = :user',
          'ExpressionAttributeValues': {':Id': {'S': 'Amazon DynamoDB#DynamoDB Thread 1'}, 
                               ':user' : {'S':'User B'}
                               }          
          }

response = query_db(table_name=reply_table['table_name'], **kwargs)

print(response)
```

    {'Items': [{'ReplyDateTime': {'S': '2015-09-22T19:58:22.947Z'}, 'Message': {'S': 'DynamoDB Thread 1 Reply 2 text'}, 'PostedBy': {'S': 'User B'}, 'Id': {'S': 'Amazon DynamoDB#DynamoDB Thread 1'}}], 'Count': 1, 'ScannedCount': 2, 'ConsumedCapacity': {'TableName': 'de-c2w1-dynamodb-Reply', 'CapacityUnits': 0.5}, 'ResponseMetadata': {'RequestId': '1IJAIUKN3FQ2CI7B1US47I5QUNVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 23 Sep 2024 04:22:47 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '289', 'connection': 'keep-alive', 'x-amzn-requestid': '1IJAIUKN3FQ2CI7B1US47I5QUNVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '3736314100'}, 'RetryAttempts': 0}}


Note that in the response you will see these lines:

```
"Count": 1,
"ScannedCount": 2,
```

This tells you that the Key Condition Expression matched 2 items (ScannedCount based on the value of the partition key) and that's what you were charged to read, but the Filter Expression reduced the result set size down to 1 item (Count).

<a name='ex06'></a>
### Exercise 6

Open the [documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/query.html) for the `DynamoDB query()` method and search for the `Limit` and `ScanIndexForward` parameters. In this exercise, you need to write the following query: return only the first reply to Thread 1.

<details>    
<summary>
    <font size="3" color="darkgreen"><b>Hint</b></font>
</summary>
<p>
<ul>
    Consider the <code>Limit</code> and <code>ScanIndexForward</code> parameters. If you want to sort items in ascending order based on the sort key, use the parameter <code>ScanIndexForward</code>. If you want to limit the number of items then use the <code>Limit</code> parameter. This would be analogous in SQL to: <code>ORDER BY ReplyDateTime ASC LIMIT 1</code>.
   
</ul>
</p>


```python
kwargs = {'ReturnConsumedCapacity': 'TOTAL', 
          'KeyConditionExpression': 'Id = :Id ',
          'ExpressionAttributeValues': {":Id" : {"S": "Amazon DynamoDB#DynamoDB Thread 1"}},
          ### START CODE HERE ### (~ 2 lines of code)
          'Limit': 1,
          'ScanIndexForward': True,
          ### END CODE HERE ###
          }

response = query_db(table_name=reply_table['table_name'], **kwargs)

print(response)
```

    {'Items': [{'ReplyDateTime': {'S': '2015-09-15T19:58:22.947Z'}, 'Message': {'S': 'DynamoDB Thread 1 Reply 1 text'}, 'PostedBy': {'S': 'User A'}, 'Id': {'S': 'Amazon DynamoDB#DynamoDB Thread 1'}}], 'Count': 1, 'ScannedCount': 1, 'LastEvaluatedKey': {'Id': {'S': 'Amazon DynamoDB#DynamoDB Thread 1'}, 'ReplyDateTime': {'S': '2015-09-15T19:58:22.947Z'}}, 'ConsumedCapacity': {'TableName': 'de-c2w1-dynamodb-Reply', 'CapacityUnits': 0.5}, 'ResponseMetadata': {'RequestId': '2CISH9T901L52H5A7FDN4IV8QNVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 23 Sep 2024 04:26:34 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '406', 'connection': 'keep-alive', 'x-amzn-requestid': '2CISH9T901L52H5A7FDN4IV8QNVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '284193681'}, 'RetryAttempts': 0}}


##### __Expected Output__ 

**Note:** The `'ResponseMetadata'` attribute can differ in your output. 

```
{'Items': [{'ReplyDateTime': {'S': '2015-09-15T19:58:22.947Z'}, 'Message': {'S': 'DynamoDB Thread 1 Reply 1 text'}, 'PostedBy': {'S': 'User A'}, 'Id': {'S': 'Amazon DynamoDB#DynamoDB Thread 1'}}], 'Count': 1, 'ScannedCount': 1, 'LastEvaluatedKey': {'Id': {'S': 'Amazon DynamoDB#DynamoDB Thread 1'}, 'ReplyDateTime': {'S': '2015-09-15T19:58:22.947Z'}}, 'ConsumedCapacity': {'TableName': 'de-c2w1-dynamodb-Reply', 'CapacityUnits': 0.5}, 'ResponseMetadata': {'RequestId': 'EMV7RBG34OOUCP0KS4LARC1B6BVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Wed, 14 Feb 2024 06:45:11 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '406', 'connection': 'keep-alive', 'x-amzn-requestid': 'EMV7RBG34OOUCP0KS4LARC1B6BVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '284193681'}, 'RetryAttempts': 0}}
```

<a name='ex07'></a>
### Exercise 7

Adjust the query to return only the most recent reply for Thread 1.


```python
kwargs = {'ReturnConsumedCapacity': 'TOTAL', 
          'KeyConditionExpression': 'Id = :Id ',
          'ExpressionAttributeValues': {":Id" : {"S": "Amazon DynamoDB#DynamoDB Thread 1"}},
          ### START CODE HERE ### (~ 2 lines of code)
          'Limit': 1,
          'ScanIndexForward': False,
          ### END CODE HERE ###
          }

response = query_db(table_name=reply_table['table_name'], **kwargs)

print(response)
```

    {'Items': [{'ReplyDateTime': {'S': '2015-09-22T19:58:22.947Z'}, 'Message': {'S': 'DynamoDB Thread 1 Reply 2 text'}, 'PostedBy': {'S': 'User B'}, 'Id': {'S': 'Amazon DynamoDB#DynamoDB Thread 1'}}], 'Count': 1, 'ScannedCount': 1, 'LastEvaluatedKey': {'Id': {'S': 'Amazon DynamoDB#DynamoDB Thread 1'}, 'ReplyDateTime': {'S': '2015-09-22T19:58:22.947Z'}}, 'ConsumedCapacity': {'TableName': 'de-c2w1-dynamodb-Reply', 'CapacityUnits': 0.5}, 'ResponseMetadata': {'RequestId': 'SVJ1F437LS54L5E5GE3QJNQEEVVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 23 Sep 2024 04:27:30 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '406', 'connection': 'keep-alive', 'x-amzn-requestid': 'SVJ1F437LS54L5E5GE3QJNQEEVVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '1848739007'}, 'RetryAttempts': 0}}


##### __Expected Output__ 

**Note:** The `'ResponseMetadata'` attribute can differ in your output. 

```
{'Items': [{'ReplyDateTime': {'S': '2015-09-22T19:58:22.947Z'}, 'Message': {'S': 'DynamoDB Thread 1 Reply 2 text'}, 'PostedBy': {'S': 'User B'}, 'Id': {'S': 'Amazon DynamoDB#DynamoDB Thread 1'}}], 'Count': 1, 'ScannedCount': 1, 'LastEvaluatedKey': {'Id': {'S': 'Amazon DynamoDB#DynamoDB Thread 1'}, 'ReplyDateTime': {'S': '2015-09-22T19:58:22.947Z'}}, 'ConsumedCapacity': {'TableName': 'de-c2w1-dynamodb-Reply', 'CapacityUnits': 0.5}, 'ResponseMetadata': {'RequestId': '7V1KQ1STK5C07EFR1DK0PGPBKFVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Wed, 14 Feb 2024 06:45:13 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '406', 'connection': 'keep-alive', 'x-amzn-requestid': '7V1KQ1STK5C07EFR1DK0PGPBKFVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '1848739007'}, 'RetryAttempts': 0}}
```

<a name='5.4'></a>
### 5.4 - Filtering the Table Scans

The `DynamoDB scan()` method is similar to the `DynamoDB query()` method except that you are scanning the whole table, not just a single Item Collection, so there is no Key Condition Expression that you need to specify for `DynamoDB scan()`. However, you can specify a `FilterExpression` which will reduce the size of the result set (even though it will not reduce the amount of capacity consumed).

For example, find all the replies in the Reply table that were posted by User A:


```python
kwargs = {'ReturnConsumedCapacity': 'TOTAL', 
          'FilterExpression': 'PostedBy = :user', 
          'ExpressionAttributeValues': {':user' : {'S':'User A'}}
        }

response = scan_db(reply_table['table_name'], **kwargs)
print(response)
```

    {'Items': [{'ReplyDateTime': {'S': '2015-09-15T19:58:22.947Z'}, 'Message': {'S': 'DynamoDB Thread 1 Reply 1 text'}, 'PostedBy': {'S': 'User A'}, 'Id': {'S': 'Amazon DynamoDB#DynamoDB Thread 1'}}, {'ReplyDateTime': {'S': '2015-09-29T19:58:22.947Z'}, 'Message': {'S': 'DynamoDB Thread 2 Reply 1 text'}, 'PostedBy': {'S': 'User A'}, 'Id': {'S': 'Amazon DynamoDB#DynamoDB Thread 2'}}, {'ReplyDateTime': {'S': '2015-10-05T19:58:22.947Z'}, 'Message': {'S': 'DynamoDB Thread 2 Reply 2 text'}, 'PostedBy': {'S': 'User A'}, 'Id': {'S': 'Amazon DynamoDB#DynamoDB Thread 2'}}], 'Count': 3, 'ScannedCount': 4, 'ConsumedCapacity': {'TableName': 'de-c2w1-dynamodb-Reply', 'CapacityUnits': 0.5}, 'ResponseMetadata': {'RequestId': 'MUP1UJV8HQE551MIU63N343TLJVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 23 Sep 2024 04:28:01 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '635', 'connection': 'keep-alive', 'x-amzn-requestid': 'MUP1UJV8HQE551MIU63N343TLJVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '771600284'}, 'RetryAttempts': 0}}


The response contains these fields:

```
"Count": 3,
"ScannedCount": 4,
```

This informs you that the `DynamoDB scan()` scanned all 4 items (`ScannedCount`) in the table and that's what you were charged to read, but the `FilterExpression` reduced the result set size down to 3 items (`Count`).

#### Start of Optional Part  - 3 (Last evaluated key)

When scanning data, the response may exceed the 1MB limit on the server side or surpass the specified `Limit` parameter. In such cases, the scan response will contain a `LastEvaluatedKey` field, allowing for subsequent scan calls to continue from where the previous scan left off. For instance, if the initial scan identified 3 items in the result set, running it again with a maximum item limit of 2 can demonstrate this behavior.


```python
kwargs = {'ReturnConsumedCapacity': 'TOTAL', 
          'FilterExpression': 'PostedBy = :user', 
          'ExpressionAttributeValues': {':user' : {'S':'User A'}},
          'Limit': 2
        }
response = scan_db(reply_table['table_name'], **kwargs)
print(response)
```

    {'Items': [{'ReplyDateTime': {'S': '2015-09-15T19:58:22.947Z'}, 'Message': {'S': 'DynamoDB Thread 1 Reply 1 text'}, 'PostedBy': {'S': 'User A'}, 'Id': {'S': 'Amazon DynamoDB#DynamoDB Thread 1'}}], 'Count': 1, 'ScannedCount': 2, 'LastEvaluatedKey': {'Id': {'S': 'Amazon DynamoDB#DynamoDB Thread 1'}, 'ReplyDateTime': {'S': '2015-09-22T19:58:22.947Z'}}, 'ConsumedCapacity': {'TableName': 'de-c2w1-dynamodb-Reply', 'CapacityUnits': 0.5}, 'ResponseMetadata': {'RequestId': 'EO98KSQCEDCQVNHNK0F5J4RLLVVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 23 Sep 2024 04:28:06 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '406', 'connection': 'keep-alive', 'x-amzn-requestid': 'EO98KSQCEDCQVNHNK0F5J4RLLVVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '1024212059'}, 'RetryAttempts': 0}}


Let's take the `LastEvaluatedKey` field and use it for the next table scan:


```python
last_evaluated_key = response.get("LastEvaluatedKey")
print(last_evaluated_key)
```

    {'Id': {'S': 'Amazon DynamoDB#DynamoDB Thread 1'}, 'ReplyDateTime': {'S': '2015-09-22T19:58:22.947Z'}}


So you can invoke the scan request again, this time passing that `LastEvaluatedKey` value to the `ExclusiveStartKey` parameter:


```python
kwargs = {'ReturnConsumedCapacity': 'TOTAL', 
          'FilterExpression': 'PostedBy = :user', 
          'ExpressionAttributeValues': {':user' : {'S':'User A'}},
          'Limit': 2,
          'ExclusiveStartKey': last_evaluated_key
        }

response = scan_db(reply_table['table_name'], **kwargs)
print(response)
```

    {'Items': [{'ReplyDateTime': {'S': '2015-09-29T19:58:22.947Z'}, 'Message': {'S': 'DynamoDB Thread 2 Reply 1 text'}, 'PostedBy': {'S': 'User A'}, 'Id': {'S': 'Amazon DynamoDB#DynamoDB Thread 2'}}, {'ReplyDateTime': {'S': '2015-10-05T19:58:22.947Z'}, 'Message': {'S': 'DynamoDB Thread 2 Reply 2 text'}, 'PostedBy': {'S': 'User A'}, 'Id': {'S': 'Amazon DynamoDB#DynamoDB Thread 2'}}], 'Count': 2, 'ScannedCount': 2, 'LastEvaluatedKey': {'Id': {'S': 'Amazon DynamoDB#DynamoDB Thread 2'}, 'ReplyDateTime': {'S': '2015-10-05T19:58:22.947Z'}}, 'ConsumedCapacity': {'TableName': 'de-c2w1-dynamodb-Reply', 'CapacityUnits': 0.5}, 'ResponseMetadata': {'RequestId': 'D5CUIJBK6MN4SMNBKGQF3NNJ5RVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 23 Sep 2024 04:28:13 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '579', 'connection': 'keep-alive', 'x-amzn-requestid': 'D5CUIJBK6MN4SMNBKGQF3NNJ5RVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '2067195067'}, 'RetryAttempts': 0}}


Check the data in the Forum table with a scan command to return only the Forums that have more than 1 thread and more than 50 views.

You can see that some items have a Threads number attribute and a Views number attribute. To solve this problem you want to use those attributes in the `FilterExpression`. Make sure to specify that these values are of the Number type by using "N" in the `--expression-attribute-values` parameter.

Since the `Views` attribute name is a DynamoDB Reserved Word, DynamoDB gives you the ability to put a placeholder in the `FilterExpression` and provide the actual attribute name in the `--expression-attribute-names` CLI parameter. For more information please see the [Expression Attribute Names](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Expressions.ExpressionAttributeNames.html) in DynamoDB in the Developer Guide.


```python
kwargs = {'ReturnConsumedCapacity': 'TOTAL', 
          'FilterExpression': 'Threads >= :threads AND #Views >= :views', 
          'ExpressionAttributeValues': {":threads" : {"N": "1"},
                                        ":views" : {"N": "50"}},
          'ExpressionAttributeNames':{"#Views" : "Views"}
        }

response = scan_db(forum_table['table_name'], **kwargs)
print(response)    
```

    {'Items': [{'Threads': {'N': '2'}, 'Category': {'S': 'Amazon Web Services'}, 'Messages': {'N': '4'}, 'Views': {'N': '1000'}, 'Name': {'S': 'Amazon DynamoDB'}}], 'Count': 1, 'ScannedCount': 2, 'ConsumedCapacity': {'TableName': 'de-c2w1-dynamodb-Forum', 'CapacityUnits': 0.5}, 'ResponseMetadata': {'RequestId': 'VNDUBVF0NGMLLLITPD39JEG70JVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 23 Sep 2024 04:28:18 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '250', 'connection': 'keep-alive', 'x-amzn-requestid': 'VNDUBVF0NGMLLLITPD39JEG70JVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '3574986003'}, 'RetryAttempts': 0}}


#### End of Optional Part - 3

<a name='6'></a>
## 6 - Insert and Update Data

<a name='6.1'></a>
### 6.1 - Insert Data

The `DynamoDB put_item()` method is used to create a new item or to replace existing items with a new item. You have already created the `put_item_db()` function to load data item-by-item to some tables. Now, let's say we wanted to insert a new item into the Reply table. You will see in the response that this request consumed 1 Write Capacity Unit (WCU) (One write capacity unit represents one write per second for an item up to 1 KB in size. [reference](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadWriteCapacityMode.html)).


```python
new_item = {
        "Id" : {"S": "Amazon DynamoDB#DynamoDB Thread 2"},
        "ReplyDateTime" : {"S": "2021-04-27T17:47:30Z"},
        "Message" : {"S": "DynamoDB Thread 2 Reply 3 text"},
        "PostedBy" : {"S": "User C"}
    }

kwargs = {'ReturnConsumedCapacity': 'TOTAL'}
    

response = put_item_db(table_name=reply_table["table_name"], item=new_item, **kwargs)
print(response)
```

    {'ConsumedCapacity': {'TableName': 'de-c2w1-dynamodb-Reply', 'CapacityUnits': 1.0}, 'ResponseMetadata': {'RequestId': 'F3SGA9NREUFKTQTNTRIK74D2BFVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 23 Sep 2024 04:28:34 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '79', 'connection': 'keep-alive', 'x-amzn-requestid': 'F3SGA9NREUFKTQTNTRIK74D2BFVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '4237884917'}, 'RetryAttempts': 0}}


<a name='6.2'></a>
### 6.2 - Update Data

The `DynamoDB update_item()` method can be used to edit an existing item's attributes or add a new item to the table if it does not already exist. "This method requires that you provide the primary key of the item that you want to update. You must also provide an update expression (`UpdateExpression`), indicating the attributes that you want to modify and the values that you want to assign to them" ([developer's guide](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/WorkingWithItems.html)). For more information about the format of the update expression, check [here](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Expressions.UpdateExpressions.html). You can also specify a condition expression to determine which items should be modified.
Take a look at the provided function below, where `ReturnValues='UPDATED_NEW'` returns only the updated attributes as they appear after the Update operation.


```python
def update_item_db(table_name: str, key: Dict[str, Any], **kwargs):
    client = boto3.client("dynamodb")

    response = client.update_item(
        TableName=table_name, Key=key, ReturnValues="UPDATED_NEW", **kwargs
    )

    return response
```


```python
kwargs= {    
    'UpdateExpression': 'SET Messages = :newMessages',
    'ConditionExpression': 'Messages = :oldMessages',
    'ExpressionAttributeValues': {
        ":oldMessages" : {"N": "4"},
        ":newMessages" : {"N": "5"}
    }
}
response = update_item_db(table_name=forum_table['table_name'], key={'Name' : {'S': 'Amazon DynamoDB'}}, **kwargs)
print(response)
```

    {'Attributes': {'Messages': {'N': '5'}}, 'ResponseMetadata': {'RequestId': 'U7LND2R8LLNGNJMA83BTNQN0T7VV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 23 Sep 2024 04:28:40 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '37', 'connection': 'keep-alive', 'x-amzn-requestid': 'U7LND2R8LLNGNJMA83BTNQN0T7VV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '1508008640'}, 'RetryAttempts': 0}}


This function updated the Forums that had the total number of messages as 4 so that now these forums have 5 messages.

<a name='ex08'></a>
### Exercise 8

Update the `de-c2w1-dynamodb-ProductCatalog` item with `Id="201"` to add new colors "Blue" and "Yellow" to the list of colors for that bike type. You are provided with the update expression which consisting of appending to a list of values. For more information, you can check the <a href="https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Expressions.UpdateExpressions.html">Update Expressions</a> page in the Developer Guide which has sections on Appending and Removing Elements in a List. </li>
   


You can use the `DyanamoDB get_item()` to verify that these changes were made after each step.


```python
kwargs = {
    'UpdateExpression': 'SET #Color = list_append(#Color, :values)',
    'ExpressionAttributeNames': {'#Color': 'Color'},
    'ExpressionAttributeValues': {':values': {'L': [{'S': 'Blue'}, {'S': 'Yellow'}]}},
    'ReturnConsumedCapacity': 'TOTAL'
}

### START CODE HERE ### (~ 1 line of code)
response = update_item_db(table_name=product_catalog_table['table_name'], key={'Id': {'N': '201'}}, **kwargs)
### END CODE HERE ###

print(response)
```

    {'Attributes': {'Color': {'L': [{'S': 'Red'}, {'S': 'Black'}, {'S': 'Blue'}, {'S': 'Yellow'}]}}, 'ConsumedCapacity': {'TableName': 'de-c2w1-dynamodb-ProductCatalog', 'CapacityUnits': 1.0}, 'ResponseMetadata': {'RequestId': 'E4PGGVO5HUJO09CG5TH1V5MI7JVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 23 Sep 2024 04:32:20 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '173', 'connection': 'keep-alive', 'x-amzn-requestid': 'E4PGGVO5HUJO09CG5TH1V5MI7JVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '3394722026'}, 'RetryAttempts': 0}}


##### __Expected Output__ 

```
{'Attributes': {'Color': {'L': [{'S': 'Red'}, {'S': 'Black'}, {'S': 'Blue'}, {'S': 'Yellow'}]}}, 'ConsumedCapacity': {'TableName': 'de-c2w1-dynamodb-ProductCatalog', 'CapacityUnits': 1.0}, 'ResponseMetadata': {'RequestId': 'D3CK6H42KF2DB9ITOO8K7UD95FVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Wed, 14 Feb 2024 06:45:33 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '173', 'connection': 'keep-alive', 'x-amzn-requestid': 'D3CK6H42KF2DB9ITOO8K7UD95FVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '3394722026'}, 'RetryAttempts': 0}}
```


```python
response = get_item_db(table_name=product_catalog_table['table_name'], 
                                      key={'Id': {'N': '201'}}
                                    )
print(response)
```

    {'Item': {'Title': {'S': '18-Bike-201'}, 'Price': {'N': '100'}, 'Brand': {'S': 'Mountain A'}, 'Color': {'L': [{'S': 'Red'}, {'S': 'Black'}, {'S': 'Blue'}, {'S': 'Yellow'}]}, 'Description': {'S': '201 Description'}, 'ProductCategory': {'S': 'Bicycle'}, 'Id': {'N': '201'}, 'BicycleType': {'S': 'Road'}}, 'ResponseMetadata': {'RequestId': '0JRP2M1MTGTDUPGEKVRS3U4NN3VV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 23 Sep 2024 04:32:28 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '271', 'connection': 'keep-alive', 'x-amzn-requestid': '0JRP2M1MTGTDUPGEKVRS3U4NN3VV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '3852755719'}, 'RetryAttempts': 0}}


<a name='ex09'></a>
### Exercise 9

In this exercise use the `update_item_db()` function to remove the list entries "Blue" and "Yellow" that you just added, to bring the bike item back to the original state. In DynamoDB, lists are 0-based indexed.


```python
kwargs = {
    'UpdateExpression': 'REMOVE #Color[2], #Color[3]',
    'ExpressionAttributeNames': {'#Color': 'Color'},
    'ReturnConsumedCapacity': 'TOTAL'
}

### START CODE HERE ### (~ 1 line of code)
response = update_item_db(table_name=product_catalog_table['table_name'], key={'Id': {'N': '201'}}, **kwargs)
### END CODE HERE ###

print(response)
```

    {'ConsumedCapacity': {'TableName': 'de-c2w1-dynamodb-ProductCatalog', 'CapacityUnits': 1.0}, 'ResponseMetadata': {'RequestId': 'SMJEFFIE99AAVT7EJOMSBQIU63VV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 23 Sep 2024 04:34:22 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '88', 'connection': 'keep-alive', 'x-amzn-requestid': 'SMJEFFIE99AAVT7EJOMSBQIU63VV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '866229524'}, 'RetryAttempts': 0}}


##### __Expected Output__ 

```
{'ConsumedCapacity': {'TableName': 'de-c2w1-dynamodb-ProductCatalog', 'CapacityUnits': 1.0}, 'ResponseMetadata': {'RequestId': 'CFU1SD9DECJOS6SLMVT3KT4CH7VV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Wed, 14 Feb 2024 06:45:37 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '88', 'connection': 'keep-alive', 'x-amzn-requestid': 'CFU1SD9DECJOS6SLMVT3KT4CH7VV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '866229524'}, 'RetryAttempts': 0}}
```


```python
response = get_item_db(table_name=product_catalog_table['table_name'], 
                                      key={'Id': {'N': '201'}}
                                    )
print(response)
```

    {'Item': {'Title': {'S': '18-Bike-201'}, 'Price': {'N': '100'}, 'Brand': {'S': 'Mountain A'}, 'Color': {'L': [{'S': 'Red'}, {'S': 'Black'}]}, 'Description': {'S': '201 Description'}, 'ProductCategory': {'S': 'Bicycle'}, 'Id': {'N': '201'}, 'BicycleType': {'S': 'Road'}}, 'ResponseMetadata': {'RequestId': 'P75P588IFJ36AFQ2B3TRF4AG8RVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 23 Sep 2024 04:34:28 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '243', 'connection': 'keep-alive', 'x-amzn-requestid': 'P75P588IFJ36AFQ2B3TRF4AG8RVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '2397163207'}, 'RetryAttempts': 0}}


<a name='7'></a>
## 7 - Delete Data

The `DynamoDB DeleteItem()` method is used to delete an item. Deletes in DynamoDB are singleton operations. There is no single command you can run that would delete all the rows in the table. Let's delete one of the items we previously added to the Reply table; for that, you need to reference the full Primary Key. Remember that the Reply table has `Id` as the partition key and `ReplyDateTime` as the sort key, so the complete Primary Key is composed of those two keys. Follow the instructions to create the `delete_item_db()` function.

<a name='ex10'></a>
### Exercise 10

1. Create the Client object `client`.
2. Use the `client.delete_item()` method of the client object. Make sure to add the table name and key parameters in the method call. The rest of the parameters should be passed as keyword arguments.


```python
def delete_item_db(table_name: str, key: dict[str, Any], **kwargs):
    ### START CODE HERE ### (~ 2 lines of code)
    client = boto3.client("dynamodb")
    response = client.delete_item(TableName=table_name, Key=key, **kwargs)
    ### END CODE HERE ###
    
    logging.info(f"response {response}")
```


```python
key = {"Id" : {"S": "Amazon DynamoDB#DynamoDB Thread 2"},
       "ReplyDateTime" : {"S": "2021-04-27T17:47:30Z"}
       }

delete_item_db(table_name=reply_table['table_name'], key=key)
```

The same item can be deleted more than once. You can run the same command above as many times as you want and it won't report any error: even if the key doesn't exist the method `DynamoDB delete_item()` returns success. Now, you have to decrement the related Forum *Messages* count: 


```python
kwargs= {    
    'UpdateExpression': 'SET Messages = :newMessages',
    'ConditionExpression': 'Messages = :oldMessages',
    'ExpressionAttributeValues': {
        ":oldMessages" : {"N": "5"},
        ":newMessages" : {"N": "4"}
    },
    'ReturnConsumedCapacity': 'TOTAL'
}

update_item_db(table_name=forum_table['table_name'], key={'Name' : {'S': 'Amazon DynamoDB'}}, **kwargs)

```




    {'Attributes': {'Messages': {'N': '4'}},
     'ConsumedCapacity': {'TableName': 'de-c2w1-dynamodb-Forum',
      'CapacityUnits': 1.0},
     'ResponseMetadata': {'RequestId': 'FRD37DI0FPQ3G2411VUKMOKQEJVV4KQNSO5AEMVJF66Q9ASUAAJG',
      'HTTPStatusCode': 200,
      'HTTPHeaders': {'server': 'Server',
       'date': 'Mon, 23 Sep 2024 04:36:01 GMT',
       'content-type': 'application/x-amz-json-1.0',
       'content-length': '115',
       'connection': 'keep-alive',
       'x-amzn-requestid': 'FRD37DI0FPQ3G2411VUKMOKQEJVV4KQNSO5AEMVJF66Q9ASUAAJG',
       'x-amz-crc32': '2262769511'},
      'RetryAttempts': 0}}



The next section is entirely optional. Feel free to skip it to go through the last section which is on cleanup.

<a name='8'></a>
## 8 - Transactions - Optional Section

The `DynamoDB transact_write_items` is a synchronous write operation that groups up to 100 action requests, with a collective size limit of 4MB for the entire transaction. These actions can operate on items in various tables, though not across distinct AWS accounts or Regions. Additionally, no two actions can target the same item. The execution of actions is atomic, ensuring that either all of them succeed or all of them fail.

You have seen that the sample data includes interconnected tables: `Forum`, `Thread`, and `Reply`. When adding a new `Reply` item, there's a need to increment the `Messages` count in the associated `Forum` item. This operation should occur within a transaction to guarantee that both changes either succeed or fail simultaneously. Any observer reading this data should witness both changes or none at the same time.
    
DynamoDB transactions adhere to the concept of **idempotency**, allowing the submission of the same transaction multiple times. However, DynamoDB will execute it only once. This feature is particularly valuable when working with APIs that lack inherent idempotency, such as using `update_item` to modify a numeric field. During transaction execution, you specify a string as the `ClientRequestToken` (also known as Idempotency Token). 
    

<a name='ex11'></a>
### Exercise 11

1. Create the Client object `client`.
2. Call the `DynamoDB transact_write_items()` method; explicitly pass the transaction items. Other parameters should be passed as keyword parameters.


```python
def transact_write_items_db(transaction_items: List[Dict[str, Any]], **kwargs):
    ### START CODE HERE ### (~ 2 lines of code)
    client = boto3.client("dynamodb")
    response = client.transact_write_items(TransactItems=transaction_items, **kwargs)
    ### END CODE HERE ###

    return response
```

Let's perform first the transaction by adding a new user to the `Reply` table.


```python
transaction_items=[
    {
        "Put": {
            "TableName" : reply_table['table_name'],
            "Item" : {
                "Id" : {"S": "Amazon DynamoDB#DynamoDB Thread 2"},
                "ReplyDateTime" : {"S": "2021-04-27T17:47:30Z"},
                "Message" : {"S": "DynamoDB Thread 2 Reply 3 text"},
                "PostedBy" : {"S": "User C"}
            }
        }
    },
    {
        "Update": {
            "TableName" : forum_table['table_name'],
            "Key" : {"Name" : {"S": "Amazon DynamoDB"}},
            "UpdateExpression": "ADD Messages :inc",
            "ExpressionAttributeValues" : { ":inc": {"N" : "1"} }
        }
    }
]

kwargs = {'ClientRequestToken': 'TRANSACTION1'}

response = transact_write_items_db(transaction_items=transaction_items, **kwargs)
print(response)
```

    {'ResponseMetadata': {'RequestId': '7K0NFDOQ6F2PDROI5J4CU5IBQVVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 23 Sep 2024 04:36:27 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '2', 'connection': 'keep-alive', 'x-amzn-requestid': '7K0NFDOQ6F2PDROI5J4CU5IBQVVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '2745614147'}, 'RetryAttempts': 0}}


After the transaction is finished, you can take a look at the Forum item and you'll see that the Messages count was incremented by 1, from 4 to 5.


```python
response = get_item_db(table_name=forum_table['table_name'], key={"Name" : {"S": "Amazon DynamoDB"}})
print(response)
```

    {'Item': {'Threads': {'N': '2'}, 'Category': {'S': 'Amazon Web Services'}, 'Messages': {'N': '5'}, 'Name': {'S': 'Amazon DynamoDB'}, 'Views': {'N': '1000'}}, 'ResponseMetadata': {'RequestId': 'H07H9EEIF05MV2AK9B3A2G04UBVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 23 Sep 2024 04:36:32 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '142', 'connection': 'keep-alive', 'x-amzn-requestid': 'H07H9EEIF05MV2AK9B3A2G04UBVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '1942891537'}, 'RetryAttempts': 0}}


If the transaction is executed again with the same value of the `'ClientRequestToken'` as `'TRANSACTION1'` you can see that other invocations of the transaction are ignored and the `Messages` attribute remains the value at 5. You can also use transactions to reverse the operation done before; take into account that there is a new value for the `ClientRequestToken` for this transaction:


```python
transaction_items=[
    {
        "Delete": {
            "TableName" : reply_table['table_name'],
            "Key" : {
                "Id" : {"S": "Amazon DynamoDB#DynamoDB Thread 2"},
                "ReplyDateTime" : {"S": "2021-04-27T17:47:30Z"}
            }
        }
    },
    {
        "Update": {
            "TableName" : forum_table['table_name'],
            "Key" : {"Name" : {"S": "Amazon DynamoDB"}},
            "UpdateExpression": "ADD Messages :inc",
            "ExpressionAttributeValues" : { ":inc": {"N" : "-1"} }
        }
    }
]

kwargs = {'ClientRequestToken': 'TRANSACTION2'}

response = transact_write_items_db(transaction_items=transaction_items, **kwargs)
print(response)
```

    {'ResponseMetadata': {'RequestId': 'GB8V53LL3ACARQOMCAPVANOTOVVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 23 Sep 2024 04:37:32 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '2', 'connection': 'keep-alive', 'x-amzn-requestid': 'GB8V53LL3ACARQOMCAPVANOTOVVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '2745614147'}, 'RetryAttempts': 0}}


<a name='9'></a>
## 9 - Cleanup

Delete the created tables from DynamoDB. Check the provided function in the next cell `delete_table_db()` and execute the next cells to delete the tables.


```python
def delete_table_db(table_name: str):
        client = boto3.client("dynamodb")
        response = client.delete_table(TableName=table_name)
        return response
```


```python
for dynamodb_tab in [product_catalog_table, forum_table, reply_table, thread_table]:
    response = delete_table_db(table_name=dynamodb_tab['table_name'])
    print(response)
```

    {'TableDescription': {'TableName': 'de-c2w1-dynamodb-ProductCatalog', 'TableStatus': 'DELETING', 'ProvisionedThroughput': {'NumberOfDecreasesToday': 0, 'ReadCapacityUnits': 10, 'WriteCapacityUnits': 5}, 'TableSizeBytes': 0, 'ItemCount': 0, 'TableArn': 'arn:aws:dynamodb:us-east-1:322144634018:table/de-c2w1-dynamodb-ProductCatalog', 'TableId': '8ca9426b-fae8-43d8-a39a-5ab8026ffb4e', 'DeletionProtectionEnabled': False}, 'ResponseMetadata': {'RequestId': 'K974B499CPPGGHKJPSK2ELIMUNVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 23 Sep 2024 04:37:39 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '399', 'connection': 'keep-alive', 'x-amzn-requestid': 'K974B499CPPGGHKJPSK2ELIMUNVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '3612788649'}, 'RetryAttempts': 0}}
    {'TableDescription': {'TableName': 'de-c2w1-dynamodb-Forum', 'TableStatus': 'DELETING', 'ProvisionedThroughput': {'NumberOfDecreasesToday': 0, 'ReadCapacityUnits': 10, 'WriteCapacityUnits': 5}, 'TableSizeBytes': 0, 'ItemCount': 0, 'TableArn': 'arn:aws:dynamodb:us-east-1:322144634018:table/de-c2w1-dynamodb-Forum', 'TableId': 'ee19182e-a625-429f-8c90-829a90ec2c19', 'DeletionProtectionEnabled': False}, 'ResponseMetadata': {'RequestId': '293HC0NJ641PCV4UPF9C9BVDAJVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 23 Sep 2024 04:37:39 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '381', 'connection': 'keep-alive', 'x-amzn-requestid': '293HC0NJ641PCV4UPF9C9BVDAJVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '145604652'}, 'RetryAttempts': 0}}
    {'TableDescription': {'TableName': 'de-c2w1-dynamodb-Reply', 'TableStatus': 'DELETING', 'ProvisionedThroughput': {'NumberOfDecreasesToday': 0, 'ReadCapacityUnits': 10, 'WriteCapacityUnits': 5}, 'TableSizeBytes': 0, 'ItemCount': 0, 'TableArn': 'arn:aws:dynamodb:us-east-1:322144634018:table/de-c2w1-dynamodb-Reply', 'TableId': '8556a55a-9bd0-426e-af19-dcc179d4e9d5', 'DeletionProtectionEnabled': False}, 'ResponseMetadata': {'RequestId': 'V962A40OG4NOT4H7M3L9CP1ADJVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 23 Sep 2024 04:37:40 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '381', 'connection': 'keep-alive', 'x-amzn-requestid': 'V962A40OG4NOT4H7M3L9CP1ADJVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '3671234206'}, 'RetryAttempts': 0}}
    {'TableDescription': {'TableName': 'de-c2w1-dynamodb-Thread', 'TableStatus': 'DELETING', 'ProvisionedThroughput': {'NumberOfDecreasesToday': 0, 'ReadCapacityUnits': 10, 'WriteCapacityUnits': 5}, 'TableSizeBytes': 0, 'ItemCount': 0, 'TableArn': 'arn:aws:dynamodb:us-east-1:322144634018:table/de-c2w1-dynamodb-Thread', 'TableId': '9f3c5685-8f81-427f-bc03-b05399ef6804', 'DeletionProtectionEnabled': False}, 'ResponseMetadata': {'RequestId': 'M0S41L1AK7AQDVRT4IDTIU028FVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 23 Sep 2024 04:37:40 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '383', 'connection': 'keep-alive', 'x-amzn-requestid': 'M0S41L1AK7AQDVRT4IDTIU028FVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '2613190991'}, 'RetryAttempts': 0}}


Finally, you can go to the AWS Console, search for **DynamoDB**, click on Tables, and check that the tables have been deleted.


```python

```
