# HCC BCLC Clinical Data Extractor

## 1. Overview

The **HCC BCLC Clinical Data Extractor** is a serverless, Python-based application designed to automate the extraction of structured clinical and experimental data from scientific articles on hepatocellular carcinoma (HCC). The system uses **AWS Lambda** and **Amazon Bedrock** to analyze research papers, normalize findings according to the BCLC framework, and persist the data into a PostgreSQL database.

This project is architected for scalability and robustness, using a Pydantic-based schema for data validation and SQLAlchemy for database interactions. By leveraging a serverless architecture, it provides a cost-effective and auto-scaling solution for clinical data analysis and research.

## 2. Key Features

-   **Serverless Architecture**: Built on AWS Lambda for auto-scaling, reliability, and cost-efficiency.
-   **AI-Powered Extraction**: Uses Amazon Bedrock with Anthropic's Claude model to extract structured data from unstructured text.
-   **Structured JSON Output**: Converts scientific text into a validated, machine-readable JSON format.
-   **Database Persistence**: Saves all extracted data into a normalized PostgreSQL database.
-   **BCLC Framework Alignment**: Normalizes data to the specific dimensions of the BCLC staging and treatment framework.
-   **Schema Validation**: Leverages Pydantic models to enforce a strict, validated data structure.
-   **PDF and Text Processing**: Capable of extracting text directly from both `.pdf` and `.txt` files.
-   **Test-Driven**: Includes a comprehensive, mocked test suite to ensure reliability without live AWS calls.

## 3. Architecture

The application is designed to be deployed as an AWS Lambda function. The key components are:
1.  **Lambda Handler (`handler.py`)**: The entry point for the Lambda function, located in the source package.
2.  **Extraction Pipeline (`pipeline.py`)**: Manages the workflow of reading a file, extracting text, and calling the data extractor.
3.  **Bedrock Extractor (`extractor.py`)**: Interfaces with the Amazon Bedrock API to invoke the LLM, sending the text and receiving a structured JSON response.
4.  **Database Module (`db.py`)**: Handles all database interactions, including connection management and data insertion using SQLAlchemy.

## 4. Setup and Installation

To get the project up and running locally, follow these steps. Python 3.11 or higher is required.

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd hcc-bclc-extractor
```

### Step 2: Install Dependencies

Use a virtual environment and install the package in editable mode with development dependencies.

```bash
python -m venv venv
source venv/bin/activate
pip install -e .[dev]
```

## 5. Local Usage

An example script, `run_extraction.py`, is provided to demonstrate the pipeline locally.

### Environment Variables

Create a `.env` file in the project root with the following variables:

```
DATABASE_URL="postgresql://user:password@host:port/dbname"
AWS_REGION="your-aws-region"
# Optional: Specify AWS credentials if not managed by an instance profile
# AWS_ACCESS_KEY_ID="your-access-key"
# AWS_SECRET_ACCESS_KEY="your-secret-key"
```

### Running the Example

The script can initialize the database, process a sample file, and persist the results.

```bash
# Initialize the database schema
python scripts/run_extraction.py --init-db

# Run extraction on the sample file and print JSON to console
python scripts/run_extraction.py

# Run extraction and save the results to the database
python scripts/run_extraction.py --persist
```

## 6. AWS Lambda Deployment

To deploy this application as a Lambda function, you will need to package it with its dependencies and configure the necessary environment variables and permissions.

### Deployment Steps
1.  **Package the code**: Create a zip file containing the `src` directory and all installed dependencies.
2.  **Create a Lambda function**: In the AWS Management Console, create a new Lambda function with a Python 3.11 runtime.
3.  **Upload the package**: Upload the zip file as the function's code.
4.  **Configure the handler**: Set the handler to `hcc_bclc_extractor.handler.handler`.
5.  **Set Environment Variables**:
    -   `DATABASE_URL`: The connection string for your PostgreSQL database.
    -   `AWS_REGION`: The AWS region where Bedrock is enabled.
6.  **Assign IAM Permissions**: Create an IAM role for the Lambda function with permissions to:
    -   Invoke the Bedrock model (`bedrock:InvokeModel`).
    -   Connect to the VPC where your database is located (if applicable).
    -   Write to CloudWatch Logs.

## 7. Running Tests

The test suite is designed to run without live AWS credentials by mocking the Bedrock API calls.

```bash
pytest
```

## 8. Project Structure

```
hcc-bclc-extractor/
├── pyproject.toml              # Project metadata and dependencies
├── README.md                   # This documentation file
├── scripts/
│   └── run_extraction.py       # Local runner script
├── src/
│   └── hcc_bclc_extractor/
│       ├── __init__.py
│       ├── handler.py          # AWS Lambda handler
│       ├── db.py               # Database connection and ORM logic
│       ├── extractor.py        # Bedrock LLM interaction logic
│       ├── pdf_text.py         # Text extraction from PDF files
│       ├── pipeline.py         # End-to-end extraction workflow
│       ├── prompts.py          # Prompt templates for the LLM
│       └── schema.py           # Pydantic data models
└── tests/
    └── ...                     # Test files and fixtures
```
