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
# MOCK utils
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
mock_audit_logger = Mock()
sys.modules["audit_logger"] = mock_audit_logger

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
def valid_sections():
    """Sections with executive summary content"""
    return [
        {"label": "Title", "content": "<p>Deviation Title</p>", "isEdited": False},
        {"label": "Overview", "content": "<p>Overview content</p>", "isEdited": True},
        {"label": "Immediate Actions", "content": "<ul><li>Action 1</li></ul>", "isEdited": False},
        {"label": "Quality Risk Evaluation", "content": "<ol><li>Risk 1</li></ol>", "isEdited": False},
        {"label": "Investigation Summary", "content": "<p>Investigation details</p>", "isEdited": False},
        {"label": "CAPA Plan", "content": "<ul><li>CAPA 1</li></ul>", "isEdited": False},
        {"label": "Recurrence Check", "content": "<p>Recurrence check</p>", "isEdited": False},
        {"label": "Effectiveness Check", "content": "<p>Effectiveness check</p>", "isEdited": False},
    ]


@pytest.fixture
def valid_payload(valid_sections):
    return {
        "deviation_id": "DV-001",
        "sections": valid_sections,
    }


def mock_db_context(rowcount=1):
    cur = Mock()
    cur.execute.return_value = None
    cur.rowcount = rowcount

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
def test_is_any_section_edited(valid_sections):
    result = lambda_function.is_any_section_edited(valid_sections)
    assert result == {"labels": ["Overview"]}


def test_is_any_section_edited_no_changes():
    result = lambda_function.is_any_section_edited(
        [{"label": "Title", "isEdited": False}]
    )
    assert result == {"labels": []}


def test_save_grading_audit_log_not_called_when_no_edit():
    conn = Mock()
    sections = [{"label": "Title", "isEdited": False}]

    lambda_function.save_grading_audit_log(
        conn=conn,
        sections=sections,
        deviation_id="DV-001"
    )

    mock_audit_logger.log_deviation_audit.assert_not_called()


# ==================================================================
# SAVE EXECUTIVE SUMMARY TESTS
# ==================================================================
def test_save_executive_summary_success(valid_sections):
    """Test: Successfully save executive summary with UPDATE"""
    cur = Mock()
    cur.rowcount = 1  # UPDATE succeeded
    
    lambda_function.save_executive_summary(
        cur=cur,
        deviation_id="DV-001",
        sections=valid_sections
    )
    
    # Should call execute once for UPDATE
    assert cur.execute.call_count == 1
    call_args = cur.execute.call_args[0]
    assert "UPDATE deviation_grading_executive" in call_args[0]
    assert "DV-001" in call_args[1]


def test_save_executive_summary_insert_when_no_record(valid_sections):
    """Test: INSERT when no existing record found"""
    cur = Mock()
    cur.rowcount = 0  # UPDATE found no rows, need INSERT
    
    lambda_function.save_executive_summary(
        cur=cur,
        deviation_id="DV-002",
        sections=valid_sections
    )
    
    # Should call execute twice: UPDATE then INSERT
    assert cur.execute.call_count == 2
    
    # First call is UPDATE
    update_call = cur.execute.call_args_list[0][0]
    assert "UPDATE deviation_grading_executive" in update_call[0]
    
    # Second call is INSERT
    insert_call = cur.execute.call_args_list[1][0]
    assert "INSERT INTO deviation_grading_executive" in insert_call[0]


def test_save_executive_summary_empty_sections():
    """Test: No action when sections list is empty"""
    cur = Mock()
    
    lambda_function.save_executive_summary(
        cur=cur,
        deviation_id="DV-003",
        sections=[]
    )
    
    # Should not call execute at all
    cur.execute.assert_not_called()


def test_save_executive_summary_removes_isedited_field(valid_sections):
    """Test: isEdited field is removed from saved data"""
    cur = Mock()
    cur.rowcount = 1
    
    lambda_function.save_executive_summary(
        cur=cur,
        deviation_id="DV-004",
        sections=valid_sections
    )
    
    # Get the JSON data that was passed to execute
    call_args = cur.execute.call_args[0]
    saved_json = call_args[1][0]
    saved_data = json.loads(saved_json)
    
    # Verify isEdited field is not in saved data
    for section in saved_data:
        assert "isEdited" not in section
        assert "label" in section
        assert "content" in section


# ==================================================================
# UPDATE GRADING STATUS TESTS
# ==================================================================
@patch.object(lambda_function, "get_db_credentials")
@patch.object(lambda_function, "log_deviation_workflow")
def test_update_grading_status_success(mock_workflow, mock_creds, valid_sections):
    mock_creds.return_value = {
        "host": "localhost",
        "dbname": "db",
        "username": "u",
        "password": "p",
    }

    conn_ctx, conn, cur = mock_db_context()
    lambda_function.psycopg.connect.return_value = conn_ctx

    result = lambda_function.update_grading_status(
        deviation_id="DV-001",
        sections=valid_sections
    )

    assert result["deviation_id"] == "DV-001"
    assert result["grading_completed"] is True
    # 3 calls: 2 for deviations table updates + 1 for executive_summary save
    assert cur.execute.call_count == 3
    mock_workflow.assert_called_once()


