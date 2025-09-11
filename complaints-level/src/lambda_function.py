import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import boto3
from botocore.config import Config

# Logger setup
logger = logging.getLogger("Levels Pipeline")
logger.setLevel(logging.INFO)

# Environment variables
aws_region_name: str = os.environ["aws_region_name"]

# Initialize AWS resources
dynamodb_resource = boto3.resource("dynamodb", region_name=aws_region_name)
runtime = boto3.client('runtime.sagemaker', config=Config(retries={'max_attempts': 0}), region_name=aws_region_name)

# Tables
audit_table = dynamodb_resource.Table(os.environ["audit_table_name"])
metadata_table = dynamodb_resource.Table(os.environ["metadata_table_name"])
lookup_table = dynamodb_resource.Table(os.environ["lookup_table_name"])


def get_current_time() -> str:
    """
    Get the current time in ISO format.

    Returns:
        str: Current timestamp in ISO 8601 format.
    """
    return datetime.now(timezone.utc).isoformat()


def calculate_processing_time(start_time: str, end_time: str) -> float:
    """
    Calculate the processing time between two timestamps.

    Args:
        start_time (str): Start time in ISO 8601 format.
        end_time (str): End time in ISO 8601 format.

    Returns:
        float: Processing time in seconds.
    """
    start = datetime.fromisoformat(start_time)
    end = datetime.fromisoformat(end_time)
    return (end - start).total_seconds()


def handle_exception(exception: Exception, message: str, status_code: int = 503) -> Dict[str, Any]:
    """
    Handle exceptions in the Lambda function.

    Args:
        exception (Exception): The exception that occurred.
        message (str): Message to log and include in the response.
        status_code (int): HTTP status code for the response.

    Returns:
        Dict[str, Any]: Formatted error response.
    """
    logger.error(f"{message}: {str(exception)}")
    return {
        "statusCode": status_code,
        "body": json.dumps({"error": str(exception)}),
    }


