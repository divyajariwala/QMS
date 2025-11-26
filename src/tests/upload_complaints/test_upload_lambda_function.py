import pytest
import json
import os
import sys
import io
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

# Add src directory to path for importing lambda_function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'app'))
from upload_complaints import lambda_function


class TestLambdaHandler:
    """Unit tests for the main lambda_handler function"""

    @patch.dict(os.environ, {
        'env': 'dev',
        'S3_BUCKET_NAME': 'test-bucket',
        'SQS_QUEUE_NAME': 'test-queue',
        'db_secret_base_name': 'aurora-postgres-master',
        'db_region': 'us-east-1'
    })
    @patch('boto3.client')
    @patch('upload_complaints.lambda_function.parse_multipart_manual')
    @patch('upload_complaints.lambda_function.create_file_record')
    @patch('upload_complaints.lambda_function.create_complaint_in_db')
    def test_successful_csv_upload(self, mock_create_complaint, mock_create_file, mock_parse, mock_boto3):
        """Test: Successful CSV file upload with database integration"""
        # Mock AWS clients
        mock_s3 = Mock()
        mock_sqs = Mock()
        mock_boto3.side_effect = lambda service: mock_s3 if service == 's3' else mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789/test-queue'}
        mock_sqs.send_message.return_value = {'MessageId': 'test-123'}
        
        # Mock database operations
        mock_create_complaint.return_value = 'CAS-00001'

        # Mock CSV with valid 2-column format
        mock_parse.return_value = {
            'filename': 'data.csv',
            'content': b'complaint_id,narrative\nOLD-001,Test complaint narrative',
            'content_type': 'text/csv',
            'field_name': 'file'
        }

        event = {
            'body': 'multipart-fake-content',
            'isBase64Encoded': False,
            'headers': {'content-type': 'multipart/form-data; boundary=test'}
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
        assert body['data']['filename'] == 'data.csv'
        assert body['data']['complaints_processed'] == 1

        mock_s3.put_object.assert_called_once()
        mock_create_file.assert_called_once()
        mock_create_complaint.assert_called_once()
        mock_sqs.send_message.assert_called_once()

    @patch.dict(os.environ, {
        'env': 'dev',
        'S3_BUCKET_NAME': 'test-bucket',
        'SQS_QUEUE_NAME': 'test-queue',
        'db_secret_base_name': 'aurora-postgres-master',
        'db_region': 'us-east-1'
    })
    @patch('boto3.client')
    @patch('upload_complaints.lambda_function.parse_multipart_manual')
    @patch('upload_complaints.lambda_function.create_file_record')
    @patch('upload_complaints.lambda_function.create_complaint_in_db')
    def test_successful_pdf_upload_sqs(self, mock_create_complaint, mock_create_file, mock_parse, mock_boto3):
        """Test: Successful PDF upload with SQS message"""
        # Mock AWS clients
        mock_s3 = Mock()
        mock_sqs = Mock()
        mock_boto3.side_effect = lambda service: mock_s3 if service == 's3' else mock_sqs
        
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789/test-queue'}
        mock_sqs.send_message.return_value = {'MessageId': 'test-456'}
        
        # Mock database operations
        mock_create_complaint.return_value = 'CAS-00002'

        # Mock PDF file
        mock_parse.return_value = {
            'filename': 'complaint.pdf',
            'content': b'%PDF-1.4 fake pdf content',
            'content_type': 'application/pdf',
            'field_name': 'file'
        }

        event = {
            'body': 'fake-pdf-content',
            'isBase64Encoded': False,
            'headers': {'content-type': 'multipart/form-data; boundary=test'}
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
        assert body['data']['status'] == 'processing'
        assert body['data']['complaint_id'] == 'CAS-00002'
        assert body['data']['message_id'] == 'test-456'
        
        # Verify S3 upload happened
        mock_s3.put_object.assert_called_once()
        
        # Verify database operations
        mock_create_file.assert_called_once()
        mock_create_complaint.assert_called_once()
        
        # Verify SQS message sent with correct format
        mock_sqs.send_message.assert_called_once()
        call_args = mock_sqs.send_message.call_args
        message_body = json.loads(call_args[1]['MessageBody'])
        assert message_body['complaint_id'] == 'CAS-00002'
        assert 's3path' in message_body
        assert 'file_id' in message_body

    @patch.dict(os.environ, {
        'env': 'dev',
        'S3_BUCKET_NAME': 'test-bucket',
        'SQS_QUEUE_NAME': 'test-queue'
    })
    @patch('boto3.client')
    def test_missing_body(self, mock_boto3):
        """Test: Error when body is missing"""
        # Mock AWS clients
        mock_sqs = Mock()
        mock_boto3.side_effect = lambda service: mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789/test-queue'}

        event = {}
        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert body['message'] == "No file provided"
    
    @patch.dict(os.environ, {
        'env': 'dev',
        'S3_BUCKET_NAME': 'test-bucket',
        'SQS_QUEUE_NAME': 'test-queue'
    })
    @patch('boto3.client')
    @patch('upload_complaints.lambda_function.parse_multipart_manual')
    @patch('upload_complaints.lambda_function.create_file_record')
    def test_csv_too_many_columns(self, mock_create_file, mock_parse, mock_boto3):
        """Test: CSV file with more than 2 columns should be rejected"""
        mock_s3 = Mock()
        mock_sqs = Mock()
        mock_boto3.side_effect = lambda service: mock_s3 if service == 's3' else mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789/test-queue'}
        
        mock_parse.return_value = {
            'filename': 'wide_data.csv',
            'content': b'complaint_id,narrative,extra_column\nOLD-001,Test narrative,Extra data',
            'content_type': 'text/csv',
            'field_name': 'file'
        }

        event = {
            'body': 'multipart-fake-content',
            'isBase64Encoded': False,
            'headers': {'content-type': 'multipart/form-data; boundary=test'}
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert 'CSV header must have exactly 2 columns' in body['message']


class TestUtilityFunctions:
    """Tests for utility functions"""

    def test_get_content_type(self):
        """Test: Detect Content-Type by extension"""
        assert lambda_function._get_content_type('test.csv') == 'text/csv'
        assert lambda_function._get_content_type(
            'test.xlsx') == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        assert lambda_function._get_content_type('test.pdf') == 'application/pdf'
        assert lambda_function._get_content_type('test.unknown') == 'application/octet-stream'

    def test_sanitize_filename(self):
        """Test: Sanitize filename"""
        assert lambda_function._sanitize_filename('normal file.csv') == 'normal_file.csv'
        assert lambda_function._sanitize_filename('file@#$.csv') == 'file_.csv'
        assert lambda_function._sanitize_filename('') == 'unknown_file'

    def test_get_file_extension(self):
        """Test: Get file extension"""
        assert lambda_function._get_file_extension('test.csv') == 'csv'
        assert lambda_function._get_file_extension('test.XLSX') == 'xlsx'
        assert lambda_function._get_file_extension('test') == ''
        assert lambda_function._get_file_extension('') == 'unknown'
        assert lambda_function._get_file_extension(None) == 'unknown'

    def test_is_allowed_file(self):
        """Test: Validate allowed extensions"""
        assert lambda_function._is_allowed_file('test.csv') is True
        assert lambda_function._is_allowed_file('test.xlsx') is True
        assert lambda_function._is_allowed_file('test.pdf') is True
        assert lambda_function._is_allowed_file('test.xls') is True
        assert lambda_function._is_allowed_file('test.txt') is False
        assert lambda_function._is_allowed_file('') is False


class TestDatabaseFunctions:
    """Tests for database-related functions"""
    
    @patch('upload_complaints.lambda_function.get_connection_string')
    @patch('psycopg.connect')
    def test_create_file_record(self, mock_connect, mock_get_conn):
        """Test: Create file record in database"""
        mock_get_conn.return_value = 'mock_connection_string'
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        lambda_function.create_file_record(
            'test-file-id', 
            'test.pdf', 
            's3://bucket/key', 
            'test-user'
        )
        
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
    
    @patch('upload_complaints.lambda_function.get_connection_string')
    @patch('psycopg.connect')
    def test_create_complaint_in_db(self, mock_connect, mock_get_conn):
        """Test: Create complaint record in database with text_extracted set to false"""
        mock_get_conn.return_value = 'mock_connection_string'
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {'complaint_id': 'CAS-00001'}
        
        result = lambda_function.create_complaint_in_db('test-file-id', 'Test narrative')
        
        assert result == 'CAS-00001'
        mock_cursor.execute.assert_called_once()
        # Verify text_extracted is set to FALSE in the SQL
        call_args = mock_cursor.execute.call_args[0]
        assert 'text_extracted' in call_args[0]
        assert 'FALSE' in call_args[0]
        mock_conn.commit.assert_called_once()


class TestCSVProcessing:
    """Tests for CSV/Excel processing functions with enhanced parsing"""
    
    @patch('upload_complaints.lambda_function.create_complaint_in_db')
    def test_process_csv_excel_file_success(self, mock_create_complaint):
        """Test: Successfully process valid CSV file"""
        mock_create_complaint.side_effect = ['CAS-00001', 'CAS-00002']
        
        csv_content = b'complaint_id,narrative\nOLD-001,First complaint\nOLD-002,Second complaint'
        
        result = lambda_function.process_csv_excel_file(csv_content, 'csv', 'test-file-id')
        
        assert result['success'] is True
        assert result['processed_complaints'] == 2
        assert len(result['complaints']) == 2
        assert result['complaints'][0]['complaint_id'] == 'CAS-00001'
        assert result['complaints'][1]['complaint_id'] == 'CAS-00002'
    
    @patch('upload_complaints.lambda_function.create_complaint_in_db')
    def test_csv_with_quoted_commas(self, mock_create_complaint):
        """Test: CSV with quoted fields containing commas"""
        mock_create_complaint.side_effect = ['CAS-00001', 'CAS-00002', 'CAS-00003']
        
        csv_content = b'''id,narrative
1,"Product arrived damaged, packaging was torn"
2,"Customer service was unhelpful, rude during call"
3,"Wrong item shipped, received blue instead of red"'''
        
        result = lambda_function.process_csv_excel_file(csv_content, 'csv', 'test-file-id')
        
        assert result['success'] is True
        assert result['processed_complaints'] == 3
        
        # Check that commas in text are preserved
        complaints = result['complaints']
        assert 'Product arrived damaged, packaging was torn' in complaints[0]['narrative_text']
        assert 'Customer service was unhelpful, rude during call' in complaints[1]['narrative_text']
        assert 'Wrong item shipped, received blue instead of red' in complaints[2]['narrative_text']
    
    @patch('upload_complaints.lambda_function.create_complaint_in_db')
    def test_tab_separated_csv_with_commas(self, mock_create_complaint):
        """Test: Tab-separated CSV with commas in text fields"""
        mock_create_complaint.side_effect = ['CAS-00001', 'CAS-00002', 'CAS-00003']
        
        csv_content = b"""id\tnarrative
1\tProduct arrived damaged, packaging was torn
2\tCustomer service was unhelpful, rude during call
3\tQuality is poor - broke after first use"""
        
        result = lambda_function.process_csv_excel_file(csv_content, 'csv', 'test-file-id')
        
        assert result['success'] is True
        assert result['processed_complaints'] == 3
        
        # Check that commas and hyphens in text are preserved
        complaints = result['complaints']
        assert 'Product arrived damaged, packaging was torn' in complaints[0]['narrative_text']
        assert 'Quality is poor - broke after first use' in complaints[2]['narrative_text']
    
    @patch('upload_complaints.lambda_function.create_complaint_in_db')
    def test_csv_with_long_narrative(self, mock_create_complaint):
        """Test: CSV with long narrative text (1500+ chars) with punctuation"""
        mock_create_complaint.return_value = 'CAS-00001'
        
        long_narrative = "This is a very long complaint narrative with over 1500 characters. " * 30 + "It contains commas, periods, quotes 'like this', and other punctuation marks! The system should handle this as one complete string."
        csv_content = f'id,narrative\n1,"{long_narrative}"'.encode('utf-8')
        
        result = lambda_function.process_csv_excel_file(csv_content, 'csv', 'test-file-id')
        
        assert result['success'] is True
        assert result['processed_complaints'] == 1
        assert long_narrative in result['complaints'][0]['narrative_text']
    
    @patch('upload_complaints.lambda_function.create_complaint_in_db')
    def test_csv_with_utf8_bom(self, mock_create_complaint):
        """Test: CSV file with UTF-8 BOM"""
        mock_create_complaint.side_effect = ['CAS-00001', 'CAS-00002']
        
        csv_content = b'\xef\xbb\xbfid,narrative\n1,Complaint with BOM\n2,Another complaint'
        
        result = lambda_function.process_csv_excel_file(csv_content, 'csv', 'test-file-id')
        
        assert result['success'] is True
        assert result['processed_complaints'] == 2
    
    def test_csv_insufficient_rows(self):
        """Test: CSV with only header row"""
        csv_content = b'id,narrative'
        
        result = lambda_function.process_csv_excel_file(csv_content, 'csv', 'test-file-id')
        
        assert result['success'] is False
        assert 'must have at least a header and one data row' in result['message']
    
    def test_csv_header_validation(self):
        """Test: CSV header must have exactly 2 columns"""
        csv_content = b"""id
1"""
        
        result = lambda_function.process_csv_excel_file(csv_content, 'csv', 'test-file-id')
        
        assert result['success'] is False
        assert 'File must have exactly 2 columns' in result['message']
    
    @patch('upload_complaints.lambda_function.create_complaint_in_db')
    def test_csv_empty_narratives_skipped(self, mock_create_complaint):
        """Test: Rows with empty narratives are skipped"""
        mock_create_complaint.side_effect = ['CAS-00001', 'CAS-00003']
        
        csv_content = b"""id,narrative
1,Valid complaint text
2,
3,Another valid complaint"""
        
        result = lambda_function.process_csv_excel_file(csv_content, 'csv', 'test-file-id')
        
        assert result['success'] is True
        assert result['total_rows'] == 3
        assert result['processed_complaints'] == 2  # Row 2 skipped due to empty text
    
    @patch('upload_complaints.lambda_function.create_complaint_in_db')
    def test_excel_file_processing(self, mock_create_complaint):
        """Test: Excel file processing"""
        mock_create_complaint.side_effect = ['CAS-00001', 'CAS-00002', 'CAS-00003']
        
        # Create a simple Excel file in memory
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'narrative': ['First complaint', 'Second complaint', 'Third complaint']
        })
        
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_content = excel_buffer.getvalue()
        
        result = lambda_function.process_csv_excel_file(excel_content, 'xlsx', 'test-file-id')
        
        assert result['success'] is True
        assert result['processed_complaints'] == 3
    
    def test_process_csv_excel_file_too_many_columns(self):
        """Test: Reject CSV with more than 2 columns"""
        csv_content = b'complaint_id,narrative,extra_column\nOLD-001,Test narrative,Extra data'
        
        result = lambda_function.process_csv_excel_file(csv_content, 'csv', 'test-file-id')
        
        assert result['success'] is False
        assert 'CSV header must have exactly 2 columns' in result['message']
    
    def test_csv_missing_narrative_column(self):
        """Test: Reject CSV without narrative column"""
        csv_content = b'complaint_id,description\nOLD-001,Test description'
        
        result = lambda_function.process_csv_excel_file(csv_content, 'csv', 'test-file-id')
        
        assert result['success'] is False
        assert 'must have a column named "narrative"' in result['message']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])