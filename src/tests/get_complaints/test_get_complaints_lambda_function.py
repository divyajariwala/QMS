import pytest
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from datetime import date, datetime

# Mock dependencies before importing
sys.modules['psycopg'] = Mock()
sys.modules['psycopg.rows'] = Mock()
sys.modules['secrets_util'] = Mock()

# Add src directory to path for importing lambda_function
get_complaints_path = os.path.join(os.path.dirname(__file__), '..', '..', 'app', 'get_complaints')
sys.path.insert(0, get_complaints_path)

import importlib.util
spec = importlib.util.spec_from_file_location("lambda_function", os.path.join(get_complaints_path, "lambda_function.py"))
lambda_function = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lambda_function)


def create_mock_cursor():
    """Helper to create properly mocked cursor with context manager"""
    mock_cursor = Mock()
    mock_context = MagicMock()
    mock_context.__enter__.return_value = mock_cursor
    mock_context.__exit__.return_value = None
    return mock_context, mock_cursor


class TestLambdaHandler:
    """Unit tests for the main lambda_handler function"""

    @patch.object(lambda_function, 'get_db_connection')
    def test_get_single_complaint_success(self, mock_get_db):
        """Test: Successful single complaint retrieval"""
        mock_conn = Mock()
        mock_context, mock_cursor = create_mock_cursor()
        mock_conn.cursor.return_value = mock_context
        mock_get_db.return_value = mock_conn

        # Mock complaint data
        mock_cursor.fetchone.side_effect = [
            {
                'complaint_id': 'CAS-123',
                'receipt_date': date(2023, 1, 7),
                'criticality': 'High',
                'report_type': 'Spontaneous',
                'narrative_summary': 'AI summary',
                'case_type': 'AE,PC',
                'narrative': 'Test complaint narrative',
                'primary_reporter': 'John Doe',
                'primary_reporter_address': '123 Main St',
                'patient_name': 'Jane Patient',
                'physician': 'Dr. Smith',
                'drug': 'Test Drug',
                'lot_no': 'LOT123',
                'dosage': '100mg',
                'expiration_date': date(2024, 1, 1),
                'part_number': 'PN123',
                'status': 'Pending',
                'file_name': 'test.pdf',
                's3_url': 's3://bucket/test.pdf'
            }
        ]
        
        # Mock inference data
        mock_cursor.fetchall.return_value = [
            {
                'id': '1',
                'label': 'Broken Needle',
                'priority': 1,
                'crl': 'High confidence',
                'unit': 1,
                'percentage': 85.5
            }
        ]

        event = {
            'queryStringParameters': {'complaint_id': 'CAS-123'}
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['case_id'] == 'CAS-123'
        assert body['narrative'] == 'Test complaint narrative'
        assert body['criticality'] == 'High'
        assert body['caseStatus'] == 'pending'
        assert len(body['category_details']) == 1

    @patch.object(lambda_function, 'get_db_connection')
    def test_get_single_complaint_not_found(self, mock_get_db):
        """Test: Single complaint not found"""
        mock_conn = Mock()
        mock_context, mock_cursor = create_mock_cursor()
        mock_conn.cursor.return_value = mock_context
        mock_get_db.return_value = mock_conn

        # Mock no complaint found
        mock_cursor.fetchone.return_value = None

        event = {
            'queryStringParameters': {'complaint_id': 'CAS-999'}
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 404
        body = json.loads(result['body'])
        assert body['success'] is False
        assert body['error'] == 'Complaint not found'

    @patch.object(lambda_function, 'get_db_connection')
    def test_get_all_complaints_success(self, mock_get_db):
        """Test: Successful all complaints retrieval with pagination"""
        mock_conn = Mock()
        mock_context, mock_cursor = create_mock_cursor()
        mock_conn.cursor.return_value = mock_context
        mock_get_db.return_value = mock_conn

        # Mock stats data
        mock_cursor.fetchall.side_effect = [
            [
                {'stat_name': 'Pending', 'stat_value': 5},
                {'stat_name': 'Processed', 'stat_value': 3},
                {'stat_name': 'Overdue', 'stat_value': 2},
                {'stat_name': 'Avg Time', 'stat_value': 24}
            ],
            # Paginated complaints
            [
                {
                    'complaint_id': 'CAS-1',
                    'criticality': 'High',
                    'report_type': 'Spontaneous',
                    'receipt_date': date(2023, 1, 1),
                    'case_type': 'AE',
                    'status': 'Pending'
                }
            ],
            # All complaints for status grouping
            [
                {'complaint_id': 'CAS-1', 'status': 'Pending', 'criticality': 'High', 'report_type': 'Spontaneous', 'receipt_date': date(2023, 1, 1), 'case_type': 'AE'},
                {'complaint_id': 'CAS-2', 'status': 'Processed', 'criticality': 'Medium', 'report_type': 'Study', 'receipt_date': date(2023, 1, 2), 'case_type': 'PC'},
                {'complaint_id': 'CAS-3', 'status': 'Overdue', 'criticality': 'Low', 'report_type': 'Literature', 'receipt_date': date(2023, 1, 3), 'case_type': 'AE'}
            ]
        ]

        # Mock total count
        mock_cursor.fetchone.return_value = {'total': 25}

        event = {}

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert 'caseStats' in body
        assert 'caseStatus' in body
        assert 'pagination' in body
        assert 'complaints' in body
        assert body['pagination']['total_items'] == 25
        assert body['pagination']['items_per_page'] == 15
        assert body['pagination']['current_page'] == 1

    @patch.object(lambda_function, 'get_db_connection')
    def test_lambda_handler_exception(self, mock_get_db):
        """Test: Lambda handler exception handling"""
        mock_get_db.side_effect = Exception("Database connection failed")

        event = {}

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert body['success'] is False
        assert body['error'] == 'Internal server error'


class TestGetAllComplaints:
    """Tests for get_all_complaints function"""

    def test_get_all_complaints_with_data(self):
        """Test: Get all complaints with various statuses"""
        mock_conn = Mock()
        mock_context, mock_cursor = create_mock_cursor()
        mock_conn.cursor.return_value = mock_context

        # Mock stats and complaints data
        mock_cursor.fetchall.side_effect = [
            [
                {'stat_name': 'Pending', 'stat_value': 2},
                {'stat_name': 'Processed', 'stat_value': 1},
                {'stat_name': 'Overdue', 'stat_value': 1}
            ],
            # Paginated complaints
            [
                {'complaint_id': 'CAS-1', 'criticality': 'High', 'report_type': 'Spontaneous', 'receipt_date': date(2023, 1, 1), 'case_type': 'AE', 'status': 'Pending'}
            ],
            # All complaints for grouping
            [
                {'complaint_id': 'CAS-1', 'status': 'Pending', 'criticality': 'High', 'report_type': 'Spontaneous', 'receipt_date': date(2023, 1, 1), 'case_type': 'AE'},
                {'complaint_id': 'CAS-2', 'status': 'Processed', 'criticality': 'Medium', 'report_type': 'Study', 'receipt_date': date(2023, 1, 2), 'case_type': 'PC'},
                {'complaint_id': 'CAS-3', 'status': 'Overdue', 'criticality': 'Low', 'report_type': 'Literature', 'receipt_date': date(2023, 1, 3), 'case_type': 'AE'}
            ]
        ]

        mock_cursor.fetchone.return_value = {'total': 15}

        result = lambda_function.get_all_complaints(mock_conn, 1, None)

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        
        # Check statistics
        stats = body['caseStats']
        assert stats['total_complaints'] == 3
        assert stats['pending'] == 2
        assert stats['processed'] == 1
        assert stats['overdue'] == 1

        # Check pagination
        pagination = body['pagination']
        assert pagination['current_page'] == 1
        assert pagination['total_items'] == 15
        assert pagination['items_per_page'] == 15


class TestUtilityFunctions:
    """Tests for utility functions"""

    def test_group_by_status_comprehensive(self):
        """Test: Group complaints by status comprehensively"""
        complaints = [
            {
                'status': 'Pending',
                'complaint_id': 'CAS-1',
                'criticality': 'High',
                'report_type': 'Spontaneous',
                'receipt_date': date(2023, 1, 1),
                'case_type': 'AE'
            },
            {
                'status': 'Processed',
                'complaint_id': 'CAS-2',
                'criticality': 'Medium',
                'report_type': 'Study',
                'receipt_date': date(2023, 1, 2),
                'case_type': 'PC'
            },
            {
                'status': 'Overdue',
                'complaint_id': 'CAS-3',
                'criticality': 'Low',
                'report_type': 'Literature',
                'receipt_date': date(2023, 1, 3),
                'case_type': 'AE'
            }
        ]

        result = lambda_function._group_by_status(complaints)

        assert len(result['pending']) == 1
        assert len(result['processed']) == 1
        assert len(result['overdue']) == 1
        
        # Check field mapping
        pending_item = result['pending'][0]
        assert pending_item['case_id'] == 'CAS-1'
        assert pending_item['criticality'] == 'High'
        assert pending_item['case_type'] == ['AE']

    def test_get_cors_headers(self):
        """Test: CORS headers function"""
        headers = lambda_function._get_cors_headers()

        assert headers['Content-Type'] == 'application/json'
        assert headers['Access-Control-Allow-Origin'] == '*'
        assert headers['Access-Control-Allow-Methods'] == 'GET, OPTIONS'
        assert 'Authorization' in headers['Access-Control-Allow-Headers']

    @patch.object(lambda_function, 'get_secret')
    def test_get_db_connection_success(self, mock_get_secret):
        """Test: Successful database connection"""
        mock_get_secret.return_value = {
            'host': 'localhost',
            'port': 5432,
            'dbname': 'testdb',
            'username': 'testuser',
            'password': 'testpass'
        }

        with patch('psycopg.connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value = mock_conn

            result = lambda_function.get_db_connection()

            assert result == mock_conn
            mock_connect.assert_called_once_with(
                host='localhost',
                port=5432,
                dbname='testdb',
                user='testuser',
                password='testpass'
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])