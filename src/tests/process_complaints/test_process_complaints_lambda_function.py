import pytest
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'app'))
from process_complaints import lambda_function


class TestLambdaHandler:
    """Unit tests for the main lambda_handler function"""

    @patch('process_complaints.lambda_function.boto3.resource')
    def test_successful_single_message_processing(self, mock_boto3_resource):
        """Test: Successfully process single SQS message"""
        # Mock DynamoDB resource and table
        mock_table = Mock()
        mock_table.put_item.return_value = {}
        mock_dynamodb = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3_resource.return_value = mock_dynamodb

        event = {
            'Records': [
                {
                    'messageId': 'test-msg-123',
                    'receiptHandle': 'test-receipt',
                    'body': json.dumps({
                        'complaint_id': 'CAS-12345',
                        'narrative': 'Test complaint narrative',
                        'status': 'IN-REVIEW',
                        'created_at': '2024-10-30T12:00:00Z',
                        'created_by': 'test@example.com'
                    })
                }
            ]
        }

        context = Mock()
        context.request_id = 'test-request-123'

        result = lambda_function.lambda_handler(event, context)

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['processed'] == 1
        assert body['successful'] == 1
        assert body['failed'] == 0

        mock_table.put_item.assert_called_once()

    @patch('process_complaints.lambda_function.boto3.resource')
    def test_successful_multiple_messages_processing(self, mock_boto3_resource):
        """Test: Successfully process multiple SQS messages"""
        mock_table = Mock()
        mock_table.put_item.return_value = {}
        mock_dynamodb = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3_resource.return_value = mock_dynamodb

        event = {
            'Records': [
                {
                    'messageId': 'msg-1',
                    'body': json.dumps({
                        'complaint_id': 'CAS-001',
                        'narrative': 'First complaint',
                        'status': 'IN-REVIEW',
                        'created_at': '2024-10-30T12:00:00Z',
                        'created_by': 'user1@example.com'
                    })
                },
                {
                    'messageId': 'msg-2',
                    'body': json.dumps({
                        'complaint_id': 'CAS-002',
                        'narrative': 'Second complaint',
                        'status': 'IN-REVIEW',
                        'created_at': '2024-10-30T12:01:00Z',
                        'created_by': 'user2@example.com'
                    })
                }
            ]
        }

        context = Mock()
        result = lambda_function.lambda_handler(event, context)

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['successful'] == 2
        assert body['failed'] == 0
        assert mock_table.put_item.call_count == 2

    @patch('process_complaints.lambda_function.boto3.resource')
    def test_invalid_json_in_message(self, mock_boto3_resource):
        """Test: Handle invalid JSON in message body"""
        mock_table = Mock()
        mock_dynamodb = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3_resource.return_value = mock_dynamodb

        event = {
            'Records': [
                {
                    'messageId': 'msg-invalid-json',
                    'body': 'invalid-json{{{'
                }
            ]
        }

        context = Mock()
        result = lambda_function.lambda_handler(event, context)

        assert result['statusCode'] == 207
        body = json.loads(result['body'])
        assert body['failed'] == 1
        assert body['errors'][0]['error'] == 'InvalidJSON'
        mock_table.put_item.assert_not_called()

    @patch('process_complaints.lambda_function.boto3.resource')
    def test_missing_required_fields(self, mock_boto3_resource):
        """Test: Handle message with missing required fields"""
        mock_table = Mock()
        mock_dynamodb = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3_resource.return_value = mock_dynamodb

        event = {
            'Records': [
                {
                    'messageId': 'msg-missing-fields',
                    'body': json.dumps({
                        'complaint_id': 'CAS-123'
                        # Missing: narrative, status, created_at, created_by
                    })
                }
            ]
        }

        context = Mock()
        result = lambda_function.lambda_handler(event, context)

        assert result['statusCode'] == 207
        body = json.loads(result['body'])
        assert body['failed'] == 1
        assert body['errors'][0]['error'] == 'ValidationError'
        mock_table.put_item.assert_not_called()

    @patch('process_complaints.lambda_function.boto3.resource')
    def test_narrative_too_long(self, mock_boto3_resource):
        """Test: Handle narrative exceeding 420 characters"""
        mock_table = Mock()
        mock_dynamodb = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3_resource.return_value = mock_dynamodb

        event = {
            'Records': [
                {
                    'messageId': 'msg-long-narrative',
                    'body': json.dumps({
                        'complaint_id': 'CAS-456',
                        'narrative': 'a' * 421,
                        'status': 'IN-REVIEW',
                        'created_at': '2024-10-30T12:00:00Z',
                        'created_by': 'test@example.com'
                    })
                }
            ]
        }

        context = Mock()
        result = lambda_function.lambda_handler(event, context)

        assert result['statusCode'] == 207
        body = json.loads(result['body'])
        assert body['failed'] == 1
        mock_table.put_item.assert_not_called()

    @patch('process_complaints.lambda_function.boto3.resource')
    def test_dynamodb_error(self, mock_boto3_resource):
        """Test: Handle DynamoDB error"""
        mock_table = Mock()
        mock_table.put_item.side_effect = Exception("DynamoDB connection error")
        mock_dynamodb = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3_resource.return_value = mock_dynamodb

        event = {
            'Records': [
                {
                    'messageId': 'msg-db-error',
                    'body': json.dumps({
                        'complaint_id': 'CAS-789',
                        'narrative': 'Test complaint',
                        'status': 'IN-REVIEW',
                        'created_at': '2024-10-30T12:00:00Z',
                        'created_by': 'test@example.com'
                    })
                }
            ]
        }

        context = Mock()
        result = lambda_function.lambda_handler(event, context)

        assert result['statusCode'] == 207
        body = json.loads(result['body'])
        assert body['failed'] == 1
        assert body['errors'][0]['error'] == 'ProcessingError'

    @patch('process_complaints.lambda_function.boto3.resource')
    def test_partial_batch_failure(self, mock_boto3_resource):
        """Test: Handle partial batch failure"""
        mock_table = Mock()
        mock_table.put_item.side_effect = [
            {},  # Success
            Exception("Database error")  # Failure
        ]
        mock_dynamodb = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3_resource.return_value = mock_dynamodb

        event = {
            'Records': [
                {
                    'messageId': 'msg-success',
                    'body': json.dumps({
                        'complaint_id': 'CAS-SUCCESS',
                        'narrative': 'This will succeed',
                        'status': 'IN-REVIEW',
                        'created_at': '2024-10-30T12:00:00Z',
                        'created_by': 'user@example.com'
                    })
                },
                {
                    'messageId': 'msg-failure',
                    'body': json.dumps({
                        'complaint_id': 'CAS-FAIL',
                        'narrative': 'This will fail',
                        'status': 'IN-REVIEW',
                        'created_at': '2024-10-30T12:01:00Z',
                        'created_by': 'user@example.com'
                    })
                }
            ]
        }

        context = Mock()
        result = lambda_function.lambda_handler(event, context)

        assert result['statusCode'] == 207
        body = json.loads(result['body'])
        assert body['successful'] == 1
        assert body['failed'] == 1

    @patch('process_complaints.lambda_function.boto3.resource')
    def test_empty_records(self, mock_boto3_resource):
        """Test: Handle event with no records"""
        mock_table = Mock()
        mock_dynamodb = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3_resource.return_value = mock_dynamodb

        event = {'Records': []}
        context = Mock()

        result = lambda_function.lambda_handler(event, context)

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['processed'] == 0
        mock_table.put_item.assert_not_called()


