from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Diffrun-like API", version="0.1.0")


class ExecuteRequest(BaseModel):
    job_id: str
    name: str
    gender: str
    book_id: str


class RegenerateRequest(BaseModel):
    job_id: str
    name: str
    gender: str
    workflow_number: int
    jobType: str
    book_id: str
    force: Optional[bool] = False


class UpdatePreview(BaseModel):
    job_id: str
    preview_url: str


class ApproveResponse(BaseModel):
    status: str


@app.post("/store-user-details")
async def store_user_details(
    name: str = Form(...),
    gender: str = Form(...),
    email: str = Form(...),
    age: str = Form(...),
    book_id: str = Form(...),
    images: List[UploadFile] = File(...),
):
    # TODO: persist job, save uploads, run face detection
    job_id = "job_12345"
    return {"job_id": job_id}


@app.post("/execute-workflow-lock")
async def execute_workflow(req: ExecuteRequest):
    # TODO: enqueue workflow tasks for each page
    return {"ok": True}


@app.get("/get-job-status/{job_id}")
async def get_job_status(job_id: str):
    # TODO: read DB for job status
    return {
        "job_id": job_id,
        "workflow_status": "running",
        "paid": False,
        "approved": False,
        "total_workflows": 14,
        "email": "",
        "username": "",
        "preview_url": "",
    }


@app.get("/poll-images-lock")
async def poll_images(job_id: str):
    # TODO: return carousels list with images
    return {
        "carousels": [
            {"workflow": 1, "images": ["https://picsum.photos/seed/1/800/800"]},
            {"workflow": 2, "images": ["https://picsum.photos/seed/2/800/800"]},
        ],
        "completed": False,
        "total_workflows": 14,
    }


@app.post("/regenerate-workflow-lock")
async def regenerate(req: RegenerateRequest):
    # TODO: enqueue regeneration for the specified workflow_number
    return {"ok": True}


@app.post("/update-preview-url")
async def update_preview(req: UpdatePreview):
    # TODO: persist preview URL for job
    return {"ok": True}


@app.post("/approve", response_model=ApproveResponse)
async def approve(
    job_id: str = Form(...),
    name: str = Form(...),
    gender: str = Form(...),
    selectedSlides: str = Form(...),
):
    # TODO: finalize selections and mark job as approved
    return ApproveResponse(status="ok")