import sys

import boto3
import numpy as np
import pandas as pd
from awsglue import DynamicFrame
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from botocore.exceptions import *
from pandas import DataFrame
from pyspark.conf import SparkConf
from pyspark.context import SparkContext

# from pyspark.sql.functions import current_timestamp
from pyspark.sql import functions as F
from pyspark.sql.types import (
    DateType,
    DecimalType,
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)


def sparkSqlQuery(
    glueContext, query, mapping, transformation_ctx
) -> DynamicFrame:
    for alias, frame in mapping.items():
        frame.toDF().createOrReplaceTempView(alias)
    result = spark.sql(query)
    return DynamicFrame.fromDF(result, glueContext, transformation_ctx)


# Get the AWS ACCOUNT ID where the Glue job is running
aws_account_id = boto3.client("sts").get_caller_identity().get("Account")

args = getResolvedOptions(
    sys.argv,
    [
        "JOB_NAME",
        "data_lake_bucket",
        "database_name",
        "ml_table",
        "lakehouse_path",
    ],
)

# Set up configuration for AWS Glue to work with Apache Iceberg
conf = SparkConf()
conf.set(
    "spark.sql.extensions",
    "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
)
conf.set(
    "spark.sql.catalog.glue_catalog", "org.apache.iceberg.spark.SparkCatalog"
)
conf.set("spark.sql.catalog.glue_catalog.warehouse", args["lakehouse_path"])
conf.set(
    "spark.sql.catalog.glue_catalog.catalog-impl",
    "org.apache.iceberg.aws.glue.GlueCatalog",
)
conf.set(
    "spark.sql.catalog.glue_catalog.io-impl",
    "org.apache.iceberg.aws.s3.S3FileIO",
)
conf.set("spark.sql.catalog.glue_catalog.glue.lakeformation-enabled", "true")
conf.set("spark.sql.catalog.glue_catalog.glue.id", aws_account_id)

sc = SparkContext(conf=conf)
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)
logger = glueContext.get_logger()

data_lake_bucket = args["data_lake_bucket"]
database_name = args["database_name"]
table_name = args["ml_table"]


# Reading Customers from landing zone
customers_df = (
    spark.read.option("header", "true")
    .option("delimiter", ";")
    .option("lineSep", "\t")
    .csv(f"s3://{data_lake_bucket}/landing_zone/rds/customers")
)

customers = DynamicFrame.fromDF(customers_df, glueContext, "customers")

# Reading Products from landing zone
products_df = (
    spark.read.option("header", "true")
    .option("delimiter", ";")
    .option("lineSep", "\t")
    .csv(f"s3://{data_lake_bucket}/landing_zone/rds/products")
)

products = DynamicFrame.fromDF(products_df, glueContext, "products")

# Reading Ratings Amazon S3
json_ratings = glueContext.create_dynamic_frame.from_options(
    format_options={"multiline": False},
    connection_type="s3",
    format="json",
    connection_options={
        "paths": [f"s3://{data_lake_bucket}/landing_zone/json/ratings/"],
        "recurse": True,
    },
    transformation_ctx="json_ratings",
)

# SQL Query to pull out all ratings with the most recent `ingest_ts` timestamp.
SqlQuery0 = """
select * 
from ratings 
where ingest_ts = (select max(ingest_ts) from ratings)
;
"""

lastest_ingested_ratings = sparkSqlQuery(
    glueContext,
    query=SqlQuery0,
    mapping={"ratings": json_ratings},
    transformation_ctx="lastest_ingested_ratings",
)

# Extract the following columns:
# `customerNumber` (casted as INTEGER. Keep the same name), `city`, `state`, `postalCode`, `country` and `creditLimit` from the `customers` table.
# `productCode` and `productRating` from the `ratings` table. 
# `productLine`, `productScale`, `quantityInStock`, `buyPrice` and `MSRP` from the `products` table.
# You will need to join the `ratings`, `products` and `customers` tables in the following way:
# `ratings` and `products` can be joined by the `productCode` column. The name is shared across the two tables.
# `ratings` and `customers` can be joined by the `customerNumber` column, which is a column name shared across the two tables.
SqlQuery1 = """
select cast(c.None as INTEGER) as customerNumber
, c.None
, c.None
, c.None
, c.None
, c.None
, r.None
, r.None
, p.None
, p.None
, p.None
, p.None
, p.None
from ratings r 
join products p on p.None = r.None 
join customers c on c.None = r.None;
"""

customers_products_ratings_join = sparkSqlQuery(
    glueContext,
    query=SqlQuery1,
    mapping={
        "customers": customers,
        "products": products,
        "ratings": lastest_ingested_ratings,
    },
    transformation_ctx="customers_products_ratings_join",
)

# Script generated for node Add Current Timestamp
joined_data_df = customers_products_ratings_join.toDF()
joined_data_df = joined_data_df.withColumn("process_ts", F.current_timestamp())
joined_data_df = joined_data_df.withColumn(
    "creditLimit", F.col("creditLimit").cast(DecimalType(10, 0))
)
joined_data_df = joined_data_df.withColumn(
    "quantityinstock", F.col("quantityinstock").cast(IntegerType())
)
joined_data_df = joined_data_df.withColumn(
    "buyprice", F.col("buyprice").cast(DecimalType(10, 0))
)
joined_data_df = joined_data_df.withColumn(
    "msrp", F.col("msrp").cast(DecimalType(10, 0))
)


# Saving transformed data in Iceberg format into AWS S3
additional_options = {"write.parquet.compression-codec": "gzip"}


glue_catalog_to_write = f"glue_catalog.{database_name}.{table_name}"
print(f"glue_catalog_to_write: {glue_catalog_to_write}")

# if table_exists:
try:
    joined_data_df.sortWithinPartitions("country").writeTo(
        glue_catalog_to_write
    ).tableProperty("format-version", "2").tableProperty(
        "location",
        f"s3://{data_lake_bucket}/{database_name}/{table_name}/iceberg",
    ).options(
        **additional_options
    ).partitionedBy(
        "country"
    ).append()

except Exception as err:
    joined_data_df.sortWithinPartitions("country").writeTo(
        glue_catalog_to_write
    ).tableProperty("format-version", "2").tableProperty(
        "location",
        f"s3://{data_lake_bucket}/{database_name}/{table_name}/iceberg",
    ).options(
        **additional_options
    ).partitionedBy(
        "country"
    ).create()


job.commit()
