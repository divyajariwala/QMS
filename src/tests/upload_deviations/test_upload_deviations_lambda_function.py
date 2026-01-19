"""
Unit tests for upload_deviations Lambda function
"""
import json
import sys
from unittest.mock import MagicMock, patch, Mock
import pytest
import importlib.util
from datetime import datetime, timezone
import base64

# Mock dependencies before importing the lambda module
mock_secrets_util = MagicMock()
mock_audit_logger = MagicMock()

sys.modules['secrets_util'] = mock_secrets_util
sys.modules['audit_logger'] = mock_audit_logger

# Load the lambda_function module
spec = importlib.util.spec_from_file_location(
    "upload_deviations_lambda",
    "src/app/upload_deviations/lambda_function.py"
)
lambda_module = importlib.util.module_from_spec(spec)
sys.modules['upload_deviations_lambda'] = lambda_module
spec.loader.exec_module(lambda_module)


@pytest.fixture(autouse=True)
def setup_environment(monkeypatch):
    """Set up environment variables for all tests"""
    monkeypatch.setenv('env', 'test')
    monkeypatch.setenv('S3_BUCKET_NAME', 'test-bucket')
    monkeypatch.setenv('SQS_QUEUE_NAME', 'test-queue')
    monkeypatch.setenv('db_secret_base_name', 'test-db-secret')
    monkeypatch.setenv('db_region', 'us-east-1')


@pytest.fixture
def mock_secrets():
    """Mock secrets_util.get_secret"""
    with patch('upload_deviations_lambda.get_secret') as mock:
        mock.return_value = {
            'host': 'test-host',
            'port': 5432,
            'dbname': 'test-db',
            'username': 'test-user',
            'password': 'test-password'
        }
        yield mock


@pytest.fixture
def mock_psycopg():
    """Mock psycopg connection and cursor"""
    with patch('upload_deviations_lambda.psycopg') as mock_pg:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        
        # Setup cursor context manager
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        
        # Setup connection context manager
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        
        # Setup connect to return connection
        mock_pg.connect.return_value = mock_conn
        
        yield {
            'psycopg': mock_pg,
            'connection': mock_conn,
            'cursor': mock_cursor
        }


@pytest.fixture
def mock_boto3():
    """Mock boto3 clients"""
    with patch('upload_deviations_lambda.boto3') as mock_b3:
        mock_s3 = MagicMock()
        mock_sqs = MagicMock()
        
        def client_factory(service_name):
            if service_name == 's3':
                return mock_s3
            elif service_name == 'sqs':
                return mock_sqs
            return MagicMock()
        
        mock_b3.client.side_effect = client_factory
        
        # Setup SQS queue URL
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789/test-queue'}
        mock_sqs.send_message.return_value = {'MessageId': 'test-message-id-123'}
        
        yield {
            'boto3': mock_b3,
            's3': mock_s3,
            'sqs': mock_sqs
        }


@pytest.fixture
def mock_log_deviation_workflow():
    """Mock log_deviation_workflow function"""
    with patch('upload_deviations_lambda.log_deviation_workflow') as mock:
        yield mock


@pytest.fixture
def sample_pdf_content():
    """Sample PDF file content"""
    return b'%PDF-1.4\n%\xE2\xE3\xCF\xD3\nSample PDF content for testing'


@pytest.fixture
def valid_multipart_event(sample_pdf_content):
    """Valid multipart/form-data event"""
    boundary = 'boundary123'
    
    # Build multipart body
    body_parts = []
    body_parts.append(f'--{boundary}\r\n')
    body_parts.append('Content-Disposition: form-data; name="file"; filename="test.pdf"\r\n')
    body_parts.append('Content-Type: application/pdf\r\n')
    body_parts.append('\r\n')
    
    # Convert to bytes and add PDF content
    body_bytes = ''.join(body_parts).encode('utf-8')
    body_bytes += sample_pdf_content
    body_bytes += f'\r\n--{boundary}--\r\n'.encode('utf-8')
    
    return {
        'headers': {
            'content-type': f'multipart/form-data; boundary={boundary}'
        },
        'body': base64.b64encode(body_bytes).decode('utf-8'),
        'isBase64Encoded': True
    }


# ============================================================================
# SUCCESS CASES
# ============================================================================

