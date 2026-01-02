import re
from typing import List, Dict, Tuple
import spacy
from transformers import pipeline
import os

class NLPAnalyzer:
    def __init__(self):
        # Lazy-load models; allow environment to choose model names.
        # For speed in dev use 'en_core_web_sm'; for better NER use 'en_core_web_trf' if installed.
        spacy_model = os.environ.get('SPACY_MODEL', 'en_core_web_sm')
        try:
            self.nlp = spacy.load(spacy_model)
        except Exception as e:
            # If model isn't installed, raise a helpful message
            raise RuntimeError(f"Failed to load spaCy model '{spacy_model}'. Please run: python -m spacy download {spacy_model}") from e

        # Set up a simple classifier pipeline using HF transformers if available
        # This expects a model name in env var TRANSFORMER_CLASSIFIER (or will use a lightweight default)
        classifier_name = os.environ.get('TRANSFORMER_CLASSIFIER', 'facebook/bart-large-mnli')
        try:
            self.classifier = pipeline('text-classification', model=classifier_name, return_all_scores=True)
        except Exception:
            # Fallback to None if transformers not available; classification will be skipped.
            self.classifier = None

    def preprocess_text(self, text: str) -> str:
        # basic cleanup
        text = text.replace('\r\n', '\n').strip()
        return text

    def extract_entities(self, text: str) -> List[Dict]:
        doc = self.nlp(text)
        entities = []
        for ent in doc.ents:
            entities.append({
                'label': ent.label_,
                'text': ent.text,
                'start_char': ent.start_char,
                'end_char': ent.end_char
            })
        return entities

    def extract_obligations_and_clauses(self, text: str) -> List[Dict]:
        # Naive rule-based clause extraction: look for sentences containing must/shall/agree/obligat
        clauses = []
        sentences = [s.string.strip() for s in self.nlp(text).sents]
        for i, sent in enumerate(sentences):
            lowered = sent.lower()
            if any(k in lowered for k in ('shall', 'must', 'agree to', 'is obligated', 'obligated to', 'required to')):
                clauses.append({'sentence': sent, 'index': i})
        # also look for numbered provisions (e.g., '2.1', 'Section 3', 'Clause 4')
        numbered = re.findall(r'((?:Section|Clause|Article)\s+\d+[\w\.]*)', text, flags=re.IGNORECASE)
        for n in numbered:
            clauses.append({'sentence': n, 'index': None})
        return clauses

    def classify_document(self, text: str, candidate_labels=None) -> Dict:
        # Use transformers zero-shot or simple classifier if available
        if self.classifier and candidate_labels:
            try:
                # using zero-shot with a model such as bart-large-mnli is possible via pipeline if set up
                # Here we expect classifier to return scores per label (interface varies)
                out = self.classifier(text)  # style: list of dicts with 'label' & 'score' if text-classification available
                # if model returned multiple score lists, try to find matches for candidate_labels
                return {'raw': out}
            except Exception:
                return {'raw': None, 'error': 'classification failed'}
        else:
            # fallback heuristic: keyword matching
            labels = {}
            text_lower = text.lower()
            if 'lease' in text_lower or 'tenant' in text_lower:
                labels['contract_type'] = 'Lease Agreement'
            elif 'purchase' in text_lower or 'seller' in text_lower:
                labels['contract_type'] = 'Purchase Agreement'
            else:
                labels['contract_type'] = 'General Contract'
            return {'heuristic': labels}

    def analyze(self, text: str, candidate_labels=None) -> Dict:
        text = self.preprocess_text(text)
        entities = self.extract_entities(text)
        clauses = self.extract_obligations_and_clauses(text)
        classification = self.classify_document(text, candidate_labels=candidate_labels)
        return {
            'text': text,
            'entities': entities,
            'clauses': clauses,
            'classification': classification
        }
