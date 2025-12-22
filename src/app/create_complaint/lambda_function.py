import json
import logging
import os
import uuid
from datetime import datetime, timezone

import boto3
import psycopg
from psycopg.rows import dict_row

try:
    from secrets_util import get_secret
except ImportError:
    from .secrets_util import get_secret

try:
    from audit_logger import log_workflow, get_user_from_event
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from audit_logger import log_workflow, get_user_from_event


# Environment variables
ENV = os.environ.get('env', 'dev')
SQS_QUEUE_BASE_NAME = os.environ.get('sqs_queue_base_name', 'preload-complaints')
SQS_QUEUE_NAME = f"qms-{ENV}-{SQS_QUEUE_BASE_NAME}"
DB_SECRET_BASE_NAME = os.environ.get('db_secret_base_name', 'aurora-postgres-master')
DB_SECRET_NAME = f"qms-{ENV}-{DB_SECRET_BASE_NAME}"
DB_REGION = os.environ.get('db_region', 'us-east-1')


# Setup logging
logger = logging.getLogger("create_complaint_lambda")
logger.setLevel(logging.INFO)

# Cache for database credentials and connection string
_db_credentials = None
_connection_string = None


def lambda_handler(event, context):
    """
    Lambda function to create a complaint and enqueue it for processing.

    Expected POST body:
    {
        "narrative": "Detailed description of the complaint."
    }
    """
    logger.info("Received event: %s", json.dumps(event, indent=2))
    try:
        # Initialize AWS clients
        sqs_client = boto3.client('sqs')

        # Resolve Queue URL from name
        try:
            queue_url = sqs_client.get_queue_url(QueueName=SQS_QUEUE_NAME)["QueueUrl"]
        except Exception as e:
            print(f"Error resolving queue URL for {SQS_QUEUE_NAME}: {e}")
            return _response(500, f"Queue {SQS_QUEUE_NAME} not found")

        # Validate request has body
        if "body" not in event:
            return _response(400, "No body provided")

        # Parse request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})

        narrative = body.get('narrative', '').strip()

        # Validations
        if not narrative:
            return _response(400, "Narrative is required")

        # Create complaint in database and get auto-generated ID
        start_time = datetime.utcnow()
        complaint_id = create_complaint_in_db(narrative, event)
        
        # Create SQS message for extract_and_process_complaints lambda
        complaint_message = {
            'complaint_id': complaint_id,
            'file_id': str(uuid.uuid4()),  # Generate file_id for narrative input
            'narrative_text': narrative
        }

        # Send to SQS for processing
        sqs_response = sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(complaint_message),
            MessageAttributes={
                'Source': {
                    'StringValue': 'manual',
                    'DataType': 'String'
                },
                'ComplaintId': {
                    'StringValue': complaint_id,
                    'DataType': 'String'
                }
            }
        )

        print(f"Complaint created and sent to SQS: {complaint_id}, MessageId: {sqs_response['MessageId']}")

        return _response(200, "Complaint created and queued for processing", {
            'complaint': {
                'complaint_id': complaint_id,
                'narrative': narrative,
                'status': 'Pending',
                'created_at': datetime.now(timezone.utc).isoformat()
            },
            'message_id': sqs_response['MessageId']
        })

    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {str(e)}")
        return _response(400, "Invalid JSON format in request body")

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return _response(500, f"Internal server error: {str(e)}")


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


def create_complaint_in_db(narrative, event):
    """
    Create complaint record in database with narrative and return auto-generated complaint_id
    """
    try:
        conninfo = get_connection_string()
        start_time = datetime.utcnow()
        
        with psycopg.connect(conninfo) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Insert complaint with narrative, let database auto-generate complaint_id
                insert_query = """
                INSERT INTO complaints (narrative, status, text_extracted) 
                VALUES (%s, 'Pending', FALSE) 
                RETURNING complaint_id
                """
                
                cur.execute(insert_query, (narrative,))
                result = cur.fetchone()
                complaint_id = result['complaint_id']
                
                conn.commit()
                logger.info(f"Created complaint in database with ID: {complaint_id}")
                
                # Log workflow step
                user = get_user_from_event(event)
                log_workflow(
                    conn, complaint_id, 'COMPLAINT_CREATED',
                    input_data={'narrative_length': len(narrative), 'created_by': user},
                    output_data={'complaint_id': complaint_id, 'status': 'Pending'},
                    start_time=start_time
                )
                
                return complaint_id
                
    except Exception as e:
        logger.error(f"Database error creating complaint: {str(e)}")
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
        return headers.get('x-user-email') or headers.get('x-user-id') or 'anonymous'

    except Exception:
        return 'anonymous'


def _response(status_code, message, data=None):
    """Standardized HTTP response"""
    body = {
        "success": status_code < 400,
        "message": message,
        "data": data or {},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "86400"
        },
        "body": json.dumps(body)
    }
