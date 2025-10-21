import pytest
import json
import io
import base64
import os
import sys
from unittest.mock import Mock, patch, MagicMock, mock_open
from PIL import Image

# Add src directory to path for importing lambda_function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from extract_complaints import lambda_function


class TestLambdaHandler:
    """Unit tests for the main lambda_handler function"""

    @patch('extract_complaints.lambda_function.boto3.client')
    @patch('extract_complaints.lambda_function.fetch_pdf_from_s3')
    @patch('extract_complaints.lambda_function.pdf_to_images')
    @patch('extract_complaints.lambda_function.images_to_base64')
    @patch('extract_complaints.lambda_function.prompt_constructor')
    @patch('extract_complaints.lambda_function.process_with_bedrock_conversations')
    def test_successful_processing(self, mock_bedrock, mock_prompt, mock_base64, 
                                 mock_pdf_to_images, mock_fetch_pdf, mock_boto3):
        """Test: Successful PDF processing"""
        # Mock return values
        mock_fetch_pdf.return_value = b'fake_pdf_data'
        mock_pdf_to_images.return_value = [Mock()]
        mock_base64.return_value = ['base64_image']
        mock_prompt.return_value = [{'role': 'user', 'content': []}]
        mock_bedrock.return_value = {'extracted': 'data'}
        
        event = {"s3path": "s3://test-bucket/test.pdf"}
        
        result = lambda_function.lambda_handler(event, {})
        
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
        assert body['result'] == {'extracted': 'data'}

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

    @patch('extract_complaints.lambda_function.fetch_pdf_from_s3')
    def test_internal_error(self, mock_fetch_pdf):
        """Test: Internal server error handling"""
        mock_fetch_pdf.side_effect = Exception("S3 error")
        
        event = {"s3path": "s3://test-bucket/test.pdf"}
        result = lambda_function.lambda_handler(event, {})
        
        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert body['success'] is False
        assert body['error'] == 'Internal error'


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

    def test_non_dict_event(self):
        """Test: Non-dictionary event"""
        with pytest.raises(ValueError, match="Missing required field: s3path"):
            lambda_function.validate_event("not a dict")


class TestLoadPromptFromFile:
    """Tests for load_prompt_from_file function"""

    @patch('builtins.open', mock_open(read_data='test prompt content'))
    def test_successful_load(self):
        """Test: Successfully load prompt file"""
        result = lambda_function.load_prompt_from_file('prompt.txt')
        assert result == 'test prompt content'

    @patch('builtins.open', side_effect=FileNotFoundError())
    def test_file_not_found(self, mock_open):
        """Test: File not found error"""
        with pytest.raises(FileNotFoundError):
            lambda_function.load_prompt_from_file('nonexistent.txt')


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

    @patch('extract_complaints.lambda_function.boto3.client')
    def test_s3_error(self, mock_boto3):
        """Test: S3 client error"""
        mock_s3 = Mock()
        mock_boto3.return_value = mock_s3
        mock_s3.head_object.side_effect = Exception("S3 error")
        
        with pytest.raises(Exception):
            lambda_function.fetch_pdf_from_s3('s3://bucket/file.pdf')


