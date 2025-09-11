import json
from typing import Any, Dict

import boto3
from botocore.exceptions import ClientError


def get_secret(secret_name: str, region_name: str) -> Dict[str, Any]:
    """
    Retrieve a secret from AWS Secrets Manager.

    Args:
        secret_name (str): The name or ARN of the secret to retrieve.
        region_name (str): The AWS region where the secret is stored.

    Returns:
        Dict[str, Any]: The secret as a dictionary.

    Raises:
        ClientError: If there is an error retrieving the secret from Secrets Manager.
    """
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        # Retrieve the secret value
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        # Handle specific exceptions from Secrets Manager
        # For a list of exceptions thrown,
        # see https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Extract the secret string and parse it as JSON
    secret = get_secret_value_response["SecretString"]

    return json.loads(secret)
