# Week 2

This week covers the information on Data Engineering lifecycle. These covers understanding source systems, ingesting data and then applying transformation and finally serving the data to data analysts or to ML teams.

The Data Engineering undercurrents also cover concepts like Security, DataOps, Data Management, Data architecture, Orchestration and Software Engineering principles.

Finally, this week included a lab for building end-to-end data pipeline ingesting data from RDBMS using Glue job and extracting metadata using Glue crawlers and finally querying this data using Athena. This lab also builds infrastructure using Terraform.

- [Quiz](quiz.html)

```shell
aws s3 cp --recursive s3://dlai-data-engineering/labs/c1w2-187976/ ./
```

As a part of this lab setup, the `~/.bashrc` contains following environment variables.

```shell
export TF_VAR_project=de-c1w2
export TF_VAR_region=us-east-1
export TF_VAR_vpc_id=vpc-07af89acaaed2746a
export TF_VAR_private_subnet_a_id=subnet-0981ec9d5ea722433
export TF_VAR_db_sg_id=sg-09c639cfd7e525f49
export TF_VAR_host=[PUBLIC_IP_RDS]
export TF_VAR_port=3306
export TF_VAR_database=classicmodels
export TF_VAR_username=admin
export TF_VAR_password=password
```

1. Follow the instructions specified in [this HTML page](lab.html).
2. It will further ask you to follow steps of [Lab specific instructions](lab/C1_W2_Assignment.md).
3. Once the ETL job has finished, you can query the data using [Jupyter Notebook](lab/infrastructure/jupyterlab/C1_W2_Dashboard.ipynb)