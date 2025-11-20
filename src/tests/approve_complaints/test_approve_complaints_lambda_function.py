import pytest
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Mock dependencies before importing
sys.modules['psycopg'] = Mock()
sys.modules['psycopg.rows'] = Mock()
sys.modules['secrets_util'] = Mock()

# Add src directory to path for importing lambda_function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'app', 'approve_complaints'))
import lambda_function


@pytest.fixture(autouse=True)
def mock_all_external_dependencies():
    """Auto-mock all external dependencies for ALL tests."""
    # Reset cache before each test
    lambda_function._db_credentials = None
    lambda_function._connection_string = None
    
    with patch.object(lambda_function, 'get_secret') as mock_get_secret, \
         patch.object(lambda_function, 'get_connection_string') as mock_get_conn_str:
        
        # Mock get_secret to return fake credentials
        mock_get_secret.return_value = {
            'host': 'test-host',
            'port': 5432,
            'dbname': 'test-db',
            'username': 'test-user',
            'password': 'test-pass'
        }
        
        # Mock connection string
        mock_get_conn_str.return_value = 'postgresql://test:test@test:5432/test'

        yield


class TestLambdaHandler:
    """Unit tests for the main lambda_handler function"""

    def test_approve_complaint_success(self):
        """Test: Successful complaint approval with category details"""
        with patch('lambda_function.psycopg.connect') as mock_connect:
            mock_cursor = MagicMock()
            mock_cursor.fetchone.side_effect = [
                {'complaint_id': 'CAS-00001', 'status': 'Pending'},
                {'inference_id': 5, 'subcategories': {"Dose confirmation": 0.9492}, 'crl_codes': {"CRL-000100": 0.9492}, 'units': {"Dose confirmation": 5}, 'final_level': '2', 'priority': 0}
            ]
            
            mock_conn = MagicMock()
            mock_conn.__enter__ = Mock(return_value=mock_conn)
            mock_conn.__exit__ = Mock(return_value=False)
            mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
            mock_conn.cursor.return_value.__exit__ = Mock(return_value=False)
            mock_connect.return_value = mock_conn

            event = {
                'body': json.dumps({
                    'case_id': 'CAS-00001',
                    'caseStatus': 'pending',
                    'categoryDetails': [{'label': 'Dose confirmation', 'percentage': 94.92, 'level': '2', 'crl': 'CRL-000100', 'priority': 0, 'unit': 5}]
                })
            }

            result = lambda_function.lambda_handler(event, {})

            assert result['statusCode'] == 200
            body = json.loads(result['body'])
            assert body['success'] is True
            assert body['data']['category_details'][0]['unit'] == 5

    def test_missing_case_id(self):
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

    def test_invalid_status(self):
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

    def test_complaint_not_found(self):
        """Test: Complaint not found in database"""
        with patch('lambda_function.psycopg.connect') as mock_connect:
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = None
            
            mock_conn = MagicMock()
            mock_conn.__enter__ = Mock(return_value=mock_conn)
            mock_conn.__exit__ = Mock(return_value=False)
            mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
            mock_conn.cursor.return_value.__exit__ = Mock(return_value=False)
            mock_connect.return_value = mock_conn

            event = {
                'body': json.dumps({
                    'case_id': 'NONEXISTENT',
                    'caseStatus': 'pending',
                    'categoryDetails': []
                })
            }

            result = lambda_function.lambda_handler(event, {})

            assert result['statusCode'] == 404
            body = json.loads(result['body'])
            assert body['success'] is False
            assert 'not found' in body['error']

    def test_database_error(self):
        """Test: Database error during connection"""
        with patch('lambda_function.psycopg.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database connection failed")

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

    def test_category_details_update(self):
        """Test: Category details are updated in inference_results"""
        with patch('lambda_function.psycopg.connect') as mock_connect:
            mock_cursor = MagicMock()
            mock_cursor.fetchone.side_effect = [
                {'complaint_id': 'CAS-00001', 'status': 'Pending'},
                {'subcategories': {"Dose confirmation": 0.9492, "Needle not fully extended": 0.0288}, 'crl_codes': {"CRL-000100": 0.9492, "CRL-000108": 0.0288}, 'units': {"Dose confirmation": 5, "Needle not fully extended": 2}, 'final_level': '2', 'priority': 0}
            ]
            
            mock_conn = MagicMock()
            mock_conn.__enter__ = Mock(return_value=mock_conn)
            mock_conn.__exit__ = Mock(return_value=False)
            mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
            mock_conn.cursor.return_value.__exit__ = Mock(return_value=False)
            mock_connect.return_value = mock_conn

            event = {
                'body': json.dumps({
                    'case_id': 'CAS-00001',
                    'caseStatus': 'pending',
                    'categoryDetails': [
                        {'label': 'Dose confirmation', 'percentage': 94.92, 'level': '2', 'crl': 'CRL-000100', 'priority': 0, 'unit': 5},
                        {'label': 'Needle not fully extended', 'percentage': 2.88, 'level': '2', 'crl': 'CRL-000108', 'priority': 0, 'unit': 2}
                    ]
                })
            }

            result = lambda_function.lambda_handler(event, {})

            assert result['statusCode'] == 200
            body = json.loads(result['body'])
            assert len(body['data']['category_details']) == 2
            assert body['data']['category_details'][0]['unit'] == 5
            assert body['data']['category_details'][1]['unit'] == 2
            # Verify inference_results UPDATE was called
            execute_calls = mock_cursor.execute.call_args_list
            update_calls = [call for call in execute_calls if 'UPDATE inference_results' in str(call)]
            assert len(update_calls) == 1




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





class TestEdgeCases:
    """Tests for edge cases"""

    def test_empty_case_id(self):
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

    def test_case_insensitive_status(self):
        """Test: Case insensitive status check - PENDING should work"""
        with patch('lambda_function.psycopg.connect') as mock_connect:
            mock_cursor = MagicMock()
            mock_cursor.fetchone.side_effect = [
                {'complaint_id': 'CAS-00001', 'status': 'Pending'},
                {'subcategories': {}, 'crl_codes': {}, 'units': {}, 'final_level': '2', 'priority': 0}
            ]
            
            mock_conn = MagicMock()
            mock_conn.__enter__ = Mock(return_value=mock_conn)
            mock_conn.__exit__ = Mock(return_value=False)
            mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
            mock_conn.cursor.return_value.__exit__ = Mock(return_value=False)
            mock_connect.return_value = mock_conn

            event = {
                'body': json.dumps({
                    'case_id': 'CAS-00001',
                    'caseStatus': 'PENDING',
                    'categoryDetails': []
                })
            }

            result = lambda_function.lambda_handler(event, {})

            assert result['statusCode'] == 200
            body = json.loads(result['body'])
            assert body['success'] is True




if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=lambda_function", "--cov-report=term-missing"])