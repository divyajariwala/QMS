import copy
import http.client
import json
import logging
import os
import ssl
from datetime import datetime, timezone
from decimal import Decimal
from urllib.parse import urlparse

import boto3
import requests
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from secrets_util import get_secret

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
aws_region_name = os.environ["aws_region_name"]
ui_results_table_name = os.environ["ui_results_table_name"]
secrets_name = os.environ["secrets_name"]

# AWS resources
dynamodb_client = boto3.client('dynamodb', region_name=aws_region_name)
dynamodb_resource = boto3.resource("dynamodb", region_name=aws_region_name)

# Tables
audit_table = dynamodb_resource.Table(os.environ["audit_table_name"])
final_results_table = dynamodb_resource.Table(os.environ["final_results_table_name"])


def lambda_handler(event, context):
    """
    Main entry point for the Lambda function.

    Args:
        event (dict): The input event containing details such as the body and other metadata.
        context (dict): The runtime context for the Lambda function.

    Returns:
        dict: A response containing the status code and body.
    """
    # Record the start time of the function execution
    start_server_time = datetime.now(timezone.utc).isoformat()
    logger.info("Input event: %s", event)

    # Retrieve secrets using a utility function
    secrets = get_secret(secrets_name, aws_region_name)

    # Parse the event body
    body = json.loads(event['body'])
    results_to_submit = []

    # Extract key fields from the request body
    uuid = body['complaint_id']
    data = body['data']
    model_priority = body.get("modelPriority", None)
    priority = body.get("priority", None)

    logger.info(f"Data: {data}, model_priority: {model_priority}, priority: {priority}")

    # Construct the partition key for DynamoDB
    partition_key = f"COMPLAINT#{uuid}"

    # Check if the DynamoDB table exists
    if not table_exists(ui_results_table_name):
        logger.error(f"Table {ui_results_table_name} does not exist.")
        return {
            'statusCode': 400,
            'body': json.dumps(f"Table {ui_results_table_name} does not exist.")
        }

    try:
        # Create model and user responses from the input data
        model_response = {f"model{i}": entry['model'] for i, entry in enumerate(data)}
        user_response = {f"user{i}": entry['user'] for i, entry in enumerate(data)}

        # Update the 'crl' field in user_response with the corresponding crlCode
        user_response_modified = copy.deepcopy(user_response)
        for value in user_response_modified.values():
            category = value.get('category')  # Retrieve category (cscValue)
            crl_value = value.get('crl')  # Retrieve the current crlValue
            if category and crl_value:
                crl_code = fetch_crl_code_from_lookup(category, crl_value)  # Query crlCode from lookup table
                value['crl'] = crl_code if crl_code else 'Unknown'

        # Construct the final result dictionary
        final_result_dict = {
            "model_response": model_response,
            "user_response": user_response_modified,
            "initial_input": body
        }

        # Add optional priorities to the result if present
        if model_priority is not None:
            final_result_dict["model_priority"] = model_priority
        if priority is not None:
            final_result_dict["priority"] = priority

        # Insert data into the UI results table
        insert_data(ui_results_table_name, uuid, model_response, user_response, model_priority, priority)

        # Prepare expression attribute names and values for DynamoDB updates
        expression_attribute_names = {
            "#model_resp": 'model response',
            "#user_resp": 'user response'
        }
        expression_attribute_values = {
            ':model_resp': model_response,
            ':user_resp': user_response,
            ':updated_at': datetime.now(timezone.utc).isoformat()
        }

        # Update expression for DynamoDB
        update_expression = "SET #model_resp = :model_resp, #user_resp = :user_resp, updated_at = :updated_at"

        # Add model_priority and priority to the update expression if provided
        if model_priority is not None:
            update_expression += ", #model_priority = :model_priority"
            expression_attribute_names["#model_priority"] = 'model_priority'
            expression_attribute_values[":model_priority"] = model_priority

        if priority is not None:
            update_expression += ", #priority = :priority"
            expression_attribute_names["#priority"] = 'priority'
            expression_attribute_values[":priority"] = priority

        # Update the final results table with the constructed update expression
        final_result = final_results_table.update_item(
            Key={'PK': partition_key},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="UPDATED_NEW"
        )
        logger.info(f"Final result saved: {final_result}")

        # Fetch and update the audit log with the final results
        audit_response = audit_table.get_item(Key={"PK": partition_key})
        audit_item = audit_response["Item"]
        audit_item["final_result"] = final_result_dict

        # Generate an authentication token for API communication
        token = generate_token(secrets)
        logger.info(f"Token generated: {token}")

        # Prepare data for submission to an external API
        for value in final_result_dict.get("user_response").values():
            logger.info("Item user response: %s", value)

            result_item = {
                "complaintId": audit_item.get("uuid"),
                "originalNarrative": audit_item.get("upload_narrative").get("narrative"),
                "complaintSubCategory": value.get("category"),
                "commonResponseLanguage": value.get("crl"),
                "priorityLevel": value.get("level"),
                "unit": str(value.get("unit")),
                "prioritySummary": json.loads(audit_item.get("priority").get("final_result")).get("summary"),
            }
            results_to_submit.append(result_item)

        logger.info("Results to submit: %s", results_to_submit)

        # Calculate and log processing time
        end_server_time = datetime.now(timezone.utc).isoformat()
        processing_time = datetime.fromisoformat(end_server_time) - datetime.fromisoformat(start_server_time)
        processing_time_seconds = processing_time.total_seconds()
        logger.info("Processing time: %s", processing_time_seconds)

        # Update audit log with processing information
        audit_item["final_result"]["start_server_time"] = start_server_time
        audit_item["final_result"]["results_to_submit"] = results_to_submit
        audit_item["final_result"]["end_server_time"] = end_server_time
        audit_item["final_result"]["processing_time_seconds"] = str(processing_time_seconds)
        audit_item["updated_at"] = datetime.now(timezone.utc).isoformat()

        # Save the updated audit log
        converted_item = convert_to_dynamodb_compatible(audit_item)
        audit_table.put_item(Item=converted_item)
        logger.info("Audit log updated successfully")

        # Post results to the external API
        response = post_record(results_to_submit, token, secrets)
        logger.info(f"Response: {response}")

        # Handle API response
        if response.get("responseStatus") != "SUCCESS":
            return {
                'statusCode': 502,
                'body': "Error in posting the record to the AI Toolkit API"
            }
        else:
            logger.info("Record posted successfully")

    except KeyError as e:
        # Handle missing keys in the input data
        logger.error("Error in %s saving the KeyError", str(e))
        return {
            'statusCode': 503,
            'body': json.dumps(str(e))
        }

    except Exception as insert_exception:
        # Handle other exceptions
        logger.error("Error in %s saving the raw data", insert_exception)
        exception_text = str(insert_exception)
        logger.info(exception_text)
        return {
            'statusCode': 503,
            'body': json.dumps(str(exception_text))
        }

    # Return success response with submitted results
    return {
        'statusCode': 200,
        'body': json.dumps(results_to_submit)
    }


