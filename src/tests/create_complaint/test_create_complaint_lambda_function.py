import pytest
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

# Mock dependencies before importing
sys.modules['psycopg'] = Mock()
sys.modules['psycopg.rows'] = Mock()
sys.modules['audit_logger'] = Mock()

# Add src directory to path for importing lambda_function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'app'))
from create_complaint import lambda_function


@pytest.fixture(autouse=True)
def mock_all_external_dependencies():
    """
    Auto-mock all external dependencies for ALL tests.
    This fixture runs automatically for every test.
    """
    with patch('create_complaint.lambda_function.get_secret') as mock_get_secret, \
            patch('create_complaint.lambda_function.psycopg.connect') as mock_psycopg_connect:
        # Mock Secrets Manager response
        mock_get_secret.return_value = {
            'host': 'test-db.cluster-xxxxx.us-east-1.rds.amazonaws.com',
            'port': 5432,
            'dbname': 'test_qms',
            'username': 'test_user',
            'password': 'test_password'
        }

        # Mock PostgreSQL connection (psycopg3 style with context managers)
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            'complaint_id': 'CAS-00001'
        }

        mock_conn = MagicMock()
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=False)

        mock_psycopg_connect.return_value = mock_conn

        # Reset cache before each test
        from create_complaint import lambda_function
        lambda_function._db_credentials = None
        lambda_function._connection_string = None

        yield


