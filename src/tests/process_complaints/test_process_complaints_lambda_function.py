import json
import pytest
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock, call
from moto import mock_aws
import boto3

# Import the lambda function
from process_complaints import lambda_function as process_complaint_lambda


@pytest.fixture
def sample_complaint():
    """Sample complaint data for testing."""
    return {
        'complaint_id': '01JBQR3K7HXGM4P9N5T8WZVF2Y',
        'narrative': 'Test complaint narrative',
        'status': 'pending',
        'created_at': '2024-11-05T10:00:00Z',
        'created_by': 'test@example.com'
    }


@pytest.fixture
def sqs_event(sample_complaint):
    """Sample SQS event for testing."""
    return {
        'Records': [
            {
                'messageId': '059f36b4-87a3-44ab-83d2-661975830a7d',
                'receiptHandle': 'AQEBwJnKyr...',
                'body': json.dumps(sample_complaint),
                'attributes': {
                    'ApproximateReceiveCount': '1',
                    'SentTimestamp': '1698765432000'
                }
            }
        ]
    }


class TestValidateComplaint:
    """Tests for validate_complaint function."""

    def test_valid_complaint(self, sample_complaint):
        """Test validation with valid complaint."""
        # Should not raise any exception
        process_complaint_lambda.validate_complaint(sample_complaint)

    def test_missing_required_field(self, sample_complaint):
        """Test validation fails when required field is missing."""
        del sample_complaint['narrative']

        with pytest.raises(ValueError) as exc_info:
            process_complaint_lambda.validate_complaint(sample_complaint)

        assert 'Missing required fields: narrative' in str(exc_info.value)

    def test_empty_complaint_id(self, sample_complaint):
        """Test validation fails when complaint_id is empty."""
        sample_complaint['complaint_id'] = '   '

        with pytest.raises(ValueError) as exc_info:
            process_complaint_lambda.validate_complaint(sample_complaint)

        assert 'complaint_id cannot be empty' in str(exc_info.value)

    def test_empty_narrative(self, sample_complaint):
        """Test validation fails when narrative is empty."""
        sample_complaint['narrative'] = '   '

        with pytest.raises(ValueError) as exc_info:
            process_complaint_lambda.validate_complaint(sample_complaint)

        assert 'narrative cannot be empty' in str(exc_info.value)

    def test_narrative_too_long(self, sample_complaint):
        """Test validation fails when narrative exceeds max length."""
        sample_complaint['narrative'] = 'x' * 421

        with pytest.raises(ValueError) as exc_info:
            process_complaint_lambda.validate_complaint(sample_complaint)

        assert 'narrative exceeds maximum length' in str(exc_info.value)


class TestSaveToDynamoDB:
    """Tests for save_to_dynamodb function."""

    def test_successful_save(self, sample_complaint):
        """Test successful save to DynamoDB."""
        # Mock table
        mock_table = Mock()
        mock_table.put_item = Mock()

        # Save to DynamoDB
        process_complaint_lambda.save_to_dynamodb(mock_table, sample_complaint)

        # Verify put_item was called
        assert mock_table.put_item.called
        call_args = mock_table.put_item.call_args
        item = call_args[1]['Item']

        # Verify Single Table Design keys
        assert item['PK'] == f"COMPLAINT#{sample_complaint['complaint_id']}"
        assert item['SK'] == 'METADATA'
        assert item['GSI1PK'] == f"STATUS#{sample_complaint['status']}"
        assert 'GSI1SK' in item
        assert item['complaint_id'] == sample_complaint['complaint_id']
        assert item['narrative'] == sample_complaint['narrative']
        assert 'processed_at' in item
        assert item['table_version'] == '1.0'

    def test_save_with_floats(self, sample_complaint):
        """Test save converts floats to Decimal."""
        sample_complaint['score'] = 3.14
        sample_complaint['nested'] = {'value': 2.71}

        # Mock table
        mock_table = Mock()

        # Save to DynamoDB
        process_complaint_lambda.save_to_dynamodb(mock_table, sample_complaint)

        # Verify floats were converted to Decimal
        call_args = mock_table.put_item.call_args
        item = call_args[1]['Item']
        assert isinstance(item['score'], Decimal)
        assert isinstance(item['nested']['value'], Decimal)

    def test_save_with_default_source(self, sample_complaint):
        """Test save adds default source if not present."""
        # Mock table
        mock_table = Mock()

        # Save to DynamoDB
        process_complaint_lambda.save_to_dynamodb(mock_table, sample_complaint)

        # Verify default source was added
        call_args = mock_table.put_item.call_args
        item = call_args[1]['Item']
        assert item['source'] == 'api'

    def test_save_error_handling(self, sample_complaint):
        """Test error handling when save fails."""
        # Mock table that raises exception
        mock_table = Mock()
        mock_table.put_item.side_effect = Exception('DynamoDB error')

        # Verify exception is raised
        with pytest.raises(Exception) as exc_info:
            process_complaint_lambda.save_to_dynamodb(mock_table, sample_complaint)

        assert 'DynamoDB error' in str(exc_info.value)


