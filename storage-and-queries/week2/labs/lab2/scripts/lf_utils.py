import boto3
import traceback
import logging

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)


def sts_assume_role(sts_client, role_arn):
    """Creates session credentials while assuming a given role.

    Args:
        sts_client (boto3.Client): STS Boto3 Client
        role_arn (str): ARN of the desired role

    Returns:
        session_creds: Credentials to assume role
    """
    session_creds = sts_client.assume_role(
        RoleArn=role_arn, RoleSessionName="CreateIcebergTableSession"
    )
    return session_creds["Credentials"]


def get_role_arn(iam_client, role_name: str):
    """Get the ARN for aa given role based on the name.

    Args:
        iam_client (boto3.Client): IAM Boto3 client
        role_name (str): Role name

    Returns:
        arn: ARN for the role
    """
    try:
        response = iam_client.get_role(RoleName=role_name)
        return response["Role"]["Arn"]
    except Exception as e:
        traceback_error = traceback.format_exc()
        logger.error(f"Error details: . {traceback_error} {e} \n")
        logger.error(f"Couldn't get role: . {role_name} {e} \n")
        return None


def grant_data_location_access(
        lf_client,
        principal_arn: str,
        data_location_arn: str):
    """Grant Data location access using a LakeFormation Client

    Args:
        lf_client (boto3.Client): LakeFormation boto3 Client
        principal_arn (str): ARN for the role or user to grant permission
        data_location_arn (str): ARN for the S3 location to grant permission
    """
    try:
        response_grant_permissions = lf_client.grant_permissions(
            Principal={"DataLakePrincipalIdentifier": principal_arn},
            Resource={
                "DataLocation": {"ResourceArn": data_location_arn},
            },
            Permissions=["DATA_LOCATION_ACCESS"],
            PermissionsWithGrantOption=["DATA_LOCATION_ACCESS"],
        )
        logger.info(f"Grant Data location access to: {principal_arn} \n")
    except Exception as e:
        traceback_error = traceback.format_exc()
        logger.error(f"Error details: . {traceback_error} {e} \n")
        logger.error(f"Couldn't grant location access: {principal_arn} \n")


def grant_database_access(lf_client,
                          principal_arn: str,
                          database_name: str,
                          permissions=["ALL"]):
    """Grants Lakeformation permissions for a given role and database.

    Args:
        lf_client (boto3.Client): LakeFormation boto3 Client
        principal_arn (str): ARN for the role or user to grant permission
        database_name (str): Database name
        permissions (list, optional): permissions to grant.
            Defaults to ["ALL"].
    """
    try:
        response_grant_permissions = lf_client.grant_permissions(
            Principal={"DataLakePrincipalIdentifier": principal_arn},
            Resource={"Database": {"Name": database_name}},
            Permissions=permissions,
        )
        logger.info(
            f"Grant database {database_name} access to:{principal_arn}\n"
        )
    except Exception as e:
        traceback_error = traceback.format_exc()
        logger.error(f"Error details: {traceback_error} {e} \n")
        logger.error(
            f"Couldn't grant {database_name} access: {principal_arn}\n")


def grant_table_access(
        lf_client,
        principal_arn: str,
        database_name: str,
        table_name: str = None,
        permissions=["ALL"],
):
    """Grants Lakeformation permissions for a given role, database and table.

    Args:
        lf_client (boto3.Client): LakeFormation boto3 Client
        principal_arn (str): ARN for the role or user to grant permission
        database_name (str): Database name
        table_name (str, optional): Table name
        permissions (list, optional): permissions to grant.
            Defaults to ["ALL"].
    """
    if table_name:
        table_config = {"DatabaseName": database_name, "Name": table_name}
    else:
        table_config = {"DatabaseName": database_name, "TableWildcard": {}}
    try:
        response_grant_permissions = lf_client.grant_permissions(
            Principal={"DataLakePrincipalIdentifier": principal_arn},
            Resource={
                "Table": table_config
            },
            Permissions=permissions,
        )
        if table_name:
            logger.info(f"Grant table {table_name} access to:{principal_arn}\n")
        else:
            logger.info(f"Grant access to:{principal_arn}\n")
    except Exception as e:
        traceback_error = traceback.format_exc()
        logger.error(f"Error details: . {traceback_error} {e} \n")
        logger.error(f"Couldn't grant table access: {principal_arn} \n")


def create_glue_database(glue_client, database_name: str, description: str):
    """Create a Glue database using a Glue boto3 client

    Args:
        glue_client (boto3.Client): Glue boto3 client
        database_name (str): Database name
        description (str): Database description
    """
    try:
        response_create_database = glue_client.create_database(
            DatabaseInput={
                "Name": database_name,
                "Description": description,
            }
        )
        logger.info(f"Created database: {database_name} \n")
    except Exception as e:
        traceback_error = traceback.format_exc()
        logger.error(f"Error details: . {traceback_error} {e} \n")
        logger.error(f"Couldn't create database: {database_name}\n")


def create_iceberg_table(glue_client,
                         database_name: str,
                         table_name: str,
                         bucket_path: str,
                         columns):
    """Create an iceberg table with a Glue boto3 client

    Args:
        glue_client (boto3.Client): Glue boto3 client
        database_name (str): Databse name that will contained the table
        table_name (str): Table Name
        bucket_path (str): S3 path to store the data
        columns (_type_): List of dictionaries with the schema for the table.
    """
    try:
        response_create_table = glue_client.create_table(
            DatabaseName=database_name,
            OpenTableFormatInput={
                "IcebergInput": {"MetadataOperation": "CREATE", "Version": "2"}
            },
            TableInput={
                "Name": table_name,
                "StorageDescriptor": {
                    "Columns": columns,
                    "Location": f"s3://{bucket_path}/iceberg",
                },
                "TableType": "EXTERNAL_TABLE",
            },
        )
        logger.info(f"Created table: {database_name}.{table_name} \n")
    except Exception as e:
        traceback_error = traceback.format_exc()
        logger.error(f"Error details: . {traceback_error} {e} \n")
        logger.error(f"Couldn't create table: {database_name}.{table_name} \n")

