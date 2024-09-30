import sys
from datetime import date, datetime

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext

args = getResolvedOptions(
    sys.argv,
    [
        "JOB_NAME",
        "rds_connection",
        "data_lake_bucket",
        "ingest_date"
    ],
)
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

rds_connection = args["rds_connection"]
data_lake_bucket = args["data_lake_bucket"]
ingest_date_str = args["ingest_date"]

# Script generated for node Relational DB
source_node = glueContext.create_dynamic_frame.from_options(
    connection_type="postgresql",
    connection_options={
        "useConnectionProperties": "true",
        "dbtable": "deftunes.songs",
        "connectionName": rds_connection,
    },
    transformation_ctx="source_node",
)
ingest_date = datetime.strptime(ingest_date_str, '%Y-%m-%d')
s3_path = (
    "s3://{}/landing_zone/db_songs/ingest_on={}"
).format(data_lake_bucket, ingest_date.strftime("%Y_%m_%d"))
# Script generated for node Amazon S3
target_node = glueContext.write_dynamic_frame.from_options(
    frame=source_node,
    connection_type="s3",
    format="csv",
    connection_options={"path": s3_path, "partitionKeys": []},
    transformation_ctx="target_node",
)

job.commit()
