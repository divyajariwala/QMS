import pytest
import json
import os
import sys
from unittest.mock import Mock, patch

# Add src directory to path for importing lambda_function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'app'))
from upload_complaints import lambda_function


class TestLambdaHandler:
    """Unit tests for the main lambda_handler function"""

    @patch.dict(os.environ, {
        'S3_BUCKET_NAME': 'test-bucket',
        'SQS_QUEUE_NAME': 'test-queue'
    })
    @patch('boto3.client')
    @patch('upload_complaints.lambda_function.parse_multipart_manual')
    def test_successful_csv_upload(self, mock_parse, mock_boto3):
        """Test: Successful CSV file upload"""
        # Mock AWS clients
        mock_s3 = Mock()
        mock_sqs = Mock()
        mock_boto3.side_effect = lambda service: mock_s3 if service == 's3' else mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789/test-queue'}
        mock_sqs.send_message.return_value = {'MessageId': 'test-123'}

        # Mock CSV
        mock_parse.return_value = {
            'filename': 'data.csv',
            'content': b'name,age\nJohn,30\nMaria,25',
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

        mock_s3.put_object.assert_called_once()
        mock_sqs.send_message.assert_called_once()

    @patch.dict(os.environ, {
        'S3_BUCKET_NAME': 'test-bucket',
        'SQS_QUEUE_NAME': 'test-queue'
    })
    @patch('boto3.client')
    @patch('upload_complaints.lambda_function.parse_multipart_manual')
    def test_successful_xlsx_upload(self, mock_parse, mock_boto3):
        """Test: Successful Excel file upload"""
        # Mock AWS clients
        mock_s3 = Mock()
        mock_sqs = Mock()
        mock_boto3.side_effect = lambda service: mock_s3 if service == 's3' else mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789/test-queue'}
        mock_sqs.send_message.return_value = {'MessageId': 'test-456'}

        # Mock Excel file
        mock_parse.return_value = {
            'filename': 'report.xlsx',
            'content': b'\x50\x4b\x03\x04',  # Typical Excel bytes
            'content_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'field_name': 'file'
        }

        event = {
            'body': 'fake-excel-content',
            'isBase64Encoded': False,
            'headers': {'content-type': 'multipart/form-data; boundary=test'}
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['data']['filename'] == 'report.xlsx'

    @patch.dict(os.environ, {
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
        'S3_BUCKET_NAME': 'test-bucket',
        'SQS_QUEUE_NAME': 'test-queue'
    })
    @patch('boto3.client')
    def test_wrong_content_type(self, mock_boto3):
        """Test: Error with incorrect Content-Type"""
        # Mock AWS clients
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
        assert "multipart/form-data" in body['message']

    @patch.dict(os.environ, {
        'S3_BUCKET_NAME': 'test-bucket',
        'SQS_QUEUE_NAME': 'test-queue'
    })
    @patch('boto3.client')
    @patch('upload_complaints.lambda_function.parse_multipart_manual')
    def test_invalid_file_extension(self, mock_parse, mock_boto3):
        """Test: Error with not allowed extension"""
        # Mock AWS clients
        mock_sqs = Mock()
        mock_boto3.side_effect = lambda service: mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789/test-queue'}

        mock_parse.return_value = {
            'filename': 'file.txt',  # Not allowed
            'content': b'content',
            'content_type': 'text/plain',
            'field_name': 'file'
        }

        event = {
            'body': 'test',
            'headers': {'content-type': 'multipart/form-data; boundary=test'}
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert "Invalid file format" in body['message']

    @patch.dict(os.environ, {
        'S3_BUCKET_NAME': 'test-bucket',
        'SQS_QUEUE_NAME': 'test-queue'
    })
    @patch('boto3.client')
    @patch('upload_complaints.lambda_function.parse_multipart_manual')
    def test_empty_file(self, mock_parse, mock_boto3):
        """Test: Error with empty file"""
        # Mock AWS clients
        mock_sqs = Mock()
        mock_boto3.side_effect = lambda service: mock_sqs
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789/test-queue'}

        mock_parse.return_value = {
            'filename': 'empty.csv',
            'content': b'',  # Empty
            'content_type': 'text/csv',
            'field_name': 'file'
        }

        event = {
            'body': 'test',
            'headers': {'content-type': 'multipart/form-data; boundary=test'}
        }

        result = lambda_function.lambda_handler(event, {})

        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert body['message'] == "File is empty"


class TestParseMultipart:
    """Tests for multipart parsing function"""

    def test_parse_csv_file(self):
        """Test: CSV file parsing"""
        # Simulated multipart data
        boundary = "----WebKitFormBoundary123"
        content_type = f"multipart/form-data; boundary={boundary}"

        body = (
            f"------WebKitFormBoundary123\r\n"
            f"Content-Disposition: form-data; name=\"file\"; filename=\"test.csv\"\r\n"
            f"Content-Type: text/csv\r\n"
            f"\r\n"
            f"name,age\nJohn,30\n"
            f"------WebKitFormBoundary123--\r\n"
        ).encode()

        result = lambda_function.parse_multipart_manual(body, content_type)

        assert result is not None
        assert result['filename'] == 'test.csv'
        assert result['content'] == b'name,age\nJohn,30'
        assert result['content_type'] == 'text/csv'

    def test_parse_no_file(self):
        """Test: No file in multipart data"""
        boundary = "----WebKitFormBoundary123"
        content_type = f"multipart/form-data; boundary={boundary}"

        # Only text field
        body = (
            f"------WebKitFormBoundary123\r\n"
            f"Content-Disposition: form-data; name=\"field\"\r\n"
            f"\r\n"
            f"value\r\n"
            f"------WebKitFormBoundary123--\r\n"
        ).encode()

        result = lambda_function.parse_multipart_manual(body, content_type)
        assert result is None

    def test_parse_no_boundary(self):
        """Test: Content-Type without boundary"""
        body = b"data"
        content_type = "multipart/form-data"

        result = lambda_function.parse_multipart_manual(body, content_type)
        assert result is None


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
        assert lambda_function._get_file_extension('test') == ''  # No extension returns empty string
        assert lambda_function._get_file_extension('') == 'unknown'  # Empty filename returns 'unknown'
        assert lambda_function._get_file_extension(None) == 'unknown'  # None returns 'unknown'

    def test_is_allowed_file(self):
        """Test: Validate allowed extensions"""
        assert lambda_function._is_allowed_file('test.csv') is True
        assert lambda_function._is_allowed_file('test.xlsx') is True
        assert lambda_function._is_allowed_file('test.pdf') is True
        assert lambda_function._is_allowed_file('test.xls') is True
        assert lambda_function._is_allowed_file('test.txt') is False
        assert lambda_function._is_allowed_file('') is False

    def test_response_function(self):
        """Test: HTTP response function"""
        # Successful response
        result = lambda_function._response(200, "OK", {"key": "value"})
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
        assert body['message'] == "OK"

        # Error response
        result = lambda_function._response(400, "Error")
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert body['success'] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])