class TestLambdaHandler:
    """Unit tests for the main lambda_handler function"""
    @patch('create_complaint.lambda_function.boto3.client')
    @patch('create_complaint.lambda_function.SQS_QUEUE_NAME', 'test-queue')
    def test_successful_complaint_creation(self, mock_boto3):
        """Test: Successful complaint creation with valid narrative"""
        # Mock SQS client
        mock_sqs = Mock()
        mock_boto3.return_value = mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789/test-queue'}
        mock_sqs.send_message.return_value = {'MessageId': 'test-message-123'}

        # Create event with valid narrative
        event = {
            'body': json.dumps({
                'narrative': 'Customer reported a defect in the product packaging. The seal was broken.'
            }),
            'headers': {
                'content-type': 'application/json',
                'x-user-email': 'test@example.com'
            }
        }

        # Mock context
        context = Mock()
        context.request_id = 'test-request-123'

        result = lambda_function.lambda_handler(event, context)

        # Assertions
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
        assert body['message'] == "Complaint created and queued for processing"
        assert 'complaint' in body['data']
        assert 'CAS-' in body['data']['complaint']['complaint_id']
        assert body['data']['message_id'] == 'test-message-123'

        # Verify SQS was called
        mock_sqs.send_message.assert_called_once()
        call_args = mock_sqs.send_message.call_args
        assert call_args[1]['QueueUrl'] == 'https://sqs.us-east-1.amazonaws.com/123456789/test-queue'

    @patch('create_complaint.lambda_function.SQS_QUEUE_NAME', 'test-queue')
    @patch('boto3.client')
    def test_successful_with_cognito_user(self, mock_boto3):
        """Test: Successful complaint with Cognito user info"""
        mock_sqs = Mock()
        mock_boto3.return_value = mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.test.com/queue'}
        mock_sqs.send_message.return_value = {'MessageId': 'msg-456'}

        event = {
            'body': json.dumps({'narrative': 'Product defect reported'}),
            'headers': {'content-type': 'application/json'},
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'email': 'cognito-user@example.com',
                        'sub': 'user-12345'
                    }
                }
            }
        }

        context = Mock()
        context.request_id = 'req-123'

        result = lambda_function.lambda_handler(event, context)

        assert result['statusCode'] == 200

        # Verify the message sent to SQS contains the correct structure
        call_args = mock_sqs.send_message.call_args
        message_body = json.loads(call_args[1]['MessageBody'])
        assert message_body['complaint_id'] == 'CAS-00001'
        assert message_body['narrative_text'] == 'Product defect reported'

    @patch('create_complaint.lambda_function.SQS_QUEUE_NAME', 'test-queue')
    @patch('boto3.client')
    def test_empty_narrative(self, mock_boto3):
        """Test: Error when narrative is empty"""
        mock_sqs = Mock()
        mock_boto3.return_value = mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.test.com/queue'}

        event = {
            'body': json.dumps({'narrative': ''}),
            'headers': {'content-type': 'application/json'}
        }

        result = lambda_function.lambda_handler(event, None)

        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert body['success'] is False
        assert body['message'] == "Narrative is required"

    @patch('create_complaint.lambda_function.SQS_QUEUE_NAME', 'test-queue')
    @patch('boto3.client')
    def test_narrative_no_length_limit(self, mock_boto3):
        """Test: Success with very long narrative (no length limit)"""
        mock_sqs = Mock()
        mock_boto3.return_value = mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.test.com/queue'}
        mock_sqs.send_message.return_value = {'MessageId': 'test-message-long'}

        # Create narrative with 5000 characters (well beyond old 1500 limit)
        very_long_narrative = 'a' * 5000

        event = {
            'body': json.dumps({'narrative': very_long_narrative}),
            'headers': {'content-type': 'application/json'}
        }

        context = Mock()
        context.request_id = 'req-long'

        result = lambda_function.lambda_handler(event, context)

        # Should succeed with no length limit
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
        assert body['message'] == "Complaint created and queued for processing"

        # Verify the full narrative was preserved
        assert body['data']['complaint']['narrative'] == very_long_narrative
        assert len(body['data']['complaint']['narrative']) == 5000

        # Verify SQS was called with the full narrative
        call_args = mock_sqs.send_message.call_args
        message_body = json.loads(call_args[1]['MessageBody'])
        assert message_body['narrative_text'] == very_long_narrative
        assert len(message_body['narrative_text']) == 5000


    @patch('create_complaint.lambda_function.SQS_QUEUE_NAME', 'test-queue')
    @patch('boto3.client')
    def test_narrative_at_max_length(self, mock_boto3):
        """Test: Success when narrative is exactly 1500 characters"""
        mock_sqs = Mock()
        mock_boto3.return_value = mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.test.com/queue'}
        mock_sqs.send_message.return_value = {'MessageId': 'msg-789'}

        # Create narrative with exactly 1500 characters
        max_narrative = 'a' * 1500

        event = {
            'body': json.dumps({'narrative': max_narrative}),
            'headers': {'content-type': 'application/json'}
        }

        context = Mock()
        context.request_id = 'req-456'

        result = lambda_function.lambda_handler(event, context)

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True

    @patch('create_complaint.lambda_function.SQS_QUEUE_NAME', 'test-queue')
    @patch('boto3.client')
    def test_missing_body(self, mock_boto3):
        """Test: Error when body is missing"""
        mock_sqs = Mock()
        mock_boto3.return_value = mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.test.com/queue'}

        event = {
            'headers': {'content-type': 'application/json'}
        }

        result = lambda_function.lambda_handler(event, None)

        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert body['success'] is False

    @patch('create_complaint.lambda_function.SQS_QUEUE_NAME', 'test-queue')
    @patch('boto3.client')
    def test_invalid_json_body(self, mock_boto3):
        """Test: Error when body has invalid JSON"""
        mock_sqs = Mock()
        mock_boto3.return_value = mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.test.com/queue'}

        event = {
            'body': 'invalid-json{{{',
            'headers': {'content-type': 'application/json'}
        }

        result = lambda_function.lambda_handler(event, None)

        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert body['success'] is False

    @patch('create_complaint.lambda_function.SQS_QUEUE_NAME', 'non-existent-queue')
    @patch('boto3.client')
    def test_queue_not_found(self, mock_boto3):
        """Test: Error when SQS queue doesn't exist"""
        mock_sqs = Mock()
        mock_boto3.return_value = mock_sqs

        # Simulate queue not found error
        from botocore.exceptions import ClientError
        mock_sqs.get_queue_url.side_effect = ClientError(
            {'Error': {'Code': 'AWS.SimpleQueueService.NonExistentQueue'}},
            'GetQueueUrl'
        )

        event = {
            'body': json.dumps({'narrative': 'Test complaint'}),
            'headers': {'content-type': 'application/json'}
        }

        result = lambda_function.lambda_handler(event, None)

        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert "not found" in body['message']

    @patch('create_complaint.lambda_function.SQS_QUEUE_NAME', 'test-queue')
    @patch('boto3.client')
    def test_sqs_send_message_failure(self, mock_boto3):
        """Test: Error when SQS send_message fails"""
        mock_sqs = Mock()
        mock_boto3.return_value = mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.test.com/queue'}

        # Simulate SQS send failure
        mock_sqs.send_message.side_effect = Exception("SQS send failed")

        event = {
            'body': json.dumps({'narrative': 'Test complaint'}),
            'headers': {'content-type': 'application/json'}
        }

        context = Mock()
        context.request_id = 'req-789'

        result = lambda_function.lambda_handler(event, context)

        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert body['success'] is False

    @patch('create_complaint.lambda_function.SQS_QUEUE_NAME', 'test-queue')
    @patch('boto3.client')
    @patch('create_complaint.lambda_function.create_complaint_in_db')
    def test_database_error_during_creation(self, mock_create_db, mock_boto3):
        """Test: Error when database creation fails"""
        mock_sqs = Mock()
        mock_boto3.return_value = mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.test.com/queue'}

        # Simulate database error
        mock_create_db.side_effect = Exception("Database error")

        event = {
            'body': json.dumps({'narrative': 'Test complaint'}),
            'headers': {'content-type': 'application/json'}
        }

        context = Mock()
        context.request_id = 'req-db-error'

        result = lambda_function.lambda_handler(event, context)

        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert body['success'] is False
        assert 'Database error' in body['message']

    @patch('create_complaint.lambda_function.SQS_QUEUE_NAME', 'test-queue')
    @patch('boto3.client')
    def test_body_as_dict_not_string(self, mock_boto3):
        """Test: Handle body as dict instead of JSON string"""
        mock_sqs = Mock()
        mock_boto3.return_value = mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.test.com/queue'}
        mock_sqs.send_message.return_value = {'MessageId': 'msg-dict'}

        # Body as dict (not JSON string)
        event = {
            'body': {'narrative': 'Direct dict body'},
            'headers': {'content-type': 'application/json'}
        }

        context = Mock()
        context.request_id = 'req-dict'

        result = lambda_function.lambda_handler(event, context)

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True




