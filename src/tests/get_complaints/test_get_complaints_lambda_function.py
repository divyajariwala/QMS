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
        # Mock inference data from new inference_results table
        mock_cursor.fetchone.side_effect = [
            {
                'complaint_id': 'CAS-123',
                'receipt_date': date(2023, 1, 7),
                'criticality': 'High',
                'report_type': 'Spontaneous',
                'narrative_summary': 'AI generated summary of the complaint narrative in 100-150 words',
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
                'text_extracted': True,
                'created_at': datetime(2023, 1, 7, 10, 0, 0),
                'file_name': 'test.pdf',
                's3_url': 's3://bucket/test.pdf'
            },
            {
                'inference_id': 5,
                'complaint_id': 'CAS-123',
                'levels': {"1": 0.11, "2": 0.81},
                'subcategories': {"Broken Needle": 0.855, "Dose confirmation": 0.145},
                'crl_codes': {"CRL-000100": 0.855, "CRL-000102": 0.145},
                'units': 3,
                'final_level': '2',
                'priority': 1,
                'priority_reason': 'High priority issue',
                'priority_summary': 'Critical safety concern'
            }
        ]

        event = {
            'queryStringParameters': {'complaint_id': 'CAS-123'}
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['case_id'] == 'CAS-123'
        assert body['created_at'] == '2023-01-07T10:00:00'
        assert body['narrative'] == 'Test complaint narrative'
        assert body['ai_summary'] == 'AI generated summary of the complaint narrative in 100-150 words'
        assert body['criticality'] == 'High'
        assert body['caseStatus'] == 'pending'
        assert body['text_extracted'] is True
        assert body['complaintClassified'] is True
        assert len(body['category_details']) == 2

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
    def test_get_single_complaint_no_inference(self, mock_get_db):
        """Test: Complaint found but no inference results yet"""
        mock_conn = Mock()
        mock_context, mock_cursor = create_mock_cursor()
        mock_conn.cursor.return_value = mock_context
        mock_get_db.return_value = mock_conn

        # Mock complaint data without inference results
        mock_cursor.fetchone.side_effect = [
            {
                'complaint_id': 'CAS-456',
                'receipt_date': date(2023, 1, 7),
                'criticality': 'Medium',
                'report_type': 'Spontaneous',
                'narrative_summary': '',
                'case_type': 'AE',
                'narrative': 'Test narrative',
                'primary_reporter': 'John Doe',
                'primary_reporter_address': '123 Main St',
                'patient_name': 'Jane Patient',
                'physician': 'Dr. Smith',
                'drug': 'Test Drug',
                'lot_no': 'LOT456',
                'dosage': '50mg',
                'expiration_date': date(2024, 6, 1),
                'part_number': 'PN456',
                'status': 'Pending',
                'text_extracted': True,
                'created_at': datetime(2023, 1, 7, 11, 0, 0),
                'file_name': 'test2.pdf',
                's3_url': 's3://bucket/test2.pdf'
            },
            None  # No inference result
        ]

        event = {
            'queryStringParameters': {'complaint_id': 'CAS-456'}
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['case_id'] == 'CAS-456'
        assert body['created_at'] == '2023-01-07T11:00:00'
        assert body['complaintClassified'] is False
        assert len(body['category_details']) == 0

    @patch.object(lambda_function, 'get_db_connection')
    def test_get_all_complaints_success(self, mock_get_db):
        """Test: Successful all complaints retrieval with pagination (no filter)"""
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
                    'status': 'Pending',
                    'text_extracted': True,
                    'created_at': datetime(2023, 1, 1, 10, 0, 0)
                }
            ],
            # All complaints for status grouping (no filter)
            [
                {'complaint_id': 'CAS-1', 'status': 'Pending', 'criticality': 'High', 'report_type': 'Spontaneous', 'receipt_date': date(2023, 1, 1), 'case_type': 'AE', 'text_extracted': True, 'created_at': datetime(2023, 1, 1, 10, 0, 0)},
                {'complaint_id': 'CAS-2', 'status': 'Processed', 'criticality': 'Medium', 'report_type': 'Study', 'receipt_date': date(2023, 1, 2), 'case_type': 'PC', 'text_extracted': False, 'created_at': datetime(2023, 1, 2, 11, 0, 0)},
                {'complaint_id': 'CAS-3', 'status': 'Overdue', 'criticality': 'Low', 'report_type': 'Literature', 'receipt_date': date(2023, 1, 3), 'case_type': 'AE', 'text_extracted': True, 'created_at': datetime(2023, 1, 3, 12, 0, 0)}
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
        # Verify all status groups have data when no filter
        assert len(body['caseStatus']['pending']) == 1
        assert len(body['caseStatus']['processed']) == 1
        assert len(body['caseStatus']['overdue']) == 1

    @patch.object(lambda_function, 'get_db_connection')
    def test_get_all_complaints_with_status_filter(self, mock_get_db):
        """Test: Get complaints with status filter - only filtered status in caseStatus"""
        mock_conn = Mock()
        mock_context, mock_cursor = create_mock_cursor()
        mock_conn.cursor.return_value = mock_context
        mock_get_db.return_value = mock_conn

        # Mock stats data
        mock_cursor.fetchall.side_effect = [
            [
                {'stat_name': 'Pending', 'stat_value': 5},
                {'stat_name': 'Processed', 'stat_value': 3},
                {'stat_name': 'Overdue', 'stat_value': 2}
            ],
            # Only pending complaints (filtered)
            [
                {
                    'complaint_id': 'CAS-1',
                    'criticality': 'High',
                    'report_type': 'Spontaneous',
                    'receipt_date': date(2023, 1, 1),
                    'case_type': 'AE',
                    'status': 'Pending',
                    'text_extracted': True,
                    'created_at': datetime(2023, 1, 1, 10, 0, 0)
                },
                {
                    'complaint_id': 'CAS-4',
                    'criticality': 'Medium',
                    'report_type': 'Study',
                    'receipt_date': date(2023, 1, 4),
                    'case_type': 'PC',
                    'status': 'Pending',
                    'text_extracted': False,
                    'created_at': datetime(2023, 1, 4, 13, 0, 0)
                }
            ]
        ]

        # Mock total count for pending only
        mock_cursor.fetchone.return_value = {'total': 5}

        event = {
            'queryStringParameters': {'status': 'pending', 'page': '1'}
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        
        # Verify pagination reflects filtered results
        assert body['pagination']['total_items'] == 5
        assert body['pagination']['current_page'] == 1
        
        # Verify only pending status has data, others are empty
        assert len(body['caseStatus']['pending']) == 2
        assert len(body['caseStatus']['processed']) == 0
        assert len(body['caseStatus']['overdue']) == 0
        
        # Verify total_complaints reflects filtered count
        assert body['caseStats']['total_complaints'] == 5

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
        """Test: Get all complaints with various statuses (no filter)"""
        mock_conn = Mock()
        mock_context, mock_cursor = create_mock_cursor()
        mock_conn.cursor.return_value = mock_context

        # Mock stats and complaints data
        mock_cursor.fetchone.return_value = {'total': 15}
        mock_cursor.fetchall.side_effect = [
            [
                {'stat_name': 'Pending', 'stat_value': 2},
                {'stat_name': 'Processed', 'stat_value': 1},
                {'stat_name': 'Overdue', 'stat_value': 1}
            ],
            # Paginated complaints
            [
                {'complaint_id': 'CAS-1', 'criticality': 'High', 'report_type': 'Spontaneous', 'receipt_date': date(2023, 1, 1), 'case_type': 'AE', 'status': 'Pending', 'text_extracted': True, 'created_at': datetime(2023, 1, 1, 10, 0, 0)}
            ],
            # All complaints for grouping (no filter) - ordered by case_id DESC
            [
                {'complaint_id': 'CAS-00003', 'status': 'Overdue', 'criticality': 'Low', 'report_type': 'Literature', 'receipt_date': date(2023, 1, 3), 'case_type': 'AE', 'text_extracted': False, 'created_at': datetime(2023, 1, 3, 12, 0, 0)},
                {'complaint_id': 'CAS-00002', 'status': 'Processed', 'criticality': 'Medium', 'report_type': 'Study', 'receipt_date': date(2023, 1, 2), 'case_type': 'PC', 'text_extracted': True, 'created_at': datetime(2023, 1, 2, 11, 0, 0)},
                {'complaint_id': 'CAS-00001', 'status': 'Pending', 'criticality': 'High', 'report_type': 'Spontaneous', 'receipt_date': date(2023, 1, 1), 'case_type': 'AE', 'text_extracted': False, 'created_at': datetime(2023, 1, 1, 10, 0, 0)}
            ]
        ]

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

    def test_get_all_complaints_with_status_filter(self):
        """Test: Get complaints with status filter applied"""
        mock_conn = Mock()
        mock_context, mock_cursor = create_mock_cursor()
        mock_conn.cursor.return_value = mock_context

        # Mock total count for pending only
        mock_cursor.fetchone.return_value = {'total': 2}
        
        # Mock stats and filtered complaints data
        mock_cursor.fetchall.side_effect = [
            [
                {'stat_name': 'Pending', 'stat_value': 2},
                {'stat_name': 'Processed', 'stat_value': 1},
                {'stat_name': 'Overdue', 'stat_value': 1}
            ],
            # Only pending complaints (filtered and paginated) - ordered by case_id DESC
            [
                {'complaint_id': 'CAS-00004', 'criticality': 'Medium', 'report_type': 'Study', 'receipt_date': date(2023, 1, 4), 'case_type': 'PC', 'status': 'Pending', 'text_extracted': True, 'created_at': datetime(2023, 1, 4, 13, 0, 0)},
                {'complaint_id': 'CAS-00001', 'criticality': 'High', 'report_type': 'Spontaneous', 'receipt_date': date(2023, 1, 1), 'case_type': 'AE', 'status': 'Pending', 'text_extracted': False, 'created_at': datetime(2023, 1, 1, 10, 0, 0)}
            ]
        ]

        result = lambda_function.get_all_complaints(mock_conn, 1, 'pending')

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        
        # Check statistics reflect filtered count
        stats = body['caseStats']
        assert stats['total_complaints'] == 2
        
        # Check pagination reflects filtered results
        pagination = body['pagination']
        assert pagination['current_page'] == 1
        assert pagination['total_items'] == 2
        assert pagination['items_per_page'] == 15
        
        # Check caseStatus only has pending complaints
        case_status = body['caseStatus']
        assert len(case_status['pending']) == 2
        assert len(case_status['processed']) == 0
        assert len(case_status['overdue']) == 0


class TestUtilityFunctions:
    """Tests for utility functions"""

    def test_group_by_status_comprehensive(self):
        """Test: Group complaints by status with descending case_id ordering"""
        complaints = [
            {
                'status': 'Pending',
                'complaint_id': 'CAS-00001',
                'criticality': 'High',
                'report_type': 'Spontaneous',
                'receipt_date': date(2023, 1, 1),
                'case_type': 'AE',
                'text_extracted': True,
                'created_at': datetime(2023, 1, 1, 10, 0, 0)
            },
            {
                'status': 'Pending',
                'complaint_id': 'CAS-00003',
                'criticality': 'Medium',
                'report_type': 'Study',
                'receipt_date': date(2023, 1, 3),
                'case_type': 'PC',
                'text_extracted': False,
                'created_at': datetime(2023, 1, 3, 12, 0, 0)
            },
            {
                'status': 'Processed',
                'complaint_id': 'CAS-00002',
                'criticality': 'Medium',
                'report_type': 'Study',
                'receipt_date': date(2023, 1, 2),
                'case_type': 'PC',
                'text_extracted': True,
                'created_at': datetime(2023, 1, 2, 11, 0, 0)
            },
            {
                'status': 'Overdue',
                'complaint_id': 'CAS-00004',
                'criticality': 'Low',
                'report_type': 'Literature',
                'receipt_date': date(2023, 1, 4),
                'case_type': 'AE',
                'text_extracted': False,
                'created_at': datetime(2023, 1, 4, 13, 0, 0)
            }
        ]

        result = lambda_function._group_by_status(complaints)

        assert len(result['pending']) == 2
        assert len(result['processed']) == 1
        assert len(result['overdue']) == 1
        
        # Check descending order by case_id within each status
        pending_items = result['pending']
        assert pending_items[0]['case_id'] == 'CAS-00003'  # Higher case_id first
        assert pending_items[1]['case_id'] == 'CAS-00001'  # Lower case_id second
        
        # Check field mapping
        assert pending_items[0]['criticality'] == 'Medium'
        assert pending_items[0]['case_type'] == ['PC']
        assert pending_items[0]['text_extracted'] is False
        assert pending_items[1]['text_extracted'] is True

    def test_get_cors_headers(self):
        """Test: CORS headers function"""
        headers = lambda_function._get_cors_headers()

        assert headers['Content-Type'] == 'application/json'
        assert headers['Access-Control-Allow-Origin'] == '*'
        assert headers['Access-Control-Allow-Methods'] == 'GET, OPTIONS'
        assert 'Authorization' in headers['Access-Control-Allow-Headers']

    @patch.dict('os.environ', {'env': 'dev', 'db_secret_base_name': 'aurora-postgres-master', 'db_region': 'us-east-1'})
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
            mock_get_secret.assert_called_once_with('qms-dev-aurora-postgres-master', 'us-east-1')
            mock_connect.assert_called_once_with(
                host='localhost',
                port=5432,
                dbname='testdb',
                user='testuser',
                password='testpass'
            )


    @patch.object(lambda_function, 'CRL_TO_LABEL', {'CRL-000100': 'Dose confirmation', 'CRL-000106': 'Needle bent'})
    @patch.object(lambda_function, 'get_db_connection')
    def test_get_single_complaint_with_crl_mapping(self, mock_get_db):
        """Test: CRL codes are mapped to labels and crl_list/label_list are included"""
        mock_conn = Mock()
        mock_context, mock_cursor = create_mock_cursor()
        mock_conn.cursor.return_value = mock_context
        mock_get_db.return_value = mock_conn

        mock_cursor.fetchone.side_effect = [
            {
                'complaint_id': 'CAS-555',
                'receipt_date': date(2023, 1, 15),
                'criticality': 'High',
                'report_type': 'Spontaneous',
                'narrative_summary': 'Test summary',
                'case_type': 'AE',
                'narrative': 'Test narrative',
                'primary_reporter': 'John Doe',
                'primary_reporter_address': '123 Main St',
                'patient_name': 'Jane Patient',
                'physician': 'Dr. Smith',
                'drug': 'Test Drug',
                'lot_no': 'LOT555',
                'dosage': '100mg',
                'expiration_date': date(2024, 1, 1),
                'part_number': 'PN555',
                'status': 'Pending',
                'text_extracted': True,
                'created_at': datetime(2023, 1, 15, 10, 0, 0),
                'file_name': 'test.pdf',
                's3_url': 's3://bucket/test.pdf'
            },
            {
                'inference_id': 10,
                'complaint_id': 'CAS-555',
                'levels': {"2": 0.85},
                'subcategories': {"Dose confirmation": 0.95},
                'crl_codes': {"CRL-000100": 0.95},
                'units': 5,
                'final_level': '2',
                'priority': 1,
                'priority_reason': 'High priority',
                'priority_summary': 'Critical issue'
            }
        ]

        event = {'queryStringParameters': {'complaint_id': 'CAS-555'}}
        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['complaintClassified'] is True
        assert len(body['category_details']) == 1
        assert body['category_details'][0]['crl'] == 'Dose confirmation'
        assert 'crl_list' in body
        assert 'label_list' in body
        assert len(body['label_list']) == 15
        assert 'Injection incomplete' in body['label_list']

    @patch.object(lambda_function, 'CRL_TO_LABEL', {'CRL-000100': 'Dose confirmation'})
    @patch.object(lambda_function, 'get_db_connection')
    def test_get_single_complaint_with_unassigned_crl(self, mock_get_db):
        """Test: UNASSIGNED CRL code is mapped to 'Not Assigned'"""
        mock_conn = Mock()
        mock_context, mock_cursor = create_mock_cursor()
        mock_conn.cursor.return_value = mock_context
        mock_get_db.return_value = mock_conn

        mock_cursor.fetchone.side_effect = [
            {
                'complaint_id': 'CAS-666',
                'receipt_date': date(2023, 1, 20),
                'criticality': 'Medium',
                'report_type': 'Spontaneous',
                'narrative_summary': 'Test',
                'case_type': 'PC',
                'narrative': 'Test',
                'primary_reporter': 'John',
                'primary_reporter_address': '123',
                'patient_name': 'Jane',
                'physician': 'Dr. Smith',
                'drug': 'Drug',
                'lot_no': 'LOT',
                'dosage': '50mg',
                'expiration_date': date(2024, 1, 1),
                'part_number': 'PN',
                'status': 'Pending',
                'text_extracted': True,
                'created_at': datetime(2023, 1, 20, 10, 0, 0),
                'file_name': 'test.pdf',
                's3_url': 's3://bucket/test.pdf'
            },
            {
                'inference_id': 11,
                'complaint_id': 'CAS-666',
                'levels': {"1": 0.75},
                'subcategories': {"Unknown Category": 0.80},
                'crl_codes': {"UNASSIGNED": 0.80},
                'units': 0,
                'final_level': '1',
                'priority': 0,
                'priority_reason': 'Low priority',
                'priority_summary': 'Minor issue'
            }
        ]

        event = {'queryStringParameters': {'complaint_id': 'CAS-666'}}
        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['category_details'][0]['crl'] == 'Not Assigned'

    @patch.object(lambda_function, 'CRL_TO_LABEL', {'CRL-000100': 'Dose confirmation'})
    @patch.object(lambda_function, 'get_db_connection')
    def test_get_single_complaint_with_unknown_crl(self, mock_get_db):
        """Test: Unknown CRL code is mapped to 'Unknown CRL'"""
        mock_conn = Mock()
        mock_context, mock_cursor = create_mock_cursor()
        mock_conn.cursor.return_value = mock_context
        mock_get_db.return_value = mock_conn

        mock_cursor.fetchone.side_effect = [
            {
                'complaint_id': 'CAS-777',
                'receipt_date': date(2023, 1, 25),
                'criticality': 'Low',
                'report_type': 'Study',
                'narrative_summary': 'Test',
                'case_type': 'AE',
                'narrative': 'Test',
                'primary_reporter': 'John',
                'primary_reporter_address': '123',
                'patient_name': 'Jane',
                'physician': 'Dr. Smith',
                'drug': 'Drug',
                'lot_no': 'LOT',
                'dosage': '25mg',
                'expiration_date': date(2024, 1, 1),
                'part_number': 'PN',
                'status': 'Pending',
                'text_extracted': True,
                'created_at': datetime(2023, 1, 25, 10, 0, 0),
                'file_name': 'test.pdf',
                's3_url': 's3://bucket/test.pdf'
            },
            {
                'inference_id': 12,
                'complaint_id': 'CAS-777',
                'levels': {"0": 0.90},
                'subcategories': {"Some Category": 0.85},
                'crl_codes': {"CRL-999999": 0.85},
                'units': 0,
                'final_level': '0',
                'priority': 0,
                'priority_reason': 'Low',
                'priority_summary': 'Minor'
            }
        ]

        event = {'queryStringParameters': {'complaint_id': 'CAS-777'}}
        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['category_details'][0]['crl'] == 'Unknown CRL'

    @patch.object(lambda_function, 'get_db_connection')
    def test_get_single_complaint_no_crl_lists_when_not_classified(self, mock_get_db):
        """Test: crl_list and label_list are not included when complaint is not classified"""
        mock_conn = Mock()
        mock_context, mock_cursor = create_mock_cursor()
        mock_conn.cursor.return_value = mock_context
        mock_get_db.return_value = mock_conn

        mock_cursor.fetchone.side_effect = [
            {
                'complaint_id': 'CAS-888',
                'receipt_date': date(2023, 1, 30),
                'criticality': 'Medium',
                'report_type': 'Spontaneous',
                'narrative_summary': '',
                'case_type': 'PC',
                'narrative': 'Test',
                'primary_reporter': 'John',
                'primary_reporter_address': '123',
                'patient_name': 'Jane',
                'physician': 'Dr. Smith',
                'drug': 'Drug',
                'lot_no': 'LOT',
                'dosage': '75mg',
                'expiration_date': date(2024, 1, 1),
                'part_number': 'PN',
                'status': 'Pending',
                'text_extracted': False,
                'created_at': datetime(2023, 1, 30, 10, 0, 0),
                'file_name': 'test.pdf',
                's3_url': 's3://bucket/test.pdf'
            },
            None
        ]

        event = {'queryStringParameters': {'complaint_id': 'CAS-888'}}
        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['complaintClassified'] is False
        assert 'crl_list' not in body
        assert 'label_list' not in body


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

    @patch.object(lambda_function, 'get_db_connection')
    def test_get_single_processed_complaint(self, mock_get_db):
        """Test: Get processed complaint - should fetch from processed_complaints table"""
        mock_conn = Mock()
        mock_context, mock_cursor = create_mock_cursor()
        mock_conn.cursor.return_value = mock_context
        mock_get_db.return_value = mock_conn

        # Mock complaint data with Processed status
        mock_cursor.fetchone.side_effect = [
            {
                'complaint_id': 'CAS-789',
                'receipt_date': date(2023, 1, 10),
                'criticality': 'High',
                'report_type': 'Spontaneous',
                'narrative_summary': 'Processed complaint summary',
                'case_type': 'AE',
                'narrative': 'Processed complaint narrative',
                'primary_reporter': 'John Doe',
                'primary_reporter_address': '123 Main St',
                'patient_name': 'Jane Patient',
                'physician': 'Dr. Smith',
                'drug': 'Test Drug',
                'lot_no': 'LOT789',
                'dosage': '200mg',
                'expiration_date': date(2024, 12, 31),
                'part_number': 'PN789',
                'status': 'Processed',
                'text_extracted': True,
                'created_at': datetime(2023, 1, 10, 10, 0, 0),
                'file_name': 'test3.pdf',
                's3_url': 's3://bucket/test3.pdf'
            },
            {
                'approved_category_details': [
                    {"id": "1", "label": "Dose confirmation", "level": "2", "crl": "CRL-000100", "priority": "Low", "unit": 5, "percentage": 94.92},
                    {"id": "2", "label": "Needle issue", "level": "1", "crl": "CRL-000105", "priority": "High", "unit": 5, "percentage": 5.08}
                ]
            }
        ]

        event = {
            'queryStringParameters': {'complaint_id': 'CAS-789'}
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['case_id'] == 'CAS-789'
        assert body['caseStatus'] == 'processed'
        assert body['complaintClassified'] is True
        assert len(body['category_details']) == 2
        assert body['category_details'][0]['label'] == 'Dose confirmation'
        assert body['category_details'][1]['label'] == 'Needle issue'
