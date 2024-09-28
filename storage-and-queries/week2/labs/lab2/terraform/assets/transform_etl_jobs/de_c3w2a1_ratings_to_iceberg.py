import sys
import traceback

import boto3
from awsglue import DynamicFrame
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from botocore.exceptions import *
from pyspark.conf import SparkConf
from pyspark.context import SparkContext
from pyspark.sql.functions import current_timestamp


def sparkSqlQuery(
    glueContext, query, mapping, transformation_ctx
) -> DynamicFrame:
    for alias, frame in mapping.items():
        frame.toDF().createOrReplaceTempView(alias)
    result = spark.sql(query)
    return DynamicFrame.fromDF(result, glueContext, transformation_ctx)


def spark_shape(frame):
    df = frame.toDF()
    return (df.count(), len(df.columns))


def show_df(frame):
    df = frame.toDF()
    return df.show(5)


# Get the AWS ACCOUNT ID where the Glue job is running
aws_account_id = boto3.client("sts").get_caller_identity().get("Account")

args = getResolvedOptions(
    sys.argv,
    [
        "JOB_NAME",
        "data_lake_bucket",
        "database_name",
        "table_name",
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
table_name = args["table_name"]

glue_client = boto3.client("glue")
response = glue_client.get_tables(DatabaseName = database_name)
curated_tables_list = response["TableList"]
curated_table_names = [tableDict["Name"] for tableDict in curated_tables_list]
table_exists = table_name in curated_table_names

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

logger.info(f"json_ratings shape: {spark_shape(json_ratings)}")
logger.info(f"json_ratings show: {show_df(json_ratings)}")

logger.info(f"json_ratings has been read: {json_ratings.schema()}")
logger.info(f"json_ratings has been read: {json_ratings.printSchema()}")

# SQL Query to pull out all ratings with the most recent `ingest_ts` timestamp.
SqlQuery0 = """
select * 
from None 
where None = (select None(None) from None)
;
"""

lastest_ingested_ratings = sparkSqlQuery(
    glueContext,
    query=SqlQuery0,
    mapping={"ratings": json_ratings},
    transformation_ctx="lastest_ingested_ratings",
)


logger.info(
    f"lastest_ingested_ratings shape: {spark_shape(lastest_ingested_ratings)}"
)
logger.info(
    f"lastest_ingested_ratings show: {show_df(lastest_ingested_ratings)}"
)
logger.info(
    f"lastest_ingested_ratings schema: {lastest_ingested_ratings.schema()}"
)
logger.info(
    f"lastest_ingested_ratings printSchema: {lastest_ingested_ratings.printSchema()}"
)

# Script generated for node Add Current Timestamp
data_df = lastest_ingested_ratings.toDF()

data_df.createOrReplaceTempView("input_table")

logger.info(f"data_df shape: { (data_df.count(), len(data_df.columns))}")
logger.info(f"data_df show: {data_df.show(5)}")

logger.info(f"data_df view created: {data_df.printSchema()}")

logger.info(
    f"glue catalog db and table: glue_catalog.{database_name}.{table_name}"
)


try:
    if table_exists:
        SqlQuery1 = f"""
            MERGE INTO glue_catalog.{database_name}.{table_name} AS t1
            USING input_table AS t2 
            ON t1.customernumber = t2.customernumber
                AND t1.productcode = t2.productcode
            WHEN MATCHED 
                    THEN UPDATE SET 
                        t1.productrating = t2.productrating,
                        t1.ingest_ts = t2.ingest_ts
            WHEN NOT MATCHED THEN INSERT *
            """
        logger.info(f"executing query: {SqlQuery1}")
        spark.sql(SqlQuery1)
        logger.info(
            f"Merged the data into {database_name}.{table_name}: {SqlQuery1} \n"
        )
    else:
        additional_options = {"write.parquet.compression-codec": "gzip"}
        data_df.writeTo(
            f"glue_catalog.{database_name}.{table_name}"
        ).tableProperty("format-version", "2").tableProperty(
            "location",
            f"s3://{data_lake_bucket}/{database_name}/{table_name}/iceberg",
        ).options(
            **additional_options
        ).create()
        logger.info(f"Created {database_name}.{table_name} \n")
except Exception as err:
    traceback_error = traceback.format_exc()
    logger.error(
        f"Error while merging into {database_name}.{table_name}. {traceback_error} {err} \n"
    )


job.commit()