def insert_data(table_name, item_uuid, model_response, user_response, model_priority=None, priority=None):
    """
    Inserts an item into a specified DynamoDB table.

    Args:
        table_name (str): The name of the DynamoDB table.
        item_uuid (str): A unique identifier for the item.
        model_response (dict): The model's response data.
        user_response (dict): The user's response data.
        model_priority (Optional[int]): The priority assigned by the model, if available.
        priority (Optional[int]): The priority specified by the user, if available.

    Returns:
        dict: A dictionary containing the status of the operation.
    """
    try:
        # Prepare the item to insert into the DynamoDB table
        item = {
            'uuid': item_uuid,
            'model_response': model_response,
            'user_response': user_response
        }

        # Add model_priority and priority if they are provided
        if model_priority is not None:
            item['model_priority'] = model_priority
        if priority is not None:
            item['priority'] = priority

        # Insert the item into the DynamoDB table
        dynamodb_resource.Table(table_name).put_item(Item=item)
        logger.info(f"Item with uuid {item_uuid} added successfully.")
    except Exception as e:
        # Log any exceptions that occur during the operation
        logger.info(f"Error putting item: {e}")

    return {
        'statusCode': 200,
        'body': json.dumps('DynamoDB item setup completed.')
    }


def convert_to_dynamodb_compatible(data):
    """
    Converts data into a format compatible with DynamoDB.

    Args:
        data: The data to be converted, which can be a dict, list, float, or other types.

    Returns:
        Converted data in a format compatible with DynamoDB (e.g., handling Decimal for float).
    """
    if isinstance(data, dict):
        # Recursively convert dictionary values
        return {k: convert_to_dynamodb_compatible(v) for k, v in data.items()}
    elif isinstance(data, list):
        # Recursively convert list elements
        return [convert_to_dynamodb_compatible(v) for v in data]
    elif isinstance(data, float):
        # Convert floats to Decimal (required by DynamoDB)
        return Decimal(str(data))
    else:
        # Return the data as-is for other types
        return data


