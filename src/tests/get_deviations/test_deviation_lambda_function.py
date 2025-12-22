import pytest
from datetime import datetime
import json
from unittest.mock import MagicMock, patch
import sys
import os

# --------------------------------------------------
# Add project root to Python path
# --------------------------------------------------
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.get_deviations.lambda_function import (
    lambda_handler,
    get_all_deviation,
    get_case_by_deviationid
)

# --------------------------------------------------
# MOCK DATA
# --------------------------------------------------

MOCK_STATS = [
    {'stat_name': 'Pending', 'stat_value': 5},
    {'stat_name': 'Processed', 'stat_value': 10},
    {'stat_name': 'Overdue', 'stat_value': 2},
    {'stat_name': 'Avg Time', 'stat_value': 48},
    {'stat_name': 'RCA Pending', 'stat_value': 3},
    {'stat_name': 'RCA Done', 'stat_value': 7},
    {'stat_name': 'Grading Pending', 'stat_value': 4},
]

MOCK_DEVIATIONS = [
    {
        'deviation_id': 'DV-001',
        'created_at': datetime.now(),
        'deviation_status': 'Pending',
        'description': 'Test deviation 1',
        'grading_approved': True,
        'rca_approved': False,
        'grading_completed': True,
        'rca_generated': True,
    }
]


# --------------------------------------------------
# FIXTURE – CORRECT CONTEXT MANAGER MOCK
# --------------------------------------------------

@pytest.fixture
def mock_db_connection():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # cursor() must act as context manager
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.__enter__.return_value = mock_cursor
    mock_cursor.__exit__.return_value = None

    mock_conn.commit = MagicMock()

    return mock_conn, mock_cursor


# --------------------------------------------------
# TEST CASES
# --------------------------------------------------

@patch("app.get_deviations.lambda_function.get_db_connection")
def test_lambda_handler_get_all(mock_get_db, mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_get_db.return_value = mock_conn

    mock_cursor.execute.return_value = None

    # ORDER IS IMPORTANT
    mock_cursor.fetchall.side_effect = [
        MOCK_STATS,  # SELECT stat_name, stat_value FROM case_stats
        MOCK_DEVIATIONS  # SELECT deviations
    ]

    mock_cursor.fetchone.return_value = {'total': 1}

    event = {'queryStringParameters': None}

    response = lambda_handler(event, None)

    assert response['statusCode'] == 200
    body = json.loads(response['body'])

    assert 'caseStats' in body
    assert 'deviations' in body
    assert 'pagination' in body
    assert body['pagination']['total_items'] == 1


@patch("app.get_deviations.lambda_function.get_db_connection")
def test_lambda_handler_get_by_id(mock_get_db, mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_get_db.return_value = mock_conn

    mock_cursor.fetchone.return_value = {
        'deviation_id': 'DV-001',
        'investigation_summary': 'Test summary',
    }

    event = {'queryStringParameters': {'deviation_id': 'DV-001'}}

    response = lambda_handler(event, None)

    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['case_id'] == 'DV-001'


def test_get_all_deviation_with_search(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection

    mock_cursor.execute.return_value = None
    mock_cursor.fetchall.side_effect = [
        MOCK_STATS,
        MOCK_DEVIATIONS
    ]
    mock_cursor.fetchone.return_value = {'total': 1}

    response = get_all_deviation(
        mock_conn,
        page=1,
        search_query='DV'
    )

    assert response['statusCode'] == 200
    body = json.loads(response['body'])

    assert len(body['deviations']) == 1
    assert body['pagination']['total_items'] == 1


def test_get_all_deviation_with_status_filter(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection

    mock_cursor.execute.return_value = None
    mock_cursor.fetchall.side_effect = [
        MOCK_STATS,
        MOCK_DEVIATIONS
    ]
    mock_cursor.fetchone.return_value = {'total': 1}

    response = get_all_deviation(
        mock_conn,
        page=1,
        status_filter='Pending'
    )

    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['pagination']['total_items'] == 1


def test_get_case_by_deviationid_found(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection

    mock_cursor.fetchone.return_value = {
        'deviation_id': 'DV-001',
        'investigation_summary': 'Test summary',
    }

    response = get_case_by_deviationid(mock_conn, 'DV-001')

    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['case_id'] == 'DV-001'


def test_get_case_by_deviationid_not_found(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection

    mock_cursor.fetchone.return_value = None

    response = get_case_by_deviationid(mock_conn, 'DV-999')

    assert response['statusCode'] == 404
    body = json.loads(response['body'])
    assert 'error' in body


@patch("app.get_deviations.lambda_function.get_db_connection")
def test_lambda_handler_error(mock_get_db):
    mock_get_db.side_effect = Exception("Test error")

    event = {'queryStringParameters': None}

    response = lambda_handler(event, None)

    assert response['statusCode'] == 500
    body = json.loads(response['body'])

    assert body['success'] is False
    assert 'error' in body
