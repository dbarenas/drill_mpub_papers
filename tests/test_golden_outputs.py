import json
from pathlib import Path
from hcc_bclc_extractor.pipeline import process_article

FIXTURE_DIR = Path(__file__).parent / "fixtures"

def test_golden_output_from_sample_article():
    """
    Tests that the pipeline's output for a sample article matches the
    'golden' or expected JSON output.

    This test is crucial for ensuring the consistency and accuracy of the
    extraction logic, especially when the underlying LLM or prompt changes.
    """
    sample_article_path = FIXTURE_DIR / "sample_article_1.txt"
    expected_json_path = FIXTURE_DIR / "sample_article_1.expected.json"

    # Load the expected output
    with open(expected_json_path, "r") as f:
        expected_data = json.load(f)

    # Run the pipeline to get the actual output
    actual_output = process_article(sample_article_path)

    # Convert the Pydantic model to a dictionary for comparison
    actual_data = actual_output.model_dump()

    # Compare the actual output with the expected output
    assert actual_data == expected_data, "The pipeline's output does not match the golden fixture."
