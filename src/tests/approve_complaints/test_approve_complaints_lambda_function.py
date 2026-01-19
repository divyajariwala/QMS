import pytest
import json
import os
import sys
import importlib.util
from unittest.mock import Mock, patch, MagicMock

# Mock dependencies before importing
sys.modules['psycopg'] = Mock()
sys.modules['psycopg.rows'] = Mock()
sys.modules['secrets_util'] = Mock()
sys.modules['audit_logger'] = Mock()

# Load lambda_function using importlib to avoid module name conflicts
lambda_function_path = os.path.join(
    os.path.dirname(__file__), '..', '..', 'app', 'approve_complaints', 'lambda_function.py'
)
spec = importlib.util.spec_from_file_location("approve_complaints_lambda", lambda_function_path)
lambda_function = importlib.util.module_from_spec(spec)
sys.modules['approve_complaints_lambda'] = lambda_function
spec.loader.exec_module(lambda_function)


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
        """Test: Successful complaint approval with category details and workflow logging"""
        with patch.object(lambda_function, 'get_connection_string', return_value='postgresql://test:test@test:5432/test'), \
             patch.object(lambda_function, 'psycopg') as mock_psycopg, \
             patch.object(lambda_function, 'log_workflow') as mock_log_workflow, \
             patch.object(lambda_function, 'log_audit') as mock_log_audit:
            
            mock_cursor = MagicMock()
            # First fetchone for existing complaint, second for inference_results
            mock_cursor.fetchone.side_effect = [
                {'complaint_id': 'CAS-00001', 'status': 'Pending'},
                {
                    'levels': {'2': 0.9, '1': 0.1},
                    'subcategories': {'Dose confirmation': 0.9, 'Other': 0.1},
                    'crl_codes': {'CRL-000100': 0.9, 'UNASSIGNED': 0.1},
                    'units': 5,
                    'priority': 0
                }
            ]
            
            mock_conn = MagicMock()
            mock_conn.__enter__ = Mock(return_value=mock_conn)
            mock_conn.__exit__ = Mock(return_value=False)
            mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
            mock_conn.cursor.return_value.__exit__ = Mock(return_value=False)
            mock_psycopg.connect.return_value = mock_conn

            category_details = [{'label': 'Dose confirmation', 'percentage': 94.92, 'level': '2', 'crl': 'CRL-000100', 'priority': 'Low', 'unit': 5}]
            event = {
                'body': json.dumps({
                    'case_id': 'CAS-00001',
                    'caseStatus': 'pending',
                    'categoryDetails': category_details
                })
            }

            result = lambda_function.lambda_handler(event, {})

            assert result['statusCode'] == 200
            body = json.loads(result['body'])
            assert body['success'] is True
            assert body['data']['category_details'] == category_details
            
            # Verify workflow logging: COMPLAINT_APPROVED always called
            assert mock_log_workflow.call_count >= 1
            # Verify audit logging for status change + percentage change
            assert mock_log_audit.call_count >= 2

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
        """Test: Invalid caseStatus (not pending or overdue)"""
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
        assert 'Invalid status' in body['error'] and 'pending or overdue' in body['error']

    def test_approve_overdue_complaint(self):
        """Test: Successful overdue complaint approval"""
        with patch.object(lambda_function, 'get_connection_string', return_value='postgresql://test:test@test:5432/test'), \
             patch.object(lambda_function, 'psycopg') as mock_psycopg:
            
            mock_cursor = MagicMock()
            mock_cursor.fetchone.side_effect = [
                {'complaint_id': 'CAS-00002', 'status': 'Overdue'},
                None  # No inference_results
            ]
            
            mock_conn = MagicMock()
            mock_conn.__enter__ = Mock(return_value=mock_conn)
            mock_conn.__exit__ = Mock(return_value=False)
            mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
            mock_conn.cursor.return_value.__exit__ = Mock(return_value=False)
            mock_psycopg.connect.return_value = mock_conn

            category_details = [{'label': 'Test issue', 'percentage': 100.0, 'level': '1', 'crl': 'CRL-000100', 'priority': 'High', 'unit': 1}]
            event = {
                'body': json.dumps({
                    'case_id': 'CAS-00002',
                    'caseStatus': 'overdue',
                    'categoryDetails': category_details
                })
            }

            result = lambda_function.lambda_handler(event, {})

            assert result['statusCode'] == 200
            body = json.loads(result['body'])
            assert body['success'] is True
            assert body['data']['caseStatus'] == 'processed'
            assert body['data']['category_details'] == category_details

    def test_complaint_not_found(self):
        """Test: Complaint not found in database"""
        with patch.object(lambda_function, 'get_connection_string', return_value='postgresql://test:test@test:5432/test'), \
             patch.object(lambda_function, 'psycopg') as mock_psycopg:
            
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = None
            
            mock_conn = MagicMock()
            mock_conn.__enter__ = Mock(return_value=mock_conn)
            mock_conn.__exit__ = Mock(return_value=False)
            mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
            mock_conn.cursor.return_value.__exit__ = Mock(return_value=False)
            mock_psycopg.connect.return_value = mock_conn

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
        with patch.object(lambda_function, 'get_connection_string', return_value='postgresql://test:test@test:5432/test'), \
             patch.object(lambda_function, 'psycopg') as mock_psycopg:
            
            mock_psycopg.connect.side_effect = Exception("Database connection failed")

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

    def test_category_details_stored_as_is(self):
        """Test: Category details are stored as-is in processed_complaints"""
        with patch.object(lambda_function, 'get_connection_string', return_value='postgresql://test:test@test:5432/test'), \
             patch.object(lambda_function, 'psycopg') as mock_psycopg:
            
            mock_cursor = MagicMock()
            mock_cursor.fetchone.side_effect = [
                {'complaint_id': 'CAS-00001', 'status': 'Pending'},
                None  # No inference_results
            ]
            
            mock_conn = MagicMock()
            mock_conn.__enter__ = Mock(return_value=mock_conn)
            mock_conn.__exit__ = Mock(return_value=False)
            mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
            mock_conn.cursor.return_value.__exit__ = Mock(return_value=False)
            mock_psycopg.connect.return_value = mock_conn

            category_details = [
                {'label': 'Dose confirmation', 'percentage': 94.92, 'level': '2', 'crl': 'CRL-000100', 'priority': 'Low', 'unit': 5},
                {'label': 'Needle not fully extended', 'percentage': 2.88, 'level': '2', 'crl': 'CRL-000108', 'priority': 'Low', 'unit': 5}
            ]
            event = {
                'body': json.dumps({
                    'case_id': 'CAS-00001',
                    'caseStatus': 'pending',
                    'categoryDetails': category_details
                })
            }

            result = lambda_function.lambda_handler(event, {})

            assert result['statusCode'] == 200
            body = json.loads(result['body'])
            assert body['data']['category_details'] == category_details
            # Verify no UPDATE to inference_results
            execute_calls = mock_cursor.execute.call_args_list
            update_calls = [call for call in execute_calls if 'UPDATE inference_results' in str(call)]
            assert len(update_calls) == 0




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
        with patch.object(lambda_function, 'get_connection_string', return_value='postgresql://test:test@test:5432/test'), \
             patch.object(lambda_function, 'psycopg') as mock_psycopg:
            
            mock_cursor = MagicMock()
            mock_cursor.fetchone.side_effect = [
                {'complaint_id': 'CAS-00001', 'status': 'Pending'},
                None  # No inference_results
            ]
            
            mock_conn = MagicMock()
            mock_conn.__enter__ = Mock(return_value=mock_conn)
            mock_conn.__exit__ = Mock(return_value=False)
            mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
            mock_conn.cursor.return_value.__exit__ = Mock(return_value=False)
            mock_psycopg.connect.return_value = mock_conn

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

    def test_category_audit_logging(self):
        """Test: Audit logging for category detail changes and workflow step"""
        with patch.object(lambda_function, 'get_connection_string', return_value='postgresql://test:test@test:5432/test'), \
             patch.object(lambda_function, 'psycopg') as mock_psycopg, \
             patch.object(lambda_function, 'log_audit') as mock_log_audit, \
             patch.object(lambda_function, 'log_workflow') as mock_log_workflow:
            
            mock_cursor = MagicMock()
            # Mock inference_results with original values
            mock_cursor.fetchone.side_effect = [
                {'complaint_id': 'CAS-00001', 'status': 'Pending'},
                {
                    'levels': {'2': 0.9, '3': 0.1},
                    'subcategories': {'Dose confirmation': 0.9},
                    'crl_codes': {'CRL-000100': 0.9},
                    'units': 5,
                    'priority': 0
                }
            ]
            
            mock_conn = MagicMock()
            mock_conn.__enter__ = Mock(return_value=mock_conn)
            mock_conn.__exit__ = Mock(return_value=False)
            mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
            mock_conn.cursor.return_value.__exit__ = Mock(return_value=False)
            mock_psycopg.connect.return_value = mock_conn

            # Modified category details
            modified_categories = [
                {'label': 'Dose confirmation', 'percentage': 95.0, 'level': '3', 'crl': 'CRL-000100', 'priority': 'High', 'unit': 5}
            ]
            event = {
                'body': json.dumps({
                    'case_id': 'CAS-00001',
                    'caseStatus': 'pending',
                    'categoryDetails': modified_categories
                })
            }

            result = lambda_function.lambda_handler(event, {})

            assert result['statusCode'] == 200
            # Verify audit logging was called for changed fields
            audit_calls = [call[0] for call in mock_log_audit.call_args_list]
            # Should log changes for: status, percentage, level, priority
            assert len(audit_calls) >= 4
            
            # Verify workflow logging: COMPLAINT_APPROVED + CATEGORY_DETAILS_MODIFIED
            assert mock_log_workflow.call_count == 2
            # Extract workflow step names (third positional argument, index 2)
            # log_workflow(conn, case_id, step_name, ...)
            workflow_calls = [call.args[2] if len(call.args) > 2 else None for call in mock_log_workflow.call_args_list]
            assert 'COMPLAINT_APPROVED' in workflow_calls
            assert 'CATEGORY_DETAILS_MODIFIED' in workflow_calls




