"""
Unit tests for update_rca lambda function

Tests cover:
- update_rca_in_database: Database update operations
- lambda_handler: API endpoint handling with validation
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import importlib.util
from datetime import datetime

# Mock dependencies before importing lambda_function
sys.modules['secrets_util'] = MagicMock()
sys.modules['utils'] = MagicMock()

# Mock the response and utility functions
mock_utils = sys.modules['utils']
mock_utils.response = lambda status, message, data=None: {
    'statusCode': status,
    'headers': {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    },
    'body': json.dumps({
        'success': status < 400,
        'message': message,
        'data': data
    })
}
mock_utils.handle_cors_preflight = lambda: {
    'statusCode': 200,
    'headers': {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
    },
    'body': ''
}
mock_utils.parse_event_body = lambda event: json.loads(event.get('body', '{}'))

# Import the specific lambda_function module for update_rca
lambda_path = os.path.join(os.path.dirname(__file__), '../../app/update_rca/lambda_function.py')
spec = importlib.util.spec_from_file_location("update_rca_lambda", lambda_path)
lambda_function = importlib.util.module_from_spec(spec)
sys.modules['update_rca_lambda'] = lambda_function
spec.loader.exec_module(lambda_function)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_db_credentials():
    """Mock database credentials"""
    return {
        "host": "test-db.amazonaws.com",
        "port": 5432,
        "dbname": "testdb",
        "username": "testuser",
        "password": "testpass"
    }


@pytest.fixture
def sample_rca_update_data():
    """Sample RCA update data"""
    return {
        "rca_id": 123,
        "deviation_id": "DV-00001",
        "issues": "Updated issues description",
        "issues_category": "Process/Manufacturing Equipment Issue",
        "major_root_cause_category": "Design Issue",
        "major_root_cause_category_validated": "Design Issue",
        "near_root_cause": "Updated near root cause explanation",
        "near_root_cause_category": "Design Input Issue",
        "root_cause": "Updated root cause explanation",
        "root_cause_category": "Design Scope Issue",
        "updated_by": "test@example.com"
    }


@pytest.fixture
def sample_event(sample_rca_update_data):
    """Sample API Gateway event"""
    return {
        'httpMethod': 'PUT',
        'body': json.dumps(sample_rca_update_data)
    }



# ============================================================================
# TEST: update_rca_in_database
# ============================================================================

class TestUpdateRcaInDatabase:
    """Tests for update_rca_in_database function"""

    @patch('update_rca_lambda.get_db_credentials')
    @patch('update_rca_lambda.psycopg.connect')
    def test_update_rca_in_database_success(self, mock_connect, mock_get_creds, mock_db_credentials):
        """Test successful RCA update"""
        # Setup
        mock_get_creds.return_value = mock_db_credentials
        mock_cursor = MagicMock()
        
        # Mock SELECT to return existing RCA
        mock_cursor.fetchone.side_effect = [
            (123,),  # First call: SELECT check
            (123, 'DV-00001', datetime(2025, 1, 1, 10, 0, 0), datetime(2025, 1, 2, 15, 30, 0))  # Second call: UPDATE RETURNING
        ]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn

        # Execute
        result = lambda_function.update_rca_in_database(
            rca_id=123,
            deviation_id='DV-00001',
            issues='Updated issues',
            issues_category='Process Issue',
            major_category='Design Issue',
            near_cause='Near cause text',
            near_cause_category='Design Input',
            root_cause='Root cause text',
            root_cause_category='Design Scope',
            updated_by='test@example.com'
        )

        # Assert
        assert result['rca_id'] == 123
        assert result['deviation_id'] == 'DV-00001'
        assert result['updated_by'] == 'test@example.com'
        assert 'created_at' in result
        assert 'updated_at' in result
        assert mock_cursor.execute.call_count == 2  # SELECT + UPDATE
        mock_conn.commit.assert_called_once()

    @patch('update_rca_lambda.get_db_credentials')
    @patch('update_rca_lambda.psycopg.connect')
    def test_update_rca_in_database_not_found(self, mock_connect, mock_get_creds, mock_db_credentials):
        """Test RCA not found in database"""
        # Setup
        mock_get_creds.return_value = mock_db_credentials
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None  # RCA not found
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn

        # Execute & Assert
        with pytest.raises(ValueError, match="RCA with ID 999 not found"):
            lambda_function.update_rca_in_database(
                rca_id=999,
                deviation_id='DV-00001',
                issues='Issues',
                issues_category='Category',
                major_category='Major',
                near_cause='Near',
                near_cause_category='Near Cat',
                root_cause='Root',
                root_cause_category='Root Cat'
            )

    @patch('update_rca_lambda.get_db_credentials')
    @patch('update_rca_lambda.psycopg.connect')
    def test_update_rca_in_database_connection_error(self, mock_connect, mock_get_creds, mock_db_credentials):
        """Test database connection error"""
        # Setup
        mock_get_creds.return_value = mock_db_credentials
        mock_connect.side_effect = Exception("Connection failed")

        # Execute & Assert
        with pytest.raises(Exception, match="Connection failed"):
            lambda_function.update_rca_in_database(
                rca_id=123,
                deviation_id='DV-00001',
                issues='Issues',
                issues_category='Category',
                major_category='Major',
                near_cause='Near',
                near_cause_category='Near Cat',
                root_cause='Root',
                root_cause_category='Root Cat'
            )

    def test_update_rca_in_database_missing_secret_name(self):
        """Test missing DB_SECRET_NAME configuration"""
        # Setup
        original_secret = lambda_function.DB_SECRET_NAME
        lambda_function.DB_SECRET_NAME = None

        # Execute & Assert
        with pytest.raises(ValueError, match="DB_SECRET_NAME not configured"):
            lambda_function.update_rca_in_database(
                rca_id=123,
                deviation_id='DV-00001',
                issues='Issues',
                issues_category='Category',
                major_category='Major',
                near_cause='Near',
                near_cause_category='Near Cat',
                root_cause='Root',
                root_cause_category='Root Cat'
            )

        # Cleanup
        lambda_function.DB_SECRET_NAME = original_secret



# ============================================================================
# TEST: lambda_handler
# ============================================================================

class TestLambdaHandler:
    """Tests for lambda_handler function"""

    @patch('update_rca_lambda.update_rca_in_database')
    def test_lambda_handler_success(self, mock_update_rca, sample_event):
        """Test successful lambda handler execution"""
        # Setup
        mock_update_rca.return_value = {
            'rca_id': 123,
            'deviation_id': 'DV-00001',
            'created_at': '2025-01-01T10:00:00',
            'updated_at': '2025-01-02T15:30:00',
            'updated_by': 'test@example.com'
        }

        # Execute
        result = lambda_function.lambda_handler(sample_event, None)

        # Assert
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
        assert 'RCA updated successfully' in body['message']
        assert body['data']['rca_id'] == 123
        assert body['data']['deviation_id'] == 'DV-00001'
        mock_update_rca.assert_called_once()

    def test_lambda_handler_options_request(self):
        """Test CORS preflight OPTIONS request"""
        # Setup
        event = {'httpMethod': 'OPTIONS'}

        # Execute
        result = lambda_function.lambda_handler(event, None)

        # Assert
        assert result['statusCode'] == 200
        assert 'Access-Control-Allow-Origin' in result['headers']

    def test_lambda_handler_invalid_method(self):
        """Test invalid HTTP method"""
        # Setup
        event = {'httpMethod': 'POST'}

        # Execute
        result = lambda_function.lambda_handler(event, None)

        # Assert
        assert result['statusCode'] == 405
        body = json.loads(result['body'])
        assert 'Method not allowed' in body['message']

    def test_lambda_handler_missing_required_fields(self):
        """Test missing required fields"""
        # Setup
        event = {
            'httpMethod': 'PUT',
            'body': json.dumps({
                'rca_id': 123,
                'deviation_id': 'DV-00001'
                # Missing other required fields
            })
        }

        # Execute
        result = lambda_function.lambda_handler(event, None)

        # Assert
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert 'Missing required fields' in body['message']

    def test_lambda_handler_invalid_rca_id_type(self):
        """Test invalid rca_id type"""
        # Setup
        event = {
            'httpMethod': 'PUT',
            'body': json.dumps({
                'rca_id': 'not-an-integer',
                'deviation_id': 'DV-00001',
                'issues': 'Issues',
                'issues_category': 'Category',
                'major_root_cause_category': 'Major',
                'near_root_cause': 'Near',
                'near_root_cause_category': 'Near Cat',
                'root_cause': 'Root',
                'root_cause_category': 'Root Cat'
            })
        }

        # Execute
        result = lambda_function.lambda_handler(event, None)

        # Assert
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert 'rca_id must be a positive integer' in body['message']

    def test_lambda_handler_negative_rca_id(self):
        """Test negative rca_id"""
        # Setup
        event = {
            'httpMethod': 'PUT',
            'body': json.dumps({
                'rca_id': -1,
                'deviation_id': 'DV-00001',
                'issues': 'Issues',
                'issues_category': 'Category',
                'major_root_cause_category': 'Major',
                'near_root_cause': 'Near',
                'near_root_cause_category': 'Near Cat',
                'root_cause': 'Root',
                'root_cause_category': 'Root Cat'
            })
        }

        # Execute
        result = lambda_function.lambda_handler(event, None)

        # Assert
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert 'rca_id must be a positive integer' in body['message']


    def test_lambda_handler_empty_deviation_id(self):
        """Test empty deviation_id"""
        # Setup
        event = {
            'httpMethod': 'PUT',
            'body': json.dumps({
                'rca_id': 123,
                'deviation_id': '   ',
                'issues': 'Issues',
                'issues_category': 'Category',
                'major_root_cause_category': 'Major',
                'near_root_cause': 'Near',
                'near_root_cause_category': 'Near Cat',
                'root_cause': 'Root',
                'root_cause_category': 'Root Cat'
            })
        }

        # Execute
        result = lambda_function.lambda_handler(event, None)

        # Assert
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert 'deviation_id must be a non-empty string' in body['message']

    def test_lambda_handler_empty_issues(self):
        """Test empty issues field"""
        # Setup
        event = {
            'httpMethod': 'PUT',
            'body': json.dumps({
                'rca_id': 123,
                'deviation_id': 'DV-00001',
                'issues': '',
                'issues_category': 'Category',
                'major_root_cause_category': 'Major',
                'near_root_cause': 'Near',
                'near_root_cause_category': 'Near Cat',
                'root_cause': 'Root',
                'root_cause_category': 'Root Cat'
            })
        }

        # Execute
        result = lambda_function.lambda_handler(event, None)

        # Assert
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert 'issues must be a non-empty string' in body['message']

    def test_lambda_handler_empty_major_category(self):
        """Test empty major_root_cause_category"""
        # Setup
        event = {
            'httpMethod': 'PUT',
            'body': json.dumps({
                'rca_id': 123,
                'deviation_id': 'DV-00001',
                'issues': 'Issues',
                'issues_category': 'Category',
                'major_root_cause_category': '  ',
                'near_root_cause': 'Near',
                'near_root_cause_category': 'Near Cat',
                'root_cause': 'Root',
                'root_cause_category': 'Root Cat'
            })
        }

        # Execute
        result = lambda_function.lambda_handler(event, None)

        # Assert
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert 'major_root_cause_category must be a non-empty string' in body['message']

    def test_lambda_handler_empty_near_cause(self):
        """Test empty near_root_cause"""
        # Setup
        event = {
            'httpMethod': 'PUT',
            'body': json.dumps({
                'rca_id': 123,
                'deviation_id': 'DV-00001',
                'issues': 'Issues',
                'issues_category': 'Category',
                'major_root_cause_category': 'Major',
                'near_root_cause': '',
                'near_root_cause_category': 'Near Cat',
                'root_cause': 'Root',
                'root_cause_category': 'Root Cat'
            })
        }

        # Execute
        result = lambda_function.lambda_handler(event, None)

        # Assert
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert 'near_root_cause must be a non-empty string' in body['message']

    def test_lambda_handler_empty_root_cause(self):
        """Test empty root_cause"""
        # Setup
        event = {
            'httpMethod': 'PUT',
            'body': json.dumps({
                'rca_id': 123,
                'deviation_id': 'DV-00001',
                'issues': 'Issues',
                'issues_category': 'Category',
                'major_root_cause_category': 'Major',
                'near_root_cause': 'Near',
                'near_root_cause_category': 'Near Cat',
                'root_cause': '   ',
                'root_cause_category': 'Root Cat'
            })
        }

        # Execute
        result = lambda_function.lambda_handler(event, None)

        # Assert
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert 'root_cause must be a non-empty string' in body['message']

    @patch('update_rca_lambda.update_rca_in_database')
    def test_lambda_handler_rca_not_found(self, mock_update_rca, sample_event):
        """Test RCA not found in database"""
        # Setup
        mock_update_rca.side_effect = ValueError("RCA with ID 999 not found")

        # Execute
        result = lambda_function.lambda_handler(sample_event, None)

        # Assert
        assert result['statusCode'] == 404
        body = json.loads(result['body'])
        assert body['success'] is False
        assert 'not found' in body['message']

    @patch('update_rca_lambda.update_rca_in_database')
    def test_lambda_handler_database_error(self, mock_update_rca, sample_event):
        """Test database error"""
        # Setup
        mock_update_rca.side_effect = Exception("Database connection failed")

        # Execute
        result = lambda_function.lambda_handler(sample_event, None)

        # Assert
        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert body['success'] is False
        assert 'Internal server error' in body['message']

    @patch('update_rca_lambda.update_rca_in_database')
    def test_lambda_handler_uses_validated_major_category(self, mock_update_rca):
        """Test that validated major category is used when provided"""
        # Setup
        mock_update_rca.return_value = {
            'rca_id': 123,
            'deviation_id': 'DV-00001',
            'created_at': '2025-01-01T10:00:00',
            'updated_at': '2025-01-02T15:30:00',
            'updated_by': 'system'
        }
        
        event = {
            'httpMethod': 'PUT',
            'body': json.dumps({
                'rca_id': 123,
                'deviation_id': 'DV-00001',
                'issues': 'Issues',
                'issues_category': 'Category',
                'major_root_cause_category': 'Original Category',
                'major_root_cause_category_validated': 'Validated Category',
                'near_root_cause': 'Near',
                'near_root_cause_category': 'Near Cat',
                'root_cause': 'Root',
                'root_cause_category': 'Root Cat'
            })
        }

        # Execute
        lambda_function.lambda_handler(event, None)

        # Assert - should use validated category
        call_args = mock_update_rca.call_args
        assert call_args[1]['major_category'] == 'Validated Category'

    @patch('update_rca_lambda.update_rca_in_database')
    def test_lambda_handler_default_updated_by(self, mock_update_rca):
        """Test default updated_by value"""
        # Setup
        mock_update_rca.return_value = {
            'rca_id': 123,
            'deviation_id': 'DV-00001',
            'created_at': '2025-01-01T10:00:00',
            'updated_at': '2025-01-02T15:30:00',
            'updated_by': 'system'
        }
        
        event = {
            'httpMethod': 'PUT',
            'body': json.dumps({
                'rca_id': 123,
                'deviation_id': 'DV-00001',
                'issues': 'Issues',
                'issues_category': 'Category',
                'major_root_cause_category': 'Major',
                'near_root_cause': 'Near',
                'near_root_cause_category': 'Near Cat',
                'root_cause': 'Root',
                'root_cause_category': 'Root Cat'
                # No updated_by field
            })
        }

        # Execute
        lambda_function.lambda_handler(event, None)

        # Assert - should use 'system' as default
        call_args = mock_update_rca.call_args
        assert call_args[1]['updated_by'] == 'system'



# ============================================================================
# TEST: Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflow"""

    @patch('update_rca_lambda.get_db_credentials')
    @patch('update_rca_lambda.psycopg.connect')
    def test_end_to_end_rca_update(self, mock_connect, mock_get_creds, 
                                   sample_event, mock_db_credentials):
        """Test complete end-to-end RCA update flow"""
        # Setup database
        mock_get_creds.return_value = mock_db_credentials
        mock_cursor = MagicMock()
        
        # Mock SELECT and UPDATE
        mock_cursor.fetchone.side_effect = [
            (123,),  # SELECT check
            (123, 'DV-00001', datetime(2025, 1, 1, 10, 0, 0), datetime(2025, 1, 2, 15, 30, 0))  # UPDATE RETURNING
        ]
        
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn

        # Execute
        result = lambda_function.lambda_handler(sample_event, None)

        # Assert
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
        assert body['data']['rca_id'] == 123
        
        # Verify database operations
        assert mock_cursor.execute.call_count == 2  # SELECT + UPDATE
        mock_conn.commit.assert_called_once()

    @patch('update_rca_lambda.update_rca_in_database')
    def test_logging_statistics(self, mock_update_rca, sample_event, caplog):
        """Test that proper logging occurs"""
        # Setup
        mock_update_rca.return_value = {
            'rca_id': 123,
            'deviation_id': 'DV-00001',
            'created_at': '2025-01-01T10:00:00',
            'updated_at': '2025-01-02T15:30:00',
            'updated_by': 'test@example.com'
        }

        # Execute
        with caplog.at_level('INFO'):
            lambda_function.lambda_handler(sample_event, None)

        # Assert - check that important log messages are present
        log_messages = [record.message for record in caplog.records]
        assert any('Updating RCA ID: 123' in msg for msg in log_messages)
        assert any('RCA update completed successfully' in msg for msg in log_messages)


