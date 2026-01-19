import pytest
import json
import os
import sys
import io
import base64
import importlib.util
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

# Mock dependencies before importing
sys.modules['psycopg'] = Mock()
sys.modules['psycopg.rows'] = Mock()
sys.modules['secrets_util'] = Mock()
sys.modules['audit_logger'] = Mock()

# Load lambda_function using importlib to avoid module name conflicts
lambda_function_path = os.path.join(
    os.path.dirname(__file__), '..', '..', 'app', 'upload_complaints', 'lambda_function.py'
)
spec = importlib.util.spec_from_file_location("upload_complaints_lambda", lambda_function_path)
lambda_function = importlib.util.module_from_spec(spec)
sys.modules['upload_complaints_lambda'] = lambda_function
spec.loader.exec_module(lambda_function)


class TestLambdaHandler:
    """Unit tests for the main lambda_handler function"""

    @patch.dict(os.environ, {
        'env': 'dev',
        'S3_BUCKET_NAME': 'test-bucket',
        'SQS_QUEUE_NAME': 'test-queue',
        'db_secret_base_name': 'aurora-postgres-master',
        'db_region': 'us-east-1'
    })
    @patch.object(lambda_function, 'get_secret')
    @patch('boto3.client')
    @patch.object(lambda_function, 'parse_multipart_manual')
    @patch.object(lambda_function, 'create_file_record')
    @patch.object(lambda_function, 'create_complaint_in_db')
    def test_successful_csv_upload(self, mock_create_complaint, mock_create_file, mock_parse, mock_boto3, mock_get_secret):
        """Test: Successful CSV file upload with database integration"""
        # Mock secrets
        mock_get_secret.return_value = {
            'host': 'test-host',
            'port': 5432,
            'dbname': 'test-db',
            'username': 'test-user',
            'password': 'test-pass'
        }
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
    @patch.object(lambda_function, 'get_secret')
    @patch('boto3.client')
    @patch.object(lambda_function, 'parse_multipart_manual')
    @patch.object(lambda_function, 'create_file_record')
    @patch.object(lambda_function, 'create_complaint_in_db')
    def test_successful_pdf_upload_sqs(self, mock_create_complaint, mock_create_file, mock_parse, mock_boto3, mock_get_secret):
        """Test: Successful PDF upload with SQS message"""
        # Mock secrets
        mock_get_secret.return_value = {
            'host': 'test-host',
            'port': 5432,
            'dbname': 'test-db',
            'username': 'test-user',
            'password': 'test-pass'
        }
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
    @patch.object(lambda_function, 'get_secret')
    @patch('boto3.client')
    @patch.object(lambda_function, 'parse_multipart_manual')
    @patch.object(lambda_function, 'create_file_record')
    @patch.object(lambda_function, 'create_complaint_in_db')
    def test_csv_with_extra_columns(self, mock_create_complaint, mock_create_file, mock_parse, mock_boto3, mock_get_secret):
        """Test: CSV file with more than 2 columns is accepted if narrative column exists"""
        # Mock secrets
        mock_get_secret.return_value = {
            'host': 'test-host',
            'port': 5432,
            'dbname': 'test-db',
            'username': 'test-user',
            'password': 'test-pass'
        }
        mock_s3 = Mock()
        mock_sqs = Mock()
        mock_boto3.side_effect = lambda service: mock_s3 if service == 's3' else mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789/test-queue'}
        mock_sqs.send_message.return_value = {'MessageId': 'test-123'}
        mock_create_complaint.return_value = 'CAS-00001'
        
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

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True


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
    
    @patch.object(lambda_function, 'get_connection_string')
    @patch.object(lambda_function, 'psycopg')
    def test_create_file_record(self, mock_psycopg, mock_get_conn):
        """Test: Create file record in database"""
        mock_get_conn.return_value = 'mock_connection_string'
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=False)
        mock_psycopg.connect.return_value = mock_conn
        
        lambda_function.create_file_record(
            'test-file-id', 
            'test.pdf', 
            's3://bucket/key', 
            'test-user'
        )
        
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
    
    @patch.object(lambda_function, 'get_connection_string')
    @patch.object(lambda_function, 'psycopg')
    def test_create_complaint_in_db(self, mock_psycopg, mock_get_conn):
        """Test: Create complaint record in database with text_extracted set to false"""
        mock_get_conn.return_value = 'mock_connection_string'
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=False)
        mock_psycopg.connect.return_value = mock_conn
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
    
    @patch.object(lambda_function, 'create_complaint_in_db')
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
    
    @patch.object(lambda_function, 'create_complaint_in_db')
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
    
    @patch.object(lambda_function, 'create_complaint_in_db')
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
    
    @patch.object(lambda_function, 'create_complaint_in_db')
    def test_csv_with_long_narrative(self, mock_create_complaint):
        """Test: CSV with long narrative text (1500+ chars) with punctuation"""
        mock_create_complaint.return_value = 'CAS-00001'
        
        long_narrative = "This is a very long complaint narrative with over 1500 characters. " * 30 + "It contains commas, periods, quotes 'like this', and other punctuation marks! The system should handle this as one complete string."
        csv_content = f'id,narrative\n1,"{long_narrative}"'.encode('utf-8')
        
        result = lambda_function.process_csv_excel_file(csv_content, 'csv', 'test-file-id')
        
        assert result['success'] is True
        assert result['processed_complaints'] == 1
        assert long_narrative in result['complaints'][0]['narrative_text']
    
    @patch.object(lambda_function, 'create_complaint_in_db')
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
    
    def test_csv_missing_narrative_header(self):
        """Test: CSV without narrative column should be rejected"""
        csv_content = b"""id,description
1,Some description"""
        
        result = lambda_function.process_csv_excel_file(csv_content, 'csv', 'test-file-id')
        
        assert result['success'] is False
        assert 'must have a column named "narrative"' in result['message']
    
    @patch.object(lambda_function, 'create_complaint_in_db')
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
    
    @patch.object(lambda_function, 'create_complaint_in_db')
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
    
    @patch.object(lambda_function, 'create_complaint_in_db')
    def test_process_csv_with_multiple_columns(self, mock_create_complaint):
        """Test: Accept CSV with multiple columns if narrative exists"""
        mock_create_complaint.return_value = 'CAS-00001'
        
        csv_content = b'complaint_id,narrative,extra_column\nOLD-001,Test narrative,Extra data'
        
        result = lambda_function.process_csv_excel_file(csv_content, 'csv', 'test-file-id')
        
        assert result['success'] is True
        assert result['processed_complaints'] == 1
    
    def test_csv_missing_narrative_column(self):
        """Test: Reject CSV without narrative column"""
        csv_content = b'complaint_id,description\nOLD-001,Test description'
        
        result = lambda_function.process_csv_excel_file(csv_content, 'csv', 'test-file-id')
        
        assert result['success'] is False
        assert 'must have a column named "narrative"' in result['message']