class TestAuditLoggingErrors:
    """Tests for audit logging error handling"""
    
    def test_audit_log_status_error(self):
        """Test: Continue processing even if status audit logging fails"""
        with patch.object(lambda_function, 'get_connection_string', return_value='postgresql://test:test@test:5432/test'), \
             patch.object(lambda_function, 'psycopg') as mock_psycopg, \
             patch.object(lambda_function, 'log_audit') as mock_log_audit, \
             patch.object(lambda_function, 'log_workflow') as mock_log_workflow:
            
            mock_cursor = MagicMock()
            mock_cursor.fetchone.side_effect = [
                {'complaint_id': 'CAS-00001', 'status': 'Pending'},
                None  # No inference_results
            ]
            
            mock_conn = MagicMock()
            mock_conn.__enter__ = Mock(return_value=mock_conn)
            mock_conn.__exit__ = Mock(return_value=False)
            mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
            mock_conn.cursor.return_value.__exit__ = Mock(return_value=False)
            mock_psycopg.connect.return_value = mock_conn
            
            # Make audit logging fail
            mock_log_audit.side_effect = Exception("Audit log failed")
            
            event = {
                'body': json.dumps({
                    'case_id': 'CAS-00001',
                    'caseStatus': 'pending',
                    'categoryDetails': []
                })
            }
            
            result = lambda_function.lambda_handler(event, {})
            
            # Should still succeed despite audit logging failure
            assert result['statusCode'] == 200
            body = json.loads(result['body'])
            assert body['success'] is True
    
    def test_workflow_log_approved_error(self):
        """Test: Continue processing even if COMPLAINT_APPROVED workflow logging fails"""
        with patch.object(lambda_function, 'get_connection_string', return_value='postgresql://test:test@test:5432/test'), \
             patch.object(lambda_function, 'psycopg') as mock_psycopg, \
             patch.object(lambda_function, 'log_workflow') as mock_log_workflow:
            
            mock_cursor = MagicMock()
            mock_cursor.fetchone.side_effect = [
                {'complaint_id': 'CAS-00001', 'status': 'Pending'},
                None
            ]
            
            mock_conn = MagicMock()
            mock_conn.__enter__ = Mock(return_value=mock_conn)
            mock_conn.__exit__ = Mock(return_value=False)
            mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
            mock_conn.cursor.return_value.__exit__ = Mock(return_value=False)
            mock_psycopg.connect.return_value = mock_conn
            
            # Make workflow logging fail
            mock_log_workflow.side_effect = Exception("Workflow log failed")
            
            event = {
                'body': json.dumps({
                    'case_id': 'CAS-00001',
                    'caseStatus': 'pending',
                    'categoryDetails': []
                })
            }
            
            result = lambda_function.lambda_handler(event, {})
            
            # Should still succeed
            assert result['statusCode'] == 200
    
    def test_workflow_log_modified_error(self):
        """Test: Continue processing even if CATEGORY_DETAILS_MODIFIED workflow logging fails"""
        with patch.object(lambda_function, 'get_connection_string', return_value='postgresql://test:test@test:5432/test'), \
             patch.object(lambda_function, 'psycopg') as mock_psycopg, \
             patch.object(lambda_function, 'log_workflow') as mock_log_workflow:
            
            mock_cursor = MagicMock()
            mock_cursor.fetchone.side_effect = [
                {'complaint_id': 'CAS-00001', 'status': 'Pending'},
                {
                    'levels': {'2': 0.9},
                    'subcategories': {'Dose confirmation': 0.9},
                    'crl_codes': {'CRL-000100': 0.9},
                    'units': 5,
                    'priority': 0
                }
            ]
            
            mock_conn = MagicMock()
            mock_conn.__enter__ = Mock(return_value=mock_conn)
            mock_conn.__exit__ = Mock(return_value=False)
            mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
            mock_conn.cursor.return_value.__exit__ = Mock(return_value=False)
            mock_psycopg.connect.return_value = mock_conn
            
            # First call succeeds (COMPLAINT_APPROVED), second fails (CATEGORY_DETAILS_MODIFIED)
            mock_log_workflow.side_effect = [None, Exception("Workflow log failed")]
            
            modified_categories = [
                {'label': 'Dose confirmation', 'percentage': 95.0, 'level': '2', 'crl': 'CRL-000100', 'priority': 'Low', 'unit': 5}
            ]
            event = {
                'body': json.dumps({
                    'case_id': 'CAS-00001',
                    'caseStatus': 'pending',
                    'categoryDetails': modified_categories
                })
            }
            
            result = lambda_function.lambda_handler(event, {})
            
            # Should still succeed
            assert result['statusCode'] == 200


