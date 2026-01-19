import pytest
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# ------------------------------------------------------------------
# MOCK DEPENDENCIES BEFORE IMPORT
# ------------------------------------------------------------------
sys.modules["psycopg"] = Mock()
sys.modules["psycopg.rows"] = Mock()
sys.modules["secrets_util"] = Mock()

# ------------------------------------------------------------------
# IMPORT LAMBDA FUNCTION
# ------------------------------------------------------------------
BASE_PATH = os.path.dirname(__file__)
LAMBDA_PATH = os.path.join(BASE_PATH, "..", "..", "app", "get_grading")
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


# ==================================================================
# LAMBDA HANDLER TESTS
# ==================================================================
class TestLambdaHandler:

    @patch.object(lambda_function, "get_db_connection")
    def test_get_grading_success(self, mock_get_db):
        mock_conn = Mock()
        mock_conn.close.return_value = None

        ctx, cursor = create_mock_cursor()
        mock_conn.cursor.return_value = ctx
        mock_get_db.return_value = mock_conn

        cursor.fetchone.return_value = {
            "deviation_id": "DV-00001",
            "title": "Deviation Title",
            "description": "Deviation description",
            "investigation_summary": "Investigation summary",
            "immediate_steps_taken": "Immediate action",
            "capa_plan": "CAPA plan",
            "quality_risk_evaluation": "Low Risk",
            "recurrence_check_details": "No recurrence",
            "effectiveness_check_plan": "Effective",
        }

        event = {
            "queryStringParameters": {
                "deviation_id": "DV-00001"
            }
        }

        result = lambda_function.lambda_handler(event, {})
        body = json.loads(result["body"])

        assert result["statusCode"] == 200
        assert "data" in body
        assert len(body["data"]) == 8
        assert body["data"][0]["label"] == "Title"

    @patch.object(lambda_function, "get_db_connection")
    def test_get_grading_not_found(self, mock_get_db):
        mock_conn = Mock()
        ctx, cursor = create_mock_cursor()
        mock_conn.cursor.return_value = ctx
        mock_get_db.return_value = mock_conn

        cursor.fetchone.return_value = None

        event = {
            "queryStringParameters": {
                "deviation_id": "DV-99999"
            }
        }

        result = lambda_function.lambda_handler(event, {})
        body = json.loads(result["body"])

        assert result["statusCode"] == 404
        assert body["error"] == "Deviation not found"

    def test_missing_deviation_id(self):
        event = {
            "queryStringParameters": {}
        }

        result = lambda_function.lambda_handler(event, {})
        body = json.loads(result["body"])

        assert result["statusCode"] == 400
        assert "Missing required query parameter" in body["error"]

    @patch.object(lambda_function, "get_db_connection")
    def test_unhandled_exception(self, mock_get_db):
        mock_get_db.side_effect = Exception("Unexpected failure")

        result = lambda_function.lambda_handler({}, {})
        body = json.loads(result["body"])

        assert result["statusCode"] == 400
    
    @patch.object(lambda_function, "get_db_connection")
    def test_database_error(self, mock_get_db):
        """Test database error handling"""
        # Import psycopg.Error from the mocked module
        psycopg_error = type('Error', (Exception,), {})
        lambda_function.psycopg.Error = psycopg_error
        
        mock_get_db.side_effect = psycopg_error("Database connection failed")
        
        event = {
            "queryStringParameters": {
                "deviation_id": "DV-00001"
            }
        }
        
        result = lambda_function.lambda_handler(event, {})
        body = json.loads(result["body"])
        
        assert result["statusCode"] == 500
        assert body["success"] is False
        assert "Database error" in body["error"]
    
    def test_missing_query_parameters(self):
        """Test when queryStringParameters is None"""
        event = {}
        
        result = lambda_function.lambda_handler(event, {})
        body = json.loads(result["body"])
        
        assert result["statusCode"] == 400
        assert "Missing required query parameter" in body["error"]
    
    @patch.object(lambda_function, "get_db_connection")
    def test_connection_closed_on_success(self, mock_get_db):
        """Test database connection is closed after successful request"""
        mock_conn = Mock()
        mock_conn.close = Mock()
        
        ctx, cursor = create_mock_cursor()
        mock_conn.cursor.return_value = ctx
        mock_get_db.return_value = mock_conn
        
        cursor.fetchone.return_value = {
            "deviation_id": "DV-00001",
            "title": "Test",
            "description": "Test",
            "investigation_summary": "Test",
            "immediate_steps_taken": "Test",
            "capa_plan": "Test",
            "quality_risk_evaluation": "Test",
            "recurrence_check_details": "Test",
            "effectiveness_check_plan": "Test",
        }
        
        event = {
            "queryStringParameters": {
                "deviation_id": "DV-00001"
            }
        }
        
        lambda_function.lambda_handler(event, {})
        
        # Verify connection was closed
        mock_conn.close.assert_called_once()
    
    @patch.object(lambda_function, "get_db_connection")
    def test_connection_closed_on_error(self, mock_get_db):
        """Test database connection is closed even when error occurs"""
        mock_conn = Mock()
        mock_conn.close = Mock()
        mock_conn.cursor.side_effect = Exception("Query failed")
        
        mock_get_db.return_value = mock_conn
        
        event = {
            "queryStringParameters": {
                "deviation_id": "DV-00001"
            }
        }
        
        lambda_function.lambda_handler(event, {})
        
        # Verify connection was closed despite error
        mock_conn.close.assert_called_once()


# ==================================================================
# DB CONNECTION TEST
# ==================================================================
class TestDBConnection:

    @patch.object(lambda_function, "get_secret")
    def test_get_db_connection_success(self, mock_get_secret):
        mock_get_secret.return_value = {
            "host": "localhost",
            "port": 5432,
            "dbname": "testdb",
            "username": "testuser",
            "password": "testpass",
        }

        with patch.object(lambda_function.psycopg, "connect") as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value = mock_conn

            conn = lambda_function.get_db_connection()

            assert conn == mock_conn
            mock_get_secret.assert_called_once()
            mock_connect.assert_called_once_with(
                host="localhost",
                port=5432,
                dbname="testdb",
                user="testuser",
                password="testpass",
                connect_timeout=5,
            )


# ==================================================================
# RESPONSE HELPERS
# ==================================================================
def test_response_helper():
    response = lambda_function._response(200, {"key": "value"})

    assert response["statusCode"] == 200
    assert json.loads(response["body"])["key"] == "value"
    assert response["headers"]["Access-Control-Allow-Origin"] == "*"


def test_cors_headers():
    headers = lambda_function._get_cors_headers()

    assert headers["Content-Type"] == "application/json"
    assert "GET" in headers["Access-Control-Allow-Methods"]