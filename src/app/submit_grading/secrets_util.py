import boto3
import json
import os

def get_secret(secret_name, region_name='us-east-1'):
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
        secret = get_secret_value_response['SecretString']
        return json.loads(secret)
    except Exception as e:
        print(f"Error retrieving secret: {str(e)}")
        raise e


def get_db_credentials(secret_name: str, region_name: str) -> Dict[str, Any]:
    """
    Retrieve database credentials from AWS Secrets Manager.
    Alias for get_secret() for consistency with other lambda functions.

    Args:
        secret_name: Name of the secret in Secrets Manager
        region_name: AWS region where the secret is stored

    Returns:
        Dictionary containing the database credentials (host, port, dbname, username, password)

    Raises:
        Exception: If secret cannot be retrieved or parsed
    """
    return get_secret(secret_name, region_name)