class TestUserExtractionEdgeCases:
    """Tests for user extraction edge cases"""
    
    def test_get_user_cognito_sub_fallback(self):
        """Test: Use sub when email not available in Cognito claims"""
        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'sub': 'user-sub-123'
                    }
                }
            }
        }
        
        user = lambda_function._get_user_from_event(event)
        assert user == 'user-sub-123'
    
    def test_get_user_header_user_id(self):
        """Test: Use x-user-id header when x-user-email not available"""
        event = {
            'headers': {
                'x-user-id': 'user-id-456'
            }
        }
        
        user = lambda_function._get_user_from_event(event)
        assert user == 'user-id-456'
    
    def test_get_user_exception_handling(self):
        """Test: Handle exception during user extraction"""
        # Create event that will cause exception
        event = {
            'requestContext': {
                'authorizer': None  # This will cause exception when accessing ['claims']
            }
        }
        
        user = lambda_function._get_user_from_event(event)
        assert user == 'system'


class TestBodyParsing:
    """Tests for request body parsing"""
    
    def test_body_already_dict(self):
        """Test: Handle body that's already a dict (not string)"""
        with patch.object(lambda_function, 'get_connection_string', return_value='postgresql://test:test@test:5432/test'), \
             patch.object(lambda_function, 'psycopg') as mock_psycopg:
            
            mock_cursor = MagicMock()
            mock_cursor.fetchone.side_effect = [
                {'complaint_id': 'CAS-00001', 'status': 'Pending'},
                None
            ]
            
            mock_conn = MagicMock()
            mock_conn.__enter__ = Mock(return_value=mock_conn)
            mock_conn.__exit__ = Mock(return_value=False)
            mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
            mock_conn.cursor.return_value.__exit__ = Mock(return_value=False)
            mock_psycopg.connect.return_value = mock_conn
            
            # Body as dict instead of string
            event = {
                'body': {
                    'case_id': 'CAS-00001',
                    'caseStatus': 'pending',
                    'categoryDetails': []
                }
            }
            
            result = lambda_function.lambda_handler(event, {})
            
            assert result['statusCode'] == 200
            body = json.loads(result['body'])
            assert body['success'] is True


