# Week 3: Batch and Streaming Transformations

This week covers concepts on Batch Transformations using Apache Spark and streaming transformations using Flink for big datasets.

## Batch Transformations

Data wrangling tools are available to take messy data and convert into clean data. These are tools like Glue Databrew. To continuously update the data, you could use one of the CDC patterns. CDC patterns can use binlogs or `last_updated_ts` fields to find the new data that needs to be merged into warehouse.

- [Data Transformations with Spark](labs/lab1/lab.html) with corresponding [Code Notebook](labs/lab1/C4_W3_Assignment_Solution.md)

- [Lab: CDC with Flink and Debezium](labs/lab2/lab.html)

- [Quiz](quiz.html)