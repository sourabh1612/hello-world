from typing import Tuple
from PIL import Image
import cv2
import numpy as np
from .image_io import pil_to_numpy_bgr, numpy_bgr_to_pil


def _resize_replacement_to_box(repl_bgr: np.ndarray, box: Tuple[int, int, int, int]) -> np.ndarray:
	_, _, w, h = box
	return cv2.resize(repl_bgr, (int(w), int(h)), interpolation=cv2.INTER_AREA)


def blend_face_with_seamless_clone(
	base_image: Image.Image,
	replacement_face: Image.Image,
	mask: Image.Image,
	face_box: Tuple[int, int, int, int],
	mode: str = "mixed",
) -> Image.Image:
	base_bgr = pil_to_numpy_bgr(base_image)
	repl_bgr = pil_to_numpy_bgr(replacement_face)

	# Resize replacement to target box
	repl_resized = _resize_replacement_to_box(repl_bgr, face_box)

	# Prepare mask crop and placement
	x, y, w, h = face_box
	mask_np = np.array(mask.convert("L"))
	# Build mask same size as replacement (crop region around box)
	mask_crop = mask_np[y:y+h, x:x+w]
	if mask_crop.shape[:2] != (h, w):
		mask_crop = cv2.resize(mask_crop, (w, h), interpolation=cv2.INTER_LINEAR)

	# Define center for seamless clone
	center = (int(x + w / 2), int(y + h / 2))

	# Create a composite canvas: place replacement onto a copy of base at the box
	canvas = base_bgr.copy()
	# Ensure the region fits
	H, W = canvas.shape[:2]
	x0, y0 = max(0, x), max(0, y)
	x1, y1 = min(W, x + w), min(H, y + h)
	roi_w, roi_h = x1 - x0, y1 - y0
	if roi_w <= 0 or roi_h <= 0:
		return numpy_bgr_to_pil(base_bgr)

	# adjust if box goes out of bounds
	repl_patch = repl_resized.copy()
	mask_patch = mask_crop.copy()
	if repl_patch.shape[0] != roi_h or repl_patch.shape[1] != roi_w:
		repl_patch = cv2.resize(repl_patch, (roi_w, roi_h), interpolation=cv2.INTER_AREA)
		mask_patch = cv2.resize(mask_patch, (roi_w, roi_h), interpolation=cv2.INTER_LINEAR)

	canvas[y0:y1, x0:x1] = repl_patch
	mask_full = np.zeros((H, W), dtype=np.uint8)
	mask_full[y0:y1, x0:x1] = mask_patch

	flags = cv2.MIXED_CLONE if mode == "mixed" else cv2.NORMAL_CLONE
	output = cv2.seamlessClone(canvas, base_bgr, mask_full, center, flags)
	return numpy_bgr_to_pil(output)