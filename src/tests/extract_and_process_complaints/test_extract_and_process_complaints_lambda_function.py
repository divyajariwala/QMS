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
sys.modules['audit_logger'] = Mock()

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
            'part_no': 'PART456',
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


class TestGetDefaultExtractionData:
    """Tests for get_default_extraction_data function"""

    def test_get_default_extraction_data_pdf(self):
        """Test: Get default extraction data for PDF"""
        result = lambda_function.get_default_extraction_data('pdf')
        
        assert result['case_id'] == 'N/A'
        assert result['narrative'] == ''  # Empty for PDF
        assert result['narrative_summary'] == 'N/A'
        assert result['criticality'] == 'N/A'
        assert result['primary_reporter']['name'] == 'N/A'
        assert result['primary_reporter']['address'] == 'N/A'
        assert result['patient_name'] == 'N/A'
        assert result['physician_name'] == 'N/A'
        assert result['product_details']['drug_name'] == 'N/A'
        assert result['product_details']['lot_no'] == 'N/A'
        assert result['product_details']['part_no'] == 'N/A'
        assert isinstance(result['category'], list)
        assert isinstance(result['case_type'], list)

    def test_get_default_extraction_data_narrative_preserved(self):
        """Test: Get default extraction data with preserved narrative"""
        result = lambda_function.get_default_extraction_data('narrative', 'Test narrative text')
        
        assert result['case_id'] == 'N/A'
        assert result['narrative'] == 'Test narrative text'  # Preserved
        assert result['narrative_summary'] == 'N/A'
        assert all(value == 'N/A' or value == 'Test narrative text' or value == '' or isinstance(value, (list, dict)) 
                   for value in result.values())


class TestLoadToolSpec:
    """Tests for load_tool_spec function"""

    @patch('builtins.open', mock_open(read_data='{"toolSpec": {"name": "test"}}'))
    def test_load_pdf_tool_spec_step1(self):
        """Test: Load PDF tool specification step 1"""
        result = lambda_function.load_tool_spec('pdf', step=1)
        assert result == {"toolSpec": {"name": "test"}}

    @patch('builtins.open', mock_open(read_data='{"toolSpec": {"name": "narrative"}}'))
    def test_load_narrative_tool_spec_step1(self):
        """Test: Load narrative tool specification step 1"""
        result = lambda_function.load_tool_spec('narrative', step=1)
        assert result == {"toolSpec": {"name": "narrative"}}

    @patch('builtins.open', mock_open(read_data='{"toolSpec": {"name": "criticality"}}'))
    def test_load_tool_spec_step2(self):
        """Test: Load tool specification step 2"""
        result = lambda_function.load_tool_spec('narrative', step=2)
        assert result == {"toolSpec": {"name": "criticality"}}

    @patch('builtins.open', mock_open(read_data='{"toolSpec": {"name": "classification"}}'))
    def test_load_tool_spec_step3(self):
        """Test: Load tool specification step 3"""
        result = lambda_function.load_tool_spec('narrative', step=3)
        assert result == {"toolSpec": {"name": "classification"}}

    @patch('builtins.open', side_effect=FileNotFoundError())
    def test_load_tool_spec_file_not_found(self, mock_open):
        """Test: FileNotFoundError when tool spec not found"""
        with pytest.raises(FileNotFoundError):
            lambda_function.load_tool_spec('pdf', step=1)


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
    def test_pdf_to_images_all_pages(self, mock_fitz):
        """Test: PDF with multiple pages processes all pages"""
        mock_doc = MagicMock()
        mock_doc.page_count = 25
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
            assert len(result) == 25

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

    def test_construct_pdf_prompt_step1(self):
        """Test: PDF prompt construction step 1"""
        base64_images = ['iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==']
        
        with patch('builtins.open', mock_open(read_data='Test prompt')):
            result = lambda_function.construct_pdf_prompt(base64_images, step=1)
            
            assert len(result) == 1
            assert result[0]['role'] == 'user'
            assert len(result[0]['content']) == 2  # 1 image + 1 text

    def test_construct_narrative_prompt_step1(self):
        """Test: Narrative prompt construction step 1"""
        narrative = "Test narrative text"
        
        with patch('builtins.open', mock_open(read_data='Test prompt from file')):
            result = lambda_function.construct_narrative_prompt(narrative, step=1)
        
        assert len(result) == 1
        assert result[0]['role'] == 'user'
        assert narrative in result[0]['content'][0]['text']
        assert 'Test prompt from file' in result[0]['content'][0]['text']

    def test_construct_narrative_prompt_step2(self):
        """Test: Narrative prompt construction step 2 (criticality)"""
        summary = "Patient experienced severe reaction"
        
        with patch('builtins.open', mock_open(read_data='Extract criticality')):
            result = lambda_function.construct_narrative_prompt(summary, step=2)
        
        assert len(result) == 1
        assert summary in result[0]['content'][0]['text']

    def test_construct_narrative_prompt_step3(self):
        """Test: Narrative prompt construction step 3 (classification)"""
        summary = "Product defect reported"
        
        with patch('builtins.open', mock_open(read_data='Extract classification')):
            result = lambda_function.construct_narrative_prompt(summary, step=3)
        
        assert len(result) == 1
        assert summary in result[0]['content'][0]['text']


