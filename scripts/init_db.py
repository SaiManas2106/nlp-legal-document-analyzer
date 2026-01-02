# A simple script to create the DB tables. Ensure DATABASE_URL is set in environment or .env.
from app import create_app
from app.db import db, init_db
import os

app = create_app()
with app.app_context():
    init_db()
    print('Database initialized (tables created).')
