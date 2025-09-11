import json
import logging
import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List

import boto3
import requests

from secrets_util import get_secret

# Variables
aws_region: str = os.environ["aws_region_name"]
secrets_name: str = os.environ.get("secrets_name", "")

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS Resources
dynamodb_resource = boto3.resource("dynamodb", region_name=aws_region)

# Audit table
audit_table = dynamodb_resource.Table(os.environ["audit_table_name"])
audit_item: Dict[str, Any] = {}
audit_entries: List[Dict[str, Any]] = []


def lambda_handler(event: dict, context) -> dict:
    """
    AWS Lambda handler function. Processes narratives, calls external APIs, and updates the audit log.

    Args:
        event (dict): Event data containing records.
        context: Lambda execution context.

    Returns:
        dict: Processed message or output.
    """
    logger.info("Received event: %s", json.dumps(event, indent=2))
    secrets = get_secret(secret_name, aws_region)

    for record in event.get("Records", []):
        narratives = parse_narratives(record)
        audit_item["narratives"] = narratives
        init_audit_log(audit_item)
        jwt = generate_token(secrets)
        logger.info("JWT: %s", jwt)
        message = aepc_post(jwt, narratives, secrets)
        update_audit_log_with_aespc_data(message)
        logger.info("Message: %s", json.dumps(message, indent=2))
        mule_post(secrets, message)
        logger.info("Audit final entries: %s", json.dumps(audit_entries, indent=2))
        save_audit_log(audit_entries)
        return message


def get_current_time() -> str:
    """
    Get the current time in ISO format.

    Returns:
        str: Current time in ISO 8601 format.
    """
    return datetime.now(timezone.utc).isoformat()


def convert_floats_to_decimal(data: Any) -> Any:
    """
    Recursively convert float values in a dictionary or list to Decimal.

    Args:
        data (Any): Input data to process.

    Returns:
        Any: Data with float values converted to Decimal.
    """
    if isinstance(data, dict):
        return {key: convert_floats_to_decimal(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_floats_to_decimal(item) for item in data]
    elif isinstance(data, float):
        return Decimal(str(data))
    else:
        return data


def parse_narratives(record: dict) -> List[dict]:
    """
    Parse the record body and return the narratives.

    Args:
        record (dict): Record containing narrative information.

    Returns:
        List[dict]: Parsed narratives.
    """
    narratives = record.get("body", "")
    if isinstance(narratives, str):
        return json.loads(narratives)
    return narratives


def aepc_post(jwt: str, narratives: List[dict], secret: dict) -> List[dict]:
    """
    Send narratives to the AEPC API and process the response.

    Args:
        jwt (str): Authentication token.
        narratives (List[dict]): List of narratives to process.
        secret (dict): Secrets configuration.

    Returns:
        List[dict]: Response data from the AEPC API.
    """
    try:
        output = []
        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Authorization": f"Bearer {jwt}",
            "configuration-item": secret["aepc_configuration_item"],
            "operation-id": "3",
        }
        for n in narratives:
            if isinstance(n, str):
                n = json.loads(n)
            request_body = {"query": n["complaintNarrative"]}
            logger.info("Request body: %s", json.dumps(request_body, indent=2))
            response = requests.post(
                secret["aepc_post_url"],
                data=json.dumps(request_body),
                headers=headers,
                verify=False,
            )
            res = json.loads(response.content)
            res["complaintId"] = n["complaintId"]
            output.append(res)
        return output
    except Exception as e:
        raise RuntimeError(f"Error in AEPC POST: {str(e)}")


def mule_post(secret: dict, message: List[dict]) -> None:
    """
    Send the processed message to an SQS queue.

    Args:
        secret (dict): Secrets configuration.
        message (List[dict]): Message to send.

    Returns:
        None
    """
    try:
        message = {"output": message}
        sqs = boto3.client("sqs")
        response = sqs.send_message(
            QueueUrl=secret["results_queue_url"], MessageBody=json.dumps(message)
        )
        logger.info(f"Message ID: {response['MessageId']}")
    except Exception as e:
        raise RuntimeError(f"Error in Mule POST: {str(e)}")


def generate_token(secret: dict) -> str:
    """
    Generate an authentication token.

    Args:
        secret (dict): Secrets configuration.

    Returns:
        str: Generated token.
    """
    request_body = {
        "grant_type": secret["grant_type"],
        "client_id": secret["client_id"],
        "client_secret": secret["client_secret"],
        "scope": secret["scope"],
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.get(
        secret["aepc_token_url"], data=request_body, headers=headers
    )
    res = json.loads(response.content)
    return res["access_token"]


def init_audit_log(audit_item: dict) -> None:
    """
    Initialize the audit log with the narratives.

    Args:
        audit_item (dict): Audit item containing narratives.

    Returns:
        None
    """
    for item in audit_item.get("narratives", []):
        upload_audit_item_dict = {
            "partition_key": f"COMPLAINT#{item.get('complaintId')}",
            "complaint_id": item.get("complaintId"),
            "input_data": {
                "complaint_id": item.get("complaintId"),
                "complaint_narrative": item.get("complaintNarrative"),
            },
        }
        logger.info("Saving audit log: %s", upload_audit_item_dict)
        audit_entries.append(upload_audit_item_dict)


def update_audit_log_with_aespc_data(updated_data: List[dict]) -> None:
    """
    Update audit entries with AEPC data.

    Args:
        updated_data (List[dict]): Data returned from AEPC API.

    Returns:
        None
    """
    for entry in audit_entries:
        complaint_id = entry["complaint_id"]
        for item in updated_data:
            if item["complaintId"] == complaint_id:
                entry["aespc_output_data"] = item.get("data", {})
                logger.info("Updated audit entry: %s", entry)
                break


def save_audit_log(audit_entries: List[dict]) -> None:
    """
    Save audit entries to the DynamoDB audit table.

    Args:
        audit_entries (List[dict]): List of audit entries to save.

    Returns:
        None
    """
    for entry in audit_entries:
        converted_entry = convert_floats_to_decimal(entry)
        try:
            audit_table.put_item(
                Item={
                    "PK": converted_entry["partition_key"],
                    "complaint_id": converted_entry["complaint_id"],
                    "input_data": converted_entry["input_data"],
                    "aespc_output_data": converted_entry.get("aespc_output_data", {}),
                    "created_at": get_current_time(),
                }
            )
        except Exception as e:
            logger.error(f"Error saving audit log: {str(e)}")
            raise RuntimeError(f"Error saving audit log: {str(e)}")
