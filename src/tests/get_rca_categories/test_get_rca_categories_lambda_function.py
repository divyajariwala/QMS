# tests/get_rca_categories/test_get_rca_categories_lambda_function.py

import pytest
import json
import os
import sys
from unittest.mock import Mock, patch, mock_open

# ------------------------------------------------------------------
# IMPORT LAMBDA FUNCTION
# ------------------------------------------------------------------
BASE_PATH = os.path.dirname(__file__)
LAMBDA_PATH = os.path.join(BASE_PATH, "..", "..", "app", "get_rca_categories")
sys.path.insert(0, LAMBDA_PATH)

import importlib.util

spec = importlib.util.spec_from_file_location(
    "lambda_function",
    os.path.join(LAMBDA_PATH, "lambda_function.py"),
)
lambda_function = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lambda_function)


# ------------------------------------------------------------------
# FIXTURES
# ------------------------------------------------------------------
@pytest.fixture
def sample_rca_data():
    """Sample RCA data structure"""
    return {
        "Factors": [
            {
                "factor_name": "Company Personnel Issue",
                "ProblemCategories": [
                    {
                        "name": "Training/Personnel Qualification Issue",
                        "number": "1",
                        "definition": "Training issue definition"
                    },
                    {
                        "name": "Personnel Performance Issue",
                        "number": "2",
                        "definition": "Performance issue definition"
                    }
                ]
            },
            {
                "factor_name": "Process/Manufacturing Equipment Issue",
                "ProblemCategories": [
                    {
                        "name": "Equipment Reliability Program Issue",
                        "number": "3",
                        "definition": "Equipment issue definition"
                    }
                ]
            }
        ],
        "MajorRootCauseCategories": [
            {
                "description": "Personnel Issues",
                "number": "10",
                "properties": {
                    "details": [
                        {
                            "NearRootCauses": "Training Issue",
                            "number": "10.1",
                            "rootcauses": [
                                {
                                    "name": "Training Not Performed",
                                    "number": "10.1.1",
                                    "definition": "Training not performed definition"
                                },
                                {
                                    "name": "Training Inadequate",
                                    "number": "10.1.2",
                                    "definition": "Training inadequate definition"
                                }
                            ]
                        }
                    ]
                }
            }
        ]
    }


@pytest.fixture
def expected_processed_data():
    """Expected data after processing (without definition and number fields)"""
    return {
        "Factors": [
            {
                "factor_name": "Company Personnel Issue",
                "ProblemCategories": [
                    {"name": "Training/Personnel Qualification Issue"},
                    {"name": "Personnel Performance Issue"}
                ]
            },
            {
                "factor_name": "Process/Manufacturing Equipment Issue",
                "ProblemCategories": [
                    {"name": "Equipment Reliability Program Issue"}
                ]
            }
        ],
        "MajorRootCauseCategories": [
            {
                "description": "Personnel Issues",
                "properties": {
                    "details": [
                        {
                            "NearRootCauses": "Training Issue",
                            "rootcauses": [
                                {"name": "Training Not Performed"},
                                {"name": "Training Inadequate"}
                            ]
                        }
                    ]
                }
            }
        ]
    }


# ==================================================================
# LOAD_RCA_CATEGORIES TESTS
# ==================================================================
class TestLoadRCACategories:
    
    def test_load_rca_categories_success(self, sample_rca_data, expected_processed_data):
        """Test successful loading and processing of RCA categories"""
        json_content = json.dumps(sample_rca_data)
        
        with patch('builtins.open', mock_open(read_data=json_content)):
            with patch('os.path.exists', return_value=True):
                result = lambda_function.load_rca_categories()
        
        # Verify structure
        assert result is not None
        assert 'Factors' in result
        assert 'MajorRootCauseCategories' in result
        
        # Verify Factors
        assert len(result['Factors']) == 2
        assert result['Factors'][0]['factor_name'] == "Company Personnel Issue"
        assert len(result['Factors'][0]['ProblemCategories']) == 2
        
        # Verify definition and number are excluded
        assert 'definition' not in result['Factors'][0]['ProblemCategories'][0]
        assert 'number' not in result['Factors'][0]['ProblemCategories'][0]
        
        # Verify Major Categories
        assert len(result['MajorRootCauseCategories']) == 1
        assert result['MajorRootCauseCategories'][0]['description'] == "Personnel Issues"
        
        # Verify root causes
        details = result['MajorRootCauseCategories'][0]['properties']['details']
        assert len(details) == 1
        assert len(details[0]['rootcauses']) == 2
        
        # Verify definition and number are excluded from root causes
        assert 'definition' not in details[0]['rootcauses'][0]
        assert 'number' not in details[0]['rootcauses'][0]
    
    def test_load_rca_categories_file_not_found(self):
        """Test when RCA data file is not found"""
        with patch('os.path.exists', return_value=False):
            result = lambda_function.load_rca_categories()
        
        assert result is None
    
    def test_load_rca_categories_invalid_json(self):
        """Test when JSON file is invalid"""
        with patch('builtins.open', mock_open(read_data='invalid json')):
            with patch('os.path.exists', return_value=True):
                with pytest.raises(json.JSONDecodeError):
                    lambda_function.load_rca_categories()
    
    def test_load_rca_categories_empty_factors(self):
        """Test with empty Factors array"""
        empty_data = {
            "Factors": [],
            "MajorRootCauseCategories": []
        }
        json_content = json.dumps(empty_data)
        
        with patch('builtins.open', mock_open(read_data=json_content)):
            with patch('os.path.exists', return_value=True):
                result = lambda_function.load_rca_categories()
        
        assert result is not None
        assert len(result['Factors']) == 0
        assert len(result['MajorRootCauseCategories']) == 0
    
    def test_load_rca_categories_missing_fields(self):
        """Test with missing optional fields"""
        minimal_data = {
            "Factors": [
                {
                    "factor_name": "Test Factor",
                    "ProblemCategories": []
                }
            ],
            "MajorRootCauseCategories": [
                {
                    "description": "Test Category",
                    "properties": {
                        "details": []
                    }
                }
            ]
        }
        json_content = json.dumps(minimal_data)
        
        with patch('builtins.open', mock_open(read_data=json_content)):
            with patch('os.path.exists', return_value=True):
                result = lambda_function.load_rca_categories()
        
        assert result is not None
        assert len(result['Factors']) == 1
        assert len(result['MajorRootCauseCategories']) == 1


