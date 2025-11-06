import pytest
import json
import io
import base64
import os
import sys
from unittest.mock import Mock, patch, MagicMock, mock_open
from PIL import Image

# Add src directory to path for importing lambda_function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'app'))
from extract_complaints import lambda_function


class TestLambdaHandler:
    """Unit tests for the main lambda_handler function"""

    @patch.dict(os.environ, {'SQS_QUEUE_NAME': 'test-queue'})
    @patch('extract_complaints.lambda_function.boto3.client')
    @patch('extract_complaints.lambda_function.fetch_pdf_from_s3')
    @patch('extract_complaints.lambda_function.pdf_to_images')
    @patch('extract_complaints.lambda_function.images_to_base64')
    @patch('extract_complaints.lambda_function.prompt_constructor')
    @patch('extract_complaints.lambda_function.process_with_bedrock_conversations')
    @patch('extract_complaints.lambda_function.create_complaint_message_from_output')
    def test_successful_processing_with_sqs(self, mock_create_complaint, mock_bedrock, mock_prompt, 
                                          mock_base64, mock_pdf_to_images, mock_fetch_pdf, mock_boto3):
        """Test: Successful PDF processing with SQS message sending"""
        # Mock AWS clients
        mock_bedrock_client = Mock()
        mock_sqs_client = Mock()
        mock_boto3.side_effect = lambda service: {
            'bedrock-runtime': mock_bedrock_client,
            'sqs': mock_sqs_client
        }[service]
        
        # Mock SQS
        mock_sqs_client.get_queue_url.return_value = {'QueueUrl': 'https://sqs.us-east-1.amazonaws.com/123/test-queue'}
        mock_sqs_client.send_message.return_value = {'MessageId': 'msg-123'}
        
        # Mock return values
        mock_fetch_pdf.return_value = b'fake_pdf_data'
        mock_pdf_to_images.return_value = [Mock()]
        mock_base64.return_value = ['base64_image']
        mock_prompt.return_value = [{'role': 'user', 'content': []}]
        mock_bedrock.return_value = {'case_id': 'TEST-001', 'narrative': 'Test narrative'}
        mock_create_complaint.return_value = {
            'complaint_id': 'CAS-123456789',
            'narrative': 'Test narrative',
            'status': 'IN-REVIEW'
        }
        
        event = {
            "s3path": "s3://test-bucket/test.pdf",
            "file_id": "file-123",
            "filename": "test.pdf",
            "created_by": "test-user"
        }
        
        result = lambda_function.lambda_handler(event, {})
        
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
        assert body['result'] == {'case_id': 'TEST-001', 'narrative': 'Test narrative'}
        assert body['complaint_id'] == 'CAS-123456789'
        assert 'message_id' in body
        
        # Verify SQS message was sent
        mock_sqs_client.send_message.assert_called_once()
        call_args = mock_sqs_client.send_message.call_args
        assert 'MessageBody' in call_args[1]
        assert 'MessageAttributes' in call_args[1]

    def test_missing_s3path(self):
        """Test: Error when s3path is missing"""
        event = {}
        result = lambda_function.lambda_handler(event, {})
        
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert body['success'] is False
        assert "Missing required field: s3path" in body['error']

    def test_invalid_s3path_format(self):
        """Test: Error with invalid S3 path format"""
        event = {"s3path": "invalid-path"}
        result = lambda_function.lambda_handler(event, {})
        
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert body['success'] is False
        assert "Invalid S3 path format" in body['error']


class TestComplaintMessageCreation:
    """Tests for complaint message creation functionality"""

    def test_create_complaint_message_from_output(self):
        """Test: Create complaint message from extraction output"""
        output_data = {
            'case_id': 'RGL22-000433',
            'narrative': 'Test narrative',
            'criticality': 'High',
            'report_type': 'Spontaneous',
            'primary_reporter': {'name': 'John Doe'},
            'patient_name': 'Jane Smith'
        }

        result = lambda_function.create_complaint_message_from_output(
            output_data, 'file-123', 'test.pdf', 'test-user'
        )

        assert result['complaint_id'] == 'RGL22-000433'  # Uses case_id from input
        assert result['narrative'] == 'Test narrative'
        assert result['criticality'] == 'High'
        assert result['status'] == 'IN-REVIEW'
        assert result['created_by'] == 'test-user'
        assert result['metadata']['file_id'] == 'file-123'
        assert result['metadata']['filename'] == 'test.pdf'

    def test_create_complaint_message_missing_case_id(self):
        """Test: Generate complaint code when case_id is missing"""
        output_data = {
            'narrative': 'Test narrative without case ID',
            'criticality': 'Medium'
        }

        result = lambda_function.create_complaint_message_from_output(
            output_data, 'file-456', 'test2.pdf', 'user2'
        )

        assert result['complaint_id'].startswith('CAS-')  # Generated code
        assert result['narrative'] == 'Test narrative without case ID'
        assert result['criticality'] == 'Medium'


class TestComplaintCodeGeneration:
    """Tests for complaint code generation functions"""

    def test_generate_complaint_code(self):
        """Test: Generate complaint code with timestamp_random strategy"""
        code = lambda_function.generate_complaint_code()
        
        assert code.startswith('CAS-')
        assert len(code) > 10  # Should be reasonably long
        
        # Generate another to ensure uniqueness
        code2 = lambda_function.generate_complaint_code()
        assert code != code2


class TestValidateEvent:
    """Tests for validate_event function"""

    def test_valid_event(self):
        """Test: Valid event with s3path"""
        event = {"s3path": "s3://bucket/file.pdf"}
        result = lambda_function.validate_event(event)
        assert result == "s3://bucket/file.pdf"

    def test_missing_s3path(self):
        """Test: Event missing s3path field"""
        with pytest.raises(ValueError, match="Missing required field: s3path"):
            lambda_function.validate_event({})

    def test_invalid_s3_format(self):
        """Test: Invalid S3 path format"""
        with pytest.raises(ValueError, match="Invalid S3 path format"):
            lambda_function.validate_event({"s3path": "invalid-path"})


class TestFetchPdfFromS3:
    """Tests for fetch_pdf_from_s3 function"""

    @patch('extract_complaints.lambda_function.boto3.client')
    def test_successful_fetch(self, mock_boto3):
        """Test: Successfully fetch PDF from S3"""
        mock_s3 = Mock()
        mock_boto3.return_value = mock_s3
        mock_s3.head_object.return_value = {'ContentLength': 1024 * 1024}  # 1MB
        mock_s3.get_object.return_value = {'Body': Mock(read=Mock(return_value=b'pdf_data'))}
        
        result = lambda_function.fetch_pdf_from_s3('s3://bucket/file.pdf')
        
        assert result == b'pdf_data'
        mock_s3.head_object.assert_called_once_with(Bucket='bucket', Key='file.pdf')
        mock_s3.get_object.assert_called_once_with(Bucket='bucket', Key='file.pdf')

    @patch('extract_complaints.lambda_function.boto3.client')
    def test_file_too_large(self, mock_boto3):
        """Test: PDF file exceeds size limit"""
        mock_s3 = Mock()
        mock_boto3.return_value = mock_s3
        mock_s3.head_object.return_value = {'ContentLength': 100 * 1024 * 1024}  # 100MB
        
        with pytest.raises(ValueError, match="PDF too large"):
            lambda_function.fetch_pdf_from_s3('s3://bucket/large.pdf')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])