class TestErrorHandling:
    """Tests for error handling scenarios"""
    
    @patch.dict(os.environ, {
        'env': 'dev',
        'S3_BUCKET_NAME': 'test-bucket',
        'SQS_QUEUE_NAME': 'test-queue'
    })
    @patch('boto3.client')
    def test_queue_not_found(self, mock_boto3):
        """Test: Error when SQS queue doesn't exist"""
        mock_sqs = Mock()
        mock_boto3.side_effect = lambda service: mock_sqs
        mock_sqs.get_queue_url.side_effect = Exception("Queue not found")
        
        event = {
            'body': 'test',
            'headers': {'content-type': 'multipart/form-data; boundary=test'}
        }
        
        result = lambda_function.lambda_handler(event, {})
        
        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert 'not found' in body['message'].lower()
    
    @patch.dict(os.environ, {
        'env': 'dev',
        'S3_BUCKET_NAME': 'test-bucket',
        'SQS_QUEUE_NAME': 'test-queue'
    })
    @patch('boto3.client')
    def test_invalid_content_type(self, mock_boto3):
        """Test: Error when content-type is not multipart/form-data"""
        mock_sqs = Mock()
        mock_boto3.side_effect = lambda service: mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789/test-queue'}
        
        event = {
            'body': 'test',
            'headers': {'content-type': 'application/json'}
        }
        
        result = lambda_function.lambda_handler(event, {})
        
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert 'Content-Type must be multipart/form-data' in body['message']
    
    @patch.dict(os.environ, {
        'env': 'dev',
        'S3_BUCKET_NAME': 'test-bucket',
        'SQS_QUEUE_NAME': 'test-queue'
    })
    @patch('boto3.client')
    @patch.object(lambda_function, 'parse_multipart_manual')
    def test_file_too_large(self, mock_parse, mock_boto3):
        """Test: Error when file exceeds maximum size"""
        mock_sqs = Mock()
        mock_boto3.side_effect = lambda service: mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789/test-queue'}
        
        # Create a body larger than MAX_FILE_SIZE (50MB)
        large_body = b'x' * (51 * 1024 * 1024)
        
        event = {
            'body': large_body,
            'isBase64Encoded': False,
            'headers': {'content-type': 'multipart/form-data; boundary=test'}
        }
        
        result = lambda_function.lambda_handler(event, {})
        
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert 'File too large' in body['message']
    
    @patch.dict(os.environ, {
        'env': 'dev',
        'S3_BUCKET_NAME': 'test-bucket',
        'SQS_QUEUE_NAME': 'test-queue'
    })
    @patch('boto3.client')
    @patch.object(lambda_function, 'parse_multipart_manual')
    def test_no_file_in_multipart(self, mock_parse, mock_boto3):
        """Test: Error when no file found in multipart data"""
        mock_sqs = Mock()
        mock_boto3.side_effect = lambda service: mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789/test-queue'}
        
        mock_parse.return_value = None
        
        event = {
            'body': 'multipart-data',
            'isBase64Encoded': False,
            'headers': {'content-type': 'multipart/form-data; boundary=test'}
        }
        
        result = lambda_function.lambda_handler(event, {})
        
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert 'No valid file found' in body['message']
    
    @patch.dict(os.environ, {
        'env': 'dev',
        'S3_BUCKET_NAME': 'test-bucket',
        'SQS_QUEUE_NAME': 'test-queue'
    })
    @patch('boto3.client')
    @patch.object(lambda_function, 'parse_multipart_manual')
    def test_invalid_file_extension(self, mock_parse, mock_boto3):
        """Test: Error when file has invalid extension"""
        mock_sqs = Mock()
        mock_boto3.side_effect = lambda service: mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789/test-queue'}
        
        mock_parse.return_value = {
            'filename': 'test.txt',
            'content': b'test content',
            'content_type': 'text/plain',
            'field_name': 'file'
        }
        
        event = {
            'body': 'multipart-data',
            'isBase64Encoded': False,
            'headers': {'content-type': 'multipart/form-data; boundary=test'}
        }
        
        result = lambda_function.lambda_handler(event, {})
        
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert 'Invalid file format' in body['message']
    
    @patch.dict(os.environ, {
        'env': 'dev',
        'S3_BUCKET_NAME': 'test-bucket',
        'SQS_QUEUE_NAME': 'test-queue'
    })
    @patch('boto3.client')
    @patch.object(lambda_function, 'parse_multipart_manual')
    def test_empty_file(self, mock_parse, mock_boto3):
        """Test: Error when file is empty"""
        mock_sqs = Mock()
        mock_boto3.side_effect = lambda service: mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789/test-queue'}
        
        mock_parse.return_value = {
            'filename': 'test.csv',
            'content': b'',
            'content_type': 'text/csv',
            'field_name': 'file'
        }
        
        event = {
            'body': 'multipart-data',
            'isBase64Encoded': False,
            'headers': {'content-type': 'multipart/form-data; boundary=test'}
        }
        
        result = lambda_function.lambda_handler(event, {})
        
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert 'File is empty' in body['message']
    
    @patch.dict(os.environ, {
        'env': 'dev',
        'S3_BUCKET_NAME': 'test-bucket',
        'SQS_QUEUE_NAME': 'test-queue'
    })
    @patch.object(lambda_function, 'get_secret')
    @patch('boto3.client')
    @patch.object(lambda_function, 'parse_multipart_manual')
    @patch.object(lambda_function, 'create_file_record')
    @patch.object(lambda_function, 'process_csv_excel_file')
    def test_csv_processing_error(self, mock_process, mock_create_file, mock_parse, mock_boto3, mock_get_secret):
        """Test: Error during CSV processing"""
        mock_get_secret.return_value = {
            'host': 'test-host',
            'port': 5432,
            'dbname': 'test-db',
            'username': 'test-user',
            'password': 'test-pass'
        }
        mock_s3 = Mock()
        mock_sqs = Mock()
        mock_boto3.side_effect = lambda service: mock_s3 if service == 's3' else mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789/test-queue'}
        
        mock_parse.return_value = {
            'filename': 'test.csv',
            'content': b'invalid,csv,data',
            'content_type': 'text/csv',
            'field_name': 'file'
        }
        
        mock_process.return_value = {
            'success': False,
            'message': 'CSV parsing error'
        }
        
        event = {
            'body': 'multipart-data',
            'isBase64Encoded': False,
            'headers': {'content-type': 'multipart/form-data; boundary=test'}
        }
        
        result = lambda_function.lambda_handler(event, {})
        
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert 'CSV parsing error' in body['message']
    
    @patch.object(lambda_function, 'get_connection_string')
    @patch.object(lambda_function, 'psycopg')
    def test_create_file_record_error(self, mock_psycopg, mock_get_conn):
        """Test: Database error when creating file record"""
        mock_get_conn.return_value = 'mock_connection_string'
        mock_psycopg.connect.side_effect = Exception("Database connection failed")
        
        with pytest.raises(Exception) as exc_info:
            lambda_function.create_file_record('test-id', 'test.pdf', 's3://bucket/key', 'user')
        
        assert "Database connection failed" in str(exc_info.value)
    
    @patch.object(lambda_function, 'get_connection_string')
    @patch.object(lambda_function, 'psycopg')
    def test_create_complaint_db_error(self, mock_psycopg, mock_get_conn):
        """Test: Database error when creating complaint"""
        mock_get_conn.return_value = 'mock_connection_string'
        mock_psycopg.connect.side_effect = Exception("Database error")
        
        with pytest.raises(Exception) as exc_info:
            lambda_function.create_complaint_in_db('test-file-id')
        
        assert "Database error" in str(exc_info.value)


