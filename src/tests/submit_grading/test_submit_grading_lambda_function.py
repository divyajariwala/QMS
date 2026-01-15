import pytest
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock


# ------------------------------------------------------------------
# MOCK psycopg
# ------------------------------------------------------------------
class PsycopgError(Exception):
    pass


mock_psycopg = Mock()
mock_psycopg.Error = PsycopgError
mock_psycopg.connect = Mock()

sys.modules["psycopg"] = mock_psycopg


# ------------------------------------------------------------------
# MOCK utils (CRITICAL FIX)
# ------------------------------------------------------------------
def mock_response(status_code, message, data=None):
    body = {"message": message}
    if data is not None:
        body["data"] = data

    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


mock_utils = Mock()
mock_utils.response.side_effect = mock_response
mock_utils.handle_cors_preflight.return_value = {
    "statusCode": 200,
    "headers": {"Access-Control-Allow-Origin": "*"},
}
mock_utils.parse_event_body = Mock()

sys.modules["utils"] = mock_utils

# ------------------------------------------------------------------
# MOCK secrets & audit logger
# ------------------------------------------------------------------
sys.modules["secrets_util"] = Mock()
sys.modules["audit_logger"] = Mock()

# ------------------------------------------------------------------
# IMPORT LAMBDA
# ------------------------------------------------------------------
BASE_PATH = os.path.dirname(__file__)
LAMBDA_PATH = os.path.join(BASE_PATH, "..", "..", "app", "submit_grading")
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
def valid_payload():
    return {
        "deviation_id": "DV-001",
        "created_by": "tester",
        "sections": [
            {"label": "Title", "content": "Title", "isEdited": False},
            {"label": "Overview", "content": "Overview", "isEdited": True},
            {"label": "Immediate Actions", "content": "Action", "isEdited": False},
            {"label": "Quality Risk Evaluation", "content": "Low", "isEdited": False},
            {"label": "Investigation Summary", "content": "Summary", "isEdited": False},
            {"label": "CAPA Plan", "content": "Plan", "isEdited": False},
            {"label": "Recurrence Check", "content": "No", "isEdited": False},
            {"label": "Effectiveness Check", "content": "Yes", "isEdited": False},
        ],
    }


def mock_db_context():
    cur = Mock()
    cur.execute.return_value = None

    cur_ctx = MagicMock()
    cur_ctx.__enter__.return_value = cur
    cur_ctx.__exit__.return_value = None

    conn = Mock()
    conn.cursor.return_value = cur_ctx
    conn.commit.return_value = None

    conn_ctx = MagicMock()
    conn_ctx.__enter__.return_value = conn
    conn_ctx.__exit__.return_value = None

    return conn_ctx, conn, cur


# ==================================================================
# HELPER FUNCTION TESTS
# ==================================================================
def test_normalize_grading_sections(valid_payload):
    result = lambda_function.normalize_grading_sections(valid_payload["sections"])
    assert result["title"] == "Title"
    assert result["overview"] == "Overview"


def test_is_any_section_edited(valid_payload):
    assert lambda_function.is_any_section_edited(valid_payload["sections"]) is True


# ==================================================================
# SAVE GRADING
# ==================================================================
@patch.object(lambda_function, "get_db_credentials")
@patch.object(lambda_function, "log_deviation_workflow")
def test_save_grading_success(mock_log, mock_creds, valid_payload):
    mock_creds.return_value = {
        "host": "localhost",
        "dbname": "db",
        "username": "u",
        "password": "p",
    }

    conn_ctx, conn, cur = mock_db_context()
    lambda_function.psycopg.connect.return_value = conn_ctx

    result = lambda_function.save_grading_to_database(valid_payload)

    assert result["deviation_id"] == "DV-001"
    assert result["is_edit"] is True
    assert cur.execute.call_count == 3


# ==================================================================
# LAMBDA HANDLER TESTS (FIXED)
# ==================================================================
def test_options_request():
    result = lambda_function.lambda_handler({"httpMethod": "OPTIONS"}, {})
    assert result["statusCode"] == 200


def test_invalid_http_method():
    result = lambda_function.lambda_handler({"httpMethod": "GET"}, {})
    assert result["statusCode"] == 405


@patch.object(lambda_function, "parse_event_body")
def test_missing_deviation_id(mock_parse):
    mock_parse.return_value = {"sections": []}
    result = lambda_function.lambda_handler({"httpMethod": "POST"}, {})
    assert result["statusCode"] == 400


@patch.object(lambda_function, "parse_event_body")
def test_empty_sections(mock_parse):
    mock_parse.return_value = {"deviation_id": "DV-1", "sections": []}
    result = lambda_function.lambda_handler({"httpMethod": "POST"}, {})
    assert result["statusCode"] == 400


@patch.object(lambda_function, "parse_event_body")
def test_section_missing_label(mock_parse):
    mock_parse.return_value = {
        "deviation_id": "DV-1",
        "sections": [{"content": "X"}],
    }
    result = lambda_function.lambda_handler({"httpMethod": "POST"}, {})
    assert result["statusCode"] == 400


@patch.object(lambda_function, "save_grading_to_database")
@patch.object(lambda_function, "parse_event_body")
def test_submit_grading_success(mock_parse, mock_save, valid_payload):
    mock_parse.return_value = valid_payload
    mock_save.return_value = {"deviation_id": "DV-001", "is_edit": True}

    result = lambda_function.lambda_handler({"httpMethod": "POST"}, {})
    assert result["statusCode"] == 200


@patch.object(lambda_function, "parse_event_body")
def test_validation_error(mock_parse):
    mock_parse.side_effect = ValueError("Invalid JSON")
    result = lambda_function.lambda_handler({"httpMethod": "POST"}, {})
    assert result["statusCode"] == 400


@patch.object(lambda_function, "parse_event_body")
def test_unexpected_exception(mock_parse):
    mock_parse.side_effect = Exception("Boom")
    result = lambda_function.lambda_handler({"httpMethod": "POST"}, {})
    assert result["statusCode"] == 500
