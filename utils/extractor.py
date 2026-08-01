"""PDF Text Extraction Module.

Provides robust PDF text extraction with primary extraction using pdfplumber
and PyPDF2 fallback mechanisms, handling edge cases gracefully.
"""

from pathlib import Path
from typing import Union, Tuple, Dict, Any
from utils.logger import setup_logger

logger = setup_logger("utils.extractor")


def extract_text_from_pdf(pdf_path: Union[str, Path]) -> Tuple[str, Dict[str, Any]]:
    """Extracts raw text content from a PDF file.

    Attempts primary text extraction using `pdfplumber`. If `pdfplumber` fails
    to extract text or encounters an exception, it falls back to `PyPDF2`.

    Args:
        pdf_path (Union[str, Path]): Path to the PDF resume file.

    Returns:
        Tuple[str, Dict[str, Any]]: A tuple containing:
            - str: Extracted raw text content (empty string if unreadable).
            - Dict[str, Any]: Metadata containing 'resume_path', 'resume_filename',
              'extraction_status', and 'extraction_method'.

    Raises:
        FileNotFoundError: If the specified PDF file path does not exist.
    """
    path = Path(pdf_path).resolve()
    metadata: Dict[str, Any] = {
        "resume_path": str(path),
        "resume_filename": path.name,
        "extraction_status": "Failed",
        "extraction_method": "None",
    }

    if not path.exists():
        logger.error(f"PDF file not found at path: {path}")
        raise FileNotFoundError(f"File not found: {path}")

    if path.suffix.lower() != ".pdf":
        logger.warning(f"File {path.name} does not have a .pdf extension.")

    if path.stat().st_size == 0:
        logger.warning(f"PDF file is empty (0 bytes): {path.name}")
        metadata["extraction_status"] = "Empty File"
        return "", metadata

    extracted_text = ""

    # Strategy 1: pdfplumber
    try:
        import pdfplumber

        with pdfplumber.open(path) as pdf:
            pages_text = []
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    pages_text.append(page_text)
            extracted_text = "\n".join(pages_text).strip()

        if extracted_text:
            logger.info(f"Successfully extracted text using pdfplumber from {path.name}")
            metadata["extraction_status"] = "Success"
            metadata["extraction_method"] = "pdfplumber"
            return extracted_text, metadata

        logger.warning(f"pdfplumber yielded empty text for {path.name}. Attempting PyPDF2 fallback.")
    except Exception as exc:
        logger.warning(f"pdfplumber extraction failed for {path.name}: {exc}. Attempting PyPDF2 fallback.")

    # Strategy 2: PyPDF2 / pypdf fallback
    try:
        try:
            import pypdf as pdf_lib
        except ImportError:
            import PyPDF2 as pdf_lib

        with open(path, "rb") as f:
            reader = pdf_lib.PdfReader(f)
            pages_text = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)
            extracted_text = "\n".join(pages_text).strip()

        if extracted_text:
            logger.info(f"Successfully extracted text using PDF fallback from {path.name}")
            metadata["extraction_status"] = "Success"
            metadata["extraction_method"] = "pypdf"
            return extracted_text, metadata

        logger.warning(f"PDF fallback also yielded empty text for {path.name}.")
        metadata["extraction_status"] = "Empty Text"
        metadata["extraction_method"] = "pypdf"
    except Exception as exc:
        logger.error(f"PDF fallback failed for {path.name}: {exc}")
        metadata["extraction_status"] = f"Error: {str(exc)}"
        metadata["extraction_method"] = "Failed"

    return extracted_text, metadata
