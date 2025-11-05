import json
import logging
import os
from datetime import datetime, timezone
from decimal import Decimal

import boto3

# Environment variables
ENV = os.environ.get('env', 'dev')
DYNAMODB_TABLE_BASE_NAME = os.environ.get('dynamodb_table_base_name', 'complaints-metadata')
DYNAMODB_TABLE_NAME = f"qms-{ENV}-{DYNAMODB_TABLE_BASE_NAME}"
CLASSIFY_SQS_QUEUE_BASE_NAME = os.environ.get('classify_sqs_queue_base_name', 'classify-complaints')
CLASSIFY_SQS_QUEUE_NAME = f"qms-{ENV}-{CLASSIFY_SQS_QUEUE_BASE_NAME}"

# Setup logging
logger = logging.getLogger("process_complaint_lambda")
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Lambda function to process SQS messages and save complaints to DynamoDB.

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
        # Initialize AWS clients (inside handler like create_complaint)
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(DYNAMODB_TABLE_NAME)
        sqs_client = boto3.client('sqs')

        # Track processing results
        successful = 0
        failed = 0
        errors = []
        # Process each SQS message
        for record in event.get('Records', []):
            try:
                message_id = record.get('messageId', 'unknown')
                logger.info(f"Processing message: {message_id}")

                # Parse message body
                body = json.loads(record['body'])

                # Validate complaint data
                validate_complaint(body)

                # Save to DynamoDB (pass table as parameter)
                save_to_dynamodb(table, body)

                # Send to classification queue
                send_to_classify_queue(sqs_client, body)

                successful += 1
                print(f"Successfully processed complaint: {body.get('complaint_id')}")

            except json.JSONDecodeError as e:
                failed += 1
                error_msg = f"Invalid JSON in message {message_id}: {str(e)}"
                print(error_msg)
                errors.append({
                    'messageId': message_id,
                    'error': 'InvalidJSON',
                    'detail': str(e)
                })

            except ValueError as e:
                failed += 1
                error_msg = f"Validation error in message {message_id}: {str(e)}"
                print(error_msg)
                errors.append({
                    'messageId': message_id,
                    'error': 'ValidationError',
                    'detail': str(e)
                })

            except Exception as e:
                failed += 1
                error_msg = f"Error processing message {message_id}: {str(e)}"
                print(error_msg)
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                errors.append({
                    'messageId': message_id,
                    'error': 'ProcessingError',
                    'detail': str(e)
                })

        # Log summary
        print(f"Processing complete - Successful: {successful}, Failed: {failed}")

        # Return results
        return {
            'statusCode': 200 if failed == 0 else 207,
            'body': json.dumps({
                'processed': successful + failed,
                'successful': successful,
                'failed': failed,
                'errors': errors
            })
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'detail': str(e)
            })
        }


def validate_complaint(complaint):
    """
    Validate that complaint has all required fields.

    Args:
        complaint (dict): Complaint data

    Raises:
        ValueError: If validation fails
    """
    required_fields = [
        'complaint_id',
        'narrative',
        'status',
        'created_at',
        'created_by'
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


def save_to_dynamodb(table, complaint):
    """
    Save complaint to DynamoDB table using Single Table Design.

    Args:
        table: DynamoDB table resource
        complaint (dict): Complaint data to save

    Raises:
        Exception: If DynamoDB operation fails
    """
    complaint_id = complaint['complaint_id']

    try:
        # Convert floats to Decimal (required by DynamoDB)
        item = _convert_floats_to_decimal(complaint)

        # Add Single Table Design keys
        item['PK'] = f"COMPLAINT#{complaint_id}"
        item['SK'] = "METADATA"

        # Add GSI keys for querying
        status = complaint.get('status', 'pending')
        created_at = complaint.get('created_at', datetime.now(timezone.utc).isoformat())

        item['GSI1PK'] = f"STATUS#{status}"
        item['GSI1SK'] = f"CREATED#{created_at}"

        # Add processing metadata
        now = datetime.now(timezone.utc)
        item['processed_at'] = now.isoformat()
        item['table_version'] = '1.0'

        # Add source tracking if available
        if 'source' not in item:
            item['source'] = 'api'

        # Save to DynamoDB
        table.put_item(Item=item)

        print(f"Saved complaint to DynamoDB: {complaint_id}")

    except Exception as e:
        print(f"DynamoDB error for complaint {complaint_id}: {str(e)}")
        raise


def send_to_classify_queue(sqs_client, complaint):
    """
    Send complaint data to classification SQS queue.

    Args:
        sqs_client: Boto3 SQS client
        complaint (dict): Complaint data

    Raises:
        Exception: If SQS operation fails
    """
    complaint_id = complaint['complaint_id']

    try:
        # Get queue URL
        queue_url_response = sqs_client.get_queue_url(
            QueueName=CLASSIFY_SQS_QUEUE_NAME
        )
        queue_url = queue_url_response['QueueUrl']

        # Prepare message with only necessary fields
        message_body = {
            'complaint_id': complaint_id,
            'narrative': complaint['narrative']
        }

        # Send message to SQS
        response = sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message_body),
            MessageAttributes={
                'complaint_id': {
                    'StringValue': complaint_id,
                    'DataType': 'String'
                }
            }
        )

        logger.info(f"Sent complaint to classify queue: {complaint_id}, MessageId: {response['MessageId']}")

    except Exception as e:
        logger.error(f"SQS error for complaint {complaint_id}: {str(e)}")
        raise


def _convert_floats_to_decimal(obj):
    """
    Convert floats to Decimal for DynamoDB compatibility.

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
