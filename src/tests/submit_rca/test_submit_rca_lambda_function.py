"""
Unit tests for submit_rca Lambda function
"""
import json
import sys
from unittest.mock import MagicMock, patch, Mock
import pytest
import importlib.util
from datetime import datetime, timezone

# Mock dependencies before importing the lambda module
mock_utils = MagicMock()
mock_secrets_util = MagicMock()
mock_audit_logger = MagicMock()

sys.modules['utils'] = mock_utils
sys.modules['secrets_util'] = mock_secrets_util
sys.modules['audit_logger'] = mock_audit_logger

# Load the lambda_function module
spec = importlib.util.spec_from_file_location(
    "submit_rca_lambda",
    "src/app/submit_rca/lambda_function.py"
)
lambda_module = importlib.util.module_from_spec(spec)
sys.modules['submit_rca_lambda'] = lambda_module
spec.loader.exec_module(lambda_module)


@pytest.fixture(autouse=True)
def setup_environment(monkeypatch):
    """Set up environment variables for all tests"""
    monkeypatch.setenv('env', 'test')
    monkeypatch.setenv('aws_region', 'us-east-1')
    monkeypatch.setenv('db_secret_base_name', 'test-db-secret')


@pytest.fixture
def mock_db_credentials():
    """Mock database credentials"""
    return {
        'host': 'test-host',
        'port': 5432,
        'dbname': 'test-db',
        'username': 'test-user',
        'password': 'test-password'
    }


@pytest.fixture
def mock_psycopg():
    """Mock psycopg connection and cursor"""
    with patch('submit_rca_lambda.psycopg') as mock_pg:
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
def mock_get_db_credentials(mock_db_credentials):
    """Mock get_db_credentials function"""
    with patch('submit_rca_lambda.get_db_credentials') as mock:
        mock.return_value = mock_db_credentials
        yield mock


@pytest.fixture
def mock_log_functions():
    """Mock audit logger functions"""
    with patch('submit_rca_lambda.log_deviation_workflow') as mock_workflow, \
         patch('submit_rca_lambda.log_deviation_audit') as mock_audit:
        yield {
            'workflow': mock_workflow,
            'audit': mock_audit
        }


@pytest.fixture
def mock_response():
    """Mock response function"""
    def response_func(status_code, message, data=None):
        return {
            'statusCode': status_code,
            'body': json.dumps({'message': message, 'data': data} if data else {'message': message})
        }
    
    with patch('submit_rca_lambda.response', side_effect=response_func):
        yield


@pytest.fixture
def mock_handle_cors():
    """Mock handle_cors_preflight function"""
    with patch('submit_rca_lambda.handle_cors_preflight') as mock:
        mock.return_value = {'statusCode': 200, 'headers': {'Access-Control-Allow-Origin': '*'}}
        yield mock


@pytest.fixture
def mock_parse_event_body():
    """Mock parse_event_body function"""
    def parse_func(event):
        body = event.get('body', '{}')
        if isinstance(body, str):
            return json.loads(body)
        return body
    
    with patch('submit_rca_lambda.parse_event_body', side_effect=parse_func):
        yield


@pytest.fixture
def valid_single_rca():
    """Valid single RCA data"""
    return {
        'deviation_id': 'DV-12345',
        'problem_category': 'Company Personnel Issue',
        'problem_category_validated': 'Problem category explanation text',
        'major_root_cause_category': 'Personnel Issues',
        'major_root_cause_category_validated': 'Major category explanation',
        'near_root_cause': 'Near root cause text',
        'near_root_cause_category': 'Training/Personnel Qualification Issue',
        'root_cause': 'Root cause text',
        'root_cause_category': 'Training Not Performed',
        'is_ai_generated': True,
        'isAdded': False,
        'isEdited': False,
        'created_by': 'test@example.com'
    }


@pytest.fixture
def valid_batch_rcas():
    """Valid batch of RCAs"""
    return [
        {
            'deviation_id': 'DV-12345',
            'problem_category': 'Company Personnel Issue',
            'problem_category_validated': 'Problem 1',
            'major_root_cause_category': 'Personnel Issues',
            'major_root_cause_category_validated': 'Major 1',
            'near_root_cause': 'Near cause 1',
            'near_root_cause_category': 'Training Issue',
            'root_cause': 'Root cause 1',
            'root_cause_category': 'Training Not Performed',
            'is_ai_generated': True,
            'created_by': 'test@example.com'
        },
        {
            'deviation_id': 'DV-12345',
            'problem_category': 'Process Issue',
            'problem_category_validated': 'Problem 2',
            'major_root_cause_category': 'Equipment Issues',
            'major_root_cause_category_validated': 'Major 2',
            'near_root_cause': 'Near cause 2',
            'near_root_cause_category': 'Equipment Failure',
            'root_cause': 'Root cause 2',
            'root_cause_category': 'Equipment Malfunction',
            'is_ai_generated': False,
            'isAdded': True
        }
    ]


