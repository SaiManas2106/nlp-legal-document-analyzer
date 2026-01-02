from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db():
    # create tables if they don't exist
    from .models import Document, Entity
    db.create_all()
