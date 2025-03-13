import json
import logging
import os
from datetime import datetime, timezone
from decimal import Decimal

import boto3

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
aws_region_name = os.environ["aws_region_name"]
inference_results_table_name = os.environ["inference_results_table_name"]

# AWS resources
dynamodb_client = boto3.client("dynamodb", region_name=aws_region_name)
dynamodb_resource = boto3.resource("dynamodb", region_name=aws_region_name)

# Tables
audit_table = dynamodb_resource.Table(os.environ["audit_table_name"])
lookup_table = dynamodb_resource.Table(os.environ["lookup_table_name"])


def lambda_handler(event: dict, context) -> dict:
    """
    AWS Lambda handler function. Processes input data and updates audit logs.

    Args:
        event (dict): Input event data from API Gateway or another service.
        context (LambdaContext): Runtime information provided by AWS Lambda.

    Returns:
        dict: Response object containing status code and result data.
    """
    logger.info("Received event is %s", event)
    start_server_time = get_current_time()

    # Verify if the table exists in dynamoDB before proceeding
    if not table_exists(inference_results_table_name):
        return handle_exception(
            f"Table {inference_results_table_name} does not exist.",
            "Table does not exist",
            400,
        )

    uuid = event[0]["uuid"]
    complaint = event[0]["complaint"]
    input_data = extract_input_data(event)

    # Query CRL mappings from lookup_table
    crl_mappings = fetch_crl_mappings(input_data)

    # Perform CRL mapping
    crl_mapping_result = perform_crl_mapping(input_data, crl_mappings)
    result = {**input_data, "CRL Value": crl_mapping_result}

    try:
        insert_data(inference_results_table_name, uuid, result)
        logger.info("item has been created")
    except Exception as insert_exception:
        return handle_exception(insert_exception, "Error inserting item", 500)

    # Prepare the priority result
    priority = {**result, "uuid": uuid, "complaint": complaint}

    # Update audit log
    partition_key = f"COMPLAINT#{uuid}"
    crl_mapping_dict = {
        "start_server_time": start_server_time,
        "complaint": complaint,
        "input_data": input_data,
    }
    audit_item = get_audit_item(partition_key)
    audit_item["crl_mapping"] = crl_mapping_dict
    update_audit_log_with_results(
        audit_item, start_server_time, result, end_server_time=get_current_time()
    )

    return create_response(priority)


def extract_input_data(event: list) -> dict:
    """
    Extracts input data from the event.

    Args:
        event (list): List of event items containing levels and categories.

    Returns:
        dict: Extracted input data containing levels and categories.
    """
    input_data = {}
    for item in event:
        if "level" in item:
            input_data["level"] = item["level"]
        if "category" in item:
            input_data["category"] = item["category"]
    return input_data


def insert_data(table_name: str, item_uuid: str, result: dict) -> dict:
    """
    Inserts data into a specified DynamoDB table.

    Args:
        table_name (str): Name of the DynamoDB table.
        item_uuid (str): Unique identifier for the item.
        result (dict): Data to be inserted.

    Returns:
        dict: Confirmation of successful insertion.
    """
    try:
        dynamodb_client.put_item(
            TableName=table_name,
            Item={
                "uuid": {"S": str(item_uuid)},
                "results": {"S": str(result)},
                "updated_at": {"S": datetime.now(timezone.utc).isoformat()},
            },
        )
        logger.info(f"Item with uuid {item_uuid} added successfully.")
    except Exception as e:
        logger.info(f"Error putting item: {e}")

    return {"statusCode": 200, "body": json.dumps("DynamoDB item setup completed.")}


