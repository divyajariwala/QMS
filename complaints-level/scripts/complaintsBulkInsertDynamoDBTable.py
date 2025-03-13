import json
from typing import Any, Dict, List

import boto3
from botocore.exceptions import ClientError

# Create a DynamoDB client
dynamodb = boto3.resource('dynamodb')

# Table name
table_name: str = 'mq-qms-complaints-unified-lookups-dev'  # Replace <Environment> with your environment
table = dynamodb.Table(table_name)


def batch_write_items(items: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Load data into the DynamoDB table using batch write.

    Args:
        items (List[Dict[str, Any]]): List of items to be written to the table.

    Returns:
        Dict[str, str]: A status dictionary indicating success or error message.
    """
    try:
        with table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)
        return {"status": "success", "message": "Batch upload successful."}
    except ClientError as e:
        return {"status": "error", "message": e.response['Error']['Message']}


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function. Processes batch data upload to DynamoDB.

    Args:
        event (Dict[str, Any]): Event data containing items to be uploaded.
        context (Any): AWS Lambda runtime context.

    Returns:
        Dict[str, Any]: Response object with the status code and operation result.
    """
    # Parse the data from the event
    try:
        items: List[Dict[str, Any]] = event['items']  # The data must be in the 'items' key
    except KeyError:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "No items found for batch upload."
            })
        }

    # Load the data into the DynamoDB table
    response: Dict[str, str] = batch_write_items(items)

    # Return the result of the operation
    return {
        "statusCode": 200,
        "body": json.dumps(response)
    }
