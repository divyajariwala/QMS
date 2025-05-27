import json
import logging
import os
from typing import Any, Dict

from secrets_util import get_secret
from utils import (
    AuthError,
    DataFetchError,
    generate_error_response,
    generate_success_response,
    generate_token,
    get_record,
)

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda entry point for handling requests.

    Args:
        event (Dict[str, Any]): The event data passed to the Lambda function,
            typically from API Gateway or another AWS service.
        context (Any): The runtime information provided by AWS Lambda.

    Returns:
        Dict[str, Any]: A JSON-formatted HTTP response with status code and message.
    """
    logger.info("Received event: %s", json.dumps(event, indent=2))

    # Extract environment variables
    aws_region_name: str = os.environ.get("aws_region_name", "us-east-2")
    secrets_name: str = os.environ.get("secrets_name", "")

    if not secrets_name:
        logger.error("Secrets name is not set in environment variables")
        return generate_error_response(500, "Internal Server Error: Missing secrets name")

    # Extract query parameters
    query_params: Dict[str, Any] = event.get("queryStringParameters", {})
    complaint_id: str = query_params.get("recordId")
    session_id: str = query_params.get("sessionId") or None
    user_name: str = query_params.get("userName") or None
    if not complaint_id:
        return generate_error_response(400, "Missing 'recordId' query parameter")

    try:
        # Retrieve secrets and generate an authentication token
        secrets = get_secret(secrets_name, aws_region_name)
        # token = generate_token(secrets)
        # logger.info("Generated token: %s", token)

        # Fetch record using the token and secrets
        # record = get_record(complaint_id, token, secrets)
        record = {
            "complaintId": complaint_id,
        }
        logger.info("Fetched record: %s", json.dumps(record, indent=2))

        # Return a success response with the fetched record
        return generate_success_response(
            {
                "complaint_id": record.get("complaintId", None),
                "complaint_narrative": record.get("complaintNarrative", None),
                "drugname": record.get("drugName", None),
                "session_id": session_id,
                "user_name": user_name,
            }
        )
    except AuthError as e:
        logger.error(f"Auth Error: {str(e)}")
        return generate_error_response(401, "Authentication Failed")
    except DataFetchError as e:
        logger.error(f"Data Fetch Error: {str(e)}")
        return generate_error_response(500, "Failed to fetch data")
    except Exception as e:
        logger.error(f"Unexpected Error: {str(e)}")
        return generate_error_response(500, "Internal Server Error")
