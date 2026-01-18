# tests/generate_rca/test_generate_rca_lambda_function.py

import pytest
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock, mock_open
from datetime import datetime, timezone

# ------------------------------------------------------------------
# MOCK DEPENDENCIES BEFORE IMPORT
# ------------------------------------------------------------------
sys.modules["psycopg"] = Mock()
sys.modules["psycopg.rows"] = Mock()
sys.modules["secrets_util"] = Mock()
sys.modules["audit_logger"] = Mock()

# ------------------------------------------------------------------
# IMPORT LAMBDA FUNCTION
# ------------------------------------------------------------------
BASE_PATH = os.path.dirname(__file__)
LAMBDA_PATH = os.path.join(BASE_PATH, "..", "..", "app", "generate_rca")
sys.path.insert(0, LAMBDA_PATH)

import importlib.util

spec = importlib.util.spec_from_file_location(
    "lambda_function",
    os.path.join(LAMBDA_PATH, "lambda_function.py"),
)
lambda_function = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lambda_function)


# ------------------------------------------------------------------
# HELPER
# ------------------------------------------------------------------
def create_mock_cursor():
    cursor = Mock()
    ctx = MagicMock()
    ctx.__enter__.return_value = cursor
    ctx.__exit__.return_value = None
    return ctx, cursor


# ------------------------------------------------------------------
# FIXTURES
# ------------------------------------------------------------------
@pytest.fixture
def mock_bedrock_client():
    """Mock Bedrock client"""
    with patch.object(lambda_function, 'bedrock_client') as mock_client:
        yield mock_client


@pytest.fixture
def mock_db_connection():
    """Mock database connection"""
    mock_conn = Mock()
    mock_conn.commit.return_value = None
    mock_conn.close.return_value = None
    ctx, cursor = create_mock_cursor()
    mock_conn.cursor.return_value = ctx
    return mock_conn, cursor


@pytest.fixture
def sample_investigation_summary():
    """Sample investigation summary for testing"""
    return """
    Who: Christopher Mapp discovered. 
    What: A case packer crash pushed cases on the floor causing the final yield to be 95.18. 
    This is lower than the L13 Lower Limit of 95.89 per 8002-TOOL-04. 
    When: Deviation identified on 08AUG2024. Deviation occurred on 08AUG2024 
    Where: Line 13 Vial Packaging 
    Why: The likely root cause was the case was imperfect and did not open correctly when the machine attempted to load bundles.
    """


@pytest.fixture
def sample_rca_response():
    """Sample RCA response from AI"""
    return [
        {
            "problem_category": "Material/Product Issue",
            "problem_category_validated": "The investigation identified a material issue with the case packaging.",
            "major_root_cause_category": "Material/Parts and Product Issue",
            "major_root_cause_category_validated": "The case packer crash was caused by an imperfect case.",
            "near_root_cause_category": "Materials/Parts Issue",
            "near_root_cause": "The case was imperfect and did not open correctly.",
            "root_cause_category": "Incoming Material Inspection Issue",
            "root_cause": "The incoming material inspection did not detect the imperfect case."
        },
        {
            "problem_category": "Process/Manufacturing Equipment Issue",
            "problem_category_validated": "The investigation identified an equipment reliability issue.",
            "major_root_cause_category": "Equipment Reliability Program Issue",
            "major_root_cause_category_validated": "The case packer experienced a crash due to equipment failure.",
            "near_root_cause_category": "Equipment Reliability Program Design Issue",
            "near_root_cause": "The equipment reliability program did not account for imperfect cases.",
            "root_cause_category": "Critical Equipment Not Identified",
            "root_cause": "The case packer was not identified as critical equipment."
        }
    ]


# ==================================================================
# LOAD_PROMPT TESTS
# ==================================================================
class TestLoadPrompt:
    
    def test_load_prompt_success(self):
        """Test successful prompt loading"""
        prompt_content = "Test prompt content"
        with patch('builtins.open', mock_open(read_data=prompt_content)):
            with patch('os.path.exists', return_value=True):
                result = lambda_function.load_prompt('test_prompt.txt')
                assert result == prompt_content
    
    def test_load_prompt_file_not_found(self):
        """Test prompt loading when file doesn't exist"""
        with patch('os.path.exists', return_value=False):
            with pytest.raises(FileNotFoundError):
                lambda_function.load_prompt('nonexistent.txt')


