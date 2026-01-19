"""
Unit tests for add_investigation_summary Lambda function
"""
import json
import sys
from unittest.mock import MagicMock, patch, Mock
import pytest
import importlib.util

# Mock secrets_util before importing the lambda module
mock_secrets_util = MagicMock()
sys.modules['secrets_util'] = mock_secrets_util

# Load the lambda_function module
spec = importlib.util.spec_from_file_location(
    "add_investigation_summary_lambda",
    "src/app/add_investigation_summary/lambda_function.py"
)
lambda_module = importlib.util.module_from_spec(spec)
sys.modules['add_investigation_summary_lambda'] = lambda_module
spec.loader.exec_module(lambda_module)


@pytest.fixture(autouse=True)
def setup_environment(monkeypatch):
    """Set up environment variables for all tests"""
    monkeypatch.setenv('env', 'test')
    monkeypatch.setenv('db_secret_base_name', 'test-db-secret')
    monkeypatch.setenv('db_region', 'us-east-1')


@pytest.fixture
def mock_secrets():
    """Mock secrets_util.get_secret"""
    with patch('add_investigation_summary_lambda.get_secret') as mock:
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
    with patch('add_investigation_summary_lambda.psycopg') as mock_pg:
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
def valid_event():
    """Valid event with all required fields"""
    return {
        'body': json.dumps({
            'deviationId': 'DV-12345',
            'summary': 'This is a test investigation summary'
        })
    }


@pytest.fixture
def valid_event_dict():
    """Valid event as dict (not stringified)"""
    return {
        'deviationId': 'DV-12345',
        'summary': 'This is a test investigation summary'
    }


# ============================================================================
# SUCCESS CASES
# ============================================================================

def test_successful_update_with_string_body(mock_secrets, mock_psycopg, valid_event):
    """Test successful update with stringified body"""
    mock_psycopg['cursor'].rowcount = 1
    
    response = lambda_module.lambda_handler(valid_event, None)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['message'] == 'Investigation summary updated successfully'
    assert response['headers']['Access-Control-Allow-Origin'] == '*'
    
    # Verify database call
    mock_psycopg['cursor'].execute.assert_called_once()
    call_args = mock_psycopg['cursor'].execute.call_args[0]
    assert 'UPDATE deviations' in call_args[0]
    assert call_args[1] == ('This is a test investigation summary', 'DV-12345')


def test_successful_update_with_dict_body(mock_secrets, mock_psycopg, valid_event_dict):
    """Test successful update with dict body (not stringified)"""
    mock_psycopg['cursor'].rowcount = 1
    
    response = lambda_module.lambda_handler(valid_event_dict, None)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['message'] == 'Investigation summary updated successfully'


def test_successful_update_with_long_summary(mock_secrets, mock_psycopg):
    """Test successful update with a long summary"""
    long_summary = "A" * 5000
    event = {
        'body': json.dumps({
            'deviationId': 'DV-99999',
            'summary': long_summary
        })
    }
    mock_psycopg['cursor'].rowcount = 1
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 200
    call_args = mock_psycopg['cursor'].execute.call_args[0]
    assert call_args[1] == (long_summary, 'DV-99999')


def test_successful_update_with_special_characters(mock_secrets, mock_psycopg):
    """Test successful update with special characters in summary"""
    special_summary = "Summary with 'quotes', \"double quotes\", and\nnewlines\t\ttabs"
    event = {
        'body': json.dumps({
            'deviationId': 'DV-00001',
            'summary': special_summary
        })
    }
    mock_psycopg['cursor'].rowcount = 1
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 200
    call_args = mock_psycopg['cursor'].execute.call_args[0]
    assert call_args[1] == (special_summary, 'DV-00001')


# ============================================================================
# VALIDATION ERROR CASES
# ============================================================================

