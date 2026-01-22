# llm_inference/ollama_client.py
import ollama

PROMPTS = {
    "beginner": "Explain the following medical text in simple terms for someone with no medical background:\n\n{}",
    "intermediate": "Explain the following medical text for a student with some medical knowledge:\n\n{}",
    "expert": "Explain the following medical text in technical detail suitable for a medical researcher:\n\n{}"
}

def generate_explanation(text, level):
    prompt = PROMPTS[level].format(text)

    response = ollama.chat(
        model="llama3.2:latest",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.message.content
