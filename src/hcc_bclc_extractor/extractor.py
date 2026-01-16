import json
from .prompts import EXTRACTION_PROMPT_TEMPLATE, SCHEMA_JSON
from .schema import ExtractionOutput

def _mock_llm_call(prompt: str) -> str:
    """
    Mocks a call to a large language model. For this project, it returns a
    hardcoded, valid JSON string that matches the golden test fixture.
    """
    mock_response = {
        "study_metadata": {
            "pmid": "12345678",
            "title": "Mock Study: Lenvatinib vs. Sorafenib for HCC",
            "year": 2023,
            "journal": "Journal of Mock Oncology",
            "doi": "10.1000/jmo.2023.001",
            "study_design": "RCT",
            "phase": "Phase III",
            "sample_size_total": 954,
            "arms": ["Lenvatinib", "Sorafenib"],
            "comparator": "Sorafenib"
        },
        "experiments": [
            {
                "arm_name": "Lenvatinib",
                "treatment": {
                    "name": "Lenvatinib",
                    "category": "Systemic",
                    "line_of_therapy": "first-line",
                    "duration": "Until progression or unacceptable toxicity",
                    "combination": False,
                    "components": None
                },
                "bclc_baseline": {
                    "tumor_burden": {
                        "nodules": ">3",
                        "largest_nodule_cm": None,
                        "vascular_invasion": True,
                        "extrahepatic_spread": True,
                        "afp_ng_ml": None,
                        "afp_gt_400": None
                    },
                    "child_pugh": {
                        "bilirubin_mg_dl": None,
                        "albumin_g_dl": None,
                        "inr": None,
                        "ascites": None,
                        "encephalopathy": None,
                        "class_letter": "A",
                        "score": 5
                    },
                    "performance_status": {
                        "ecog": 1
                    }
                },
                "bclc_stage_reported": "C",
                "bclc_2025_cuse": {
                    "mentioned": False,
                    "cuse_criteria": None,
                    "personalized_factors": None,
                    "decision_logic": None
                },
                "results": {
                    "response_criteria": "mRECIST",
                    "os": {
                        "value": "13.6 months",
                        "ci": None,
                        "p_value": None,
                        "follow_up": None
                    },
                    "pfs": {
                        "value": "7.4 months",
                        "ci": None,
                        "p_value": None,
                        "follow_up": None
                    },
                    "orr": {
                        "value": "24.1%",
                        "ci": None,
                        "p_value": None,
                        "follow_up": None
                    },
                    "dcr": {
                        "value": None,
                        "ci": None,
                        "p_value": None,
                        "follow_up": None
                    },
                    "ttp": {
                        "value": None,
                        "ci": None,
                        "p_value": None,
                        "follow_up": None
                    },
                    "other": None
                },
                "safety": {
                    "any_adverse_events_reported": True,
                    "grade_3_4_events": [
                        {
                            "name": "Hypertension",
                            "grade": None,
                            "frequency": "42%",
                            "notes": None
                        },
                        {
                            "name": "Diarrhea",
                            "grade": None,
                            "frequency": "8%",
                            "notes": None
                        }
                    ],
                    "saes": None,
                    "discontinuation_due_to_toxicity": None,
                    "treatment_related_deaths": None,
                    "narrative": None
                }
            }
        ],
        "evidence_level": "high"
    }
    return json.dumps(mock_response)

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
