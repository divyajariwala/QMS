import pytest
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock, mock_open
from datetime import datetime, timezone
import io
import base64

# Mock dependencies before importing
sys.modules['fitz'] = Mock()
mock_psycopg = Mock()
mock_psycopg.connect = MagicMock()
sys.modules['psycopg'] = mock_psycopg
sys.modules['PIL'] = Mock()
sys.modules['PIL.Image'] = Mock()

# Add src directory to path for importing lambda_function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'app', 'extract_and_process_complaints'))
import lambda_function


@pytest.fixture
def mock_db_config():
    """Mock database configuration"""
    return {
        'host': 'test-host',
        'port': 5432,
        'database': 'test_db',
        'user': 'test_user',
        'password': 'test_pass'
    }


@pytest.fixture
def sample_pdf_event():
    """Sample event for PDF processing"""
    return {
        'complaint_id': 'CAS-123',
        'file_id': 'file-456',
        's3path': 's3://test-bucket/test.pdf'
    }


@pytest.fixture
def sample_narrative_event():
    """Sample event for narrative processing"""
    return {
        'complaint_id': 'CAS-789',
        'file_id': 'file-101',
        'narrative_text': 'Patient reported adverse reaction to medication'
    }


@pytest.fixture
def mock_extracted_data():
    """Mock extracted data from Bedrock"""
    return {
        'case_id': 'RGL23-000070',
        'narrative': 'Test narrative',
        'criticality': 'High',
        'category': ['AE', 'PC'],
        'case_type': ['Adverse Event'],
        'report_type': 'Spontaneous',
        'receipt_date': '2023-01-01',
        'primary_reporter': {'name': 'John Doe', 'address': '123 Main St'},
        'patient_name': 'Jane Patient',
        'physician_name': 'Dr. Smith',
        'product_details': {
            'drug_name': 'TestDrug',
            'dosage': '100mg',
            'lot_no': 'LOT123',
            'expiration_date': '2024-12-31'
        }
    }


class TestValidateEvent:
    """Tests for validate_event function"""

    def test_valid_pdf_event(self, sample_pdf_event):
        """Test: Valid PDF event validation"""
        result = lambda_function.validate_event(sample_pdf_event)
        assert result == 'pdf'

    def test_valid_narrative_event(self, sample_narrative_event):
        """Test: Valid narrative event validation"""
        result = lambda_function.validate_event(sample_narrative_event)
        assert result == 'narrative'

    def test_missing_required_fields(self):
        """Test: Missing required fields raises ValueError"""
        event = {'complaint_id': 'CAS-123'}
        with pytest.raises(ValueError) as exc_info:
            lambda_function.validate_event(event)
        assert "Missing required fields" in str(exc_info.value)

    def test_invalid_s3_path(self):
        """Test: Invalid S3 path format"""
        event = {
            'complaint_id': 'CAS-123',
            'file_id': 'file-456',
            's3path': 'invalid-path'
        }
        with pytest.raises(ValueError) as exc_info:
            lambda_function.validate_event(event)
        assert "Invalid S3 path format" in str(exc_info.value)

    def test_no_input_type(self):
        """Test: No narrative_text or s3path provided"""
        event = {
            'complaint_id': 'CAS-123',
            'file_id': 'file-456'
        }
        with pytest.raises(ValueError) as exc_info:
            lambda_function.validate_event(event)
        assert "Must provide either 'narrative_text' or 's3path'" in str(exc_info.value)


class TestGetDbConfig:
    """Tests for get_db_config function"""

    @patch.dict(os.environ, {'DB_SECRET_ARN': 'test-secret-arn'})
    @patch('boto3.client')
    def test_get_db_config_success(self, mock_boto3):
        """Test: Successful database config retrieval"""
        mock_secrets = Mock()
        mock_boto3.return_value = mock_secrets
        mock_secrets.get_secret_value.return_value = {
            'SecretString': json.dumps({
                'host': 'test-host',
                'port': 5432,
                'dbname': 'test_db',
                'username': 'test_user',
                'password': 'test_pass'
            })
        }

        result = lambda_function.get_db_config()

        assert result['host'] == 'test-host'
        assert result['port'] == 5432
        assert result['database'] == 'test_db'
        assert result['user'] == 'test_user'
        assert result['password'] == 'test_pass'

    @patch.dict(os.environ, {'DB_SECRET_ARN': 'test-secret-arn'})
    @patch('boto3.client')
    def test_get_db_config_default_port(self, mock_boto3):
        """Test: Default port when not specified"""
        mock_secrets = Mock()
        mock_boto3.return_value = mock_secrets
        mock_secrets.get_secret_value.return_value = {
            'SecretString': json.dumps({
                'host': 'test-host',
                'dbname': 'test_db',
                'username': 'test_user',
                'password': 'test_pass'
            })
        }

        result = lambda_function.get_db_config()
        assert result['port'] == 5432


