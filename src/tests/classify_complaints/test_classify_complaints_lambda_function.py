"""
Unit tests for classify_complaints lambda function

Tests cover:
- get_connection_string: Database connection string building
- get_narrative_from_db: Database queries for complaint narrative
- build_step_function_arn: ARN construction from Lambda context
- start_step_function: Step Functions execution
- lambda_handler: API endpoint handling
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import importlib.util
from datetime import datetime, timezone

# Mock dependencies before importing lambda_function
sys.modules['audit_logger'] = MagicMock()
sys.modules['secrets_util'] = MagicMock()

# Import the specific lambda_function module for classify_complaints
lambda_path = os.path.join(os.path.dirname(__file__), '../../app/classify_complaints/lambda_function.py')
spec = importlib.util.spec_from_file_location("classify_complaints_lambda", lambda_path)
lambda_function = importlib.util.module_from_spec(spec)
sys.modules['classify_complaints_lambda'] = lambda_function
spec.loader.exec_module(lambda_function)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_db_secret():
    """Mock database secret"""
    return {
        "host": "test-db.amazonaws.com",
        "port": 5432,
        "dbname": "testdb",
        "username": "testuser",
        "password": "testpass"
    }


@pytest.fixture
def sample_complaint_narrative():
    """Sample complaint narrative"""
    return "Patient reported adverse reaction to medication. Symptoms included nausea and dizziness."


@pytest.fixture
def mock_lambda_context():
    """Mock Lambda context"""
    context = MagicMock()
    context.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"
    return context


@pytest.fixture
def sample_event():
    """Sample API Gateway event"""
    return {
        'httpMethod': 'POST',
        'body': json.dumps({'complaint_id': 'CAS-00001'}),
        'requestContext': {
            'authorizer': {
                'claims': {
                    'email': 'test@example.com'
                }
            }
        }
    }


# ============================================================================
# TEST: get_connection_string
# ============================================================================

class TestGetConnectionString:
    """Tests for get_connection_string function"""

    @patch('classify_complaints_lambda.get_secret')
    def test_get_connection_string_success(self, mock_get_secret, mock_db_secret):
        """Test successful connection string building"""
        # Setup
        mock_get_secret.return_value = mock_db_secret
        # Reset cache
        lambda_function._db_credentials = None
        lambda_function._connection_string = None

        # Execute
        result = lambda_function.get_connection_string()

        # Assert
        assert 'postgresql://' in result
        assert 'testuser' in result
        assert 'testpass' in result
        assert 'test-db.amazonaws.com' in result
        assert '5432' in result
        assert 'testdb' in result
        mock_get_secret.assert_called_once()

    @patch('classify_complaints_lambda.get_secret')
    def test_get_connection_string_caching(self, mock_get_secret, mock_db_secret):
        """Test connection string is cached"""
        # Setup
        mock_get_secret.return_value = mock_db_secret
        lambda_function._db_credentials = None
        lambda_function._connection_string = None

        # Execute - first call
        result1 = lambda_function.get_connection_string()
        # Execute - second call
        result2 = lambda_function.get_connection_string()

        # Assert
        assert result1 == result2
        # get_secret should only be called once due to caching
        mock_get_secret.assert_called_once()


    @patch('classify_complaints_lambda.get_secret')
    def test_get_connection_string_default_port(self, mock_get_secret):
        """Test connection string with default port"""
        # Setup
        secret_without_port = {
            "host": "test-db.amazonaws.com",
            "dbname": "testdb",
            "username": "testuser",
            "password": "testpass"
        }
        mock_get_secret.return_value = secret_without_port
        lambda_function._db_credentials = None
        lambda_function._connection_string = None

        # Execute
        result = lambda_function.get_connection_string()

        # Assert - should use default port 5432
        assert '5432' in result


# ============================================================================
# TEST: get_narrative_from_db
# ============================================================================

class TestGetNarrativeFromDb:
    """Tests for get_narrative_from_db function"""

    @patch('classify_complaints_lambda.psycopg.connect')
    @patch('classify_complaints_lambda.get_connection_string')
    def test_get_narrative_from_db_success(self, mock_get_conn_str, mock_connect, 
                                          sample_complaint_narrative):
        """Test successful narrative retrieval"""
        # Setup
        mock_get_conn_str.return_value = "postgresql://test"
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (sample_complaint_narrative,)
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn

        # Execute
        result = lambda_function.get_narrative_from_db('CAS-00001')

        # Assert
        assert result == sample_complaint_narrative
        mock_cursor.execute.assert_called_once()
        assert 'CAS-00001' in str(mock_cursor.execute.call_args)

    @patch('classify_complaints_lambda.psycopg.connect')
    @patch('classify_complaints_lambda.get_connection_string')
    def test_get_narrative_from_db_not_found(self, mock_get_conn_str, mock_connect):
        """Test complaint not found in database"""
        # Setup
        mock_get_conn_str.return_value = "postgresql://test"
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn

        # Execute & Assert
        with pytest.raises(ValueError, match="Complaint CAS-99999 not found"):
            lambda_function.get_narrative_from_db('CAS-99999')

    @patch('classify_complaints_lambda.psycopg.connect')
    @patch('classify_complaints_lambda.get_connection_string')
    def test_get_narrative_from_db_connection_error(self, mock_get_conn_str, mock_connect):
        """Test database connection error"""
        # Setup
        mock_get_conn_str.return_value = "postgresql://test"
        mock_connect.side_effect = Exception("Connection failed")

        # Execute & Assert
        with pytest.raises(Exception, match="Connection failed"):
            lambda_function.get_narrative_from_db('CAS-00001')


# ============================================================================
# TEST: build_step_function_arn
# ============================================================================

class TestBuildStepFunctionArn:
    """Tests for build_step_function_arn function"""

    def test_build_step_function_arn_success(self, mock_lambda_context):
        """Test successful ARN building"""
        # Execute
        result = lambda_function.build_step_function_arn(mock_lambda_context)

        # Assert
        assert result.startswith('arn:aws:states:')
        assert '123456789012' in result  # Account ID from context
        assert 'stateMachine' in result
        assert 'classify-complaints' in result

    def test_build_step_function_arn_with_env(self, mock_lambda_context):
        """Test ARN building with environment variable"""
        # Setup
        original_env = lambda_function.ENV
        original_step_name = lambda_function.STEP_FUNCTION_NAME
        lambda_function.ENV = 'prod'
        lambda_function.STEP_FUNCTION_NAME = 'qms-prod-classify-complaints'

        # Execute
        result = lambda_function.build_step_function_arn(mock_lambda_context)

        # Assert
        assert 'qms-prod-classify-complaints' in result

        # Cleanup
        lambda_function.ENV = original_env
        lambda_function.STEP_FUNCTION_NAME = original_step_name



# ============================================================================
# TEST: start_step_function
# ============================================================================

class TestStartStepFunction:
    """Tests for start_step_function function"""

    def test_start_step_function_success(self, sample_complaint_narrative):
        """Test successful Step Function execution start"""
        # Setup
        mock_sf_client = MagicMock()
        mock_sf_client.start_execution.return_value = {
            'executionArn': 'arn:aws:states:us-east-1:123456789012:execution:test:exec-123'
        }
        step_function_arn = 'arn:aws:states:us-east-1:123456789012:stateMachine:test'

        # Execute
        result = lambda_function.start_step_function(
            mock_sf_client,
            step_function_arn,
            'CAS-00001',
            sample_complaint_narrative
        )

        # Assert
        assert result == 'arn:aws:states:us-east-1:123456789012:execution:test:exec-123'
        mock_sf_client.start_execution.assert_called_once()
        
        # Verify call arguments
        call_args = mock_sf_client.start_execution.call_args
        assert call_args[1]['stateMachineArn'] == step_function_arn
        assert 'classify-CAS-00001-' in call_args[1]['name']
        
        # Verify input contains required fields
        input_data = json.loads(call_args[1]['input'])
        assert input_data['complaint_id'] == 'CAS-00001'
        assert input_data['narrative'] == sample_complaint_narrative
        assert input_data['status'] == 'IN-REVIEW'
        assert 'triggered_at' in input_data

    def test_start_step_function_api_error(self, sample_complaint_narrative):
        """Test Step Function API error"""
        # Setup
        mock_sf_client = MagicMock()
        mock_sf_client.start_execution.side_effect = Exception("Step Functions API error")
        step_function_arn = 'arn:aws:states:us-east-1:123456789012:stateMachine:test'

        # Execute & Assert
        with pytest.raises(Exception, match="Step Functions API error"):
            lambda_function.start_step_function(
                mock_sf_client,
                step_function_arn,
                'CAS-00001',
                sample_complaint_narrative
            )


# ============================================================================
# TEST: lambda_handler
# ============================================================================

class TestLambdaHandler:
    """Tests for lambda_handler function"""

    @patch('classify_complaints_lambda.log_workflow')
    @patch('classify_complaints_lambda.get_user_from_event')
    @patch('classify_complaints_lambda.psycopg.connect')
    @patch('classify_complaints_lambda.start_step_function')
    @patch('classify_complaints_lambda.get_narrative_from_db')
    @patch('classify_complaints_lambda.boto3.client')
    def test_lambda_handler_success(self, mock_boto_client, mock_get_narrative, 
                                    mock_start_sf, mock_connect, mock_get_user,
                                    mock_log_workflow, sample_event, 
                                    sample_complaint_narrative, mock_lambda_context):
        """Test successful lambda handler execution"""
        # Setup
        mock_get_narrative.return_value = sample_complaint_narrative
        mock_start_sf.return_value = 'arn:aws:states:us-east-1:123456789012:execution:test:exec-123'
        mock_get_user.return_value = 'test@example.com'
        mock_conn = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn

        # Execute
        result = lambda_function.lambda_handler(sample_event, mock_lambda_context)

        # Assert
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
        assert 'Classification started successfully' in body['message']
        assert body['data']['complaint_id'] == 'CAS-00001'
        assert 'execution_arn' in body['data']
        assert body['data']['status'] == 'started'
        
        # Verify workflow was logged
        mock_log_workflow.assert_called_once()
        mock_conn.commit.assert_called_once()

    def test_lambda_handler_options_request(self):
        """Test CORS preflight OPTIONS request"""
        # Setup
        event = {'httpMethod': 'OPTIONS'}

        # Execute
        result = lambda_function.lambda_handler(event, None)

        # Assert
        assert result['statusCode'] == 200
        assert 'Access-Control-Allow-Origin' in result['headers']

    def test_lambda_handler_missing_complaint_id(self, mock_lambda_context):
        """Test missing complaint_id in request"""
        # Setup
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({})
        }

        # Execute
        result = lambda_function.lambda_handler(event, mock_lambda_context)

        # Assert
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert body['success'] is False
        assert 'Missing complaint_id' in body['message']


    @patch('classify_complaints_lambda.get_narrative_from_db')
    @patch('classify_complaints_lambda.boto3.client')
    def test_lambda_handler_complaint_not_found(self, mock_boto_client, mock_get_narrative, 
                                                mock_lambda_context):
        """Test complaint not found in database"""
        # Setup
        mock_get_narrative.side_effect = ValueError("Complaint CAS-99999 not found")
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({'complaint_id': 'CAS-99999'})
        }

        # Execute
        result = lambda_function.lambda_handler(event, mock_lambda_context)

        # Assert
        assert result['statusCode'] == 404
        body = json.loads(result['body'])
        assert body['success'] is False
        assert 'not found' in body['message']

    @patch('classify_complaints_lambda.get_narrative_from_db')
    @patch('classify_complaints_lambda.boto3.client')
    def test_lambda_handler_database_error(self, mock_boto_client, mock_get_narrative, 
                                          mock_lambda_context):
        """Test database error"""
        # Setup
        mock_get_narrative.side_effect = Exception("Database connection failed")
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({'complaint_id': 'CAS-00001'})
        }

        # Execute
        result = lambda_function.lambda_handler(event, mock_lambda_context)

        # Assert
        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert body['success'] is False
        assert 'Internal server error' in body['message']

    @patch('classify_complaints_lambda.start_step_function')
    @patch('classify_complaints_lambda.get_narrative_from_db')
    @patch('classify_complaints_lambda.boto3.client')
    def test_lambda_handler_step_function_error(self, mock_boto_client, mock_get_narrative,
                                               mock_start_sf, sample_complaint_narrative,
                                               mock_lambda_context):
        """Test Step Function start error"""
        # Setup
        mock_get_narrative.return_value = sample_complaint_narrative
        mock_start_sf.side_effect = Exception("Step Functions error")
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({'complaint_id': 'CAS-00001'})
        }

        # Execute
        result = lambda_function.lambda_handler(event, mock_lambda_context)

        # Assert
        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert body['success'] is False

    def test_lambda_handler_invalid_json_body(self, mock_lambda_context):
        """Test invalid JSON in request body"""
        # Setup
        event = {
            'httpMethod': 'POST',
            'body': 'not valid json'
        }

        # Execute
        result = lambda_function.lambda_handler(event, mock_lambda_context)

        # Assert - JSON decode error is caught as ValueError, returns 404
        assert result['statusCode'] == 404
        body = json.loads(result['body'])
        assert body['success'] is False

    def test_lambda_handler_empty_body(self, mock_lambda_context):
        """Test empty request body"""
        # Setup
        event = {
            'httpMethod': 'POST',
            'body': None
        }

        # Execute
        result = lambda_function.lambda_handler(event, mock_lambda_context)

        # Assert - None body causes exception, returns 500
        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert body['success'] is False


# ============================================================================
# TEST: _response helper
# ============================================================================

class TestResponseHelper:
    """Tests for _response helper function"""

    def test_response_success(self):
        """Test successful response format"""
        # Execute
        result = lambda_function._response(200, "Success", {"key": "value"})

        # Assert
        assert result['statusCode'] == 200
        assert 'Access-Control-Allow-Origin' in result['headers']
        assert result['headers']['Access-Control-Allow-Origin'] == '*'
        
        body = json.loads(result['body'])
        assert body['success'] is True
        assert body['message'] == "Success"
        assert body['data'] == {"key": "value"}
        assert 'timestamp' in body

    def test_response_error(self):
        """Test error response format"""
        # Execute
        result = lambda_function._response(404, "Not found")

        # Assert
        assert result['statusCode'] == 404
        
        body = json.loads(result['body'])
        assert body['success'] is False
        assert body['message'] == "Not found"
        assert body['data'] == {}

    def test_response_cors_headers(self):
        """Test CORS headers are present"""
        # Execute
        result = lambda_function._response(200, "OK")

        # Assert
        headers = result['headers']
        assert 'Access-Control-Allow-Origin' in headers
        assert 'Access-Control-Allow-Methods' in headers
        assert 'Access-Control-Allow-Headers' in headers
        assert 'Access-Control-Max-Age' in headers



# ============================================================================
# TEST: Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflow"""

    @patch('classify_complaints_lambda.log_workflow')
    @patch('classify_complaints_lambda.get_user_from_event')
    @patch('classify_complaints_lambda.psycopg.connect')
    @patch('classify_complaints_lambda.get_secret')
    @patch('classify_complaints_lambda.boto3.client')
    def test_end_to_end_classification_flow(self, mock_boto_client, mock_get_secret,
                                           mock_connect, mock_get_user, mock_log_workflow,
                                           sample_event, sample_complaint_narrative,
                                           mock_db_secret, mock_lambda_context):
        """Test complete end-to-end classification flow"""
        # Setup database
        mock_get_secret.return_value = mock_db_secret
        lambda_function._db_credentials = None
        lambda_function._connection_string = None
        
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (sample_complaint_narrative,)
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn

        # Setup Step Functions
        mock_sf_client = MagicMock()
        mock_sf_client.start_execution.return_value = {
            'executionArn': 'arn:aws:states:us-east-1:123456789012:execution:test:exec-123'
        }
        mock_boto_client.return_value = mock_sf_client

        # Setup user
        mock_get_user.return_value = 'test@example.com'

        # Execute
        result = lambda_function.lambda_handler(sample_event, mock_lambda_context)

        # Assert
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
        assert body['data']['complaint_id'] == 'CAS-00001'
        
        # Verify all steps were called
        mock_cursor.execute.assert_called_once()
        mock_sf_client.start_execution.assert_called_once()
        mock_log_workflow.assert_called_once()
        mock_conn.commit.assert_called_once()

    @patch('classify_complaints_lambda.log_workflow')
    @patch('classify_complaints_lambda.get_user_from_event')
    @patch('classify_complaints_lambda.psycopg.connect')
    @patch('classify_complaints_lambda.start_step_function')
    @patch('classify_complaints_lambda.get_narrative_from_db')
    @patch('classify_complaints_lambda.boto3.client')
    def test_logging_statistics(self, mock_boto_client, mock_get_narrative, mock_start_sf,
                               mock_connect, mock_get_user, mock_log_workflow,
                               sample_event, sample_complaint_narrative,
                               mock_lambda_context, caplog):
        """Test that proper logging occurs"""
        # Setup
        mock_get_narrative.return_value = sample_complaint_narrative
        mock_start_sf.return_value = 'arn:aws:states:us-east-1:123456789012:execution:test:exec-123'
        mock_get_user.return_value = 'test@example.com'
        mock_conn = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn

        # Execute
        with caplog.at_level('INFO'):
            lambda_function.lambda_handler(sample_event, mock_lambda_context)

        # Assert - check that important log messages are present
        log_messages = [record.message for record in caplog.records]
        assert any('CAS-00001' in msg for msg in log_messages)
        assert any('Successfully processed' in msg for msg in log_messages)


