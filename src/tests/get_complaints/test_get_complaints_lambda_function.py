import pytest
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal

# Add src directory to path for importing lambda_function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'app', 'get_complaints'))
import lambda_function


class TestLambdaHandler:
    """Unit tests for the main lambda_handler function"""

    @patch.dict(os.environ, {'DYNAMODB_TABLE_NAME': 'test-table'})
    @patch('boto3.resource')
    def test_get_single_complaint_success(self, mock_boto3):
        """Test: Successful single complaint retrieval"""
        # Mock DynamoDB
        mock_table = Mock()
        mock_dynamodb = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3.return_value = mock_dynamodb

        # Mock DynamoDB response
        mock_table.get_item.return_value = {
            'Item': {
                'PK': 'COMPLAINT#CAS-123',
                'SK': 'METADATA',
                'complaint_id': 'CAS-123',
                'case_id': 'RGL23-000070',
                'narrative': 'Test complaint narrative',
                'criticality': 'High',
                'status': 'pending',
                'created_at': '2023-01-07T00:00:00Z',
                'primary_reporter': {'name': 'John Doe'},
                'product_details': {'drug_name': 'Test Drug'}
            }
        }

        event = {
            'pathParameters': {'complaint_id': 'CAS-123'}
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['case_id'] == 'RGL23-000070'
        assert body['narrative'] == 'Test complaint narrative'
        assert body['criticality'] == 'High'
        assert body['caseStatus'] == 'pending'

    @patch.dict(os.environ, {'DYNAMODB_TABLE_NAME': 'test-table'})
    @patch('boto3.resource')
    def test_get_single_complaint_not_found(self, mock_boto3):
        """Test: Single complaint not found"""
        # Mock DynamoDB
        mock_table = Mock()
        mock_dynamodb = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3.return_value = mock_dynamodb

        # Mock DynamoDB response - no item found
        mock_table.get_item.return_value = {}

        event = {
            'pathParameters': {'complaint_id': 'CAS-999'}
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 404
        body = json.loads(result['body'])
        assert body['success'] is False
        assert body['error'] == 'Complaint not found'

    @patch.dict(os.environ, {'DYNAMODB_TABLE_NAME': 'test-table'})
    @patch('boto3.resource')
    def test_get_all_complaints_success(self, mock_boto3):
        """Test: Successful all complaints retrieval"""
        # Mock DynamoDB
        mock_table = Mock()
        mock_dynamodb = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3.return_value = mock_dynamodb

        # Mock GSI query responses
        mock_table.query.side_effect = [
            {'Items': [{'status': 'IN-REVIEW', 'complaint_id': 'CAS-1'}]},
            {'Items': [{'status': 'PROCESSED', 'complaint_id': 'CAS-2'}]},
            {'Items': [{'status': 'OVERDUE', 'complaint_id': 'CAS-3'}]}
        ]

        event = {}  # No path parameters

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert 'caseStats' in body
        assert 'caseStatus' in body
        assert body['caseStats']['total_complaints'] == 3

    @patch.dict(os.environ, {'DYNAMODB_TABLE_NAME': 'test-table'})
    @patch('boto3.resource')
    def test_get_all_complaints_gsi_fallback(self, mock_boto3):
        """Test: GSI query fails, fallback to scan"""
        # Mock DynamoDB
        mock_table = Mock()
        mock_dynamodb = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3.return_value = mock_dynamodb

        # Mock GSI query failure, scan success
        mock_table.query.side_effect = Exception("GSI error")
        mock_table.scan.return_value = {
            'Items': [
                {'PK': 'COMPLAINT#CAS-1', 'status': 'pending'},
                {'PK': 'COMPLAINT#CAS-2', 'status': 'processed'}
            ]
        }

        event = {}

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['caseStats']['total_complaints'] == 2

    @patch.dict(os.environ, {'DYNAMODB_TABLE_NAME': 'test-table'})
    @patch('boto3.resource')
    def test_lambda_handler_exception(self, mock_boto3):
        """Test: Lambda handler exception handling"""
        # Mock DynamoDB to raise exception
        mock_boto3.side_effect = Exception("DynamoDB connection failed")

        event = {}

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert body['success'] is False
        assert body['error'] == 'Internal server error'

    @patch.dict(os.environ, {'DYNAMODB_TABLE_NAME': 'test-table'})
    @patch('boto3.resource')
    def test_empty_path_parameters(self, mock_boto3):
        """Test: Empty path parameters triggers get_all_complaints"""
        # Mock DynamoDB
        mock_table = Mock()
        mock_dynamodb = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3.return_value = mock_dynamodb

        # Mock GSI queries to return empty results, then scan fallback
        mock_table.query.return_value = {'Items': []}
        mock_table.scan.return_value = {'Items': []}

        event = {'pathParameters': {}}

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 200
        # Should call get_all_complaints, not get_single_complaint


class TestGetSingleComplaint:
    """Tests for get_single_complaint function"""

    def test_get_single_complaint_with_all_fields(self):
        """Test: Single complaint with all fields"""
        mock_table = Mock()
        mock_table.get_item.return_value = {
            'Item': {
                'complaint_id': 'CAS-123',
                'case_id': 'RGL23-000070',
                'narrative': 'Full narrative text',
                'narrative_text': 'Alternative narrative',
                'criticality': 'Medium',
                'report_type': 'Spontaneous',
                'ai_summary': 'AI generated summary',
                'short_description': 'Short desc',
                'case_type': ['AE', 'PC'],
                'primary_reporter': {'name': 'Jane Doe', 'address': '123 Main St'},
                'patient_name': 'John Patient',
                'physician_name': 'Dr. Smith',
                'product_details': {'drug_name': 'TestDrug', 'dosage': '100mg'},
                'status': 'in-review',
                'receipt_date': '2023-01-01',
                'created_at': '2023-01-01T10:00:00Z'
            }
        }

        result = lambda_function.get_single_complaint(mock_table, 'CAS-123')

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['case_id'] == 'RGL23-000070'
        assert body['narrative'] == 'Full narrative text'
        assert body['ai_summary'] == 'AI generated summary'
        assert body['case_type'] == ['AE', 'PC']
        assert body['caseStatus'] == 'in-review'

    def test_get_single_complaint_minimal_fields(self):
        """Test: Single complaint with minimal fields"""
        mock_table = Mock()
        mock_table.get_item.return_value = {
            'Item': {
                'complaint_id': 'CAS-456'
            }
        }

        result = lambda_function.get_single_complaint(mock_table, 'CAS-456')

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['case_id'] == 'CAS-456'  # Falls back to complaint_id
        assert body['criticality'] == 'NA'
        assert body['report_type'] == 'NA'
        assert body['narrative'] == ''
        assert body['caseStatus'] == 'pending'

    def test_get_single_complaint_db_error(self):
        """Test: Database error in get_single_complaint"""
        mock_table = Mock()
        mock_table.get_item.side_effect = Exception("DynamoDB error")

        result = lambda_function.get_single_complaint(mock_table, 'CAS-123')

        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert body['success'] is False
        assert body['error'] == 'Failed to retrieve complaint'

    def test_get_single_complaint_with_decimals(self):
        """Test: Single complaint with Decimal values"""
        mock_table = Mock()
        mock_table.get_item.return_value = {
            'Item': {
                'complaint_id': 'CAS-789',
                'score': Decimal('95.5'),
                'confidence': Decimal('0.85')
            }
        }

        result = lambda_function.get_single_complaint(mock_table, 'CAS-789')

        assert result['statusCode'] == 200
        # Should handle Decimal encoding without errors


class TestGetAllComplaints:
    """Tests for get_all_complaints function"""

    def test_get_all_complaints_with_data(self):
        """Test: Get all complaints with various statuses"""
        mock_table = Mock()
        
        # Mock GSI queries for different statuses
        mock_table.query.side_effect = [
            {'Items': [
                {'status': 'IN-REVIEW', 'complaint_id': 'CAS-1', 'criticality': 'High'},
                {'status': 'PENDING', 'complaint_id': 'CAS-2', 'criticality': 'Medium'}
            ]},
            {'Items': [
                {'status': 'PROCESSED', 'complaint_id': 'CAS-3', 'criticality': 'Low'}
            ]},
            {'Items': [
                {'status': 'OVERDUE', 'complaint_id': 'CAS-4', 'criticality': 'High'}
            ]}
        ]

        result = lambda_function.get_all_complaints(mock_table)

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        
        # Check statistics
        stats = body['caseStats']
        assert stats['total_complaints'] == 4
        assert stats['pending'] == 2  # IN-REVIEW + PENDING
        assert stats['processed'] == 1
        assert stats['overdue'] == 1

        # Check case status grouping
        case_status = body['caseStatus']
        assert len(case_status['pending']) == 2
        assert len(case_status['processed']) == 1
        assert len(case_status['overdue']) == 1

    def test_get_all_complaints_empty_result(self):
        """Test: Get all complaints with no data"""
        mock_table = Mock()
        # Mock GSI queries to return empty, then scan fallback
        mock_table.query.return_value = {'Items': []}
        mock_table.scan.return_value = {'Items': []}

        result = lambda_function.get_all_complaints(mock_table)

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['caseStats']['total_complaints'] == 0

    def test_get_all_complaints_scan_fallback(self):
        """Test: GSI query fails, uses scan fallback"""
        mock_table = Mock()
        
        # All GSI queries fail
        mock_table.query.side_effect = Exception("GSI unavailable")
        
        # Scan succeeds
        mock_table.scan.return_value = {
            'Items': [
                {'PK': 'COMPLAINT#CAS-1', 'status': 'pending'},
                {'PK': 'COMPLAINT#CAS-2', 'status': 'processed'}
            ]
        }

        result = lambda_function.get_all_complaints(mock_table)

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['caseStats']['total_complaints'] == 2

    def test_get_all_complaints_db_error(self):
        """Test: Database error in get_all_complaints"""
        mock_table = Mock()
        mock_table.query.side_effect = Exception("Query failed")
        mock_table.scan.side_effect = Exception("Scan failed")

        result = lambda_function.get_all_complaints(mock_table)

        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert body['success'] is False
        assert body['error'] == 'Failed to retrieve complaints'


class TestUtilityFunctions:
    """Tests for utility functions"""

    def test_calculate_stats_various_statuses(self):
        """Test: Calculate statistics with various statuses"""
        complaints = [
            {'status': 'PENDING'},
            {'status': 'IN-REVIEW'},
            {'status': 'PROCESSED'},
            {'status': 'COMPLETED'},
            {'status': 'OVERDUE'},
            {'status': 'pending'},  # lowercase
            {'status': ''}  # empty status
        ]

        stats = lambda_function._calculate_stats(complaints)

        assert stats['total_complaints'] == 7
        assert stats['pending'] == 3  # PENDING, IN-REVIEW, pending
        assert stats['processed'] == 2  # PROCESSED, COMPLETED
        assert stats['overdue'] == 1
        assert stats['avg_cycle_time'] == 24
        assert stats['best_time'] == 7
        assert stats['longest_time'] == 72

    def test_calculate_stats_empty_list(self):
        """Test: Calculate statistics with empty list"""
        stats = lambda_function._calculate_stats([])

        assert stats['total_complaints'] == 0
        assert stats['pending'] == 0
        assert stats['processed'] == 0
        assert stats['overdue'] == 0

    def test_group_by_status_comprehensive(self):
        """Test: Group complaints by status comprehensively"""
        complaints = [
            {
                'status': 'pending',
                'complaint_id': 'CAS-1',
                'case_id': 'RGL-1',
                'criticality': 'High',
                'report_type': 'Spontaneous',
                'created_at': '2023-01-01'
            },
            {
                'status': 'IN-REVIEW',
                'complaint_id': 'CAS-2',
                'criticality': 'Medium'
            },
            {
                'status': 'PROCESSED',
                'case_id': 'RGL-3',
                'criticality': 'Low'
            },
            {
                'status': 'overdue',
                'complaint_id': 'CAS-4'
            },
            {
                'status': 'unknown',  # Should not be grouped
                'complaint_id': 'CAS-5'
            }
        ]

        result = lambda_function._group_by_status(complaints)

        assert len(result['pending']) == 2  # pending, IN-REVIEW
        assert len(result['processed']) == 1  # PROCESSED
        assert len(result['overdue']) == 1   # overdue
        
        # Check field mapping
        pending_item = result['pending'][0]
        assert pending_item['case_id'] == 'RGL-1'
        assert pending_item['criticality'] == 'High'
        assert pending_item['report_type'] == 'Spontaneous'

    def test_group_by_status_missing_fields(self):
        """Test: Group by status with missing fields"""
        complaints = [
            {'status': 'pending'},  # Minimal data
            {}  # No status
        ]

        result = lambda_function._group_by_status(complaints)

        assert len(result['pending']) == 1
        pending_item = result['pending'][0]
        assert pending_item['case_id'] == ''
        assert pending_item['criticality'] == 'NA'

    def test_get_cors_headers(self):
        """Test: CORS headers function"""
        headers = lambda_function._get_cors_headers()

        assert headers['Content-Type'] == 'application/json'
        assert headers['Access-Control-Allow-Origin'] == '*'
        assert headers['Access-Control-Allow-Methods'] == 'GET, OPTIONS'
        assert 'Authorization' in headers['Access-Control-Allow-Headers']


class TestDecimalEncoder:
    """Tests for DecimalEncoder class"""

    def test_decimal_encoder_with_decimal(self):
        """Test: Decimal encoder with Decimal values"""
        encoder = lambda_function.DecimalEncoder()
        
        test_data = {
            'score': Decimal('95.5'),
            'confidence': Decimal('0.85'),
            'count': 10,
            'name': 'test'
        }

        result = json.dumps(test_data, cls=lambda_function.DecimalEncoder)
        parsed = json.loads(result)

        assert parsed['score'] == 95.5
        assert parsed['confidence'] == 0.85
        assert parsed['count'] == 10
        assert parsed['name'] == 'test'

    def test_decimal_encoder_without_decimal(self):
        """Test: Decimal encoder with non-Decimal values"""
        encoder = lambda_function.DecimalEncoder()
        
        test_data = {
            'number': 42,
            'text': 'hello',
            'boolean': True,
            'list': [1, 2, 3]
        }

        result = json.dumps(test_data, cls=lambda_function.DecimalEncoder)
        parsed = json.loads(result)

        assert parsed == test_data


class TestEdgeCases:
    """Tests for edge cases and error conditions"""

    @patch.dict(os.environ, {'DYNAMODB_TABLE_NAME': 'test-table'})
    @patch('boto3.resource')
    def test_none_path_parameters(self, mock_boto3):
        """Test: None path parameters"""
        mock_table = Mock()
        mock_dynamodb = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3.return_value = mock_dynamodb

        # Mock GSI queries and scan fallback
        mock_table.query.return_value = {'Items': []}
        mock_table.scan.return_value = {'Items': []}

        event = {'pathParameters': None}

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 200
        # Should trigger get_all_complaints path

    @patch.dict(os.environ, {'DYNAMODB_TABLE_NAME': 'test-table'})
    @patch('boto3.resource')
    def test_complaint_id_none(self, mock_boto3):
        """Test: complaint_id is None in path parameters"""
        mock_table = Mock()
        mock_dynamodb = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3.return_value = mock_dynamodb

        # Mock GSI queries and scan fallback
        mock_table.query.return_value = {'Items': []}
        mock_table.scan.return_value = {'Items': []}

        event = {'pathParameters': {'complaint_id': None}}

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 200
        # Should trigger get_all_complaints path

    def test_calculate_stats_case_insensitive(self):
        """Test: Statistics calculation is case insensitive"""
        complaints = [
            {'status': 'Pending'},
            {'status': 'PENDING'},
            {'status': 'pending'},
            {'status': 'In-Review'},
            {'status': 'PROCESSED'},
            {'status': 'Overdue'}
        ]

        stats = lambda_function._calculate_stats(complaints)

        assert stats['pending'] == 4  # All pending variants
        assert stats['processed'] == 1
        assert stats['overdue'] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=get_complaints.lambda_function", "--cov-report=term-missing"])