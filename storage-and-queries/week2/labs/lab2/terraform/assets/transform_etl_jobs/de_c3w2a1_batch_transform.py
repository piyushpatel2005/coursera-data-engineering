import sys
import numpy as np
import pandas as pd
from typing import Tuple
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pandas import DataFrame
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.types import StructType, StructField, StringType, \
    IntegerType, DoubleType, DateType, TimestampType

args = getResolvedOptions(sys.argv, ['JOB_NAME', 'data_lake_bucket'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)
data_lake_bucket = args['data_lake_bucket']
# set custom logging on
logger = glueContext.get_logger()

tables_schema = {
    "customers": StructType([
        StructField("customerNumber", IntegerType(), True),
        StructField("customerName", StringType(), True),
        StructField("contactLastName", StringType(), True),
        StructField("contactFirstName", StringType(), True),
        StructField("phone", StringType(), True),
        StructField("addressLine1", StringType(), True),
        StructField("addressLine2", StringType(), True),
        StructField("city", StringType(), True),
        StructField("state", StringType(), True),
        StructField("postalCode", StringType(), True),
        StructField("country", StringType(), True),
        StructField("salesRepEmployeeNumber", IntegerType(), True),
        StructField("creditLimit", DoubleType(), True)
    ]),
    "employees": StructType([
        StructField("employeeNumber", IntegerType(), True),
        StructField("lastName", StringType(), True),
        StructField("firstName", StringType(), True),
        StructField("extension", StringType(), True),
        StructField("email", StringType(), True),
        StructField("officeCode", StringType(), True),
        StructField("reportsTo", IntegerType(), True),
        StructField("jobTitle", StringType(), True)
    ]),
    "offices": StructType([
        StructField("officeCode", StringType(), True),
        StructField("city", StringType(), True),
        StructField("phone", StringType(), True),
        StructField("addressLine1", StringType(), True),
        StructField("addressLine2", StringType(), True),
        StructField("state", StringType(), True),
        StructField("country", StringType(), True),
        StructField("postalCode", StringType(), True),
        StructField("territory", StringType(), True)
    ]),
    "orderdetails": StructType([
        StructField("orderNumber", IntegerType(), True),
        StructField("productCode", StringType(), True),
        StructField("quantityOrdered", IntegerType(), True),
        StructField("priceEach", DoubleType(), True),
        StructField("orderLineNumber", IntegerType(), True)
    ]),
    "orders": StructType([
        StructField("orderNumber", IntegerType(), True),
        StructField("orderDate", DateType(), True),
        StructField("requiredDate", DateType(), True),
        StructField("shippedDate", DateType(), True),
        StructField("status", StringType(), True),
        StructField("comments", StringType(), True),
        StructField("customerNumber", IntegerType(), True)
    ]),
    "payments": StructType([
        StructField("customerNumber", IntegerType(), True),
        StructField("checkNumber", StringType(), True),
        StructField("paymentDate", DateType(), True),
        StructField("amount", DoubleType(), True)
    ]),
    "productlines": StructType([
        StructField("productLine", StringType(), True),
        StructField("textDescription", StringType(), True),
        StructField("htmlDescription", StringType(), True),
        StructField("image", StringType(), True)
    ]),
    "products": StructType([
        StructField("productCode", StringType(), True),
        StructField("productName", StringType(), True),
        StructField("productLine", StringType(), True),
        StructField("productScale", StringType(), True),
        StructField("productVendor", StringType(), True),
        StructField("productDescription", StringType(), True),
        StructField("quantityInStock", IntegerType(), True),
        StructField("buyPrice", DoubleType(), True),
        StructField("MSRP", DoubleType(), True)
    ])
}


def add_metadata(source_pd: DataFrame,
                 source_schema: StructType) -> Tuple[DataFrame, StructType]:
    """Add ingest_ts and source metadata to the raw data located in a dataframe
    also add to the schema the new columns related to metadata.

    Args:
        source_pd (DataFrame): Dataframe containing the source table data.
        source_schema (StructType): Schema associated to the source table

    Returns:
        Tuple[DataFrame, StructType]: updated Dataframe and schema
    """
    source_pd['ingest_ts'] = pd.Timestamp("now")
    ### START CODE HERE ### (2 lines of code)

    # Replace `None` with the appropriate `source` metadata string, which will be the "classic_models_mysql".
    source_pd['source'] = "None"

    # Add the current timestamp as a column named `ingest_ts` into the current schema `source_schema`. 
    # You can use the function `StructField()` passing the `TimestampType()` as an argument.
    source_schema.add(None("None", TimestampType(), True))
    ### END CODE HERE ###

    source_schema.add(StructField("source", StringType(), True))
    return source_pd, source_schema


def enforce_schema(source_pd: DataFrame,
                   source_schema: StructType) -> DataFrame:
    """Cast the columns of the source DataFrame to comply with the provided schema

    Args:
        source_pd (DataFrame): Dataframe containing the source table data.
        source_schema (StructType): Schema associated to the source table

    Returns:
        DataFrame: Dataframe with the correct data types for each column.
    """
    source_schema_dict = {name: field.dataType for name, field in zip(
        source_schema.names, source_schema.fields)}
    for field_name, field_type in source_schema_dict.items():

        ### START CODE HERE ### (10 lines of code)

        # Check if the field type is an integer type replacing `None` with the `IntegerType`.
        if isinstance(field_type, None):
            source_pd[field_name] = pd.to_numeric(source_pd[field_name], errors='coerce')
            source_pd[field_name] = source_pd[field_name].replace(np.nan, 0)
            source_pd[field_name] = source_pd[field_name].astype(np.int64)
        elif isinstance(field_type, DoubleType):

            # Handle the DoubleType case similar to the IntegerType case above.
            # Use pd.to_numeric with errors='coerce'.
            source_pd[field_name] = pd.None(None[None], None='None')

            # Replace np.nan with `0.0`.
            source_pd[field_name] = None[None].None(None.None, 0.0)

            # Convert the column to `np.float16` using `astype()` method.
            source_pd[field_name] = None[None].None(None.None)
        
        # Check if the field type is an date type replacing `None` with the `DateType`.
        elif isinstance(field_type, None):

            # Convert the column to datetime using `to_datetime` method.
            source_pd[field_name] = pd.None(None[None])

        ### END CODE HERE ###
    return source_pd


for table_name, table_schema in tables_schema.items():
    # Read file as Pyspark DataFrame
    source_data_df = spark.read\
        .option("header", "true")\
        .option("delimiter", ";")\
        .option("lineSep", "\t")\
        .csv(f"s3://{data_lake_bucket}/landing_zone/rds/{table_name}")
    # Convert to Pandas DataFrame
    source_data_pd = source_data_df.toPandas()
    # Enforce schema
    source_data_pd = enforce_schema(source_data_pd,
                                    table_schema)
    logger.info(f"enforced schema done for {table_name}")
    # Add metadata
    target_pd, target_schema = add_metadata(source_data_pd, table_schema)
    logger.info(f"add metadata done for {table_name}")
    # Cconvert back to PySpark DataFrame with the schema
    target_data_df = spark.createDataFrame(target_pd, schema=target_schema)
    # Write data into silver location and glue catalog
    target_data_path = f"s3://{data_lake_bucket}/curated_zone/{table_name}"
    target_data = DynamicFrame.fromDF(target_data_df, glueContext,
                                      "target_data")
    sink = glueContext.getSink(connection_type="s3", path=target_data_path,
                               enableUpdateCatalog=True,
                               updateBehavior="UPDATE_IN_DATABASE",
                               partitionKeys=[],
                               compression="snappy"
                               )
    sink.setFormat("parquet", useGlueParquetWriter=True)
    sink.setCatalogInfo(catalogDatabase='curated_zone',
                        catalogTableName=table_name)
    sink.writeFrame(target_data)
    logger.info(f"write done for {table_name}")
job.commit()
