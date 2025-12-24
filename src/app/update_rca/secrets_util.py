import json
import boto3
import logging

logger = logging.getLogger()


def get_db_credentials(secret_name: str, region_name: str = 'us-east-1'):
    """
    Retrieve database credentials from AWS Secrets Manager
    
    Args:
        secret_name: Name of the secret in Secrets Manager
        region_name: AWS region where the secret is stored
        
    Returns:
        Dict with database credentials (host, port, dbname, username, password)
        
    Raises:
        Exception: If secret cannot be retrieved
    """
    logger.info(f"Retrieving secret")
    
    try:
        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )
        
        # Retrieve the secret value
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        
        # Parse the secret string
        secret = json.loads(get_secret_value_response['SecretString'])
        
        logger.info(f"✅ Successfully retrieved secret")
        
        return {
            'host': secret.get('host'),
            'port': secret.get('port', 5432),
            'dbname': secret.get('dbname'),
            'username': secret.get('username'),
            'password': secret.get('password')
        }
        
    except Exception as e:
        logger.error(f"❌ Error retrieving secret: {str(e)}")
        raise
