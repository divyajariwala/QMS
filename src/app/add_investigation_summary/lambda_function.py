import json
import logging
import os

import psycopg
from psycopg.rows import dict_row

try:
    from secrets_util import get_secret
except ImportError:
    from .secrets_util import get_secret

# Environment variables
ENV = os.environ.get('env', 'dev')
DB_SECRET_BASE_NAME = os.environ.get('db_secret_base_name', 'aurora-postgres-master')
DB_SECRET_NAME = f"qms-{ENV}-{DB_SECRET_BASE_NAME}"
DB_REGION = os.environ.get('db_region', 'us-east-1')

# Setup logging
logger = logging.getLogger("add_investigation_summary_lambda")
logger.setLevel(logging.INFO)

# Cache for database credentials and connection string
_db_credentials = None
_connection_string = None

def lambda_handler(event, context):
    try:
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event
        deviation_id = body['deviationId']
        summary = body['summary']
        
        update_investigation_summary(deviation_id, summary)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'message': 'Investigation summary updated successfully'})
        }
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': f'Database error: {str(e)}'})
        }

def get_connection_string():
    global _connection_string, _db_credentials
    
    if _connection_string is not None:
        return _connection_string
    
    try:
        _db_credentials = get_secret(DB_SECRET_NAME, DB_REGION)
        
        host = _db_credentials['host']
        port = _db_credentials.get('port', 5432)
        dbname = _db_credentials['dbname']
        user = _db_credentials['username']
        password = _db_credentials['password']
        
        _connection_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        return _connection_string
        
    except Exception as e:
        logger.error(f"Error building connection string: {str(e)}")
        raise

def update_investigation_summary(deviation_id, summary):
    try:
        conninfo = get_connection_string()
        
        with psycopg.connect(conninfo) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                update_query = """
                UPDATE deviations 
                SET investigation_summary = %s
                WHERE deviation_id = %s
                """
                
                cur.execute(update_query, (summary, deviation_id))
                conn.commit()
                logger.info(f"Updated investigation summary for deviation_id: {deviation_id}")
                
    except Exception as e:
        logger.error(f"Database error updating investigation summary: {str(e)}")
        raise
