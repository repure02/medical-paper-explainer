import re
import os
from collections import Counter

from llm_inference.ollama_client import generate_explanation
from pdf_processing.extractor import extract_pages_from_pdf, chunk_pages

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def extract_cited_chunk_ids(explanation: str):
    # finds <<12>> and returns [12, ...]
    ids = re.findall(r"<<(\d+)>>", explanation or "")
    return [int(x) for x in ids]

def select_relevant_chunks(chunks, top_k=5):
    """
    Simple retrieval:
    - build top-N keywords from the whole document
    - score each chunk by keyword overlap
    - return top_k chunks
    """
    if not chunks:
        return []

    # Build global keyword set (simple heuristic)
    all_words = []
    for c in chunks:
        all_words.extend(c["text"].lower().split())

    # Take most common words (skip very short ones)
    filtered = [w for w in all_words if len(w) > 4]
    common = Counter(filtered).most_common(50)  # top 50 keywords
    keywords = set([w for w, _ in common])

    scored = []
    for c in chunks:
        text_words = set(c["text"].lower().split())
        score = len(text_words & keywords)
        scored.append((score, c))

    scored.sort(key=lambda x: x[0], reverse=True)

    return [c for score, c in scored[:top_k]]

# Process PDF files
def process_paper(file, level):
    if not file or file.filename == "":
        return None, "No file provided", 400

    if not file.filename.lower().endswith(".pdf"):
        return None, "Only PDF files are supported", 415

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    pages = extract_pages_from_pdf(file_path)
    chunks = chunk_pages(pages)

    if not chunks:
        return None, "Could not extract text from PDF", 422

    selected_chunks = select_relevant_chunks(chunks)

    # Build text for model from selected chunks only
    context_text = "\n\n".join(
    f"<<CHUNK:{c['chunk_id']}>> (page {c['page']})\n{c['text']}"
    for c in selected_chunks
)

    explanation = generate_explanation(context_text, level)

    cited_ids = extract_cited_chunk_ids(explanation)

    # Map all chunks by id (so we can fetch any cited chunk)
    chunk_map = {c["chunk_id"]: c for c in chunks}

    # Build sources in the order they appear in the explanation, unique, and only if we have them
    final_sources = []
    seen = set()
    for cid in cited_ids:
        if cid in chunk_map and cid not in seen:
            final_sources.append(chunk_map[cid])
            seen.add(cid)

    # Fallback: if model cited nothing (or weirdly), keep your retrieved chunks
    if not final_sources:
        final_sources = selected_chunks

    return {
        "explanation": explanation,
        "level": level,
        "sources": final_sources
    }, None, 200

# Process raw text instead of PDF
def process_text(text, level):
    if not text or not text.strip():
        return None, 'No text provided', 400
    
    explanation = generate_explanation(text, level)

    return {
        'explanation': explanation,
        'level': level
    }, None, 200