# ==================================================================
# CALL_BEDROCK TESTS
# ==================================================================
class TestCallBedrock:
    
    def test_call_bedrock_success(self, mock_bedrock_client):
        """Test successful Bedrock API call"""
        mock_response = {
            'output': {
                'message': {
                    'content': [{'text': 'Test response'}]
                }
            }
        }
        mock_bedrock_client.converse.return_value = mock_response
        
        result = lambda_function.call_bedrock("Test prompt")
        
        assert result == "Test response"
        mock_bedrock_client.converse.assert_called_once()
    
    def test_call_bedrock_error(self, mock_bedrock_client):
        """Test Bedrock API call error handling"""
        mock_bedrock_client.converse.side_effect = Exception("API Error")
        
        with pytest.raises(Exception):
            lambda_function.call_bedrock("Test prompt")


# ==================================================================
# GENERATE_MULTIPLE_RCAS TESTS
# ==================================================================
class TestGenerateMultipleRCAs:
    
    def test_generate_multiple_rcas_success(self, mock_bedrock_client, sample_investigation_summary, sample_rca_response):
        """Test successful generation of multiple RCAs"""
        mock_response = {
            'output': {
                'message': {
                    'content': [{'text': json.dumps(sample_rca_response)}]
                }
            }
        }
        mock_bedrock_client.converse.return_value = mock_response
        
        with patch.object(lambda_function, 'load_prompt', return_value="Test prompt {investigation_summary}"):
            result = lambda_function.generate_multiple_rcas(sample_investigation_summary)
        
        assert isinstance(result, list)
        assert len(result) >= 2
        assert 'problem_category' in result[0]
    
    def test_generate_multiple_rcas_single_rca_fallback(self, mock_bedrock_client, sample_investigation_summary):
        """Test fallback when only 1 RCA is generated"""
        single_rca = [{
            "problem_category": "Test",
            "problem_category_validated": "Test validated"
        }]
        mock_response = {
            'output': {
                'message': {
                    'content': [{'text': json.dumps(single_rca)}]
                }
            }
        }
        mock_bedrock_client.converse.return_value = mock_response
        
        with patch.object(lambda_function, 'load_prompt', return_value="Test prompt {investigation_summary}"):
            with patch.object(lambda_function, 'generate_rcas_sequential', return_value=[{}, {}]) as mock_sequential:
                result = lambda_function.generate_multiple_rcas(sample_investigation_summary)
                mock_sequential.assert_called_once()
    
    def test_generate_multiple_rcas_json_error_fallback(self, mock_bedrock_client, sample_investigation_summary):
        """Test fallback when JSON parsing fails"""
        mock_response = {
            'output': {
                'message': {
                    'content': [{'text': 'Invalid JSON'}]
                }
            }
        }
        mock_bedrock_client.converse.return_value = mock_response
        
        with patch.object(lambda_function, 'load_prompt', return_value="Test prompt {investigation_summary}"):
            with patch.object(lambda_function, 'generate_rcas_sequential', return_value=[{}, {}]) as mock_sequential:
                result = lambda_function.generate_multiple_rcas(sample_investigation_summary)
                mock_sequential.assert_called_once()


# ==================================================================
# GENERATE_RCAS_SEQUENTIAL TESTS
# ==================================================================
class TestGenerateRCAsSequential:
    
    def test_generate_rcas_sequential_success(self, sample_investigation_summary):
        """Test sequential RCA generation"""
        with patch.object(lambda_function, 'generate_problem_category', return_value="Problem category"):
            with patch.object(lambda_function, 'generate_major_root_cause_category', return_value="Major category"):
                with patch.object(lambda_function, 'generate_near_root_cause', return_value="Near cause"):
                    with patch.object(lambda_function, 'generate_root_cause', return_value="Root cause"):
                        result = lambda_function.generate_rcas_sequential(sample_investigation_summary)
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert 'problem_category_validated' in result[0]
        assert 'problem_category_validated' in result[1]


# ==================================================================
# GENERATE_PROBLEM_CATEGORY TESTS
# ==================================================================
class TestGenerateProblemCategory:
    
    def test_generate_problem_category_success(self, sample_investigation_summary):
        """Test problem category generation"""
        with patch.object(lambda_function, 'load_prompt', return_value="Test prompt {investigation_summary}"):
            with patch.object(lambda_function, 'call_bedrock', return_value="Generated problem category"):
                result = lambda_function.generate_problem_category(sample_investigation_summary)
        
        assert result == "Generated problem category"