class TestProcessWithBedrock:
    """Tests for process_with_bedrock function"""

    @patch('boto3.client')
    @patch('lambda_function.load_tool_spec')
    def test_process_with_bedrock_success_step1(self, mock_load_spec, mock_boto3):
        """Test: Successful Bedrock processing step 1 with Haiku model"""
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
        result = lambda_function.process_with_bedrock(messages, 'pdf', step=1)
        
        assert result == {'extracted': 'data'}
        mock_bedrock.converse.assert_called_once()
        call_args = mock_bedrock.converse.call_args
        assert call_args[1]['modelId'] == 'anthropic.claude-3-haiku-20240307-v1:0'

    @patch('boto3.client')
    @patch('lambda_function.load_tool_spec')
    def test_process_with_bedrock_step2_criticality(self, mock_load_spec, mock_boto3):
        """Test: Bedrock processing step 2 returns criticality"""
        mock_bedrock = Mock()
        mock_boto3.return_value = mock_bedrock
        mock_load_spec.return_value = {'toolSpec': {'name': 'extract_criticality'}}
        
        mock_bedrock.converse.return_value = {
            'output': {
                'message': {
                    'content': [
                        {'toolUse': {'input': {'criticality': 'Critical'}}}
                    ]
                }
            }
        }

        messages = [{'role': 'user', 'content': [{'text': 'summary'}]}]
        result = lambda_function.process_with_bedrock(messages, 'narrative', step=2)
        
        assert result == {'criticality': 'Critical'}

    @patch('boto3.client')
    @patch('lambda_function.load_tool_spec')
    def test_process_with_bedrock_step3_classification(self, mock_load_spec, mock_boto3):
        """Test: Bedrock processing step 3 returns classification"""
        mock_bedrock = Mock()
        mock_boto3.return_value = mock_bedrock
        mock_load_spec.return_value = {'toolSpec': {'name': 'extract_classification'}}
        
        mock_bedrock.converse.return_value = {
            'output': {
                'message': {
                    'content': [
                        {'toolUse': {'input': {'category': ['Pharmaceutical Drug'], 'case_type': ['Adverse Event']}}}
                    ]
                }
            }
        }

        messages = [{'role': 'user', 'content': [{'text': 'summary'}]}]
        result = lambda_function.process_with_bedrock(messages, 'narrative', step=3)
        
        assert result == {'category': ['Pharmaceutical Drug'], 'case_type': ['Adverse Event']}

    @patch('lambda_function.get_default_extraction_data')
    @patch('lambda_function.load_tool_spec')
    @patch('boto3.client')
    def test_process_with_bedrock_no_tool_use_step1(self, mock_boto3, mock_load_spec, mock_get_default):
        """Test: No tool use found for step 1 returns default"""
        mock_bedrock = Mock()
        mock_boto3.return_value = mock_bedrock
        mock_load_spec.return_value = {'toolSpec': {'name': 'test'}}
        mock_get_default.return_value = {
            'case_id': 'N/A',
            'narrative': 'PDF Extraction Failed',
            'narrative_summary': 'N/A',
            'primary_reporter': {'name': 'N/A', 'address': 'N/A'}
        }
        
        mock_bedrock.converse.return_value = {
            'output': {
                'message': {
                    'content': [{'text': 'no tool use'}]
                }
            }
        }

        messages = [{'role': 'user', 'content': [{'text': 'test'}]}]
        result = lambda_function.process_with_bedrock(messages, 'pdf', 'PDF Extraction Failed', step=1)
        
        assert result['narrative'] == 'PDF Extraction Failed'
        mock_get_default.assert_called_once_with('pdf', 'PDF Extraction Failed')

    @patch('lambda_function.load_tool_spec')
    @patch('boto3.client')
    def test_process_with_bedrock_no_tool_use_step2(self, mock_boto3, mock_load_spec):
        """Test: No tool use found for step 2 returns default criticality"""
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
        result = lambda_function.process_with_bedrock(messages, 'narrative', '', step=2)
        
        assert result == {'criticality': 'N/A'}

    @patch('lambda_function.load_tool_spec')
    @patch('boto3.client')
    def test_process_with_bedrock_no_tool_use_step3(self, mock_boto3, mock_load_spec):
        """Test: No tool use found for step 3 returns default classification"""
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
        result = lambda_function.process_with_bedrock(messages, 'narrative', '', step=3)
        
        assert result == {'category': [], 'case_type': []}

    @patch('lambda_function.get_default_extraction_data')
    @patch('lambda_function.load_tool_spec')
    @patch('boto3.client')
    def test_process_with_bedrock_no_tool_use_narrative_step1(self, mock_boto3, mock_load_spec, mock_get_default):
        """Test: No tool use found for narrative step 1 returns default with preserved narrative"""
        mock_bedrock = Mock()
        mock_boto3.return_value = mock_bedrock
        mock_load_spec.return_value = {'toolSpec': {'name': 'test'}}
        mock_get_default.return_value = {
            'case_id': 'N/A',
            'narrative': 'Test narrative',
            'narrative_summary': 'N/A',
            'primary_reporter': {'name': 'N/A', 'address': 'N/A'}
        }
        
        mock_bedrock.converse.return_value = {
            'output': {
                'message': {
                    'content': [{'text': 'no tool use'}]
                }
            }
        }

        messages = [{'role': 'user', 'content': [{'text': 'test'}]}]
        result = lambda_function.process_with_bedrock(messages, 'narrative', 'Test narrative', step=1)
        
        assert result['case_id'] == 'N/A'
        assert result['narrative'] == 'Test narrative'
        assert result['narrative_summary'] == 'N/A'
        mock_get_default.assert_called_once_with('narrative', 'Test narrative')