# ============================================================================
# TEST: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions"""

    @patch('classify_complaints_lambda.psycopg.connect')
    @patch('classify_complaints_lambda.get_connection_string')
    def test_empty_narrative(self, mock_get_conn_str, mock_connect):
        """Test handling of empty narrative"""
        # Setup
        mock_get_conn_str.return_value = "postgresql://test"
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ('',)  # Empty narrative
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn

        # Execute
        result = lambda_function.get_narrative_from_db('CAS-00001')

        # Assert - should return empty string
        assert result == ''

    @patch('classify_complaints_lambda.psycopg.connect')
    @patch('classify_complaints_lambda.get_connection_string')
    def test_very_long_narrative(self, mock_get_conn_str, mock_connect):
        """Test handling of very long narrative"""
        # Setup
        long_narrative = "A" * 100000  # 100k characters
        mock_get_conn_str.return_value = "postgresql://test"
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (long_narrative,)
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn

        # Execute
        result = lambda_function.get_narrative_from_db('CAS-00001')

        # Assert
        assert result == long_narrative
        assert len(result) == 100000

    def test_special_characters_in_complaint_id(self):
        """Test handling of special characters in complaint_id"""
        # Setup
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({'complaint_id': 'CAS-00001-TEST'})
        }
        mock_context = MagicMock()
        mock_context.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test"

        # Execute
        with patch('classify_complaints_lambda.get_narrative_from_db') as mock_get_narrative:
            with patch('classify_complaints_lambda.boto3.client'):
                mock_get_narrative.side_effect = ValueError("Complaint CAS-00001-TEST not found")
                result = lambda_function.lambda_handler(event, mock_context)

        # Assert
        assert result['statusCode'] == 404

    @patch('classify_complaints_lambda.log_workflow')
    @patch('classify_complaints_lambda.get_user_from_event')
    @patch('classify_complaints_lambda.psycopg.connect')
    @patch('classify_complaints_lambda.start_step_function')
    @patch('classify_complaints_lambda.get_narrative_from_db')
    @patch('classify_complaints_lambda.boto3.client')
    def test_workflow_logging_failure_causes_error(self, mock_boto_client, 
                                                   mock_get_narrative, mock_start_sf,
                                                   mock_connect, mock_get_user,
                                                   mock_log_workflow,
                                                   sample_complaint_narrative,
                                                   mock_lambda_context):
        """Test that workflow logging failure causes error response"""
        # Setup
        mock_get_narrative.return_value = sample_complaint_narrative
        mock_start_sf.return_value = 'arn:aws:states:us-east-1:123456789012:execution:test:exec-123'
        mock_get_user.return_value = 'test@example.com'
        mock_log_workflow.side_effect = Exception("Logging failed")
        mock_conn = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({'complaint_id': 'CAS-00001'})
        }

        # Execute - logging error is caught and returns 500
        result = lambda_function.lambda_handler(event, mock_lambda_context)
        
        # Assert
        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert body['success'] is False
        assert 'Logging failed' in body['message']