def test_successful_pdf_upload(mock_secrets, mock_psycopg, mock_boto3, 
                               mock_log_deviation_workflow, valid_multipart_event):
    """Test successful PDF upload"""
    # Setup database mocks
    mock_psycopg['cursor'].fetchone.return_value = {'deviation_id': 'DV-12345'}
    
    response = lambda_module.lambda_handler(valid_multipart_event, None)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    assert body['message'] == 'PDF file uploaded and queued for processing successfully'
    assert 'file_id' in body['data']
    assert body['data']['deviation_id'] == 'DV-12345'
    assert body['data']['filename'] == 'test.pdf'
    assert body['data']['status'] == 'processing'
    
    # Verify S3 upload
    mock_boto3['s3'].put_object.assert_called_once()
    
    # Verify SQS message
    mock_boto3['sqs'].send_message.assert_called_once()
    
    # Verify database inserts
    assert mock_psycopg['cursor'].execute.call_count == 2  # deviation_files + deviations


def test_successful_upload_with_user_from_authorizer(mock_secrets, mock_psycopg, 
                                                      mock_boto3, mock_log_deviation_workflow,
                                                      valid_multipart_event):
    """Test upload with user from authorizer claims"""
    valid_multipart_event['requestContext'] = {
        'authorizer': {
            'claims': {
                'email': 'user@example.com'
            }
        }
    }
    
    mock_psycopg['cursor'].fetchone.return_value = {'deviation_id': 'DV-12346'}
    
    response = lambda_module.lambda_handler(valid_multipart_event, None)
    
    assert response['statusCode'] == 200
    
    # Verify user was passed to database
    call_args = mock_psycopg['cursor'].execute.call_args_list[0][0]
    assert call_args[1][3] == 'user@example.com'


def test_successful_upload_with_user_from_header(mock_secrets, mock_psycopg,
                                                  mock_boto3, mock_log_deviation_workflow,
                                                  valid_multipart_event):
    """Test upload with user from header"""
    valid_multipart_event['headers']['x-user-email'] = 'header@example.com'
    
    mock_psycopg['cursor'].fetchone.return_value = {'deviation_id': 'DV-12347'}
    
    response = lambda_module.lambda_handler(valid_multipart_event, None)
    
    assert response['statusCode'] == 200


# ============================================================================
# VALIDATION ERROR CASES
# ============================================================================

