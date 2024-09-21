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

# Extract data from source tables
customers = glueContext.create_dynamic_frame.from_options(
    connection_type="mysql",
    connection_options={
        "useConnectionProperties": "true",
        "dbtable": "classicmodels.customers",
        "connectionName": args["glue_connection"],
    },
    transformation_ctx="customers",
)

orders = glueContext.create_dynamic_frame.from_options(
    connection_type="mysql",
    connection_options={
        "useConnectionProperties": "true",
        "dbtable": "classicmodels.orders",
        "connectionName": args["glue_connection"],
    },
    transformation_ctx="orders",
)

orderdetails = glueContext.create_dynamic_frame.from_options(
    connection_type="mysql",
    connection_options={
        "useConnectionProperties": "true",
        "dbtable": "classicmodels.orderdetails",
        "connectionName": args["glue_connection"],
    },
    transformation_ctx="orderdetails",
)

products = glueContext.create_dynamic_frame.from_options(
    connection_type="mysql",
    connection_options={
        "useConnectionProperties": "true",
        "dbtable": "classicmodels.products",
        "connectionName": args["glue_connection"],
    },
    transformation_ctx="products",
)

productlines = glueContext.create_dynamic_frame.from_options(
    connection_type="mysql",
    connection_options={
        "useConnectionProperties": "true",
        "dbtable": "classicmodels.productlines",
        "connectionName": args["glue_connection"],
    },
    transformation_ctx="productslines",
)

# Transform data to build a star schema
sql_query_dim_customers = """
with dim_customers as (
    select
        customerNumber,
        customerName,
        contactLastName,
        contactFirstName,
        phone,
        addressLine1,
        addressLine2,
        creditLimit
    from customers
)
select * from dim_customers
"""

dim_customers = sparkSqlQuery(
    glueContext,
    query=sql_query_dim_customers,
    mapping={"customers": customers},
    transformation_ctx="dim_customers",
)

sql_query_dim_products = """
with dim_products as (
    select
        products.productCode,
        products.productName,
        products.productLine,
        products.productScale,
        products.productVendor,
        products.productDescription,
        productlines.textDescription as productLineDescription
    from products
    left join productlines using (productLine)
)
select * from dim_products
"""

dim_products = sparkSqlQuery(
    glueContext,
    query=sql_query_dim_products,
    mapping={
        "products": products,
        "productlines": productlines,
    },
    transformation_ctx="dim_products",
)

sql_query_dim_locations = """
with dim_locations as (
    select distinct
        postalCode,
        city,
        state,
        country
    from customers
)
select * from dim_locations
"""

dim_locations = sparkSqlQuery(
    glueContext,
    query=sql_query_dim_locations,
    mapping={"customers": customers},
    transformation_ctx="dim_locations",
)

sql_query_fact_orders = """
with fact_orders as (
    select
        orderLineNumber,
        orders.orderNumber,
        orders.customerNumber,
        location.postalCode,
        orderdetails.productCode,
        orders.orderDate,
        orders.requiredDate,
        orders.shippedDate,
        orders.status,
        orders.comments,
        orderdetails.quantityOrdered,
        orderdetails.priceEach,
        (orderdetails.quantityOrdered * orderdetails.priceEach) AS orderAmount,
        products.buyPrice,
        products.MSRP
    from orders
    left join orderdetails using (orderNumber)
    left join products using (productCode)
    left join customers using (customerNumber)
    left join location using (postalCode)
)
select * from fact_orders
"""

fact_orders = sparkSqlQuery(
    glueContext,
    query=sql_query_fact_orders,
    mapping={
        "orders": orders,
        "orderdetails": orderdetails,
        "products": products,
        "location": dim_locations,
    },
    transformation_ctx="fact_orders",
)

# Load transformed data into S3

dim_customers_to_s3 = glueContext.getSink(
    path=f"{args['target_path']}/dim_customers/",
    connection_type="s3",
    updateBehavior="UPDATE_IN_DATABASE",
    partitionKeys=[],
    compression="snappy",
    enableUpdateCatalog=True,
    transformation_ctx="dim_customers_to_s3",
)
dim_customers_to_s3.setCatalogInfo(
    catalogDatabase=args["glue_database"],
    catalogTableName="dim_customers",
)
dim_customers_to_s3.setFormat("glueparquet")
dim_customers_to_s3.writeFrame(dim_customers)

dim_products_to_s3 = glueContext.getSink(
    path=f"{args['target_path']}/dim_products/",
    connection_type="s3",
    updateBehavior="UPDATE_IN_DATABASE",
    partitionKeys=[],
    compression="snappy",
    enableUpdateCatalog=True,
    transformation_ctx="dim_products_to_s3",
)
dim_products_to_s3.setCatalogInfo(
    catalogDatabase=args["glue_database"],
    catalogTableName="dim_products",
)
dim_products_to_s3.setFormat("glueparquet")
dim_products_to_s3.writeFrame(dim_products)

dim_locations_to_s3 = glueContext.getSink(
    path=f"{args['target_path']}/dim_locations/",
    connection_type="s3",
    updateBehavior="UPDATE_IN_DATABASE",
    partitionKeys=[],
    compression="snappy",
    enableUpdateCatalog=True,
    transformation_ctx="dim_locations_to_s3",
)
dim_locations_to_s3.setCatalogInfo(
    catalogDatabase=args["glue_database"],
    catalogTableName="dim_locations",
)
dim_locations_to_s3.setFormat("glueparquet")
dim_locations_to_s3.writeFrame(dim_locations)

fact_orders_to_s3 = glueContext.getSink(
    path=f"{args['target_path']}/fact_orders/",
    connection_type="s3",
    updateBehavior="UPDATE_IN_DATABASE",
    partitionKeys=[],
    compression="snappy",
    enableUpdateCatalog=True,
    transformation_ctx="fact_orders_to_s3",
)
fact_orders_to_s3.setCatalogInfo(
    catalogDatabase=args["glue_database"],
    catalogTableName="fact_orders",
)
fact_orders_to_s3.setFormat("glueparquet")
fact_orders_to_s3.writeFrame(fact_orders)

job.commit()
