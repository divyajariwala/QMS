import json
from datetime import datetime


def response(status_code: int, message: str, data: dict = None):
    """
    Create a standardized API response
    
    Args:
        status_code: HTTP status code
        message: Response message
        data: Optional data payload
        
    Returns:
        API Gateway response dict with CORS headers
    """
    body = {
        'success': status_code < 400,
        'message': message,
        'data': data if data is not None else {},
        'timestamp': datetime.utcnow().isoformat() + '+00:00'
    }
    
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'OPTIONS,PUT'
        },
        'body': json.dumps(body)
    }


def handle_cors_preflight():
    """
    Handle CORS preflight OPTIONS request
    
    Returns:
        API Gateway response for OPTIONS request
    """
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'OPTIONS,PUT'
        },
        'body': json.dumps({'message': 'CORS preflight successful'})
    }


def parse_event_body(event: dict):
    """
    Parse and validate event body
    
    Args:
        event: Lambda event dict
        
    Returns:
        Parsed body as dict
        
    Raises:
        ValueError: If body is missing or invalid JSON
    """
    body = event.get('body')
    
    if not body:
        raise ValueError("Request body is required")
    
    try:
        if isinstance(body, str):
            return json.loads(body)
        return body
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in request body: {str(e)}")
