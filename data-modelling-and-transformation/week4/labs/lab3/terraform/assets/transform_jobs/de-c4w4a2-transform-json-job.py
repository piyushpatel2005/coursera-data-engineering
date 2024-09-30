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
from pyspark.sql.functions import col, explode, lit, to_date, udf
from pyspark.sql.types import TimestampType

# Initialize Glue context and Spark session
args = getResolvedOptions(
    sys.argv,
    [
        "JOB_NAME",
        # "lakehouse_path",
        "catalog_database",
        "ingest_date",
        "users_source_path",
        "sessions_source_path",
        "target_bucket_path",
        "users_table",
        "sessions_table",
    ],
)

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

# Add Date UDF
def _to_timestamp(s):
    return datetime.fromisoformat(s)

udf_to_timestamp = udf(_to_timestamp, TimestampType())

# Define S3 paths
ingest_date_str = args["ingest_date"]
ingest_date = datetime.strptime(ingest_date_str, '%Y-%m-%d')
formatted_ingest_date= ingest_date.strftime("%Y_%m_%d")
s3_path_users = f"{args['users_source_path']}/ingest_on={formatted_ingest_date}"
s3_path_sessions = f"{args['sessions_source_path']}/ingest_on={formatted_ingest_date}"

# Read JSON data from S3
users_df = spark.read.json(s3_path_users)
sessions_df = spark.read.json(s3_path_sessions)

# Add ingestion and processing timestamp metadata
# Extract date for partitioning
users_df = users_df.withColumn(
    "ingest_on", to_date(lit(ingest_date_str), "yyyy-MM-dd")
)

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
    "ingest_on", to_date(lit(ingest_date_str), "yyyy-MM-dd")
)

print("sessions_df schema", sessions_df.printSchema())


processing_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

users_df = users_df.withColumn(
    "processing_timestamp", lit(processing_timestamp)
)
sessions_df = sessions_df.withColumn(
    "processing_timestamp", lit(processing_timestamp)
)

sessions_df = sessions_df.withColumn('session_ts',
                                     udf_to_timestamp(col('session_start_time')))

# Unnest the session_items in sessions_df
sessions_df = sessions_df.withColumn("session_item", explode("session_items"))
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
    col("session_ts").alias("session_start_time"),
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
