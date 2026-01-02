from flask import request, jsonify, current_app
from .db import db
from .models import Document, Entity
from werkzeug.utils import secure_filename

def register_routes(app):
    @app.route('/ping')
    def ping():
        return jsonify({'status': 'ok', 'app': 'nlp-legal-analyzer'})

    @app.route('/analyze', methods=['POST'])
    def analyze():
        # accept raw text in JSON or file upload
        text = None
        if 'file' in request.files:
            f = request.files['file']
            filename = secure_filename(f.filename)
            text = f.read().decode('utf-8', errors='ignore')
        else:
            body = request.get_json(silent=True) or {}
            text = body.get('text') or body.get('raw_text')

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        # optional labels for classification (zero-shot)
        candidate_labels = request.form.get('candidate_labels')
        if candidate_labels:
            candidate_labels = [c.strip() for c in candidate_labels.split(',') if c.strip()]

        result = current_app.nlp.analyze(text, candidate_labels=candidate_labels)

        # persist summary to DB
        doc = Document(title=(text[:60] + '...') if len(text) > 60 else text, raw_text=text)
        # if classification heuristic provided, store doc_type
        if 'heuristic' in result.get('classification', {}):
            doc.doc_type = result['classification']['heuristic'].get('contract_type')
        db.session.add(doc)
        db.session.flush()  # to get doc.id

        # save extracted entities
        for e in result.get('entities', []):
            entity = Entity(document_id=doc.id, label=e['label'], text=e['text'], start_char=e['start_char'], end_char=e['end_char'])
            db.session.add(entity)
        db.session.commit()

        response = {'document': doc.as_dict(), 'entities': [e.as_dict() for e in doc.entities], 'clauses': result.get('clauses', []), 'classification': result.get('classification', {})}
        return jsonify(response), 200

    @app.route('/documents', methods=['GET'])
    def list_documents():
        docs = Document.query.order_by(Document.created_at.desc()).limit(50).all()
        return jsonify([d.as_dict() for d in docs])

    @app.route('/documents/<int:doc_id>', methods=['GET'])
    def get_document(doc_id):
        d = Document.query.get_or_404(doc_id)
        return jsonify({
            'document': d.as_dict(),
            'entities': [e.as_dict() for e in d.entities],
            'raw_text': d.raw_text
        })
