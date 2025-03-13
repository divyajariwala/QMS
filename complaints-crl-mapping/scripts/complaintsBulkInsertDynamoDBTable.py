import json

import boto3
from botocore.exceptions import ClientError

# Create a DynamoDB client
dynamodb = boto3.resource("dynamodb")

# Table name
table_name = "mq-qms-complaints-unified-lookups-dev"  # Replace <Environment> with your environment
table = dynamodb.Table(table_name)


def batch_write_items(items):
    """
    Function to load data into the table using batch write
    """
    try:
        with table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)
        return {"status": "success", "message": "Batch upload successful."}
    except ClientError as e:
        return {"status": "error", "message": e.response["Error"]["Message"]}


def lambda_handler(event, context):
    """
    Main Lambda function. Receives the event with the data to be loaded.
    """
    # Parse the data from the event
    try:
        items = event["items"]  # The data must be in the 'items' key
    except KeyError:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "No items found for batch upload."}),
        }

    # Load the data into the DynamoDB table
    response = batch_write_items(items)

    # Return the result of the operation
    return {"statusCode": 200, "body": json.dumps(response)}