class TestInferenceResultsEdgeCases:
    """Tests for inference results edge cases"""
    
    def test_inference_results_non_dict_fields(self):
        """Test: Handle inference results with non-dict fields"""
        with patch.object(lambda_function, 'get_connection_string', return_value='postgresql://test:test@test:5432/test'), \
             patch.object(lambda_function, 'psycopg') as mock_psycopg:
            
            mock_cursor = MagicMock()
            mock_cursor.fetchone.side_effect = [
                {'complaint_id': 'CAS-00001', 'status': 'Pending'},
                {
                    'levels': 'not-a-dict',  # Invalid type
                    'subcategories': None,  # None
                    'crl_codes': [],  # Empty list
                    'units': 5,
                    'priority': 0
                }
            ]
            
            mock_conn = MagicMock()
            mock_conn.__enter__ = Mock(return_value=mock_conn)
            mock_conn.__exit__ = Mock(return_value=False)
            mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
            mock_conn.cursor.return_value.__exit__ = Mock(return_value=False)
            mock_psycopg.connect.return_value = mock_conn
            
            event = {
                'body': json.dumps({
                    'case_id': 'CAS-00001',
                    'caseStatus': 'pending',
                    'categoryDetails': []
                })
            }
            
            result = lambda_function.lambda_handler(event, {})
            
            # Should handle gracefully and still succeed
            assert result['statusCode'] == 200
    
    def test_priority_mapping(self):
        """Test: Priority value mapping to string"""
        with patch.object(lambda_function, 'get_connection_string', return_value='postgresql://test:test@test:5432/test'), \
             patch.object(lambda_function, 'psycopg') as mock_psycopg:
            
            mock_cursor = MagicMock()
            # Test different priority values
            mock_cursor.fetchone.side_effect = [
                {'complaint_id': 'CAS-00001', 'status': 'Pending'},
                {
                    'levels': {'2': 0.9},
                    'subcategories': {'Test': 0.9},
                    'crl_codes': {'CRL-000100': 0.9},
                    'units': 5,
                    'priority': 1  # Should map to "High"
                }
            ]
            
            mock_conn = MagicMock()
            mock_conn.__enter__ = Mock(return_value=mock_conn)
            mock_conn.__exit__ = Mock(return_value=False)
            mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
            mock_conn.cursor.return_value.__exit__ = Mock(return_value=False)
            mock_psycopg.connect.return_value = mock_conn
            
            event = {
                'body': json.dumps({
                    'case_id': 'CAS-00001',
                    'caseStatus': 'pending',
                    'categoryDetails': []
                })
            }
            
            result = lambda_function.lambda_handler(event, {})
            
            assert result['statusCode'] == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=lambda_function", "--cov-report=term-missing"])