"""
Unit tests for generate_executive_summary lambda function

Tests cover:
- get_deviation_info: Database queries for deviation data
- load_prompt: Loading prompt templates
- call_bedrock: AI model invocation
- generate_executive_summary: Executive summary generation
- lambda_handler: API endpoint handling
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

# Import the specific lambda_function module for generate_executive_summary
lambda_path = os.path.join(os.path.dirname(__file__), '../../app/generate_executive_summary/lambda_function.py')
spec = importlib.util.spec_from_file_location("generate_executive_summary_lambda", lambda_path)
lambda_function = importlib.util.module_from_spec(spec)
sys.modules['generate_executive_summary_lambda'] = lambda_function
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
def sample_executive_summary():
    """Sample executive summary output"""
    return [
        {
            "label": "Title",
            "content": "Deviation: QA Oversight Gap in Non-Routine Analytical Results Verification"
        },
        {
            "label": "Description",
            "content": "On 01Nov2023 during periodic review of KIN-OVR-42071 'Biotech Process Cleaning HP ALM System Operation' it was noted by the QA representative that non-routine Analytical Results verification did not have QA oversight as per procedure."
        },
        {
            "label": "Immediate Steps Taken",
            "content": "Cleaning representatives were notified and this record was raised. It was discovered upon investigation that there is a discrepancy in the approval requirements for analytical runs."
        },
        {
            "label": "Quality Risk Evaluation",
            "content": "Preliminary risk assessment indicates potential for inconsistent verification outcomes. No impact to product quality identified for batches reviewed; additional retrospective checks initiated."
        },
        {
            "label": "Investigation Details",
            "content": "It was discovered during the investigation that there is a discrepancy in approval requirements for analytical runs between KIN-OVR-42071 and KIN-OVR-41656. Process gaps were traced to oversight in procedural harmonization."
        },
        {
            "label": "CAPA Plan",
            "content": "1) Harmonize approval requirements across related procedures. 2) Update verification workflow in HP ALM. 3) Train impacted personnel. 4) Implement QA verification checkpoint for non-routine runs."
        },
        {
            "label": "Recurrence Check Details",
            "content": "Retrospective review of the last 12 months of non-routine analytical runs to confirm adherence. Monitoring dashboard to be established for quarterly checks."
        },
        {
            "label": "Effectiveness Check Plan",
            "content": "Effectiveness will be measured by zero recurrences over two consecutive quarters and audit verification of updated workflows and training completion."
        }
    ]


@pytest.fixture
def sample_prompt_template():
    """Sample prompt template"""
    return """You are an expert in creating executive summaries.

**INPUT DATA:**

Title:
{{title}}

Description:
{{description}}

Immediate Steps Taken:
{{immediate_steps_taken}}

Quality Risk Evaluation:
{{quality_risk_evaluation}}

Investigation Summary:
{{investigation_summary}}

CAPA Plan:
{{capa_plan}}

Recurrence Check Details:
{{recurrence_check_details}}

Effectiveness Check Plan:
{{effectiveness_check_plan}}

