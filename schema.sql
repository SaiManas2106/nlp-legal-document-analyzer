-- SQL schema for PostgreSQL (simple)
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(512),
    raw_text TEXT,
    doc_type VARCHAR(128),
    classification_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS entities (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    label VARCHAR(128),
    text TEXT,
    start_char INTEGER,
    end_char INTEGER
);
