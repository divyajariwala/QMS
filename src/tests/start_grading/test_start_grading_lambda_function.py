"""
Unit tests for start_grading lambda function

Tests cover:
- get_deviation_info: Database queries for deviation data
- load_prompt: Loading prompt templates
- call_bedrock: AI model invocation
- get_section_requirements: Section requirements retrieval
- grade_single_section: Individual section grading
- grade_all_sections: All sections grading
- save_grading_results: Database save/update operations
- lambda_handler: API endpoint handling (initial and regeneration modes)
"""

import json
import pytest
from unittest.mock import Mock, patch, mock_open, MagicMock
import sys
import os
import importlib.util

# Mock dependencies before importing lambda_function
sys.modules['audit_logger'] = MagicMock()
sys.modules['secrets_util'] = MagicMock()
sys.modules['utils'] = MagicMock()

# Mock the response and utility functions
mock_utils = sys.modules['utils']
mock_utils.response = lambda status, message, data=None: {
    'statusCode': status,
    'headers': {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    },
    'body': json.dumps({
        'success': status < 400,
        'message': message,
        'data': data
    })
}
mock_utils.handle_cors_preflight = lambda: {
    'statusCode': 200,
    'headers': {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
    },
    'body': ''
}
mock_utils.parse_event_body = lambda event: json.loads(event.get('body', '{}'))

# Import the specific lambda_function module for start_grading
lambda_path = os.path.join(os.path.dirname(__file__), '../../app/start_grading/lambda_function.py')
spec = importlib.util.spec_from_file_location("start_grading_lambda", lambda_path)
lambda_function = importlib.util.module_from_spec(spec)
sys.modules['start_grading_lambda'] = lambda_function
spec.loader.exec_module(lambda_function)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_deviation_data():
    """Sample deviation data from database"""
    return {
        'deviation_id': 'DV-00001',
        'title': 'QA Oversight Gap in Non-Routine Analytical Results',
        'description': 'On 01Nov2023 during periodic review of KIN-OVR-42071 it was noted by QA that non-routine Analytical Results verification did not have QA oversight.',
        'immediate_steps_taken': 'Cleaning representatives were notified and this record was raised.',
        'quality_risk_evaluation': 'Preliminary risk assessment indicates potential for inconsistent verification outcomes.',
        'investigation_summary': 'Investigation discovered discrepancy in approval requirements between KIN-OVR-42071 and KIN-OVR-41656.',
        'capa_plan': '1) Harmonize approval requirements. 2) Update verification workflow. 3) Train personnel.',
        'recurrence_check_details': 'Retrospective review of last 12 months of non-routine analytical runs.',
        'effectiveness_check_plan': 'Effectiveness measured by zero recurrences over two consecutive quarters.'
    }


@pytest.fixture
def sample_grading_result():
    """Sample grading result for a single section"""
    return {
        "section_label": "Title",
        "text": "QA Oversight Gap in Non-Routine Analytical Results",
        "improvement_suggestion": "Consider adding 'Deviation:' prefix and specifying the affected process more clearly.",
        "score": 7
    }


@pytest.fixture
def sample_grading_results():
    """Sample grading results for all sections"""
    return [
        {
            "section_label": "Title",
            "text": "QA Oversight Gap in Non-Routine Analytical Results",
            "improvement_suggestion": "Consider adding 'Deviation:' prefix.",
            "score": 7
        },
        {
            "section_label": "Description",
            "text": "On 01Nov2023 during periodic review...",
            "improvement_suggestion": "Good description, consider adding more context.",
            "score": 8
        },
        {
            "section_label": "Immediate Steps Taken",
            "text": "Cleaning representatives were notified...",
            "improvement_suggestion": "List actions in chronological order.",
            "score": 6
        },
        {
            "section_label": "Quality Risk Evaluation",
            "text": "Preliminary risk assessment...",
            "improvement_suggestion": "Include specific risk levels.",
            "score": 7
        },
        {
            "section_label": "Investigation Details",
            "text": "Investigation discovered discrepancy...",
            "improvement_suggestion": "Add timeline and evidence details.",
            "score": 6
        },
        {
            "section_label": "CAPA Plan",
            "text": "1) Harmonize approval requirements...",
            "improvement_suggestion": "Add ownership and target dates.",
            "score": 7
        },
        {
            "section_label": "Recurrence Check Details",
            "text": "Retrospective review of last 12 months...",
            "improvement_suggestion": "Specify sample size and criteria.",
            "score": 6
        },
        {
            "section_label": "Effectiveness Check Plan",
            "text": "Effectiveness measured by zero recurrences...",
            "improvement_suggestion": "Define specific metrics and timeline.",
            "score": 7
        }
    ]


