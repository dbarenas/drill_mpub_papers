import json
from .schema import ExtractionOutput

# Generate the JSON schema from the Pydantic model and store it as a string
SCHEMA_DICT = ExtractionOutput.model_json_schema()
SCHEMA_JSON = json.dumps(SCHEMA_DICT, indent=2)

# Define the prompt as a simple multi-line string with placeholders
EXTRACTION_PROMPT_TEMPLATE = """
You are a senior clinical data extraction agent specialized in hepatocellular carcinoma (HCC),
clinical trials, and evidence-based oncology frameworks.

Your task is to analyze the FULL TEXT of a scientific article, provided below,
and extract structured experimental and clinical data focused on treatment efficacy,
safety, and outcomes.

You MUST normalize all extracted information using the BCLC (Barcelona Clinic Liver Cancer) framework.

----------------------------------
IMPORTANT RULES
----------------------------------
- If information is missing or not explicitly stated, use null.
- DO NOT infer or hallucinate values unless clearly supported by the text.
- Return ONLY a valid, machine-parseable JSON object that strictly adheres to the schema provided below. Do not include any explanatory text or markdown formatting before or after the JSON object.
- Preserve numeric units exactly as reported in the text.
- Classify the evidence level based on the study design as described in the schema.
- For each distinct treatment arm or experimental group described in the study, create a separate object in the "experiments" list.

----------------------------------
OUTPUT JSON SCHEMA
----------------------------------
{schema_json}

----------------------------------
BEGIN ARTICLE TEXT
----------------------------------
{article_text}
"""
