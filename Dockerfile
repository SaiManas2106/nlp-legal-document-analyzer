FROM python:3.10-slim
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip && pip install -r requirements.txt
# download small spaCy model to container (optional & can be moved to build step)
RUN python -m spacy download en_core_web_sm
EXPOSE 5000
CMD ["gunicorn", "run:app", "-b", "0.0.0.0:5000", "--workers", "2"]
