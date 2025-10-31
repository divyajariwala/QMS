import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('qms-dev-complaints-metadata')

def lambda_handler(event, context):
    """
    Lambda function handler to retrieve complaints data from DynamoDB.
    
    Args:
        event (dict): Lambda event object
        context (object): Lambda context object
        
    Returns:
        dict: API Gateway response with complaints data
    """
    def get_single_complaint(case_id):
        response = table.get_item(Key={'caseId': case_id})
        if 'Item' in response:
            return {
                'statusCode': 200,
                'body': json.dumps(response['Item'])
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'success': False, 'error': 'Complaint not found'})
            }

    def get_all_complaints():
        response = table.scan()
        items = response.get('Items', [])
        return {
            'statusCode': 200,
            'body': json.dumps(items)
        }
    
    path_parameters = event.get('pathParameters', {})

    if path_parameters and 'caseId' in path_parameters:
        # Handle single complaint request
        case_id = path_parameters['caseId']
        return get_single_complaint(case_id)
    else:
        # Handle all complaints request
        return get_all_complaints()
