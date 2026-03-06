FROM python:3.11-slim

WORKDIR /app

# install system deps (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
EXPOSE 5000

CMD ["gunicorn", "main:app", "--workers", "3", "--bind", "0.0.0.0:5000"]
