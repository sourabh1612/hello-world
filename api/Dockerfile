FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app /app/app

CMD ["bash","-lc","if [ \"$SERVICE_ROLE\" = \"worker\" ]; then celery -A app.celery_app.celery_app worker -l INFO; else uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload; fi"]