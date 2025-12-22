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

try:
    from audit_logger import log_workflow, log_audit, get_user_from_event
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from audit_logger import log_workflow, log_audit, get_user_from_event

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
        user = get_user_from_event(event)
        
        # Update complaint in database
        update_complaint_in_db(case_id, body, event, user)
        
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

def update_complaint_in_db(case_id, body, event, user):
    try:
        conninfo = get_connection_string()
        start_time = datetime.utcnow()
        
        with psycopg.connect(conninfo) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Get current values for audit
                cur.execute("SELECT * FROM complaints WHERE complaint_id = %s", (case_id,))
                old_data = cur.fetchone()
                
                if not old_data:
                    raise Exception(f"Complaint {case_id} not found")
                
                update_query = """
                UPDATE complaints 
                SET primary_reporter = %s,
                    primary_reporter_address = %s,
                    patient_name = %s,
                    physician = %s,
                    drug = %s,
                    lot_no = %s,
                    dosage = %s,
                    expiration_date = %s,
                    part_number = %s
                WHERE complaint_id = %s
                """
                
                new_values = {
                    'primary_reporter': body['primaryReporter']['name'],
                    'primary_reporter_address': body['primaryReporter']['address'],
                    'patient_name': body['patientName'],
                    'physician': body['physicianName'],
                    'drug': body['drug'],
                    'lot_no': body['lotNumber'],
                    'dosage': body['doseAmount'],
                    'expiration_date': body['expirationDate'] if body['expirationDate'] else None,
                    'part_number': body['partNumber']
                }
                
                cur.execute(update_query, (
                    new_values['primary_reporter'],
                    new_values['primary_reporter_address'],
                    new_values['patient_name'],
                    new_values['physician'],
                    new_values['drug'],
                    new_values['lot_no'],
                    new_values['dosage'],
                    new_values['expiration_date'],
                    new_values['part_number'],
                    case_id
                ))
                
                conn.commit()
                logger.info(f"Updated complaint with case_id: {case_id}")
                
                # Log audit trail for each changed field
                fields_modified = []
                for field, new_val in new_values.items():
                    old_val = old_data.get(field)
                    if str(old_val) != str(new_val):
                        log_audit(conn, 'Complaint', case_id, field, old_val, new_val, user)
                        fields_modified.append(field)
                
                # Log workflow step
                log_workflow(conn, case_id, 'DETAILS_MODIFIED',
                    input_data={'fields_count': len(fields_modified), 'modified_by': user},
                    output_data={'fields_modified': fields_modified},
                    start_time=start_time)
                
    except Exception as e:
        logger.error(f"Database error updating complaint: {str(e)}")
        raise