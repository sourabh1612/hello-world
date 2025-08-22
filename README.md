# Diffrun-like Backend Scaffold

This repository provides a runnable scaffold for a personalized storybook backend:
- FastAPI API service (job lifecycle and polling endpoint)
- Celery worker (stub generation pipeline producing placeholder page images)
- Postgres (jobs/workflows/images)
- Redis (Celery broker/results)
- MinIO (S3-compatible storage for images)

## Prerequisites
- Docker and Docker Compose

## Run
```bash
docker compose up -d --build
```
- API: http://localhost:8000/docs
- MinIO Console: http://localhost:9001 (minioadmin / minioadmin)

## First test
1) Create a job: `POST /store-user-details` with form-data name, gender, email, age, book_id, images[] (1-3 files)
2) Start workflow: `POST /execute-workflow-lock` (job_id, name, gender, book_id)
3) Poll images: `GET /poll-images-lock?job_id=...`
4) Regenerate a page: `POST /regenerate-workflow-lock` (job_id, workflow_number, ...)
5) Approve: `POST /approve` (job_id, selectedSlides)

## Notes
- This is a development scaffold with placeholder rendering (Pillow) instead of real diffusion models.
- Replace `app/tasks.py` with your generation pipeline (e.g., SDXL + ID adapters) as needed.