class TestUpdateComplaintInDb:
    """Tests for update_complaint_in_db function"""

    @patch('lambda_function.get_connection_string')
    def test_update_complaint_success(self, mock_get_connection, mock_extracted_data):
        """Test: Successful complaint update in database with text_extracted set to true"""
        mock_get_connection.return_value = 'postgresql://user:pass@host:5432/db'
        mock_extracted_data['narrative_summary'] = 'AI generated summary of the narrative'
        # Change to mixed case type to avoid triggering adverse event move
        mock_extracted_data['case_type'] = ['Adverse Event', 'Product Complaint']
        
        with patch('lambda_function.psycopg.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.__enter__.return_value = mock_conn
            mock_conn.__exit__.return_value = False
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            mock_conn.cursor.return_value.__exit__.return_value = False
            mock_connect.return_value = mock_conn

            lambda_function.update_complaint_in_db('CAS-123', mock_extracted_data)
            
            # Should only have 1 execute call (UPDATE) since it's not pure adverse event
            mock_cursor.execute.assert_called_once()
            # Verify text_extracted is set to TRUE and part_number is in SQL
            call_args = mock_cursor.execute.call_args[0]
            assert 'text_extracted = TRUE' in call_args[0]
            assert 'part_number = %s' in call_args[0]
            # Should have 2 commits: one for UPDATE, one for log_workflow
            assert mock_conn.commit.call_count == 2

    @patch('lambda_function.move_to_adverse_events')
    @patch('lambda_function.get_connection_string')
    def test_update_complaint_adverse_events_only(self, mock_get_connection, mock_move):
        """Test: Adverse events only case is moved to adverse_events table with two-step commit"""
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
                'case_type': ['Adverse Event']
            }

            lambda_function.update_complaint_in_db('CAS-123', extracted_data)
            
            # Verify move was called after first commit
            mock_move.assert_called_once_with(mock_cursor, 'CAS-123')
            # Verify three commits: one for update, one for move, one for log_workflow
            assert mock_conn.commit.call_count == 3

    @patch('lambda_function.move_to_adverse_events')
    @patch('lambda_function.get_connection_string')
    def test_update_complaint_mixed_case_not_moved(self, mock_get_connection, mock_move):
        """Test: Mixed case (adverse events + product complaint) is not moved"""
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
                'case_type': ['Adverse Events', 'Product Complaint']
            }

            lambda_function.update_complaint_in_db('CAS-123', extracted_data)
            
            mock_move.assert_not_called()
            # Should have 2 commits: one for UPDATE, one for log_workflow
            assert mock_conn.commit.call_count == 2

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
        """Test: Successful SQS batch processing with parallel execution"""
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
        # Verify parallel processing - both complaints processed
        assert mock_process_single.call_count == 2

    @patch('lambda_function.process_single_complaint')
    def test_lambda_handler_parallel_batch_processing(self, mock_process_single):
        """Test: Parallel batch processing with 30 complaints"""
        mock_process_single.return_value = {
            'success': True,
            'complaint_id': 'CAS-TEST',
            'input_type': 'narrative'
        }

        # Create batch of 30 complaints
        sqs_event = {
            'Records': [
                {
                    'body': json.dumps({
                        'complaint_id': f'CAS-{i}',
                        'file_id': f'file-{i}',
                        'narrative_text': f'Test narrative {i}'
                    })
                }
                for i in range(30)
            ]
        }

        result = lambda_function.lambda_handler(sqs_event, {})

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
        assert body['processed_count'] == 30
        assert len(body['results']) == 30
        # Verify all 30 complaints were processed
        assert mock_process_single.call_count == 30

    @patch('lambda_function.validate_event')
    @patch('lambda_function.construct_narrative_prompt')
    @patch('lambda_function.process_with_bedrock')
    @patch('lambda_function.update_complaint_in_db')
    def test_lambda_handler_direct_invocation(self, mock_update_db, mock_bedrock, mock_construct_prompt,
                                            mock_validate, sample_narrative_event):
        """Test: Direct invocation (non-SQS) with 3-step chaining"""
        mock_validate.return_value = 'narrative'
        mock_construct_prompt.return_value = [{'role': 'user', 'content': []}]
        
        # 3-step responses
        step1_data = {'case_id': 'TEST', 'narrative': 'Test', 'narrative_summary': 'Summary'}
        step2_data = {'criticality': 'Minor'}
        step3_data = {'category': ['Pharmaceutical Drug'], 'case_type': ['Adverse Event']}
        mock_bedrock.side_effect = [step1_data, step2_data, step3_data]

        result = lambda_function.lambda_handler(sample_narrative_event, {})

        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
        assert body['complaint_id'] == 'CAS-789'
        assert body['input_type'] == 'narrative'
        assert mock_bedrock.call_count == 3

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
    def test_process_single_complaint_narrative_3step(self, mock_update_db, mock_bedrock, mock_construct_prompt, mock_validate):
        """Test: Process single narrative complaint with 3-step chaining"""
        mock_validate.return_value = 'narrative'
        mock_construct_prompt.return_value = [{'role': 'user', 'content': []}]
        
        # Step 1: Basic info
        step1_data = {
            'case_id': 'RGL23-000070',
            'narrative': 'Test narrative',
            'narrative_summary': 'Patient experienced adverse reaction',
            'receipt_date': '2023-01-01',
            'primary_reporter': {'name': 'John Doe', 'address': '123 Main St'},
            'patient_name': 'Jane Patient',
            'physician_name': 'Dr. Smith',
            'product_details': {'drug_name': 'TestDrug', 'dosage': '100mg', 'lot_no': 'LOT123', 'part_no': 'PART456', 'expiration_date': '2024-12-31'}
        }
        # Step 2: Criticality
        step2_data = {'criticality': 'Critical'}
        # Step 3: Classification
        step3_data = {'category': ['Pharmaceutical Drug'], 'case_type': ['Adverse Event']}
        
        mock_bedrock.side_effect = [step1_data, step2_data, step3_data]

        message_data = {
            'complaint_id': 'CAS-123',
            'file_id': 'file-456',
            'narrative_text': 'Test narrative'
        }

        result = lambda_function.process_single_complaint(message_data)

        assert result['success'] is True
        assert result['complaint_id'] == 'CAS-123'
        assert result['input_type'] == 'narrative'
        assert mock_bedrock.call_count == 3
        mock_update_db.assert_called_once()

    @patch('lambda_function.validate_event')
    @patch('lambda_function.construct_narrative_prompt')
    @patch('lambda_function.process_with_bedrock')
    @patch('lambda_function.update_complaint_in_db')
    def test_process_single_complaint_narrative_preserved_on_failure(self, mock_update_db, mock_bedrock, mock_construct_prompt, mock_validate):
        """Test: Narrative is preserved even when LLM tool use fails in step 1"""
        mock_validate.return_value = 'narrative'
        mock_construct_prompt.return_value = [{'role': 'user', 'content': []}]
        # Step 1 returns data without narrative
        step1_data = {'case_id': 'N/A', 'narrative_summary': 'N/A'}
        mock_bedrock.return_value = step1_data

        message_data = {
            'complaint_id': 'CAS-123',
            'file_id': 'file-456',
            'narrative_text': 'Original narrative text'
        }

        result = lambda_function.process_single_complaint(message_data)

        assert result['success'] is True
        update_call_args = mock_update_db.call_args[0]
        assert update_call_args[1]['narrative'] == 'Original narrative text'
        assert update_call_args[1]['criticality'] == 'N/A'
        assert update_call_args[1]['category'] == []
        assert update_call_args[1]['case_type'] == []

    @patch('lambda_function.validate_event')
    @patch('lambda_function.fetch_pdf_from_s3')
    @patch('lambda_function.pdf_to_images')
    @patch('lambda_function.images_to_base64')
    @patch('lambda_function.construct_pdf_prompt')
    @patch('lambda_function.construct_narrative_prompt')
    @patch('lambda_function.process_with_bedrock')
    @patch('lambda_function.update_complaint_in_db')
    def test_process_single_complaint_pdf_3step_success(self, mock_update_db, mock_bedrock, mock_construct_narrative, mock_construct_prompt, mock_images_to_base64, mock_pdf_to_images, mock_fetch_pdf, mock_validate):
        """Test: PDF complaint with 3-step chaining"""
        mock_validate.return_value = 'pdf'
        mock_fetch_pdf.return_value = b'pdf-data'
        mock_pdf_to_images.return_value = [Mock()]
        mock_images_to_base64.return_value = ['base64-image']
        mock_construct_prompt.return_value = [{'role': 'user', 'content': []}]
        mock_construct_narrative.return_value = [{'role': 'user', 'content': []}]
        
        # Step 1: Basic info
        step1_data = {'case_id': 'TEST', 'narrative': 'Full narrative', 'narrative_summary': 'Summary of complaint'}
        # Step 2: Criticality
        step2_data = {'criticality': 'Major'}
        # Step 3: Classification
        step3_data = {'category': ['Medical Device'], 'case_type': ['Product Complaint']}
        
        mock_bedrock.side_effect = [step1_data, step2_data, step3_data]

        message_data = {
            'complaint_id': 'CAS-123',
            'file_id': 'file-456',
            's3path': 's3://bucket/file.pdf'
        }

        result = lambda_function.process_single_complaint(message_data)
        
        assert result['success'] is True
        assert mock_bedrock.call_count == 3
        update_call_args = mock_update_db.call_args[0]
        assert update_call_args[1]['narrative'] == 'Full narrative'
        assert update_call_args[1]['criticality'] == 'Major'
        assert update_call_args[1]['category'] == ['Medical Device']

    @patch('lambda_function.validate_event')
    @patch('lambda_function.fetch_pdf_from_s3')
    @patch('lambda_function.pdf_to_images')
    @patch('lambda_function.images_to_base64')
    @patch('lambda_function.construct_pdf_prompt')
    @patch('lambda_function.process_with_bedrock')
    @patch('lambda_function.update_complaint_in_db')
    def test_process_single_complaint_pdf_empty_narrative_sets_error_message(self, mock_update_db, mock_bedrock, mock_construct_prompt, mock_images_to_base64, mock_pdf_to_images, mock_fetch_pdf, mock_validate):
        """Test: PDF complaint gets error message when narrative is empty in step 1"""
        mock_validate.return_value = 'pdf'
        mock_fetch_pdf.return_value = b'pdf-data'
        mock_pdf_to_images.return_value = [Mock()]
        mock_images_to_base64.return_value = ['base64-image']
        mock_construct_prompt.return_value = [{'role': 'user', 'content': []}]
        # Step 1 returns empty narrative
        mock_bedrock.return_value = {'case_id': 'TEST', 'narrative': ''}

        message_data = {
            'complaint_id': 'CAS-123',
            'file_id': 'file-456',
            's3path': 's3://bucket/file.pdf'
        }

        result = lambda_function.process_single_complaint(message_data)
        
        assert result['success'] is True
        assert mock_bedrock.call_count == 1  # Only step 1 called
        update_call_args = mock_update_db.call_args[0]
        assert update_call_args[1]['narrative'] == 'Not a Product Complaint Document'
        assert update_call_args[1]['criticality'] == 'N/A'
        assert update_call_args[1]['category'] == []
        assert update_call_args[1]['case_type'] == []

    @patch('lambda_function.validate_event')
    @patch('lambda_function.construct_narrative_prompt')
    @patch('lambda_function.process_with_bedrock')
    @patch('lambda_function.update_complaint_in_db')
    def test_process_single_complaint_not_a_complaint(self, mock_update_db, mock_bedrock, mock_construct_prompt, mock_validate):
        """Test: Process narrative that is not a product complaint"""
        mock_validate.return_value = 'narrative'
        mock_construct_prompt.return_value = [{'role': 'user', 'content': []}]
        # Step 1 identifies it's not a complaint
        step1_data = {
            'case_id': 'N/A',
            'narrative': 'Random text',
            'narrative_summary': 'Not a Product Complaint'
        }
        mock_bedrock.return_value = step1_data

        message_data = {
            'complaint_id': 'CAS-123',
            'file_id': 'file-456',
            'narrative_text': 'Random unrelated text'
        }

        result = lambda_function.process_single_complaint(message_data)

        assert result['success'] is True
        assert mock_bedrock.call_count == 1  # Only step 1, no steps 2 and 3
        update_call_args = mock_update_db.call_args[0]
        assert update_call_args[1]['narrative_summary'] == 'Not a Product Complaint'
        assert update_call_args[1]['criticality'] == 'N/A'
        assert update_call_args[1]['category'] == []
        assert update_call_args[1]['case_type'] == []

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

    @patch('lambda_function.validate_event')
    @patch('lambda_function.fetch_pdf_from_s3')
    @patch('lambda_function.pdf_to_images')
    @patch('lambda_function.update_complaint_in_db')
    def test_process_single_complaint_empty_pdf(self, mock_update_db, mock_pdf_to_images, mock_fetch_pdf, mock_validate):
        """Test: Empty PDF with no pages"""
        mock_validate.return_value = 'pdf'
        mock_fetch_pdf.return_value = b'pdf-data'
        mock_pdf_to_images.return_value = []

        message_data = {
            'complaint_id': 'CAS-123',
            'file_id': 'file-456',
            's3path': 's3://bucket/empty.pdf'
        }

        result = lambda_function.process_single_complaint(message_data)
        
        assert result['success'] is True
        update_call_args = mock_update_db.call_args[0]
        assert update_call_args[1]['narrative'] == 'Empty PDF - No Pages'

    @patch('lambda_function.validate_event')
    @patch('lambda_function.update_complaint_in_db')
    def test_process_single_complaint_empty_narrative(self, mock_update_db, mock_validate):
        """Test: Empty narrative text"""
        mock_validate.return_value = 'narrative'

        message_data = {
            'complaint_id': 'CAS-123',
            'file_id': 'file-456',
            'narrative_text': '   '
        }

        result = lambda_function.process_single_complaint(message_data)
        
        assert result['success'] is True
        update_call_args = mock_update_db.call_args[0]
        assert update_call_args[1]['narrative'] == 'Empty Narrative'

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

            lambda_function.update_complaint_in_db('CAS-123', extracted_data)
            mock_cursor.execute.assert_called_once()

    @patch('lambda_function.get_connection_string')
    def test_update_complaint_malformed_nested_objects(self, mock_get_connection):
        """Test: Malformed primary_reporter or product_details"""
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
                'primary_reporter': 'Not a dict',
                'product_details': None
            }

            lambda_function.update_complaint_in_db('CAS-123', extracted_data)
            mock_cursor.execute.assert_called_once()

    def test_construct_pdf_prompt_empty_images(self):
        """Test: PDF prompt with empty images list"""
        with patch('builtins.open', mock_open(read_data='Test prompt')):
            result = lambda_function.construct_pdf_prompt([])
            assert len(result[0]['content']) == 1

    @patch('lambda_function.validate_event')
    @patch('lambda_function.update_complaint_in_db')
    def test_process_single_complaint_missing_narrative_key(self, mock_update_db, mock_validate):
        """Test: Missing narrative_text key"""
        mock_validate.return_value = 'narrative'

        message_data = {
            'complaint_id': 'CAS-123',
            'file_id': 'file-456'
        }

        result = lambda_function.process_single_complaint(message_data)
        
        assert result['success'] is True
        update_call_args = mock_update_db.call_args[0]
        assert update_call_args[1]['narrative'] == 'Empty Narrative'


