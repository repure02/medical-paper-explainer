import ollama
import re

# Detect chunk citations like <<12>>
CITATION_PATTERN = re.compile(r"<<\d+>>")
# Detect the required citations list line
CITATIONS_USED_PATTERN = re.compile(r"(?im)^CITATIONS USED:\s*(.+)$")


CITATION_RULES = """
CITATION RULES:
- Use ONLY the provided context chunks.
- Chunk markers appear in the context as <<CHUNK:ID>>.
- When you cite evidence, cite ONLY using chunk ids in the format <<ID>> (example: <<2>> or <<2>><<5>>).
- Every paragraph MUST contain at least one chunk citation in the format <<ID>>.
- Do NOT use square bracket citations like [6] because those are paper references, not chunk ids.
- If the context does not contain enough information, say:
  "I couldn't find that information in the provided paper excerpt."
- Do NOT invent facts or citations.
- Valid chunk ids you are allowed to cite: {valid_ids}

OUTPUT FORMAT (MUST FOLLOW EXACTLY):
Explanation:
<your explanation with citations <<ID>> in every paragraph>

CITATIONS USED: <comma-separated list of <<ID>> you used, e.g. <<2>>, <<5>>
"""

PROMPTS = {
    "beginner": """
You are a helpful assistant explaining a medical paper to someone with no medical background.

{citation_rules}

CONTEXT:
{context}

TASK:
Write a clear, simple explanation using only the context above.
""",
#-------
    "intermediate": """
You are a helpful assistant explaining a medical paper to a student with some medical knowledge.

{citation_rules}

CONTEXT:
{context}

TASK:
Write a structured explanation using only the context above.
""",
#-------
    "expert": """
You are a medical research assistant explaining a paper to an expert audience.

{citation_rules}

CONTEXT:
{context}

TASK:
Write a detailed, technical explanation using only the context above.
"""
}


def _build_prompt(context_text: str, level: str) -> str:
    # Extract ids from markers like: <<CHUNK:12>>
    ids = re.findall(r"<<CHUNK:(\d+)>>", context_text)
    valid_ids = ", ".join(sorted(set(ids), key=int)) if ids else "None"

    return PROMPTS[level].format(
        context=context_text,
        citation_rules=CITATION_RULES.format(valid_ids=valid_ids)
    )


def _needs_retry(output: str) -> bool:
    """
    We retry if:
    - No <<ID>> citations appear anywhere, OR
    - The 'CITATIONS USED:' line is missing.
    """
    has_any_citation = bool(CITATION_PATTERN.search(output))
    has_citations_used_line = bool(CITATIONS_USED_PATTERN.search(output))
    return (not has_any_citation) or (not has_citations_used_line)


def generate_explanation(context_text: str, level: str) -> str:
    prompt = _build_prompt(context_text, level)

    response = ollama.chat(
        model="llama3.2:latest",
        messages=[{"role": "user", "content": prompt}]
    )
    output = response.message.content

    # One retry with stricter instruction if needed
    if _needs_retry(output):
        retry_prompt = prompt + """
IMPORTANT: Your previous answer did not follow the required output format.
You MUST:
- Include at least one <<ID>> citation in EVERY paragraph.
- Include a final line exactly like:
  CITATIONS USED: <<2>>, <<5>>
Now rewrite the answer in the required format.
"""
        response2 = ollama.chat(
            model="llama3.2:latest",
            messages=[{"role": "user", "content": retry_prompt}]
        )
        output = response2.message.content

    return output
