import json
import logging
import os
from datetime import datetime, timezone

import boto3
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
logger = logging.getLogger("approve_complaint_lambda")
logger.setLevel(logging.INFO)

# Cache for database credentials and connection string
_db_credentials = None
_connection_string = None

def lambda_handler(event, context):
    """
    Lambda function to approve complaints by updating status from Pending to Processed.
    
    Expected POST body format (based on input.json):
    {
        "case_id": "RGL23-000070",
        "receipt_date": "08/Jan/2023",
        "criticality": "Major",
        "report_type": "Spontaneous",
        "ai_summary": "...",
        "case_type": ["AE", "PC"],
        "narrative": "...",
        "primary_reporter": {...},
        "patient_name": "...",
        "physician_name": "...",
        "product_details": {...},
        "caseStatus": "pending",
        "categoryDetails": [...]
    }
    """
    try:
        # Parse request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        # Validate required fields
        case_id = body.get('case_id')
        if not case_id:
            return _error_response(400, "case_id is required")
        
        current_status = body.get('caseStatus', '').lower()
        if current_status != 'pending':
            return _error_response(400, f"Can only approve complaints with pending status. Current status: {current_status}")
        
        # Get database connection string after validation
        conninfo = get_connection_string()
        
        # Check if complaint exists and get current data
        with psycopg.connect(conninfo) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "SELECT * FROM complaints WHERE complaint_id = %s AND status = 'Pending'",
                    (case_id,)
                )
                existing_complaint = cur.fetchone()
                
                if not existing_complaint:
                    return _error_response(404, f"Complaint with case_id '{case_id}' not found or not in Pending status")
            
                # Update complaint status to Processed
                approved_at = datetime.now(timezone.utc)
                approved_by = _get_user_from_event(event)
                
                # Update only status and approval details - no other fields allowed
                update_fields = ['status = %s']
                update_values = ['Processed']
                
                update_values.append(case_id)
                
                cur.execute(
                    f"UPDATE complaints SET {', '.join(update_fields)} WHERE complaint_id = %s",
                    update_values
                )
                
                # Insert into processed_complaints table
                cur.execute(
                    "INSERT INTO processed_complaints (complaint_id, approved_at, approved_by) VALUES (%s, %s, %s)",
                    (case_id, approved_at, approved_by)
                )
                
                conn.commit()
            
                # Get updated complaint data
                cur.execute("SELECT * FROM complaints WHERE complaint_id = %s", (case_id,))
                updated_complaint = cur.fetchone()
            
                # Prepare response with updated data
                response_data = {
                    'case_id': updated_complaint['complaint_id'],
                    'receipt_date': str(updated_complaint.get('receipt_date', '')) if updated_complaint.get('receipt_date') else '',
                    'criticality': updated_complaint.get('criticality', '') or '',
                    'report_type': updated_complaint.get('report_type', '') or '',
                    'ai_summary': updated_complaint.get('narrative_summary', '') or '',
                    'case_type': [updated_complaint['case_type']] if updated_complaint.get('case_type') else [],
                    'narrative': updated_complaint.get('narrative', '') or '',
                    'primary_reporter': {'name': updated_complaint.get('primary_reporter', '') or '', 'address': updated_complaint.get('primary_reporter_address', '') or ''},
                    'patient_name': updated_complaint.get('patient_name', '') or '',
                    'physician_name': updated_complaint.get('physician', '') or '',
                    'product_details': {'drug': updated_complaint.get('drug', '') or '', 'lot_no': updated_complaint.get('lot_no', '') or ''},
                    'category_details': [],
                    'caseStatus': 'processed',
                    'approved_at': approved_at.isoformat(),
                    'approved_by': approved_by
                }
                
                return {
                    'statusCode': 200,
                    'headers': _get_cors_headers(),
                    'body': json.dumps({
                        'success': True,
                        'message': f'Complaint {case_id} approved successfully',
                        'data': response_data
                    })
                }
        
    except json.JSONDecodeError as e:
        return _error_response(400, f"Invalid JSON format: {str(e)}")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return _error_response(500, f"Internal server error: {str(e)}")

def get_connection_string():
    """
    Build PostgreSQL connection string from credentials in Secrets Manager.
    Credentials are cached to avoid repeated API calls.

    Returns:
        str: PostgreSQL connection string in format:
             "postgresql://user:password@host:port/dbname"
    """
    global _connection_string, _db_credentials

    if _connection_string is not None:
        return _connection_string

    try:
        # Use the existing secrets_util function
        _db_credentials = get_secret(DB_SECRET_NAME, DB_REGION)

        # Build connection string
        host = _db_credentials['host']
        port = _db_credentials.get('port', 5432)
        dbname = _db_credentials['dbname']
        user = _db_credentials['username']
        password = _db_credentials['password']

        _connection_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

        logger.info(f"Database connection string built from secret: {DB_SECRET_NAME}")
        return _connection_string

    except Exception as e:
        logger.error(f"Error building connection string: {str(e)}")
        raise


def _get_user_from_event(event):
    """Extract user information from event (Cognito, API Key, etc.)"""
    try:
        # From Cognito authorizer
        request_context = event.get('requestContext', {})
        authorizer = request_context.get('authorizer', {})

        if 'claims' in authorizer:
            return authorizer['claims'].get('email') or authorizer['claims'].get('sub')

        # From custom header
        headers = event.get('headers', {})
        return headers.get('x-user-email') or headers.get('x-user-id') or 'system'

    except Exception:
        return 'system'

def _error_response(status_code, message):
    """Return standardized error response"""
    return {
        'statusCode': status_code,
        'headers': _get_cors_headers(),
        'body': json.dumps({
            'success': False,
            'error': message,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
    }

def _get_cors_headers():
    """Return CORS headers for API Gateway"""
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }

