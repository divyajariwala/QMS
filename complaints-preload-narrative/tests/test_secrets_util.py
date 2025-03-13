from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from src.secrets_util import get_secret


@patch("src.secrets_util.boto3.session.Session")
def test_get_secret_success(mock_session):
    # Mock the session and client
    mock_client = MagicMock()
    mock_session.return_value.client.return_value = mock_client

    # Define the secret to be returned
    mock_secret_value = {"SecretString": '{"username": "test_user", "password": "test_pass"}'}
    mock_client.get_secret_value.return_value = mock_secret_value

    # Call the function
    secret_name = "test/secret"
    region = "us-east-1"
    result = get_secret(secret_name, region)

    # Assertions
    assert result == {"username": "test_user", "password": "test_pass"}
    mock_client.get_secret_value.assert_called_once_with(SecretId=secret_name)


@patch("src.secrets_util.boto3.session.Session")
def test_get_secret_client_error(mock_session):
    # Mock the session and client
    mock_client = MagicMock()
    mock_session.return_value.client.return_value = mock_client

    # Set up the client to raise ClientError
    error_response = {"Error": {"Code": "ResourceNotFoundException", "Message": "Secret not found"}}
    mock_client.get_secret_value.side_effect = ClientError(error_response, "GetSecretValue")

    # Call the function and expect an exception
    secret_name = "nonexistent/secret"
    region = "us-east-1"

    with pytest.raises(ClientError) as exc_info:
        get_secret(secret_name, region)

    # Assertions
    assert exc_info.value.response["Error"]["Code"] == "ResourceNotFoundException"
    mock_client.get_secret_value.assert_called_once_with(SecretId=secret_name)


@patch("src.secrets_util.boto3.session.Session")
def test_get_secret_missing_secret_string(mock_session):
    # Mock the session and client
    mock_client = MagicMock()
    mock_session.return_value.client.return_value = mock_client

    # SecretString key is missing
    mock_secret_value = {}
    mock_client.get_secret_value.return_value = mock_secret_value

    # Call the function and expect a KeyError
    secret_name = "test/secret"
    region = "us-east-1"

    with pytest.raises(KeyError):
        get_secret(secret_name, region)