@pytest.fixture
def sample_prompt_template():
    """Sample prompt template"""
    return """Grade the following field:

Field Name: {{field_name}}
Content: {{field}}
Requirements: {{req}}

Provide a grade from 1-10 and explanation."""


@pytest.fixture
def mock_db_secret():
    """Mock database secret"""
    return {
        "host": "test-db.amazonaws.com",
        "port": 5432,
        "dbname": "testdb",
        "username": "testuser",
        "password": "testpass"
    }


# ============================================================================
# TEST: get_deviation_info
# ============================================================================

class TestGetDeviationInfo:
    """Tests for get_deviation_info function"""

    @patch('start_grading_lambda.get_secret')
    @patch('start_grading_lambda.psycopg.connect')
    def test_get_deviation_info_success(self, mock_connect, mock_get_secret, sample_deviation_data, mock_db_secret):
        """Test successful deviation info retrieval"""
        # Setup
        mock_get_secret.return_value = mock_db_secret
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = sample_deviation_data
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Execute
        result = lambda_function.get_deviation_info('DV-00001')

        # Assert
        assert result['deviation_id'] == 'DV-00001'
        assert result['title'] == 'QA Oversight Gap in Non-Routine Analytical Results'
        assert len(result) == 9  # 9 fields total
        mock_cursor.execute.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('start_grading_lambda.get_secret')
    @patch('start_grading_lambda.psycopg.connect')
    def test_get_deviation_info_not_found(self, mock_connect, mock_get_secret, mock_db_secret):
        """Test deviation not found in database"""
        # Setup
        mock_get_secret.return_value = mock_db_secret
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Execute & Assert
        with pytest.raises(ValueError, match="Deviation DV-99999 not found"):
            lambda_function.get_deviation_info('DV-99999')

        mock_conn.close.assert_called_once()

    @patch('start_grading_lambda.get_secret')
    @patch('start_grading_lambda.psycopg.connect')
    def test_get_deviation_info_handles_null_values(self, mock_connect, mock_get_secret, mock_db_secret):
        """Test handling of NULL values in database"""
        # Setup
        mock_get_secret.return_value = mock_db_secret
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            'deviation_id': 'DV-00002',
            'title': 'Test Deviation',
            'description': None,
            'immediate_steps_taken': None,
            'quality_risk_evaluation': None,
            'investigation_summary': None,
            'capa_plan': None,
            'recurrence_check_details': None,
            'effectiveness_check_plan': None
        }
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Execute
        result = lambda_function.get_deviation_info('DV-00002')

        # Assert - NULL values should be converted to empty strings
        assert result['description'] == ''
        assert result['immediate_steps_taken'] == ''
        assert result['quality_risk_evaluation'] == ''


    @patch('start_grading_lambda.get_secret')
    @patch('start_grading_lambda.psycopg.connect')
    def test_get_deviation_info_database_error(self, mock_connect, mock_get_secret, mock_db_secret):
        """Test database connection error"""
        # Setup
        mock_get_secret.return_value = mock_db_secret
        mock_connect.side_effect = Exception("Database connection failed")

        # Execute & Assert
        with pytest.raises(Exception, match="Database connection failed"):
            lambda_function.get_deviation_info('DV-00001')


# ============================================================================
# TEST: load_prompt
# ============================================================================

class TestLoadPrompt:
    """Tests for load_prompt function"""

    def test_load_prompt_success(self, sample_prompt_template):
        """Test successful prompt loading"""
        # Setup
        mock_file = mock_open(read_data=sample_prompt_template)
        
        with patch('builtins.open', mock_file):
            with patch('os.path.exists', return_value=True):
                # Execute
                result = lambda_function.load_prompt('field_grading.txt')

                # Assert
                assert 'Grade the following field' in result
                assert '{{field_name}}' in result

    def test_load_prompt_file_not_found(self):
        """Test prompt file not found"""
        # Setup
        with patch('os.path.exists', return_value=False):
            # Execute & Assert
            with pytest.raises(FileNotFoundError, match="Prompt file.*not found"):
                lambda_function.load_prompt('nonexistent.txt')

    def test_load_prompt_read_error(self):
        """Test error reading prompt file"""
        # Setup
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', side_effect=IOError("Read error")):
                # Execute & Assert
                with pytest.raises(IOError):
                    lambda_function.load_prompt('field_grading.txt')


