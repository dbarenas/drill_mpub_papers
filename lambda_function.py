import json
import os
import logging
from hcc_bclc_extractor.pipeline import process_article
from hcc_bclc_extractor import db

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def handler(event, context):
    """
    AWS Lambda handler for the HCC BCLC Clinical Data Extractor.

    This function is triggered by an event (e.g., an S3 object creation) and
    orchestrates the data extraction pipeline.

    The expected event format is:
    {
        "file_path": "path/to/the/document.pdf",
        "article_type": "some_category",
        "persist_to_db": true,
        "use_mock": false
    }
    """
    try:
        # Validate and get parameters from the event
        file_path = event.get("file_path")
        if not file_path:
            raise ValueError("Missing 'file_path' in the event payload.")

        article_type = event.get("article_type", "unknown")
        persist_to_db = event.get("persist_to_db", False)
        use_mock = event.get("use_mock", False)

        logger.info(
            "Processing request for file: %s, persist: %s, use_mock: %s",
            file_path, persist_to_db, use_mock
        )

        # Initialize DB schema if the environment variable is set
        if os.getenv("INIT_DB_ON_LAMBDA_START", "false").lower() == "true":
            logger.info("Initializing database schema as requested...")
            db.initialize_schema()
            logger.info("Database schema initialization complete.")

        # Run the extraction pipeline
        extracted_data = process_article(
            file_path=file_path,
            persist_to_db=persist_to_db,
            article_type=article_type,
        )

        # Convert Pydantic model to a dictionary
        output_dict = extracted_data.model_dump()

        logger.info("Successfully processed and extracted data for: %s", file_path)

        return {
            "statusCode": 200,
            "body": json.dumps(output_dict, indent=2),
        }

    except FileNotFoundError:
        logger.error("The specified file was not found: %s", file_path)
        return {
            "statusCode": 404,
            "body": json.dumps({"error": f"File not found: {file_path}"}),
        }
    except ValueError as ve:
        logger.error("A value error occurred: %s", ve)
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(ve)}),
        }
    except Exception as e:
        logger.error("An unexpected error occurred: %s", e, exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "An internal server error occurred."}),
        }
