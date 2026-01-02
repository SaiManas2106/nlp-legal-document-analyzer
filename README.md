# NLP-Powered Legal Document Analyzer

**Short description**
A Flask-based service that extracts entities, clauses, and obligations from legal contracts using spaCy and Transformers,
offers a REST API for uploads/analysis, and persists extracted metadata in PostgreSQL with simple full-text support.

## Contents
- `app/` - Flask application package (routes, NLP pipeline, DB models)
- `scripts/` - helper scripts (init_db)
- `sample_docs/` - sample contract documents
- `requirements.txt` - Python dependencies
- `Dockerfile` - example Dockerfile
- `.env.example` - sample environment variables

## Quick setup (development)
1. Clone or download this repo, then create a virtualenv:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Download spaCy model(s):
   ```bash
   python -m spacy download en_core_web_sm
   # optionally for transformer-based NER (accurate but heavier):
   # python -m spacy download en_core_web_trf
   ```
3. Set environment variables (see `.env.example`), then initialize the database:
   ```bash
   cp .env.example .env
   # edit .env to set DB URL and secret key
   python scripts/init_db.py
   ```
4. Run the Flask app:
   ```bash
   export FLASK_APP=run.py
   export FLASK_ENV=development
   flask run --host=0.0.0.0 --port=5000
   ```
5. Use the `/analyze` endpoint to POST a text file or JSON `{"text": "..."}.

## Example curl
```bash
curl -X POST http://localhost:5000/analyze -F "file=@sample_docs/sample_contract.txt"
```

## Notes
- This project uses spaCy for NER + lightweight rule-based clause extraction; Transformers (Hugging Face) are used for document classification.
- For production, use a proper database server (Postgres), configure connection pooling, and place models behind a model server if needed.
