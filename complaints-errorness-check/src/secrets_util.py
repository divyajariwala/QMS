import json
import boto3
from botocore.exceptions import ClientError


def get_secret(secret_name: str, region: str) -> dict:
    """
    Retrieve a secret from AWS Secrets Manager.

    Args:
        secret_name (str): The name of the secret to retrieve.
        region (str): The AWS region where the secret is stored.

    Returns:
        dict: The secret data in JSON format.

    Raises:
        ClientError: If an error occurs while retrieving the secret.
    """
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region)

    try:
        # Fetch the secret value from AWS Secrets Manager
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        # Raise the exception for the caller to handle
        raise e

    # Parse and return the secret as a JSON object
    secret = get_secret_value_response["SecretString"]
    return json.loads(secret)