Generate the executive summary now:
"""


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

    @patch('generate_executive_summary_lambda.get_secret')
    @patch('generate_executive_summary_lambda.psycopg.connect')
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
        assert result['description'] == 'On 01Nov2023 during periodic review of KIN-OVR-42071 it was noted by QA that non-routine Analytical Results verification did not have QA oversight.'
        assert len(result) == 9  # 9 fields total
        mock_cursor.execute.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('generate_executive_summary_lambda.get_secret')
    @patch('generate_executive_summary_lambda.psycopg.connect')
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

    @patch('generate_executive_summary_lambda.get_secret')
    @patch('generate_executive_summary_lambda.psycopg.connect')
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
        assert result['investigation_summary'] == ''
        assert result['capa_plan'] == ''
        assert result['recurrence_check_details'] == ''
        assert result['effectiveness_check_plan'] == ''

    @patch('generate_executive_summary_lambda.get_secret')
    @patch('generate_executive_summary_lambda.psycopg.connect')
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
                result = lambda_function.load_prompt('executive_summary.txt')

                # Assert
                assert 'You are an expert' in result
                assert '{{title}}' in result
                assert '{{description}}' in result

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
                    lambda_function.load_prompt('executive_summary.txt')


# ============================================================================
# TEST: call_bedrock
# ============================================================================

class TestCallBedrock:
    """Tests for call_bedrock function"""

    @patch('generate_executive_summary_lambda.bedrock_client')
    def test_call_bedrock_success(self, mock_bedrock):
        """Test successful Bedrock API call"""
        # Setup
        mock_response = {
            'output': {
                'message': {
                    'content': [
                        {'text': '  [{"label": "Title", "content": "Test"}]  '}
                    ]
                }
            }
        }
        mock_bedrock.converse.return_value = mock_response

        # Execute
        result = lambda_function.call_bedrock("Test prompt")

        # Assert
        assert result == '[{"label": "Title", "content": "Test"}]'
        mock_bedrock.converse.assert_called_once()
        call_args = mock_bedrock.converse.call_args
        assert call_args[1]['messages'][0]['content'][0]['text'] == "Test prompt"
        assert call_args[1]['inferenceConfig']['temperature'] == 0
        assert call_args[1]['inferenceConfig']['maxTokens'] == 4096

    @patch('generate_executive_summary_lambda.bedrock_client')
    def test_call_bedrock_api_error(self, mock_bedrock):
        """Test Bedrock API error"""
        # Setup
        mock_bedrock.converse.side_effect = Exception("API Error")

        # Execute & Assert
        with pytest.raises(Exception, match="API Error"):
            lambda_function.call_bedrock("Test prompt")


# ============================================================================
# TEST: generate_executive_summary
# ============================================================================

class TestGenerateExecutiveSummary:
    """Tests for generate_executive_summary function"""

    @patch('generate_executive_summary_lambda.call_bedrock')
    @patch('generate_executive_summary_lambda.load_prompt')
    def test_generate_executive_summary_success(self, mock_load_prompt, mock_call_bedrock, 
                                                sample_deviation_data, sample_prompt_template, 
                                                sample_executive_summary):
        """Test successful executive summary generation"""
        # Setup
        mock_load_prompt.return_value = sample_prompt_template
        mock_call_bedrock.return_value = json.dumps(sample_executive_summary)

        # Execute
        result = lambda_function.generate_executive_summary(sample_deviation_data)

        # Assert
        assert isinstance(result, list)
        assert len(result) == 8
        assert result[0]['label'] == 'Title'
        assert result[1]['label'] == 'Description'
        assert result[2]['label'] == 'Immediate Steps Taken'
        assert result[3]['label'] == 'Quality Risk Evaluation'
        assert result[4]['label'] == 'Investigation Details'
        assert result[5]['label'] == 'CAPA Plan'
        assert result[6]['label'] == 'Recurrence Check Details'
        assert result[7]['label'] == 'Effectiveness Check Plan'
        
        # Verify all sections have content
        for section in result:
            assert 'label' in section
            assert 'content' in section
            assert len(section['content']) > 0

    @patch('generate_executive_summary_lambda.call_bedrock')
    @patch('generate_executive_summary_lambda.load_prompt')
    def test_generate_executive_summary_invalid_json(self, mock_load_prompt, mock_call_bedrock, 
                                                     sample_deviation_data, sample_prompt_template):
        """Test handling of invalid JSON response"""
        # Setup
        mock_load_prompt.return_value = sample_prompt_template
        mock_call_bedrock.return_value = "This is not valid JSON"

        # Execute & Assert
        with pytest.raises(json.JSONDecodeError):
            lambda_function.generate_executive_summary(sample_deviation_data)

    @patch('generate_executive_summary_lambda.call_bedrock')
    @patch('generate_executive_summary_lambda.load_prompt')
    def test_generate_executive_summary_invalid_format_not_list(self, mock_load_prompt, mock_call_bedrock, 
                                                                sample_deviation_data, sample_prompt_template):
        """Test handling of response that's not a list"""
        # Setup
        mock_load_prompt.return_value = sample_prompt_template
        mock_call_bedrock.return_value = json.dumps({"error": "not a list"})

        # Execute & Assert
        with pytest.raises(ValueError, match="Invalid response format: expected list"):
            lambda_function.generate_executive_summary(sample_deviation_data)

    @patch('generate_executive_summary_lambda.call_bedrock')
    @patch('generate_executive_summary_lambda.load_prompt')
    def test_generate_executive_summary_missing_fields(self, mock_load_prompt, mock_call_bedrock, 
                                                       sample_deviation_data, sample_prompt_template):
        """Test handling of sections missing label or content"""
        # Setup
        mock_load_prompt.return_value = sample_prompt_template
        invalid_response = [
            {"label": "Title"},  # Missing content
            {"content": "Some content"}  # Missing label
        ]
        mock_call_bedrock.return_value = json.dumps(invalid_response)

        # Execute & Assert
        with pytest.raises(ValueError, match="Invalid section format: missing label or content"):
            lambda_function.generate_executive_summary(sample_deviation_data)

    @patch('generate_executive_summary_lambda.call_bedrock')
    @patch('generate_executive_summary_lambda.load_prompt')
    def test_generate_executive_summary_prompt_substitution(self, mock_load_prompt, mock_call_bedrock, 
                                                            sample_deviation_data, sample_prompt_template,
                                                            sample_executive_summary):
        """Test that prompt placeholders are correctly substituted"""
        # Setup
        mock_load_prompt.return_value = sample_prompt_template
        mock_call_bedrock.return_value = json.dumps(sample_executive_summary)

        # Execute
        lambda_function.generate_executive_summary(sample_deviation_data)

        # Assert - check that call_bedrock received prompt with substituted values
        call_args = mock_call_bedrock.call_args[0][0]
        assert sample_deviation_data['title'] in call_args
        assert sample_deviation_data['description'] in call_args
        assert sample_deviation_data['immediate_steps_taken'] in call_args
        assert '{{title}}' not in call_args  # Placeholder should be replaced
        assert '{{description}}' not in call_args