# ============================================================================
# TEST: call_bedrock
# ============================================================================

class TestCallBedrock:
    """Tests for call_bedrock function"""

    @patch('start_grading_lambda.bedrock_client')
    def test_call_bedrock_success(self, mock_bedrock):
        """Test successful Bedrock API call"""
        # Setup
        mock_response = {
            'output': {
                'message': {
                    'content': [
                        {'text': '  {"grade": 7, "grade_explanation": "Good work"}  '}
                    ]
                }
            }
        }
        mock_bedrock.converse.return_value = mock_response

        # Execute
        result = lambda_function.call_bedrock("Test prompt")

        # Assert
        assert result == '{"grade": 7, "grade_explanation": "Good work"}'
        mock_bedrock.converse.assert_called_once()
        call_args = mock_bedrock.converse.call_args
        assert call_args[1]['inferenceConfig']['temperature'] == 0
        assert call_args[1]['inferenceConfig']['maxTokens'] == 2048


    @patch('start_grading_lambda.bedrock_client')
    def test_call_bedrock_api_error(self, mock_bedrock):
        """Test Bedrock API error"""
        # Setup
        mock_bedrock.converse.side_effect = Exception("API Error")

        # Execute & Assert
        with pytest.raises(Exception, match="API Error"):
            lambda_function.call_bedrock("Test prompt")


# ============================================================================
# TEST: get_section_requirements
# ============================================================================

class TestGetSectionRequirements:
    """Tests for get_section_requirements function"""

    def test_get_section_requirements_title(self):
        """Test getting requirements for Title section"""
        # Execute
        result = lambda_function.get_section_requirements("Title")

        # Assert
        assert "Clearly state the type of deviation" in result
        assert "concise and specific" in result

    def test_get_section_requirements_description(self):
        """Test getting requirements for Description section"""
        # Execute
        result = lambda_function.get_section_requirements("Description")

        # Assert
        assert "clear context" in result
        assert "when and where" in result

    def test_get_section_requirements_capa(self):
        """Test getting requirements for CAPA Plan section"""
        # Execute
        result = lambda_function.get_section_requirements("CAPA Plan")

        # Assert
        assert "corrective actions" in result
        assert "preventive actions" in result

    def test_get_section_requirements_unknown(self):
        """Test getting requirements for unknown section"""
        # Execute
        result = lambda_function.get_section_requirements("Unknown Section")

        # Assert
        assert "No specific requirements defined" in result


# ============================================================================
# TEST: grade_single_section
# ============================================================================

class TestGradeSingleSection:
    """Tests for grade_single_section function"""

    @patch('start_grading_lambda.call_bedrock')
    @patch('start_grading_lambda.load_prompt')
    def test_grade_single_section_success(self, mock_load_prompt, mock_call_bedrock, sample_prompt_template):
        """Test successful section grading"""
        # Setup
        mock_load_prompt.return_value = sample_prompt_template
        mock_call_bedrock.return_value = json.dumps({
            "grade": 7,
            "grade_explanation": "Good title but could be more specific."
        })

        # Execute
        result = lambda_function.grade_single_section(
            "Title",
            "QA Oversight Gap",
            "Requirements for title..."
        )

        # Assert
        assert result['section_label'] == 'Title'
        assert result['text'] == 'QA Oversight Gap'
        assert result['improvement_suggestion'] == 'Good title but could be more specific.'
        assert result['score'] == 7


    @patch('start_grading_lambda.call_bedrock')
    @patch('start_grading_lambda.load_prompt')
    def test_grade_single_section_invalid_json(self, mock_load_prompt, mock_call_bedrock, sample_prompt_template):
        """Test handling of invalid JSON response"""
        # Setup
        mock_load_prompt.return_value = sample_prompt_template
        mock_call_bedrock.return_value = "This is not valid JSON"

        # Execute
        result = lambda_function.grade_single_section("Title", "Test content", "Requirements")

        # Assert - should return default values
        assert result['section_label'] == 'Title'
        assert result['text'] == 'Test content'
        assert 'Unable to parse grading response' in result['improvement_suggestion']
        assert result['score'] == 0

    @patch('start_grading_lambda.call_bedrock')
    @patch('start_grading_lambda.load_prompt')
    def test_grade_single_section_bedrock_error(self, mock_load_prompt, mock_call_bedrock, sample_prompt_template):
        """Test handling of Bedrock API error"""
        # Setup
        mock_load_prompt.return_value = sample_prompt_template
        mock_call_bedrock.side_effect = Exception("Bedrock API failed")

        # Execute
        result = lambda_function.grade_single_section("Title", "Test content", "Requirements")

        # Assert - should return default values
        assert result['section_label'] == 'Title'
        assert result['text'] == 'Test content'
        assert 'Unable to grade this section' in result['improvement_suggestion']
        assert result['score'] == 0


