from unittest.mock import patch

import pytest
import requests

from src.utils import (
    AuthError,
    DataFetchError,
    generate_error_response,
    generate_success_response,
    generate_token,
    get_record,
)


@patch("src.utils.requests.post")
def test_generate_token_success(mock_post):
    # Simulate a successful response
    mock_response = {"access_token": "mock-token"}
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = mock_response

    secret = {
        "token_url": "https://mock-token-url.com",
        "token_client_id": "mock-client-id",
        "token_client_secret": "mock-client-secret",
        "token_scope": "mock-scope",
    }

    token = generate_token(secret)

    # Verifies that the function returns the expected token
    assert token == "mock-token"

    # Verifies if the requests.post function was called with the expected arguments
    mock_post.assert_called_once_with(
        secret["token_url"],
        data={
            "grant_type": "client_credentials",
            "client_id": secret["token_client_id"],
            "client_secret": secret["token_client_secret"],
            "scope": secret["token_scope"],
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )


@patch("src.utils.requests.post")
def test_generate_token_http_error(mock_post):
    # Simulates a 400 Bad Request response
    mock_post.return_value.status_code = 400
    mock_post.return_value.text = "Bad Request"
    mock_post.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError("HTTP Error")

    secret = {
        "token_url": "https://example.com",
        "token_client_id": "test-client-id",
        "token_client_secret": "test-client-secret",
        "token_scope": "test-scope",
    }

    # Verifies that an AuthError is raised with the expected message
    with pytest.raises(AuthError, match="HTTP Error: 400, Message: Bad Request"):
        generate_token(secret)


@patch("src.utils.requests.post")
def test_generate_token_connection_error(mock_post):
    # Simulates a connection error
    mock_post.side_effect = requests.exceptions.ConnectionError("Connection Error")

    secret = {
        "token_url": "https://example.com",
        "token_client_id": "test-client-id",
        "token_client_secret": "test-client-secret",
        "token_scope": "test-scope",
    }

    # Verifies that an AuthError is raised with the expected message
    with pytest.raises(AuthError, match="Request Error: Connection Error"):
        generate_token(secret)


@patch("src.utils.requests.post")
def test_generate_token_timeout(mock_post):
    # Simulates a timeout error
    mock_post.side_effect = requests.exceptions.Timeout("Request timed out")

    secret = {
        "token_url": "https://example.com",
        "token_client_id": "test-client-id",
        "token_client_secret": "test-client-secret",
        "token_scope": "test-scope",
    }

    # Verifies that an AuthError is raised with the expected message
    with pytest.raises(AuthError, match="Request Error: Request timed out"):
        generate_token(secret)


def test_generate_token_missing_key():
    secret = {
        "token_url": "https://example.com/token",
        "token_client_id": "test-client-id",
        # "token_client_secret": "test-client-secret",  # Clave faltante
        "token_scope": "test-scope",
    }

    with pytest.raises(KeyError, match="'token_client_secret'"):
        generate_token(secret)


def test_generate_success_response():
    data = {"key": "value"}
    response = generate_success_response(data)

    # Verifies the status code and the body content
    assert response["statusCode"] == 200
    assert "key" in response["body"]
    assert response["body"] == '{"key": "value"}'


def test_generate_error_response():
    response = generate_error_response(400, "Bad Request")

    # Verifies the status code and the body content
    assert response["statusCode"] == 400
    assert "error" in response["body"]
    assert response["body"] == '{"error": "Bad Request"}'


@patch("src.utils.requests.get")
def test_get_record_http_error(mock_get):
    mock_get.return_value.status_code = 404
    mock_get.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError("Not Found")

    secret = {
        "mqqms_ai_toolkit_eapi_url": "https://example.com/api",
        "toolkit_client_id": "test-client-id",
        "toolkit_client_secret": "test-client-secret",
    }

    with pytest.raises(DataFetchError, match="HTTP Error: Not Found"):
        get_record("12345", "mock-token", secret)


@patch("src.utils.requests.get")
def test_get_record_non_json_response(mock_get):
    # Simulate a successful response with non-JSON content
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "Not JSON"
    mock_get.return_value.json.side_effect = ValueError("Invalid JSON")  # Simula error al intentar interpretar JSON

    secret = {
        "mqqms_ai_toolkit_eapi_url": "https://example.com/api",
        "toolkit_client_id": "test-client-id",
        "toolkit_client_secret": "test-client-secret",
    }

    # Verifies that a DataFetchError is raised with the expected message
    with pytest.raises(DataFetchError, match="Request Error: Invalid JSON"):
        get_record("12345", "mock-token", secret)

    # Besure that the function was called with the expected arguments
    mock_get.assert_called_once_with(
        "https://example.com/api/classification?complaintId=12345",
        headers={
            "Authorization": "Bearer mock-token",
            "client_id": "test-client-id",
            "client_secret": "test-client-secret",
        },
        verify=False,
    )


@patch("src.utils.requests.get")
def test_get_record_request_exception(mock_get):
    # Simulate a generic RequestException
    mock_get.side_effect = requests.exceptions.RequestException("Generic Request Error")

    secret = {
        "mqqms_ai_toolkit_eapi_url": "https://example.com/api",
        "toolkit_client_id": "test-client-id",
        "toolkit_client_secret": "test-client-secret",
    }

    # Verify that a DataFetchError is raised with the correct message
    with pytest.raises(DataFetchError, match="Request Error: Generic Request Error"):
        get_record("12345", "mock-token", secret)

    # Ensure requests.get was called with the correct arguments
    mock_get.assert_called_once_with(
        "https://example.com/api/classification?complaintId=12345",
        headers={
            "Authorization": "Bearer mock-token",
            "client_id": "test-client-id",
            "client_secret": "test-client-secret",
        },
        verify=False,
    )
