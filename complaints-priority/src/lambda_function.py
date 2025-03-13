import json
import logging
import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, Union

import boto3

# Environment variables
aws_region_name = os.environ["aws_region_name"]
priority_results_table_name = os.environ["priority_results_table_name"]
model_id = os.environ["llm_model_id"]
priority_enabled = os.environ["priority_enabled_flag"] == "1"

# AWS resources
dynamodb_client = boto3.client('dynamodb', region_name=aws_region_name)
dynamodb_resource = boto3.resource("dynamodb", region_name=aws_region_name)
client = boto3.client("bedrock-runtime", region_name="us-east-1")

# Setup logging
logger = logging.getLogger("SEP_Priority_Checker")
logger.setLevel(logging.INFO)

# Tables
audit_table = dynamodb_resource.Table(os.environ["audit_table_name"])


def lambda_handler(event, context):
    start_server_time = datetime.now(timezone.utc).isoformat()
    logger.info("Input event: %s", str(event))
    body = json.loads(event["body"])
    try:
        uuid = body["uuid"]
        complaint = body["complaint"]
        level = list(body["level"].keys())[0]

        if priority_enabled:
            logger.info("Priority calculation started...")
            csc = list(body["category"].keys())[0]
            input_data = {
                "Complaint": complaint,
                "Level": level,
                "csc": csc
            }
            prompt1 = f'''
You are a professional medical assessor with the following task:

Given a medical product complaint narrative, check if the complaint narrative should be considered as Level 3:
    Consider a narrative as Level 3 if it explicitly mentions any of the following issues:
        - Unspecified product appearance issue (e.g., broken/chipped tablets, cloudy unused solution)
        - appearance-solution is cloudy
        - Foreign material in unused drug product
        - Illegible batch on label, wrong product in package
        - Musty/Moldy Odor in Dry Products
        - Metal seal crimping issue (on parenteral product) indicating potential container closure integrity rupture without misuse
        - Reported Counterfeit
        - Reported Tampering
        - Lot number / mfg date / expiry date discrepancy

Here is the complaint narrative: {complaint}.
Here is the complaint level: {level}.

Please provide the answer in the following JSON format:
    Level: (if the level information has been updated in step a then output the updated version, otherwise the original level),
    Reason: (why or why not you assign level 3 for this complaint narrative)
            '''
            # Format the request payload using the model's native structure.
            native_request = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2048,
                "temperature": 0,
                "messages": [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": prompt1}],
                    }
                ],
            }
            payload = json.dumps(native_request)
            response = client.invoke_model(modelId=model_id, body=payload)
            model_response = json.loads(response["body"].read())
            response_text = model_response["content"][0]["text"]
            result = json.loads(response_text)
            updated_level = result['Level']
            print(f"updated_level {updated_level}")
            prompt2 = f'''
You are a professional medical assessor with the following task:

a. Determine if the complaint narrative is Priority:
    Based on this information, apply the following priority rules strictly and without personal judgment:
        1. All Level 3 complaints must be Priority.
        2. Level 2 complaints related to emergency medications requiring an investigation record are Priority. (the narrative has to explicity mention the narrative is related to emergency medications)
        3. Complaints with CSCs other than "Lack of Drug Effect" that are related to products with Emergency Use Authorizations are Priority.
        4. All complaints requiring a response to a Regulatory Authority are Priority.
        5. Complaints requiring prompt investigation for *Japan* malfunction reporting, as requested by the *Japan* affiliate, are Priority.
    Please carefully review the narrative. If there is any doubt or ambiguity, do not assign Priority. It is better to under-classify than to incorrectly assign a high priority.
    In addition, please provide an explanation (1-2 sentences) of why you determinate as a priority or non-priority.

b. Summarizing medical product complaints
    Step 1: Identify the core issues related to the product complaint.
    Step 2: Disregard general process steps or information not directly related to the complaint.
    Step 3: Exclude any extraneous details that don't contribute to understanding the nature of the complaint.
    Step 4: Summarize the key points of the complaint in a clear, concise manner.
    step 5: Ensure your summary captures the essential information needed to understand the complaint without unnecessary elaboration.
    The summary should be succinct yet informative (2-3 sentences), providing a quick overview of the complaint's main points for efficient review

Here is the complaint narrative: {complaint}.
Here is the complaint level: {updated_level}.
Here is the complaint sub category: {csc}.

Please provide the answer in the following JSON format:
    CSC: {csc}
    Level: {updated_level},
    Priority: (1 if the complaint is priority, otherwise 0)
    Priority Reason: (the priority reason from part a)
    Priority Summary: (the priority summary from part b)
    '''
            native_request = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2048,
                "temperature": 0,
                "messages": [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": prompt2}],
                    }
                ],
            }
            payload = json.dumps(native_request)
            # Invoke the model with the request.
            response = client.invoke_model(modelId=model_id, body=payload)
            logger.info(response)
            model_result = json.loads(response["body"].read())
            final_result = model_result["content"][0]["text"]
            final_result = json.loads(final_result)
            logger.info(model_result)
            print("check here", final_result)

            final_result = {
                'uuid': uuid,
                'updated_level': final_result["Level"],
                'priority': final_result["Priority"],
                'reason': final_result["Priority Reason"],
                'summary': final_result["Priority Summary"]
            }
            logger.info(final_result)

        else:
            logger.info("Priority summary generation started...")
            prompt1 = f'''
You are a professional medical assessor with the following task:

Assuming you are receiving this priority medical product complaint narrative:
    Step 1: Identify the core issues related to the product complaint.
    Step 2: Disregard general process steps or information not directly related to the complaint.
    Step 3: Exclude any extraneous details that don't contribute to understanding the nature of the complaint.
    Step 4: Summarize the key points of the complaint in a clear, concise manner.
    step 5: Ensure your summary captures the essential information needed to understand the complaint without unnecessary elaboration.
    The summary should be succinct yet informative (2-3 sentences), providing a quick overview of the complaint's main points for efficient review
Here is the complaint narrative: {complaint}.

Please provide the answer in the following JSON format:
    Priority Summary:
            '''
            native_request = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2048,
                "temperature": 0,
                "messages": [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": prompt1}],
                    }
                ],
            }
            payload = json.dumps(native_request)
            response = client.invoke_model(modelId=model_id, body=payload)
            model_response = json.loads(response["body"].read())
            response_text = model_response["content"][0]["text"]
            final_result = json.loads(response_text)
            final_result = {
                'uuid': uuid,
                'summary': final_result["Priority Summary"]
            }

        # Verify if the table priority_results_table_name exists
        if not table_exists(priority_results_table_name):
            return handle_exception(f"Table {priority_results_table_name} does not exist.", "Table does not exist", 400)

        try:
            response = insert_data(priority_results_table_name, uuid, final_result)
            logger.info("item has been created")
        except Exception as insert_exception:
            logger.error("Error in %s saving the raw data", insert_exception)
            exception_text = str(insert_exception)
            logger.info(exception_text)
            return {
                'statusCode': 503,
                'body': json.dumps(str(exception_text))
            }

        partition_key = f"COMPLAINT#{str(uuid)}"
        priority_dict = {
            "start_server_time": start_server_time,
            "input_data": (input_data := input_data) if 'input_data' in locals() else None,
            "model_id": model_id,
            "prompt1": prompt1,
            "prompt2": (prompt2 := prompt2) if 'prompt2' in locals() else None,
            "final_result": json.dumps(final_result)
        }
        audit_response = audit_table.get_item(Key={"PK": partition_key})
        audit_item = audit_response["Item"]
        audit_item["priority"] = priority_dict
        end_server_time = datetime.now(timezone.utc).isoformat()
        processing_time = datetime.fromisoformat(end_server_time) - datetime.fromisoformat(start_server_time)
        processing_time_seconds = processing_time.total_seconds()
        logger.info("Processing time: %s", processing_time_seconds)
        audit_item["priority"]["end_server_time"] = end_server_time
        audit_item["priority"]["processing_time_seconds"] = str(processing_time_seconds)
        audit_item["updated_at"] = datetime.now(timezone.utc).isoformat()
        converted_item = convert_to_dynamodb_compatible(audit_item)
        audit_table.put_item(Item=converted_item)

        return {
            'statusCode': 200,
            'body': json.dumps(final_result)
        }

    except Exception as exc:
        logger.info(exc)
        logger.error(f"Exception i.e. {str(exc)} has occured.")
        prediction = {'priority': 0, 'reason': 'error occured', 'summary': 'error occured', 'uuid': body['uuid']}
        return prediction