class TestLoadToolSpec:
    """Tests for load_tool_spec function"""

    @patch('builtins.open', mock_open(read_data='{"toolSpec": {"name": "test"}}'))
    def test_load_pdf_tool_spec(self):
        """Test: Load PDF tool specification"""
        result = lambda_function.load_tool_spec('pdf')
        assert result == {"toolSpec": {"name": "test"}}

    @patch('builtins.open', mock_open(read_data='{"toolSpec": {"name": "narrative"}}'))
    def test_load_narrative_tool_spec(self):
        """Test: Load narrative tool specification"""
        result = lambda_function.load_tool_spec('narrative')
        assert result == {"toolSpec": {"name": "narrative"}}

    @patch('builtins.open', side_effect=FileNotFoundError())
    def test_load_tool_spec_file_not_found(self, mock_open):
        """Test: FileNotFoundError when tool spec not found"""
        with pytest.raises(FileNotFoundError):
            lambda_function.load_tool_spec('pdf')


class TestFetchPdfFromS3:
    """Tests for fetch_pdf_from_s3 function"""

    @patch('boto3.client')
    def test_fetch_pdf_success(self, mock_boto3):
        """Test: Successful PDF fetch from S3"""
        mock_s3 = Mock()
        mock_boto3.return_value = mock_s3
        mock_s3.head_object.return_value = {'ContentLength': 1024 * 1024}  # 1MB
        mock_s3.get_object.return_value = {'Body': Mock(read=Mock(return_value=b'pdf-content'))}

        result = lambda_function.fetch_pdf_from_s3('s3://test-bucket/test.pdf')
        assert result == b'pdf-content'

    @patch('boto3.client')
    def test_fetch_pdf_too_large(self, mock_boto3):
        """Test: PDF too large error"""
        mock_s3 = Mock()
        mock_boto3.return_value = mock_s3
        mock_s3.head_object.return_value = {'ContentLength': 60 * 1024 * 1024}  # 60MB

        with pytest.raises(ValueError) as exc_info:
            lambda_function.fetch_pdf_from_s3('s3://test-bucket/large.pdf')
        assert "PDF too large" in str(exc_info.value)

    @patch('boto3.client')
    def test_fetch_pdf_s3_error(self, mock_boto3):
        """Test: S3 error handling"""
        mock_s3 = Mock()
        mock_boto3.return_value = mock_s3
        mock_s3.head_object.side_effect = Exception("S3 error")

        with pytest.raises(Exception):
            lambda_function.fetch_pdf_from_s3('s3://test-bucket/error.pdf')


class TestPdfToImages:
    """Tests for pdf_to_images function"""

    @patch('fitz.open')
    def test_pdf_to_images_success(self, mock_fitz):
        """Test: Successful PDF to images conversion"""
        # Mock PDF document
        mock_doc = MagicMock()
        mock_doc.page_count = 2
        mock_fitz.return_value = mock_doc

        # Mock pages
        mock_page = Mock()
        mock_pix = Mock()
        mock_pix.tobytes.return_value = b'fake-png-data'
        mock_page.get_pixmap.return_value = mock_pix
        mock_doc.__getitem__.return_value = mock_page

        # Mock PIL Image
        with patch('PIL.Image.open') as mock_image_open:
            mock_image = Mock()
            mock_image_open.return_value = mock_image

            result = lambda_function.pdf_to_images(b'pdf-data')
            assert len(result) == 2
            assert all(img is not None for img in result)

    @patch('fitz.open')
    def test_pdf_to_images_max_pages(self, mock_fitz):
        """Test: PDF with more than MAX_PAGES"""
        mock_doc = MagicMock()
        mock_doc.page_count = 25  # More than MAX_PAGES (20)
        mock_fitz.return_value = mock_doc

        mock_page = Mock()
        mock_pix = Mock()
        mock_pix.tobytes.return_value = b'fake-png-data'
        mock_page.get_pixmap.return_value = mock_pix
        mock_doc.__getitem__.return_value = mock_page

        with patch('PIL.Image.open') as mock_image_open:
            mock_image = Mock()
            mock_image_open.return_value = mock_image

            result = lambda_function.pdf_to_images(b'pdf-data')
            assert len(result) == 20  # Should be limited to MAX_PAGES

    @patch('fitz.open')
    def test_pdf_to_images_error(self, mock_fitz):
        """Test: Error handling in PDF conversion"""
        mock_fitz.side_effect = Exception("PDF conversion error")

        with pytest.raises(Exception):
            lambda_function.pdf_to_images(b'invalid-pdf')


