# run_extraction.py
import json
import argparse
import os
from pathlib import Path
from hcc_bclc_extractor.pipeline import process_article
from hcc_bclc_extractor import db
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

def main():
    """
    An example script to demonstrate the clinical data extraction pipeline.

    This script can:
    1. Initialize the database schema.
    2. Process a sample article file and print the JSON output.
    3. Process a sample article and save the results to the database.
    """
    parser = argparse.ArgumentParser(description="HCC BCLC Clinical Data Extractor Runner")
    parser.add_argument(
        "--init-db",
        action="store_true",
        help="Initialize the database schema and exit."
    )
    parser.add_argument(
        "--persist",
        action="store_true",
        help="Persist the extraction result to the database."
    )
    parser.add_argument(
        "--article-type",
        type=str,
        default="systemic_therapy",
        help="The type of the article being processed (e.g., tare, tace)."
    )
    args = parser.parse_args()

    # If --init-db flag is used, initialize schema and exit
    if args.init_db:
        print("Initializing database schema...")
        if not os.getenv("DATABASE_URL"):
            print("Error: DATABASE_URL environment variable is not set.")
            print("Please create a .env file with the DATABASE_URL.")
            return
        db.initialize_schema()
        return

    # Define the path to the sample article file
    sample_file = Path("tests/fixtures/sample_article_1.txt")
    print(f"Processing article: {sample_file}...")

    # Check for DATABASE_URL if persisting
    if args.persist and not os.getenv("DATABASE_URL"):
        print("Error: --persist requires the DATABASE_URL environment variable to be set.")
        print("Please create a .env file with the DATABASE_URL.")
        return

    try:
        # Run the extraction pipeline
        extracted_data = process_article(
            sample_file,
            persist_to_db=args.persist,
            article_type=args.article_type
        )

        # Convert the Pydantic model to a JSON string for pretty printing
        output_json = extracted_data.model_dump_json(indent=2)

        print("\nExtraction Complete. Results:")
        print("----------------------------------")
        print(output_json)
        print("----------------------------------")

    except FileNotFoundError:
        print(f"Error: The file was not found at '{sample_file}'.")
    except ValueError as e:
        print(f"Error processing the article: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
