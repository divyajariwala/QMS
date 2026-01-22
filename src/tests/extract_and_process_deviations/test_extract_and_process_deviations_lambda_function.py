"""
Unit tests for extract_and_process_deviations Lambda function
"""
import json
import sys
from unittest.mock import MagicMock, patch, Mock, mock_open
import pytest
import importlib.util
from datetime import datetime
import io

# Mock dependencies before importing the lambda module
mock_secrets_util = MagicMock()
mock_audit_logger = MagicMock()
mock_fitz = MagicMock()
mock_pil = MagicMock()

sys.modules['secrets_util'] = mock_secrets_util
sys.modules['audit_logger'] = mock_audit_logger
sys.modules['fitz'] = mock_fitz
sys.modules['PIL'] = mock_pil
sys.modules['PIL.Image'] = mock_pil.Image

# Load the lambda_function module
spec = importlib.util.spec_from_file_location(
    "extract_and_process_deviations_lambda",
    "src/app/extract_and_process_deviations/lambda_function.py"
)
lambda_module = importlib.util.module_from_spec(spec)
sys.modules['extract_and_process_deviations_lambda'] = lambda_module
spec.loader.exec_module(lambda_module)


@pytest.fixture(autouse=True)
def setup_environment(monkeypatch):
    """Set up environment variables for all tests"""
    monkeypatch.setenv('env', 'test')
    monkeypatch.setenv('db_secret_base_name', 'test-db-secret')
    monkeypatch.setenv('db_region', 'us-east-1')


@pytest.fixture
def mock_secrets():
    """Mock secrets_util.get_secret"""
    with patch('extract_and_process_deviations_lambda.get_secret') as mock:
        mock.return_value = {
            'host': 'test-host',
            'port': 5432,
            'dbname': 'test-db',
            'username': 'test-user',
            'password': 'test-password'
        }
        yield mock


@pytest.fixture
def mock_psycopg():
    """Mock psycopg connection and cursor"""
    with patch('extract_and_process_deviations_lambda.psycopg') as mock_pg:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        
        # Setup cursor context manager
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        
        # Setup connection context manager
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        
        # Setup connect to return connection
        mock_pg.connect.return_value = mock_conn
        
        yield {
            'psycopg': mock_pg,
            'connection': mock_conn,
            'cursor': mock_cursor
        }


@pytest.fixture
def mock_boto3():
    """Mock boto3 clients"""
    with patch('extract_and_process_deviations_lambda.boto3') as mock_b3:
        mock_s3 = MagicMock()
        mock_bedrock = MagicMock()
        
        def client_factory(service_name):
            if service_name == 's3':
                return mock_s3
            elif service_name == 'bedrock-runtime':
                return mock_bedrock
            return MagicMock()
        
        mock_b3.client.side_effect = client_factory
        
        yield {
            'boto3': mock_b3,
            's3': mock_s3,
            'bedrock': mock_bedrock
        }


@pytest.fixture
def mock_log_deviation_workflow():
    """Mock audit_logger.log_deviation_workflow"""
    with patch('extract_and_process_deviations_lambda.log_deviation_workflow') as mock:
        yield mock


@pytest.fixture
def sample_pdf_bytes():
    """Sample PDF bytes"""
    return b'%PDF-1.4 sample pdf content'


@pytest.fixture
def sample_extracted_data():
    """Sample extracted data from Claude"""
    return {
        "title": "Test Deviation",
        "description": "Test description",
        "immediate_steps_taken": "Test steps",
        "quality_risk_evaluation": "Test evaluation",
        "investigation_summary": "Test summary",
        "capa_plan": "Test CAPA",
        "recurrence_check_details": "Test recurrence",
        "effectiveness_check_plan": "Test effectiveness"
    }


@pytest.fixture
def sample_tool_spec():
    """Sample tool spec JSON"""
    return {
        "toolSpec": {
            "name": "extract_deviation",
            "description": "Extract deviation data"
        }
    }