class TestSendToClassifyQueue:
    """Tests for send_to_classify_queue function."""

    def test_successful_send(self, sample_complaint):
        """Test successful send to classify queue."""
        # Mock SQS client
        mock_sqs_client = Mock()
        mock_sqs_client.get_queue_url.return_value = {
            'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789012/qms-dev-classify-complaints'
        }
        mock_sqs_client.send_message.return_value = {
            'MessageId': 'test-message-id-123'
        }

        # Send to queue
        process_complaint_lambda.send_to_classify_queue(mock_sqs_client, sample_complaint)

        # Verify get_queue_url was called
        mock_sqs_client.get_queue_url.assert_called_once_with(
            QueueName='qms-dev-classify-complaints'
        )

        # Verify send_message was called with correct parameters
        mock_sqs_client.send_message.assert_called_once()
        call_args = mock_sqs_client.send_message.call_args

        assert call_args[1][
                   'QueueUrl'] == 'https://sqs.us-east-1.amazonaws.com/123456789012/qms-dev-classify-complaints'

        # Verify message body
        message_body = json.loads(call_args[1]['MessageBody'])
        assert message_body['complaint_id'] == sample_complaint['complaint_id']
        assert message_body['narrative'] == sample_complaint['narrative']
        assert len(message_body) == 2  # Only complaint_id and narrative

        # Verify message attributes
        message_attrs = call_args[1]['MessageAttributes']
        assert message_attrs['complaint_id']['StringValue'] == sample_complaint['complaint_id']
        assert message_attrs['complaint_id']['DataType'] == 'String'

    def test_send_failure(self, sample_complaint):
        """Test error handling when send fails."""
        # Mock SQS client that raises exception
        mock_sqs_client = Mock()
        mock_sqs_client.get_queue_url.side_effect = Exception('Queue not found')

        with pytest.raises(Exception) as exc_info:
            process_complaint_lambda.send_to_classify_queue(mock_sqs_client, sample_complaint)

        assert 'Queue not found' in str(exc_info.value)