class TestBase64Encoding:
    """Tests for base64 encoding scenarios"""
    
    @patch.dict(os.environ, {
        'env': 'dev',
        'S3_BUCKET_NAME': 'test-bucket',
        'SQS_QUEUE_NAME': 'test-queue'
    })
    @patch.object(lambda_function, 'get_secret')
    @patch('boto3.client')
    @patch.object(lambda_function, 'parse_multipart_manual')
    @patch.object(lambda_function, 'create_file_record')
    @patch.object(lambda_function, 'create_complaint_in_db')
    def test_base64_encoded_body(self, mock_create_complaint, mock_create_file, mock_parse, mock_boto3, mock_get_secret):
        """Test: Handle base64 encoded body"""
        mock_get_secret.return_value = {
            'host': 'test-host',
            'port': 5432,
            'dbname': 'test-db',
            'username': 'test-user',
            'password': 'test-pass'
        }
        mock_s3 = Mock()
        mock_sqs = Mock()
        mock_boto3.side_effect = lambda service: mock_s3 if service == 's3' else mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789/test-queue'}
        mock_sqs.send_message.return_value = {'MessageId': 'test-123'}
        mock_create_complaint.return_value = 'CAS-00001'
        
        # Base64 encode the body
        original_body = b'multipart-fake-content'
        encoded_body = base64.b64encode(original_body).decode('utf-8')
        
        mock_parse.return_value = {
            'filename': 'test.pdf',
            'content': b'%PDF-1.4 content',
            'content_type': 'application/pdf',
            'field_name': 'file'
        }
        
        event = {
            'body': encoded_body,
            'isBase64Encoded': True,
            'headers': {'content-type': 'multipart/form-data; boundary=test'}
        }
        
        result = lambda_function.lambda_handler(event, {})
        
        assert result['statusCode'] == 200


