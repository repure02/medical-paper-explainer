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
            if page_text:
                full_text += page_text + "\n"
    return full_text


def extract_pages_from_pdf(filepath):
    """
    Returns a list of dicts:
    [
        {"page": 1, "text": "..."},
        {"page": 2, "text": "..."}
    ]
    """
    pages = []

    with pdfplumber.open(filepath) as pdf:
        for idx, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text() or ""
            pages.append({
                "page": idx,
                "text": page_text
            })

    return pages


def chunk_pages(pages, max_words=250):
    """
    Split page texts into smaller chunks.
    Returns:
    [
        {"chunk_id": 1, "page": 1, "text": "..."},
        ...
    ]
    """
    chunks = []
    chunk_id = 1

    for item in pages:
        page_num = item["page"]
        text = item["text"]
        words = text.split()

        for i in range(0, len(words), max_words):
            chunk_words = words[i:i + max_words]
            chunk_text = " ".join(chunk_words).strip()

            if chunk_text:
                chunks.append({
                    "chunk_id": chunk_id,
                    "page": page_num,
                    "text": chunk_text
                })
                chunk_id += 1

    return chunks