# Utils
def get_current_time():
    """
    Get the current time in ISO 8601 format.

    Returns:
        str: The current time in ISO 8601 format with timezone.
    """
    return datetime.now(timezone.utc).isoformat()


def calculate_processing_time(start_time, end_time):
    """
    Calculate the processing time between two timestamps.

    Args:
        start_time (str): The start time in ISO 8601 format.
        end_time (str): The end time in ISO 8601 format.

    Returns:
        float: The total processing time in seconds.
    """
    start = datetime.fromisoformat(start_time)
    end = datetime.fromisoformat(end_time)
    return (end - start).total_seconds()


def handle_exception(exception, message, status_code=503):
    """
    Handles exceptions and logs error messages.

    Args:
        exception (Exception): The exception object.
        message (str): A custom error message.
        status_code (int): The HTTP status code to include in the response.

    Returns:
        dict: A formatted error response.
    """
    logger.error(f"{message}: {str(exception)}")
    return {
        "statusCode": status_code,
        "body": json.dumps({"error": str(exception)}),
    }


def create_response(body, status_code=200):
    """
    Creates a formatted HTTP response.

    Args:
        body (dict): The body content of the response.
        status_code (int): The HTTP status code of the response.

    Returns:
        dict: The formatted HTTP response.
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


def parse_event_body(event):
    """
    Parses and validates the body of an event.

    Args:
        event (dict): The event object containing the request body.

    Returns:
        dict: The parsed and validated event body.

    Raises:
        ValueError: If required fields are missing or the JSON is invalid.
    """
    try:
        content = json.loads(event["body"])
        # Ensure the required keys are present in the event body
        if not all(key in content for key in ["time", "narrative"]):
            raise ValueError("Missing required fields in the request body")
        return content
    except (KeyError, ValueError, json.JSONDecodeError) as e:
        raise ValueError(f"Invalid event body: {str(e)}")


# DynamoDB utils
def table_exists(table_name):
    """
    Checks if a DynamoDB table exists.

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


def save_audit_log(uid4, content, start_server_time):
    """
    Saves the initial log to the audit table.

    Args:
        uid4 (str): Unique identifier for the audit log entry.
        content (dict): Content data to include in the log.
        start_server_time (str): The server start time in ISO 8601 format.

    Raises:
        RuntimeError: If there is an error saving the log.
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
                "upload_narrative": upload_narrative_dict,
                "created_at": get_current_time(),
            }
        )
    except Exception as e:
        raise RuntimeError(f"Error saving audit log: {str(e)}")


def update_audit_log(uid4, end_server_time, processing_time_seconds):
    """
    Updates the audit log with the processing time and end time.

    Args:
        uid4 (str): Unique identifier for the audit log entry.
        end_server_time (str): The server end time in ISO 8601 format.
        processing_time_seconds (float): The total processing time in seconds.

    Raises:
        RuntimeError: If there is an error updating the log.
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


