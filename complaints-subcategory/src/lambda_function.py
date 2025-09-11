import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import boto3
from botocore.config import Config

# Logger setup
logger = logging.getLogger("Subcategory Pipeline")
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


# Utility Functions
def get_current_time() -> str:
    """
    Get the current time in ISO 8601 format.

    Returns:
        str: Current UTC time in ISO format.
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
    Handle exceptions in the Lambda function and generate an error response.

    Args:
        exception (Exception): The exception that occurred.
        message (str): A descriptive error message.
        status_code (int, optional): HTTP status code. Defaults to 503.

    Returns:
        Dict[str, Any]: Error response containing the status code and error message.
    """
    logger.error(f"{message}: {str(exception)}")
    return {
        "statusCode": status_code,
        "body": json.dumps({"error": str(exception)}),
    }


def get_item_from_dynamodb(table: Any, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Retrieve an item from a DynamoDB table.

    Args:
        table (Any): DynamoDB table resource.
        key (Dict[str, Any]): Key to identify the item in the table.

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
    Fetch model routing information from the lookup table using the drug name.

    Args:
        drug_name (str): The drug name to query the lookup table.

    Returns:
        Dict[str, str]: Routing information including model endpoints.

    Raises:
        RuntimeError: If data retrieval fails or no routing information is found.
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


def update_audit_log_initial(partition_key: str, subcategory_dict: Dict[str, Any]) -> None:
    """
    Perform an initial update of the audit log with subcategory information.

    Args:
        partition_key (str): Partition key to locate the audit item.
        subcategory_dict (Dict[str, Any]): Subcategory data to store.

    Returns:
        None
    """
    audit_table.update_item(
        Key={"PK": partition_key},
        UpdateExpression="SET #subcat = :subcat",
        ExpressionAttributeNames={
            "#subcat": "subcategory"
        },
        ExpressionAttributeValues={
            ":subcat": subcategory_dict
        }
    )


def update_audit_log_results(partition_key: str, result: Dict[str, Any], end_server_time: str, processing_time_seconds: float) -> None:
    """
    Update the audit log with the processing results, end time, and processing time.

    Args:
        partition_key (str): Partition key to locate the audit item.
        result (Dict[str, Any]): Processed result to store.
        end_server_time (str): End time of the process in ISO format.
        processing_time_seconds (float): Processing time in seconds.

    Returns:
        None
    """
    audit_table.update_item(
        Key={"PK": partition_key},
        UpdateExpression="SET #subcat.#result = :result, #subcat.#end = :end, #subcat.#proc_time = :proc_time, updated_at = :updated_at",
        ExpressionAttributeNames={
            "#subcat": "subcategory",
            "#result": "result",
            "#end": "end_server_time",
            "#proc_time": "processing_time_seconds",
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
        payload (str): JSON-formatted payload to send to the endpoint.

    Returns:
        Dict[str, Any]: Parsed JSON response from the SageMaker endpoint.

    Raises:
        RuntimeError: If the invocation fails.
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
    Main Lambda function to process subcategory assignment and update the audit log.

    Args:
        event (Dict[str, Any]): Event data containing the UUID and complaint details.
        context (Any): AWS Lambda context object.

    Returns:
        Dict[str, Any]: Processed subcategory result or error prediction.
    """
    logger.info("Received event: %s", event)

    try:
        start_server_time = get_current_time()
        uuid: str = event["uuid"]

        # Get drugname from metadata
        metadata_item = get_item_from_dynamodb(metadata_table, {'uuid': uuid})
        if not metadata_item:
            raise ValueError(f"No metadata found for UUID: {uuid}")

        drugname: str = metadata_item.get("drugname")
        logger.info(f"The drugname is {drugname}")

        # Retrieve model routing information
        model_routing = get_model_routing_from_lookup(drugname)
        model_endpoint: str = model_routing.get("modelCategoryEndpoint")
        logger.info(f"The model endpoint is {model_endpoint}")

        # Prepare input data
        complaint: str = event["Complaint"]
        input_data = [{"modelInput": {"Complaint": complaint}}]
        payload = json.dumps(input_data)

        # Log initial processing state
        partition_key = f"COMPLAINT#{uuid}"
        subcategory_dict = {
            "start_server_time": start_server_time,
            "metadata_item": metadata_item,
            "model_endpoint": model_endpoint,
            "complaint": complaint,
        }
        update_audit_log_initial(partition_key, subcategory_dict)

        # Process using SageMaker
        result = invoke_sagemaker_endpoint(model_endpoint, payload)
        result["uuid"] = uuid
        logger.info(f"Model result: {result}")

        # Finalize processing
        end_server_time = get_current_time()
        processing_time_seconds = calculate_processing_time(start_server_time, end_server_time)
        update_audit_log_results(partition_key, result, end_server_time, processing_time_seconds)

        return result

    except Exception as exc:
        logger.error(f"Exception occurred: {str(exc)}")
        prediction = {'complaint': event.get("Complaint", ""), 'uuid': uuid, 'subcategory': {'null': 'error'}}
        return prediction