# ============================================================================
# SUCCESS CASES - SINGLE RCA
# ============================================================================

def test_successful_single_rca_submission(mock_psycopg, mock_get_db_credentials, 
                                          mock_log_functions, mock_response, 
                                          mock_parse_event_body, valid_single_rca):
    """Test successful submission of single RCA"""
    # Setup cursor mock to return RCA ID and timestamps
    mock_psycopg['cursor'].fetchone.side_effect = [
        (123, datetime(2025, 1, 19, 10, 30, 0), datetime(2025, 1, 19, 10, 30, 0)),  # RCA insert
        ('DV-12345', True, True, datetime(2025, 1, 19, 10, 30, 0))  # Deviation update
    ]
    
    event = {
        'httpMethod': 'POST',
        'body': json.dumps(valid_single_rca)
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['message'] == 'RCA saved successfully'
    assert body['data']['rca_id'] == 123
    assert body['data']['deviation_id'] == 'DV-12345'
    
    # Verify database calls
    assert mock_psycopg['cursor'].execute.call_count == 2  # INSERT + UPDATE
    mock_psycopg['connection'].commit.assert_called_once()


def test_successful_single_rca_with_default_created_by(mock_psycopg, mock_get_db_credentials,
                                                        mock_log_functions, mock_response,
                                                        mock_parse_event_body, valid_single_rca):
    """Test single RCA submission with default created_by"""
    del valid_single_rca['created_by']
    
    mock_psycopg['cursor'].fetchone.side_effect = [
        (124, datetime(2025, 1, 19, 10, 30, 0), datetime(2025, 1, 19, 10, 30, 0)),
        ('DV-12345', True, True, datetime(2025, 1, 19, 10, 30, 0))
    ]
    
    event = {
        'httpMethod': 'POST',
        'body': json.dumps(valid_single_rca)
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 200
    # Verify 'system' was used as default
    call_args = mock_psycopg['cursor'].execute.call_args_list[0][0]
    assert call_args[1][-1] == 'system'  # created_by parameter


# ============================================================================
# SUCCESS CASES - BATCH RCA
# ============================================================================

def test_successful_batch_rca_submission(mock_psycopg, mock_get_db_credentials,
                                         mock_log_functions, mock_response,
                                         mock_parse_event_body, valid_batch_rcas):
    """Test successful submission of batch RCAs"""
    # Setup cursor mock to return RCA IDs and timestamps
    mock_psycopg['cursor'].fetchone.side_effect = [
        (201, datetime(2025, 1, 19, 10, 30, 0), datetime(2025, 1, 19, 10, 30, 0)),  # RCA 1
        (202, datetime(2025, 1, 19, 10, 30, 0), datetime(2025, 1, 19, 10, 30, 0)),  # RCA 2
        ('DV-12345', True, True, datetime(2025, 1, 19, 10, 30, 0))  # Deviation update
    ]
    
    event = {
        'httpMethod': 'POST',
        'body': json.dumps(valid_batch_rcas)
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['message'] == '2 RCAs saved successfully'
    assert body['data']['saved_count'] == 2
    assert len(body['data']['rcas']) == 2
    
    # Verify database calls (2 INSERTs + 1 UPDATE)
    assert mock_psycopg['cursor'].execute.call_count == 3
    mock_psycopg['connection'].commit.assert_called_once()


# ============================================================================
# VALIDATION ERROR CASES - SINGLE RCA
# ============================================================================

def test_missing_deviation_id(mock_response, mock_parse_event_body, valid_single_rca):
    """Test error when deviation_id is missing"""
    del valid_single_rca['deviation_id']
    
    event = {
        'httpMethod': 'POST',
        'body': json.dumps(valid_single_rca)
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'deviation_id' in body['message']


def test_missing_problem_category(mock_response, mock_parse_event_body, valid_single_rca):
    """Test error when problem_category is missing"""
    del valid_single_rca['problem_category']
    
    event = {
        'httpMethod': 'POST',
        'body': json.dumps(valid_single_rca)
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'problem_category' in body['message']


def test_empty_problem_category(mock_response, mock_parse_event_body, valid_single_rca):
    """Test error when problem_category is empty"""
    valid_single_rca['problem_category'] = '   '  # Whitespace only
    
    event = {
        'httpMethod': 'POST',
        'body': json.dumps(valid_single_rca)
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'problem_category must be a non-empty string' in body['message']


def test_invalid_problem_category_type(mock_response, mock_parse_event_body, valid_single_rca):
    """Test error when problem_category is not a string"""
    valid_single_rca['problem_category'] = 123
    
    event = {
        'httpMethod': 'POST',
        'body': json.dumps(valid_single_rca)
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 400


def test_empty_major_root_cause_category(mock_response, mock_parse_event_body, valid_single_rca):
    """Test error when major_root_cause_category is empty"""
    valid_single_rca['major_root_cause_category'] = '   '
    
    event = {
        'httpMethod': 'POST',
        'body': json.dumps(valid_single_rca)
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 400


def test_empty_near_root_cause(mock_response, mock_parse_event_body, valid_single_rca):
    """Test error when near_root_cause is empty"""
    valid_single_rca['near_root_cause'] = ''
    
    event = {
        'httpMethod': 'POST',
        'body': json.dumps(valid_single_rca)
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 400


def test_empty_root_cause(mock_response, mock_parse_event_body, valid_single_rca):
    """Test error when root_cause is empty"""
    valid_single_rca['root_cause'] = ''
    
    event = {
        'httpMethod': 'POST',
        'body': json.dumps(valid_single_rca)
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 400


# ============================================================================
# VALIDATION ERROR CASES - BATCH RCA
# ============================================================================

def test_empty_batch_array(mock_response, mock_parse_event_body):
    """Test error when batch array is empty"""
    event = {
        'httpMethod': 'POST',
        'body': json.dumps([])
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'empty array' in body['message']


def test_batch_with_non_dict_item(mock_response, mock_parse_event_body):
    """Test error when batch contains non-dict item"""
    event = {
        'httpMethod': 'POST',
        'body': json.dumps(['invalid', 'items'])
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'must be an object' in body['message']


def test_batch_with_missing_field_in_item(mock_response, mock_parse_event_body, valid_batch_rcas):
    """Test error when batch item is missing required field"""
    del valid_batch_rcas[1]['root_cause']
    
    event = {
        'httpMethod': 'POST',
        'body': json.dumps(valid_batch_rcas)
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'index 1' in body['message']
    assert 'root_cause' in body['message']


def test_batch_with_invalid_field_type(mock_response, mock_parse_event_body, valid_batch_rcas):
    """Test error when batch item has invalid field type"""
    valid_batch_rcas[0]['problem_category'] = 123
    
    event = {
        'httpMethod': 'POST',
        'body': json.dumps(valid_batch_rcas)
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'index 0' in body['message']


# ============================================================================
# HTTP METHOD TESTS
# ============================================================================

def test_options_request(mock_handle_cors):
    """Test OPTIONS request for CORS preflight"""
    event = {
        'httpMethod': 'OPTIONS'
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 200
    mock_handle_cors.assert_called_once()


def test_invalid_http_method(mock_response):
    """Test error with invalid HTTP method"""
    event = {
        'httpMethod': 'GET'
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 405
    body = json.loads(response['body'])
    assert 'Method not allowed' in body['message']


# ============================================================================
# DATABASE ERROR CASES
# ============================================================================

def test_database_connection_error(mock_psycopg, mock_get_db_credentials,
                                   mock_response, mock_parse_event_body, valid_single_rca):
    """Test error when database connection fails"""
    mock_psycopg['psycopg'].connect.side_effect = Exception("Connection failed")
    
    event = {
        'httpMethod': 'POST',
        'body': json.dumps(valid_single_rca)
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 500


def test_database_insert_error(mock_psycopg, mock_get_db_credentials, mock_log_functions,
                               mock_response, mock_parse_event_body, valid_single_rca):
    """Test error when database insert fails"""
    mock_psycopg['cursor'].execute.side_effect = Exception("Insert failed")
    
    event = {
        'httpMethod': 'POST',
        'body': json.dumps(valid_single_rca)
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 500


def test_get_db_credentials_error(mock_get_db_credentials, mock_response,
                                  mock_parse_event_body, valid_single_rca):
    """Test error when getting database credentials fails"""
    mock_get_db_credentials.side_effect = Exception("Credentials error")
    
    event = {
        'httpMethod': 'POST',
        'body': json.dumps(valid_single_rca)
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 500


# ============================================================================
# AUDIT LOGGING TESTS
# ============================================================================

def test_audit_log_for_added_rca(mock_psycopg, mock_get_db_credentials,
                                 mock_log_functions, mock_response,
                                 mock_parse_event_body, valid_single_rca):
    """Test audit log is created for added RCA"""
    valid_single_rca['isAdded'] = True
    valid_single_rca['isEdited'] = False
    
    mock_psycopg['cursor'].fetchone.side_effect = [
        (125, datetime(2025, 1, 19, 10, 30, 0), datetime(2025, 1, 19, 10, 30, 0)),
        ('DV-12345', True, True, datetime(2025, 1, 19, 10, 30, 0))
    ]
    
    event = {
        'httpMethod': 'POST',
        'body': json.dumps(valid_single_rca)
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 200
    # Verify audit log was called for ADDED
    mock_log_functions['audit'].assert_called()
    call_args = mock_log_functions['audit'].call_args
    assert call_args[1]['audit_type'] == 'ADDED'


def test_audit_log_for_edited_rca(mock_psycopg, mock_get_db_credentials,
                                  mock_log_functions, mock_response,
                                  mock_parse_event_body, valid_single_rca):
    """Test audit log is created for edited RCA"""
    valid_single_rca['isAdded'] = False
    valid_single_rca['isEdited'] = True
    
    mock_psycopg['cursor'].fetchone.side_effect = [
        (126, datetime(2025, 1, 19, 10, 30, 0), datetime(2025, 1, 19, 10, 30, 0)),
        ('DV-12345', True, True, datetime(2025, 1, 19, 10, 30, 0))
    ]
    
    event = {
        'httpMethod': 'POST',
        'body': json.dumps(valid_single_rca)
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 200
    # Verify audit log was called for EDITED
    mock_log_functions['audit'].assert_called()
    call_args = mock_log_functions['audit'].call_args
    assert call_args[1]['audit_type'] == 'EDITED'


def test_workflow_log_on_success(mock_psycopg, mock_get_db_credentials,
                                 mock_log_functions, mock_response,
                                 mock_parse_event_body, valid_single_rca):
    """Test workflow log is created on successful submission"""
    mock_psycopg['cursor'].fetchone.side_effect = [
        (127, datetime(2025, 1, 19, 10, 30, 0), datetime(2025, 1, 19, 10, 30, 0)),
        ('DV-12345', True, True, datetime(2025, 1, 19, 10, 30, 0))
    ]
    
    event = {
        'httpMethod': 'POST',
        'body': json.dumps(valid_single_rca)
    }
    
    response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 200
    # Verify workflow log was called
    mock_log_functions['workflow'].assert_called()
    call_args = mock_log_functions['workflow'].call_args
    assert call_args[1]['step'] == 'RCA_SUBMITTED'


# ============================================================================
# HELPER FUNCTION TESTS
# ============================================================================

def test_save_rca_audit_log_added(mock_psycopg, mock_log_functions):
    """Test save_rca_audit_log for added RCA"""
    rca = {
        'problem_category': 'Test Category',
        'major_root_cause_category': 'Test Major',
        'root_cause_category': 'Test Root',
        'near_root_cause_category': 'Test Near',
        'isAdded': True,
        'isEdited': False
    }
    
    lambda_module.save_rca_audit_log(mock_psycopg['connection'], rca, 'DV-12345')
    
    mock_log_functions['audit'].assert_called_once()
    call_args = mock_log_functions['audit'].call_args
    assert call_args[1]['audit_type'] == 'ADDED'
    assert call_args[1]['deviation_id'] == 'DV-12345'


def test_save_rca_audit_log_edited(mock_psycopg, mock_log_functions):
    """Test save_rca_audit_log for edited RCA"""
    rca = {
        'problem_category': 'Test Category',
        'isAdded': False,
        'isEdited': True
    }
    
    lambda_module.save_rca_audit_log(mock_psycopg['connection'], rca, 'DV-12345')
    
    mock_log_functions['audit'].assert_called_once()
    call_args = mock_log_functions['audit'].call_args
    assert call_args[1]['audit_type'] == 'EDITED'


def test_save_rca_audit_log_no_flags(mock_psycopg, mock_log_functions):
    """Test save_rca_audit_log when no flags are set"""
    rca = {
        'problem_category': 'Test Category',
        'isAdded': False,
        'isEdited': False
    }
    
    lambda_module.save_rca_audit_log(mock_psycopg['connection'], rca, 'DV-12345')
    
    # Should not call audit log
    mock_log_functions['audit'].assert_not_called()