class TestMoveToAdverseEvents:
    """Tests for move_to_adverse_events function"""

    @patch('lambda_function.log_workflow')
    def test_move_to_adverse_events_success(self, mock_log_workflow):
        """Test: Successfully move complaint to adverse_events table with workflow logging"""
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_cursor.connection = mock_conn
        
        lambda_function.move_to_adverse_events(mock_cursor, 'CAS-123')
        
        # Verify workflow logging was called
        mock_log_workflow.assert_called_once_with(
            mock_conn, 'CAS-123', 'MOVED_TO_ADVERSE_EVENTS',
            input_data={'reason': 'Purely adverse event detected'},
            output_data={'target_table': 'adverse_events'}
        )
        # Verify database operations
        assert mock_cursor.execute.call_count == 2
        insert_call = mock_cursor.execute.call_args_list[0][0]
        delete_call = mock_cursor.execute.call_args_list[1][0]
        assert 'INSERT INTO adverse_events' in insert_call[0]
        assert 'DELETE FROM complaints' in delete_call[0]

    def test_move_to_adverse_events_error(self):
        """Test: Error handling in move_to_adverse_events"""
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("Database error")
        
        with pytest.raises(Exception):
            lambda_function.move_to_adverse_events(mock_cursor, 'CAS-123')


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=extract_and_process_complaints.lambda_function", "--cov-report=term-missing"])