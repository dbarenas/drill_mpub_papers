import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts all text content from a given PDF file.

    Args:
        pdf_path: The file path to the PDF document.

    Returns:
        A single string containing all the extracted text from the PDF.
    """
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception as e:
        print(f"Error processing PDF file {pdf_path}: {e}")
        return ""
    return text
