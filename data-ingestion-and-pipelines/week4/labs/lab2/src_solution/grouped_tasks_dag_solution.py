import datetime as dt
import re

import pandas as pd
from airflow import DAG
from airflow.models import Variable
from airflow.operators.dummy import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.providers.amazon.aws.transfers.sql_to_s3 import SqlToS3Operator
from airflow.utils.context import Context
from airflow.utils.task_group import TaskGroup

S3_URI_PATTTERN = r"^s3://[a-zA-Z0-9.\-_]+(/[a-zA-Z0-9.\-_]+)*$"
tables = ["payments", "customers", "products"]


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

    df = df.dropna()
    df = df.drop_duplicates()

    df.to_csv(target_s3_uri)

    num_valid_records = len(df)
    context["ti"].xcom_push(key="valid_records", value=num_valid_records)

def notify_valid_records(tables: list[str], **context: Context):
    """This function is used to notify about the number of valid records in a
    table.

    Args:
        tables: list[str]: A list containing the names of the tables to notify
        on.
        context: dict: Airflow context.
    """
    for table in tables:
        task_id = f"transform_{table}"
        task_id = f"{table}.{task_id}" if len(tables) > 1 else task_id
        
        valid_records = context["ti"].xcom_pull(
            task_ids=[task_id], key="valid_records"
        )

        print(f"Number of valid records in table {table}: {valid_records}")


with DAG(
    dag_id="grouped_tasks_dag",
    schedule="@daily",
    start_date=dt.datetime(year=2024, month=4, day=1),
    catchup=False,
) as dag:
    partition_date = '{{ macros.ds_format(ds, "%Y-%m-%d", "%Y/%m/%d") }}'

    start_task = DummyOperator(task_id="start")

    task_group = []
    for table in tables:
        with TaskGroup(table) as etl_tg:
            
            extract_load_task = SqlToS3Operator(
                task_id=f"extract_load_{table}",
                sql_conn_id="mysql_connection",
                query=f"SELECT * FROM {table};",
                s3_bucket=Variable.get("s3_bucket"),
                s3_key=f"bronze/{partition_date}/{table}.csv",
                replace=True,
            )

            transform_task = PythonOperator(
                task_id=f"transform_{table}",
                python_callable=drop_nas_and_duplicates,
                provide_context=True,
                op_kwargs={
                    "source_bucket": Variable.get("s3_bucket"),
                    "source_key": f"bronze/{partition_date}/{table}.csv",
                    "target_key": f"silver/{partition_date}/{table}.csv",
                },
            )
    
            ############################# START OF EXERCISE 9 #############################
            
            ### START CODE HERE ### (2 lines of code)
            # Use the `>>` operator to define relation between the tasks 
            # `extract_load_task` and `transform_task`
            extract_load_task >> transform_task

            # append each of the `etl_tg` elements into the `task_group`
            # using append() method
            task_group.append(etl_tg)
            
            ############################## END OF EXERCISE 9 ##############################

    notification_task = PythonOperator(
        task_id="notification",
        python_callable=notify_valid_records, 
        provide_context=True,
        op_kwargs={"tables": tables}, 
    )

    end_task = DummyOperator(task_id="end")


    ############################# START OF EXERCISE 10 #############################

    ### START CODE HERE ### (1 line of code)
    (start_task >> task_group >> notification_task >> end_task)
    ### END CODE HERE ###

    ############################## END OF EXERCISE 9 ##############################
