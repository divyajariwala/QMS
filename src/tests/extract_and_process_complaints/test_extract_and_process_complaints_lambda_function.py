import pytest
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock, mock_open
from datetime import datetime, timezone
import io
import base64
import importlib.util

# Mock dependencies before importing
sys.modules['fitz'] = Mock()
mock_psycopg = Mock()
mock_psycopg.connect = MagicMock()
mock_psycopg_rows = Mock()
mock_psycopg_rows.dict_row = Mock()
sys.modules['psycopg'] = mock_psycopg
sys.modules['psycopg.rows'] = mock_psycopg_rows
sys.modules['PIL'] = Mock()
sys.modules['PIL.Image'] = Mock()

# Mock secrets_util
mock_secrets_util = Mock()
mock_secrets_util.get_secret = Mock()
sys.modules['secrets_util'] = mock_secrets_util

# Get the absolute path to the lambda_function.py file
lambda_function_path = os.path.join(
    os.path.dirname(__file__), 
    '..', '..', 'app', 'extract_and_process_complaints', 'lambda_function.py'
)
lambda_function_path = os.path.abspath(lambda_function_path)

# Load the module using importlib
spec = importlib.util.spec_from_file_location("lambda_function", lambda_function_path)
lambda_function = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lambda_function)

# Add to sys.modules so patches can find it
sys.modules['lambda_function'] = lambda_function


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
        'narrative_summary': 'AI generated summary of the test narrative',
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