class TestDatabaseIntegration:
    """Tests for database integration functions"""

    @patch('create_complaint.lambda_function.get_connection_string')
    @patch('create_complaint.lambda_function.psycopg.connect')
    @patch('create_complaint.lambda_function.log_workflow')
    def test_create_complaint_in_db_success(self, mock_log_workflow, mock_connect, mock_get_connection):
        """Test: Successful complaint creation in database with workflow logging"""
        mock_get_connection.return_value = 'postgresql://user:pass@host:5432/db'
        
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {'complaint_id': 'CAS-00001'}
        
        mock_conn = MagicMock()
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=False)
        mock_connect.return_value = mock_conn

        event = {'headers': {}}
        result = lambda_function.create_complaint_in_db('Test narrative', event)
        
        assert result == 'CAS-00001'
        mock_cursor.execute.assert_called_once()
        # Verify text_extracted is set to FALSE in the SQL
        call_args = mock_cursor.execute.call_args[0]
        assert 'text_extracted' in call_args[0]
        assert 'FALSE' in call_args[0]
        # Verify commit is called twice: once after INSERT, once after log_workflow
        assert mock_conn.commit.call_count == 2
        
        # Verify workflow logging was called
        mock_log_workflow.assert_called_once()

    @patch('create_complaint.lambda_function.get_connection_string')
    @patch('create_complaint.lambda_function.psycopg.connect')
    def test_create_complaint_in_db_error(self, mock_connect, mock_get_connection):
        """Test: Database error handling"""
        mock_get_connection.return_value = 'postgresql://user:pass@host:5432/db'
        mock_connect.side_effect = Exception("Database connection failed")

        event = {'headers': {}}
        with pytest.raises(Exception):
            lambda_function.create_complaint_in_db('Test narrative', event)

    @patch('create_complaint.lambda_function.get_connection_string')
    @patch('create_complaint.lambda_function.psycopg.connect')
    @patch('create_complaint.lambda_function.log_workflow')
    def test_create_complaint_workflow_logging_error(self, mock_log_workflow, mock_connect, mock_get_connection):
        """Test: Workflow logging error doesn't prevent complaint creation"""
        mock_get_connection.return_value = 'postgresql://user:pass@host:5432/db'
        
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {'complaint_id': 'CAS-00002'}
        
        mock_conn = MagicMock()
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=False)
        mock_connect.return_value = mock_conn
        
        # Simulate workflow logging error
        mock_log_workflow.side_effect = Exception("Workflow logging failed")

        event = {'headers': {'x-user-email': 'test@example.com'}}
        
        # Should raise the exception
        with pytest.raises(Exception):
            lambda_function.create_complaint_in_db('Test narrative', event)


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

    def test_get_user_from_event_cognito_sub_only(self):
        """Test: Extract user from Cognito sub when email is missing"""
        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'sub': 'user-456'
                    }
                }
            }
        }

        user = lambda_function._get_user_from_event(event)
        assert user == 'user-456'

    def test_get_user_from_event_header(self):
        """Test: Extract user from header"""
        event = {
            'headers': {
                'x-user-email': 'header-user@example.com'
            }
        }

        user = lambda_function._get_user_from_event(event)
        assert user == 'header-user@example.com'

    def test_get_user_from_event_header_user_id(self):
        """Test: Extract user from x-user-id header"""
        event = {
            'headers': {
                'x-user-id': 'user-789'
            }
        }

        user = lambda_function._get_user_from_event(event)
        assert user == 'user-789'

    def test_get_user_from_event_anonymous(self):
        """Test: Return anonymous when no user info"""
        event = {}

        user = lambda_function._get_user_from_event(event)
        assert user == 'anonymous'

    def test_get_user_from_event_exception(self):
        """Test: Return anonymous when exception occurs"""
        event = {
            'requestContext': {
                'authorizer': None  # This will cause an error when accessing ['claims']
            }
        }

        user = lambda_function._get_user_from_event(event)
        assert user == 'anonymous'

    def test_response_function_success(self):
        """Test: HTTP response for success"""
        result = lambda_function._response(200, "Success", {"key": "value"})

        assert result['statusCode'] == 200
        assert 'Access-Control-Allow-Origin' in result['headers']

        body = json.loads(result['body'])
        assert body['success'] is True
        assert body['message'] == "Success"
        assert body['data']['key'] == "value"
        assert 'timestamp' in body

    def test_response_function_error(self):
        """Test: HTTP response for error"""
        result = lambda_function._response(400, "Bad Request")

        assert result['statusCode'] == 400

        body = json.loads(result['body'])
        assert body['success'] is False
        assert body['message'] == "Bad Request"
        assert body['data'] == {}


