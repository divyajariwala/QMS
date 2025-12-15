import boto3
import json
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger()

def get_secret(secret_name, region_name):
    """
    Retrieve secret from AWS Secrets Manager
    """
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        logger.error(f"Error retrieving secret {secret_name}: {str(e)}")
        raise e

    secret = get_secret_value_response['SecretString']
    return json.loads(secret)
