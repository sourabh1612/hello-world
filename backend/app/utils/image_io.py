from typing import Optional
from fastapi import UploadFile
from PIL import Image
import io
import numpy as np


async def read_image_from_upload(file: UploadFile, force_mode: Optional[str] = None) -> Image.Image:
	data = await file.read()
	img = Image.open(io.BytesIO(data))
	if force_mode:
		return img.convert(force_mode)
	return img.convert("RGBA") if img.mode in ("P", "RGBA") else img.convert("RGB")


def pil_to_numpy_bgr(img: Image.Image) -> np.ndarray:
	arr = np.array(img)
	if arr.ndim == 2:
		return np.stack([arr, arr, arr], axis=-1)[:, :, ::-1]
	if arr.shape[2] == 4:
		arr = arr[:, :, :3]
	return arr[:, :, ::-1].copy()


def numpy_bgr_to_pil(arr_bgr: np.ndarray) -> Image.Image:
	arr_rgb = arr_bgr[:, :, ::-1]
	return Image.fromarray(arr_rgb)


def pil_to_png_bytes(img: Image.Image) -> bytes:
	buf = io.BytesIO()
	img.save(buf, format="PNG")
	return buf.getvalue()