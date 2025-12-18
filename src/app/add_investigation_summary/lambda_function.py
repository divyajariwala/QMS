import json
import logging
import os
import re

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
        
        # Validate required fields
        if 'deviationId' not in body:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Missing required field: deviationId'})
            }
        
        if 'summary' not in body:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Missing required field: summary'})
            }
        
        deviation_id = body['deviationId']
        summary = body['summary']
        
        # Validate field types and values
        if not isinstance(deviation_id, str) or not deviation_id.strip():
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'deviationId must be a non-empty string'})
            }
        
        # Validate deviationId format (DV-XXXXX)
        if not re.match(r'^DV-\d{5}$', deviation_id):
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'deviationId must be in format DV-XXXXX'})
            }
        
        if not isinstance(summary, str) or not summary.strip():
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'summary must be a non-empty string'})
            }
        
        rows_updated = update_investigation_summary(deviation_id, summary)
        
        if rows_updated == 0:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': f'Deviation not found: {deviation_id}'})
            }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'message': 'Investigation summary updated successfully'})
        }
        
    except Exception as e:
        logger.exception("Unexpected error in lambda_handler")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Internal server error'})
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
                rows_updated = cur.rowcount
                conn.commit()
                
                if rows_updated > 0:
                    logger.info(f"Updated investigation summary for deviation_id: {deviation_id}")
                else:
                    logger.warning(f"No rows updated for deviation_id: {deviation_id}")
                
                return rows_updated
                
    except Exception as e:
        logger.exception("Database error updating investigation summary")
        raise