@patch.object(lambda_function, "get_db_credentials")
def test_update_grading_status_deviation_not_found(mock_creds):
    mock_creds.return_value = {
        "host": "localhost",
        "dbname": "db",
        "username": "u",
        "password": "p",
    }

    conn_ctx, conn, cur = mock_db_context(rowcount=0)
    lambda_function.psycopg.connect.return_value = conn_ctx

    with pytest.raises(ValueError):
        lambda_function.update_grading_status(
            deviation_id="DV-404",
            sections=[]
        )


def test_update_grading_status_missing_db_secret():
    """Test: Error when DB_SECRET_NAME is not configured"""
    # Temporarily set DB_SECRET_NAME to None
    original_secret = lambda_function.DB_SECRET_NAME
    lambda_function.DB_SECRET_NAME = None
    
    try:
        with pytest.raises(ValueError, match="DB_SECRET_NAME not configured"):
            lambda_function.update_grading_status(
                deviation_id="DV-001",
                sections=[]
            )
    finally:
        lambda_function.DB_SECRET_NAME = original_secret


@patch.object(lambda_function, "get_db_credentials")
@patch.object(lambda_function, "log_deviation_workflow")
@patch.object(lambda_function, "save_grading_audit_log")
def test_update_grading_status_with_audit_log(mock_audit, mock_workflow, mock_creds, valid_sections):
    """Test: Audit log is called when sections are edited"""
    mock_creds.return_value = {
        "host": "localhost",
        "dbname": "db",
        "username": "u",
        "password": "p",
    }

    conn_ctx, conn, cur = mock_db_context()
    lambda_function.psycopg.connect.return_value = conn_ctx

    result = lambda_function.update_grading_status(
        deviation_id="DV-002",
        sections=valid_sections
    )

    assert result["deviation_id"] == "DV-002"
    mock_audit.assert_called_once_with(conn, valid_sections, "DV-002")


@patch.object(lambda_function, "get_db_credentials")
@patch.object(lambda_function, "log_deviation_workflow")
@patch.object(lambda_function, "save_executive_summary")
def test_update_grading_status_saves_executive_summary(mock_save_exec, mock_workflow, mock_creds, valid_sections):
    """Test: Executive summary is always saved from sections"""
    mock_creds.return_value = {
        "host": "localhost",
        "dbname": "db",
        "username": "u",
        "password": "p",
    }

    conn_ctx, conn, cur = mock_db_context()
    lambda_function.psycopg.connect.return_value = conn_ctx

    result = lambda_function.update_grading_status(
        deviation_id="DV-003",
        sections=valid_sections
    )

    assert result["deviation_id"] == "DV-003"
    assert result["grading_completed"] is True
    
    # Verify save_executive_summary was called with sections
    mock_save_exec.assert_called_once_with(cur, "DV-003", valid_sections)


@patch.object(lambda_function, "get_db_credentials")
@patch.object(lambda_function, "log_deviation_workflow")
@patch.object(lambda_function, "save_executive_summary")
def test_update_grading_status_with_empty_sections(mock_save_exec, mock_workflow, mock_creds):
    """Test: Executive summary save is called even with empty sections (it handles empty internally)"""
    mock_creds.return_value = {
        "host": "localhost",
        "dbname": "db",
        "username": "u",
        "password": "p",
    }

    conn_ctx, conn, cur = mock_db_context()
    lambda_function.psycopg.connect.return_value = conn_ctx

    result = lambda_function.update_grading_status(
        deviation_id="DV-004",
        sections=[]
    )

    assert result["deviation_id"] == "DV-004"
    
    # Verify save_executive_summary was called (it will handle empty list internally)
    mock_save_exec.assert_called_once_with(cur, "DV-004", [])


# ==================================================================
# LAMBDA HANDLER TESTS
# ==================================================================
def test_options_request():
    result = lambda_function.lambda_handler(
        {"httpMethod": "OPTIONS"}, {}
    )
    assert result["statusCode"] == 200


def test_invalid_http_method():
    result = lambda_function.lambda_handler(
        {"httpMethod": "GET"}, {}
    )
    assert result["statusCode"] == 405


@patch.object(lambda_function, "parse_event_body")
def test_missing_deviation_id(mock_parse):
    mock_parse.return_value = {}
    result = lambda_function.lambda_handler(
        {"httpMethod": "POST"}, {}
    )
    assert result["statusCode"] == 400


@patch.object(lambda_function, "update_grading_status")
@patch.object(lambda_function, "parse_event_body")
def test_submit_grading_success(mock_parse, mock_update, valid_payload):
    mock_parse.return_value = valid_payload
    mock_update.return_value = {
        "deviation_id": "DV-001",
        "grading_completed": True,
    }

    result = lambda_function.lambda_handler(
        {"httpMethod": "POST"}, {}
    )

    assert result["statusCode"] == 200
    mock_update.assert_called_once_with(
        deviation_id="DV-001",
        sections=valid_payload["sections"]
    )


@patch.object(lambda_function, "parse_event_body")
def test_validation_error(mock_parse):
    mock_parse.side_effect = ValueError("Invalid JSON")
    result = lambda_function.lambda_handler(
        {"httpMethod": "POST"}, {}
    )
    assert result["statusCode"] == 400


@patch.object(lambda_function, "parse_event_body")
def test_unexpected_exception(mock_parse):
    mock_parse.side_effect = Exception("Boom")
    result = lambda_function.lambda_handler(
        {"httpMethod": "POST"}, {}
    )
    assert result["statusCode"] == 500