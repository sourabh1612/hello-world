from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from starlette.staticfiles import StaticFiles
import io
from PIL import Image
import numpy as np
import os

from .utils.face_detection import detect_faces
from .utils.mask import generate_face_mask_from_box
from .utils.inpaint import blend_face_with_seamless_clone
from .utils.image_io import read_image_from_upload, pil_to_png_bytes

app = FastAPI(title="Watercolor Face Swap API", version="0.1.0")

app.add_middleware(	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# Serve production frontend if built
FRONTEND_DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if os.path.isdir(FRONTEND_DIST):
	app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")

@app.post("/api/detect-faces")
async def api_detect_faces(image: UploadFile = File(...)):
	pil_img = await read_image_from_upload(image)
	boxes = detect_faces(pil_img)
	# boxes as list of dicts
	return JSONResponse({"faces": boxes})

@app.post("/api/auto-mask")
async def api_auto_mask(
	image: UploadFile = File(...),
	x: int = Form(...), y: int = Form(...), w: int = Form(...), h: int = Form(...),
	feather_px: int = Form(12),
):
	pil_img = await read_image_from_upload(image)
	mask = generate_face_mask_from_box(pil_img.size, (x, y, w, h), feather_px=feather_px)
	buf = io.BytesIO()
	mask.save(buf, format="PNG")
	buf.seek(0)
	return StreamingResponse(buf, media_type="image/png")

@app.post("/api/swap-face")
async def api_swap_face(
	base_image: UploadFile = File(...),
	replacement_image: UploadFile = File(...),
	mask_image: UploadFile | None = File(None),
	x: int = Form(...), y: int = Form(...), w: int = Form(...), h: int = Form(...),
	clone_mode: str = Form("mixed"),  # "normal" | "mixed"
):
	base_pil = await read_image_from_upload(base_image)
	repl_pil = await read_image_from_upload(replacement_image)
	if mask_image is not None:
		mask_pil = await read_image_from_upload(mask_image, force_mode="L")
	else:
		mask_pil = generate_face_mask_from_box(base_pil.size, (x, y, w, h), feather_px=12)

	result_pil = blend_face_with_seamless_clone(
		base_image=base_pil,
		replacement_face=repl_pil,
		mask=mask_pil,
		face_box=(x, y, w, h),
		mode=clone_mode,
	)
	buf = io.BytesIO()
	result_pil.save(buf, format="PNG")
	buf.seek(0)
	return StreamingResponse(buf, media_type="image/png")