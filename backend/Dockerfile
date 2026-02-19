FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir -r /app/requirements.txt || true
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend /app/backend
COPY templates /app/templates
COPY static /app/static

ENV PYTHONUNBUFFERED=1
EXPOSE 8080

CMD ["gunicorn", "-b", "0.0.0.0:8080", "backend.app:app", "--workers", "2", "--threads", "4"]
