import json
import logging
import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Union

import boto3
from boto3.dynamodb.conditions import Attr, Key
from botocore.exceptions import ClientError

# Environment variables
aws_region_name: str = os.environ["aws_region_name"]

# AWS resources
dynamodb_resource = boto3.resource("dynamodb", region_name=aws_region_name)

# Set up logging
logger = logging.getLogger("Fetch Results Pipeline")
logger.setLevel(logging.INFO)

# Tables
audit_table = dynamodb_resource.Table(os.environ["audit_table_name"])
inference_results_table = dynamodb_resource.Table(os.environ["inference_results_table_name"])
priority_results_table = dynamodb_resource.Table(os.environ["priority_results_table_name"])
final_results_table = dynamodb_resource.Table(os.environ["final_results_table_name"])
lookup_table = dynamodb_resource.Table(os.environ["lookup_table_name"])


def lambda_handler(event: dict, context: Any) -> Union[dict, None]:
    """
    AWS Lambda handler function to process an incoming event, fetch data from DynamoDB tables,
    combine results, and update audit logs.

    Args:
        event (dict): The incoming event data, typically from an API Gateway or SQS.
        context (Any): AWS Lambda execution context.

    Returns:
        Union[dict, None]: Returns a dictionary with combined results and additional data if successful,
                           or None in case of an error.
    """
    start_server_time: str = datetime.now(timezone.utc).isoformat()
    logger.info("Input event: %s", event)

    content: dict = json.loads(event["body"])
    content['uuid'] = content['complaint_id']

    try:
        # Fetch results from inference and priority tables
        response = inference_results_table.get_item(Key={'uuid': content['uuid']})
        item_crl = eval(response.get('Item', {}).get('results', '{}'))

        response_priority = priority_results_table.get_item(Key={'uuid': content['uuid']})
        item_priority = eval(response_priority.get('Item', {}).get('results', '{}'))

        # Merge results
        combined_results = {**item_priority, **item_crl}
        logger.info("Combined results: %s", combined_results)

        # Add details
        def find_crl_value(crl_values: dict, category: str) -> Union[str, None]:
            """
            Find the CRL value matching the given category.

            Args:
                crl_values (dict): A dictionary of CRL values.
                category (str): The category to search for.

            Returns:
                Union[str, None]: The matching CRL value, or None if not found.
            """
            for key in crl_values:
                if key and key.startswith(category):
                    return key
            return None

        details: List[Dict[str, Any]] = []
        for category, category_confidence_score in combined_results["category"].items():
            crl_value_key = find_crl_value(combined_results["CRL Value"], category)
            if crl_value_key:
                crl_value = crl_value_key
            else:
                crl_value = None
            level = max(combined_results["level"], key=combined_results["level"].get)

            # Hard rules check
            if category in ["Needle did not retract", "Device not working", "Device defective"]:
                level = 2

            details.append(
                {
                    "category": category,
                    "category_confidence_score": round(category_confidence_score, 2),
                    "crl_value": crl_value,
                    "level": int(level)
                }
            )
        combined_results["details"] = details

        # Remove unused keys
        combined_results.pop("CRL Value")
        combined_results.pop("level")
        combined_results.pop("category")
        logger.info("Combined results dict: %s", combined_results)

        # Update levels
        combined_results = update_levels(combined_results)

        # Hard rules check
        hard_rules_level_2: List[str] = ["Needle did not retract", "Device not working", "Device defective"]
        for detail in combined_results["details"]:
            if detail["category"] in hard_rules_level_2:
                detail["level"] = 2

        # Final merge
        combined: Dict[str, Any] = {
            'results': combined_results
        }

        # Partition key for final results table
        partition_key: str = f"COMPLAINT#{content['uuid']}"

        fetch_result_dict: Dict[str, Any] = {
            "start_server_time": start_server_time,
            "combined_results": combined
        }
        audit_response = audit_table.get_item(Key={"PK": partition_key})
        audit_item = audit_response["Item"]
        drugname: str = audit_item.get("upload_narrative", {}).get("drugname", None)
        audit_item["fetch_result"] = fetch_result_dict

        # Put the item in the final results table
        final_results_table.put_item(
            Item={
                'PK': partition_key,
                'uuid': content['uuid'],
                'results': json.dumps(combined_results),
                'details': json.dumps(details),
                'created_at': datetime.now(timezone.utc).isoformat()
            }
        )
        end_server_time: str = datetime.now(timezone.utc).isoformat()
        processing_time: timedelta = datetime.fromisoformat(end_server_time) - datetime.fromisoformat(start_server_time)
        processing_time_seconds: float = processing_time.total_seconds()
        logger.info("Processing time: %s", processing_time_seconds)
        audit_item["fetch_result"]["end_server_time"] = end_server_time
        audit_item["fetch_result"]["processing_time_seconds"] = str(processing_time_seconds)
        audit_item["updated_at"] = datetime.now(timezone.utc).isoformat()
        converted_item: Dict[str, Any] = convert_to_dynamodb_compatible(audit_item)
        audit_table.put_item(Item=converted_item)

        # Add CRL values from lookup_table
        crl_values: List[str] = fetch_crl_values()
        combined.update({"crl_values": crl_values})
        # Add CSC values from lookup_table
        csc_values: List[str] = fetch_csc_values(drugname)
        combined.update({"csc_values": csc_values})

        if item_crl:
            logger.info("Item found: %s", item_crl)
            return {
                'statusCode': 200,
                'body': json.dumps(combined)
            }
        else:
            logger.info("Item not found")
    except ClientError as e:
        logger.error(f"Error querying item: {e.response['Error']['Message']}")


def convert_to_dynamodb_compatible(data: Any) -> Any:
    """
    Convert data to DynamoDB-compatible format.

    Args:
        data (Any): Input data.

    Returns:
        Any: DynamoDB-compatible data.
    """
    if isinstance(data, dict):
        return {k: convert_to_dynamodb_compatible(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_to_dynamodb_compatible(v) for v in data]
    elif isinstance(data, float):
        return Decimal(str(data))
    return data


def update_levels(data: dict) -> dict:
    """
    Update levels in data by overwriting them with updated levels if available.

    Args:
        data (dict): The input data containing details.

    Returns:
        dict: Data with updated levels.
    """
    if 'updated_level' in data:
        updated_level: int = data['updated_level']
        for detail in data['details']:
            detail['original_level'] = detail['level']
            detail['level'] = updated_level
    return data


def fetch_crl_values() -> List[str]:
    """
    Fetch CRL values from the lookup table.

    Returns:
        List[str]: List of CRL values.
    """
    try:
        response = lookup_table.query(KeyConditionExpression=Key('PK').eq('LOOKUP#CrlMapping'))
        return [item["crlValue"] for item in response.get('Items', [])]
    except ClientError as e:
        logger.error(f"Error fetching CRL values: {e.response['Error']['Message']}")
        return []


def fetch_csc_values(drugname: str) -> List[str]:
    """
    Fetch CSC values from the lookup table for a specific drug name.

    Args:
        drugname (str): Drug name to filter values.

    Returns:
        List[str]: List of CSC values.
    """
    try:
        response = lookup_table.query(
            KeyConditionExpression=Key('PK').eq('LOOKUP#CrlMapping'),
            FilterExpression=Attr('drugNames').contains(drugname)
        )
        return [item["cscValue"] for item in response.get('Items', [])]
    except ClientError as e:
        logger.error(f"Error fetching CSC values: {e.response['Error']['Message']}")
        return []
