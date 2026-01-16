# run_extraction.py
import json
from pathlib import Path
from hcc_bclc_extractor.pipeline import process_article

def main():
    """
    An example script to demonstrate the clinical data extraction pipeline.

    This script processes a sample article file, extracts the structured data,
    and prints the result as a formatted JSON object to the console.
    """
    # Define the path to the sample article file
    # You can change this to a .pdf file if you have one available.
    sample_file = Path("tests/fixtures/sample_article_1.txt")

    print(f"Processing article: {sample_file}...")

    try:
        # Run the extraction pipeline on the specified file
        extracted_data = process_article(sample_file)

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
