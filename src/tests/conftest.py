import pytest
from unittest.mock import patch

@pytest.fixture(autouse=True)
def mock_list_profiles():
    with patch("narrative_aepc_detector.lambda_function.list_profiles", return_value={"inferenceProfileSummaries": []}):
        yield