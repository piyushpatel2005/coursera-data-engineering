import boto3


def download_file_from_s3(bucket_name, s3_key, local_path):
    """
    Download a file from an S3 bucket to a local directory.

    Args:
    - bucket_name (str): Name of the S3 bucket.
    - s3_key (str): Key of the object in the S3 bucket.
    - local_path (str): Local directory path where the file will be saved.
    """
    # Create a boto3 S3 client
    s3_client = boto3.client("s3")

    try:
        # Download the file from S3
        s3_client.download_file(bucket_name, s3_key, local_path)
        print(f"File downloaded successfully to {local_path}")
    except Exception as e:
        print(f"Error downloading file: {e}")


# Example usage
bucket_name = "de-c2w1a1-056446560159-us-east-1-data-test"
s3_key = "csv/ratings_ml_training_dataset.csv"
local_path = "data/ratings_ml_training_dataset.csv"

download_file_from_s3(bucket_name, s3_key, local_path)
