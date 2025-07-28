FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

CMD ["python3", "main.py"]
