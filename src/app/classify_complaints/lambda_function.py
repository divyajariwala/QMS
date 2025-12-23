import json
import logging
import os
from datetime import datetime, timezone

import boto3
import psycopg

from secrets_util import get_secret

try:
    from audit_logger import log_workflow, get_user_from_event
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from audit_logger import log_workflow, get_user_from_event

# Environment variables
ENV = os.environ.get('env', 'dev')
STEP_FUNCTION_BASE_NAME = os.environ.get('step_function_base_name', 'classify-complaints')
STEP_FUNCTION_NAME = f"qms-{ENV}-{STEP_FUNCTION_BASE_NAME}"
AWS_REGION = os.environ.get('aws_region', 'us-east-1')
DB_SECRET_BASE_NAME = os.environ.get('db_secret_base_name', 'aurora-postgres-master')
DB_SECRET_NAME = f"qms-{ENV}-{DB_SECRET_BASE_NAME}"
DB_REGION = os.environ.get('db_region', 'us-east-1')

# Setup logging
logger = logging.getLogger("classify_complaints_lambda")
logger.setLevel(logging.INFO)

# Cache
_db_credentials = None
_connection_string = None


def lambda_handler(event, context):
    """
    Process complaint classification requests.

    Expected event format:
    - Direct: {"complaint_id": "CAS-00001"}

    Workflow:
    1. Extract complaint_id from event
    2. Query PostgreSQL to get narrative
    3. Start Step Functions with narrative
    """
    logger.info(f"Received event: {json.dumps(event)}")

    # Handle OPTIONS request for CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return _response(200, "OK")

    try:
        # Parse body from API Gateway event
        body = json.loads(event.get('body', '{}'))

        # Extract complaint_id from parsed body
        complaint_id = body.get('complaint_id')

        if not complaint_id:
            logger.error("Missing complaint_id in request")
            return _response(400, "Missing complaint_id")

        logger.info(f"Processing complaint: {complaint_id}")

        # Initialize Step Functions client
        stepfunctions = boto3.client('stepfunctions', region_name=AWS_REGION)

        # Build Step Function ARN
        step_function_arn = build_step_function_arn(context)
        logger.info(f"Step Function ARN: {step_function_arn}")

        # 1. Get narrative from DB
        start_time = datetime.utcnow()
        narrative = get_narrative_from_db(complaint_id)

        # 2. Start Step Function execution
        execution_arn = start_step_function(
            stepfunctions_client=stepfunctions,
            step_function_arn=step_function_arn,
            complaint_id=complaint_id,
            narrative=narrative
        )
        
        # 3. Log workflow step
        conninfo = get_connection_string()
        with psycopg.connect(conninfo) as conn:
            user = get_user_from_event(event)
            log_workflow(conn, complaint_id, 'CLASSIFICATION_STARTED',
                input_data={'narrative_length': len(narrative), 'triggered_by': user},
                output_data={'execution_arn': execution_arn},
                start_time=start_time)
            conn.commit()

        logger.info(f"✅ Successfully processed: {complaint_id}")

        # Return success response
        return _response(200, "Classification started successfully", {
            'complaint_id': complaint_id,
            'execution_arn': execution_arn,
            'status': 'started'
        })

    except ValueError as e:
        logger.error(f"❌ Validation error: {str(e)}")
        return _response(404, str(e))

    except Exception as e:
        logger.error(f"❌ Handler error: {str(e)}")
        return _response(500, f"Internal server error: {str(e)}")


def get_connection_string():
    """Get PostgreSQL connection string from Secrets Manager."""
    global _db_credentials, _connection_string

    if _connection_string:
        return _connection_string

    if not _db_credentials:
        logger.info(f"Getting DB credentials from Secrets Manager")
        _db_credentials = get_secret(DB_SECRET_NAME, DB_REGION)

    host = _db_credentials['host']
    port = _db_credentials.get('port', 5432)
    dbname = _db_credentials['dbname']
    username = _db_credentials['username']
    password = _db_credentials['password']

    _connection_string = f"postgresql://{username}:{password}@{host}:{port}/{dbname}"

    return _connection_string


def get_narrative_from_db(complaint_id):
    """
    Get complaint narrative from PostgreSQL database.

    Query simple:
    SELECT narrative FROM complaints WHERE complaint_id = 'CAS-00001'
    """
    conninfo = get_connection_string()

    logger.info(f"Fetching narrative for complaint: {complaint_id}")

    with psycopg.connect(conninfo) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT narrative FROM complaints WHERE complaint_id = %s",
                (complaint_id,)
            )

            row = cur.fetchone()

            if not row:
                raise ValueError(f"Complaint {complaint_id} not found")

            narrative = row[0]
            logger.info(f"Got narrative for {complaint_id}, length: {len(narrative)} chars")

            return narrative


def build_step_function_arn(context):
    """Build Step Function ARN from Lambda context."""
    lambda_arn = context.invoked_function_arn
    account_id = lambda_arn.split(':')[4]

    step_function_arn = f"arn:aws:states:{AWS_REGION}:{account_id}:stateMachine:{STEP_FUNCTION_NAME}"

    return step_function_arn


def start_step_function(stepfunctions_client, step_function_arn, complaint_id, narrative):
    """Start Step Function execution for complaint classification."""

    # Prepare input for Step Function
    step_input = {
        'complaint_id': complaint_id,
        'narrative': narrative,
        'status': 'IN-REVIEW',
        'triggered_at': datetime.now(timezone.utc).isoformat()
    }

    # Unique execution name
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    execution_name = f"classify-{complaint_id}-{timestamp}"

    # Start execution
    response = stepfunctions_client.start_execution(
        stateMachineArn=step_function_arn,
        name=execution_name,
        input=json.dumps(step_input)
    )

    execution_arn = response['executionArn']
    logger.info(f"Started Step Function: {execution_arn}")

    return execution_arn


def _response(status_code, message, data=None):
    """Standardized HTTP response with CORS headers"""
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