# ============================================================================
# TEST: grade_all_sections
# ============================================================================

class TestGradeAllSections:
    """Tests for grade_all_sections function"""

    @patch('start_grading_lambda.grade_single_section')
    @patch('start_grading_lambda.get_section_requirements')
    def test_grade_all_sections_success(self, mock_get_requirements, mock_grade_section, 
                                       sample_deviation_data, sample_grading_result):
        """Test successful grading of all sections"""
        # Setup
        mock_get_requirements.return_value = "Requirements text"
        mock_grade_section.return_value = sample_grading_result

        # Execute
        result = lambda_function.grade_all_sections(sample_deviation_data)

        # Assert
        assert len(result) == 8  # 8 sections
        assert mock_grade_section.call_count == 8
        assert all(isinstance(r, dict) for r in result)

    @patch('start_grading_lambda.get_section_requirements')
    def test_grade_all_sections_empty_content(self, mock_get_requirements, sample_deviation_data):
        """Test handling of empty section content"""
        # Setup
        mock_get_requirements.return_value = "Requirements text"
        empty_deviation = sample_deviation_data.copy()
        empty_deviation['title'] = ''
        empty_deviation['description'] = '   '  # Whitespace only

        # Execute
        result = lambda_function.grade_all_sections(empty_deviation)

        # Assert
        assert len(result) == 8
        # First two sections should have score 0 and empty message
        assert result[0]['score'] == 0
        assert 'empty' in result[0]['improvement_suggestion'].lower()
        assert result[1]['score'] == 0
        assert 'empty' in result[1]['improvement_suggestion'].lower()


# ============================================================================
# TEST: save_grading_results
# ============================================================================

class TestSaveGradingResults:
    """Tests for save_grading_results function"""

    @patch('start_grading_lambda.get_secret')
    @patch('start_grading_lambda.psycopg.connect')
    def test_save_grading_results_insert_new(self, mock_connect, mock_get_secret, 
                                            sample_grading_results, mock_db_secret):
        """Test inserting new grading results"""
        # Setup
        mock_get_secret.return_value = mock_db_secret
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None  # No existing record
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Execute
        lambda_function.save_grading_results('DV-00001', sample_grading_results, is_regeneration=False)

        # Assert
        assert mock_cursor.execute.call_count == 2  # SELECT + INSERT
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('start_grading_lambda.get_secret')
    @patch('start_grading_lambda.psycopg.connect')
    def test_save_grading_results_update_existing(self, mock_connect, mock_get_secret, 
                                                  sample_grading_results, mock_db_secret):
        """Test updating existing grading results (regeneration)"""
        # Setup
        mock_get_secret.return_value = mock_db_secret
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1  # UPDATE affected 1 row
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Execute
        lambda_function.save_grading_results('DV-00001', sample_grading_results, is_regeneration=True)

        # Assert
        mock_cursor.execute.assert_called_once()  # UPDATE only
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('start_grading_lambda.get_secret')
    @patch('start_grading_lambda.psycopg.connect')
    def test_save_grading_results_update_not_found_fallback(self, mock_connect, mock_get_secret, 
                                                            sample_grading_results, mock_db_secret):
        """Test UPDATE with no rows affected falls back to INSERT"""
        # Setup
        mock_get_secret.return_value = mock_db_secret
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 0  # UPDATE affected 0 rows
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Execute
        lambda_function.save_grading_results('DV-00001', sample_grading_results, is_regeneration=True)

        # Assert
        assert mock_cursor.execute.call_count == 2  # UPDATE + INSERT
        mock_conn.commit.assert_called_once()

    @patch('start_grading_lambda.get_secret')
    @patch('start_grading_lambda.psycopg.connect')
    def test_save_grading_results_database_error(self, mock_connect, mock_get_secret, 
                                                 sample_grading_results, mock_db_secret):
        """Test database error during save"""
        # Setup
        mock_get_secret.return_value = mock_db_secret
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("Database error")
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Execute & Assert
        with pytest.raises(Exception, match="Database error"):
            lambda_function.save_grading_results('DV-00001', sample_grading_results, is_regeneration=False)

        mock_conn.rollback.assert_called_once()
        mock_conn.close.assert_called_once()


