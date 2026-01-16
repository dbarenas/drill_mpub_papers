# HCC BCLC Clinical Data Extractor

## 1. Overview

The **HCC BCLC Clinical Data Extractor** is a specialized Python-based tool designed to automate the extraction of structured clinical and experimental data from scientific articles on hepatocellular carcinoma (HCC). The agent analyzes the full text of research papers, normalizes the findings according to the **Barcelona Clinic Liver Cancer (BCLC)** framework, and outputs the data in a clean, machine-readable JSON format.

This project is built to be a robust foundation for clinical data analysis, evidence synthesis, and research. It uses a Pydantic-based schema to ensure that all extracted data is strongly typed and validated, preventing data integrity issues.

The current implementation uses a **mocked Large Language Model (LLM)** for deterministic testing, allowing the entire pipeline—from PDF text extraction to data validation—to be verified without relying on an external API.

## 2. Key Features

-   **Structured Data Extraction**: Converts unstructured text from scientific papers into a structured JSON object.
-   **BCLC Framework Alignment**: Normalizes all extracted data to the specific dimensions of the BCLC staging and treatment framework.
-   **Schema Validation**: Leverages Pydantic models to enforce a strict, validated data structure for all outputs.
-   **PDF and Text Processing**: Capable of extracting text directly from both `.pdf` and `.txt` files.
-   **Modular Architecture**: The codebase is organized into logical, decoupled modules for easy maintenance and extension.
-   **Test-Driven**: Includes a comprehensive test suite with unit, smoke, and golden-file tests to ensure reliability.
-   **Extensible**: Designed to be easily adapted to use a live LLM by replacing the mock function in the `extractor` module.

## 3. Setup and Installation

To get the project up and running, follow these steps. Python 3.11 or higher is required.

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd hcc-bclc-extractor
```

### Step 2: Install Dependencies

The project uses `pip` and `pyproject.toml` for dependency management. It is highly recommended to use a virtual environment.

```bash
# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install the package in editable mode with development dependencies
pip install -e .[dev]
```

Installing in **editable mode** (`-e`) ensures that any changes you make to the source code are immediately available without needing to reinstall the package.

## 4. Usage

An example script, `run_extraction.py`, is provided in the root directory to demonstrate how to use the data extraction pipeline.

### Running the Example

The script is configured to process a sample text file located at `tests/fixtures/sample_article_1.txt`. To run it, execute the following command from the project's root directory:

```bash
python run_extraction.py
```

### Expected Output

The script will process the article and print a formatted JSON object to the console, containing the data extracted and validated by the pipeline.

```json
Processing article: tests/fixtures/sample_article_1.txt...

Extraction Complete. Results:
----------------------------------
{
  "study_metadata": {
    "pmid": "12345678",
    // ... (full JSON output)
  },
  "experiments": [
    // ...
  ],
  "evidence_level": "high"
}
----------------------------------
```

### Processing Your Own Files

To process your own scientific article (e.g., a PDF), simply modify the `sample_file` path in `run_extraction.py`:

```python
# In run_extraction.py
# Change this path to your file
sample_file = Path("path/to/your/document.pdf")
```

## 5. Running Tests

The project includes a full test suite to ensure the code is working correctly. To run all tests, use `pytest`:

```bash
pytest
```

The tests will:
1.  Verify that the Pydantic schema can be correctly initialized.
2.  Run a "smoke test" to ensure the main pipeline executes without errors.
3.  Perform a "golden file" test to ensure the pipeline's output for a sample article exactly matches a pre-defined, expected JSON structure.

## 6. Project Structure

The project is organized into the following key modules and directories:

```
hcc-bclc-extractor/
├── pyproject.toml              # Project metadata and dependencies
├── README.md                   # This documentation file
├── run_extraction.py           # Example script for demonstrating the pipeline
├── src/
│   └── hcc_bclc_extractor/
│       ├── __init__.py
│       ├── schema.py           # Defines the Pydantic models for data validation
│       ├── pdf_text.py         # Handles text extraction from PDF files
│       ├── prompts.py          # Contains the prompt template for the LLM
│       ├── extractor.py        # Core logic for LLM interaction and data parsing
│       ├── pipeline.py         # Orchestrates the end-to-end extraction workflow
│       ├── pubmed.py           # (Placeholder) For fetching articles from PubMed
│       ├── pmc.py              # (Placeholder) For fetching articles from PMC
│       └── metrics.py          # (Placeholder) For evaluating extraction quality
└── tests/
    ├── fixtures/               # Contains sample articles and expected JSON outputs
    │   ├── sample_article_1.txt
    │   └── sample_article_1.expected.json
    ├── test_schema_validation.py # Tests for the Pydantic schema
    ├── test_extraction_smoke.py  # Smoke test for the main pipeline
    └── test_golden_outputs.py    # Golden file test for output validation
```

### Module Descriptions

-   **`schema.py`**: The heart of the project's data structure. It contains all the Pydantic models that define the shape and types of the final JSON output. `ConfigDict(extra="forbid")` is used to prevent any data that doesn't conform to the schema.
-   **`pdf_text.py`**: A utility module that uses the `PyMuPDF` (fitz) library to extract raw text content from PDF documents.
-   **`prompts.py`**: Defines the master prompt template sent to the LLM. It dynamically incorporates the JSON schema from `schema.py` to ensure the model's output will be valid.
-   **`extractor.py`**: Contains the logic for interacting with the LLM. It formats the prompt, makes the call (currently mocked), receives the response, and uses the Pydantic models from `schema.py` to parse and validate the JSON.
-   **`pipeline.py`**: The main orchestrator. Its `process_article` function ties everything together, taking a file path as input and returning a fully validated `ExtractionOutput` object.
-   **Placeholder Modules (`pubmed.py`, `pmc.py`, `metrics.py`)**: These are included to outline the future direction of the project, such as integrating data fetching and performance evaluation.
