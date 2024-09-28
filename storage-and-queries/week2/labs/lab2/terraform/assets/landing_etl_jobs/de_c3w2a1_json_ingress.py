import sys

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import current_timestamp

args = getResolvedOptions(
    sys.argv, ["JOB_NAME", "source_data_lake_bucket", "dest_data_lake_bucket"]
)
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

source_data_lake_bucket = args["source_data_lake_bucket"]
dest_data_lake_bucket = args["dest_data_lake_bucket"]

# Reading source dataset
source_ratings_json = glueContext.create_dynamic_frame.from_options(
    format_options={"multiline": False},
    connection_type="s3",
    format="json",
    connection_options={
        # "paths": [f"s3://{source_data_lake_bucket}/ratings_with_timestamp/"],
        "paths": [f"s3://{source_data_lake_bucket}/ratings/"],
        "recurse": True,
    },
    transformation_ctx="source_ratings_json",
)

# Add Current Timestamp as ingestion timestamp
source_ratings_json_df = source_ratings_json.toDF()
source_ratings_json_df = source_ratings_json_df.withColumn(
    "ingest_ts", current_timestamp()
)


# Saving to S3 in json format, no partitions
source_ratings_json_df.write.mode("overwrite").format("json").save(
    f"s3://{dest_data_lake_bucket}/landing_zone/json/ratings"
)

job.commit()