def insert_data(table_name: str, item_uuid: str, result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Insert data into a DynamoDB table.

    Args:
        table_name (str): Name of the DynamoDB table.
        item_uuid (str): Unique identifier for the item to insert.
        result (Dict[str, Any]): Data to insert into the table.

    Returns:
        Dict[str, Any]: A response confirming the insertion status.
    """
    try:
        dynamodb_client.put_item(
            TableName=table_name,
            Item={
                'uuid': {'S': str(item_uuid)},
                'results': {'S': str(result)},
                'created_at': {'S': datetime.now(timezone.utc).isoformat()}
            })
        logger.info(f"Item with uuid {item_uuid} added successfully.")
    except Exception as e:
        logger.info(f"Error putting item: {e}")

    return {
        'statusCode': 200,
        'body': json.dumps('DynamoDB item setup completed.')
    }


def convert_to_dynamodb_compatible(data: Any) -> Any:
    """
    Convert Python data into a format compatible with DynamoDB.

    Args:
        data (Any): Data to convert.

    Returns:
        Any: Data in a format compatible with DynamoDB.
    """
    if isinstance(data, dict):
        return {k: convert_to_dynamodb_compatible(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_to_dynamodb_compatible(v) for v in data]
    elif isinstance(data, float):
        return Decimal(str(data))
    else:
        return data


def get_current_time() -> str:
    """
    Get the current time in ISO format.

    Returns:
        str: Current time in ISO 8601 format.
    """
    return datetime.now(timezone.utc).isoformat()


def calculate_processing_time(start_time: str, end_time: str) -> float:
    """
    Calculate the processing time in seconds between two timestamps.

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
    Handle exceptions and return a formatted error response.

    Args:
        exception (Exception): The exception that occurred.
        message (str): Custom error message.
        status_code (int, optional): HTTP status code for the error. Defaults to 503.

    Returns:
        Dict[str, Any]: Error response object.
    """
    logger.error(f"{message}: {str(exception)}")
    return {
        "statusCode": status_code,
        "body": json.dumps({"error": str(exception)}),
    }


def create_response(body: Union[Dict[str, Any], str], status_code: int = 200) -> Dict[str, Any]:
    """
    Create a formatted HTTP response.

    Args:
        body (Union[Dict[str, Any], str]): Response body content.
        status_code (int, optional): HTTP status code. Defaults to 200.

    Returns:
        Dict[str, Any]: HTTP response object.
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
        event (Dict[str, Any]): Event containing the body.

    Returns:
        Dict[str, Any]: Parsed event body.

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
        table_name (str): Name of the table to check.

    Returns:
        bool: True if the table exists, False otherwise.
    """
    try:
        dynamodb_client.describe_table(TableName=table_name)
        return True
    except dynamodb_client.exceptions.ResourceNotFoundException:
        return False


def save_audit_log(uid4: str, content: Dict[str, Any], start_server_time: str) -> None:
    """
    Save the initial audit log in the DynamoDB audit table.

    Args:
        uid4 (str): Unique identifier for the complaint.
        content (Dict[str, Any]): Complaint content data.
        start_server_time (str): Start time of the operation.

    Returns:
        None
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


def update_audit_log(uid4: str, end_server_time: str, processing_time_seconds: float) -> None:
    """
    Update the audit log with processing time and end time.

    Args:
        uid4 (str): Unique identifier for the complaint.
        end_server_time (str): End time of the operation.
        processing_time_seconds (float): Total processing time in seconds.

    Returns:
        None
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