# ============================================================================
# TEST: lambda_handler
# ============================================================================

class TestLambdaHandler:
    """Tests for lambda_handler function"""

    @patch('generate_executive_summary_lambda.generate_executive_summary')
    @patch('generate_executive_summary_lambda.get_deviation_info')
    def test_lambda_handler_success(self, mock_get_deviation, mock_generate_summary,
                                    sample_deviation_data, sample_executive_summary):
        """Test successful lambda handler execution"""
        # Setup
        mock_get_deviation.return_value = sample_deviation_data
        mock_generate_summary.return_value = sample_executive_summary
        
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
        assert body['message'] == 'Executive summary generated successfully'
        assert isinstance(body['data'], list)
        assert len(body['data']) == 8
        mock_get_deviation.assert_called_once_with('DV-00001')
        mock_generate_summary.assert_called_once()

    def test_lambda_handler_options_request(self):
        """Test CORS preflight OPTIONS request"""
        # Setup
        event = {'httpMethod': 'OPTIONS'}

        # Execute
        result = lambda_function.lambda_handler(event, None)

        # Assert
        assert result['statusCode'] == 200
        assert 'Access-Control-Allow-Origin' in result['headers']
        assert 'Access-Control-Allow-Methods' in result['headers']

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

    @patch('generate_executive_summary_lambda.get_deviation_info')
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

    @patch('generate_executive_summary_lambda.get_deviation_info')
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

    @patch('generate_executive_summary_lambda.generate_executive_summary')
    @patch('generate_executive_summary_lambda.get_deviation_info')
    def test_lambda_handler_generation_error(self, mock_get_deviation, mock_generate_summary,
                                            sample_deviation_data):
        """Test error during executive summary generation"""
        # Setup
        mock_get_deviation.return_value = sample_deviation_data
        mock_generate_summary.side_effect = Exception("AI generation failed")
        
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({'deviation_id': 'DV-00001'})
        }

        # Execute
        result = lambda_function.lambda_handler(event, None)

        # Assert
        assert result['statusCode'] == 500
        body = json.loads(result['body'])
        assert 'Error generating executive summary' in body['message']

    def test_lambda_handler_invalid_json_body(self):
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


# ============================================================================
# TEST: Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflow"""

    @patch('generate_executive_summary_lambda.bedrock_client')
    @patch('generate_executive_summary_lambda.get_secret')
    @patch('generate_executive_summary_lambda.psycopg.connect')
    def test_end_to_end_executive_summary_generation(self, mock_connect, mock_get_secret, 
                                                     mock_bedrock, sample_deviation_data,
                                                     sample_executive_summary, mock_db_secret,
                                                     sample_prompt_template):
        """Test complete end-to-end executive summary generation"""
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
                    'content': [{'text': json.dumps(sample_executive_summary)}]
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
        assert body['data'][0]['label'] == 'Title'
        assert 'Deviation:' in body['data'][0]['content']

    @patch('generate_executive_summary_lambda.generate_executive_summary')
    @patch('generate_executive_summary_lambda.get_deviation_info')
    def test_logging_statistics(self, mock_get_deviation, mock_generate_summary,
                                sample_deviation_data, sample_executive_summary, caplog):
        """Test that proper logging occurs"""
        # Setup
        mock_get_deviation.return_value = sample_deviation_data
        mock_generate_summary.return_value = sample_executive_summary
        
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({'deviation_id': 'DV-00001'})
        }

        # Execute
        with caplog.at_level('INFO'):
            lambda_function.lambda_handler(event, None)

        # Assert - check that important log messages are present
        log_messages = [record.message for record in caplog.records]
        assert any('DV-00001' in msg for msg in log_messages)
        assert any('Executive summary generated successfully' in msg for msg in log_messages)


