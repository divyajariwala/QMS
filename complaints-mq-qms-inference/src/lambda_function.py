import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Union

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
aws_region_name: str = os.environ["aws_region_name"]
metadata_table_name: str = os.environ["metadata_table_name"]
state_machine_name: str = os.environ["state_machine_name"]

# Global AWS clients
lambda_client = boto3.client("lambda", region_name=aws_region_name)
dynamodb_resource = boto3.resource('dynamodb', region_name=aws_region_name)
sf = boto3.client('stepfunctions', region_name=aws_region_name)

# Audit log table
audit_table = dynamodb_resource.Table(os.environ["audit_table_name"])


def lambda_handler(event: Dict[str, Any], context: Any) -> Union[Dict[str, Any], None]:
    """
    AWS Lambda handler function to process incoming SQS messages, query DynamoDB,
    start Step Function execution, and update the audit log.

    Args:
        event (Dict[str, Any]): The event data received by the Lambda function, typically from SQS.
        context (Any): AWS Lambda execution context.

    Returns:
        Union[Dict[str, Any], None]: Returns a response object with batchItemFailures if an error occurs,
        otherwise None.
    """
    logger.info("Input event: %s", str(event))
    batch_item_failures: List[Dict[str, str]] = []
    sqs_batch_response: Dict[str, List[Dict[str, str]]] = {}

    try:
        if event:
            start_server_time: str = get_current_time()
            message_body: str = event["Records"][0]["body"]
            message_body_json: Dict[str, Any] = json.loads(message_body)
            logger.info(message_body_json)

            uuid: str = message_body_json['uuid']

            res_narrative: str = get_narrative_from_dynamodb(uuid)
            logger.info(res_narrative)

            partition_key: str = f"COMPLAINT#{str(uuid)}"
            inference_dict: Dict[str, Any] = {
                "start_server_time": start_server_time,
                "message_body": message_body,
                "message_body_json": message_body_json,
                "res_narrative": res_narrative
            }

            audit_item: Dict[str, Any] = update_audit_table(partition_key, inference_dict)

            input_dict: Dict[str, str] = {
                'uuid': uuid,
                'Complaint': res_narrative
            }
            logger.info(input_dict)

            response: Dict[str, Any] = sf.start_execution(
                stateMachineArn=state_machine_name,
                input=json.dumps(input_dict)
            )
            logger.info(f"Added the UUID to the queue {str(response)}")

            end_server_time: str = get_current_time()
            processing_time_seconds: float = calculate_processing_time(start_server_time, end_server_time)
            audit_item["inference"]["end_server_time"] = end_server_time
            audit_item["inference"]["processing_time_seconds"] = str(processing_time_seconds)
            audit_item["updated_at"] = get_current_time()
            audit_table.put_item(Item=audit_item)

    except Exception as sqs_dlq:
        logger.error("Could not process the request: %s", str(sqs_dlq))
        batch_item_failures.append(
            {"itemIdentifier": event['Records'][0]['messageId']}
        )
        sqs_batch_response["batchItemFailures"] = batch_item_failures
        logger.info(sqs_batch_response)
        return sqs_batch_response


def get_narrative_from_dynamodb(uuid: str) -> str:
    """
    Query the DynamoDB metadata table to fetch the narrative for a given UUID.

    Args:
        uuid (str): The unique identifier for the record.

    Returns:
        str: The narrative if found, otherwise an error message or default value.
    """
    try:
        response: Dict[str, Any] = dynamodb_resource.Table(metadata_table_name).get_item(
            Key={"uuid": uuid}
        )
        narrative: str = response.get('Item', {}).get('narrative', 'Narrative not found')

        if not narrative:
            logger.error(f"Narrative not found for UUID: {uuid}")
            return "Narrative not found"

        return narrative
    except Exception as e:
        logger.error(f"Error getting narrative from DynamoDB: {str(e)}")
        return "Error fetching narrative"


def update_audit_table(partition_key: str, inference_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update the audit table with the provided inference data.

    Args:
        partition_key (str): The partition key for the audit table.
        inference_dict (Dict[str, Any]): The data to update in the audit table.

    Returns:
        Dict[str, Any]: The updated audit item, or an empty dictionary if an error occurs.
    """
    try:
        audit_response: Dict[str, Any] = audit_table.get_item(Key={"PK": partition_key})
        audit_item: Dict[str, Any] = audit_response.get("Item", {})
        audit_item["inference"] = inference_dict
        audit_table.put_item(Item=audit_item)
        return audit_item
    except Exception as e:
        logger.error(f"Error updating audit table: {str(e)}")
        return {}


def get_current_time() -> str:
    """
    Get the current time in ISO 8601 format.

    Returns:
        str: The current time as a string.
    """
    return datetime.now(timezone.utc).isoformat()


def calculate_processing_time(start_time: str, end_time: str) -> float:
    """
    Calculate the processing time in seconds between two timestamps.

    Args:
        start_time (str): The start time in ISO 8601 format.
        end_time (str): The end time in ISO 8601 format.

    Returns:
        float: The processing time in seconds.
    """
    start: datetime = datetime.fromisoformat(start_time)
    end: datetime = datetime.fromisoformat(end_time)
    return (end - start).total_seconds()


def handle_exception(exception: Exception, message: str, status_code: int = 503) -> Dict[str, Any]:
    """
    Handle exceptions by logging the error and returning an HTTP response.

    Args:
        exception (Exception): The exception that occurred.
        message (str): A custom error message.
        status_code (int): The HTTP status code for the response.

    Returns:
        Dict[str, Any]: The formatted error response.
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
        body (Dict[str, Any]): The response body.
        status_code (int): The HTTP status code.

    Returns:
        Dict[str, Any]: The formatted response.
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
