import json
import sys
from datetime import datetime

from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.conf import SparkConf
from pyspark.context import SparkContext
from pyspark.sql.functions import col, explode, lit, to_date

# Initialize Glue context and Spark session
# Take a look to the `args` object with the parameters required to run the Job
args = getResolvedOptions(
    sys.argv,
    [
        "JOB_NAME",
        # "lakehouse_path",
        # The Glue Catalog database name
        "catalog_database",
        # The date where data was ingested. This is your current date
        "ingest_date",
        # Object's path in the source Data Lake for the users data
        "users_source_path",
        # Object's path in the source Data Lake for the sessions data
        "sessions_source_path",
        # Object's path in the destination Data Lake
        "target_bucket_path",
        # Name of the users table inside the Glue Catalog Database
        "users_table",
        # Name of the sessions table inside the Glue Catalog Database.
        "sessions_table",
    ],
)

# The Glue Job has been configured to store data in Apache Iceberg Format
conf = SparkConf()
conf.set(
    "spark.sql.extensions",
    "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
)
conf.set(
    "spark.sql.catalog.glue_catalog", "org.apache.iceberg.spark.SparkCatalog"
)
conf.set(
    "spark.sql.catalog.glue_catalog.warehouse",
    f"s3://{args['target_bucket_path']}/transform_zone",
)
conf.set(
    "spark.sql.catalog.glue_catalog.catalog-impl",
    "org.apache.iceberg.aws.glue.GlueCatalog",
)
conf.set(
    "spark.sql.catalog.glue_catalog.io-impl",
    "org.apache.iceberg.aws.s3.S3FileIO",
)

sc = SparkContext(conf=conf)
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)
spark.conf.set("spark.sql.sources.partitionOverwriteMode", "dynamic")
logger = glueContext.get_logger()

# Define S3 paths
ingestion_timestamp = args["ingest_date"]
s3_path_users = f"{args['users_source_path']}/{ingestion_timestamp}"
s3_path_sessions = f"{args['sessions_source_path']}/{ingestion_timestamp}"

# Read JSON data from S3
# In this Glue job, the datasets are created directy as Spark Dataframes. Use the `s3_path_users` and `s3_path_sessions` as argument inside 
# The `spark.read.json()` method respectively for the users, `users_df`, and sessions, `sessions_df`, dataframes
users_df = spark.read.json(s3_path_users)
sessions_df = spark.read.json(s3_path_sessions)

# Add ingestion and processing timestamp metadata
# Extract date for partitioning
users_df = users_df.withColumn(
    "ingest_on", to_date(lit(ingestion_timestamp), "yyyy-MM-dd")
)

# For the `users_df` you are already provided with the `"ingest_on"` column. On the other hand, remember from your initial exploration that there 
# Is a field named `user_location`. This field is actually an array; you are already provided with an example on how to extract an element from 
# This array to create the `"latitude"` column. Now you will create the `"longitude"`, `"place_name"`, `"country_code"` and `"timezone"` columns 
# based on the other elements of the `user_location` field.
users_df = (
    users_df.withColumn("latitude", col("user_location")[0])
    .withColumn("longitude", col("user_location")[1])
    .withColumn("place_name", col("user_location")[2])
    .withColumn("country_code", col("user_location")[3])
    .withColumn("timezone", col("user_location")[4])
    .drop("user_location")
)

print("users_df schema", users_df.printSchema())

sessions_df = sessions_df.withColumn(
    "ingest_on", to_date(lit(ingestion_timestamp), "yyyy-MM-dd")
)
print("sessions_df schema", sessions_df.printSchema())


processing_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

users_df = users_df.withColumn(
    "processing_timestamp", lit(processing_timestamp)
)
sessions_df = sessions_df.withColumn(
    "processing_timestamp", lit(processing_timestamp)
)


# Unnest the session_items in sessions_df
# For the `sessions_df`, you have `session_items` field, which is a JSON object
# You will create a new item named `"session_item"` by applying the `explode()` method to the `session_items` field
sessions_df = sessions_df.withColumn("session_item", explode("session_items"))

# Then, you will apply the `select` method of the `sessions_df` Spark Dataframe with the `col()` method to select the required columns
sessions_df = sessions_df.select(
    col("user_id"),
    col("session_id"),
    col("session_item.song_id").alias("song_id"),
    col("session_item.song_name").alias("song_name"),
    col("session_item.artist_id").alias("artist_id"),
    col("session_item.artist_name").alias("artist_name"),
    col("session_item.price").alias("price"),
    col("session_item.currency").alias("currency"),
    col("session_item.liked").alias("liked"),
    col("session_item.liked_since").alias("liked_since"),
    col("user_agent"),
    col("session_start_time"),
    col("ingest_on"),
)

print("users_df schema", users_df.printSchema())
print("sessions_df schema", sessions_df.printSchema())

print("users_df schema", users_df.show(5))
print("sessions_df schema", sessions_df.show(5))


# Writing data
catalog_database = args["catalog_database"]
users_table_name = args["users_table"]
sessions_table_name = args["sessions_table"]
target_bucket_path = args["target_bucket_path"]

tables_collection = spark.catalog.listTables(catalog_database)
tables_in_db = [table.name for table in tables_collection]

users_table_exists = users_table_name in tables_in_db
sessions_table_exists = sessions_table_name in tables_in_db

print("Saving users_df")

# Users
if users_table_exists:

    users_df.writeTo(
        f"glue_catalog.{catalog_database}.{users_table_name}"
    ).tableProperty("format-version", "2").partitionedBy("ingest_on").append()

else:
    # Create (equivalent to CREATE TABLE AS SELECT)
    users_df.writeTo(
        f"glue_catalog.{catalog_database}.{users_table_name}"
    ).tableProperty("format-version", "2").partitionedBy(
        "ingest_on"
    ).createOrReplace()


print("Saved users_df")
print("Saving sessions_df")

# sessions
if sessions_table_exists:
    # Append (equivalent to INSERT INTO)
    sessions_df.writeTo(
        f"glue_catalog.{catalog_database}.{sessions_table_name}"
    ).tableProperty("format-version", "2").partitionedBy("ingest_on").append()

else:
    # Create (equivalent to CREATE TABLE AS SELECT)
    sessions_df.writeTo(
        f"glue_catalog.{catalog_database}.{sessions_table_name}"
    ).tableProperty("format-version", "2").partitionedBy(
        "ingest_on"
    ).createOrReplace()


print("Saved sessions_df")


# Commit job
job.commit()
