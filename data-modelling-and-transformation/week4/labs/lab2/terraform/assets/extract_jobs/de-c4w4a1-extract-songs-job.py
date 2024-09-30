import sys
from datetime import date

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext

# See the parameters that it receives in the `args` object. 
# Apart from the `"JOB_NAME"`, this script requires the RDS connection and the name of the S3 bucket that will be used as Data Lake.
args = getResolvedOptions(
    sys.argv,
    [
        "JOB_NAME",
        "rds_connection",
        "data_lake_bucket"
    ],
)
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

rds_connection = args["rds_connection"]
data_lake_bucket = args["data_lake_bucket"]

# Script generated for node Relational DB
# Complete the parameters to create the dynamic frame
source_node = glueContext.create_dynamic_frame.from_options(
    # Set `connection_type` to `"postgresql"`
    connection_type="postgresql",
    # Set `connection_options`
    connection_options={
        "useConnectionProperties": "true",
        # Set `"dbtable"` to `"deftunes.songs"`
        "dbtable": "deftunes.songs",
        # Set `"connectionName"` to the `rds_connection` object that has already been defined
        "connectionName": rds_connection,
    },
    transformation_ctx="source_node",
)
# Set `ingest_day` to `date.today()`.
ingest_day = date.today()
s3_path = (
    "s3://{}/landing_zone/db_songs/ingest_on={}"
).format(data_lake_bucket, ingest_day.strftime("%Y_%m_%d"))
# Script generated for node Amazon S3
# Prepare the `target_node` object
target_node = glueContext.write_dynamic_frame.from_options(
    # Set `frame` to the `source_node` object
    frame=source_node,
    # Set `connection_type` to `"s3"`
    connection_type="s3",
    # Set the output `format` to `"csv"`
    format="csv",
    # In `connection_options` set the `"path"` to the provided `s3_path` string and leave the partition keys as an empty list
    connection_options={"path": s3_path, "partitionKeys": []},
    transformation_ctx="target_node",
)

job.commit()