class TestValidateComplaint:
    """Tests for validate_complaint function"""

    def test_valid_complaint(self):
        """Test: Valid complaint passes validation"""
        complaint = {
            'complaint_id': 'CAS-12345',
            'narrative': 'Valid complaint narrative',
            'status': 'IN-REVIEW',
            'created_at': '2024-10-30T12:00:00Z',
            'created_by': 'test@example.com'
        }

        lambda_function.validate_complaint(complaint)

    def test_missing_complaint_id(self):
        """Test: Missing complaint_id raises ValueError"""
        complaint = {
            'narrative': 'Test',
            'status': 'IN-REVIEW',
            'created_at': '2024-10-30T12:00:00Z',
            'created_by': 'test@example.com'
        }

        with pytest.raises(ValueError) as exc_info:
            lambda_function.validate_complaint(complaint)
        assert 'complaint_id' in str(exc_info.value)

    def test_empty_narrative(self):
        """Test: Empty narrative raises ValueError"""
        complaint = {
            'complaint_id': 'CAS-12345',
            'narrative': '',
            'status': 'IN-REVIEW',
            'created_at': '2024-10-30T12:00:00Z',
            'created_by': 'test@example.com'
        }

        with pytest.raises(ValueError) as exc_info:
            lambda_function.validate_complaint(complaint)
        assert 'narrative' in str(exc_info.value)

    def test_narrative_too_long(self):
        """Test: Narrative over 420 characters raises ValueError"""
        complaint = {
            'complaint_id': 'CAS-12345',
            'narrative': 'a' * 421,
            'status': 'IN-REVIEW',
            'created_at': '2024-10-30T12:00:00Z',
            'created_by': 'test@example.com'
        }

        with pytest.raises(ValueError) as exc_info:
            lambda_function.validate_complaint(complaint)
        assert '420' in str(exc_info.value)