# ============================================================================
# TEST: lambda_handler
# ============================================================================

class TestLambdaHandler:
    """Tests for lambda_handler function"""

    @patch('start_grading_lambda.save_grading_results')
    @patch('start_grading_lambda.grade_all_sections')
    @patch('start_grading_lambda.get_deviation_info')
    def test_lambda_handler_success_initial_grading(self, mock_get_deviation, mock_grade_all, 
                                                    mock_save_results, sample_deviation_data, 
                                                    sample_grading_results):
        """Test successful initial grading (no existing_results)"""
        # Setup
        mock_get_deviation.return_value = sample_deviation_data
        mock_grade_all.return_value = sample_grading_results
        
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({'deviation_id': 'DV-00001'})
        }

        # Execute
        result = lambda_function.lambda_handler(event, None)

        # Assert
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
        assert 'Grading completed successfully' in body['message']
        assert isinstance(body['data'], list)
        assert len(body['data']) == 8
        mock_get_deviation.assert_called_once_with('DV-00001')
        mock_grade_all.assert_called_once()
        mock_save_results.assert_called_once_with('DV-00001', sample_grading_results, False)

    @patch('start_grading_lambda.save_grading_results')
    @patch('start_grading_lambda.grade_all_sections')
    def test_lambda_handler_success_regeneration(self, mock_grade_all, mock_save_results, 
                                                 sample_grading_results):
        """Test successful regeneration (with existing_results)"""
        # Setup
        mock_grade_all.return_value = sample_grading_results
        
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({
                'deviation_id': 'DV-00001',
                'existing_results': sample_grading_results
            })
        }

        # Execute
        result = lambda_function.lambda_handler(event, None)

        # Assert
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
        assert 'regenerated successfully' in body['message']
        mock_grade_all.assert_called_once()
        mock_save_results.assert_called_once_with('DV-00001', sample_grading_results, True)

    def test_lambda_handler_options_request(self):
        """Test CORS preflight OPTIONS request"""
        # Setup
        event = {'httpMethod': 'OPTIONS'}

        # Execute
        result = lambda_function.lambda_handler(event, None)

        # Assert
        assert result['statusCode'] == 200
        assert 'Access-Control-Allow-Origin' in result['headers']

    def test_lambda_handler_invalid_method(self):
        """Test invalid HTTP method"""
        # Setup
        event = {'httpMethod': 'GET'}

        # Execute
        result = lambda_function.lambda_handler(event, None)

        # Assert
        assert result['statusCode'] == 405
        body = json.loads(result['body'])
        assert 'Method not allowed' in body['message']

    def test_lambda_handler_missing_deviation_id(self):
        """Test missing deviation_id in request"""
        # Setup
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({})
        }

        # Execute
        result = lambda_function.lambda_handler(event, None)

        # Assert
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert 'deviation_id is required' in body['message']


    def test_lambda_handler_invalid_deviation_id_type(self):
        """Test invalid deviation_id type"""
        # Setup
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({'deviation_id': 123})
        }

        # Execute
        result = lambda_function.lambda_handler(event, None)

        # Assert
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert 'deviation_id must be a string' in body['message']

    def test_lambda_handler_empty_deviation_id(self):
        """Test empty deviation_id"""
        # Setup
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({'deviation_id': '   '})
        }

        # Execute
        result = lambda_function.lambda_handler(event, None)

        # Assert
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert 'deviation_id cannot be empty' in body['message']

    def test_lambda_handler_invalid_existing_results_type(self):
        """Test invalid existing_results type"""
        # Setup
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({
                'deviation_id': 'DV-00001',
                'existing_results': 'not an array'
            })
        }

        # Execute
        result = lambda_function.lambda_handler(event, None)

        # Assert
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert 'existing_results must be an array' in body['message']

    @patch('start_grading_lambda.get_deviation_info')
    def test_lambda_handler_deviation_not_found(self, mock_get_deviation):
        """Test deviation not found in database"""
        # Setup
        mock_get_deviation.side_effect = ValueError("Deviation DV-99999 not found in database")
        
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({'deviation_id': 'DV-99999'})
        }

        # Execute
        result = lambda_function.lambda_handler(event, None)

        # Assert
        assert result['statusCode'] == 404
        body = json.loads(result['body'])
        assert 'not found' in body['message']

    @patch('start_grading_lambda.get_deviation_info')
    def test_lambda_handler_database_error(self, mock_get_deviation):
        """Test database error"""
        # Setup
        mock_get_deviation.side_effect = Exception("Database connection failed")
        
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({'deviation_id': 'DV-00001'})
        }

        # Execute
        result = lambda_function.lambda_handler(event, None)

        # Assert
        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert 'Error fetching deviation information' in body['message']

    @patch('start_grading_lambda.grade_all_sections')
    @patch('start_grading_lambda.get_deviation_info')
    def test_lambda_handler_grading_error(self, mock_get_deviation, mock_grade_all, 
                                         sample_deviation_data):
        """Test error during grading"""
        # Setup
        mock_get_deviation.return_value = sample_deviation_data
        mock_grade_all.side_effect = Exception("Grading failed")
        
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({'deviation_id': 'DV-00001'})
        }

        # Execute
        result = lambda_function.lambda_handler(event, None)

        # Assert
        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert 'Error grading deviation sections' in body['message']


    @patch('start_grading_lambda.save_grading_results')
    @patch('start_grading_lambda.grade_all_sections')
    @patch('start_grading_lambda.get_deviation_info')
    def test_lambda_handler_save_error_continues(self, mock_get_deviation, mock_grade_all, 
                                                 mock_save_results, sample_deviation_data, 
                                                 sample_grading_results):
        """Test that save error doesn't fail the request"""
        # Setup
        mock_get_deviation.return_value = sample_deviation_data
        mock_grade_all.return_value = sample_grading_results
        mock_save_results.side_effect = Exception("Save failed")
        
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({'deviation_id': 'DV-00001'})
        }

        # Execute
        result = lambda_function.lambda_handler(event, None)

        # Assert - should still return 200 with grading results
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
        assert len(body['data']) == 8


