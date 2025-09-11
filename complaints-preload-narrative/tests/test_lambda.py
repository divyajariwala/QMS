import json
import os
from unittest.mock import patch

from src.lambda_function import lambda_handler


@patch("src.lambda_function.get_secret")
@patch("src.lambda_function.generate_token")
@patch("src.lambda_function.get_record")
def test_lambda_handler_success(mock_get_record, mock_generate_token, mock_get_secret):
    # Set up environment variables
    os.environ["secrets_name"] = "secret"

    # Mock the utility functions
    mock_get_secret.return_value = {"mock": "secret"}
    mock_generate_token.return_value = "mock_token"
    mock_get_record.return_value = {
        "complaintId": "123",
        "complaintNarrative": "Test narrative",
        "drugName": "Test drug",
    }

    # Define event and context
    event = {"queryStringParameters": {"recordId": "123"}}
    context = {}

    # Call the Lambda function
    response = lambda_handler(event, context)

    # Assertions
    assert response["statusCode"] == 200
    assert "complaint_id" in response["body"]
    assert "complaint_narrative" in response["body"]
    assert "drugname" in response["body"]


def test_lambda_handler_missing_env_variable():
    # Define event and context
    event = {"queryStringParameters": {"complaintId": "123"}}
    context = {}

    # Patch os.environ to simulate missing environment variable
    with patch("src.lambda_function.os.environ", {"aws_region_name": "us-east-2"}):
        response = lambda_handler(event, context)

    # Assertions
    assert response["statusCode"] == 500
    assert "Missing secrets name" in response["body"]


def test_lambda_handler_missing_complaint_id():
    # Define event and context
    event = {"queryStringParameters": {}}
    context = {}

    # Patch os.environ to provide environment variables
    with patch("src.lambda_function.os.environ", {"aws_region_name": "us-east-2", "secrets_name": "test_secret"}):
        response = lambda_handler(event, context)

    # Assertions
    assert response["statusCode"] == 400
    assert "Missing 'recordId'" in response["body"]


@patch("src.lambda_function.get_secret")
def test_lambda_handler_unexpected_exception(mock_get_secret):
    # Mock get_secret to raise an unexpected exception
    mock_get_secret.side_effect = Exception("Unexpected error")

    # Define event and context
    event = {"queryStringParameters": {"recordId": "123"}}
    context = {}

    # Patch os.environ to provide environment variables
    with patch("src.lambda_function.os.environ", {"aws_region_name": "us-east-2", "secrets_name": "test_secret"}):
        response = lambda_handler(event, context)

    # Assertions
    assert response["statusCode"] == 500
    assert "Internal Server Error" in response["body"]


@patch("src.lambda_function.get_secret")
@patch("src.lambda_function.generate_token")
@patch("src.lambda_function.get_record")
def test_lambda_handler_with_session_and_user(mock_get_record, mock_generate_token, mock_get_secret):
    # Set up environment variables
    os.environ["secrets_name"] = "secret"

    # Mock the utility functions
    mock_get_secret.return_value = {"mock": "secret"}
    mock_generate_token.return_value = "mock_token"
    mock_get_record.return_value = {
        "complaintId": "123",
        "complaintNarrative": "Test narrative",
        "drugName": "Test drug",
    }

    # Define event and context with session_id and user_name
    event = {
        "queryStringParameters": {
            "recordId": "123",
            "sessionId": "test_session",
            "userName": "test_user",
        }
    }
    context = {}

    # Call the Lambda function
    response = lambda_handler(event, context)

    # Assertions
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["complaint_id"] == "123"
    assert body["complaint_narrative"] == "Test narrative"
    assert body["drugname"] == "Test drug"
    assert body["session_id"] == "test_session"
    assert body["user_name"] == "test_user"
