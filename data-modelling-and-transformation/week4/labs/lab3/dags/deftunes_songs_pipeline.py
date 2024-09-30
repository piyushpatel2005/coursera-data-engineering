from datetime import datetime, timedelta

from airflow import DAG
from airflow.decorators import dag, task
from airflow.operators.dummy import DummyOperator
from airflow.providers.amazon.aws.operators.glue import (
    GlueDataQualityRuleSetEvaluationRunOperator,
    GlueJobOperator,
)
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount

default_args = {
    "owner": "airflow",
    "description": "Demo for usage of the DockerOperator for DBT",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


DATA_BUCKET_NAME = "de-c4w4a2-767397743417-us-east-1-data-lake"
SCRIPTS_BUCKET_NAME = "de-c4w4a2-767397743417-us-east-1-scripts"


@dag(
    default_args=default_args,
    schedule_interval="0 0 1 * *",  # Runs at midnight on the first day of every month
    start_date=datetime(2020, 2, 1),
    end_date=datetime(2020, 3, 1),
    catchup=True,
    max_active_runs=1,
    dag_id="deftunes_songs_pipeline_dag",
)
def deftunes_songs_pipeline():

    # `start` task based on a `DummyOperator`
    start = DummyOperator(task_id="start")

    # `rds_extract_glue_job` task based on a `GlueJobOperator`
    # This job will extract the data from the RDS into the landing zone in CSV format
    rds_extract_glue_job = GlueJobOperator(
        task_id="rds_extract_glue_job",
        # The name of the Glue job you created in Terraform. This corresponds to the value that you can find in the Terraform output with the key `glue_rds_extract_job`
        job_name="de-c4w4a2-rds-extract-job",
        # Location in the S3 bucket that you used to deploy your scripts
        script_location=f"s3://{SCRIPTS_BUCKET_NAME}/de-c4w4a2-extract-songs-job.py",
        job_desc="Glue Job to extract data from RDS",
        # The name of the IAM role that you deployed with Terraform and can be found in the Terraform output `glue_role_arn`.
        # Take into account that you only need the name instead of the complete ARN
        iam_role_name="Cloud9-de-c4w4a2-glue-role",
        s3_bucket=f"{SCRIPTS_BUCKET_NAME}",
        region_name="us-east-1",
        # Configuration settings for Glue, you will provide the Glue version and the number of workers
        create_job_kwargs={
            "GlueVersion": "3.0",
            "NumberOfWorkers": 2,
            "WorkerType": "G.1X",
        },
        # This is a dictionary with the parameters that the Glue job will use in a key, value format.
        # The parameters depend on the job but you can find the data lake bucket name, the RDS connection, and the ingestion date. 
        # For the ingestion date, pay attention to the usage of Jinja templating to get the next date. 
        # Currently the `"{{ next_ds }}"` variable is deprecated but you are using it by simplicity to take the next start date.
        script_args={
            "--data_lake_bucket": f"{DATA_BUCKET_NAME}",
            "--rds_connection": "de-c4w4a2-connection-rds",
            "--ingest_date": "{{ next_ds }}",
        },
    )

    # The next task corresponds to the `songs_transform_glue_job` Glue job. 
    # This job transforms the CSV files extracted from the RDS, adds some metadata and saves the information in Apache Iceberg format in the transformation zone. 
    # Configuration is similar to the previous one but with the corresponding Glue job parameters.
    songs_transform_glue_job = GlueJobOperator(
        task_id="songs_transform_glue_job",
        job_name="de-c4w4a2-songs-transform-job",
        script_location=f"s3://{SCRIPTS_BUCKET_NAME}/de-c4w4a2-transform-songs-job.py",
        job_desc="Glue Job to extract data from RDS",
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
            "--songs_table": "songs",
            "--source_bucket_path": f"{DATA_BUCKET_NAME}",
            "--target_bucket_path": f"{DATA_BUCKET_NAME}",
        },
    )

    # Task `dq_check_songs_job` based on `GlueDataQualityRuleSetEvaluationRunOperator`
    dq_check_songs_job = GlueDataQualityRuleSetEvaluationRunOperator(
        task_id="dq_check_songs",
        # This is the same glue role used in the previous Glue jobs. 
        # In this case, instead of just the name, you are required to pass the complete ARN as in the Terraform output `glue_role_arn`.
        role="arn:aws:iam::767397743417:role/Cloud9-de-c4w4a2-glue-role",
        # A list with the set of rules that you want to evaluate. For the `songs` data coming from the RDS, the name of the rule set is in the Terraform output `songs_db_ruleset_name`.
        rule_set_names=["songs_dq_ruleset"],
        # Number of workers to run the job.
        number_of_workers=2,
        wait_for_completion=True,
        region_name="us-east-1",
        # A configuration dictionary with the Glue database and table name where the set of rules will be evaluated.
        datasource={
            "GlueTable": {
                "TableName": "songs",
                "DatabaseName": "de_c4w4a2_transform_db",
            }
        },
    )

    # Once the quality checks are evaluated, you will use the `DockerOperator` in the task named `task_db`. 
    # This task is in charge of using DBT to take the data from the `deftunes_transform` schema created with Redshift Spectrum and transform it to a star schema hosted 
    # in the `deftunes_serving` schema. This operator takes a docker image to create a container and passes a command to be executed.
    task_dbt = DockerOperator(
        task_id="docker_dbt_command",
        # The docker DBT image name used to deploy the docker containers.
        image="dbt_custom_image",
        api_version="auto",
        # As `auto_remove` is set to `True`, the Docker container will be automatically removed after the task finishes. This helps to clean up and not leave unused containers behind.
        auto_remove=True,
        # This specifies the URL to the Docker daemon. 
        # In this case, `"unix://var/run/docker.sock"` is used, which is the default Unix socket for Docker on most Linux systems. 
        # This URL is how Airflow connects to the Docker service running on the host machine.
        docker_url="unix://var/run/docker.sock",
        # The command to run inside the Docker container. The provided command checks the version of `dbt` and then runs `dbt debug` to ensure that the `dbt` configuration is correct. 
        # Then, the `dbt run` command is executed to perform the transformations.
        command='bash -c "dbt --version && dbt debug --profiles-dir /usr/app/.dbt --project-dir /usr/app/dbt_modeling  && dbt run --profiles-dir /usr/app/.dbt --project-dir /usr/app/dbt_modeling"',
        # This is a list of Docker mounts to attach to the container.
        mounts=[
            Mount(
                # Define the path on the host machine to be mounted.
                source="/docker_dbt/dbt_project/dbt_modeling/dbt_project.yml",
                # Define the path inside the container where the host path will be mounted.
                target="/usr/app/dbt_modeling/dbt_project.yml",
                # The type of mount, in this case, "bind" which binds a host path to a container path.
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

        # This sets the networking mode for the container. `"container:dbt"` specifies that the container should join another container’s network. 
        # In this case, it joins the network of a container named `dbt`, allowing it to communicate directly with that container using localhost.
        network_mode="container:dbt",
    )

    # `end` task based on another `DummyOperator`
    end = DummyOperator(task_id="end")

    (
        start
        >> rds_extract_glue_job
        >> songs_transform_glue_job
        >> dq_check_songs_job
        >> task_dbt
        >> end
    )


deftunes_songs_pipeline()
