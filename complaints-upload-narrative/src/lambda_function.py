import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

import boto3

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
metadata_table_name = os.environ["metadata_table_name"]  # Name of the metadata table in DynamoDB
aws_region_name = os.environ["aws_region_name"]  # AWS region name

# AWS resources
dynamodb_client = boto3.client("dynamodb", region_name=aws_region_name)
dynamodb_resource = boto3.resource("dynamodb", region_name=aws_region_name)

# Audit log table
audit_table = dynamodb_resource.Table(os.environ["audit_table_name"])  # Name of the audit log table


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main entry point for the Lambda function.

    Args:
        event (Dict[str, Any]): The input event from the API Gateway.
        context (Any): The runtime context for the Lambda function.

    Returns:
        Dict[str, Any]: A JSON response with status code and message.
    """
    logger.info("Received event: %s", event)
    uid4 = None  # Unique identifier for the complaint

    try:
        # Validate the incoming API call
        if "invokeapi" not in event.get("rawPath", ""):
            raise ValueError("Invalid API call")

        # Get the current time at the start of processing
        start_server_time = get_current_time()

        # Parse and validate the event body
        content = parse_event_body(event)

        # Generate or extract the complaint ID
        if "complaint_id" in content and content["complaint_id"]:
            uid4 = content["complaint_id"]
        else:
            uid4 = uuid.uuid4()

        content["uuid"] = str(uid4)
        session_id = content.get("session_id", None)
        user_name = content.get("user_name", None)

        # Insert the initial data into the audit log table
        save_audit_log(uid4, session_id, user_name, content, start_server_time)

        # Validate if the metadata table exists
        if not table_exists(metadata_table_name):
            raise ValueError(f"Table {metadata_table_name} does not exist.")

        # Insert the complaint data into the metadata table
        insert_data(
            metadata_table_name,
            str(uid4),
            content["narrative"],
            content["time"],
            content.get("drugname", "DEVICE MOUNJARO")
        )

        # Calculate the processing time and update the audit log
        end_server_time = get_current_time()
        processing_time_seconds = calculate_processing_time(start_server_time, end_server_time)
        update_audit_log(uid4, end_server_time, processing_time_seconds)

        # Return the response with the generated complaint ID
        return create_response(str(uid4), 200)

    except Exception as e:
        # Log the error and handle exceptions
        logger.error(f"Error processing request: {str(e)}")
        return handle_exception(e, "Error processing request")


def get_current_time() -> str:
    """
    Get the current time in ISO 8601 format.

    Returns:
        str: The current time in ISO 8601 format.
    """
    return datetime.now(timezone.utc).isoformat()


def calculate_processing_time(start_time: str, end_time: str) -> float:
    """
    Calculate the processing time between two timestamps.

    Args:
        start_time (str): The start time in ISO 8601 format.
        end_time (str): The end time in ISO 8601 format.

    Returns:
        float: The processing time in seconds.
    """
    start = datetime.fromisoformat(start_time)
    end = datetime.fromisoformat(end_time)
    return (end - start).total_seconds()


def handle_exception(exception: Exception, message: str, status_code: int = 503) -> Dict[str, Any]:
    """
    Handle exceptions and create a formatted error response.

    Args:
        exception (Exception): The exception that occurred.
        message (str): A custom error message.
        status_code (int): The HTTP status code for the response.

    Returns:
        Dict[str, Any]: A JSON response containing the error message.
    """
    logger.error(f"{message}: {str(exception)}")
    return {
        "statusCode": status_code,
        "body": json.dumps({"error": str(exception)}),
    }


def create_response(body: str, status_code: int = 200) -> Dict[str, Any]:
    """
    Create a formatted response for the Lambda function.

    Args:
        body (str): The body of the response.
        status_code (int): The HTTP status code.

    Returns:
        Dict[str, Any]: A JSON response.
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


def parse_event_body(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse and validate the event body.

    Args:
        event (Dict[str, Any]): The input event from the API Gateway.

    Returns:
        Dict[str, Any]: The parsed content of the event body.

    Raises:
        ValueError: If required fields are missing or the body is invalid.
    """
    try:
        content = json.loads(event["body"])
        if not all(key in content for key in ["time", "narrative"]):
            raise ValueError("Missing required fields in the request body")
        return content
    except (KeyError, ValueError, json.JSONDecodeError) as e:
        raise ValueError(f"Invalid event body: {str(e)}")


def table_exists(table_name: str) -> bool:
    """
    Check if a DynamoDB table exists.

    Args:
        table_name (str): The name of the DynamoDB table.

    Returns:
        bool: True if the table exists, False otherwise.
    """
    try:
        dynamodb_client.describe_table(TableName=table_name)
        return True
    except dynamodb_client.exceptions.ResourceNotFoundException:
        return False


def save_audit_log(uid4: str, session_id: str, user_name: str, content: Dict[str, Any], start_server_time: str) -> None:
    """
    Save the initial log in the audit table.

    Args:
        uid4 (str): The unique identifier for the complaint.
        content (Dict[str, Any]): The content of the complaint.
        start_server_time (str): The start time of the process in ISO 8601 format.

    Raises:
        RuntimeError: If an error occurs while saving the log.
    """
    partition_key = f"COMPLAINT#{str(uid4)}"
    upload_narrative_dict = {
        "start_server_time": start_server_time,
        "narrative_time": content["time"],
        "narrative": content["narrative"],
        "drugname": content.get("drugname", "Mounjaro")
    }

    try:
        audit_table.put_item(
            Item={
                "PK": partition_key,
                "uuid": str(uid4),
                "session_id": session_id,
                "user_name": user_name,
                "upload_narrative": upload_narrative_dict,
                "created_at": get_current_time(),
            }
        )
    except Exception as e:
        raise RuntimeError(f"Error saving audit log: {str(e)}")


def update_audit_log(uid4: str, end_server_time: str, processing_time_seconds: float) -> None:
    """
    Update the audit log with processing time and end time.

    Args:
        uid4 (str): The unique identifier for the complaint.
        end_server_time (str): The end time of the process in ISO 8601 format.
        processing_time_seconds (float): The total processing time in seconds.

    Raises:
        RuntimeError: If an error occurs while updating the log.
    """
    partition_key = f"COMPLAINT#{str(uid4)}"
    try:
        audit_response = audit_table.get_item(Key={"PK": partition_key})
        audit_item = audit_response["Item"]
        audit_item["upload_narrative"]["end_server_time"] = end_server_time
        audit_item["upload_narrative"]["processing_time_seconds"] = str(processing_time_seconds)
        audit_table.put_item(Item=audit_item)
    except Exception as e:
        raise RuntimeError(f"Error updating audit log: {str(e)}")


def insert_data(table_name: str, item_uuid: str, narrative: str, dt: str, drugname: str) -> None:
    """
    Insert an item into the DynamoDB table.

    Args:
        table_name (str): The name of the DynamoDB table.
        item_uuid (str): The unique identifier for the complaint.
        narrative (str): The narrative content of the complaint.
        dt (str): The timestamp associated with the complaint.
        drugname (str): The name of the drug associated with the complaint.

    Raises:
        RuntimeError: If an error occurs while inserting the data.
    """
    try:
        dynamodb_client.put_item(
            TableName=table_name,
            Item={
                "uuid": {"S": item_uuid},
                "narrative": {"S": narrative},
                "datetime": {"S": dt},
                "drugname": {"S": drugname},
            },
        )
        logger.info(f"Item with uuid {item_uuid} added successfully.")
    except Exception as e:
        raise RuntimeError(f"Error inserting data into DynamoDB: {str(e)}")
