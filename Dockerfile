FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app4.py .

CMD ["uvicorn", "app4:app", "--host", "0.0.0.0", "--port", "8080"]