# ==================================================================
# LAMBDA_HANDLER TESTS
# ==================================================================
class TestLambdaHandler:
    
    def test_lambda_handler_success(self, sample_rca_data):
        """Test successful lambda handler execution"""
        json_content = json.dumps(sample_rca_data)
        
        with patch('builtins.open', mock_open(read_data=json_content)):
            with patch('os.path.exists', return_value=True):
                event = {'httpMethod': 'GET'}
                result = lambda_function.lambda_handler(event, {})
        
        body = json.loads(result['body'])
        
        assert result['statusCode'] == 200
        assert body['success'] is True
        assert 'RCA categories retrieved successfully' in body['message']
        assert 'Factors' in body['data']
        assert 'MajorRootCauseCategories' in body['data']
    
    def test_lambda_handler_options_request(self):
        """Test CORS preflight OPTIONS request"""
        event = {'httpMethod': 'OPTIONS'}
        result = lambda_function.lambda_handler(event, {})
        
        assert result['statusCode'] == 200
        assert 'Access-Control-Allow-Origin' in result['headers']
    
    def test_lambda_handler_invalid_method(self):
        """Test invalid HTTP method"""
        event = {'httpMethod': 'POST'}
        result = lambda_function.lambda_handler(event, {})
        body = json.loads(result['body'])
        
        assert result['statusCode'] == 405
        assert body['success'] is False
        assert 'Method not allowed' in body['message']
    
    def test_lambda_handler_file_not_found(self):
        """Test when RCA data file is not found"""
        with patch('os.path.exists', return_value=False):
            event = {'httpMethod': 'GET'}
            result = lambda_function.lambda_handler(event, {})
        
        body = json.loads(result['body'])
        
        assert result['statusCode'] == 500
        assert body['success'] is False
        assert 'Failed to load RCA categories' in body['message']
    
    def test_lambda_handler_exception(self):
        """Test exception handling"""
        with patch('os.path.exists', side_effect=Exception("Test error")):
            event = {'httpMethod': 'GET'}
            result = lambda_function.lambda_handler(event, {})
        
        body = json.loads(result['body'])
        
        assert result['statusCode'] == 500
        assert body['success'] is False
        assert 'Internal server error' in body['message']
    
    def test_lambda_handler_statistics_logging(self, sample_rca_data):
        """Test that statistics are calculated correctly"""
        json_content = json.dumps(sample_rca_data)
        
        with patch('builtins.open', mock_open(read_data=json_content)):
            with patch('os.path.exists', return_value=True):
                event = {'httpMethod': 'GET'}
                result = lambda_function.lambda_handler(event, {})
        
        body = json.loads(result['body'])
        
        # Verify data structure
        assert len(body['data']['Factors']) == 2
        assert len(body['data']['MajorRootCauseCategories']) == 1
        
        # Count problem categories
        total_problem_categories = sum(
            len(factor['ProblemCategories']) 
            for factor in body['data']['Factors']
        )
        assert total_problem_categories == 3  # 2 + 1
        
        # Count near causes
        total_near_causes = sum(
            len(major_cat['properties']['details'])
            for major_cat in body['data']['MajorRootCauseCategories']
        )
        assert total_near_causes == 1


