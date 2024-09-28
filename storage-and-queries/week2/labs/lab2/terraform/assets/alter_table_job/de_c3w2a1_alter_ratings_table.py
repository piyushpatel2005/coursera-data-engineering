import sys
import traceback

import boto3
from awsglue.context import GlueContext

# from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from botocore.exceptions import *
from pyspark.conf import SparkConf
from pyspark.context import SparkContext
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Get the AWS ACCOUNT ID where the Glue job is running
aws_account_id = boto3.client("sts").get_caller_identity().get("Account")

# Read Job Parameters
args = getResolvedOptions(
    sys.argv,
    [
        "JOB_NAME",
        "lakehouse_path",
        "database_name",
        "table_name",
        "column_name",
        "column_type",        
    ],
)

database_name = args["database_name"]
table_name = args["table_name"]

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


def add_column(database_name, table_name, column_name, column_type):
    try:
        sql_stmt = f"""
            ALTER TABLE glue_catalog.{database_name}.{table_name}
                ADD COLUMNS 
                (
                    {column_name} {column_type}
                )
            """
        logger.info(f"Executing SQL statement : {sql_stmt} \n")
        spark.sql(sql_stmt)

    except Exception as e:
        traceback_error = traceback.format_exc()
        logger.error(
            f"Error while adding the column {column_name} to {database_name}.{table_name}. {traceback_error} {e} \n"
        )
        sys.exit(
            f"Error while adding the column {column_name} to {database_name}.{table_name} {e} \n"
        )


# Execute Function

# Add a new column: ratingtimestamp as string
column_name = args["column_name"]  # "ratingtimestamp"
column_type = args["column_type"]  # "string"
add_column(database_name, table_name, column_name, column_type)

job.commit()
