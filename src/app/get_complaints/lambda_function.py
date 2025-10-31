import json
import boto3
import os
from datetime import datetime, timezone
from decimal import Decimal

# Environment variables
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', 'qms-dev-complaints-metadata')

def lambda_handler(event, context):
    """
    Lambda function handler to retrieve complaints data from DynamoDB.
    Supports two endpoints:
    - GET /getComplaints - Returns all complaints with stats
    - GET /getComplaints/{complaint_id} - Returns specific complaint details
    """
    try:
        # Initialize DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(DYNAMODB_TABLE_NAME)
        
        # Get path parameters
        path_parameters = event.get('pathParameters', {})
        complaint_id = path_parameters.get('complaint_id') if path_parameters else None
        
        if complaint_id:
            # Handle single complaint request: /getComplaints/{complaint_id}
            return get_single_complaint(table, complaint_id)
        else:
            # Handle all complaints request: /getComplaints
            return get_all_complaints(table)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': _get_cors_headers(),
            'body': json.dumps({
                'success': False,
                'error': 'Internal server error',
                'message': str(e)
            })
        }

def get_single_complaint(table, complaint_id):
    """
    Get single complaint details by complaint_id
    """
    try:
        # Query using PK for the specific complaint
        response = table.get_item(
            Key={
                'PK': f'COMPLAINT#{complaint_id}',
                'SK': 'METADATA'
            }
        )
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': _get_cors_headers(),
                'body': json.dumps({
                    'success': False,
                    'error': 'Complaint not found'
                })
            }
        
        item = response['Item']
        
        # Transform DynamoDB item to response format
        complaint_details = {
            'case_id': item.get('case_id', item.get('complaint_id', complaint_id)),
            'receipt_date': item.get('receipt_date', item.get('created_at', '')),
            'criticality': item.get('criticality', 'NA'),
            'report_type': item.get('report_type', 'NA'),
            'ai_summary': item.get('ai_summary', item.get('short_description', '')),
            'case_type': item.get('case_type', []),
            'narrative': item.get('narrative', item.get('narrative_text', '')),
            'primary_reporter': item.get('primary_reporter', {}),
            'patient_name': item.get('patient_name', ''),
            'physician_name': item.get('physician_name', ''),
            'product_details': item.get('product_details', {}),
            'caseStatus': item.get('status', 'pending')
        }
        
        return {
            'statusCode': 200,
            'headers': _get_cors_headers(),
            'body': json.dumps(complaint_details, cls=DecimalEncoder)
        }
        
    except Exception as e:
        print(f"Error getting single complaint: {str(e)}")
        return {
            'statusCode': 500,
            'headers': _get_cors_headers(),
            'body': json.dumps({
                'success': False,
                'error': 'Failed to retrieve complaint',
                'message': str(e)
            })
        }

def get_all_complaints(table):
    """
    Get all complaints with statistics
    """
    try:
        # Query all complaints using GSI1 to get by status
        all_complaints = []
        
        # Get complaints by status using GSI1PK
        for status in ['IN-REVIEW', 'PROCESSED', 'OVERDUE']:
            try:
                response = table.query(
                    IndexName='GSI1',
                    KeyConditionExpression='GSI1PK = :status',
                    ExpressionAttributeValues={
                        ':status': f'STATUS#{status}'
                    }
                )
                all_complaints.extend(response.get('Items', []))
            except Exception as e:
                print(f"Error querying status {status}: {str(e)}")
        
        # If GSI query fails, fallback to scan
        if not all_complaints:
            response = table.scan(
                FilterExpression='begins_with(PK, :pk_prefix)',
                ExpressionAttributeValues={
                    ':pk_prefix': 'COMPLAINT#'
                }
            )
            all_complaints = response.get('Items', [])
        
        # Calculate statistics
        stats = _calculate_stats(all_complaints)
        
        # Group complaints by status
        case_status = _group_by_status(all_complaints)
        
        response_data = {
            'caseStats': stats,
            'caseStatus': case_status
        }
        
        return {
            'statusCode': 200,
            'headers': _get_cors_headers(),
            'body': json.dumps(response_data, cls=DecimalEncoder)
        }
        
    except Exception as e:
        print(f"Error getting all complaints: {str(e)}")
        return {
            'statusCode': 500,
            'headers': _get_cors_headers(),
            'body': json.dumps({
                'success': False,
                'error': 'Failed to retrieve complaints',
                'message': str(e)
            })
        }

def _calculate_stats(complaints):
    """
    Calculate complaint statistics
    """
    total = len(complaints)
    pending = len([c for c in complaints if c.get('status', '').upper() in ['PENDING', 'IN-REVIEW']])
    processed = len([c for c in complaints if c.get('status', '').upper() in ['PROCESSED', 'COMPLETED']])
    overdue = len([c for c in complaints if c.get('status', '').upper() == 'OVERDUE'])
    
    # Calculate cycle times (mock values for now)
    avg_cycle_time = 24
    best_time = 7
    longest_time = 72
    
    return {
        'total_complaints': total,
        'pending': pending,
        'processed': processed,
        'overdue': overdue,
        'avg_cycle_time': avg_cycle_time,
        'best_time': best_time,
        'longest_time': longest_time
    }

def _group_by_status(complaints):
    """
    Group complaints by status for response
    """
    status_groups = {
        'pending': [],
        'processed': [],
        'overdue': []
    }
    
    for complaint in complaints:
        status = complaint.get('status', '').lower()
        
        complaint_summary = {
            'case_id': complaint.get('case_id', complaint.get('complaint_id', '')),
            'criticality': complaint.get('criticality', 'NA'),
            'report_type': complaint.get('report_type', 'NA'),
            'receipt_date': complaint.get('receipt_date', complaint.get('created_at', '')),
            'case_type': complaint.get('case_type', [])
        }
        
        if status in ['pending', 'in-review']:
            status_groups['pending'].append(complaint_summary)
        elif status in ['processed', 'completed']:
            status_groups['processed'].append(complaint_summary)
        elif status == 'overdue':
            status_groups['overdue'].append(complaint_summary)
    
    return status_groups

def _get_cors_headers():
    """
    Return CORS headers for API Gateway
    """
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }

class DecimalEncoder(json.JSONEncoder):
    """
    JSON encoder for DynamoDB Decimal types
    """
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)