class TestImagesToBase64:
    """Tests for images_to_base64 function"""

    def test_images_to_base64_success(self):
        """Test: Successful images to base64 conversion"""
        # Mock PIL images
        mock_images = []
        for i in range(2):
            mock_img = Mock()
            mock_img.save = Mock()
            mock_images.append(mock_img)

        with patch('io.BytesIO') as mock_bytesio:
            mock_buffer = Mock()
            mock_buffer.getvalue.return_value = b'fake-image-data'
            mock_bytesio.return_value = mock_buffer

            result = lambda_function.images_to_base64(mock_images)
            assert len(result) == 2
            assert all(isinstance(b64, str) for b64 in result)


class TestConstructPrompts:
    """Tests for prompt construction functions"""

    def test_construct_pdf_prompt(self):
        """Test: PDF prompt construction"""
        base64_images = ['iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==']
        
        with patch('builtins.open', mock_open(read_data='Test prompt')):
            result = lambda_function.construct_pdf_prompt(base64_images)
            
            assert len(result) == 1
            assert result[0]['role'] == 'user'
            assert len(result[0]['content']) == 2  # 1 image + 1 text

    def test_construct_narrative_prompt(self):
        """Test: Narrative prompt construction"""
        narrative = "Test narrative text"
        result = lambda_function.construct_narrative_prompt(narrative)
        
        assert len(result) == 1
        assert result[0]['role'] == 'user'
        assert narrative in result[0]['content'][0]['text']


class TestProcessWithBedrock:
    """Tests for process_with_bedrock function"""

    @patch('boto3.client')
    @patch('lambda_function.load_tool_spec')
    def test_process_with_bedrock_success(self, mock_load_spec, mock_boto3):
        """Test: Successful Bedrock processing"""
        mock_bedrock = Mock()
        mock_boto3.return_value = mock_bedrock
        mock_load_spec.return_value = {'toolSpec': {'name': 'test'}}
        
        mock_bedrock.converse.return_value = {
            'output': {
                'message': {
                    'content': [
                        {'toolUse': {'input': {'extracted': 'data'}}}
                    ]
                }
            }
        }

        messages = [{'role': 'user', 'content': [{'text': 'test'}]}]
        result = lambda_function.process_with_bedrock(messages, 'pdf')
        
        assert result == {'extracted': 'data'}

    @patch('boto3.client')
    @patch('lambda_function.load_tool_spec')
    def test_process_with_bedrock_no_tool_use(self, mock_load_spec, mock_boto3):
        """Test: No tool use found in response"""
        mock_bedrock = Mock()
        mock_boto3.return_value = mock_bedrock
        mock_load_spec.return_value = {'toolSpec': {'name': 'test'}}
        
        mock_bedrock.converse.return_value = {
            'output': {
                'message': {
                    'content': [{'text': 'no tool use'}]
                }
            }
        }

        messages = [{'role': 'user', 'content': [{'text': 'test'}]}]
        
        with pytest.raises(ValueError) as exc_info:
            lambda_function.process_with_bedrock(messages, 'pdf')
        assert "No tool use found in response" in str(exc_info.value)


class TestUpdateComplaintInDb:
    """Tests for update_complaint_in_db function"""

    @patch('lambda_function.get_db_config')
    @patch('psycopg.connect')
    def test_update_complaint_success(self, mock_connect, mock_get_config, mock_extracted_data):
        """Test: Successful complaint update in database"""
        mock_get_config.return_value = {
            'host': 'test-host',
            'port': 5432,
            'database': 'test_db',
            'user': 'test_user',
            'password': 'test_pass'
        }
        
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=False)
        mock_connect.return_value = mock_conn

        lambda_function.update_complaint_in_db('CAS-123', mock_extracted_data)
        
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    @patch('lambda_function.get_db_config')
    @patch('psycopg.connect')
    def test_update_complaint_with_na_values(self, mock_connect, mock_get_config):
        """Test: Update complaint with N/A values"""
        mock_get_config.return_value = {'host': 'test'}
        
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=False)
        mock_connect.return_value = mock_conn

        extracted_data = {
            'narrative': 'Test',
            'primary_reporter': {'name': 'N/A', 'address': 'N/A'},
            'patient_name': 'N/A',
            'physician_name': 'N/A',
            'product_details': {'drug_name': 'N/A'}
        }

        lambda_function.update_complaint_in_db('CAS-123', extracted_data)
        
        # Verify execute was called (N/A values should be converted to None)
        mock_cursor.execute.assert_called_once()

    @patch('lambda_function.get_db_config')
    @patch('psycopg.connect')
    def test_update_complaint_db_error(self, mock_connect, mock_get_config):
        """Test: Database error handling"""
        mock_get_config.return_value = {'host': 'test'}
        mock_connect.side_effect = Exception("Database connection failed")

        with pytest.raises(Exception):
            lambda_function.update_complaint_in_db('CAS-123', {})