def test_missing_body(mock_boto3):
    """Test error when body is missing"""
    event = {
        'headers': {
            'content-type': 'multipart/form-data; boundary=test'
        }
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'No file provided' in body['message']


def test_invalid_content_type(mock_boto3):
    """Test error when content-type is not multipart/form-data"""
    event = {
        'headers': {
            'content-type': 'application/json'
        },
        'body': 'test'
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'multipart/form-data' in body['message']


def test_missing_content_type(mock_boto3):
    """Test error when content-type header is missing"""
    event = {
        'headers': {},
        'body': 'test'
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 400


def test_file_too_large(mock_boto3, sample_pdf_content):
    """Test error when file exceeds size limit"""
    boundary = 'boundary123'
    
    # Create a large file (> 10MB)
    large_content = b'X' * (11 * 1024 * 1024)
    
    body_parts = []
    body_parts.append(f'--{boundary}\r\n')
    body_parts.append('Content-Disposition: form-data; name="file"; filename="large.pdf"\r\n')
    body_parts.append('Content-Type: application/pdf\r\n')
    body_parts.append('\r\n')
    
    body_bytes = ''.join(body_parts).encode('utf-8')
    body_bytes += large_content
    body_bytes += f'\r\n--{boundary}--\r\n'.encode('utf-8')
    
    event = {
        'headers': {
            'content-type': f'multipart/form-data; boundary={boundary}'
        },
        'body': base64.b64encode(body_bytes).decode('utf-8'),
        'isBase64Encoded': True
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'too large' in body['message']


def test_non_pdf_file(mock_boto3):
    """Test error when file is not a PDF"""
    boundary = 'boundary123'
    
    body_parts = []
    body_parts.append(f'--{boundary}\r\n')
    body_parts.append('Content-Disposition: form-data; name="file"; filename="test.txt"\r\n')
    body_parts.append('Content-Type: text/plain\r\n')
    body_parts.append('\r\n')
    body_parts.append('Some text content\r\n')
    body_parts.append(f'--{boundary}--\r\n')
    
    body_bytes = ''.join(body_parts).encode('utf-8')
    
    event = {
        'headers': {
            'content-type': f'multipart/form-data; boundary={boundary}'
        },
        'body': base64.b64encode(body_bytes).decode('utf-8'),
        'isBase64Encoded': True
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'PDF' in body['message']


def test_empty_file(mock_boto3):
    """Test error when file is empty"""
    boundary = 'boundary123'
    
    body_parts = []
    body_parts.append(f'--{boundary}\r\n')
    body_parts.append('Content-Disposition: form-data; name="file"; filename="empty.pdf"\r\n')
    body_parts.append('Content-Type: application/pdf\r\n')
    body_parts.append('\r\n')
    body_parts.append(f'\r\n--{boundary}--\r\n')
    
    body_bytes = ''.join(body_parts).encode('utf-8')
    
    event = {
        'headers': {
            'content-type': f'multipart/form-data; boundary={boundary}'
        },
        'body': base64.b64encode(body_bytes).decode('utf-8'),
        'isBase64Encoded': True
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'empty' in body['message']


def test_no_valid_file_in_multipart(mock_boto3):
    """Test error when no valid file found in multipart data"""
    boundary = 'boundary123'
    
    body_parts = []
    body_parts.append(f'--{boundary}\r\n')
    body_parts.append('Content-Disposition: form-data; name="field"\r\n')
    body_parts.append('\r\n')
    body_parts.append('some value\r\n')
    body_parts.append(f'--{boundary}--\r\n')
    
    body_bytes = ''.join(body_parts).encode('utf-8')
    
    event = {
        'headers': {
            'content-type': f'multipart/form-data; boundary={boundary}'
        },
        'body': base64.b64encode(body_bytes).decode('utf-8'),
        'isBase64Encoded': True
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'No valid file' in body['message']


# ============================================================================
# ERROR CASES
# ============================================================================

def test_sqs_queue_not_found(mock_boto3):
    """Test error when SQS queue is not found"""
    mock_boto3['sqs'].get_queue_url.side_effect = Exception("Queue not found")
    
    event = {
        'headers': {
            'content-type': 'multipart/form-data; boundary=test'
        },
        'body': 'test'
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 500
    body = json.loads(response['body'])
    assert 'Queue' in body['message']


def test_s3_upload_error(mock_secrets, mock_psycopg, mock_boto3,
                         mock_log_deviation_workflow, valid_multipart_event):
    """Test error when S3 upload fails"""
    mock_boto3['s3'].put_object.side_effect = Exception("S3 upload failed")
    
    response = lambda_module.lambda_handler(valid_multipart_event, None)
    
    assert response['statusCode'] == 500


def test_database_error(mock_secrets, mock_psycopg, mock_boto3,
                        mock_log_deviation_workflow, valid_multipart_event):
    """Test error when database operation fails"""
    mock_psycopg['cursor'].execute.side_effect = Exception("Database error")
    
    response = lambda_module.lambda_handler(valid_multipart_event, None)
    
    assert response['statusCode'] == 500


def test_sqs_send_message_error(mock_secrets, mock_psycopg, mock_boto3,
                                mock_log_deviation_workflow, valid_multipart_event):
    """Test error when SQS send message fails"""
    mock_psycopg['cursor'].fetchone.return_value = {'deviation_id': 'DV-12348'}
    mock_boto3['sqs'].send_message.side_effect = Exception("SQS error")
    
    response = lambda_module.lambda_handler(valid_multipart_event, None)
    
    assert response['statusCode'] == 500


# ============================================================================
# HELPER FUNCTION TESTS
# ============================================================================

def test_sanitize_filename():
    """Test filename sanitization"""
    assert lambda_module._sanitize_filename('test file.pdf') == 'test_file.pdf'
    assert lambda_module._sanitize_filename('test@#$%file.pdf') == 'test_file.pdf'
    assert lambda_module._sanitize_filename('test___file.pdf') == 'test_file.pdf'
    assert lambda_module._sanitize_filename('') == 'unknown_file.pdf'
    assert lambda_module._sanitize_filename(None) == 'unknown_file.pdf'


def test_get_user_from_event_with_claims():
    """Test extracting user from event with claims"""
    event = {
        'requestContext': {
            'authorizer': {
                'claims': {
                    'email': 'test@example.com'
                }
            }
        }
    }
    
    user = lambda_module._get_user_from_event(event)
    assert user == 'test@example.com'


def test_get_user_from_event_with_sub():
    """Test extracting user from event with sub claim"""
    event = {
        'requestContext': {
            'authorizer': {
                'claims': {
                    'sub': 'user-123'
                }
            }
        }
    }
    
    user = lambda_module._get_user_from_event(event)
    assert user == 'user-123'


def test_get_user_from_event_with_header():
    """Test extracting user from event headers"""
    event = {
        'headers': {
            'x-user-email': 'header@example.com'
        }
    }
    
    user = lambda_module._get_user_from_event(event)
    assert user == 'header@example.com'


def test_get_user_from_event_anonymous():
    """Test default anonymous user"""
    event = {}
    
    user = lambda_module._get_user_from_event(event)
    assert user == 'anonymous'


def test_get_connection_string_success(mock_secrets, monkeypatch):
    """Test get_connection_string builds correct connection string"""
    lambda_module._connection_string = None
    lambda_module._db_credentials = None
    
    monkeypatch.setenv('env', 'test')
    monkeypatch.setenv('db_secret_base_name', 'test-db-secret')
    lambda_module.ENV = 'test'
    lambda_module.DB_SECRET_NAME = 'qms-test-test-db-secret'
    
    conn_string = lambda_module.get_connection_string()
    
    assert conn_string == "postgresql://test-user:test-password@test-host:5432/test-db"


def test_get_connection_string_cached(mock_secrets):
    """Test get_connection_string uses cached value"""
    lambda_module._connection_string = "cached://connection"
    
    conn_string = lambda_module.get_connection_string()
    
    assert conn_string == "cached://connection"
    mock_secrets.assert_not_called()


def test_create_deviation_file_record(mock_secrets, mock_psycopg):
    """Test creating deviation file record"""
    lambda_module._connection_string = "postgresql://test:test@localhost:5432/test"
    
    lambda_module.create_deviation_file_record(
        'file-123',
        'test.pdf',
        's3://bucket/key',
        'user@example.com'
    )
    
    mock_psycopg['cursor'].execute.assert_called_once()
    call_args = mock_psycopg['cursor'].execute.call_args[0]
    assert 'INSERT INTO deviation_files' in call_args[0]
    assert call_args[1] == ('file-123', 'test.pdf', 's3://bucket/key', 'user@example.com')


def test_create_deviation_in_db(mock_secrets, mock_psycopg, mock_log_deviation_workflow):
    """Test creating deviation in database"""
    lambda_module._connection_string = "postgresql://test:test@localhost:5432/test"
    mock_psycopg['cursor'].fetchone.return_value = {'deviation_id': 'DV-99999'}
    
    start_time = datetime.utcnow()
    deviation_id = lambda_module.create_deviation_in_db('file-456', start_time)
    
    assert deviation_id == 'DV-99999'
    mock_psycopg['cursor'].execute.assert_called_once()
    mock_log_deviation_workflow.assert_called_once()


def test_parse_multipart_manual_success(sample_pdf_content):
    """Test successful multipart parsing"""
    boundary = 'testboundary'
    content_type = f'multipart/form-data; boundary={boundary}'
    
    body_parts = []
    body_parts.append(f'--{boundary}\r\n')
    body_parts.append('Content-Disposition: form-data; name="file"; filename="test.pdf"\r\n')
    body_parts.append('Content-Type: application/pdf\r\n')
    body_parts.append('\r\n')
    
    body_bytes = ''.join(body_parts).encode('utf-8')
    body_bytes += sample_pdf_content
    body_bytes += f'\r\n--{boundary}--\r\n'.encode('utf-8')
    
    result = lambda_module.parse_multipart_manual(body_bytes, content_type)
    
    assert result is not None
    assert result['filename'] == 'test.pdf'
    assert result['content'] == sample_pdf_content
    assert result['content_type'] == 'application/pdf'


def test_parse_multipart_manual_no_boundary():
    """Test multipart parsing with no boundary"""
    content_type = 'multipart/form-data'
    body_bytes = b'some data'
    
    result = lambda_module.parse_multipart_manual(body_bytes, content_type)
    
    assert result is None


def test_parse_multipart_manual_no_file():
    """Test multipart parsing with no file field"""
    boundary = 'testboundary'
    content_type = f'multipart/form-data; boundary={boundary}'
    
    body_parts = []
    body_parts.append(f'--{boundary}\r\n')
    body_parts.append('Content-Disposition: form-data; name="field"\r\n')
    body_parts.append('\r\n')
    body_parts.append('value\r\n')
    body_parts.append(f'--{boundary}--\r\n')
    
    body_bytes = ''.join(body_parts).encode('utf-8')
    
    result = lambda_module.parse_multipart_manual(body_bytes, content_type)
    
    assert result is None


def test_response_helper():
    """Test _response helper function"""
    response = lambda_module._response(200, "Success", {"key": "value"})
    
    assert response['statusCode'] == 200
    assert 'Access-Control-Allow-Origin' in response['headers']
    
    body = json.loads(response['body'])
    assert body['success'] is True
    assert body['message'] == "Success"
    assert body['data'] == {"key": "value"}
    assert 'timestamp' in body


def test_response_helper_error():
    """Test _response helper for error responses"""
    response = lambda_module._response(400, "Bad Request")
    
    assert response['statusCode'] == 400
    
    body = json.loads(response['body'])
    assert body['success'] is False
    assert body['message'] == "Bad Request"
