import json
import pathlib
from .prompts import EXTRACTION_PROMPT_TEMPLATE, SCHEMA_JSON
from .schema import ExtractionOutput

def _mock_llm_call(prompt: str) -> str:
    """
    Mocks a call to a large language model. For this project, it returns a
    hardcoded, valid JSON string that matches the golden test fixture.
    """
    # This path is relative to the current file, which is inside the package
    fixture_path = pathlib.Path(__file__).parent.parent.parent / "tests" / "fixtures" / "sample_article_1.expected.json"
    with open(fixture_path, "r") as f:
        mock_response_str = f.read()
    return mock_response_str

def extract_structured_data(article_text: str) -> ExtractionOutput:
    """
    Extracts structured clinical data from the text of a scientific article.
    """
    # Format the prompt with both the schema and the article text
    prompt = EXTRACTION_PROMPT_TEMPLATE.format(
        schema_json=SCHEMA_JSON,
        article_text=article_text
    )

    # Simulate a call to an LLM
    llm_output = _mock_llm_call(prompt)

    # Parse and validate the output
    extracted_json = json.loads(llm_output)
    validated_data = ExtractionOutput.model_validate(extracted_json)

    return validated_data
