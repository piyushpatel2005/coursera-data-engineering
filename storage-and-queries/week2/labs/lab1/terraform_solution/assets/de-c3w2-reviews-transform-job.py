import json
import sys

# Import the AWS Glue libraries
import pandas as pd
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pandas import DataFrame
from pyspark.context import SparkContext

# Get arguments that are passed when running the script
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
# Main entry point for Spark functionality, connection to a Spark cluster
sc = SparkContext()
# Glue wrapper to provide additional features on top of Spark
glueContext = GlueContext(sc)
# Spark Session, the entry point to programming Spark with the Dataset and DataFrame API
spark = glueContext.spark_session
# Instanciate a Glue Job with the Glue context
job = Job(glueContext)
# Initialize the Job
job.init(args["JOB_NAME"], args)


def transform(raw_df: DataFrame) -> DataFrame:
    """Function in charge of the tranformation of the raw data of the
    Reviews.

    Args:
        raw_df (DataFrame): Raw data loaded in dataframe

    Returns:
        DataFrame: Returned transformed dataframe
    """
    ### START CODE HERE ### (5 lines of code)
    raw_df['reviewTime'] = pd.to_datetime(raw_df['unixReviewTime'], unit='s')
    raw_df['year'] = raw_df['reviewTime'].dt.year
    raw_df['month'] = raw_df['reviewTime'].dt.month
    
    df_helpful = pd.DataFrame(raw_df['helpful'].to_list(), columns=['helpful', 'not_helpful'])
    target_df = pd.concat([raw_df.drop(columns=['helpful']), df_helpful], axis=1)
    ### END CODE HERE ###
    
    print(f"target_df: {target_df.shape}")
    print(f"target_df: {target_df.columns}")
    print(f"target_df: {target_df.head()}")
    return target_df


partition_cols = json.loads(args["partition_cols"])

# Script generated for node Source Amazon S3
source_df = glueContext.create_dynamic_frame.from_options(
    format_options={"multiline": False},
    connection_type="s3",
    format="json",
    connection_options={
        "paths": [f"s3://{args['s3_bucket']}/{args['source_path']}"],
        "recurse": True,
    },
    transformation_ctx="source_df",
)

# Convert Glue DynamicFrame to Spark DataFrame
source_df = source_df.toDF()

# Convert Spark DataFrame to Pandas DataFrame
source_pd = source_df.toPandas()

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

# Write the previous Glue DynamicFrame to a parquet file in a given S3 path
datasink = glueContext.write_dynamic_frame.from_options(
    frame=dest_df,
    connection_type="s3",
    format="glueparquet",
    connection_options=connection_options,
    format_options={"compression": args["compression"]},
    transformation_ctx="datasink",
)

job.commit()