def generate_token(secret):
    """
    Generates an authentication token using client credentials.

    Args:
        secret (dict): Secret credentials for the authentication request.

    Returns:
        str: The generated access token.

    Raises:
        RuntimeError: If there is an error during the token generation process.
    """
    try:
        request_body = {
            'grant_type': 'client_credentials',
            'client_id': secret['token_client_id'],
            'client_secret': secret['token_client_secret'],
            'scope': secret['token_scope']
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.post(secret['token_url'], data=request_body, headers=headers)
        response.raise_for_status()
        res = response.json()
        return res['access_token']
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"HTTP Error: {e.response.status_code}, Message: {e.response.text}")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Request Error: {str(e)}")


def post_record(results, token, secret):
    """
    Posts results to an external AI Toolkit API.

    Args:
        results (list): The results to be sent to the API.
        token (str): The authentication token.
        secret (dict): Secret credentials for the API.

    Returns:
        dict: The API response.
    """
    headers = {
        'Content-Type': 'application/json;charset=utf-8',
        'Authorization': f'Bearer {token}',
        "client_id": secret["toolkit_client_id"],
        "client_secret": secret["toolkit_client_secret"],
    }
    url = f"{secret['mqqms_ai_toolkit_eapi_url']}/classification"
    response = requests.post(url, json=results, headers=headers, verify=False)
    logger.info(f"Response: {response}")
    return response.json()


def post_record_with_http_client(results, token, secret):
    """
    Posts results to the AI Toolkit API using http.client.

    Args:
        results (list): The results to be sent to the API.
        token (str): The authentication token.
        secret (dict): Secret credentials for the API.

    Returns:
        dict: The API response.
    """
    url = urlparse(secret['mqqms_ai_toolkit_eapi_url'])
    context = ssl._create_unverified_context()
    connection = http.client.HTTPSConnection(url.netloc, context=context)

    headers = {
        'Content-Type': 'application/json;charset=utf-8',
        'Authorization': f'Bearer {token}',
        "client_id": secret["toolkit_client_id"],
        "client_secret": secret["toolkit_client_secret"],
    }
    payload = json.dumps(results)
    endpoint = f"{url.path}/classification"
    connection.request("POST", endpoint, body=payload, headers=headers)
    response = connection.getresponse()
    logger.info(f"Response status: {response.status}")
    response_data = response.read().decode("utf-8")
    connection.close()
    try:
        return json.loads(response_data)
    except json.JSONDecodeError:
        logger.error("Failed to decode JSON response.")
        return {"error": "Invalid response format"}


def fetch_crl_code_from_lookup(category, crl_value):
    """
    Fetches the crlCode from the lookup table based on category and crlValue.

    Args:
        category (str): The complaint sub-category.
        crl_value (str): The CRL value.

    Returns:
        str or None: The crlCode if found, otherwise None.
    """
    lookup_table = dynamodb_resource.Table(os.environ["lookup_table_name"])
    try:
        response = lookup_table.query(
            KeyConditionExpression=Key('PK').eq('LOOKUP#CrlMapping') & Key('SK').eq(f"CRL#{category}")
        )
        items = response.get('Items', [])
        for item in items:
            if item.get('crlValue') == crl_value:
                return item.get('crlCode')
        logger.warning(f"No matching crlCode found for category '{category}' and crlValue '{crl_value}'")
        return None
    except ClientError as e:
        logger.error(f"Error fetching crlCode: {e.response['Error']['Message']}")
        return None