@pytest.fixture
def valid_sqs_event():
    """Valid SQS event with single record"""
    return {
        "Records": [
            {
                "body": json.dumps({
                    "deviation_id": "DV-12345",
                    "s3path": "s3://test-bucket/test.pdf"
                })
            }
        ]
    }


@pytest.fixture
def valid_direct_event():
    """Valid direct invocation event"""
    return {
        "deviation_id": "DV-12345",
        "s3path": "s3://test-bucket/test.pdf"
    }


# ============================================================================
# SUCCESS CASES - PDF DOCUMENT EXTRACTION
# ============================================================================

def test_successful_pdf_document_extraction(mock_secrets, mock_psycopg, mock_boto3, 
                                            mock_log_deviation_workflow, sample_pdf_bytes, 
                                            sample_extracted_data, sample_tool_spec, valid_direct_event):
    """Test successful extraction using PDF document method"""
    # Setup S3 mock
    mock_boto3['s3'].head_object.return_value = {'ContentLength': 1024 * 1024}  # 1MB
    mock_boto3['s3'].get_object.return_value = {'Body': io.BytesIO(sample_pdf_bytes)}
    
    # Setup Bedrock mock for PDF document extraction
    mock_boto3['bedrock'].converse.return_value = {
        'output': {
            'message': {
                'content': [
                    {
                        'toolUse': {
                            'input': sample_extracted_data
                        }
                    }
                ]
            }
        }
    }
    
    # Mock file reads - need to handle both prompt.txt and toolspec.json
    def mock_open_handler(filename, *args, **kwargs):
        if 'toolspec.json' in str(filename):
            return mock_open(read_data=json.dumps(sample_tool_spec))()
        else:
            return mock_open(read_data='test prompt')()
    
    with patch('builtins.open', side_effect=mock_open_handler):
        response = lambda_module.lambda_handler(valid_direct_event, None)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    assert body['deviation_id'] == 'DV-12345'
    assert body['extracted_data']['title'] == 'Test Deviation'
    
    # Verify database update
    mock_psycopg['cursor'].execute.assert_called()
    call_args = mock_psycopg['cursor'].execute.call_args[0]
    assert 'UPDATE deviations' in call_args[0]
    assert call_args[1][0] == 'Test Deviation'  # title
    assert call_args[1][-1] == 'DV-12345'  # deviation_id


def test_successful_sqs_batch_processing(mock_secrets, mock_psycopg, mock_boto3,
                                         mock_log_deviation_workflow, sample_pdf_bytes,
                                         sample_extracted_data, sample_tool_spec):
    """Test successful processing of SQS batch with multiple records"""
    # Setup S3 mock
    mock_boto3['s3'].head_object.return_value = {'ContentLength': 1024 * 1024}
    mock_boto3['s3'].get_object.return_value = {'Body': io.BytesIO(sample_pdf_bytes)}
    
    # Setup Bedrock mock
    mock_boto3['bedrock'].converse.return_value = {
        'output': {
            'message': {
                'content': [
                    {
                        'toolUse': {
                            'input': sample_extracted_data
                        }
                    }
                ]
            }
        }
    }
    
    event = {
        "Records": [
            {
                "body": json.dumps({
                    "deviation_id": "DV-00001",
                    "s3path": "s3://test-bucket/test1.pdf"
                })
            },
            {
                "body": json.dumps({
                    "deviation_id": "DV-00002",
                    "s3path": "s3://test-bucket/test2.pdf"
                })
            }
        ]
    }
    
    def mock_open_handler(filename, *args, **kwargs):
        if 'toolspec.json' in str(filename):
            return mock_open(read_data=json.dumps(sample_tool_spec))()
        else:
            return mock_open(read_data='test prompt')()
    
    with patch('builtins.open', side_effect=mock_open_handler):
        response = lambda_module.lambda_handler(event, None)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert len(body) == 2
    assert body[0]['success'] is True
    assert body[1]['success'] is True


