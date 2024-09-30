from datetime import datetime, timedelta

from airflow import DAG
from airflow.decorators import dag, task
from airflow.operators.docker_operator import DockerOperator
from airflow.operators.dummy import DummyOperator
from airflow.providers.amazon.aws.operators.glue import (
    GlueDataQualityRuleSetEvaluationRunOperator,
    GlueJobOperator,
)
from docker.types import Mount

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

DATA_BUCKET_NAME = "de-c4w4a2-767397743417-us-east-1-data-lake"
SCRIPTS_BUCKET_NAME = "de-c4w4a2-767397743417-us-east-1-scripts"
API_URL = "34.206.194.53:8000"


@dag(
    default_args=default_args,
    description="DefTunes pipeline. Run AWS Glue jobs with parameters and perform data quality checks",
    schedule_interval="0 0 1 * *",  # Runs at midnight on the first day of every month
    start_date=datetime(2020, 2, 1),
    end_date=datetime(2020, 4, 1),
    catchup=True,
    max_active_runs=1,
    dag_id="deftunes_api_pipeline_dag",
)
def deftunes_pipeline():

    # `start` task based on a `DummyOperator`
    start = DummyOperator(task_id="start")

    # Use a `GlueJobOperator` to create the `api_users_extract_glue_job` task. This task is in charge of creating a Glue job that will ingest the Users endpoint 
    # and save the data in JSON format in the landing zone.
    api_users_extract_glue_job = GlueJobOperator(
        task_id="api_users_extract_glue_job",
        # For the `job_name`, the value is from the Terraform output `glue_api_users_extract_job`.
        job_name="de-c4w4a2-api-users-extract-job",
        script_location=f"s3://{SCRIPTS_BUCKET_NAME}/de-c4w4a2-api-extract-job.py",
        job_desc="Glue Job to extract data from User's API endpoint",
        # The name of the role from the Terraform output `glue_role_arn`.
        iam_role_name="Cloud9-de-c4w4a2-glue-role",
        # `s3_bucket` is set to the scripts bucket.
        s3_bucket=f"{SCRIPTS_BUCKET_NAME}",
        region_name="us-east-1",
        create_job_kwargs={
            "GlueVersion": "3.0",
            "NumberOfWorkers": 2,
            "WorkerType": "G.1X",
        },
        script_args={
            "--target_path": f"s3://{DATA_BUCKET_NAME}/landing_zone/api/users",
            "--api_url": f"http://{API_URL}/users",
            "--api_start_date": "{{ ds }}",
            "--api_end_date": "{{ macros.ds_add(next_ds, -1) }}",
            "--ingest_date": "{{ next_ds }}",
        },
    )

    # This task will create the Glue job to ingest data from the Sessions endpoint.
    api_sessions_extract_glue_job = GlueJobOperator(
        task_id="api_sessions_extract_glue_job",
        job_name="de-c4w4a2-api-sessions-extract-job",
        script_location=f"s3://{SCRIPTS_BUCKET_NAME}/de-c4w4a2-api-extract-job.py",
        job_desc="Glue Job to extract data from User's API endpoint",
        iam_role_name="Cloud9-de-c4w4a2-glue-role",
        s3_bucket=f"{SCRIPTS_BUCKET_NAME}",
        region_name="us-east-1",
        create_job_kwargs={
            "GlueVersion": "3.0",
            "NumberOfWorkers": 2,
            "WorkerType": "G.1X",
        },
        script_args={
            "--target_path": f"s3://{DATA_BUCKET_NAME}/landing_zone/api/sessions",
            "--api_url": f"http://{API_URL}/sessions",
            "--api_start_date": "{{ ds }}",
            "--api_end_date": "{{ macros.ds_add(next_ds, -1) }}",
            "--ingest_date": "{{ next_ds }}",
        },
    )

    # This task will take the data in JSON format from the users and sessions endpoints and will add some metadata and perform unnest transformations. 
    # The resulting data will be stored in Iceberg format at the transformation layer. 
    json_transform_glue_job = GlueJobOperator(
        task_id="json_transform_glue_job",
        job_name="de-c4w4a2-json-transform-job",
        script_location=f"s3://{SCRIPTS_BUCKET_NAME}/de-c4w4a2-transform-json-job.py",
        job_desc="Glue Job to extract data from Sessions's API endpoint",
        iam_role_name="Cloud9-de-c4w4a2-glue-role",
        s3_bucket=f"{SCRIPTS_BUCKET_NAME}",
        region_name="us-east-1",
        create_job_kwargs={
            "GlueVersion": "3.0",
            "NumberOfWorkers": 2,
            "WorkerType": "G.1X",
        },
        script_args={
            "--catalog_database": "de_c4w4a2_transform_db",
            "--ingest_date": "{{ next_ds }}",
            "--users_source_path": f"s3://{DATA_BUCKET_NAME}/landing_zone/api/users/",
            "--sessions_source_path": f"s3://{DATA_BUCKET_NAME}/landing_zone/api/sessions/",
            "--target_bucket_path": f"{DATA_BUCKET_NAME}",
            "--users_table": "users",
            "--sessions_table": "sessions",
        },
    )

    # This task will evaluate the rule set for users that you created with Terraform and associated with the Terraform output `users_db_ruleset_name`. 
    # You will use the same Glue Database and the `"users"` table.
    dq_check_users_job = GlueDataQualityRuleSetEvaluationRunOperator(
        task_id="dq_check_users",
        role="arn:aws:iam::767397743417:role/Cloud9-de-c4w4a2-glue-role",
        rule_set_names=["users_dq_ruleset"],
        number_of_workers=2,
        wait_for_completion=True,
        region_name="us-east-1",
        datasource={
            "GlueTable": {
                "TableName": "users",
                "DatabaseName": "de_c4w4a2_transform_db",
            }
        },
    )

    # Similar task but for the sessions.
    dq_check_sessions_job = GlueDataQualityRuleSetEvaluationRunOperator(
        task_id="dq_check_sessions",
        role="arn:aws:iam::767397743417:role/Cloud9-de-c4w4a2-glue-role",
        rule_set_names=["sessions_dq_ruleset"],
        number_of_workers=2,
        wait_for_completion=True,
        region_name="us-east-1",
        datasource={
            "GlueTable": {
                "TableName": "sessions",
                "DatabaseName": "de_c4w4a2_transform_db",
            }
        },
    )

    # You will use the `DockerOperator` in the task named `task_db` to use DBT.
    task_dbt = DockerOperator(
        task_id="docker_dbt_command",
        image="dbt_custom_image",
        api_version="auto",
        auto_remove=True,
        docker_url="unix://var/run/docker.sock",
        command='bash -c "dbt --version && dbt run --profiles-dir /usr/app/.dbt --project-dir /usr/app/dbt_modeling"',
        mounts=[
            Mount(
                source="/docker_dbt/dbt_project/dbt_modeling/dbt_project.yml",
                target="/usr/app/dbt_modeling/dbt_project.yml",
                type="bind",
            ),
            Mount(
                source="/docker_dbt/dbt_project/dbt_modeling/models",
                target="/usr/app/dbt_modeling/models",
                type="bind",
            ),
            Mount(
                source="/docker_dbt/dbt_project/.dbt",
                target="/usr/app/.dbt",
                type="bind",
            ),
        ],
        network_mode="container:dbt",
    )

    # `end` task based on a `DummyOperator`
    end = DummyOperator(task_id="end")

    start >> [api_users_extract_glue_job, api_sessions_extract_glue_job]
    [
        api_users_extract_glue_job,
        api_sessions_extract_glue_job,
    ] >> json_transform_glue_job
    json_transform_glue_job >> [dq_check_users_job, dq_check_sessions_job]
    [dq_check_users_job, dq_check_sessions_job] >> task_dbt
    task_dbt >> end


deftunes_pipeline()