class TestLambdaHandler:
    """Tests for lambda_handler function."""

    @patch('process_complaints.lambda_function.boto3')
    def test_successful_processing(self, mock_boto3, sqs_event):
        """Test successful processing of SQS message."""
        # Mock DynamoDB
        mock_dynamodb = Mock()
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table

        # Mock SQS
        mock_sqs_client = Mock()
        mock_sqs_client.get_queue_url.return_value = {
            'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123/qms-dev-classify-complaints'
        }
        mock_sqs_client.send_message.return_value = {
            'MessageId': 'test-message-id'
        }

        # Setup boto3 mock
        mock_boto3.resource.return_value = mock_dynamodb
        mock_boto3.client.return_value = mock_sqs_client

        # Process event
        response = process_complaint_lambda.lambda_handler(sqs_event, None)

        # Verify response
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['successful'] == 1
        assert body['failed'] == 0
        assert body['processed'] == 1

        # Verify DynamoDB was called
        assert mock_table.put_item.called

        # Verify SQS was called
        assert mock_sqs_client.get_queue_url.called
        assert mock_sqs_client.send_message.called

    @patch('process_complaints.lambda_function.boto3')
    def test_invalid_json(self, mock_boto3):
        """Test handling of invalid JSON in message."""
        # Mock clients
        mock_dynamodb = Mock()
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_sqs_client = Mock()

        mock_boto3.resource.return_value = mock_dynamodb
        mock_boto3.client.return_value = mock_sqs_client

        # Create event with invalid JSON
        event = {
            'Records': [
                {
                    'messageId': 'test-message-id',
                    'body': 'invalid json{'
                }
            ]
        }

        response = process_complaint_lambda.lambda_handler(event, None)

        assert response['statusCode'] == 207
        body = json.loads(response['body'])
        assert body['successful'] == 0
        assert body['failed'] == 1
        assert body['errors'][0]['error'] == 'InvalidJSON'

    @patch('process_complaints.lambda_function.boto3')
    def test_validation_error(self, mock_boto3):
        """Test handling of validation errors."""
        # Mock clients
        mock_dynamodb = Mock()
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_sqs_client = Mock()

        mock_boto3.resource.return_value = mock_dynamodb
        mock_boto3.client.return_value = mock_sqs_client

        # Create event with invalid complaint
        invalid_complaint = {'complaint_id': '123'}  # Missing required fields
        event = {
            'Records': [
                {
                    'messageId': 'test-message-id',
                    'body': json.dumps(invalid_complaint)
                }
            ]
        }

        response = process_complaint_lambda.lambda_handler(event, None)

        assert response['statusCode'] == 207
        body = json.loads(response['body'])
        assert body['successful'] == 0
        assert body['failed'] == 1
        assert body['errors'][0]['error'] == 'ValidationError'

    @patch('process_complaints.lambda_function.boto3')
    def test_dynamodb_error(self, mock_boto3, sample_complaint):
        """Test handling of DynamoDB errors."""
        # Mock DynamoDB that raises exception
        mock_dynamodb = Mock()
        mock_table = Mock()
        mock_table.put_item.side_effect = Exception('DynamoDB connection error')
        mock_dynamodb.Table.return_value = mock_table

        # Mock SQS
        mock_sqs_client = Mock()

        mock_boto3.resource.return_value = mock_dynamodb
        mock_boto3.client.return_value = mock_sqs_client

        # Create event
        event = {
            'Records': [
                {
                    'messageId': 'test-message-id',
                    'body': json.dumps(sample_complaint)
                }
            ]
        }

        response = process_complaint_lambda.lambda_handler(event, None)

        assert response['statusCode'] == 207
        body = json.loads(response['body'])
        assert body['successful'] == 0
        assert body['failed'] == 1
        assert body['errors'][0]['error'] == 'ProcessingError'

    @patch('process_complaints.lambda_function.boto3')
    def test_sqs_send_error(self, mock_boto3, sample_complaint):
        """Test handling of SQS send errors."""
        # Mock DynamoDB
        mock_dynamodb = Mock()
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table

        # Mock SQS that raises exception
        mock_sqs_client = Mock()
        mock_sqs_client.get_queue_url.side_effect = Exception('Queue not found')

        mock_boto3.resource.return_value = mock_dynamodb
        mock_boto3.client.return_value = mock_sqs_client

        # Create event
        event = {
            'Records': [
                {
                    'messageId': 'test-message-id',
                    'body': json.dumps(sample_complaint)
                }
            ]
        }

        response = process_complaint_lambda.lambda_handler(event, None)

        assert response['statusCode'] == 207
        body = json.loads(response['body'])
        assert body['successful'] == 0
        assert body['failed'] == 1
        assert body['errors'][0]['error'] == 'ProcessingError'

    @patch('process_complaints.lambda_function.boto3')
    def test_multiple_messages(self, mock_boto3, sample_complaint):
        """Test processing multiple messages."""
        # Mock DynamoDB
        mock_dynamodb = Mock()
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table

        # Mock SQS
        mock_sqs_client = Mock()
        mock_sqs_client.get_queue_url.return_value = {
            'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123/qms-dev-classify-complaints'
        }
        mock_sqs_client.send_message.return_value = {
            'MessageId': 'test-message-id'
        }

        mock_boto3.resource.return_value = mock_dynamodb
        mock_boto3.client.return_value = mock_sqs_client

        # Create event with multiple records
        event = {
            'Records': [
                {
                    'messageId': f'message-{i}',
                    'body': json.dumps({**sample_complaint, 'complaint_id': f'ID-{i}'})
                }
                for i in range(3)
            ]
        }

        response = process_complaint_lambda.lambda_handler(event, None)

        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['successful'] == 3
        assert body['failed'] == 0
        assert body['processed'] == 3

        # Verify DynamoDB was called 3 times
        assert mock_table.put_item.call_count == 3

        # Verify SQS was called 3 times
        assert mock_sqs_client.send_message.call_count == 3

    @patch('process_complaints.lambda_function.boto3')
    def test_partial_batch_failure(self, mock_boto3, sample_complaint):
        """Test processing when some messages succeed and some fail."""
        # Mock DynamoDB
        mock_dynamodb = Mock()
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table

        # Mock SQS
        mock_sqs_client = Mock()
        mock_sqs_client.get_queue_url.return_value = {
            'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123/qms-dev-classify-complaints'
        }
        mock_sqs_client.send_message.return_value = {
            'MessageId': 'test-message-id'
        }

        mock_boto3.resource.return_value = mock_dynamodb
        mock_boto3.client.return_value = mock_sqs_client

        # Create event with valid and invalid messages
        event = {
            'Records': [
                {
                    'messageId': 'message-1',
                    'body': json.dumps(sample_complaint)
                },
                {
                    'messageId': 'message-2',
                    'body': 'invalid json'
                },
                {
                    'messageId': 'message-3',
                    'body': json.dumps({**sample_complaint, 'complaint_id': 'ID-3'})
                }
            ]
        }

        response = process_complaint_lambda.lambda_handler(event, None)

        assert response['statusCode'] == 207  # Partial success
        body = json.loads(response['body'])
        assert body['successful'] == 2
        assert body['failed'] == 1
        assert body['processed'] == 3
        assert len(body['errors']) == 1
        assert body['errors'][0]['messageId'] == 'message-2'


