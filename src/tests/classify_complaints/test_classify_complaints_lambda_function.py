import json
import pytest
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock
import boto3

# Import the lambda function
from classify_complaints import lambda_function as classify_complaint_lambda


@pytest.fixture
def sample_complaint():
    """Sample complaint data for testing."""
    return {
        'complaint_id': '01JBQR3K7HXGM4P9N5T8WZVF2Y',
        'narrative': 'Test complaint narrative for classification'
    }


@pytest.fixture
def sample_complaint_full():
    """Sample complaint with full data."""
    return {
        'complaint_id': '01JBQR3K7HXGM4P9N5T8WZVF2Y',
        'code': 'CAS-20241105112345',
        'narrative': 'Test complaint narrative for classification',
        'status': 'IN-REVIEW',
        'created_at': '2024-11-05T10:00:00Z',
        'created_by': 'test@example.com',
        'source': 'api'
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


@pytest.fixture
def mock_context():
    """Mock Lambda context."""
    context = Mock()
    context.invoked_function_arn = 'arn:aws:lambda:us-east-1:123456789012:function:qms-dev-classify-complaints'
    context.function_name = 'qms-dev-classify-complaints'
    context.memory_limit_in_mb = 512
    context.request_id = 'test-request-id'
    return context


class TestBuildStepFunctionArn:
    """Tests for build_step_function_arn function."""

    def test_build_arn_from_context(self, mock_context):
        """Test building Step Function ARN from Lambda context."""
        arn = classify_complaint_lambda.build_step_function_arn(mock_context)

        assert arn == 'arn:aws:states:us-east-1:123456789012:stateMachine:qms-dev-complaints'
        assert 'stateMachine' in arn
        assert '123456789012' in arn

    def test_build_arn_with_custom_env(self, mock_context, monkeypatch):
        """Test building ARN with custom environment."""
        monkeypatch.setenv('env', 'prod')

        # Reload module to pick up new env var
        import importlib
        importlib.reload(classify_complaint_lambda)

        arn = classify_complaint_lambda.build_step_function_arn(mock_context)

        assert 'qms-prod-complaints' in arn


class TestValidateComplaint:
    """Tests for validate_complaint function."""

    def test_valid_complaint_minimal(self, sample_complaint):
        """Test validation with minimal valid complaint."""
        # Should not raise any exception
        classify_complaint_lambda.validate_complaint(sample_complaint)

    def test_valid_complaint_full(self, sample_complaint_full):
        """Test validation with full complaint data."""
        # Should not raise any exception
        classify_complaint_lambda.validate_complaint(sample_complaint_full)

    def test_missing_complaint_id(self, sample_complaint):
        """Test validation fails when complaint_id is missing."""
        del sample_complaint['complaint_id']

        with pytest.raises(ValueError) as exc_info:
            classify_complaint_lambda.validate_complaint(sample_complaint)

        assert 'Missing required fields: complaint_id' in str(exc_info.value)

    def test_missing_narrative(self, sample_complaint):
        """Test validation fails when narrative is missing."""
        del sample_complaint['narrative']

        with pytest.raises(ValueError) as exc_info:
            classify_complaint_lambda.validate_complaint(sample_complaint)

        assert 'Missing required fields: narrative' in str(exc_info.value)

    def test_empty_complaint_id(self, sample_complaint):
        """Test validation fails when complaint_id is empty."""
        sample_complaint['complaint_id'] = '   '

        with pytest.raises(ValueError) as exc_info:
            classify_complaint_lambda.validate_complaint(sample_complaint)

        assert 'complaint_id cannot be empty' in str(exc_info.value)

    def test_empty_narrative(self, sample_complaint):
        """Test validation fails when narrative is empty."""
        sample_complaint['narrative'] = '   '

        with pytest.raises(ValueError) as exc_info:
            classify_complaint_lambda.validate_complaint(sample_complaint)

        assert 'narrative cannot be empty' in str(exc_info.value)

    def test_narrative_too_long(self, sample_complaint):
        """Test validation fails when narrative exceeds max length."""
        sample_complaint['narrative'] = 'x' * 421

        with pytest.raises(ValueError) as exc_info:
            classify_complaint_lambda.validate_complaint(sample_complaint)

        assert 'narrative exceeds maximum length' in str(exc_info.value)


class TestPrepareStepFunctionInput:
    """Tests for prepare_step_function_input function."""

    def test_prepare_input_minimal(self, sample_complaint):
        """Test preparing Step Function input with minimal data."""
        result = classify_complaint_lambda.prepare_step_function_input(sample_complaint)

        assert result['complaint_id'] == sample_complaint['complaint_id']
        assert result['narrative'] == sample_complaint['narrative']
        assert result['status'] == 'IN-REVIEW'  # default
        assert result['source'] == 'api'  # default
        assert 'metadata' in result
        assert result['metadata']['trigger_source'] == 'classify_complaints_lambda'

    def test_prepare_input_full(self, sample_complaint_full):
        """Test preparing Step Function input with full data."""
        result = classify_complaint_lambda.prepare_step_function_input(sample_complaint_full)

        assert result['complaint_id'] == sample_complaint_full['complaint_id']
        assert result['code'] == sample_complaint_full['code']
        assert result['narrative'] == sample_complaint_full['narrative']
        assert result['status'] == sample_complaint_full['status']
        assert result['created_at'] == sample_complaint_full['created_at']
        assert result['created_by'] == sample_complaint_full['created_by']
        assert result['source'] == sample_complaint_full['source']

    def test_prepare_input_with_floats(self, sample_complaint):
        """Test preparing input converts floats to Decimal."""
        sample_complaint['score'] = 3.14
        sample_complaint['metrics'] = {'value': 2.71}

        result = classify_complaint_lambda.prepare_step_function_input(sample_complaint)

        assert isinstance(result['score'], Decimal)
        assert isinstance(result['metrics']['value'], Decimal)

    def test_prepare_input_adds_metadata(self, sample_complaint):
        """Test that metadata is added to input."""
        result = classify_complaint_lambda.prepare_step_function_input(sample_complaint)

        assert 'metadata' in result
        assert 'triggered_at' in result['metadata']
        assert 'trigger_source' in result['metadata']


class TestStartStepFunction:
    """Tests for start_step_function function."""

    def test_successful_start(self, sample_complaint):
        """Test successful Step Function execution start."""
        # Mock Step Functions client
        mock_sf_client = Mock()
        mock_sf_client.start_execution.return_value = {
            'executionArn': 'arn:aws:states:us-east-1:123456789012:execution:qms-dev-classify:exec-123',
            'startDate': datetime.now(timezone.utc)
        }

        step_function_arn = 'arn:aws:states:us-east-1:123456789012:stateMachine:qms-dev-classify-complaints'

        # Start execution
        execution_arn = classify_complaint_lambda.start_step_function(
            mock_sf_client,
            step_function_arn,
            sample_complaint
        )

        # Verify start_execution was called
        assert mock_sf_client.start_execution.called
        call_args = mock_sf_client.start_execution.call_args

        assert call_args[1]['stateMachineArn'] == step_function_arn
        assert 'classify-' in call_args[1]['name']
        assert sample_complaint['complaint_id'] in call_args[1]['name']

        # Verify input contains required fields
        step_input = json.loads(call_args[1]['input'])
        assert step_input['complaint_id'] == sample_complaint['complaint_id']
        assert step_input['narrative'] == sample_complaint['narrative']

        # Verify return value
        assert execution_arn == 'arn:aws:states:us-east-1:123456789012:execution:qms-dev-classify:exec-123'

    def test_start_with_full_data(self, sample_complaint_full):
        """Test starting Step Function with full complaint data."""
        mock_sf_client = Mock()
        mock_sf_client.start_execution.return_value = {
            'executionArn': 'arn:aws:states:us-east-1:123456789012:execution:qms-dev-classify:exec-456'
        }

        step_function_arn = 'arn:aws:states:us-east-1:123456789012:stateMachine:qms-dev-classify-complaints'

        execution_arn = classify_complaint_lambda.start_step_function(
            mock_sf_client,
            step_function_arn,
            sample_complaint_full
        )

        # Verify input contains all fields
        call_args = mock_sf_client.start_execution.call_args
        step_input = json.loads(call_args[1]['input'])

        assert step_input['code'] == sample_complaint_full['code']
        assert step_input['status'] == sample_complaint_full['status']

    def test_start_failure(self, sample_complaint):
        """Test error handling when start fails."""
        mock_sf_client = Mock()
        mock_sf_client.start_execution.side_effect = Exception('Step Function not found')

        step_function_arn = 'arn:aws:states:us-east-1:123456789012:stateMachine:qms-dev-classify-complaints'

        with pytest.raises(Exception) as exc_info:
            classify_complaint_lambda.start_step_function(
                mock_sf_client,
                step_function_arn,
                sample_complaint
            )

        assert 'Step Function not found' in str(exc_info.value)


class TestLambdaHandler:
    """Tests for lambda_handler function."""

    @patch('classify_complaints.lambda_function.boto3')
    def test_successful_processing(self, mock_boto3, sqs_event, mock_context):
        """Test successful processing of SQS message."""
        # Mock Step Functions client
        mock_sf_client = Mock()
        mock_sf_client.start_execution.return_value = {
            'executionArn': 'arn:aws:states:us-east-1:123456789012:execution:qms-dev-classify:exec-123'
        }

        mock_boto3.client.return_value = mock_sf_client

        # Process event
        response = classify_complaint_lambda.lambda_handler(sqs_event, mock_context)

        # Verify response
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['successful'] == 1
        assert body['failed'] == 0
        assert body['processed'] == 1
        assert len(body['executions']) == 1
        assert body['executions'][0]['complaint_id'] == '01JBQR3K7HXGM4P9N5T8WZVF2Y'

    @patch('classify_complaints.lambda_function.boto3')
    def test_invalid_json(self, mock_boto3, mock_context):
        """Test handling of invalid JSON in message."""
        mock_sf_client = Mock()
        mock_boto3.client.return_value = mock_sf_client

        # Create event with invalid JSON
        event = {
            'Records': [
                {
                    'messageId': 'test-message-id',
                    'body': 'invalid json{'
                }
            ]
        }

        response = classify_complaint_lambda.lambda_handler(event, mock_context)

        assert response['statusCode'] == 207
        body = json.loads(response['body'])
        assert body['successful'] == 0
        assert body['failed'] == 1
        assert body['errors'][0]['error'] == 'InvalidJSON'

    @patch('classify_complaints.lambda_function.boto3')
    def test_validation_error(self, mock_boto3, mock_context):
        """Test handling of validation errors."""
        mock_sf_client = Mock()
        mock_boto3.client.return_value = mock_sf_client

        # Create event with invalid complaint (missing narrative)
        invalid_complaint = {'complaint_id': '123'}
        event = {
            'Records': [
                {
                    'messageId': 'test-message-id',
                    'body': json.dumps(invalid_complaint)
                }
            ]
        }

        response = classify_complaint_lambda.lambda_handler(event, mock_context)

        assert response['statusCode'] == 207
        body = json.loads(response['body'])
        assert body['successful'] == 0
        assert body['failed'] == 1
        assert body['errors'][0]['error'] == 'ValidationError'

    @patch('classify_complaints.lambda_function.boto3')
    def test_step_function_error(self, mock_boto3, sample_complaint, mock_context):
        """Test handling of Step Function errors."""
        # Mock Step Functions client that raises exception
        mock_sf_client = Mock()
        mock_sf_client.start_execution.side_effect = Exception('Step Function execution failed')
        mock_boto3.client.return_value = mock_sf_client

        # Create event
        event = {
            'Records': [
                {
                    'messageId': 'test-message-id',
                    'body': json.dumps(sample_complaint)
                }
            ]
        }

        response = classify_complaint_lambda.lambda_handler(event, mock_context)

        assert response['statusCode'] == 207
        body = json.loads(response['body'])
        assert body['successful'] == 0
        assert body['failed'] == 1
        assert body['errors'][0]['error'] == 'ProcessingError'

    @patch('classify_complaints.lambda_function.boto3')
    def test_multiple_messages(self, mock_boto3, sample_complaint, mock_context):
        """Test processing multiple messages."""
        mock_sf_client = Mock()
        mock_sf_client.start_execution.return_value = {
            'executionArn': 'arn:aws:states:us-east-1:123456789012:execution:qms-dev-classify:exec-123'
        }
        mock_boto3.client.return_value = mock_sf_client

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

        response = classify_complaint_lambda.lambda_handler(event, mock_context)

        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['successful'] == 3
        assert body['failed'] == 0
        assert body['processed'] == 3
        assert len(body['executions']) == 3

        # Verify Step Functions was called 3 times
        assert mock_sf_client.start_execution.call_count == 3

    @patch('classify_complaints.lambda_function.boto3')
    def test_partial_batch_failure(self, mock_boto3, sample_complaint, mock_context):
        """Test processing when some messages succeed and some fail."""
        mock_sf_client = Mock()
        mock_sf_client.start_execution.return_value = {
            'executionArn': 'arn:aws:states:us-east-1:123456789012:execution:qms-dev-classify:exec-123'
        }
        mock_boto3.client.return_value = mock_sf_client

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

        response = classify_complaint_lambda.lambda_handler(event, mock_context)

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
        result = classify_complaint_lambda._convert_floats_to_decimal(3.14)
        assert isinstance(result, Decimal)
        assert result == Decimal('3.14')

    def test_convert_dict_with_floats(self):
        """Test conversion of dict containing floats."""
        data = {
            'score': 3.14,
            'name': 'test',
            'count': 5
        }
        result = classify_complaint_lambda._convert_floats_to_decimal(data)

        assert isinstance(result['score'], Decimal)
        assert isinstance(result['name'], str)
        assert isinstance(result['count'], int)

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
        result = classify_complaint_lambda._convert_floats_to_decimal(data)

        assert all(isinstance(x, Decimal) for x in result['scores'])
        assert isinstance(result['metadata']['average'], Decimal)
        assert all(isinstance(item['value'], Decimal) for item in result['metadata']['items'])


class TestDecimalDefault:
    """Tests for decimal_default function."""

    def test_serialize_decimal(self):
        """Test serializing Decimal to float."""
        result = classify_complaint_lambda.decimal_default(Decimal('3.14'))
        assert isinstance(result, float)
        assert result == 3.14

    def test_serialize_non_decimal_raises_error(self):
        """Test that non-Decimal objects raise TypeError."""
        with pytest.raises(TypeError):
            classify_complaint_lambda.decimal_default("not a decimal")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