def get_item_from_dynamodb(table: Any, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Get an item from a DynamoDB table.

    Args:
        table (Any): DynamoDB table resource.
        key (Dict[str, Any]): Key to query the item.

    Returns:
        Optional[Dict[str, Any]]: Retrieved item or None if not found.
    """
    try:
        response = table.get_item(Key=key)
        return response.get('Item', None)
    except Exception as e:
        logger.error(f"Error fetching data from DynamoDB: {str(e)}")
        raise RuntimeError(f"Error fetching data from DynamoDB: {str(e)}")


def get_model_routing_from_lookup(drug_name: str) -> Dict[str, str]:
    """
    Fetch model routing information from the lookup table using the SK (Sort Key).

    Args:
        drug_name (str): The name of the drug to fetch routing information.

    Returns:
        Dict[str, str]: Routing information including model category and endpoints.

    Raises:
        RuntimeError: If no routing information is found or an error occurs.
    """
    try:
        sk_value = f"DRUG#{drug_name}"
        response = lookup_table.get_item(
            Key={
                'PK': 'LOOKUP#ModelRouting',
                'SK': sk_value
            }
        )
        item = response.get('Item', None)
        if not item:
            raise ValueError(f"No routing information found for drug: {drug_name}")
        return {
            'drugName': item['drugName'],
            'modelCategoryEndpoint': item['modelCategoryEndpoint'],
            'modelLevelEndpoint': item['modelLevelEndpoint']
        }
    except Exception as e:
        logger.error(f"Error fetching model routing from lookup table: {str(e)}")
        raise RuntimeError(f"Error fetching model routing from lookup table: {str(e)}")


def update_audit_log_initial(partition_key: str, level_dict: Dict[str, Any]) -> None:
    """
    Initial update of the audit log with base level information.

    Args:
        partition_key (str): Partition key for the audit table.
        level_dict (Dict[str, Any]): Level data to update in the audit log.

    Returns:
        None
    """
    audit_table.update_item(
        Key={"PK": partition_key},
        UpdateExpression="SET #lvl = :lvl",
        ExpressionAttributeNames={
            "#lvl": "level"
        },
        ExpressionAttributeValues={
            ":lvl": level_dict
        }
    )


def update_audit_log_results(partition_key: str, result: Dict[str, Any], end_server_time: str, processing_time_seconds: float) -> None:
    """
    Update the audit log with results, processing time, and end time.

    Args:
        partition_key (str): Partition key for the audit table.
        result (Dict[str, Any]): Processed result data.
        end_server_time (str): End time in ISO 8601 format.
        processing_time_seconds (float): Processing time in seconds.

    Returns:
        None
    """
    audit_table.update_item(
        Key={"PK": partition_key},
        UpdateExpression="SET #lvl.#result = :result, #lvl.#end = :end, #lvl.#proc_time = :proc_time, updated_at = :updated_at",
        ExpressionAttributeNames={
            "#lvl": "level",
            "#result": "result",
            "#end": "end_server_time",
            "#proc_time": "processing_time_seconds"
        },
        ExpressionAttributeValues={
            ":result": json.dumps(result),
            ":end": end_server_time,
            ":proc_time": str(processing_time_seconds),
            ":updated_at": get_current_time()
        }
    )


def invoke_sagemaker_endpoint(endpoint_name: str, payload: str) -> Dict[str, Any]:
    """
    Invoke a SageMaker endpoint and return the result.

    Args:
        endpoint_name (str): Name of the SageMaker endpoint.
        payload (str): Input payload in JSON format.

    Returns:
        Dict[str, Any]: Response from the SageMaker endpoint.

    Raises:
        RuntimeError: If the SageMaker invocation fails.
    """
    try:
        response = runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType='application/json',
            Body=payload
        )
        return json.loads(response['Body'].read().decode())
    except Exception as e:
        logger.error(f"Error invoking SageMaker endpoint: {str(e)}")
        raise RuntimeError(f"Error invoking SageMaker endpoint: {str(e)}")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda function handler for processing levels pipeline.

    Args:
        event (Dict[str, Any]): Event data triggering the Lambda function.
        context (Any): AWS Lambda runtime context.

    Returns:
        Dict[str, Any]: Final result or error response.
    """
    logger.info("Received event: %s", event)

    try:
        start_server_time = get_current_time()
        uuid = event["uuid"]

        # Get drugname
        metadata_item = get_item_from_dynamodb(metadata_table, {'uuid': uuid})
        if not metadata_item:
            raise ValueError(f"No metadata found for UUID: {uuid}")

        drugname = metadata_item.get("drugname")
        logger.info(f"The drugname is {str(drugname)}")

        # Retrieve model routing information from lookup table
        model_routing = get_model_routing_from_lookup(drugname)
        model_endpoint = model_routing.get("modelLevelEndpoint")
        logger.info(f"The model endpoint is {str(model_endpoint)}")

        # Create the input data
        complaint = event["Complaint"]
        input_data = [{
            "modelInput": {
                "Complaint": complaint
            }
        }]
        logger.info("Payload---------")
        logger.info(input_data)
        payload = json.dumps(input_data)

        # Invoke the SageMaker endpoint
        result = invoke_sagemaker_endpoint(model_endpoint, payload)
        result["uuid"] = uuid
        logger.info(f"Model result: {result}")

        # Update audit log before processing completion
        partition_key = f"COMPLAINT#{uuid}"
        level_dict = {
            "start_server_time": start_server_time,
            "complaint": complaint,
            "metadata_item": metadata_item,
            "input_data": input_data,
            "model_endpoint": model_endpoint,
            "result": json.dumps(result)
        }
        update_audit_log_initial(partition_key, level_dict)

        # Calculate processing time and update audit log after processing completion
        end_server_time = get_current_time()
        processing_time_seconds = calculate_processing_time(start_server_time, end_server_time)
        update_audit_log_results(partition_key, level_dict, end_server_time, processing_time_seconds)

        return result

    except Exception as exc:
        logger.error(f"Exception occurred: {str(exc)}")
        prediction = {'complaint': event["Complaint"], 'uuid': uuid, 'level': {'0': '0.00'}}
        return prediction
