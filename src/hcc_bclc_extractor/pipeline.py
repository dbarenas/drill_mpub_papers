from typing import Union
from pathlib import Path
from .pdf_text import extract_text_from_pdf
from .extractor import extract_structured_data
from .schema import ExtractionOutput
from . import db

def process_article(
    file_path: Union[str, Path],
    persist_to_db: bool = False,
    article_type: str = "unknown"
) -> ExtractionOutput:
    """
    Runs the full data extraction pipeline on a single article file.

    This function orchestrates the process:
    1. Determines the file type (currently supports PDF and TXT).
    2. Extracts the full text from the file.
    3. Sends the text to the extraction module to get structured data.
    4. Optionally, persists the extraction to the database.

    Args:
        file_path: The path to the article file (e.g., a PDF or a text file).
        persist_to_db: If True, saves the extraction to the database.
        article_type: A string representing the type of article (e.g., "TARE").

    Returns:
        An ExtractionOutput object containing the extracted and validated data.
    """
    file_path = Path(file_path)
    if not file_path.is_file():
        raise FileNotFoundError(f"The file was not found at: {file_path}")

    if file_path.suffix.lower() == ".pdf":
        text = extract_text_from_pdf(str(file_path))
    elif file_path.suffix.lower() == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        raise ValueError(f"Unsupported file type: {file_path.suffix}. Please provide a .pdf or .txt file.")

    if not text:
        raise ValueError("Failed to extract text from the document.")

    structured_data = extract_structured_data(text)

    if persist_to_db:
        print("Persisting extraction to the database...")
        db.insert_extraction(
            extraction_output=structured_data,
            pdf_path=str(file_path),
            article_type=article_type
        )

    return structured_data