class TestGetConnectionString:
    """Tests for get_connection_string function"""

    @patch.dict(os.environ, {'env': 'dev', 'db_secret_base_name': 'aurora-postgres-master', 'db_region': 'us-east-1'})
    @patch('lambda_function.get_secret')
    def test_get_connection_string_success(self, mock_get_secret):
        """Test: Successful connection string building"""
        mock_get_secret.return_value = {
            'host': 'test-host',
            'port': 5432,
            'dbname': 'test_db',
            'username': 'test_user',
            'password': 'test_pass'
        }

        # Reset cache
        lambda_function._connection_string = None
        lambda_function._db_credentials = None

        result = lambda_function.get_connection_string()

        assert result == 'postgresql://test_user:test_pass@test-host:5432/test_db'
        mock_get_secret.assert_called_once_with('qms-dev-aurora-postgres-master', 'us-east-1')

    @patch.dict(os.environ, {'env': 'dev', 'db_secret_base_name': 'aurora-postgres-master', 'db_region': 'us-east-1'})
    @patch('lambda_function.get_secret')
    def test_get_connection_string_cached(self, mock_get_secret):
        """Test: Connection string caching"""
        # Set cache
        lambda_function._connection_string = 'cached://connection'
        
        result = lambda_function.get_connection_string()
        
        assert result == 'cached://connection'
        mock_get_secret.assert_not_called()


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
        
        with patch('builtins.open', mock_open(read_data='Test prompt from file')):
            result = lambda_function.construct_narrative_prompt(narrative)
        
        assert len(result) == 1
        assert result[0]['role'] == 'user'
        assert narrative in result[0]['content'][0]['text']
        assert 'Test prompt from file' in result[0]['content'][0]['text']


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

    @patch('lambda_function.get_connection_string')
    def test_update_complaint_success(self, mock_get_connection, mock_extracted_data):
        """Test: Successful complaint update in database with text_extracted set to true"""
        mock_get_connection.return_value = 'postgresql://user:pass@host:5432/db'
        mock_extracted_data['narrative_summary'] = 'AI generated summary of the narrative'
        
        with patch('lambda_function.psycopg.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.__enter__.return_value = mock_conn
            mock_conn.__exit__.return_value = False
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_conn.cursor.return_value.__exit__.return_value = False
            mock_connect.return_value = mock_conn

            lambda_function.update_complaint_in_db('CAS-123', mock_extracted_data)
            
            mock_cursor.execute.assert_called_once()
            # Verify text_extracted is set to TRUE in the SQL
            call_args = mock_cursor.execute.call_args[0]
            assert 'text_extracted = TRUE' in call_args[0]
            mock_conn.commit.assert_called_once()

    @patch('lambda_function.get_connection_string')
    def test_update_complaint_with_na_values(self, mock_get_connection):
        """Test: Update complaint with N/A values"""
        mock_get_connection.return_value = 'postgresql://user:pass@host:5432/db'
        
        with patch('lambda_function.psycopg.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.__enter__.return_value = mock_conn
            mock_conn.__exit__.return_value = False
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_conn.cursor.return_value.__exit__.return_value = False
            mock_connect.return_value = mock_conn

            extracted_data = {
                'narrative': 'Test',
                'narrative_summary': 'Test summary',
                'primary_reporter': {'name': 'N/A', 'address': 'N/A'},
                'patient_name': 'N/A',
                'physician_name': 'N/A',
                'product_details': {'drug_name': 'N/A'}
            }

            lambda_function.update_complaint_in_db('CAS-123', extracted_data)
            
            # Verify execute was called (N/A values should be converted to None)
            mock_cursor.execute.assert_called_once()

    @patch('lambda_function.get_connection_string')
    def test_update_complaint_db_error(self, mock_get_connection):
        """Test: Database error handling"""
        mock_get_connection.return_value = 'postgresql://user:pass@host:5432/db'
        
        with patch('lambda_function.psycopg.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database connection failed")

            with pytest.raises(Exception):
                lambda_function.update_complaint_in_db('CAS-123', {})


class TestLambdaHandler:
    """Tests for lambda_handler function"""

    @patch('lambda_function.process_single_complaint')
    def test_lambda_handler_sqs_batch_success(self, mock_process_single):
        """Test: Successful SQS batch processing"""
        mock_process_single.return_value = {
            'success': True,
            'complaint_id': 'CAS-123',
            'input_type': 'narrative'
        }

        sqs_event = {
            'Records': [
                {
                    'body': json.dumps({
                        'complaint_id': 'CAS-123',
                        'file_id': 'file-456',
                        'narrative_text': 'Test narrative'
                    })
                },
                {
                    'body': json.dumps({
                        'complaint_id': 'CAS-124',
                        'file_id': 'file-457',
                        'narrative_text': 'Another narrative'
                    })
                }
            ]
        }

        result = lambda_function.lambda_handler(sqs_event, {})

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
        assert body['processed_count'] == 2
        assert len(body['results']) == 2
        assert mock_process_single.call_count == 2

    @patch('lambda_function.validate_event')
    @patch('lambda_function.construct_narrative_prompt')
    @patch('lambda_function.process_with_bedrock')
    @patch('lambda_function.update_complaint_in_db')
    def test_lambda_handler_direct_invocation(self, mock_update_db, mock_bedrock, mock_construct_prompt,
                                            mock_validate, sample_narrative_event, mock_extracted_data):
        """Test: Direct invocation (non-SQS)"""
        mock_validate.return_value = 'narrative'
        mock_construct_prompt.return_value = [{'role': 'user', 'content': []}]
        mock_bedrock.return_value = mock_extracted_data

        result = lambda_function.lambda_handler(sample_narrative_event, {})

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
        assert body['complaint_id'] == 'CAS-789'
        assert body['input_type'] == 'narrative'

    @patch('lambda_function.process_single_complaint')
    def test_lambda_handler_sqs_processing_error(self, mock_process_single):
        """Test: SQS processing error handling"""
        mock_process_single.side_effect = Exception("Processing failed")

        sqs_event = {
            'Records': [
                {
                    'body': json.dumps({
                        'complaint_id': 'CAS-123',
                        'file_id': 'file-456',
                        'narrative_text': 'Test narrative'
                    })
                }
            ]
        }

        result = lambda_function.lambda_handler(sqs_event, {})

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
        assert body['processed_count'] == 1
        assert body['results'][0]['success'] is False

    def test_lambda_handler_general_error(self):
        """Test: General error handling"""
        # Invalid event structure
        result = lambda_function.lambda_handler(None, {})

        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert body['success'] is False
        assert body['error'] == 'Internal error'


class TestProcessSingleComplaint:
    """Tests for process_single_complaint function"""

    @patch('lambda_function.validate_event')
    @patch('lambda_function.construct_narrative_prompt')
    @patch('lambda_function.process_with_bedrock')
    @patch('lambda_function.update_complaint_in_db')
    def test_process_single_complaint_narrative(self, mock_update_db, mock_bedrock, mock_construct_prompt, mock_validate, mock_extracted_data):
        """Test: Process single narrative complaint"""
        mock_validate.return_value = 'narrative'
        mock_construct_prompt.return_value = [{'role': 'user', 'content': []}]
        mock_bedrock.return_value = mock_extracted_data

        message_data = {
            'complaint_id': 'CAS-123',
            'file_id': 'file-456',
            'narrative_text': 'Test narrative'
        }

        result = lambda_function.process_single_complaint(message_data)

        assert result['success'] is True
        assert result['complaint_id'] == 'CAS-123'
        assert result['input_type'] == 'narrative'
        mock_update_db.assert_called_once()

    @patch('lambda_function.validate_event')
    def test_process_single_complaint_validation_error(self, mock_validate):
        """Test: Process single complaint validation error"""
        mock_validate.side_effect = ValueError("Invalid event")

        message_data = {'invalid': 'data'}

        with pytest.raises(ValueError):
            lambda_function.process_single_complaint(message_data)


class TestEdgeCases:
    """Tests for edge cases and error conditions"""

    def test_validate_event_empty_event(self):
        """Test: Empty event validation"""
        with pytest.raises(ValueError):
            lambda_function.validate_event({})

    @patch('lambda_function.get_connection_string')
    def test_update_complaint_invalid_dates(self, mock_get_connection):
        """Test: Invalid date handling in database update"""
        mock_get_connection.return_value = 'postgresql://user:pass@host:5432/db'
        
        with patch('lambda_function.psycopg.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.__enter__.return_value = mock_conn
            mock_conn.__exit__.return_value = False
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_conn.cursor.return_value.__exit__.return_value = False
            mock_connect.return_value = mock_conn

            extracted_data = {
                'narrative_summary': 'Test summary',
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