from flask import Flask
from .db import db, init_db
from .nlp import NLPAnalyzer
from .routes import register_routes
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    # init extensions
    db.init_app(app)
    with app.app_context():
        init_db()

    # NLP analyzer (singleton-like)
    app.nlp = NLPAnalyzer()

    # register routes
    register_routes(app)
    return app
