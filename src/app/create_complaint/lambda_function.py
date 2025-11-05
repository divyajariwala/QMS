import json
import logging
import os
import random
import string
from datetime import datetime, timezone

import boto3

# Environment variables
ENV = os.environ.get('env', 'dev')
CODE_STRATEGY = os.environ.get('CODE_STRATEGY', 'timestamp_random')
SQS_QUEUE_BASE_NAME = os.environ.get('sqs_queue_base_name', 'preload-complaints')
SQS_QUEUE_NAME = f"qms-{ENV}-{SQS_QUEUE_BASE_NAME}"


# Setup logging
logger = logging.getLogger("create_complaint_lambda")
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Lambda function to create a complaint and enqueue it for processing.

    Expected POST body:
    {
        "narrative": "Detailed description of the complaint here (max 420 chars)."
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

        if len(narrative) > 420:
            return _response(400, "Narrative exceeds maximum length of 420 characters")

        # Generate unique complaint code
        complaint_code = generate_complaint_code(CODE_STRATEGY)

        # Create complaint message
        now = datetime.now(timezone.utc)
        complaint_message = {
            'complaint_id': complaint_code,
            'narrative': narrative,
            'short_description': narrative[:100],  # First 100 chars as short desc
            'status': 'IN-REVIEW',
            'caseStatus': 'pending',
            'criticality': 'NA',
            'report_type': 'NA',
            'created_at': now.isoformat(),
            'updated_at': now.isoformat(),
            'created_by': _get_user_from_event(event),
            'metadata': {
                'source': 'manual',
                'version': '1.0'
            }
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
                'ComplaintCode': {
                    'StringValue': complaint_code,
                    'DataType': 'String'
                },
                'CreatedBy': {
                    'StringValue': _get_user_from_event(event),
                    'DataType': 'String'
                }
            }
        )

        print(f"Complaint sent to SQS successfully: {complaint_code}, MessageId: {sqs_response['MessageId']}")

        return _response(200, "Complaint created and queued for processing", {
            'complaint': {
                'complaint_id': complaint_code,
                'code': complaint_code,
                'narrative': narrative,
                'short_description': complaint_message['short_description'],
                'status': 'IN-REVIEW',
                'created_at': now.isoformat()
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


def generate_complaint_code(strategy='timestamp_random'):
    """
    Generate unique complaint code with different strategies

    Strategies:
    - timestamp_random: CAS-20241030154523789 (timestamp + 3 random digits)
    - ulid: CAS-01HQZP2N7V8CHJ... (ULID format)
    - uuid_short: CAS-A7B2C9D4 (8 chars from UUID)
    - nanoid: CAS-V1StGXR8 (8 random alphanumeric)
    """

    if strategy == 'timestamp_random':
        # CAS-20241030154523789456 (timestamp with microseconds + 3 random digits)
        now = datetime.now(timezone.utc)
        timestamp = now.strftime('%Y%m%d%H%M%S')
        microseconds = str(now.microsecond)[:3]  # First 3 digits of microseconds
        random_suffix = ''.join(random.choices(string.digits, k=3))
        return f"CAS-{timestamp}{microseconds}{random_suffix}"

    elif strategy == 'ulid':
        # CAS-01HQZP2N7V8CHJ9K3T2W4X5Y6Z
        ulid = generate_ulid()
        return f"CAS-{ulid}"

    elif strategy == 'uuid_short':
        # CAS-A7B2C9D4
        import uuid
        short_uuid = str(uuid.uuid4()).replace('-', '')[:8].upper()
        return f"CAS-{short_uuid}"

    elif strategy == 'nanoid':
        # CAS-V1StGXR8
        nanoid = generate_nanoid(8)
        return f"CAS-{nanoid}"

    else:
        # Default: timestamp_random
        return generate_complaint_code('timestamp_random')


def generate_ulid():
    """
    Generate ULID (Universally Unique Lexicographically Sortable Identifier)
    Format: 26 characters, time-sortable
    """
    # Timestamp part (10 chars, 48 bits)
    timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)

    # Crockford's Base32 encoding
    encoding = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

    # Encode timestamp (10 characters)
    time_part = ""
    for _ in range(10):
        time_part = encoding[timestamp % 32] + time_part
        timestamp //= 32

    # Random part (16 chars, 80 bits)
    random_part = ''.join(random.choices(encoding, k=16))

    return time_part + random_part


def generate_nanoid(length=8):
    """
    Generate Nanoid-style identifier
    URL-safe, readable, no ambiguous characters
    """
    # Exclude similar looking characters: 0/O, 1/I/l
    alphabet = "23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz"
    return ''.join(random.choices(alphabet, k=length))


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
