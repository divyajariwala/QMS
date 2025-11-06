import json
import logging
import os
from datetime import datetime, timezone
from decimal import Decimal

import boto3

# Environment variables
ENV = os.environ.get('env', 'dev')
STEP_FUNCTION_BASE_NAME = os.environ.get('step_function_base_name', 'classify-complaints')
STEP_FUNCTION_NAME = f"qms-{ENV}-{STEP_FUNCTION_BASE_NAME}"
AWS_REGION = os.environ.get('aws_region', 'us-east-1')
AUDIT_LOG_TABLE_BASE_NAME = os.environ.get('audit_log_table_base_name', 'complaints-audit-log')
AUDIT_LOG_TABLE_NAME = f"qms-{ENV}-{AUDIT_LOG_TABLE_BASE_NAME}"

# Setup logging
logger = logging.getLogger("classify_complaints_lambda")
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Lambda function to trigger Step Functions for complaint classification.

    Expected SQS event structure:
    {
        "Records": [
            {
                "messageId": "...",
                "body": "{...complaint data...}"
            }
        ]
    }
    """
    logger.info("Received event: %s", json.dumps(event, indent=2))

    try:
        # Initialize AWS clients (inside handler for testability)
        stepfunctions = boto3.client('stepfunctions')
        dynamodb = boto3.resource('dynamodb')
        audit_table = dynamodb.Table(AUDIT_LOG_TABLE_NAME)

        # Build Step Function ARN from context
        step_function_arn = build_step_function_arn(context)
        logger.info(f"Using Step Function ARN: {step_function_arn}")

        # Track processing results
        successful = 0
        failed = 0
        errors = []
        executions = []

        # Process each SQS message
        for record in event.get('Records', []):
            try:
                message_id = record.get('messageId', 'unknown')
                logger.info(f"Processing message: {message_id}")

                # Parse message body
                body = json.loads(record['body'])

                # Validate complaint data
                validate_complaint(body)

                complaint_id = body.get('complaint_id')
                logger.info(f"Validated complaint ID: {complaint_id}")

                try:
                    audit_entry = save_initial_audit_log(
                        audit_table=audit_table,
                        complaint_id=complaint_id,
                        complaint_data=body,
                        message_id=message_id
                    )
                    logger.info(f"Saved initial audit log for complaint ID: {complaint_id}")
                except Exception as audit_error:
                    logger.error(f"Failed to save audit log for complaint ID {complaint_id}: {str(audit_error)}")

                # Start Step Function execution
                execution_arn = start_step_function(stepfunctions, step_function_arn, body)

                successful += 1
                executions.append({
                    'complaint_id': body.get('complaint_id'),
                    'execution_arn': execution_arn,
                    'messageId': message_id,
                    'audit_logged': True
                })
                logger.info(f"Successfully started classification for complaint: {body.get('complaint_id')}")

            except json.JSONDecodeError as e:
                failed += 1
                error_msg = f"Invalid JSON in message {message_id}: {str(e)}"
                logger.error(error_msg)
                errors.append({
                    'messageId': message_id,
                    'error': 'InvalidJSON',
                    'detail': str(e)
                })

            except ValueError as e:
                failed += 1
                error_msg = f"Validation error in message {message_id}: {str(e)}"
                logger.error(error_msg)
                errors.append({
                    'messageId': message_id,
                    'error': 'ValidationError',
                    'detail': str(e)
                })

            except Exception as e:
                failed += 1
                error_msg = f"Error processing message {message_id}: {str(e)}"
                logger.error(error_msg)
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                errors.append({
                    'messageId': message_id,
                    'error': 'ProcessingError',
                    'detail': str(e)
                })

        # Log summary
        logger.info(f"Processing complete - Successful: {successful}, Failed: {failed}")

        # Return results
        return {
            'statusCode': 200 if failed == 0 else 207,
            'body': json.dumps({
                'processed': successful + failed,
                'successful': successful,
                'failed': failed,
                'executions': executions,
                'errors': errors
            })
        }

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'detail': str(e)
            })
        }


def save_initial_audit_log(audit_table, complaint_id, complaint_data, message_id):
    """
    Save initial audit log entry for the complaint classification process.

    Args:
        audit_table: DynamoDB Table resource
        complaint_id (str): Complaint ID
        complaint_data (dict): Full complaint data
        message_id (str): SQS message ID

    Returns:
        dict: Saved audit log entry
    """
    timestamp = datetime.now(timezone.utc).isoformat()

    audit_entry = {
        # Primary Keys
        'PK': f'COMPLAINT#{complaint_id}',
        'SK': 'STEP#classify-complaints-trigger',

        # Complaint Info
        'complaint_id': complaint_id,
        'lambda_name': 'classify-complaints',
        'step_name': 'classification_trigger',
        'step_order': 0,  # Primer paso

        # Execution Info
        'last_execution': {
            'timestamp': timestamp,
            'status': 'triggered',
            'message_id': message_id
        },

        # Input data
        'input': {
            'complaint_id': complaint_id,
            'narrative': complaint_data.get('narrative'),
            'code': complaint_data.get('code'),
            'status': complaint_data.get('status', 'IN-REVIEW'),
            'source': complaint_data.get('source', 'api')
        },

        # Output data (empty at this stage)
        'output': {},

        # Metadata
        'metadata': {
            'triggered_at': timestamp,
            'trigger_source': 'sqs',
            'full_complaint_data': complaint_data
        },

        # GSI1 - To query by Lambda function
        'GSI1PK': 'LAMBDA#classify-complaints',
        'GSI1SK': f"STATUS#triggered#{timestamp}",

        # GSI2 - To query by status and time
        'GSI2PK': 'STATUS#triggered',
        'GSI2SK': f"TIME#{timestamp}"
    }

    # Record audit log in DynamoDB
    audit_table.put_item(Item=audit_entry)

    logger.info(f"Audit log saved: PK={audit_entry['PK']}, SK={audit_entry['SK']}")

    return audit_entry


def build_step_function_arn(context):
    """
    Build Step Function ARN from Lambda context.

    Args:
        context: Lambda context object

    Returns:
        str: Complete Step Function ARN
    """
    # Extract account ID from Lambda ARN
    # Lambda ARN format: arn:aws:lambda:region:account-id:function:function-name
    lambda_arn = context.invoked_function_arn
    account_id = lambda_arn.split(':')[4]

    # Build complete ARN
    step_function_arn = f"arn:aws:states:{AWS_REGION}:{account_id}:stateMachine:{STEP_FUNCTION_NAME}"

    return step_function_arn


def validate_complaint(complaint):
    """
    Validate that complaint has all required fields for classification.

    Args:
        complaint (dict): Complaint data

    Raises:
        ValueError: If validation fails
    """
    required_fields = [
        'complaint_id',
        'narrative'
    ]

    # Check required fields
    missing_fields = [field for field in required_fields if field not in complaint]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

    # Validate field values
    if not complaint['complaint_id'].strip():
        raise ValueError("complaint_id cannot be empty")

    if not complaint['narrative'].strip():
        raise ValueError("narrative cannot be empty")

    if len(complaint['narrative']) > 420:
        raise ValueError("narrative exceeds maximum length of 420 characters")


def start_step_function(stepfunctions_client, step_function_arn, complaint):
    """
    Start Step Function execution for complaint classification.

    Args:
        stepfunctions_client: Boto3 Step Functions client
        step_function_arn: Complete ARN of the Step Function
        complaint (dict): Complaint data to process

    Returns:
        str: Execution ARN

    Raises:
        Exception: If Step Functions operation fails
    """
    complaint_id = complaint['complaint_id']

    try:
        # Prepare input for Step Function
        step_input = prepare_step_function_input(complaint)

        # Generate unique execution name
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
        # Add microseconds for uniqueness
        microseconds = datetime.now(timezone.utc).strftime('%f')[:3]
        execution_name = f"classify-{complaint_id}-{timestamp}-{microseconds}"

        # Start execution
        response = stepfunctions_client.start_execution(
            stateMachineArn=step_function_arn,
            name=execution_name,
            input=json.dumps(step_input, default=decimal_default)
        )

        execution_arn = response['executionArn']
        logger.info(f"Started Step Function execution: {execution_arn}")

        return execution_arn

    except Exception as e:
        logger.error(f"Step Functions error for complaint {complaint_id}: {str(e)}")
        raise


def prepare_step_function_input(complaint):
    """
    Prepare input data for Step Function execution.

    Args:
        complaint (dict): Original complaint data

    Returns:
        dict: Formatted input for Step Function
    """
    # Convert floats to Decimal for JSON serialization
    complaint_data = _convert_floats_to_decimal(complaint)

    # Build Step Function input
    step_input = {
        'complaint_id': complaint_data['complaint_id'],
        'narrative': complaint_data['narrative'],
        'code': complaint_data.get('code'),
        'status': complaint_data.get('status', 'IN-REVIEW'),
        'created_at': complaint_data.get('created_at', datetime.now(timezone.utc).isoformat()),
        'created_by': complaint_data.get('created_by'),
        'source': complaint_data.get('source', 'api'),
        'metadata': {
            'triggered_at': datetime.now(timezone.utc).isoformat(),
            'trigger_source': 'classify_complaints_lambda'
        }
    }

    # Include any additional fields from original complaint
    for key, value in complaint_data.items():
        if key not in step_input:
            step_input[key] = value

    return step_input


def _convert_floats_to_decimal(obj):
    """
    Convert floats to Decimal for JSON compatibility.

    Args:
        obj: Object to convert (dict, list, or primitive)

    Returns:
        Object with floats converted to Decimal
    """
    if isinstance(obj, list):
        return [_convert_floats_to_decimal(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: _convert_floats_to_decimal(value) for key, value in obj.items()}
    elif isinstance(obj, float):
        return Decimal(str(obj))
    else:
        return obj


def decimal_default(obj):
    """
    JSON serializer for Decimal objects.

    Args:
        obj: Object to serialize

    Returns:
        Serializable representation
    """
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
