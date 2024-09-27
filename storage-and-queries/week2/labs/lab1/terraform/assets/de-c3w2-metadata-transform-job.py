import ast
import json
import sys

import boto3
import pandas as pd
import smart_open
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pandas import DataFrame
from pyspark.context import SparkContext

args = getResolvedOptions(
    sys.argv,
    [
        "JOB_NAME",
        "s3_bucket",
        "source_path",
        "target_path",
        "compression",
        "partition_cols",
    ],
)
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)


def read_data(bucket_name: str, s3_file_key: str) -> pd.DataFrame:
    """Reads metadata file

    Args:
        bucket_name (str): Bucket name
        s3_file_key (str): Dataset s3 key location

    Returns:
        pd.DataFrame: Read dataframe
    """
    s3_client = boto3.client("s3")
    source_uri = f"s3://{bucket_name}/{s3_file_key}"
    json_list = []
    for json_line in smart_open.open(
        source_uri, transport_params={"client": s3_client}
    ):
        json_list.append(ast.literal_eval(json_line))
    df = pd.DataFrame(json_list)
    print(f"df: {df.shape}")
    print(f"df: {df.head()}")
    print(f"df: {df.columns}")
    print(f"df: {df['salesRank'].head()}")
    return df


def transform(raw_df: DataFrame) -> DataFrame:
    """Function in charge of the tranformation of the raw data of the
    Reviews Metadata.

    Args:
        raw_df (DataFrame): Raw data loaded in dataframe

    Returns:
        DataFrame: Returned transformed dataframe
    """

    cols = ["asin",
        "description",
        "title",
        "price",
        "brand",
        "sales_category",
        "sales_rank",
    ]
    
    ### START CODE HERE ### (6 lines of code)
    tmp_df = None
    
    df_rank = None
    
    target_df = None
    target_df = None
    target_df = None
    target_df = None
    ### END CODE HERE ###
    
    print(f"target_df: {target_df.shape}")
    print(f"target_df: {target_df.columns}")
    print(f"target_df: {target_df.head()}")
    return target_df


partition_cols = json.loads(args["partition_cols"])

# Load raw data into `source_pd` using `read_data` function.
source_pd = read_data(args["s3_bucket"], args["source_path"])
# Transformation step, generates destination dataframe in Pandas
dest_pd = transform(source_pd)
# Generate a Spark DataFrame from Pandas DataFrame
dest_pd = spark.createDataFrame(dest_pd)
# Generate a  Glue DynamicFrame from Spark DataFrame
dest_df = DynamicFrame.fromDF(dest_pd, glueContext, "dest_df")

connection_options = (
    {
        "path": f"s3://{args['s3_bucket']}/processed_data/{args['compression']}/no_partition/{args['target_path']}/",
    }
    if not partition_cols
    else {
        "path": f"s3://{args['s3_bucket']}/processed_data/{args['compression']}/partition_by_{'_'.join(partition_cols)}/{args['target_path']}/",
        "partitionKeys": partition_cols,
    }
)

datasink = glueContext.write_dynamic_frame.from_options(
    frame=dest_df,
    connection_type="s3",
    format="glueparquet",
    connection_options=connection_options,
    format_options={"compression": args["compression"]},
    transformation_ctx="datasink",
)

job.commit()