class TestUserExtraction:
    """Tests for user extraction from event"""
    
    def test_get_user_from_cognito(self):
        """Test: Extract user from Cognito claims"""
        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {
                        'email': 'test@example.com'
                    }
                }
            }
        }
        
        user = lambda_function._get_user_from_event(event)
        assert user == 'test@example.com'
    
    def test_get_user_from_header(self):
        """Test: Extract user from custom header"""
        event = {
            'headers': {
                'x-user-email': 'header@example.com'
            }
        }
        
        user = lambda_function._get_user_from_event(event)
        assert user == 'header@example.com'
    
    def test_get_user_anonymous(self):
        """Test: Return anonymous when no user info"""
        event = {}
        
        user = lambda_function._get_user_from_event(event)
        assert user == 'anonymous'


class TestMultipartParsing:
    """Tests for multipart parsing edge cases"""
    
    def test_parse_multipart_no_boundary(self):
        """Test: Error when no boundary in content-type"""
        body = b'test-content'
        content_type = 'multipart/form-data'
        
        result = lambda_function.parse_multipart_manual(body, content_type)
        
        assert result is None
    
    def test_parse_multipart_with_boundary(self):
        """Test: Parse multipart with proper boundary"""
        boundary = b'----WebKitFormBoundary'
        body = b'------WebKitFormBoundary\r\nContent-Disposition: form-data; name="file"; filename="test.pdf"\r\nContent-Type: application/pdf\r\n\r\n%PDF-1.4 content\r\n------WebKitFormBoundary--'
        content_type = 'multipart/form-data; boundary=----WebKitFormBoundary'
        
        result = lambda_function.parse_multipart_manual(body, content_type)
        
        assert result is not None
        assert result['filename'] == 'test.pdf'
        assert b'%PDF-1.4 content' in result['content']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])