# ============================================================================
# SUCCESS CASES - VISION FALLBACK
# ============================================================================

def test_vision_fallback_when_pdf_extraction_fails(mock_secrets, mock_psycopg, mock_boto3,
                                                    mock_log_deviation_workflow, sample_pdf_bytes,
                                                    sample_tool_spec, valid_direct_event):
    """Test vision fallback when PDF document extraction returns empty description"""
    # Setup S3 mock
    mock_boto3['s3'].head_object.return_value = {'ContentLength': 1024 * 1024}
    mock_boto3['s3'].get_object.return_value = {'Body': io.BytesIO(sample_pdf_bytes)}
    
    # First call (PDF) returns empty description
    # Second call (Vision) returns valid data
    vision_data = {
        "title": "Vision Extracted Title",
        "description": "Vision extracted description",
        "immediate_steps_taken": "Steps",
        "quality_risk_evaluation": "Evaluation",
        "investigation_summary": "Summary",
        "capa_plan": "CAPA",
        "recurrence_check_details": "Recurrence",
        "effectiveness_check_plan": "Effectiveness"
    }
    
    mock_boto3['bedrock'].converse.side_effect = [
        # First call - PDF extraction returns empty
        {
            'output': {
                'message': {
                    'content': [
                        {
                            'toolUse': {
                                'input': {
                                    "title": "Test",
                                    "description": "",  # Empty triggers fallback
                                }
                            }
                        }
                    ]
                }
            }
        },
        # Second call - Vision extraction
        {
            'output': {
                'message': {
                    'content': [
                        {
                            'toolUse': {
                                'input': vision_data
                            }
                        }
                    ]
                }
            }
        }
    ]
    
    # Mock fitz for PDF to images conversion
    mock_page = MagicMock()
    mock_pixmap = MagicMock()
    mock_pixmap.tobytes.return_value = b'fake_png_data'
    mock_page.get_pixmap.return_value = mock_pixmap
    
    mock_doc = MagicMock()
    mock_doc.__iter__ = MagicMock(return_value=iter([mock_page]))
    mock_doc.close = MagicMock()
    
    def mock_open_handler(filename, *args, **kwargs):
        if 'toolspec.json' in str(filename):
            return mock_open(read_data=json.dumps(sample_tool_spec))()
        else:
            return mock_open(read_data='test prompt')()
    
    with patch('extract_and_process_deviations_lambda.fitz.open', return_value=mock_doc):
        with patch('extract_and_process_deviations_lambda.Image.open') as mock_img_open:
            mock_img = MagicMock()
            mock_img_open.return_value = mock_img
            
            with patch('builtins.open', side_effect=mock_open_handler):
                response = lambda_module.lambda_handler(valid_direct_event, None)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    assert body['extracted_data']['_extraction_method'] == 'vision'
    assert body['extracted_data']['title'] == 'Vision Extracted Title'


