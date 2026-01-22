import pdfplumber

def extract_text_from_pdf(filepath):
    """
    Extracts text from all pages of a PDF file.
    Returns the full text as a string.
    """
    full_text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:  # Avoid adding None
                full_text += page_text + "\n"
    return full_text