class TestMessageFormatting:
    """Tests for SQS message formatting"""

    @patch('create_complaint.lambda_function.SQS_QUEUE_NAME', 'test-queue')
    @patch('boto3.client')
    def test_sqs_message_structure(self, mock_boto3):
        """Test: SQS message has correct structure"""
        mock_sqs = Mock()
        mock_boto3.return_value = mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.test.com/queue'}
        mock_sqs.send_message.return_value = {'MessageId': 'msg-test'}

        narrative = "Test complaint narrative"
        event = {
            'body': json.dumps({'narrative': narrative}),
            'headers': {
                'content-type': 'application/json',
                'x-user-email': 'tester@example.com'
            }
        }

        context = Mock()
        context.request_id = 'req-test'

        lambda_function.lambda_handler(event, context)

        # Verify send_message was called
        call_args = mock_sqs.send_message.call_args

        # Check message body
        message_body = json.loads(call_args[1]['MessageBody'])
        assert 'complaint_id' in message_body
        assert message_body['complaint_id'].startswith('CAS-')
        assert message_body['narrative_text'] == narrative
        assert 'file_id' in message_body

    @patch('create_complaint.lambda_function.SQS_QUEUE_NAME', 'test-queue')
    @patch('boto3.client')
    def test_narrative_preservation(self, mock_boto3):
        """Test: Long narratives are truncated in short_description"""
        mock_sqs = Mock()
        mock_boto3.return_value = mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.test.com/queue'}
        mock_sqs.send_message.return_value = {'MessageId': 'msg-test'}

        # Narrative longer than 100 characters
        long_narrative = "A" * 200

        event = {
            'body': json.dumps({'narrative': long_narrative}),
            'headers': {'content-type': 'application/json'}
        }

        context = Mock()
        context.request_id = 'req-test'

        lambda_function.lambda_handler(event, context)

        # Get the message that was sent
        call_args = mock_sqs.send_message.call_args
        message_body = json.loads(call_args[1]['MessageBody'])

        # narrative_text should be preserved in full
        assert message_body['narrative_text'] == long_narrative
        assert len(message_body['narrative_text']) == 200


class TestIntegration:
    """Integration tests for complete workflows"""

    @patch('create_complaint.lambda_function.SQS_QUEUE_NAME', 'test-queue')
    @patch('boto3.client')
    def test_end_to_end_complaint_creation(self, mock_boto3):
        """Test: Complete complaint creation workflow"""
        mock_sqs = Mock()
        mock_boto3.return_value = mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123/queue'}
        mock_sqs.send_message.return_value = {'MessageId': 'final-msg-id'}

        event = {
            'body': json.dumps({
                'narrative': 'Customer reported critical safety issue with product batch #12345'
            }),
            'headers': {
                'content-type': 'application/json',
                'x-user-email': 'safety@company.com'
            },
            'requestContext': {
                'requestId': 'api-req-123'
            }
        }

        context = Mock()
        context.request_id = 'lambda-req-456'
        context.function_name = 'create-complaint-test'

        # Execute
        result = lambda_function.lambda_handler(event, context)

        # Verify response
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True

        complaint_data = body['data']['complaint']
        assert complaint_data['complaint_id'].startswith('CAS-')
        assert complaint_data['status'] == 'Pending'
        assert 'created_at' in complaint_data

        # Verify SQS interaction
        mock_sqs.get_queue_url.assert_called_once_with(QueueName='test-queue')
        mock_sqs.send_message.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=create_complaint.lambda_function", "--cov-report=html"])
