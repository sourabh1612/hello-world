from typing import Tuple
from PIL import Image, ImageDraw, ImageFilter


def generate_face_mask_from_box(image_size: Tuple[int, int], box: Tuple[int, int, int, int], feather_px: int = 12) -> Image.Image:
	width, height = image_size
	x, y, w, h = box
	mask = Image.new("L", (width, height), 0)
	draw = ImageDraw.Draw(mask)
	# Slightly inset ellipse to avoid hair/background
	inset_x = int(w * 0.08)
	inset_y = int(h * 0.12)
	x0 = max(0, x + inset_x)
	y0 = max(0, y + inset_y)
	x1 = min(width, x + w - inset_x)
	y1 = min(height, y + h - inset_y)
	draw.ellipse([x0, y0, x1, y1], fill=255)
	if feather_px > 0:
		mask = mask.filter(ImageFilter.GaussianBlur(radius=feather_px))
	return mask