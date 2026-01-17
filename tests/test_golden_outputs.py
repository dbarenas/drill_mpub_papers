import json
from pathlib import Path
from unittest.mock import patch
from hcc_bclc_extractor.pipeline import process_article

FIXTURE_DIR = Path(__file__).parent / "fixtures"

@patch('hcc_bclc_extractor.extractor._bedrock_llm_call')
def test_golden_output_from_sample_article(mock_bedrock_llm_call):
    """
    Tests that the pipeline's output for a sample article matches the
    'golden' or expected JSON output, using a mocked Bedrock call.
    """
    sample_article_path = FIXTURE_DIR / "sample_article_1.txt"
    expected_json_path = FIXTURE_DIR / "sample_article_1.expected.json"

    # Load the expected output and configure the mock to return it
    with open(expected_json_path, "r") as f:
        expected_json_str = f.read()
        expected_data = json.loads(expected_json_str)

    mock_bedrock_llm_call.return_value = expected_json_str

    # Run the pipeline; it will now use the mocked Bedrock call
    # We explicitly set use_mock=False to ensure the Bedrock path is taken
    actual_output = process_article(sample_article_path, use_mock=False)

    # Convert the Pydantic model to a dictionary for comparison
    actual_data = actual_output.model_dump()

    # Compare the actual output with the expected output
    assert actual_data == expected_data, "The pipeline's output does not match the golden fixture."

    # Verify that the mock was called
    mock_bedrock_llm_call.assert_called_once()
