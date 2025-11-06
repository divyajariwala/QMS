import pytest
import json
import os
import sys
from unittest.mock import Mock, patch
from decimal import Decimal

# Add src directory to path for importing lambda_function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'app', 'approve_complaints'))
import lambda_function


class TestLambdaHandler:
    """Unit tests for the main lambda_handler function"""

    @patch.dict(os.environ, {'DYNAMODB_TABLE_NAME': 'test-table'})
    @patch('boto3.resource')
    def test_approve_complaint_success(self, mock_boto3):
        """Test: Successful complaint approval"""
        mock_table = Mock()
        mock_dynamodb = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3.return_value = mock_dynamodb

        # Mock existing complaint
        mock_table.get_item.return_value = {
            'Item': {
                'PK': 'COMPLAINT#RGL23-000070',
                'SK': 'METADATA',
                'case_id': 'RGL23-000070',
                'caseStatus': 'pending',
                'narrative': 'Original narrative'
            }
        }

        event = {
            'body': json.dumps({
                'case_id': 'RGL23-000070',
                'caseStatus': 'pending',
                'narrative': 'Updated narrative',
                'criticality': 'High'
            })
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
        assert body['data']['caseStatus'] == 'processed'
        assert body['data']['case_id'] == 'RGL23-000070'
        mock_table.put_item.assert_called_once()

    @patch.dict(os.environ, {'DYNAMODB_TABLE_NAME': 'test-table'})
    @patch('boto3.resource')
    def test_missing_case_id(self, mock_boto3):
        """Test: Missing case_id in request"""
        event = {
            'body': json.dumps({
                'narrative': 'Test narrative'
            })
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert body['success'] is False
        assert body['error'] == 'case_id is required'

    @patch.dict(os.environ, {'DYNAMODB_TABLE_NAME': 'test-table'})
    @patch('boto3.resource')
    def test_invalid_status(self, mock_boto3):
        """Test: Invalid caseStatus (not pending)"""
        event = {
            'body': json.dumps({
                'case_id': 'RGL23-000070',
                'caseStatus': 'processed'
            })
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert body['success'] is False
        assert 'Can only approve complaints with pending status' in body['error']

    @patch.dict(os.environ, {'DYNAMODB_TABLE_NAME': 'test-table'})
    @patch('boto3.resource')
    def test_complaint_not_found(self, mock_boto3):
        """Test: Complaint not found in database"""
        mock_table = Mock()
        mock_dynamodb = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3.return_value = mock_dynamodb

        mock_table.get_item.return_value = {}

        event = {
            'body': json.dumps({
                'case_id': 'NONEXISTENT',
                'caseStatus': 'pending'
            })
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 404
        body = json.loads(result['body'])
        assert body['success'] is False
        assert 'not found' in body['error']

    @patch.dict(os.environ, {'DYNAMODB_TABLE_NAME': 'test-table'})
    @patch('boto3.resource')
    def test_database_error_on_get(self, mock_boto3):
        """Test: Database error during get_item"""
        mock_table = Mock()
        mock_dynamodb = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3.return_value = mock_dynamodb

        mock_table.get_item.side_effect = Exception("DynamoDB error")

        event = {
            'body': json.dumps({
                'case_id': 'RGL23-000070',
                'caseStatus': 'pending'
            })
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert body['success'] is False
        assert 'Error retrieving complaint' in body['error']

    @patch.dict(os.environ, {'DYNAMODB_TABLE_NAME': 'test-table'})
    @patch('boto3.resource')
    def test_database_error_on_put(self, mock_boto3):
        """Test: Database error during put_item"""
        mock_table = Mock()
        mock_dynamodb = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3.return_value = mock_dynamodb

        mock_table.get_item.return_value = {
            'Item': {
                'PK': 'COMPLAINT#RGL23-000070',
                'SK': 'METADATA',
                'case_id': 'RGL23-000070',
                'caseStatus': 'pending'
            }
        }
        mock_table.put_item.side_effect = Exception("Put failed")

        event = {
            'body': json.dumps({
                'case_id': 'RGL23-000070',
                'caseStatus': 'pending'
            })
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert body['success'] is False
        assert 'Error updating complaint' in body['error']

    def test_invalid_json(self):
        """Test: Invalid JSON in request body"""
        event = {
            'body': 'invalid json'
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert body['success'] is False
        assert 'Invalid JSON format' in body['error']

    @patch.dict(os.environ, {'DYNAMODB_TABLE_NAME': 'test-table'})
    @patch('boto3.resource')
    def test_complete_complaint_data(self, mock_boto3):
        """Test: Complete complaint data update"""
        mock_table = Mock()
        mock_dynamodb = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3.return_value = mock_dynamodb

        mock_table.get_item.return_value = {
            'Item': {
                'PK': 'COMPLAINT#RGL23-000070',
                'SK': 'METADATA',
                'case_id': 'RGL23-000070',
                'caseStatus': 'pending',
                'existing_field': 'should_be_preserved'
            }
        }

        complete_data = {
            'case_id': 'RGL23-000070',
            'receipt_date': '08/Jan/2023',
            'criticality': 'Major',
            'report_type': 'Spontaneous',
            'ai_summary': 'AI summary text',
            'case_type': ['AE', 'PC'],
            'narrative': 'Complete narrative',
            'primary_reporter': {'name': 'John Doe'},
            'patient_name': 'Patient Name',
            'physician_name': 'Dr. Smith',
            'product_details': {'drug_name': 'TestDrug'},
            'category_details': [{'id': '1', 'label': 'Test'}],
            'caseStatus': 'pending'
        }

        event = {
            'body': json.dumps(complete_data),
            'requestContext': {
                'authorizer': {
                    'claims': {'email': 'test@example.com'}
                }
            }
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
        assert body['data']['caseStatus'] == 'processed'
        assert body['data']['approved_by'] == 'test@example.com'

    @patch.dict(os.environ, {'DYNAMODB_TABLE_NAME': 'test-table'})
    @patch('boto3.resource')
    def test_dict_body_format(self, mock_boto3):
        """Test: Request body as dict (not string)"""
        mock_table = Mock()
        mock_dynamodb = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3.return_value = mock_dynamodb

        mock_table.get_item.return_value = {
            'Item': {
                'PK': 'COMPLAINT#RGL23-000070',
                'SK': 'METADATA',
                'case_id': 'RGL23-000070',
                'caseStatus': 'pending'
            }
        }

        event = {
            'body': {
                'case_id': 'RGL23-000070',
                'caseStatus': 'pending'
            }
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True


class TestUtilityFunctions:
    """Tests for utility functions"""

    def test_get_user_from_event_cognito(self):
        """Test: Extract user from Cognito claims"""
        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'email': 'user@example.com',
                        'sub': 'user-123'
                    }
                }
            }
        }

        user = lambda_function._get_user_from_event(event)
        assert user == 'user@example.com'

    def test_get_user_from_event_headers(self):
        """Test: Extract user from headers"""
        event = {
            'headers': {
                'x-user-email': 'header@example.com'
            }
        }

        user = lambda_function._get_user_from_event(event)
        assert user == 'header@example.com'

    def test_get_user_from_event_fallback(self):
        """Test: Fallback to system when no user info"""
        event = {}

        user = lambda_function._get_user_from_event(event)
        assert user == 'system'

    def test_error_response(self):
        """Test: Error response format"""
        response = lambda_function._error_response(400, "Test error")

        assert response['statusCode'] == 400
        assert response['headers']['Content-Type'] == 'application/json'
        body = json.loads(response['body'])
        assert body['success'] is False
        assert body['error'] == 'Test error'
        assert 'timestamp' in body

    def test_get_cors_headers(self):
        """Test: CORS headers"""
        headers = lambda_function._get_cors_headers()

        assert headers['Content-Type'] == 'application/json'
        assert headers['Access-Control-Allow-Origin'] == '*'
        assert headers['Access-Control-Allow-Methods'] == 'POST, OPTIONS'
        assert 'Authorization' in headers['Access-Control-Allow-Headers']


class TestDecimalEncoder:
    """Tests for DecimalEncoder class"""

    def test_decimal_encoder_with_decimal(self):
        """Test: Decimal encoder with Decimal values"""
        test_data = {
            'score': Decimal('95.5'),
            'confidence': Decimal('0.85')
        }

        result = json.dumps(test_data, cls=lambda_function.DecimalEncoder)
        parsed = json.loads(result)

        assert parsed['score'] == 95.5
        assert parsed['confidence'] == 0.85

    def test_decimal_encoder_without_decimal(self):
        """Test: Decimal encoder with regular values"""
        test_data = {
            'number': 42,
            'text': 'hello'
        }

        result = json.dumps(test_data, cls=lambda_function.DecimalEncoder)
        parsed = json.loads(result)

        assert parsed == test_data


class TestEdgeCases:
    """Tests for edge cases"""

    @patch.dict(os.environ, {'DYNAMODB_TABLE_NAME': 'test-table'})
    @patch('boto3.resource')
    def test_empty_case_id(self, mock_boto3):
        """Test: Empty case_id"""
        event = {
            'body': json.dumps({
                'case_id': '',
                'caseStatus': 'pending'
            })
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert body['error'] == 'case_id is required'

    @patch.dict(os.environ, {'DYNAMODB_TABLE_NAME': 'test-table'})
    @patch('boto3.resource')
    def test_case_insensitive_status(self, mock_boto3):
        """Test: Case insensitive status check - PENDING should work"""
        mock_table = Mock()
        mock_dynamodb = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3.return_value = mock_dynamodb

        mock_table.get_item.return_value = {
            'Item': {
                'PK': 'COMPLAINT#RGL23-000070',
                'SK': 'METADATA',
                'case_id': 'RGL23-000070',
                'caseStatus': 'pending'
            }
        }

        event = {
            'body': json.dumps({
                'case_id': 'RGL23-000070',
                'caseStatus': 'PENDING'  # Should work as it converts to lowercase
            })
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True

    @patch('boto3.resource')
    def test_boto3_connection_error(self, mock_boto3):
        """Test: Boto3 connection error"""
        mock_boto3.side_effect = Exception("AWS connection failed")

        event = {
            'body': json.dumps({
                'case_id': 'RGL23-000070',
                'caseStatus': 'pending'
            })
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert body['success'] is False
        assert 'Internal server error' in body['error']


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=approve_complaints.lambda_function", "--cov-report=term-missing"])