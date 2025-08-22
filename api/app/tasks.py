import io
import os
import time
import uuid
from PIL import Image, ImageDraw, ImageFont
from minio import Minio
from minio.error import S3Error
from .celery_app import celery_app

S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", "http://minio:9000")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minioadmin")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minioadmin")
S3_BUCKET = os.getenv("S3_BUCKET", "books")
S3_USE_SSL = os.getenv("S3_USE_SSL", "false").lower() == "true"

minio_client = Minio(
    S3_ENDPOINT_URL.replace("http://", "").replace("https://", ""),
    access_key=S3_ACCESS_KEY,
    secret_key=S3_SECRET_KEY,
    secure=S3_USE_SSL,
)


def _ensure_bucket():
    try:
        if not minio_client.bucket_exists(S3_BUCKET):
            minio_client.make_bucket(S3_BUCKET)
    except S3Error:
        pass


def _put_image(img: Image.Image, key: str) -> str:
    _ensure_bucket()
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    buf.seek(0)
    minio_client.put_object(
        S3_BUCKET, key, buf, length=buf.getbuffer().nbytes, content_type="image/jpeg"
    )
    scheme = "https" if S3_USE_SSL else "http"
    return f"{scheme}://{S3_ENDPOINT_URL.replace('http://','').replace('https://','')}/{S3_BUCKET}/{key}"


def _render_placeholder(text: str, seed: int = 0) -> Image.Image:
    w, h = 1024, 1024
    img = Image.new("RGB", (w, h), (240, 240, 240))
    d = ImageDraw.Draw(img)
    # Simple seed-based color stripe
    stripe = (50 + (seed * 37) % 205, 50 + (seed * 73) % 205, 50 + (seed * 91) % 205)
    d.rectangle([0, h - 200, w, h], fill=stripe)
    msg = text
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 48)
    except Exception:
        font = ImageFont.load_default()
    tw, th = d.textsize(msg, font=font)
    d.text(((w - tw) / 2, (h - th) / 2), msg, fill=(20, 20, 20), font=font)
    return img


@celery_app.task(name="app.tasks.generate_page")
def generate_page(job_id: str, workflow_number: int, seed: int = 0) -> str:
    time.sleep(1.0)
    img = _render_placeholder(f"Job {job_id} - Page {workflow_number}", seed=seed)
    key = f"{job_id}/page_{workflow_number}_{uuid.uuid4().hex[:8]}.jpg"
    return _put_image(img, key)


@celery_app.task(name="app.tasks.regenerate_page")
def regenerate_page(job_id: str, workflow_number: int, seed: int = 0) -> str:
    return generate_page(job_id, workflow_number, seed=seed + 1)