class TestLambdaHandler:
    """Tests for lambda_handler function"""

    @patch('lambda_function.validate_event')
    @patch('lambda_function.fetch_pdf_from_s3')
    @patch('lambda_function.pdf_to_images')
    @patch('lambda_function.images_to_base64')
    @patch('lambda_function.construct_pdf_prompt')
    @patch('lambda_function.process_with_bedrock')
    @patch('lambda_function.update_complaint_in_db')
    def test_lambda_handler_pdf_success(self, mock_update_db, mock_bedrock, mock_construct_prompt,
                                       mock_to_base64, mock_to_images, mock_fetch_pdf, mock_validate,
                                       sample_pdf_event, mock_extracted_data):
        """Test: Successful PDF processing"""
        mock_validate.return_value = 'pdf'
        mock_fetch_pdf.return_value = b'pdf-data'
        mock_to_images.return_value = [Mock(), Mock()]
        mock_to_base64.return_value = ['base64-1', 'base64-2']
        mock_construct_prompt.return_value = [{'role': 'user', 'content': []}]
        mock_bedrock.return_value = mock_extracted_data

        result = lambda_function.lambda_handler(sample_pdf_event, {})

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
        assert body['complaint_id'] == 'CAS-123'
        assert body['input_type'] == 'pdf'

    @patch('lambda_function.validate_event')
    @patch('lambda_function.construct_narrative_prompt')
    @patch('lambda_function.process_with_bedrock')
    @patch('lambda_function.update_complaint_in_db')
    def test_lambda_handler_narrative_success(self, mock_update_db, mock_bedrock, mock_construct_prompt,
                                            mock_validate, sample_narrative_event, mock_extracted_data):
        """Test: Successful narrative processing"""
        mock_validate.return_value = 'narrative'
        mock_construct_prompt.return_value = [{'role': 'user', 'content': []}]
        mock_bedrock.return_value = mock_extracted_data

        result = lambda_function.lambda_handler(sample_narrative_event, {})

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
        assert body['complaint_id'] == 'CAS-789'
        assert body['input_type'] == 'narrative'

    @patch('lambda_function.validate_event')
    def test_lambda_handler_validation_error(self, mock_validate):
        """Test: Validation error handling"""
        mock_validate.side_effect = ValueError("Invalid event")

        result = lambda_function.lambda_handler({}, {})

        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert body['success'] is False
        assert body['error'] == 'Invalid event'

    @patch('lambda_function.validate_event')
    @patch('lambda_function.fetch_pdf_from_s3')
    def test_lambda_handler_processing_error(self, mock_fetch_pdf, mock_validate, sample_pdf_event):
        """Test: Processing error handling"""
        mock_validate.return_value = 'pdf'
        mock_fetch_pdf.side_effect = Exception("Processing failed")

        result = lambda_function.lambda_handler(sample_pdf_event, {})

        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert body['success'] is False
        assert body['error'] == 'Internal error'


class TestEdgeCases:
    """Tests for edge cases and error conditions"""

    def test_validate_event_empty_event(self):
        """Test: Empty event validation"""
        with pytest.raises(ValueError):
            lambda_function.validate_event({})

    @patch('lambda_function.get_db_config')
    @patch('psycopg.connect')
    def test_update_complaint_invalid_dates(self, mock_connect, mock_get_config):
        """Test: Invalid date handling in database update"""
        mock_get_config.return_value = {'host': 'test'}
        
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=False)
        mock_connect.return_value = mock_conn

        extracted_data = {
            'receipt_date': 'invalid-date',
            'product_details': {'expiration_date': 'also-invalid'}
        }

        # Should not raise exception, invalid dates should be set to None
        lambda_function.update_complaint_in_db('CAS-123', extracted_data)
        mock_cursor.execute.assert_called_once()

    def test_construct_pdf_prompt_empty_images(self):
        """Test: PDF prompt with empty images list"""
        with patch('builtins.open', mock_open(read_data='Test prompt')):
            result = lambda_function.construct_pdf_prompt([])
            assert len(result[0]['content']) == 1  # Only text, no images


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=extract_and_process_complaints.lambda_function", "--cov-report=term-missing"])