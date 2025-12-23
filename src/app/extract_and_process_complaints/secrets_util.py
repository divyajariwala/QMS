import json
import logging
from typing import Any, Dict, Optional

import boto3
from botocore.exceptions import ClientError

# Setup logging
logger = logging.getLogger(__name__)

# Cache for secrets to avoid repeated API calls
_secrets_cache: Dict[str, Dict[str, Any]] = {}


def get_secret(secret_name: str, region_name: str, use_cache: bool = True) -> Dict[str, Any]:
    """
    Retrieve a secret from AWS Secrets Manager with caching support.

    Args:
        secret_name (str): The name or ARN of the secret to retrieve.
        region_name (str): The AWS region where the secret is stored.
        use_cache (bool): Whether to use cached credentials. Default: True.

    Returns:
        Dict[str, Any]: The secret as a dictionary.

    Raises:
        ClientError: If there is an error retrieving the secret from Secrets Manager.
        ValueError: If the secret string is not valid JSON.
        KeyError: If the secret does not contain expected keys.
    """
    # Check cache first
    cache_key = f"{region_name}:{secret_name}"
    if use_cache and cache_key in _secrets_cache:
        logger.debug(f"Returning cached secret")
        return _secrets_cache[cache_key]

    try:
        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(service_name="secretsmanager", region_name=region_name)

        # Retrieve the secret value
        logger.info(f"Retrieving secret from Secrets Manager")
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)

    except ClientError as e:
        error_code = e.response['Error']['Code']
        logger.error(f"Error retrieving secret '{error_code}': {str(e)}")

        # Provide more specific error messages
        if error_code == 'ResourceNotFoundException':
            raise ValueError(f"Secret '{secret_name}' not found in region '{region_name}'") from e
        elif error_code == 'InvalidRequestException':
            raise ValueError(f"Invalid request for secret '{secret_name}'") from e
        elif error_code == 'InvalidParameterException':
            raise ValueError(f"Invalid parameter for secret '{secret_name}'") from e
        elif error_code == 'DecryptionFailure':
            raise ValueError(f"Cannot decrypt secret '{secret_name}'") from e
        elif error_code == 'InternalServiceError':
            raise ValueError(f"Internal service error retrieving secret '{secret_name}'") from e
        else:
            raise

    # Extract the secret string
    if 'SecretString' not in get_secret_value_response:
        raise ValueError(f"Secret '{secret_name}' does not contain a SecretString")

    secret_string = get_secret_value_response["SecretString"]

    # Parse JSON
    try:
        secret_dict = json.loads(secret_string)
    except json.JSONDecodeError as e:
        logger.error(f"Secret is not valid JSON: {str(e)}")
        raise ValueError(f"Secret contains invalid JSON") from e

    # Cache the secret
    if use_cache:
        _secrets_cache[cache_key] = secret_dict
        logger.debug(f"Cached secret")

    return secret_dict


def clear_secrets_cache(secret_name: Optional[str] = None, region_name: Optional[str] = None):
    """
    Clear the secrets cache.

    Args:
        secret_name (str, optional): Specific secret to clear. If None, clears all.
        region_name (str, optional): Region of the secret. Required if secret_name is provided.
    """
    global _secrets_cache

    if secret_name and region_name:
        cache_key = f"{region_name}:{secret_name}"
        if cache_key in _secrets_cache:
            del _secrets_cache[cache_key]
            logger.info(f"Cleared cache for secret: {secret_name}")
    else:
        _secrets_cache = {}
        logger.info("Cleared all secrets cache")


def get_db_credentials(secret_name: str, region_name: str) -> Dict[str, Any]:
    """
    Retrieve database credentials from Secrets Manager.
    Validates that required keys are present.

    Args:
        secret_name (str): The name or ARN of the secret containing DB credentials.
        region_name (str): The AWS region where the secret is stored.

    Returns:
        Dict[str, Any]: Database credentials with keys:
            - host: Database host
            - port: Database port (defaults to 5432 if not present)
            - dbname: Database name
            - username: Database username
            - password: Database password

    Raises:
        KeyError: If required credentials are missing.
    """
    credentials = get_secret(secret_name, region_name)

    # Validate required keys
    required_keys = ['host', 'dbname', 'username', 'password']
    missing_keys = [key for key in required_keys if key not in credentials]

    if missing_keys:
        raise KeyError(f"Secret '{secret_name}' is missing required keys: {missing_keys}")

    # Set default port if not present
    if 'port' not in credentials:
        credentials['port'] = 5432
        logger.debug("Using default port 5432 for database connection")

    return credentials