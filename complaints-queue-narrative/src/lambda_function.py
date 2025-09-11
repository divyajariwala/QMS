import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict

import boto3

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
aws_region_name: str = os.environ["aws_region_name"]
complaints_queue_url: str = os.environ["complaints_queue_url"]

# AWS resources
sqs = boto3.client("sqs", region_name=aws_region_name)
dynamodb = boto3.resource("dynamodb", region_name=aws_region_name)

# Audit log table
audit_table = dynamodb.Table(os.environ["audit_table_name"])


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Entry point for the AWS Lambda function.

    Args:
        event (Dict[str, Any]): Event data passed to the function.
        context (Any): Runtime information provided by AWS Lambda.

    Returns:
        Dict[str, Any]: Response object containing status code and message.
    """
    logger.info("The input event is %s", event)

    # Basic validation of the input event
    if not event.get("body"):
        return create_response({"error": "Invalid input: No body present"}, 400)

    if "categoryinvoke" in event.get("rawPath", ""):
        start_server_time: str = get_current_time()
        content: Dict[str, Any] = json.loads(event["body"])
        content["uuid"] = content["complaint_id"]

        partition_key: str = f"COMPLAINT#{str(content['uuid'])}"
        queue_narrative_dict: Dict[str, Any] = {
            "start_server_time": start_server_time,
            "content": content,
        }

        # Retrieve existing audit log entry
        audit_response = audit_table.get_item(Key={"PK": partition_key})
        audit_item: Dict[str, Any] = audit_response.get("Item", {})
        audit_item["queue_narrative"] = queue_narrative_dict
        audit_table.put_item(Item=audit_item)

        logger.info(json.dumps(content))
        try:
            response = send_to_queue(content)
            logger.info(f"Added the UUID to the queue {str(response)}")

            end_server_time: str = get_current_time()
            processing_time = datetime.fromisoformat(
                end_server_time
            ) - datetime.fromisoformat(start_server_time)
            processing_time_seconds: float = processing_time.total_seconds()
            audit_item["queue_narrative"]["end_server_time"] = end_server_time
            audit_item["queue_narrative"]["processing_time_seconds"] = str(
                processing_time_seconds
            )
            audit_item["updated_at"] = datetime.now(timezone.utc).isoformat()
            audit_table.put_item(Item=audit_item)

            return create_response({"response": response}, 200)
        except Exception as exception:
            return handle_exception(exception, "Error sending message to SQS")


# Utils
def get_current_time() -> str:
    """
    Get the current time in ISO format.

    Returns:
        str: Current time in ISO 8601 format.
    """
    return datetime.now(timezone.utc).isoformat()


def calculate_processing_time(start_time: str, end_time: str) -> float:
    """
    Calculate the processing time between two timestamps.

    Args:
        start_time (str): Start time in ISO format.
        end_time (str): End time in ISO format.

    Returns:
        float: Processing time in seconds.
    """
    start = datetime.fromisoformat(start_time)
    end = datetime.fromisoformat(end_time)
    return (end - start).total_seconds()


def handle_exception(exception: Exception, message: str, status_code: int = 503) -> Dict[str, Any]:
    """
    Handle exceptions in the Lambda function and return a formatted error response.

    Args:
        exception (Exception): The exception that occurred.
        message (str): Custom error message to log and include in the response.
        status_code (int, optional): HTTP status code for the error. Defaults to 503.

    Returns:
        Dict[str, Any]: Error response object.
    """
    logger.error(f"{message}: {str(exception)}")
    return {
        "statusCode": status_code,
        "body": json.dumps({"error": str(exception)}),
    }


def create_response(body: Dict[str, Any], status_code: int = 200) -> Dict[str, Any]:
    """
    Create a formatted HTTP response.

    Args:
        body (Dict[str, Any]): Response body content.
        status_code (int, optional): HTTP status code. Defaults to 200.

    Returns:
        Dict[str, Any]: Formatted HTTP response object.
    """
    return {
        "statusCode": status_code,
        "body": json.dumps(body),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "isBase64Encoded": False,
    }


# SQS and DynamoDB utils
def send_to_queue(content: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send a message to the SQS queue.

    Args:
        content (Dict[str, Any]): Message content to send to the queue.

    Returns:
        Dict[str, Any]: Response from the SQS service after sending the message.
    """
    return sqs.send_message(
        QueueUrl=complaints_queue_url,
        MessageBody=json.dumps(content)
    )
