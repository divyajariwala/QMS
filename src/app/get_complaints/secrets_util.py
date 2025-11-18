import boto3
import json
import os

def get_secret(secret_name):
    """
    Retrieve secret from AWS Secrets Manager
    """
    region_name = os.environ.get('AWS_REGION', 'us-east-1')
    
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
        print(f"Error retrieving secret {secret_name}: {str(e)}")
        raise e