def test_vision_fallback_when_pdf_extraction_returns_none(mock_secrets, mock_psycopg, mock_boto3,
                                                           mock_log_deviation_workflow, sample_pdf_bytes,
                                                           sample_tool_spec, valid_direct_event):
    """Test vision fallback when PDF document extraction returns None"""
    # Setup S3 mock
    mock_boto3['s3'].head_object.return_value = {'ContentLength': 1024 * 1024}
    mock_boto3['s3'].get_object.return_value = {'Body': io.BytesIO(sample_pdf_bytes)}
    
    vision_data = {
        "title": "Vision Title",
        "description": "Vision description",
        "immediate_steps_taken": "Steps",
        "quality_risk_evaluation": "Eval",
        "investigation_summary": "Summary",
        "capa_plan": "CAPA",
        "recurrence_check_details": "Recurrence",
        "effectiveness_check_plan": "Effectiveness"
    }
    
    # First call returns no toolUse (None)
    # Second call returns vision data
    mock_boto3['bedrock'].converse.side_effect = [
        {
            'output': {
                'message': {
                    'content': []  # No toolUse
                }
            }
        },
        {
            'output': {
                'message': {
                    'content': [
                        {
                            'toolUse': {
                                'input': vision_data
                            }
                        }
                    ]
                }
            }
        }
    ]
    
    # Mock fitz
    mock_page = MagicMock()
    mock_pixmap = MagicMock()
    mock_pixmap.tobytes.return_value = b'fake_png_data'
    mock_page.get_pixmap.return_value = mock_pixmap
    
    mock_doc = MagicMock()
    mock_doc.__iter__ = MagicMock(return_value=iter([mock_page]))
    mock_doc.close = MagicMock()
    
    def mock_open_handler(filename, *args, **kwargs):
        if 'toolspec.json' in str(filename):
            return mock_open(read_data=json.dumps(sample_tool_spec))()
        else:
            return mock_open(read_data='test prompt')()
    
    with patch('extract_and_process_deviations_lambda.fitz.open', return_value=mock_doc):
        with patch('extract_and_process_deviations_lambda.Image.open'):
            with patch('builtins.open', side_effect=mock_open_handler):
                response = lambda_module.lambda_handler(valid_direct_event, None)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['extracted_data']['_extraction_method'] == 'vision'


def test_empty_pdf_handling(mock_secrets, mock_psycopg, mock_boto3,
                            mock_log_deviation_workflow, sample_pdf_bytes,
                            sample_tool_spec, valid_direct_event):
    """Test handling of empty PDF (no pages)"""
    # Setup S3 mock
    mock_boto3['s3'].head_object.return_value = {'ContentLength': 1024 * 1024}
    mock_boto3['s3'].get_object.return_value = {'Body': io.BytesIO(sample_pdf_bytes)}
    
    # PDF extraction returns None
    mock_boto3['bedrock'].converse.return_value = {
        'output': {
            'message': {
                'content': []
            }
        }
    }
    
    # Mock fitz to return empty document
    mock_doc = MagicMock()
    mock_doc.__iter__ = MagicMock(return_value=iter([]))  # No pages
    mock_doc.close = MagicMock()
    
    def mock_open_handler(filename, *args, **kwargs):
        if 'toolspec.json' in str(filename):
            return mock_open(read_data=json.dumps(sample_tool_spec))()
        else:
            return mock_open(read_data='test prompt')()
    
    with patch('extract_and_process_deviations_lambda.fitz.open', return_value=mock_doc):
        with patch('builtins.open', side_effect=mock_open_handler):
            response = lambda_module.lambda_handler(valid_direct_event, None)
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    assert body['extracted_data']['_extraction_method'] == 'failed'
    assert body['extracted_data']['title'] == 'Extraction Failed'
    assert body['extracted_data']['description'] == 'Unable to extract data from PDF'


# ============================================================================
# ERROR CASES
# ============================================================================

def test_pdf_too_large_error(mock_secrets, mock_psycopg, mock_boto3, valid_direct_event):
    """Test error when PDF exceeds size limit"""
    # Setup S3 mock to return large file
    mock_boto3['s3'].head_object.return_value = {
        'ContentLength': 60 * 1024 * 1024  # 60MB > 50MB limit
    }
    
    response = lambda_module.lambda_handler(valid_direct_event, None)
    
    assert response['statusCode'] == 500
    body = json.loads(response['body'])
    assert body['success'] is False


def test_s3_fetch_error(mock_secrets, mock_psycopg, mock_boto3, valid_direct_event):
    """Test error when S3 fetch fails"""
    mock_boto3['s3'].head_object.side_effect = Exception("S3 error")
    
    response = lambda_module.lambda_handler(valid_direct_event, None)
    
    assert response['statusCode'] == 500
    body = json.loads(response['body'])
    assert body['success'] is False