# ============================================================================
# TEST: Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflow"""

    @patch('start_grading_lambda.save_grading_results')
    @patch('start_grading_lambda.bedrock_client')
    @patch('start_grading_lambda.get_secret')
    @patch('start_grading_lambda.psycopg.connect')
    def test_end_to_end_initial_grading(self, mock_connect, mock_get_secret, mock_bedrock,
                                       mock_save_results, sample_deviation_data, 
                                       mock_db_secret, sample_prompt_template):
        """Test complete end-to-end initial grading"""
        # Setup database
        mock_get_secret.return_value = mock_db_secret
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = sample_deviation_data
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Setup Bedrock
        mock_bedrock.converse.return_value = {
            'output': {
                'message': {
                    'content': [{'text': json.dumps({
                        "grade": 7,
                        "grade_explanation": "Good work, consider improvements."
                    })}]
                }
            }
        }

        # Setup prompt loading
        mock_file = mock_open(read_data=sample_prompt_template)
        
        with patch('builtins.open', mock_file):
            with patch('os.path.exists', return_value=True):
                # Execute
                event = {
                    'httpMethod': 'POST',
                    'body': json.dumps({'deviation_id': 'DV-00001'})
                }
                result = lambda_function.lambda_handler(event, None)

        # Assert
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
        assert len(body['data']) == 8
        assert all('section_label' in item for item in body['data'])
        assert all('score' in item for item in body['data'])
        mock_save_results.assert_called_once()

    @patch('start_grading_lambda.save_grading_results')
    @patch('start_grading_lambda.grade_all_sections')
    def test_logging_statistics(self, mock_grade_all, mock_save_results, 
                                sample_grading_results, caplog):
        """Test that proper logging occurs"""
        # Setup
        mock_grade_all.return_value = sample_grading_results
        
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({
                'deviation_id': 'DV-00001',
                'existing_results': sample_grading_results
            })
        }

        # Execute
        with caplog.at_level('INFO'):
            lambda_function.lambda_handler(event, None)

        # Assert - check that important log messages are present
        log_messages = [record.message for record in caplog.records]
        assert any('DV-00001' in msg for msg in log_messages)
        assert any('Grading' in msg and 'successfully' in msg for msg in log_messages)
        assert any('Scores:' in msg for msg in log_messages)



