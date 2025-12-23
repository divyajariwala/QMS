import json
import boto3
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def get_secret(secret_name: str, region_name: str) -> Dict[str, Any]:
    """
    Retrieve secret from AWS Secrets Manager
    
    Args:
        secret_name: Name of the secret in Secrets Manager
        region_name: AWS region where the secret is stored
        
    Returns:
        Dictionary containing the secret values
        
    Raises:
        Exception: If secret cannot be retrieved or parsed
    """
    try:
        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )
        
        logger.info(f"Retrieving secret.")
        
        # Get the secret value
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        
        # Parse the secret string as JSON
        secret = json.loads(get_secret_value_response['SecretString'])
        
        logger.info(f"Successfully retrieved secret.")
        return secret
        
    except Exception as e:
        logger.error(f"Error retrieving secret: {str(e)}")
        raise


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