class TestConvertFloatsToDecimal:
    """Tests for _convert_floats_to_decimal function"""

    def test_convert_float(self):
        """Test: Convert float to Decimal"""
        from decimal import Decimal

        result = lambda_function._convert_floats_to_decimal(3.14)
        assert isinstance(result, Decimal)
        assert result == Decimal('3.14')

    def test_convert_dict_with_floats(self):
        """Test: Convert floats in dictionary"""
        from decimal import Decimal

        data = {
            'name': 'Test',
            'value': 3.14,
            'count': 5,
            'nested': {
                'price': 9.99
            }
        }

        result = lambda_function._convert_floats_to_decimal(data)

        assert isinstance(result['value'], Decimal)
        assert isinstance(result['nested']['price'], Decimal)
        assert isinstance(result['count'], int)

    def test_convert_list_with_floats(self):
        """Test: Convert floats in list"""
        from decimal import Decimal

        data = [1.5, 2.5, 3, 'text']
        result = lambda_function._convert_floats_to_decimal(data)

        assert isinstance(result[0], Decimal)
        assert isinstance(result[1], Decimal)
        assert isinstance(result[2], int)


class TestSaveToDynamoDB:
    """Tests for save_to_dynamodb function"""

    def test_successful_save(self):
        """Test: Successfully save complaint to DynamoDB with Single Table Design"""
        mock_table = Mock()
        mock_table.put_item.return_value = {}

        complaint = {
            'complaint_id': 'CAS-12345',
            'narrative': 'Test complaint',
            'status': 'IN-REVIEW',
            'created_at': '2024-10-30T12:00:00Z',
            'created_by': 'test@example.com'
        }

        lambda_function.save_to_dynamodb(mock_table, complaint)

        mock_table.put_item.assert_called_once()
        call_args = mock_table.put_item.call_args
        item = call_args[1]['Item']

        # Verify original fields
        assert item['complaint_id'] == 'CAS-12345'

        # Verify Single Table Design keys
        assert item['PK'] == 'COMPLAINT#CAS-12345'
        assert item['SK'] == 'METADATA'
        assert item['GSI1PK'] == 'STATUS#IN-REVIEW'
        assert item['GSI1SK'] == 'CREATED#2024-10-30T12:00:00Z'

        # Verify metadata
        assert 'processed_at' in item
        assert 'table_version' in item
        assert item['table_version'] == '1.0'

        # Verify narrative field
        assert item['narrative'] == 'Test complaint'

    def test_save_with_floats(self):
        """Test: Floats are converted to Decimal before saving"""
        from decimal import Decimal

        mock_table = Mock()
        mock_table.put_item.return_value = {}

        complaint = {
            'complaint_id': 'CAS-12345',
            'narrative': 'Test',
            'status': 'IN-REVIEW',
            'created_at': '2024-10-30T12:00:00Z',
            'created_by': 'test@example.com',
            'score': 3.14
        }

        lambda_function.save_to_dynamodb(mock_table, complaint)

        call_args = mock_table.put_item.call_args
        item = call_args[1]['Item']
        assert isinstance(item['score'], Decimal)

    def test_save_dynamodb_error(self):
        """Test: DynamoDB error is raised"""
        mock_table = Mock()
        mock_table.put_item.side_effect = Exception("Connection error")

        complaint = {
            'complaint_id': 'CAS-12345',
            'narrative': 'Test',
            'status': 'IN-REVIEW',
            'created_at': '2024-10-30T12:00:00Z',
            'created_by': 'test@example.com'
        }

        with pytest.raises(Exception) as exc_info:
            lambda_function.save_to_dynamodb(mock_table, complaint)
        assert 'Connection error' in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