class TestPdfToImages:
    """Tests for pdf_to_images function"""

    @patch('extract_complaints.lambda_function.fitz.open')
    def test_successful_conversion(self, mock_fitz_open):
        """Test: Successfully convert PDF to images"""
        # Mock PDF document
        mock_doc = Mock()
        mock_doc.page_count = 2
        mock_page = Mock()
        mock_pixmap = Mock()
        mock_pixmap.tobytes.return_value = b'fake_png_data'
        mock_page.get_pixmap.return_value = mock_pixmap
        mock_doc.__getitem__ = Mock(return_value=mock_page)
        mock_fitz_open.return_value = mock_doc
        
        # Mock PIL Image
        with patch('extract_complaints.lambda_function.Image.open') as mock_image_open:
            mock_image = Mock()
            mock_image_open.return_value = mock_image
            
            result = lambda_function.pdf_to_images(b'pdf_data')
            
            assert len(result) == 2
            assert result[0] == mock_image
            mock_doc.close.assert_called_once()

    @patch('extract_complaints.lambda_function.fitz.open')
    def test_max_pages_limit(self, mock_fitz_open):
        """Test: Respects MAX_PAGES limit"""
        mock_doc = Mock()
        mock_doc.page_count = 50  # More than MAX_PAGES (20)
        mock_page = Mock()
        mock_pixmap = Mock()
        mock_pixmap.tobytes.return_value = b'fake_png_data'
        mock_page.get_pixmap.return_value = mock_pixmap
        mock_doc.__getitem__ = Mock(return_value=mock_page)
        mock_fitz_open.return_value = mock_doc
        
        with patch('extract_complaints.lambda_function.Image.open') as mock_image_open:
            mock_image_open.return_value = Mock()
            result = lambda_function.pdf_to_images(b'pdf_data')
            assert len(result) == lambda_function.MAX_PAGES


class TestImagesToBase64:
    """Tests for images_to_base64 function"""

    def test_successful_conversion(self):
        """Test: Successfully convert images to base64"""
        # Create mock image
        mock_image = Mock()
        mock_buffer = io.BytesIO(b'fake_image_data')
        
        with patch('io.BytesIO', return_value=mock_buffer):
            result = lambda_function.images_to_base64([mock_image])
            
            expected_base64 = base64.b64encode(b'fake_image_data').decode('utf8')
            assert result == [expected_base64]
            mock_image.save.assert_called_once_with(mock_buffer, format='PNG')


class TestPromptConstructor:
    """Tests for prompt_constructor function"""

    @patch('extract_complaints.lambda_function.load_prompt_from_file')
    def test_successful_construction(self, mock_load_prompt):
        """Test: Successfully construct prompt with images"""
        mock_load_prompt.return_value = "Test prompt"
        base64_images = ['aGVsbG8=']  # base64 for 'hello'
        
        result = lambda_function.prompt_constructor(base64_images)
        
        assert len(result) == 1
        assert result[0]['role'] == 'user'
        content = result[0]['content']
        assert len(content) == 2  # 1 image + 1 text
        assert content[0]['image']['format'] == 'png'
        assert content[1]['text'] == "Test prompt"


class TestLoadToolSpec:
    """Tests for load_tool_spec function"""

    @patch('builtins.open', mock_open(read_data='{"tool": "spec"}'))
    def test_successful_load(self):
        """Test: Successfully load tool specification"""
        result = lambda_function.load_tool_spec()
        assert result == {"tool": "spec"}

    @patch('builtins.open', side_effect=FileNotFoundError())
    def test_file_not_found(self, mock_open):
        """Test: Tool spec file not found"""
        with pytest.raises(FileNotFoundError):
            lambda_function.load_tool_spec()


class TestProcessWithBedrockConversations:
    """Tests for process_with_bedrock_conversations function"""

    def test_successful_processing(self):
        """Test: Successfully process with Bedrock"""
        mock_bedrock = Mock()
        mock_response = {
            'output': {
                'message': {
                    'content': [
                        {'text': 'some text'},
                        {'toolUse': {'input': {'extracted': 'data'}}}
                    ]
                }
            }
        }
        mock_bedrock.converse.return_value = mock_response
        
        with patch('extract_complaints.lambda_function.load_tool_spec', return_value={'tool': 'spec'}):
            result = lambda_function.process_with_bedrock_conversations([], mock_bedrock)
            
            assert result == {'extracted': 'data'}

    def test_no_tool_use_found(self):
        """Test: No tool use in response"""
        mock_bedrock = Mock()
        mock_response = {
            'output': {
                'message': {
                    'content': [{'text': 'only text response'}]
                }
            }
        }
        mock_bedrock.converse.return_value = mock_response
        
        with patch('extract_complaints.lambda_function.load_tool_spec', return_value={'tool': 'spec'}):
            with pytest.raises(ValueError, match="No tool use found in response"):
                lambda_function.process_with_bedrock_conversations([], mock_bedrock)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])