# ============================================================================
# TEST: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions"""

    @patch('start_grading_lambda.grade_single_section')
    @patch('start_grading_lambda.get_section_requirements')
    def test_all_empty_sections(self, mock_get_requirements, mock_grade_section):
        """Test grading with all empty sections"""
        # Setup
        mock_get_requirements.return_value = "Requirements"
        empty_deviation = {
            'deviation_id': 'DV-00003',
            'title': '',
            'description': '',
            'immediate_steps_taken': '',
            'quality_risk_evaluation': '',
            'investigation_summary': '',
            'capa_plan': '',
            'recurrence_check_details': '',
            'effectiveness_check_plan': ''
        }

        # Execute
        result = lambda_function.grade_all_sections(empty_deviation)

        # Assert
        assert len(result) == 8
        assert all(r['score'] == 0 for r in result)
        assert all('empty' in r['improvement_suggestion'].lower() for r in result)
        # grade_single_section should not be called for empty sections
        mock_grade_section.assert_not_called()

    @patch('start_grading_lambda.call_bedrock')
    @patch('start_grading_lambda.load_prompt')
    def test_very_long_content(self, mock_load_prompt, mock_call_bedrock, sample_prompt_template):
        """Test grading very long content"""
        # Setup
        mock_load_prompt.return_value = sample_prompt_template
        mock_call_bedrock.return_value = json.dumps({
            "grade": 5,
            "grade_explanation": "Content is too verbose."
        })
        
        long_content = "A" * 10000  # 10k characters

        # Execute
        result = lambda_function.grade_single_section("Title", long_content, "Requirements")

        # Assert
        assert result['score'] == 5
        assert result['text'] == long_content
        mock_call_bedrock.assert_called_once()

    @patch('start_grading_lambda.call_bedrock')
    @patch('start_grading_lambda.load_prompt')
    def test_special_characters_in_content(self, mock_load_prompt, mock_call_bedrock, 
                                          sample_prompt_template):
        """Test grading content with special characters"""
        # Setup
        mock_load_prompt.return_value = sample_prompt_template
        mock_call_bedrock.return_value = json.dumps({
            "grade": 7,
            "grade_explanation": "Good content with special chars."
        })
        
        special_content = 'Test with "quotes" and \'apostrophes\' & <html> tags'

        # Execute
        result = lambda_function.grade_single_section("Title", special_content, "Requirements")

        # Assert
        assert result['score'] == 7
        assert result['text'] == special_content

    @patch('start_grading_lambda.save_grading_results')
    @patch('start_grading_lambda.grade_all_sections')
    def test_regeneration_with_partial_existing_results(self, mock_grade_all, mock_save_results):
        """Test regeneration with incomplete existing_results"""
        # Setup
        partial_results = [
            {
                "section_label": "Title",
                "text": "Some title",
                "improvement_suggestion": "Improve this",
                "score": 5
            },
            {
                "section_label": "Description",
                "text": "Some description",
                "improvement_suggestion": "Improve this too",
                "score": 6
            }
            # Missing other 6 sections
        ]
        
        mock_grade_all.return_value = partial_results
        
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({
                'deviation_id': 'DV-00001',
                'existing_results': partial_results
            })
        }

        # Execute
        result = lambda_function.lambda_handler(event, None)

        # Assert
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
        # Should still process successfully even with partial data
        mock_grade_all.assert_called_once()

    def test_invalid_json_body(self):
        """Test invalid JSON in request body"""
        # Setup
        event = {
            'httpMethod': 'POST',
            'body': 'not valid json'
        }

        # Execute
        result = lambda_function.lambda_handler(event, None)

        # Assert
        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert body['success'] is False
