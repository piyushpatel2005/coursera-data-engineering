import datetime as dt
import re

import pandas as pd
from airflow import DAG
from airflow.models import Variable
from airflow.operators.dummy import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.providers.amazon.aws.transfers.sql_to_s3 import SqlToS3Operator
from airflow.utils.context import Context

S3_URI_PATTTERN = r"^s3://[a-zA-Z0-9.\-_]+(/[a-zA-Z0-9.\-_]+)*$"


def drop_nas_and_duplicates(
    source_bucket: str,
    source_key: str,
    target_key: str,
    target_bucket: str = "",
    **context: Context,
):
    """This function is used to drop rows with missing values and duplicates
    from a file in an S3 bucket.

    Args:
        source_bucket: str: The name of the bucket that contains the source CSV
        file.
        source_key: str: Object storage key of the source file (in the source bucket).
        target_key: str: Object storage key of the target file (in the target bucket).
        context: Context: Airflow context.
        target_bucket: str: The name of the bucket that will contain the target
         file. If not provided, the source bucket will be used.
    """
    if not target_bucket:
        target_bucket = source_bucket

    source_s3_uri = f"s3://{source_bucket}/{source_key}"
    target_s3_uri = f"s3://{target_bucket}/{target_key}"

    assert re.match(S3_URI_PATTTERN, source_s3_uri)
    assert re.match(S3_URI_PATTTERN, target_s3_uri)

    df = pd.read_csv(source_s3_uri)

############################# START OF EXERCISE 4 #############################

    ### START CODE HERE ### (~ 5 lines of code)
    # Apply `dropna()` method to the dataframe `df`
    df = df.dropna()
    
    # Apply `drop_duplicates()` method to the dataframe `df`
    df = df.drop_duplicates()

    df.to_csv(target_s3_uri)
    
    # Find number of the valid records with the function `len()`
    num_valid_records = len(df)
    
    # Use `xcom_push` method passing the number of the valid records
    context["ti"].xcom_push(key="valid_records", value=num_valid_records)
    ### END CODE HERE ###

############################## END OF EXERCISE 4 ##############################

############################# START OF EXERCISE 6 #############################

def notify_valid_records(table: str, **context: Context):
    """This function is used to notify about the number of valid records in a
    table.

    Args:
        table: str: The name of the table.
        context: dict: Airflow context.
    """

    ### START CODE HERE ### (1 line of code)
    # Use `xcom_pull()` method passing previously defined as `task_id` 
    task_id = f"transform_{table}"
    valid_records = context["ti"].xcom_pull(task_ids=task_id, key="valid_records")
    ### END CODE HERE ###

    print(f"Number of valid records in table {table}: {valid_records}")
    
############################## END OF EXERCISE 6 ##############################

############################# START OF EXERCISE 1 #############################

with DAG(
    dag_id="simple_dag",
    
    ### START CODE HERE ### (~ 6 lines of code)
    # Set the `schedule` equal to `"@daily"` to run DAG daily
    schedule="@daily",
    
    # Set the `start_date` as a `datetime` object representing the date at which
    # you're taking the lab
    start_date=dt.datetime(year=2024, month=4, day=1),
    ### END CODE HERE ###
    
    catchup=False,
) as dag:
    ############################## END OF EXERCISE 1 ##############################

    ############################# START OF EXERCISE 2 #############################
    
    ### START CODE HERE ### (~ 3 lines of code)
    partition_date = (
        # Use the built-in variable `ds` to specify the partition date in 
        # the format "YYYY/MM/DD", which should be passed as "%Y/%m/%d"
        # "%Y-%m-%d" represents the input format
        '{{ macros.ds_format(ds, "%Y-%m-%d", "%Y/%m/%d") }}'
    )
    ### END CODE HERE ###
    
    ############################## END OF EXERCISE 2 ##############################
    
    start_task = DummyOperator(task_id="start")
    
    ############################# START OF EXERCISE 3 #############################

    ### START CODE HERE ### (~ 8 lines of code)
    extract_and_load_task = SqlToS3Operator(
        task_id="extract_and_load_orders",
        
        # Pass the connection ID, which should be the same connection ID you 
        # specified while creating the connection in the Airflow UI
        sql_conn_id="mysql_connection",
        
        # Set the query value
        query="SELECT * FROM orders;",
        
        # Use method `get()` requesting the `s3_bucket` name
        s3_bucket=Variable.get("s3_bucket"), 
        s3_key=f"bronze/{partition_date}/orders.csv",
        replace=True,
    )
    ### END CODE HERE ###

    ############################## END OF EXERCISE 3 ##############################
    
    ############################# START OF EXERCISE 5 #############################
    
    ### START CODE HERE ### (10 lines of code)
    transform_task = PythonOperator(
        task_id="transform_orders",
        
        # Pass the `drop_nas_and_duplicates` function defined above
        python_callable=drop_nas_and_duplicates,
        
        provide_context=True,
        op_kwargs={
            
            # Use method `get()` requesting the `s3_bucket` name
            "source_bucket": Variable.get("s3_bucket"), 
            "source_key": f"bronze/{partition_date}/orders.csv",
            "target_key": f"silver/{partition_date}/orders.csv", 
        },
    )
    ### END CODE HERE ###
    
    ############################## END OF EXERCISE 5 ##############################
    
    ############################# START OF EXERCISE 7 #############################
    
    ### START CODE HERE ### (6 lines of code)
    notification_task = PythonOperator(
        task_id="notification",
        
        # Pass previously defined function `notify_valid_records`
        python_callable=notify_valid_records, 
        
        provide_context=True,
        op_kwargs={"table": "orders"},
    )
    ### END CODE HERE ###
    
    ############################## END OF EXERCISE 7 ##############################

    end_task = DummyOperator(task_id="end")

    ############################# START OF EXERCISE 8 #############################
    
    ### START CODE HERE ### (1 line of code)
    (start_task >> extract_and_load_task >> transform_task >> notification_task >> end_task)
    ### END CODE HERE ###
    
    ############################## END OF EXERCISE 8 ##############################