def test_database_update_error(mock_secrets, mock_psycopg, mock_boto3,
                               sample_pdf_bytes, sample_extracted_data, sample_tool_spec,
                               valid_direct_event):
    """Test error when database update fails"""
    # Setup S3 mock
    mock_boto3['s3'].head_object.return_value = {'ContentLength': 1024 * 1024}
    mock_boto3['s3'].get_object.return_value = {'Body': io.BytesIO(sample_pdf_bytes)}
    
    # Setup Bedrock mock
    mock_boto3['bedrock'].converse.return_value = {
        'output': {
            'message': {
                'content': [
                    {
                        'toolUse': {
                            'input': sample_extracted_data
                        }
                    }
                ]
            }
        }
    }
    
    # Database error
    mock_psycopg['cursor'].execute.side_effect = Exception("Database error")
    
    def mock_open_handler(filename, *args, **kwargs):
        if 'toolspec.json' in str(filename):
            return mock_open(read_data=json.dumps(sample_tool_spec))()
        else:
            return mock_open(read_data='test prompt')()
    
    with patch('builtins.open', side_effect=mock_open_handler):
        response = lambda_module.lambda_handler(valid_direct_event, None)
    
    assert response['statusCode'] == 500
    body = json.loads(response['body'])
    assert body['success'] is False


def test_bedrock_api_error(mock_secrets, mock_psycopg, mock_boto3,
                           sample_pdf_bytes, sample_tool_spec, valid_direct_event):
    """Test error when Bedrock API fails - falls back to vision then marks as failed"""
    # Setup S3 mock
    mock_boto3['s3'].head_object.return_value = {'ContentLength': 1024 * 1024}
    mock_boto3['s3'].get_object.return_value = {'Body': io.BytesIO(sample_pdf_bytes)}
    
    # Bedrock error - will trigger fallback to vision
    mock_boto3['bedrock'].converse.side_effect = Exception("Bedrock API error")
    
    # Mock fitz to return empty document (no pages for vision fallback)
    mock_doc = MagicMock()
    mock_doc.__iter__ = MagicMock(return_value=iter([]))
    mock_doc.close = MagicMock()
    
    def mock_open_handler(filename, *args, **kwargs):
        if 'toolspec.json' in str(filename):
            return mock_open(read_data=json.dumps(sample_tool_spec))()
        else:
            return mock_open(read_data='test prompt')()
    
    with patch('extract_and_process_deviations_lambda.fitz.open', return_value=mock_doc):
        with patch('builtins.open', side_effect=mock_open_handler):
            response = lambda_module.lambda_handler(valid_direct_event, None)
    
    # When both PDF and vision fail, it returns 200 with failed status
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['success'] is True
    assert body['extracted_data']['_extraction_method'] == 'failed'


# ============================================================================
# HELPER FUNCTION TESTS
# ============================================================================

def test_get_connection_string_success(mock_secrets, monkeypatch):
    """Test get_connection_string builds correct connection string"""
    lambda_module._connection_string = None
    lambda_module._db_credentials = None
    
    monkeypatch.setenv('env', 'test')
    monkeypatch.setenv('db_secret_base_name', 'test-db-secret')
    lambda_module.ENV = 'test'
    lambda_module.DB_SECRET_NAME = 'qms-test-test-db-secret'
    
    conn_string = lambda_module.get_connection_string()
    
    assert conn_string == "postgresql://test-user:test-password@test-host:5432/test-db"


def test_get_connection_string_cached(mock_secrets):
    """Test get_connection_string uses cached value"""
    lambda_module._connection_string = "cached://connection"
    
    conn_string = lambda_module.get_connection_string()
    
    assert conn_string == "cached://connection"
    mock_secrets.assert_not_called()


def test_fetch_pdf_from_s3_success(mock_boto3, sample_pdf_bytes):
    """Test successful PDF fetch from S3"""
    mock_boto3['s3'].head_object.return_value = {'ContentLength': 1024 * 1024}
    mock_boto3['s3'].get_object.return_value = {'Body': io.BytesIO(sample_pdf_bytes)}
    
    result = lambda_module.fetch_pdf_from_s3("s3://test-bucket/path/to/file.pdf")
    
    assert result == sample_pdf_bytes
    mock_boto3['s3'].head_object.assert_called_once_with(
        Bucket='test-bucket',
        Key='path/to/file.pdf'
    )


