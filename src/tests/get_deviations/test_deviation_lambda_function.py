# tests/get_deviations/test_deviation_lambda_function.py

import pytest
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

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
LAMBDA_PATH = os.path.join(BASE_PATH, "..", "..", "app", "get_deviations")
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
    def test_get_all_deviations_success(self, mock_get_db):
        mock_conn = Mock()
        mock_conn.commit.return_value = None
        mock_conn.close.return_value = None

        ctx, cursor = create_mock_cursor()
        mock_conn.cursor.return_value = ctx
        mock_get_db.return_value = mock_conn
        cursor.execute.return_value = None

        cursor.fetchall.side_effect = [
            [
                {"stat_name": "Pending", "stat_value": 5},
                {"stat_name": "Processed", "stat_value": 3},
                {"stat_name": "Overdue", "stat_value": 2},
                {"stat_name": "Avg Cycle Time", "stat_value": 5},
            ],
            [
                {
                    "deviation_id": "DV-001",
                    "created_at": datetime(2023, 1, 1, 10, 0),
                    "deviation_status": "Pending",
                    "description": "Test deviation",
                    "grading_approved": True,
                    "rca_approved": False,
                    "grading_completed": True,
                    "rca_generated": True,
                    "text_extracted": None,
                }
            ],
        ]
        cursor.fetchone.return_value = {"total": 10}

        result = lambda_function.lambda_handler({}, {})
        body = json.loads(result["body"])

        assert result["statusCode"] == 200
        assert body["deviationStats"]["total_deviations"] == 10
        assert len(body["deviations"]) == 1

    @patch.object(lambda_function, "get_db_connection")
    def test_get_deviations_with_status_filter(self, mock_get_db):
        mock_conn = Mock()
        mock_conn.commit.return_value = None
        mock_conn.close.return_value = None

        ctx, cursor = create_mock_cursor()
        mock_conn.cursor.return_value = ctx
        mock_get_db.return_value = mock_conn
        cursor.execute.return_value = None

        cursor.fetchall.side_effect = [
            [
                {"stat_name": "Pending", "stat_value": 5},
                {"stat_name": "Processed", "stat_value": 3},
                {"stat_name": "Overdue", "stat_value": 2},
            ],
            [
                {
                    "deviation_id": "DV-002",
                    "created_at": datetime(2023, 2, 1, 10, 0),
                    "deviation_status": "Pending",
                    "description": "Pending deviation",
                    "grading_approved": False,
                    "rca_approved": False,
                    "grading_completed": False,
                    "rca_generated": False,
                    "text_extracted": None,
                }
            ],
        ]
        cursor.fetchone.return_value = {"total": 1}

        event = {"queryStringParameters": {"status": "pending"}}
        result = lambda_function.lambda_handler(event, {})
        body = json.loads(result["body"])

        assert result["statusCode"] == 200
        assert body["deviations"][0]["status"] == "pending"

    @patch.object(lambda_function, "get_db_connection")
    def test_get_deviations_with_search(self, mock_get_db):
        mock_conn = Mock()
        mock_conn.commit.return_value = None
        mock_conn.close.return_value = None

        ctx, cursor = create_mock_cursor()
        mock_conn.cursor.return_value = ctx
        mock_get_db.return_value = mock_conn
        cursor.execute.return_value = None

        cursor.fetchall.side_effect = [
            [
                {"stat_name": "Pending", "stat_value": 5},
                {"stat_name": "Processed", "stat_value": 3},
                {"stat_name": "Overdue", "stat_value": 2},
            ],
            [
                {
                    "deviation_id": "DV-123",
                    "created_at": datetime(2023, 3, 1, 10, 0),
                    "deviation_status": "Pending",
                    "description": "Search result",
                    "grading_approved": True,
                    "rca_approved": False,
                    "grading_completed": True,
                    "rca_generated": True,
                    "text_extracted": None,
                }
            ],
        ]
        cursor.fetchone.return_value = {"total": 1}

        event = {"queryStringParameters": {"search": "123"}}
        result = lambda_function.lambda_handler(event, {})
        body = json.loads(result["body"])

        assert result["statusCode"] == 200
        assert body["deviations"][0]["deviation_id"] == "DV-123"

    @patch.object(lambda_function, "get_db_connection")
    def test_get_single_deviation_success(self, mock_get_db):
        mock_conn = Mock()
        ctx, cursor = create_mock_cursor()
        mock_conn.cursor.return_value = ctx
        mock_get_db.return_value = mock_conn

        # Mock multiple queries: deviation, rca_analysis, deviation_grading_executive
        cursor.fetchone.side_effect = [
            # First query: deviation details
            {
                "deviation_id": "DV-005",
                "investigation_summary": "Root cause analysis",
                "created_at": datetime(2023, 2, 1, 10, 0),
                "deviation_status": "pending",
                "grading_approved": True,
                "rca_approved": True,
                "grading_completed": False,
                "rca_generated": True,
            },
            # Third query: deviation_grading_executive (single row)
            {
                "title": "Test Title",
                "overview": "Test Overview",
                "immediate_actions": "Test Actions",
                "quality_risk_evaluation": "Test Risk",
                "investigation_summary": "Test Investigation",
                "capa_plan": "Test CAPA",
                "recurrence_check": "Test Recurrence",
                "effectiveness_check": "Test Effectiveness",
                "executive_summary": [
                    {"label": "Title", "content": "<p>Test Title Content</p>"},
                    {"label": "Overview", "content": "<p>Test Overview Content</p>"}
                ]
            }
        ]
        
        # Mock fetchall for rca_analysis (can have multiple rows)
        cursor.fetchall.return_value = [
            {
                "problem_category": "Equipment Issue",
                "major_root_cause_category": "Process Issue",
                "near_root_cause_category": "Human Error",
                "root_cause_category": "Training Gap",
            }
        ]

        event = {"queryStringParameters": {"deviation_id": "DV-005"}}
        result = lambda_function.lambda_handler(event, {})
        body = json.loads(result["body"])

        assert result["statusCode"] == 200
        assert body["deviation_id"] == "DV-005"
        assert "rcaData" in body
        assert "gradingData" in body
        assert "executiveSummary" in body
        assert len(body["rcaData"]) == 1
        assert body["rcaData"][0]["problem_category"] == "Equipment Issue"
        assert len(body["executiveSummary"]) == 2
        assert body["executiveSummary"][0]["label"] == "Title"

    @patch.object(lambda_function, "get_db_connection")
    def test_get_single_deviation_not_found(self, mock_get_db):
        mock_conn = Mock()
        ctx, cursor = create_mock_cursor()
        mock_conn.cursor.return_value = ctx
        mock_get_db.return_value = mock_conn

        # First query returns None (deviation not found)
        cursor.fetchone.return_value = None

        event = {"queryStringParameters": {"deviation_id": "DV-999"}}
        result = lambda_function.lambda_handler(event, {})

        assert result["statusCode"] == 404

    @patch.object(lambda_function, "get_db_connection")
    def test_get_single_deviation_with_empty_rca_data(self, mock_get_db):
        """Test: Deviation with no RCA data returns empty array"""
        mock_conn = Mock()
        ctx, cursor = create_mock_cursor()
        mock_conn.cursor.return_value = ctx
        mock_get_db.return_value = mock_conn

        cursor.fetchone.side_effect = [
            {
                "deviation_id": "DV-006",
                "investigation_summary": "Test summary",
                "created_at": datetime(2023, 2, 1, 10, 0),
                "deviation_status": "pending",
                "grading_approved": False,
                "rca_approved": False,
                "grading_completed": False,
                "rca_generated": False,
            },
            None  # No grading data
        ]
        
        cursor.fetchall.return_value = []  # No RCA data

        event = {"queryStringParameters": {"deviation_id": "DV-006"}}
        result = lambda_function.lambda_handler(event, {})
        body = json.loads(result["body"])

        assert result["statusCode"] == 200
        assert body["rcaData"] == []
        assert body["gradingData"] == []
        assert body["executiveSummary"] == []

    @patch.object(lambda_function, "get_db_connection")
    def test_get_single_deviation_with_multiple_rca_entries(self, mock_get_db):
        """Test: Deviation with multiple RCA analysis entries"""
        mock_conn = Mock()
        ctx, cursor = create_mock_cursor()
        mock_conn.cursor.return_value = ctx
        mock_get_db.return_value = mock_conn

        cursor.fetchone.side_effect = [
            {
                "deviation_id": "DV-007",
                "investigation_summary": "Multiple RCA",
                "created_at": datetime(2023, 2, 1, 10, 0),
                "deviation_status": "pending",
                "grading_approved": True,
                "rca_approved": True,
                "grading_completed": True,
                "rca_generated": True,
            },
            None  # No grading data
        ]
        
        # Multiple RCA entries
        cursor.fetchall.return_value = [
            {
                "problem_category": "Equipment Issue",
                "major_root_cause_category": "Process Issue",
                "near_root_cause_category": "Human Error",
                "root_cause_category": "Training Gap",
            },
            {
                "problem_category": "Documentation Issue",
                "major_root_cause_category": "System Issue",
                "near_root_cause_category": "Procedure Gap",
                "root_cause_category": "Missing SOP",
            }
        ]

        event = {"queryStringParameters": {"deviation_id": "DV-007"}}
        result = lambda_function.lambda_handler(event, {})
        body = json.loads(result["body"])

        assert result["statusCode"] == 200
        assert len(body["rcaData"]) == 2
        assert body["rcaData"][0]["problem_category"] == "Equipment Issue"
        assert body["rcaData"][1]["problem_category"] == "Documentation Issue"

    @patch.object(lambda_function, "get_db_connection")
    def test_lambda_handler_exception(self, mock_get_db):
        mock_get_db.side_effect = Exception("DB failure")

        result = lambda_function.lambda_handler({}, {})
        body = json.loads(result["body"])

        assert result["statusCode"] == 500
        assert body["error"] == "Internal server error"

    @patch.object(lambda_function, "get_db_connection")
    def test_get_deviations_with_pagination(self, mock_get_db):
        """Test: Pagination with page parameter"""
        mock_conn = Mock()
        mock_conn.commit.return_value = None
        mock_conn.close.return_value = None

        ctx, cursor = create_mock_cursor()
        mock_conn.cursor.return_value = ctx
        mock_get_db.return_value = mock_conn
        cursor.execute.return_value = None

        cursor.fetchall.side_effect = [
            [{"stat_name": "Pending", "stat_value": 5}],
            [
                {
                    "deviation_id": "DV-016",
                    "created_at": datetime(2023, 4, 1, 10, 0),
                    "deviation_status": "Pending",
                    "description": "Page 2 deviation",
                    "grading_approved": False,
                    "rca_approved": False,
                    "grading_completed": False,
                    "rca_generated": False,
                    "text_extracted": None,
                }
            ],
        ]
        cursor.fetchone.return_value = {"total": 20}

        event = {"queryStringParameters": {"page": "2"}}
        result = lambda_function.lambda_handler(event, {})
        body = json.loads(result["body"])

        assert result["statusCode"] == 200
        assert body["pagination"]["current_page"] == 2
        assert body["pagination"]["has_previous"] is True

    @patch.object(lambda_function, "get_db_connection")
    def test_get_deviations_with_search_and_status(self, mock_get_db):
        """Test: Search with status filter combined"""
        mock_conn = Mock()
        mock_conn.commit.return_value = None
        mock_conn.close.return_value = None

        ctx, cursor = create_mock_cursor()
        mock_conn.cursor.return_value = ctx
        mock_get_db.return_value = mock_conn
        cursor.execute.return_value = None

        cursor.fetchall.side_effect = [
            [{"stat_name": "Pending", "stat_value": 5}],
            [
                {
                    "deviation_id": "DV-200",
                    "created_at": datetime(2023, 5, 1, 10, 0),
                    "deviation_status": "Pending",
                    "description": "Combined search",
                    "grading_approved": False,
                    "rca_approved": False,
                    "grading_completed": False,
                    "rca_generated": False,
                    "text_extracted": None,
                }
            ],
        ]
        cursor.fetchone.return_value = {"total": 1}

        event = {"queryStringParameters": {"search": "200", "status": "pending"}}
        result = lambda_function.lambda_handler(event, {})
        body = json.loads(result["body"])

        assert result["statusCode"] == 200
        assert body["deviations"][0]["deviation_id"] == "DV-200"
        assert body["deviations"][0]["status"] == "pending"

    @patch.object(lambda_function, "get_db_connection")
    def test_get_single_deviation_backward_compatibility(self, mock_get_db):
        """Test: Backward compatibility when grading_details and executive_summary columns don't exist"""
        mock_conn = Mock()
        ctx, cursor = create_mock_cursor()
        mock_conn.cursor.return_value = ctx
        mock_get_db.return_value = mock_conn

        # First query: deviation details
        cursor.fetchone.side_effect = [
            {
                "deviation_id": "DV-OLD",
                "investigation_summary": "Old deviation",
                "created_at": datetime(2023, 1, 1, 10, 0),
                "deviation_status": "pending",
                "grading_approved": False,
                "rca_approved": False,
                "grading_completed": False,
                "rca_generated": False,
            },
            # Simulate column doesn't exist error, then return old format
            {
                "title": "Old Title",
                "overview": "Old Overview",
                "immediate_actions": None,
                "quality_risk_evaluation": None,
                "investigation_summary": None,
                "capa_plan": None,
                "recurrence_check": None,
                "effectiveness_check": None,
            }
        ]
        
        cursor.fetchall.return_value = []
        
        # Simulate the first execute raising an error for missing columns
        def execute_side_effect(*args, **kwargs):
            sql = args[0] if args else ""
            if "executive_summary" in sql and "grading_details" in sql:
                raise Exception("column 'executive_summary' does not exist")
        
        cursor.execute.side_effect = execute_side_effect

        event = {"queryStringParameters": {"deviation_id": "DV-OLD"}}
        result = lambda_function.lambda_handler(event, {})
        body = json.loads(result["body"])

        assert result["statusCode"] == 200
        assert body["deviation_id"] == "DV-OLD"
        # Should have backward compatible structure
        assert "gradingData" in body
        assert "executiveSummary" in body

    @patch.object(lambda_function, "get_db_connection")
    def test_get_single_deviation_with_grading_details_json(self, mock_get_db):
        """Test: Grading details as JSON string (backward compatibility)"""
        mock_conn = Mock()
        ctx, cursor = create_mock_cursor()
        mock_conn.cursor.return_value = ctx
        mock_get_db.return_value = mock_conn

        cursor.fetchone.side_effect = [
            {
                "deviation_id": "DV-JSON",
                "investigation_summary": "JSON test",
                "created_at": datetime(2023, 1, 1, 10, 0),
                "deviation_status": "pending",
                "grading_approved": True,
                "rca_approved": True,
                "grading_completed": True,
                "rca_generated": True,
            },
            {
                "title": "Test Title",
                "overview": "Test Overview",
                "immediate_actions": None,
                "quality_risk_evaluation": None,
                "investigation_summary": None,
                "capa_plan": None,
                "recurrence_check": None,
                "effectiveness_check": None,
                "executive_summary": json.dumps([{"label": "Test", "content": "Content"}]),
                "grading_details": json.dumps({
                    "Title": {"improvement_suggestion": "Improve title", "score": 8},
                    "Overview": {"improvement_suggestion": "Improve overview", "score": 7}
                })
            }
        ]
        
        cursor.fetchall.return_value = []

        event = {"queryStringParameters": {"deviation_id": "DV-JSON"}}
        result = lambda_function.lambda_handler(event, {})
        body = json.loads(result["body"])

        assert result["statusCode"] == 200
        assert len(body["gradingData"]) == 2
        assert body["gradingData"][0]["improvement_suggestion"] == "Improve title"
        assert body["gradingData"][0]["score"] == 8
        assert len(body["executiveSummary"]) == 1

    @patch.object(lambda_function, "get_db_connection")
    def test_get_all_deviations_error_handling(self, mock_get_db):
        """Test: Error handling in get_all_deviations"""
        mock_conn = Mock()
        ctx, cursor = create_mock_cursor()
        mock_conn.cursor.return_value = ctx
        mock_get_db.return_value = mock_conn
        
        # Simulate database error
        cursor.execute.side_effect = Exception("Database query failed")

        event = {"queryStringParameters": {}}
        result = lambda_function.lambda_handler(event, {})

        assert result["statusCode"] == 500
        body = json.loads(result["body"])
        assert body["success"] is False


# ==================================================================
# DB CONNECTION TEST
# ==================================================================
class TestDBConnection:

    @patch.object(lambda_function, "get_secret")  # ✅ FIX IS HERE
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
            )