class TestConvertFloatsToDecimal:
    """Tests for _convert_floats_to_decimal function."""

    def test_convert_float(self):
        """Test conversion of float to Decimal."""
        result = process_complaint_lambda._convert_floats_to_decimal(3.14)
        assert isinstance(result, Decimal)
        assert result == Decimal('3.14')

    def test_convert_dict_with_floats(self):
        """Test conversion of dict containing floats."""
        data = {
            'score': 3.14,
            'name': 'test',
            'count': 5
        }
        result = process_complaint_lambda._convert_floats_to_decimal(data)

        assert isinstance(result['score'], Decimal)
        assert isinstance(result['name'], str)
        assert isinstance(result['count'], int)

    def test_convert_list_with_floats(self):
        """Test conversion of list containing floats."""
        data = [1.5, 2.7, 'text', 42]
        result = process_complaint_lambda._convert_floats_to_decimal(data)

        assert isinstance(result[0], Decimal)
        assert isinstance(result[1], Decimal)
        assert isinstance(result[2], str)
        assert isinstance(result[3], int)

    def test_convert_nested_structure(self):
        """Test conversion of nested structures."""
        data = {
            'scores': [1.5, 2.7],
            'metadata': {
                'average': 3.14,
                'items': [
                    {'value': 1.1},
                    {'value': 2.2}
                ]
            }
        }
        result = process_complaint_lambda._convert_floats_to_decimal(data)

        assert all(isinstance(x, Decimal) for x in result['scores'])
        assert isinstance(result['metadata']['average'], Decimal)
        assert all(isinstance(item['value'], Decimal) for item in result['metadata']['items'])


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