def test_fetch_pdf_from_s3_size_limit(mock_boto3):
    """Test PDF size limit enforcement"""
    mock_boto3['s3'].head_object.return_value = {
        'ContentLength': 60 * 1024 * 1024  # 60MB
    }
    
    with pytest.raises(ValueError, match="PDF too large"):
        lambda_module.fetch_pdf_from_s3("s3://test-bucket/large.pdf")


def test_pdf_to_images_success():
    """Test PDF to images conversion"""
    mock_page = MagicMock()
    mock_pixmap = MagicMock()
    mock_pixmap.tobytes.return_value = b'fake_png_data'
    mock_page.get_pixmap.return_value = mock_pixmap
    
    mock_doc = MagicMock()
    mock_doc.__iter__ = MagicMock(return_value=iter([mock_page, mock_page]))
    mock_doc.close = MagicMock()
    
    with patch('extract_and_process_deviations_lambda.fitz.open', return_value=mock_doc):
        with patch('extract_and_process_deviations_lambda.Image.open') as mock_img:
            mock_img.return_value = MagicMock()
            images = lambda_module.pdf_to_images(b'pdf_bytes')
    
    assert len(images) == 2
    mock_doc.close.assert_called_once()


def test_images_to_base64_success():
    """Test images to base64 conversion"""
    mock_img1 = MagicMock()
    mock_img2 = MagicMock()
    
    def save_side_effect(buf, format):
        buf.write(b'fake_image_data')
    
    mock_img1.save.side_effect = save_side_effect
    mock_img2.save.side_effect = save_side_effect
    
    result = lambda_module.images_to_base64([mock_img1, mock_img2])
    
    assert len(result) == 2
    assert isinstance(result[0], str)
    assert isinstance(result[1], str)


def test_load_tool_spec():
    """Test loading tool spec from JSON file"""
    tool_spec = {"name": "test_tool", "description": "Test"}
    
    with patch('builtins.open', mock_open(read_data=json.dumps(tool_spec))):
        result = lambda_module.load_tool_spec()
    
    assert result == tool_spec


def test_extract_from_pdf_document_success(mock_boto3, sample_pdf_bytes, sample_extracted_data, sample_tool_spec):
    """Test successful PDF document extraction"""
    mock_boto3['bedrock'].converse.return_value = {
        'output': {
            'message': {
                'content': [
                    {
                        'toolUse': {
                            'input': sample_extracted_data
                        }
                    }
                ]
            }
        }
    }
    
    def mock_open_handler(filename, *args, **kwargs):
        if 'toolspec.json' in str(filename):
            return mock_open(read_data=json.dumps(sample_tool_spec))()
        else:
            return mock_open(read_data='test prompt')()
    
    with patch('builtins.open', side_effect=mock_open_handler):
        result = lambda_module.extract_from_pdf_document(sample_pdf_bytes, "test.pdf")
    
    assert result == sample_extracted_data


def test_extract_from_pdf_document_no_tool_use(mock_boto3, sample_pdf_bytes, sample_tool_spec):
    """Test PDF document extraction when no toolUse in response"""
    mock_boto3['bedrock'].converse.return_value = {
        'output': {
            'message': {
                'content': [
                    {'text': 'Some text response'}
                ]
            }
        }
    }
    
    def mock_open_handler(filename, *args, **kwargs):
        if 'toolspec.json' in str(filename):
            return mock_open(read_data=json.dumps(sample_tool_spec))()
        else:
            return mock_open(read_data='test prompt')()
    
    with patch('builtins.open', side_effect=mock_open_handler):
        result = lambda_module.extract_from_pdf_document(sample_pdf_bytes, "test.pdf")
    
    assert result is None


