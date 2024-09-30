import sys

from awsglue import DynamicFrame
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext


def sparkSqlQuery(
    glueContext, query, mapping, transformation_ctx
) -> DynamicFrame:
    for alias, frame in mapping.items():
        frame.toDF().createOrReplaceTempView(alias)
    result = spark.sql(query)
    return DynamicFrame.fromDF(result, glueContext, transformation_ctx)


args = getResolvedOptions(
    sys.argv, ["JOB_NAME", "glue_connection", "glue_database", "target_path"]
)
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Script generated for node Products
products_node = glueContext.create_dynamic_frame.from_options(
    connection_type="mysql",
    connection_options={
        "useConnectionProperties": "true",
        "dbtable": "classicmodels.products",
        "connectionName": args["glue_connection"],
    },
    transformation_ctx="products_node",
)

# Script generated for node Customers
customers_node = glueContext.create_dynamic_frame.from_options(
    connection_type="mysql",
    connection_options={
        "useConnectionProperties": "true",
        "dbtable": "classicmodels.customers",
        "connectionName": args["glue_connection"],
    },
    transformation_ctx="customers_node",
)

# Script generated for node Ratings
ratings_node = glueContext.create_dynamic_frame.from_options(
    connection_type="mysql",
    connection_options={
        "useConnectionProperties": "true",
        "dbtable": "classicmodels.ratings",
        "connectionName": args["glue_connection"],
    },
    transformation_ctx="ratings_node",
)

# Script generated for node Join
sql_join_query = """
select r.customerNumber
, c.city
, c.state
, c.postalCode
, c.country
, c.creditLimit
, r.productCode
, p.productLine
, p.productScale
, p.quantityInStock
, p.buyPrice
, p.MSRP
, r.productRating
from ratings r 
join products p on p.productCode = r.productCode 
join customers c on c.customerNumber = r.customerNumber;
"""

join_node = sparkSqlQuery(
    glueContext,
    query=sql_join_query,
    mapping={
        "ratings": ratings_node,
        "products": products_node,
        "customers": customers_node,
    },
    transformation_ctx="join_node",
)

# Script generated for node de-c1w4-s3
s3_upload_node = glueContext.getSink(
    path=f"{args['target_path']}/ratings_ml_training/",
    connection_type="s3",
    updateBehavior="UPDATE_IN_DATABASE",
    partitionKeys=["customerNumber"],
    enableUpdateCatalog=True,
    transformation_ctx="s3_upload_node",
)
s3_upload_node.setCatalogInfo(
    catalogDatabase=args["glue_database"],
    catalogTableName="ratings_ml_training",
)
s3_upload_node.setFormat("glueparquet", compression="snappy")
s3_upload_node.writeFrame(join_node)
job.commit()
