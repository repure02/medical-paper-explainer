# Medical Paper Explainer (Flask + ML)

A Flask-based web application that explains medical research papers
using a local LLM, with both UI and REST API support.

## Features
- Upload PDF or paste text
- Beginner / Intermediate / Expert explanations
- REST API tested with Insomnia
- Clean Flask architecture (Blueprints + Services)
- Local LLM inference (Ollama)

## How to run
```bash
pip install -r requirements.txt
python app.py
```

## API endpoints

GET /api/health

GET /api/levels

POST /api/explain-pdf

POST /api/explain-text
