import os
from pdf_processing.extractor import extract_text_from_pdf
from llm_inference.ollama_client import generate_explanation

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def process_paper(file, level):
    """
    Core business logic.
    Returns (result_dict, error_message, status_code)
    """
    if not file or file.filename == "":
        return None, "No file provided", 400

    if not file.filename.lower().endswith(".pdf"):
        return None, "Only PDF files are supported", 415

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    text = extract_text_from_pdf(file_path)
    if not text.strip():
        return None, "Could not extract text from PDF", 422

    explanation = generate_explanation(text, level)

    return {
        "explanation": explanation,
        "level": level,
        "filename": file.filename
    }, None, 200

def process_text(text, level):
    #Process raw text instead of PDF
    if not text or not text.strip():
        return None, 'No text provided', 400
    
    explanation = generate_explanation(text, level)

    return {
        'explanation': explanation,
        'level': level
    }, None, 200