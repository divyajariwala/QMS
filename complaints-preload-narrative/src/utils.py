import json
from typing import Any, Dict

import requests


class AuthError(Exception):
    """Custom exception for authentication errors."""

    pass


class DataFetchError(Exception):
    """Custom exception for data fetching errors."""

    pass


def generate_token(secret: Dict[str, Any]) -> str:
    """
    Generate an authentication token using client credentials.

    Args:
        secret (Dict[str, Any]): Dictionary containing client credentials and token endpoint.

    Returns:
        str: Generated authentication token.

    Raises:
        AuthError: If there is an issue generating the token.
    """
    url = secret["token_url"]
    request_body = {
        "grant_type": "client_credentials",
        "client_id": secret["token_client_id"],
        "client_secret": secret["token_client_secret"],
        "scope": secret["token_scope"],
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        response = requests.post(url, data=request_body, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        res = response.json()  # Parse JSON response
        return res["access_token"]
    except requests.exceptions.HTTPError as e:
        raise AuthError(f"HTTP Error: {response.status_code}, Message: {response.text}, Exception: {str(e)}")
    except requests.exceptions.RequestException as e:
        raise AuthError(f"Request Error: {str(e)}")


def get_record(record_id: str, token: str, secret: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch a record from an external API using a token.

    Args:
        record_id (str): The ID of the record to fetch.
        token (str): Bearer token for authorization.
        secret (Dict[str, Any]): Dictionary containing client credentials and API URL.

    Returns:
        Dict[str, Any]: Record data retrieved from the external API.

    Raises:
        DataFetchError: If there is an issue fetching the record.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "client_id": secret["toolkit_client_id"],
        "client_secret": secret["toolkit_client_secret"],
    }

    url = f"{secret['mqqms_ai_toolkit_eapi_url']}/classification?complaintId={record_id}"
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        return response.json()  # Parse JSON response
    except requests.exceptions.HTTPError as e:
        raise DataFetchError(f"HTTP Error: {str(e)}")
    except requests.exceptions.RequestException as e:
        raise DataFetchError(f"Request Error: {str(e)}")
    except ValueError as e:
        raise DataFetchError(f"Request Error: Invalid JSON, {str(e)}")


def generate_success_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a success response.

    Args:
        data (Dict[str, Any]): Data to include in the success response.

    Returns:
        Dict[str, Any]: HTTP success response with a 200 status code and data.
    """
    return {"statusCode": 200, "body": json.dumps(data)}


def generate_error_response(status_code: int, message: str) -> Dict[str, Any]:
    """
    Generate an error response.

    Args:
        status_code (int): HTTP status code for the error response.
        message (str): Error message to include in the response.

    Returns:
        Dict[str, Any]: HTTP error response with the provided status code and message.
    """
    return {"statusCode": status_code, "body": json.dumps({"error": message})}
