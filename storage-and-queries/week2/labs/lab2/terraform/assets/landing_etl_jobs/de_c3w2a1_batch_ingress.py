import sys

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext

args = getResolvedOptions(sys.argv, ["JOB_NAME", "data_lake_bucket"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)
data_lake_bucket = args["data_lake_bucket"]
tables = [
    "customers",
    "employees",
    "offices",
    "orderdetails",
    "orders",
    "payments",
    "productlines",
    "products",
]
for table in tables:
    # Read from source system
    source_data = glueContext.create_dynamic_frame.from_options(
        connection_type="mysql",
        connection_options={
            "useConnectionProperties": "true",
            "dbtable": table,
            "connectionName": "de-c3w2a1-rds-connection",
        },
        transformation_ctx=f"source_data_{table}",
    )
    # Repartition source dataframe
    source_data = source_data.toDF().repartition(1)
    # Save source dataframe in bronze location
    source_data.write.mode("overwrite").csv(
        f"s3://{data_lake_bucket}/landing_zone/rds/{table}",
        header="true",
        sep=";",
        lineSep="\t"
    )

job.commit()