# ==================================================================
# LAMBDA_HANDLER TESTS
# ==================================================================
class TestLambdaHandler:
    
    @patch.object(lambda_function, 'get_db_connection')
    @patch.object(lambda_function, 'generate_multiple_rcas')
    @patch('sys.modules', {'audit_logger': Mock()})
    def test_lambda_handler_success(self, mock_generate_rcas, mock_get_db, sample_investigation_summary, sample_rca_response):
        """Test successful lambda handler execution"""
        # Mock database connection
        mock_conn, cursor = create_mock_cursor()
        mock_get_db.return_value = mock_conn
        
        # Mock RCA generation
        mock_generate_rcas.return_value = sample_rca_response
        
        # Create event
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({
                'investigation_summary': sample_investigation_summary,
                'deviationId': 'DV-00001'
            })
        }
        
        # Execute lambda
        result = lambda_function.lambda_handler(event, {})
        body = json.loads(result['body'])
        
        # Assertions
        assert result['statusCode'] == 200
        assert body['success'] is True
        assert 'RCA(s) generated successfully' in body['message']
        assert isinstance(body['data'], list)
        assert len(body['data']) >= 2
    
    def test_lambda_handler_options_request(self):
        """Test CORS preflight OPTIONS request"""
        event = {'httpMethod': 'OPTIONS'}
        result = lambda_function.lambda_handler(event, {})
        
        assert result['statusCode'] == 200
        assert 'Access-Control-Allow-Origin' in result['headers']
    
    def test_lambda_handler_invalid_method(self):
        """Test invalid HTTP method"""
        event = {'httpMethod': 'GET'}
        result = lambda_function.lambda_handler(event, {})
        body = json.loads(result['body'])
        
        assert result['statusCode'] == 405
        assert body['success'] is False
    
    def test_lambda_handler_missing_investigation_summary(self):
        """Test missing investigation_summary"""
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({})
        }
        result = lambda_function.lambda_handler(event, {})
        body = json.loads(result['body'])
        
        assert result['statusCode'] == 400
        assert body['success'] is False
        assert 'investigation_summary is required' in body['message']
    
    def test_lambda_handler_empty_investigation_summary(self):
        """Test empty investigation_summary"""
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({
                'investigation_summary': '   '
            })
        }
        result = lambda_function.lambda_handler(event, {})
        body = json.loads(result['body'])
        
        assert result['statusCode'] == 400
        assert body['success'] is False
    
    def test_lambda_handler_invalid_investigation_summary_type(self):
        """Test invalid investigation_summary type"""
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({
                'investigation_summary': 123
            })
        }
        result = lambda_function.lambda_handler(event, {})
        body = json.loads(result['body'])
        
        assert result['statusCode'] == 400
        assert body['success'] is False
        assert 'must be a string' in body['message']
    
    @patch.object(lambda_function, 'get_db_connection')
    @patch.object(lambda_function, 'generate_multiple_rcas')
    def test_lambda_handler_generation_error(self, mock_generate_rcas, mock_get_db, sample_investigation_summary):
        """Test error during RCA generation"""
        # Mock database connection
        mock_conn, cursor = create_mock_cursor()
        mock_get_db.return_value = mock_conn
        
        # Mock RCA generation error
        mock_generate_rcas.side_effect = Exception("Generation failed")
        
        # Create event
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({
                'investigation_summary': sample_investigation_summary
            })
        }
        
        # Execute lambda
        result = lambda_function.lambda_handler(event, {})
        body = json.loads(result['body'])
        
        # Assertions
        assert result['statusCode'] == 500
        assert body['success'] is False


# ==================================================================
# INTEGRATION TESTS
# ==================================================================
class TestIntegration:
    
    @patch.object(lambda_function, 'get_db_connection')
    @patch.object(lambda_function, 'bedrock_client')
    def test_end_to_end_rca_generation(self, mock_bedrock_client, mock_get_db, sample_investigation_summary, sample_rca_response):
        """Test end-to-end RCA generation flow"""
        # Mock database
        mock_conn, cursor = create_mock_cursor()
        mock_get_db.return_value = mock_conn
        
        # Mock Bedrock response
        mock_response = {
            'output': {
                'message': {
                    'content': [{'text': json.dumps(sample_rca_response)}]
                }
            }
        }
        mock_bedrock_client.converse.return_value = mock_response
        
        # Mock prompt loading
        with patch.object(lambda_function, 'load_prompt', return_value="Test prompt {investigation_summary}"):
            # Create event
            event = {
                'httpMethod': 'POST',
                'body': json.dumps({
                    'investigation_summary': sample_investigation_summary,
                    'deviationId': 'DV-00001'
                })
            }
            
            # Execute
            result = lambda_function.lambda_handler(event, {})
            body = json.loads(result['body'])
            
            # Verify
            assert result['statusCode'] == 200
            assert body['success'] is True
            assert len(body['data']) >= 2
            
            # Verify RCA structure
            for rca in body['data']:
                assert 'deviation_id' in rca
                assert 'problem_category' in rca
                assert 'major_root_cause_category' in rca
                assert 'is_ai_generated' in rca
                assert rca['is_ai_generated'] is True
