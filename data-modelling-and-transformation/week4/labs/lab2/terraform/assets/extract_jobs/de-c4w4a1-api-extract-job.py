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

# In this job, you will use pure pyspark dataframes syntax to extract the data
# Initialize Glue context and Spark session
# Take a look to the parameters that it requires: a target path where data will be stored, the API endpoint URL and a start and end date that are required by each API endpoint
args = getResolvedOptions(
    sys.argv,
    [
        "JOB_NAME",        
        "target_path",
        "api_url",
        "api_start_date",
        "api_end_date",
    ],
)
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)


# Function to fetch data from API
# This function requires an `api_url` string with the endpoint 
def fetch_data_from_api(api_url: str):
    # Use the `requests.get()` method to perform a GET request to the `api_url` endpoint
    response = requests.get(api_url)
    # See that when the response status code is 200 is the moment in which the data is actually retrieved
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
current_timestamp = datetime.now().strftime("%Y-%m-%d")
print(f"Current Timestamp: {current_timestamp}")

# Create the `request_api_url` string by passing the `request_start_date` and `request_end_date` to the `start_date` and `end_date` endpoint parameters
# See that those values come from the parameters that are passed to the glue job
request_api_url = (
    f"{api_url}?start_date={request_start_date}&end_date={request_end_date}"
)
print(f"request_api_url: {request_api_url}")


# Fetch data from API
# Pass the `request_api_url` to the `fetch_data_from_api()` function
request_data = fetch_data_from_api(request_api_url)

# Complete the transformation of the data into a spark dataframe
# Inside the `sc.parallelize` method there is a list. In this list, use the `json.dumps()` method applied over the `request_data` object
# The `json.dumps()` method should convert the Python dictionary (or more precisely list of dictionaries) `request_data` into a JSON-formatted string
api_data_df = spark.read.json(sc.parallelize([json.dumps(request_data)]))

# Coalesce dataframes to a single partition: this helps to avoid having empty files due to parallelization
api_data_df = api_data_df.coalesce(1)

# Show dataframe schema
api_data_df.printSchema()

# Write dataframe to S3
api_data_df.write.mode("overwrite").json(f"{target_path}/{current_timestamp}/")

# Commit job
job.commit()