# ==================================================================
# INTEGRATION TESTS
# ==================================================================
class TestIntegration:
    
    def test_end_to_end_rca_categories_retrieval(self, sample_rca_data):
        """Test complete end-to-end flow"""
        json_content = json.dumps(sample_rca_data)
        
        with patch('builtins.open', mock_open(read_data=json_content)):
            with patch('os.path.exists', return_value=True):
                event = {'httpMethod': 'GET'}
                result = lambda_function.lambda_handler(event, {})
        
        # Verify response structure
        assert result['statusCode'] == 200
        assert 'headers' in result
        assert 'body' in result
        
        # Verify CORS headers
        assert result['headers']['Access-Control-Allow-Origin'] == '*'
        
        # Verify body
        body = json.loads(result['body'])
        assert body['success'] is True
        assert 'data' in body
        assert 'timestamp' in body
        
        # Verify data structure
        data = body['data']
        assert 'Factors' in data
        assert 'MajorRootCauseCategories' in data
        
        # Verify Factors structure
        for factor in data['Factors']:
            assert 'factor_name' in factor
            assert 'ProblemCategories' in factor
            for category in factor['ProblemCategories']:
                assert 'name' in category
                assert 'definition' not in category  # Should be excluded
                assert 'number' not in category  # Should be excluded
        
        # Verify Major Categories structure
        for major_cat in data['MajorRootCauseCategories']:
            assert 'description' in major_cat
            assert 'properties' in major_cat
            assert 'details' in major_cat['properties']
            
            for detail in major_cat['properties']['details']:
                assert 'NearRootCauses' in detail
                assert 'rootcauses' in detail
                
                for root_cause in detail['rootcauses']:
                    assert 'name' in root_cause
                    assert 'definition' not in root_cause  # Should be excluded
                    assert 'number' not in root_cause  # Should be excluded
    
    def test_data_size_reduction(self, sample_rca_data):
        """Test that excluding definition and number reduces payload size"""
        json_content = json.dumps(sample_rca_data)
        
        with patch('builtins.open', mock_open(read_data=json_content)):
            with patch('os.path.exists', return_value=True):
                result = lambda_function.load_rca_categories()
        
        # Original data size
        original_size = len(json.dumps(sample_rca_data))
        
        # Processed data size
        processed_size = len(json.dumps(result))
        
        # Processed should be smaller (definition and number fields removed)
        assert processed_size < original_size
        
        # Verify specific fields are excluded
        result_str = json.dumps(result)
        assert 'definition' not in result_str
        # Note: 'number' might appear in other contexts, so we check structure instead
        
        # Verify structure is correct
        assert 'Factors' in result
        assert 'MajorRootCauseCategories' in result


# ==================================================================
# EDGE CASES
# ==================================================================
class TestEdgeCases:
    
    def test_empty_problem_categories(self):
        """Test factor with empty ProblemCategories"""
        data = {
            "Factors": [
                {
                    "factor_name": "Empty Factor",
                    "ProblemCategories": []
                }
            ],
            "MajorRootCauseCategories": []
        }
        json_content = json.dumps(data)
        
        with patch('builtins.open', mock_open(read_data=json_content)):
            with patch('os.path.exists', return_value=True):
                result = lambda_function.load_rca_categories()
        
        assert result is not None
        assert len(result['Factors']) == 1
        assert len(result['Factors'][0]['ProblemCategories']) == 0
    
    def test_empty_root_causes(self):
        """Test detail with empty rootcauses"""
        data = {
            "Factors": [],
            "MajorRootCauseCategories": [
                {
                    "description": "Test Category",
                    "properties": {
                        "details": [
                            {
                                "NearRootCauses": "Test Near Cause",
                                "rootcauses": []
                            }
                        ]
                    }
                }
            ]
        }
        json_content = json.dumps(data)
        
        with patch('builtins.open', mock_open(read_data=json_content)):
            with patch('os.path.exists', return_value=True):
                result = lambda_function.load_rca_categories()
        
        assert result is not None
        assert len(result['MajorRootCauseCategories']) == 1
        details = result['MajorRootCauseCategories'][0]['properties']['details']
        assert len(details) == 1
        assert len(details[0]['rootcauses']) == 0
    
    def test_missing_properties_key(self):
        """Test major category with missing properties key"""
        data = {
            "Factors": [],
            "MajorRootCauseCategories": [
                {
                    "description": "Test Category"
                    # Missing 'properties' key
                }
            ]
        }
        json_content = json.dumps(data)
        
        with patch('builtins.open', mock_open(read_data=json_content)):
            with patch('os.path.exists', return_value=True):
                # Should handle gracefully
                result = lambda_function.load_rca_categories()
        
        assert result is not None
        assert len(result['MajorRootCauseCategories']) == 1
        # Should have empty details
        assert result['MajorRootCauseCategories'][0]['properties']['details'] == []
