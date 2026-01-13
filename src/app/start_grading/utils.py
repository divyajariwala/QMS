import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional


def response(status_code: int, message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Standardized HTTP response with CORS headers

    Args:
        status_code: HTTP status code
        message: Response message
        data: Optional data payload

    Returns:
        Formatted API Gateway response
    """
    body = {
        "success": status_code < 400,
        "message": message,
        "data": data or {},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS, GET",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Max-Age": "86400"
        },
        "body": json.dumps(body)
    }


def handle_cors_preflight() -> Dict[str, Any]:
    """
    Handle CORS preflight OPTIONS requests

    Returns:
        CORS preflight response
    """
    return response(200, "OK")


def parse_event_body(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse body from API Gateway event

    Args:
        event: Lambda event from API Gateway

    Returns:
        Parsed body as dictionary

    Raises:
        json.JSONDecodeError: If body is not valid JSON
    """
    if 'body' in event:
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
    else:
        body = event

    return body