FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir -r /app/requirements.txt || true
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend /app/backend
COPY templates /app/templates
COPY static /app/static

ENV PYTHONUNBUFFERED=1
ENV PORT=8086
EXPOSE 8086

CMD ["sh", "-c", "exec gunicorn -k gthread -w 1 --threads 8 --bind 0.0.0.0:${PORT} backend.app:app"]
