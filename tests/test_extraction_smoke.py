import json
from pathlib import Path
import pytest
from unittest.mock import patch
from hcc_bclc_extractor.pipeline import process_article

FIXTURE_DIR = Path(__file__).parent / "fixtures"

@patch('hcc_bclc_extractor.extractor._bedrock_llm_call')
def test_pipeline_smoke_run(mock_bedrock_llm_call):
    """
    Tests that the main processing pipeline runs without errors on a sample text file,
    using a mocked Bedrock call.
    """
    sample_article_path = FIXTURE_DIR / "sample_article_1.txt"
    expected_json_path = FIXTURE_DIR / "sample_article_1.expected.json"

    # Configure the mock to return a valid JSON string, so the pipeline can complete
    with open(expected_json_path, "r") as f:
        mock_bedrock_llm_call.return_value = f.read()

    try:
        # We explicitly set use_mock=False to ensure the Bedrock path is taken
        result = process_article(sample_article_path, use_mock=False)
        assert result is not None, "The pipeline should return an ExtractionOutput object."
    except Exception as e:
        pytest.fail(f"The pipeline raised an unexpected exception: {e}")

    # Verify that the mock was called
    mock_bedrock_llm_call.assert_called_once()
