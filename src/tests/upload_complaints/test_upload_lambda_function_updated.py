import pytest
import json
import os
import sys
import io
from unittest.mock import Mock, patch
import pandas as pd

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
            'content': b'Case ID,Narrative Text\nCAS-001,Test complaint narrative',
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
        mock_sqs.send_message.assert_called_once()  # Only one complaint from CSV

    @patch.dict(os.environ, {
        'S3_BUCKET_NAME': 'test-bucket',
        'SQS_QUEUE_NAME': 'test-queue'
    })
    @patch('boto3.client')
    @patch('upload_complaints.lambda_function.parse_multipart_manual')
    def test_successful_pdf_upload_async(self, mock_parse, mock_boto3):
        """Test: Successful PDF upload with async lambda invocation"""
        # Mock AWS clients
        mock_s3 = Mock()
        mock_sqs = Mock()
        mock_lambda = Mock()
        mock_boto3.side_effect = lambda service: {
            's3': mock_s3,
            'sqs': mock_sqs,
            'lambda': mock_lambda
        }[service]
        
        mock_sqs.get_queue_url.return_value = {'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123456789/test-queue'}

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
        
        # Verify lambda extraction was called asynchronously
        mock_lambda.invoke.assert_called_once()
        call_args = mock_lambda.invoke.call_args
        assert call_args[1]['InvocationType'] == 'Event'  # Async invocation
        assert call_args[1]['FunctionName'] == 'qms-dev-extract-complaints'
        
        # Verify S3 upload happened
        mock_s3.put_object.assert_called_once()
        
        # Verify no SQS messages sent from upload lambda (handled by extract lambda now)
        mock_sqs.send_message.assert_not_called()

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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])