# ============================================================================
# TEST: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions"""

    @patch('update_rca_lambda.update_rca_in_database')
    def test_very_long_text_fields(self, mock_update_rca):
        """Test handling of very long text fields"""
        # Setup
        long_text = "A" * 10000  # 10k characters
        mock_update_rca.return_value = {
            'rca_id': 123,
            'deviation_id': 'DV-00001',
            'created_at': '2025-01-01T10:00:00',
            'updated_at': '2025-01-02T15:30:00',
            'updated_by': 'system'
        }
        
        event = {
            'httpMethod': 'PUT',
            'body': json.dumps({
                'rca_id': 123,
                'deviation_id': 'DV-00001',
                'issues': long_text,
                'issues_category': 'Category',
                'major_root_cause_category': 'Major',
                'near_root_cause': long_text,
                'near_root_cause_category': 'Near Cat',
                'root_cause': long_text,
                'root_cause_category': 'Root Cat'
            })
        }

        # Execute
        result = lambda_function.lambda_handler(event, None)

        # Assert
        assert result['statusCode'] == 200
        # Verify long text was passed to database function
        call_args = mock_update_rca.call_args
        assert len(call_args[1]['issues']) == 10000

    @patch('update_rca_lambda.update_rca_in_database')
    def test_special_characters_in_text(self, mock_update_rca):
        """Test handling of special characters"""
        # Setup
        special_text = 'Test with "quotes" and \'apostrophes\' & <html> tags'
        mock_update_rca.return_value = {
            'rca_id': 123,
            'deviation_id': 'DV-00001',
            'created_at': '2025-01-01T10:00:00',
            'updated_at': '2025-01-02T15:30:00',
            'updated_by': 'system'
        }
        
        event = {
            'httpMethod': 'PUT',
            'body': json.dumps({
                'rca_id': 123,
                'deviation_id': 'DV-00001',
                'issues': special_text,
                'issues_category': 'Category',
                'major_root_cause_category': 'Major',
                'near_root_cause': special_text,
                'near_root_cause_category': 'Near Cat',
                'root_cause': special_text,
                'root_cause_category': 'Root Cat'
            })
        }

        # Execute
        result = lambda_function.lambda_handler(event, None)

        # Assert
        assert result['statusCode'] == 200

    def test_invalid_json_body(self):
        """Test invalid JSON in request body"""
        # Setup
        event = {
            'httpMethod': 'PUT',
            'body': 'not valid json'
        }

        # Execute
        result = lambda_function.lambda_handler(event, None)

        # Assert - JSON decode error is caught as ValueError, returns 404
        assert result['statusCode'] == 404
        body = json.loads(result['body'])
        assert body['success'] is False

    def test_null_field_values(self):
        """Test null values in required fields"""
        # Setup
        event = {
            'httpMethod': 'PUT',
            'body': json.dumps({
                'rca_id': 123,
                'deviation_id': None,
                'issues': None,
                'issues_category': 'Category',
                'major_root_cause_category': 'Major',
                'near_root_cause': 'Near',
                'near_root_cause_category': 'Near Cat',
                'root_cause': 'Root',
                'root_cause_category': 'Root Cat'
            })
        }

        # Execute
        result = lambda_function.lambda_handler(event, None)

        # Assert
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert 'Missing required fields' in body['message']

    @patch('update_rca_lambda.update_rca_in_database')
    def test_zero_rca_id(self, mock_update_rca):
        """Test rca_id of zero"""
        # Setup
        event = {
            'httpMethod': 'PUT',
            'body': json.dumps({
                'rca_id': 0,
                'deviation_id': 'DV-00001',
                'issues': 'Issues',
                'issues_category': 'Category',
                'major_root_cause_category': 'Major',
                'near_root_cause': 'Near',
                'near_root_cause_category': 'Near Cat',
                'root_cause': 'Root',
                'root_cause_category': 'Root Cat'
            })
        }

        # Execute
        result = lambda_function.lambda_handler(event, None)

        # Assert
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert 'rca_id must be a positive integer' in body['message']
