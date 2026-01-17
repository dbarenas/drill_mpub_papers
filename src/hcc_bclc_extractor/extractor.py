import json
import pathlib
import boto3
import logging
from .prompts import EXTRACTION_PROMPT_TEMPLATE, SCHEMA_JSON
from .schema import ExtractionOutput

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize the Bedrock client
try:
    bedrock_client = boto3.client(service_name="bedrock-runtime")
except Exception as e:
    logger.error("Failed to initialize Bedrock client: %s", e)
    bedrock_client = None

def _mock_llm_call(prompt: str) -> str:
    """
    Mocks a call to a large language model. For this project, it returns a
    hardcoded, valid JSON string that matches the golden test fixture.
    """
    fixture_path = pathlib.Path(__file__).parent.parent.parent / "tests" / "fixtures" / "sample_article_1.expected.json"
    with open(fixture_path, "r") as f:
        mock_response_str = f.read()
    return mock_response_str

def _bedrock_llm_call(prompt: str) -> str:
    """
    Calls the Anthropic Claude v2.1 model via AWS Bedrock.
    """
    if not bedrock_client:
        raise ConnectionError("Bedrock client is not initialized. Check AWS credentials and permissions.")

    model_id = "anthropic.claude-v2:1"
    claude_prompt = f"\n\nHuman: {prompt}\n\nAssistant:"

    body = json.dumps({
        "prompt": claude_prompt,
        "max_tokens_to_sample": 8191,
        "temperature": 0.0,
        "top_p": 1,
        "stop_sequences": ["\n\nHuman:"],
    })

    try:
        logger.info("Invoking Bedrock model %s...", model_id)
        response = bedrock_client.invoke_model(
            body=body,
            modelId=model_id,
            accept="application/json",
            contentType="application/json",
        )
        response_body = json.loads(response.get("body").read())
        completion = response_body.get("completion")

        if not completion:
            raise ValueError("Received an empty completion from the Bedrock model.")

        logger.info("Successfully received completion from Bedrock model.")
        return completion
    except Exception as e:
        logger.error("An error occurred while invoking the Bedrock model: %s", e)
        raise

def extract_structured_data(article_text: str, use_mock: bool = False) -> ExtractionOutput:
    """
    Extracts structured clinical data from the text of a scientific article.
    """
    prompt = EXTRACTION_PROMPT_TEMPLATE.format(
        schema_json=SCHEMA_JSON,
        article_text=article_text
    )

    if use_mock:
        logger.info("Using MOCK LLM call.")
        llm_output = _mock_llm_call(prompt)
    else:
        logger.info("Using Bedrock LLM call.")
        llm_output = _bedrock_llm_call(prompt)

    if "```json" in llm_output:
        json_str = llm_output.split("```json")[1].split("```")[0].strip()
    else:
        json_str = llm_output

    try:
        extracted_json = json.loads(json_str)
        validated_data = ExtractionOutput.model_validate(extracted_json)
    except json.JSONDecodeError as e:
        logger.error("Failed to decode JSON from LLM output: %s", e)
        logger.error("LLM Output that failed to parse:\n%s", json_str)
        raise
    except Exception as e:
        logger.error("Failed to validate data against Pydantic schema: %s", e)
        raise

    return validated_data
