from __future__ import annotations
from typing import List, Dict, Tuple
import os
import cv2
import numpy as np
from PIL import Image
from .image_io import pil_to_numpy_bgr

WEIGHTS_DIR = os.path.join(os.path.dirname(__file__), "..", "weights")
CAFFE_PROTO = os.path.join(WEIGHTS_DIR, "deploy.prototxt")
CAFFE_MODEL = os.path.join(WEIGHTS_DIR, "res10_300x300_ssd_iter_140000.caffemodel")

CAFFE_PROTO_URL = "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt"
CAFFE_MODEL_URL = "https://raw.githubusercontent.com/opencv/opencv_3rdparty/20190709-dnn_face_detector/res10_300x300_ssd_iter_140000_fp16.caffemodel"


def _ensure_weights_present() -> None:
	os.makedirs(WEIGHTS_DIR, exist_ok=True)
	if not os.path.isfile(CAFFE_PROTO):
		try:
			import urllib.request
			urllib.request.urlretrieve(CAFFE_PROTO_URL, CAFFE_PROTO)
		except Exception:
			pass
	if not os.path.isfile(CAFFE_MODEL):
		try:
			import urllib.request
			urllib.request.urlretrieve(CAFFE_MODEL_URL, CAFFE_MODEL)
		except Exception:
			pass


def _dnn_net() -> cv2.dnn_Net | None:
	_ensure_weights_present()
	if os.path.isfile(CAFFE_PROTO) and os.path.isfile(CAFFE_MODEL):
		try:
			return cv2.dnn.readNetFromCaffe(CAFFE_PROTO, CAFFE_MODEL)
		except Exception:
			return None
	return None


def _haar_cascade() -> cv2.CascadeClassifier:
	cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
	return cv2.CascadeClassifier(cascade_path)


def detect_faces(pil_img: Image.Image) -> List[Dict[str, int]]:
	img_bgr = pil_to_numpy_bgr(pil_img)
	h, w = img_bgr.shape[:2]
	results: List[Tuple[int, int, int, int]] = []

	net = _dnn_net()
	if net is not None:
		blob = cv2.dnn.blobFromImage(cv2.resize(img_bgr, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
		net.setInput(blob)
		detections = net.forward()
		for i in range(detections.shape[2]):
			confidence = float(detections[0, 0, i, 2])
			if confidence < 0.5:
				continue
			box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
			x1, y1, x2, y2 = box.astype(int)
			x, y = max(0, x1), max(0, y1)
			bw, bh = int(max(0, x2 - x1)), int(max(0, y2 - y1))
			if bw > 0 and bh > 0:
				results.append((x, y, bw, bh))

	# fallback if nothing found
	if not results:
		gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
		faces = _haar_cascade().detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
		for (x, y, bw, bh) in faces:
			results.append((int(x), int(y), int(bw), int(bh)))

	boxes: List[Dict[str, int]] = [
		{"x": int(x), "y": int(y), "w": int(bw), "h": int(bh)} for (x, y, bw, bh) in results
	]
	return boxes