# ============================================================================
# TEST: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions"""

    @patch('generate_executive_summary_lambda.call_bedrock')
    @patch('generate_executive_summary_lambda.load_prompt')
    def test_empty_deviation_fields(self, mock_load_prompt, mock_call_bedrock, sample_prompt_template):
        """Test handling of deviation with all empty fields"""
        # Setup
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
        
        mock_load_prompt.return_value = sample_prompt_template
        mock_call_bedrock.return_value = json.dumps([
            {"label": "Title", "content": "Deviation: Pending Investigation"},
            {"label": "Description", "content": "Details to be determined"},
            {"label": "Immediate Steps Taken", "content": "Under review"},
            {"label": "Quality Risk Evaluation", "content": "Assessment pending"},
            {"label": "Investigation Details", "content": "Investigation in progress"},
            {"label": "CAPA Plan", "content": "To be developed"},
            {"label": "Recurrence Check Details", "content": "To be defined"},
            {"label": "Effectiveness Check Plan", "content": "To be established"}
        ])

        # Execute
        result = lambda_function.generate_executive_summary(empty_deviation)

        # Assert
        assert len(result) == 8
        assert all('label' in section and 'content' in section for section in result)

    @patch('generate_executive_summary_lambda.call_bedrock')
    @patch('generate_executive_summary_lambda.load_prompt')
    def test_very_long_deviation_content(self, mock_load_prompt, mock_call_bedrock, 
                                        sample_prompt_template, sample_executive_summary):
        """Test handling of very long deviation content"""
        # Setup
        long_deviation = {
            'deviation_id': 'DV-00004',
            'title': 'A' * 500,
            'description': 'B' * 5000,
            'immediate_steps_taken': 'C' * 2000,
            'quality_risk_evaluation': 'D' * 2000,
            'investigation_summary': 'E' * 3000,
            'capa_plan': 'F' * 2000,
            'recurrence_check_details': 'G' * 2000,
            'effectiveness_check_plan': 'H' * 2000
        }
        
        mock_load_prompt.return_value = sample_prompt_template
        mock_call_bedrock.return_value = json.dumps(sample_executive_summary)

        # Execute
        result = lambda_function.generate_executive_summary(long_deviation)

        # Assert
        assert len(result) == 8
        # Verify that call_bedrock was called with the long content
        call_args = mock_call_bedrock.call_args[0][0]
        assert 'A' * 500 in call_args

    @patch('generate_executive_summary_lambda.call_bedrock')
    @patch('generate_executive_summary_lambda.load_prompt')
    def test_special_characters_in_content(self, mock_load_prompt, mock_call_bedrock, 
                                          sample_prompt_template, sample_executive_summary):
        """Test handling of special characters in deviation content"""
        # Setup
        special_char_deviation = {
            'deviation_id': 'DV-00005',
            'title': 'Test with "quotes" and \'apostrophes\'',
            'description': 'Contains <html> & special chars: €, £, ¥',
            'immediate_steps_taken': 'Line 1\nLine 2\tTabbed',
            'quality_risk_evaluation': 'Path: C:\\Users\\test\\file.txt',
            'investigation_summary': 'JSON: {"key": "value"}',
            'capa_plan': 'Bullet • points ◦ and symbols',
            'recurrence_check_details': 'Math: 2 + 2 = 4, 50% > 25%',
            'effectiveness_check_plan': 'Email: test@example.com'
        }
        
        mock_load_prompt.return_value = sample_prompt_template
        mock_call_bedrock.return_value = json.dumps(sample_executive_summary)

        # Execute
        result = lambda_function.generate_executive_summary(special_char_deviation)

        # Assert
        assert len(result) == 8
        assert isinstance(result, list)