def test_missing_deviation_id(mock_secrets, mock_psycopg):
    """Test error when deviationId is missing"""
    event = {
        'body': json.dumps({
            'summary': 'Test summary'
        })
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'Missing required field: deviationId' in body['error']
    mock_psycopg['cursor'].execute.assert_not_called()


def test_missing_summary(mock_secrets, mock_psycopg):
    """Test error when summary is missing"""
    event = {
        'body': json.dumps({
            'deviationId': 'DV-12345'
        })
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'Missing required field: summary' in body['error']
    mock_psycopg['cursor'].execute.assert_not_called()


def test_empty_deviation_id(mock_secrets, mock_psycopg):
    """Test error when deviationId is empty string"""
    event = {
        'body': json.dumps({
            'deviationId': '',
            'summary': 'Test summary'
        })
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'deviationId must be a non-empty string' in body['error']


def test_whitespace_only_deviation_id(mock_secrets, mock_psycopg):
    """Test error when deviationId is only whitespace"""
    event = {
        'body': json.dumps({
            'deviationId': '   ',
            'summary': 'Test summary'
        })
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'deviationId must be a non-empty string' in body['error']


def test_invalid_deviation_id_format_no_prefix(mock_secrets, mock_psycopg):
    """Test error when deviationId doesn't have DV- prefix"""
    event = {
        'body': json.dumps({
            'deviationId': '12345',
            'summary': 'Test summary'
        })
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'deviationId must be in format DV-XXXXX' in body['error']


def test_invalid_deviation_id_format_wrong_prefix(mock_secrets, mock_psycopg):
    """Test error when deviationId has wrong prefix"""
    event = {
        'body': json.dumps({
            'deviationId': 'DEV-12345',
            'summary': 'Test summary'
        })
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'deviationId must be in format DV-XXXXX' in body['error']


def test_invalid_deviation_id_format_too_few_digits(mock_secrets, mock_psycopg):
    """Test error when deviationId has too few digits"""
    event = {
        'body': json.dumps({
            'deviationId': 'DV-123',
            'summary': 'Test summary'
        })
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'deviationId must be in format DV-XXXXX' in body['error']


def test_invalid_deviation_id_format_too_many_digits(mock_secrets, mock_psycopg):
    """Test error when deviationId has too many digits"""
    event = {
        'body': json.dumps({
            'deviationId': 'DV-123456',
            'summary': 'Test summary'
        })
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'deviationId must be in format DV-XXXXX' in body['error']


def test_invalid_deviation_id_format_letters_in_number(mock_secrets, mock_psycopg):
    """Test error when deviationId has letters in the number part"""
    event = {
        'body': json.dumps({
            'deviationId': 'DV-12A45',
            'summary': 'Test summary'
        })
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'deviationId must be in format DV-XXXXX' in body['error']


def test_empty_summary(mock_secrets, mock_psycopg):
    """Test error when summary is empty string"""
    event = {
        'body': json.dumps({
            'deviationId': 'DV-12345',
            'summary': ''
        })
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'summary must be a non-empty string' in body['error']


def test_whitespace_only_summary(mock_secrets, mock_psycopg):
    """Test error when summary is only whitespace"""
    event = {
        'body': json.dumps({
            'deviationId': 'DV-12345',
            'summary': '   \n\t  '
        })
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'summary must be a non-empty string' in body['error']


def test_invalid_deviation_id_type_number(mock_secrets, mock_psycopg):
    """Test error when deviationId is a number"""
    event = {
        'body': json.dumps({
            'deviationId': 12345,
            'summary': 'Test summary'
        })
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'deviationId must be a non-empty string' in body['error']


def test_invalid_summary_type_number(mock_secrets, mock_psycopg):
    """Test error when summary is a number"""
    event = {
        'body': json.dumps({
            'deviationId': 'DV-12345',
            'summary': 12345
        })
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'summary must be a non-empty string' in body['error']


def test_invalid_summary_type_null(mock_secrets, mock_psycopg):
    """Test error when summary is null"""
    event = {
        'body': json.dumps({
            'deviationId': 'DV-12345',
            'summary': None
        })
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'summary must be a non-empty string' in body['error']


# ============================================================================
# NOT FOUND CASES
# ============================================================================

def test_deviation_not_found(mock_secrets, mock_psycopg):
    """Test error when deviation doesn't exist in database"""
    mock_psycopg['cursor'].rowcount = 0
    event = {
        'body': json.dumps({
            'deviationId': 'DV-99999',
            'summary': 'Test summary'
        })
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 404
    body = json.loads(response['body'])
    assert 'Deviation not found: DV-99999' in body['error']


# ============================================================================
# ERROR HANDLING CASES
# ============================================================================

def test_invalid_json_body(mock_secrets, mock_psycopg):
    """Test error when body is invalid JSON"""
    event = {
        'body': 'invalid json {'
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 500
    body = json.loads(response['body'])
    assert 'Internal server error' in body['error']


def test_database_connection_error(mock_secrets, mock_psycopg):
    """Test error when database connection fails"""
    mock_psycopg['psycopg'].connect.side_effect = Exception("Connection failed")
    event = {
        'body': json.dumps({
            'deviationId': 'DV-12345',
            'summary': 'Test summary'
        })
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 500
    body = json.loads(response['body'])
    assert 'Internal server error' in body['error']


def test_database_query_error(mock_secrets, mock_psycopg):
    """Test error when database query fails"""
    mock_psycopg['cursor'].execute.side_effect = Exception("Query failed")
    event = {
        'body': json.dumps({
            'deviationId': 'DV-12345',
            'summary': 'Test summary'
        })
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 500
    body = json.loads(response['body'])
    assert 'Internal server error' in body['error']


def test_secrets_retrieval_error(mock_secrets, mock_psycopg):
    """Test error when secrets retrieval fails"""
    mock_secrets.side_effect = Exception("Secrets error")
    event = {
        'body': json.dumps({
            'deviationId': 'DV-12345',
            'summary': 'Test summary'
        })
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 500
    body = json.loads(response['body'])
    assert 'Internal server error' in body['error']


# ============================================================================
# HELPER FUNCTION TESTS
# ============================================================================

def test_get_connection_string_success(mock_secrets, monkeypatch):
    """Test get_connection_string builds correct connection string"""
    # Reset cached values
    lambda_module._connection_string = None
    lambda_module._db_credentials = None
    
    # Set environment variables before calling
    monkeypatch.setenv('env', 'test')
    monkeypatch.setenv('db_secret_base_name', 'test-db-secret')
    monkeypatch.setenv('db_region', 'us-east-1')
    
    # Update module constants
    lambda_module.ENV = 'test'
    lambda_module.DB_SECRET_NAME = 'qms-test-test-db-secret'
    lambda_module.DB_REGION = 'us-east-1'
    
    conn_string = lambda_module.get_connection_string()
    
    assert conn_string == "postgresql://test-user:test-password@test-host:5432/test-db"
    mock_secrets.assert_called_once_with('qms-test-test-db-secret', 'us-east-1')


def test_get_connection_string_cached(mock_secrets):
    """Test get_connection_string uses cached value"""
    # Set cached value
    lambda_module._connection_string = "cached://connection"
    
    conn_string = lambda_module.get_connection_string()
    
    assert conn_string == "cached://connection"
    mock_secrets.assert_not_called()


def test_get_connection_string_with_default_port(mock_secrets):
    """Test get_connection_string uses default port when not provided"""
    lambda_module._connection_string = None
    lambda_module._db_credentials = None
    
    mock_secrets.return_value = {
        'host': 'test-host',
        'dbname': 'test-db',
        'username': 'test-user',
        'password': 'test-password'
        # port is missing
    }
    
    conn_string = lambda_module.get_connection_string()
    
    assert conn_string == "postgresql://test-user:test-password@test-host:5432/test-db"


def test_get_connection_string_error(mock_secrets):
    """Test get_connection_string handles errors"""
    lambda_module._connection_string = None
    lambda_module._db_credentials = None
    
    mock_secrets.side_effect = Exception("Secrets error")
    
    with pytest.raises(Exception, match="Secrets error"):
        lambda_module.get_connection_string()


def test_update_investigation_summary_success(mock_secrets, mock_psycopg):
    """Test update_investigation_summary executes correct query"""
    lambda_module._connection_string = "postgresql://test:test@localhost:5432/test"
    mock_psycopg['cursor'].rowcount = 1
    
    rows = lambda_module.update_investigation_summary('DV-12345', 'Test summary')
    
    assert rows == 1
    mock_psycopg['cursor'].execute.assert_called_once()
    call_args = mock_psycopg['cursor'].execute.call_args[0]
    assert 'UPDATE deviations' in call_args[0]
    assert 'SET investigation_summary = %s' in call_args[0]
    assert 'WHERE deviation_id = %s' in call_args[0]
    assert call_args[1] == ('Test summary', 'DV-12345')


def test_update_investigation_summary_no_rows(mock_secrets, mock_psycopg):
    """Test update_investigation_summary when no rows are updated"""
    lambda_module._connection_string = "postgresql://test:test@localhost:5432/test"
    mock_psycopg['cursor'].rowcount = 0
    
    rows = lambda_module.update_investigation_summary('DV-99999', 'Test summary')
    
    assert rows == 0


def test_update_investigation_summary_database_error(mock_secrets, mock_psycopg):
    """Test update_investigation_summary handles database errors"""
    lambda_module._connection_string = "postgresql://test:test@localhost:5432/test"
    mock_psycopg['cursor'].execute.side_effect = Exception("Database error")
    
    with pytest.raises(Exception, match="Database error"):
        lambda_module.update_investigation_summary('DV-12345', 'Test summary')


# ============================================================================
# CORS HEADERS TESTS
# ============================================================================

def test_cors_headers_on_success(mock_secrets, mock_psycopg, valid_event):
    """Test CORS headers are present on success response"""
    mock_psycopg['cursor'].rowcount = 1
    
    response = lambda_module.lambda_handler(valid_event, None)
    
    assert 'Access-Control-Allow-Origin' in response['headers']
    assert response['headers']['Access-Control-Allow-Origin'] == '*'
    assert response['headers']['Content-Type'] == 'application/json'


def test_cors_headers_on_validation_error(mock_secrets, mock_psycopg):
    """Test CORS headers are present on validation error"""
    event = {
        'body': json.dumps({
            'deviationId': 'invalid',
            'summary': 'Test'
        })
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert 'Access-Control-Allow-Origin' in response['headers']
    assert response['headers']['Access-Control-Allow-Origin'] == '*'


def test_cors_headers_on_not_found(mock_secrets, mock_psycopg):
    """Test CORS headers are present on not found error"""
    mock_psycopg['cursor'].rowcount = 0
    event = {
        'body': json.dumps({
            'deviationId': 'DV-99999',
            'summary': 'Test'
        })
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert 'Access-Control-Allow-Origin' in response['headers']
    assert response['headers']['Access-Control-Allow-Origin'] == '*'


def test_cors_headers_on_server_error(mock_secrets, mock_psycopg):
    """Test CORS headers are present on server error"""
    mock_psycopg['psycopg'].connect.side_effect = Exception("Error")
    event = {
        'body': json.dumps({
            'deviationId': 'DV-12345',
            'summary': 'Test'
        })
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert 'Access-Control-Allow-Origin' in response['headers']
    assert response['headers']['Access-Control-Allow-Origin'] == '*'
