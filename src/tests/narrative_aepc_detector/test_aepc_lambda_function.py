import json
import os
import sys
from unittest.mock import Mock, patch

import pytest

# Add src directory to path for importing lambda_functio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from narrative_aepc_detector import lambda_function


class TestAEPCDetectorLambda:
    """Unit tests for narrative-aepc-detector lambda_handler"""

    @patch("narrative_aepc_detector.lambda_function.list_profiles", return_value={"inferenceProfileSummaries": []})
    @patch("narrative_aepc_detector.lambda_function.bedrock_client")
    @patch("narrative_aepc_detector.lambda_function.load_prompt", return_value="Prompt base")
    def test_successful_response(self, mock_prompt, mock_bedrock, mock_profiles):
        mock_bedrock.invoke_model.return_value = {
            "body": Mock(read=lambda: json.dumps({
                "content": [{"text": "AEPC detected"}]
            }).encode("utf-8"))
        }

        event = {"body": json.dumps({"narrative": "Patient had nausea"})}
        result = lambda_function.lambda_handler(event, {})

        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert "AEPC detected" in body["result"]
        mock_profiles.assert_called_once()

    def test_missing_narrative(self):
        """Error: Missing 'narrative' in request"""
        event = {"body": json.dumps({})}
        result = lambda_function.lambda_handler(event, {})

        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert "Missing 'narrative'" in body["error"]

    @patch("narrative_aepc_detector.lambda_function.bedrock_client")
    @patch("narrative_aepc_detector.lambda_function.load_prompt", return_value="Prompt base")
    def test_error_invoke_model(self, mock_prompt, mock_client):
        """Error: Throwing exception from Bedrock client"""
        mock_client.invoke_model.side_effect = Exception("Bedrock error")

        event = {"body": json.dumps({"narrative": "Test narrative"})}
        result = lambda_function.lambda_handler(event, {})

        assert result["statusCode"] == 500
        body = json.loads(result["body"])
        assert "Bedrock error" in body["error"]

    @patch("narrative_aepc_detector.lambda_function.bedrock_client")
    @patch("narrative_aepc_detector.lambda_function.load_prompt", return_value="Prompt base")
    def test_event_without_body(self, mock_prompt, mock_client):
        """Event without 'body', narrative directly in event"""
        mock_client.invoke_model.return_value = {
            "body": Mock(read=lambda: json.dumps({
                "content": [{"text": "AEPC result"}]
            }).encode("utf-8"))
        }

        event = {"narrative": "Direct event narrative"}
        result = lambda_function.lambda_handler(event, {})

        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert "AEPC result" in body["result"]

    @patch("narrative_aepc_detector.lambda_function.bedrock_client")
    @patch("narrative_aepc_detector.lambda_function.load_prompt", return_value="Prompt base")
    def test_empty_response_from_model(self, mock_prompt, mock_client):
        """Error: Empty content array from model response"""
        mock_client.invoke_model.return_value = {
            "body": Mock(read=lambda: json.dumps({
                "content": []
            }).encode("utf-8"))
        }

        event = {"body": json.dumps({"narrative": "Empty response narrative"})}
        result = lambda_function.lambda_handler(event, {})

        assert result["statusCode"] == 500
        body = json.loads(result["body"])
        assert "error" in body

    @patch.dict(os.environ, {}, clear=True)
    def test_default_model_id(self):
        """Verify default MODEL_ID when env var not set"""
        assert lambda_function.MODEL_ID.startswith("arn:aws:bedrock")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
