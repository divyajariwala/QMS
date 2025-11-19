import json
import logging
import os
from datetime import datetime, timezone

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
logger = logging.getLogger("modify_extracted_text_lambda")
logger.setLevel(logging.INFO)

# Cache for database credentials and connection string
_db_credentials = None
_connection_string = None

def lambda_handler(event, context):
    try:
        # Parse input
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event
        case_id = body['caseId']
        
        # Update complaint in database
        update_complaint_in_db(case_id, body)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'message': 'Record updated successfully'})
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

def update_complaint_in_db(case_id, body):
    try:
        conninfo = get_connection_string()
        
        with psycopg.connect(conninfo) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                update_query = """
                UPDATE complaints 
                SET primary_reporter_name = %s,
                    primary_reporter_address = %s,
                    patient_name = %s,
                    physician_name = %s,
                    drug = %s,
                    lot_number = %s,
                    dose_amount = %s,
                    expiration_date = %s,
                    part_number = %s
                WHERE case_id = %s
                """
                
                cur.execute(update_query, (
                    body['primaryReporter']['name'],
                    body['primaryReporter']['address'],
                    body['patientName'],
                    body['physicianName'],
                    body['drug'],
                    body['lotNumber'],
                    body['doseAmount'],
                    body['expirationDate'],
                    body['partNumber'],
                    case_id
                ))
                
                conn.commit()
                logger.info(f"Updated complaint with case_id: {case_id}")
                
    except Exception as e:
        logger.error(f"Database error updating complaint: {str(e)}")
        raise