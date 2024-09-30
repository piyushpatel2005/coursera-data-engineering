import json
import sys
from datetime import datetime

import requests
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import SparkSession, SQLContext
from pyspark.sql.functions import col

# Initialize Glue context and Spark session
args = getResolvedOptions(
    sys.argv,
    [
        "JOB_NAME",        
        "target_path",
        "api_url",
        "api_start_date",
        "api_end_date",
        "ingest_date"
    ],
)
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)


# Function to fetch data from API
def fetch_data_from_api(api_url: str):
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Response status code: {response.status_code}")
        response.raise_for_status()


# Replace with your API URLs
api_url = args["api_url"]
request_start_date = args["api_start_date"]
request_end_date = args["api_end_date"]
target_path = args["target_path"]
ingest_date_str = args["ingest_date"] if "ingest_date" in args else request_end_date
ingest_date = datetime.strptime(ingest_date_str, '%Y-%m-%d')
formatted_ingest_date = ingest_date.strftime("%Y_%m_%d")
print(f"Ingest date: {ingest_date_str}")

request_api_url = (
    f"{api_url}?start_date={request_start_date}&end_date={request_end_date}"
)
print(f"request_api_url: {request_api_url}")


# Fetch data from API
request_data = fetch_data_from_api(request_api_url)

# Convert data to Spark DataFrames
api_data_df = spark.read.json(sc.parallelize([json.dumps(request_data)]))

# Coalesce DataFrames to a single partition: this avoid having empty files due to parallelization
api_data_df = api_data_df.coalesce(1)

# Show DataFrame schema
api_data_df.printSchema()

# Write DataFrames to S3
api_data_df.write.mode("overwrite").json(f"{target_path}/ingest_on={formatted_ingest_date}/")

# Commit job
job.commit()
