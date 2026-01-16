from pathlib import Path
import pytest
from hcc_bclc_extractor.pipeline import process_article

FIXTURE_DIR = Path(__file__).parent / "fixtures"

def test_pipeline_smoke_run():
    """
    Tests that the main processing pipeline runs without errors on a sample text file.
    It does not check the output, only that the process completes successfully.
    """
    sample_article_path = FIXTURE_DIR / "sample_article_1.txt"

    try:
        result = process_article(sample_article_path)
        assert result is not None, "The pipeline should return an ExtractionOutput object."
    except Exception as e:
        pytest.fail(f"The pipeline raised an unexpected exception: {e}")