def convert_to_dynamodb_compatible(data):
    """
    Converts Python data to DynamoDB-compatible format.

    Args:
        data (any): Data to be converted.

    Returns:
        any: Data in DynamoDB-compatible format.
    """
    if isinstance(data, dict):
        return {k: convert_to_dynamodb_compatible(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_to_dynamodb_compatible(v) for v in data]
    elif isinstance(data, float):
        return Decimal(str(data))
    else:
        return data


def get_audit_item(partition_key: str) -> dict:
    """
    Retrieves an audit item from the DynamoDB table.

    Args:
        partition_key (str): Partition key of the audit item.

    Returns:
        dict: Retrieved audit item.
    """
    audit_response = audit_table.get_item(Key={"PK": partition_key})
    return audit_response.get("Item", {})


def update_audit_log_with_results(
    audit_item: dict, start_server_time: str, result: dict, end_server_time: str
) -> None:
    """
    Updates the audit log with results and processing time.

    Args:
        audit_item (dict): Existing audit item to be updated.
        start_server_time (str): Start time of the process.
        result (dict): Results to update in the audit log.
        end_server_time (str): End time of the process.

    Returns:
        None
    """
    processing_time_seconds = calculate_processing_time(
        start_server_time, end_server_time
    )

    audit_item["crl_mapping"]["end_server_time"] = end_server_time
    audit_item["crl_mapping"]["processing_time_seconds"] = str(processing_time_seconds)
    audit_item["updated_at"] = get_current_time()

    converted_item = convert_to_dynamodb_compatible(audit_item)
    audit_table.put_item(Item=converted_item)


def get_current_time() -> str:
    """
    Gets the current time in ISO format.

    Returns:
        str: Current time in ISO 8601 format.
    """
    return datetime.now(timezone.utc).isoformat()


def calculate_processing_time(start_time: str, end_time: str) -> float:
    """
    Calculates the processing time between two timestamps.

    Args:
        start_time (str): Start time in ISO 8601 format.
        end_time (str): End time in ISO 8601 format.

    Returns:
        float: Processing time in seconds.
    """
    start = datetime.fromisoformat(start_time)
    end = datetime.fromisoformat(end_time)
    return (end - start).total_seconds()


def handle_exception(exception: Exception, message: str, status_code: int = 503) -> dict:
    """
    Handles exceptions and generates error responses.

    Args:
        exception (Exception): The exception that occurred.
        message (str): Error message to include in the response.
        status_code (int): HTTP status code for the response.

    Returns:
        dict: Error response object.
    """
    logger.error(f"{message}: {str(exception)}")
    return {
        "statusCode": status_code,
        "body": json.dumps({"error": str(exception)}),
    }


def create_response(body: dict, status_code: int = 200) -> dict:
    """
    Creates a formatted HTTP response.

    Args:
        body (dict): Body of the response.
        status_code (int): HTTP status code.

    Returns:
        dict: Formatted HTTP response.
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


def fetch_crl_mappings(input_data: dict) -> dict:
    """
    Fetches CRL mappings from the lookup table based on input categories.

    Args:
        input_data (dict): Input data containing categories.

    Returns:
        dict: Mappings of categories to CRL values.
    """
    crl_mappings = {}
    try:
        for category in input_data.get("category", {}):
            sk_value = f"CRL#{category}"
            response = lookup_table.get_item(
                Key={"PK": "LOOKUP#CrlMapping", "SK": sk_value}
            )
            item = response.get("Item")
            if item:
                crl_mappings[category] = item["crlValue"]
            else:
                crl_mappings[category] = "Unassigned CRL"
    except Exception as e:
        logger.error(f"Error fetching CRL mappings: {str(e)}")
        raise RuntimeError(f"Error fetching CRL mappings: {str(e)}")
    return crl_mappings


def perform_crl_mapping(input_data: dict, crl_mappings: dict) -> dict:
    """
    Maps input data categories to CRL values using fetched mappings.

    Args:
        input_data (dict): Input data containing categories.
        crl_mappings (dict): Fetched CRL mappings.

    Returns:
        dict: Mapped CRL values for each category.
    """
    crl_mapping = {}
    for key, value in input_data.get("category", {}).items():
        if key in crl_mappings:
            crl_mapping[crl_mappings[key]] = value
        else:
            crl_mapping["Unassigned CRL"] = value
    return crl_mapping


def parse_event_body(event: dict) -> dict:
    """
    Parses and validates the event body.

    Args:
        event (dict): Event object containing the body.

    Returns:
        dict: Parsed and validated event body.

    Raises:
        ValueError: If required fields are missing or invalid.
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
    Checks if a DynamoDB table exists.

    Args:
        table_name (str): Name of the table to check.

    Returns:
        bool: True if the table exists, False otherwise.
    """
    try:
        dynamodb_client.describe_table(TableName=table_name)
        return True
    except dynamodb_client.exceptions.ResourceNotFoundException:
        return False


def save_audit_log(uid4: str, content: dict, start_server_time: str) -> None:
    """
    Saves the initial audit log in the audit table.

    Args:
        uid4 (str): Unique identifier for the item.
        content (dict): Content to save in the audit log.
        start_server_time (str): Start time of the process.

    Returns:
        None
    """
    partition_key = f"COMPLAINT#{str(uid4)}"
    upload_narrative_dict = {
        "start_server_time": start_server_time,
        "narrative_time": content["time"],
        "narrative": content["narrative"],
        "drugname": content.get("drugname", "Mounjaro"),
    }

    try:
        audit_table.put_item(
            Item={
                "PK": partition_key,
                "uuid": str(uid4),
                "upload_narrative": upload_narrative_dict,
                "created_at": get_current_time(),
            }
        )
    except Exception as e:
        raise RuntimeError(f"Error saving audit log: {str(e)}")


def update_audit_log(uid4: str, end_server_time: str, processing_time_seconds: float) -> None:
    """
    Updates the audit log with processing time and end time.

    Args:
        uid4 (str): Unique identifier for the item.
        end_server_time (str): End time of the process.
        processing_time_seconds (float): Time taken for the process.

    Returns:
        None
    """
    partition_key = f"COMPLAINT#{str(uid4)}"
    try:
        audit_response = audit_table.get_item(Key={"PK": partition_key})
        audit_item = audit_response["Item"]
        audit_item["upload_narrative"]["end_server_time"] = end_server_time
        audit_item["upload_narrative"]["processing_time_seconds"] = str(
            processing_time_seconds
        )
        audit_table.put_item(Item=audit_item)
    except Exception as e:
        raise RuntimeError(f"Error updating audit log: {str(e)}")
