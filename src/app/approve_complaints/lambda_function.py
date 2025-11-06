import json
import boto3
import os
from datetime import datetime, timezone
from decimal import Decimal

# Environment variables
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', 'qms-dev-complaints-metadata')

def lambda_handler(event, context):
    """
    Lambda function to approve complaints by updating caseStatus from pending to processed.
    
    Expected POST body format (based on input.json):
    {
        "case_id": "RGL23-000070",
        "receipt_date": "08/Jan/2023",
        "criticality": "Major",
        "report_type": "Spontaneous",
        "ai_summary": "...",
        "case_type": ["AE", "PC"],
        "narrative": "...",
        "primary_reporter": {...},
        "patient_name": "...",
        "physician_name": "...",
        "product_details": {...},
        "caseStatus": "pending",
        "categoryDetails": [...]
    }
    """
    try:
        # Initialize DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(DYNAMODB_TABLE_NAME)
        
        # Parse request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        # Validate required fields
        case_id = body.get('case_id')
        if not case_id:
            return _error_response(400, "case_id is required")
        
        current_status = body.get('caseStatus', '').lower()
        if current_status != 'pending':
            return _error_response(400, f"Can only approve complaints with pending status. Current status: {current_status}")
        
        # Check if complaint exists
        try:
            response = table.get_item(
                Key={
                    'PK': f'COMPLAINT#{case_id}',
                    'SK': 'METADATA'
                }
            )
            
            if 'Item' not in response:
                return _error_response(404, f"Complaint with case_id '{case_id}' not found")
            
            existing_item = response['Item']
            print(f"DEBUG: Existing item keys: {list(existing_item.keys())}")
            print(f"DEBUG: Existing case_type: {existing_item.get('case_type')}")
            print(f"DEBUG: Existing primary_reporter: {existing_item.get('primary_reporter')}")
            
        except Exception as e:
            return _error_response(500, f"Error retrieving complaint: {str(e)}")
        
        # Start with existing item and only update specific fields
        updated_item = existing_item.copy()
        
        # Ensure case_id is properly set
        updated_item['case_id'] = case_id
        
        # Update status-related fields
        updated_item.update({
            'GSI1PK': 'STATUS#processed',  # Update GSI for status queries
            'GSI1SK': f'COMPLAINT#{case_id}',
            'caseStatus': 'processed',  # Change status to processed
            'status': 'processed',  # Keep both for compatibility
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'approved_at': datetime.now(timezone.utc).isoformat(),
            'approved_by': _get_user_from_event(event)
        })
        
        # Only update fields that are explicitly provided in the request body
        if 'receipt_date' in body:
            updated_item['receipt_date'] = body['receipt_date']
        if 'criticality' in body:
            updated_item['criticality'] = body['criticality']
        if 'report_type' in body:
            updated_item['report_type'] = body['report_type']
        if 'ai_summary' in body:
            updated_item['ai_summary'] = body['ai_summary']
        if 'case_type' in body:
            updated_item['case_type'] = body['case_type']
        if 'narrative' in body:
            updated_item['narrative'] = body['narrative']
        if 'primary_reporter' in body:
            updated_item['primary_reporter'] = body['primary_reporter']
        if 'patient_name' in body:
            updated_item['patient_name'] = body['patient_name']
        if 'physician_name' in body:
            updated_item['physician_name'] = body['physician_name']
        if 'product_details' in body:
            updated_item['product_details'] = body['product_details']
        if 'category_details' in body:
            updated_item['category_details'] = body['category_details']
            
        print(f"DEBUG: Updated case_type: {updated_item.get('case_type')}")
        print(f"DEBUG: Updated primary_reporter: {updated_item.get('primary_reporter')}")
        
        # Ensure required fields have default values if missing
        field_defaults = {
            'case_type': [],
            'primary_reporter': {},
            'patient_name': '',
            'physician_name': '',
            'product_details': {},
            'category_details': [],
            'criticality': 'NA',
            'report_type': 'NA',
            'ai_summary': '',
            'narrative': '',
            'receipt_date': ''
        }
        
        for field, default_value in field_defaults.items():
            if field not in updated_item or updated_item[field] is None:
                updated_item[field] = default_value
        
        # Update the item in DynamoDB
        try:
            table.put_item(Item=updated_item)
            
            # Prepare response with updated data
            response_data = {
                'case_id': updated_item['case_id'],
                'receipt_date': updated_item['receipt_date'],
                'criticality': updated_item['criticality'],
                'report_type': updated_item['report_type'],
                'ai_summary': updated_item['ai_summary'],
                'case_type': updated_item['case_type'],
                'narrative': updated_item['narrative'],
                'primary_reporter': updated_item['primary_reporter'],
                'patient_name': updated_item['patient_name'],
                'physician_name': updated_item['physician_name'],
                'product_details': updated_item['product_details'],
                'category_details': updated_item['category_details'],
                'caseStatus': updated_item['caseStatus'],
                'approved_at': updated_item['approved_at'],
                'approved_by': updated_item['approved_by']
            }
            
            return {
                'statusCode': 200,
                'headers': _get_cors_headers(),
                'body': json.dumps({
                    'success': True,
                    'message': f'Complaint {case_id} approved successfully',
                    'data': response_data
                }, cls=DecimalEncoder)
            }
            
        except Exception as e:
            return _error_response(500, f"Error updating complaint: {str(e)}")
        
    except json.JSONDecodeError as e:
        return _error_response(400, f"Invalid JSON format: {str(e)}")
    
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return _error_response(500, f"Internal server error: {str(e)}")

def _get_user_from_event(event):
    """Extract user information from event"""
    try:
        request_context = event.get('requestContext', {})
        authorizer = request_context.get('authorizer', {})
        
        if 'claims' in authorizer:
            return authorizer['claims'].get('email') or authorizer['claims'].get('sub')
        
        headers = event.get('headers', {})
        return headers.get('x-user-email') or headers.get('x-user-id') or 'system'
    except Exception:
        return 'system'

def _error_response(status_code, message):
    """Return standardized error response"""
    return {
        'statusCode': status_code,
        'headers': _get_cors_headers(),
        'body': json.dumps({
            'success': False,
            'error': message,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
    }

def _get_cors_headers():
    """Return CORS headers for API Gateway"""
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }

class DecimalEncoder(json.JSONEncoder):
    """JSON encoder for DynamoDB Decimal types"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)