def test_extract_from_pdf_document_error(mock_boto3, sample_pdf_bytes, sample_tool_spec):
    """Test PDF document extraction handles errors"""
    mock_boto3['bedrock'].converse.side_effect = Exception("API error")
    
    def mock_open_handler(filename, *args, **kwargs):
        if 'toolspec.json' in str(filename):
            return mock_open(read_data=json.dumps(sample_tool_spec))()
        else:
            return mock_open(read_data='test prompt')()
    
    with patch('builtins.open', side_effect=mock_open_handler):
        result = lambda_module.extract_from_pdf_document(sample_pdf_bytes, "test.pdf")
    
    assert result is None


def test_extract_from_images_success(mock_boto3, sample_extracted_data, sample_tool_spec):
    """Test successful image extraction"""
    mock_img = MagicMock()
    
    def save_side_effect(buf, format):
        buf.write(b'fake_image_data')
    
    mock_img.save.side_effect = save_side_effect
    
    mock_boto3['bedrock'].converse.return_value = {
        'output': {
            'message': {
                'content': [
                    {
                        'toolUse': {
                            'input': sample_extracted_data
                        }
                    }
                ]
            }
        }
    }
    
    def mock_open_handler(filename, *args, **kwargs):
        if 'toolspec.json' in str(filename):
            return mock_open(read_data=json.dumps(sample_tool_spec))()
        else:
            return mock_open(read_data='test prompt')()
    
    with patch('builtins.open', side_effect=mock_open_handler):
        result = lambda_module.extract_from_images([mock_img])
    
    assert result == sample_extracted_data


def test_update_deviation_in_db_success(mock_secrets, mock_psycopg, 
                                        mock_log_deviation_workflow, sample_extracted_data):
    """Test successful database update"""
    lambda_module._connection_string = "postgresql://test:test@localhost:5432/test"
    
    start_time = datetime.utcnow()
    lambda_module.update_deviation_in_db('DV-12345', sample_extracted_data, start_time)
    
    mock_psycopg['cursor'].execute.assert_called_once()
    call_args = mock_psycopg['cursor'].execute.call_args[0]
    assert 'UPDATE deviations' in call_args[0]
    assert call_args[1][-1] == 'DV-12345'
    
    mock_log_deviation_workflow.assert_called_once()


def test_process_single_deviation_success(mock_secrets, mock_psycopg, mock_boto3,
                                          mock_log_deviation_workflow, sample_pdf_bytes,
                                          sample_extracted_data, sample_tool_spec):
    """Test successful processing of single deviation"""
    mock_boto3['s3'].head_object.return_value = {'ContentLength': 1024 * 1024}
    mock_boto3['s3'].get_object.return_value = {'Body': io.BytesIO(sample_pdf_bytes)}
    
    mock_boto3['bedrock'].converse.return_value = {
        'output': {
            'message': {
                'content': [
                    {
                        'toolUse': {
                            'input': sample_extracted_data
                        }
                    }
                ]
            }
        }
    }
    
    message = {
        "deviation_id": "DV-12345",
        "s3path": "s3://test-bucket/test.pdf"
    }
    
    def mock_open_handler(filename, *args, **kwargs):
        if 'toolspec.json' in str(filename):
            return mock_open(read_data=json.dumps(sample_tool_spec))()
        else:
            return mock_open(read_data='test prompt')()
    
    with patch('builtins.open', side_effect=mock_open_handler):
        result = lambda_module.process_single_deviation(message)
    
    assert result['success'] is True
    assert result['deviation_id'] == 'DV-12345'
    assert 'extracted_data' in result


def test_process_single_deviation_error(mock_boto3):
    """Test process_single_deviation handles errors"""
    mock_boto3['s3'].head_object.side_effect = Exception("S3 error")
    
    message = {
        "deviation_id": "DV-12345",
        "s3path": "s3://test-bucket/test.pdf"
    }
    
    with pytest.raises(Exception):
        lambda_module.process_single_deviation(message)
