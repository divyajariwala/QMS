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
    
    Expected POST body format:
    {
        "case_id": "CAS-00001",
        "categoryDetails": [
            {"label": "Dose confirmation", "percentage": 94.92, "level": "2", "crl": "CRL-000100", "priority": 0, "unit": 5},
            {"label": "Needle not fully extended", "percentage": 2.88, "level": "2", "crl": "CRL-000108", "priority": 0, "unit": 2}
        ],
        "caseStatus": "pending"
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
        
        category_details = body.get('categoryDetails') or body.get('category_details', [])
        
        logger.info(f"Category details received: {category_details}")
        
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
                
                cur.execute("UPDATE complaints SET status = %s WHERE complaint_id = %s", ('Processed', case_id))
                
                # Update inference_results if category details provided
                if category_details and len(category_details) > 0:
                    levels = {}
                    subcategories = {}
                    crl_codes = {}
                    units = 0
                    final_level = None
                    priority_str = None
                    
                    for cat in category_details:
                        if not isinstance(cat, dict):
                            logger.warning(f"Skipping non-dict category: {cat}")
                            continue
                            
                        label = cat.get('label', '')
                        percentage = float(cat.get('percentage', 0)) / 100
                        level = str(cat.get('level', ''))
                        crl = cat.get('crl', '')
                        priority_str = cat.get('priority', 'Low')
                        unit = int(cat.get('unit', 0))
                        
                        if label:
                            subcategories[label] = percentage
                        if level and level in ['1', '2', '3']:
                            levels[level] = percentage
                            if not final_level:
                                final_level = level
                        if crl:
                            crl_codes[crl] = percentage
                        if unit:
                            units = unit
                    
                    # Ensure final_level is valid (1, 2, or 3)
                    if final_level not in ['1', '2', '3']:
                        final_level = '2'  # Default to level 2 if invalid
                    
                    # Convert priority string to int (0=Low, 1=High, 2=Medium)
                    priority = 0 if priority_str == 'Low' else 1 if priority_str == 'High' else 2
                    
                    cur.execute(
                        """UPDATE inference_results 
                           SET levels = %s, subcategories = %s, crl_codes = %s, units = %s, final_level = %s, priority = %s
                           WHERE complaint_id = %s""",
                        (json.dumps(levels), json.dumps(subcategories), json.dumps(crl_codes), units, final_level, priority, case_id)
                    )
                
                # Insert into processed_complaints table with approved category details
                cur.execute(
                    "INSERT INTO processed_complaints (complaint_id, approved_at, approved_by, approved_category_details) VALUES (%s, %s, %s, %s)",
                    (case_id, approved_at, approved_by, json.dumps(category_details))
                )
                
                # Update case stats after approval
                cur.execute("SELECT update_stats_only()")
                
                conn.commit()
            
                # Get updated inference data
                cur.execute("SELECT * FROM inference_results WHERE complaint_id = %s ORDER BY created_at DESC LIMIT 1", (case_id,))
                inference_result = cur.fetchone()
                
                logger.info(f"Inference result: {inference_result}")
                
                # Transform inference data to category details
                response_category_details = []
                if inference_result and isinstance(inference_result, dict):
                    levels_raw = inference_result.get('levels')
                    subcategories_raw = inference_result.get('subcategories')
                    crl_codes_raw = inference_result.get('crl_codes')
                    
                    levels = levels_raw if isinstance(levels_raw, dict) else {}
                    subcategories = subcategories_raw if isinstance(subcategories_raw, dict) else {}
                    crl_codes = crl_codes_raw if isinstance(crl_codes_raw, dict) else {}
                    units = inference_result.get('units', 0)
                    priority = inference_result.get('priority', 0)
                    priority_str = "Low" if priority == 0 else "High" if priority <= 2 else "Medium" if priority <= 4 else "Low"
                    
                    # Convert to lists maintaining order
                    level_items = list(levels.items())
                    subcat_items = list(subcategories.items())
                    crl_items = list(crl_codes.items())
                    
                    # Create array with sequential IDs
                    for idx in range(len(subcat_items)):
                        level_key = level_items[idx][0] if idx < len(level_items) else ''
                        subcat_label = subcat_items[idx][0] if idx < len(subcat_items) else ''
                        subcat_pct = subcat_items[idx][1] if idx < len(subcat_items) else 0
                        crl_code = crl_items[idx][0] if idx < len(crl_items) else ''
                        
                        response_category_details.append({
                            "id": str(idx + 1),
                            "label": subcat_label,
                            "level": level_key,
                            "crl": crl_code,
                            "priority": priority_str,
                            "unit": units,
                            "percentage": subcat_pct * 100
                        })
            
                response_data = {
                    'case_id': case_id,
                    'category_details': response_category_details,
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

