from .db import db
from datetime import datetime

class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(512))
    raw_text = db.Column(db.Text)
    doc_type = db.Column(db.String(128))
    classification_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    entities = db.relationship('Entity', back_populates='document', cascade='all, delete-orphan')

    def as_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'doc_type': self.doc_type,
            'classification_score': self.classification_score,
            'created_at': self.created_at.isoformat(),
        }

class Entity(db.Model):
    __tablename__ = 'entities'
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    label = db.Column(db.String(128))
    text = db.Column(db.Text)
    start_char = db.Column(db.Integer)
    end_char = db.Column(db.Integer)

    document = db.relationship('Document', back_populates='entities')

    def as_dict(self):
        return {
            'id': self.id,
            'label': self.label,
            'text': self.text,
            'start_char': self.start_char,
            'end_char': self.end_char,
        }
