#!/usr/bin/env python3
"""Prepare the source portrait for high-resolution ASCII rendering."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import requests
from rembg import remove

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "data" / "profile-processed.png"
DEFAULT_REMOTE_PHOTO = "https://github.com/user-attachments/assets/53108fb8-6e6d-4907-b680-8109e63dae47"


def discover_source_image() -> Path:
    """Pick the best portrait candidate from repository images."""
    candidates: list[Path] = []
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
        candidates.extend(ROOT.glob(f"data/{ext}"))
        candidates.extend(ROOT.glob(f"assets/misc/{ext}"))
        candidates.extend(ROOT.glob(ext))

    preferred = []
    fallback = []
    for path in candidates:
        if path == OUTPUT_PATH or path.name == "profile-processed.png":
            continue
        key = path.name.lower()
        if any(token in key for token in ("profile", "portrait", "kavish", "photo")):
            preferred.append(path)
        else:
            fallback.append(path)

    ordered = preferred + fallback
    if not ordered:
        ordered = [download_remote_photo()]

    def score(path: Path) -> tuple[int, int]:
        image = cv2.imread(str(path))
        if image is None:
            return (-1, -1)
        area = image.shape[0] * image.shape[1]
        return (1, area)

    best = max(ordered, key=score)
    if score(best)[0] < 0:
        raise ValueError("Found portrait candidates, but none could be decoded as images.")
    return best



def download_remote_photo() -> Path:
    """Download portrait from configured URL when no local file exists."""
    target = ROOT / "data" / "profile-photo.jpg"
    response = requests.get(DEFAULT_REMOTE_PHOTO, timeout=45, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    target.write_bytes(response.content)
    return target


def remove_background(image: np.ndarray) -> np.ndarray:
    """Remove background using rembg and composite foreground on black."""
    ok, encoded = cv2.imencode(".png", image)
    if not ok:
        raise ValueError("Failed to encode source image for background removal")

    rgba_bytes = remove(encoded.tobytes())
    rgba = cv2.imdecode(np.frombuffer(rgba_bytes, np.uint8), cv2.IMREAD_UNCHANGED)
    if rgba is None or rgba.shape[2] != 4:
        raise ValueError("rembg did not return valid RGBA output")

    alpha = rgba[:, :, 3:4].astype(np.float32) / 255.0
    rgb = rgba[:, :, :3].astype(np.float32)
    return (rgb * alpha).astype(np.uint8)


def detect_face_crop(image: np.ndarray, padding: float = 0.45) -> np.ndarray:
    """Detect and crop face region with generous padding for hairstyle and jawline.

    This script intentionally falls back to a centered crop if OpenCV's
    Haar cascade API is unavailable. That keeps the cron job stable even
    if the runner image ships a newer cv2 build without CascadeClassifier.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    h, w = image.shape[:2]

    faces = ()
    cascade_path = None
    if hasattr(cv2, "data") and hasattr(cv2.data, "haarcascades"):
        candidate = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
        if candidate.exists() and hasattr(cv2, "CascadeClassifier"):
            cascade_path = candidate

    if cascade_path is not None:
        detector = cv2.CascadeClassifier(str(cascade_path))
        if not detector.empty():
            faces = detector.detectMultiScale(gray, scaleFactor=1.08, minNeighbors=5, minSize=(120, 120))

    if len(faces) == 0:
        size = min(h, w)
        x0 = (w - size) // 2
        y0 = (h - size) // 2
        return image[y0 : y0 + size, x0 : x0 + size]

    x, y, fw, fh = max(faces, key=lambda f: f[2] * f[3])
    x_pad = int(fw * padding)
    top_pad = int(fh * 0.55)
    bottom_pad = int(fh * 0.65)

    x0 = max(0, x - x_pad)
    y0 = max(0, y - top_pad)
    x1 = min(w, x + fw + x_pad)
    y1 = min(h, y + fh + bottom_pad)
    return image[y0:y1, x0:x1]


def enhance_for_ascii(image: np.ndarray) -> np.ndarray:
    """Apply CLAHE, bilateral denoise, and adaptive sharpening."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.4, tileGridSize=(8, 8))
    contrast = clahe.apply(gray)

    smoothed = cv2.bilateralFilter(contrast, d=9, sigmaColor=30, sigmaSpace=30)
    base_blur = cv2.GaussianBlur(smoothed, (0, 0), sigmaX=1.2)
    sharpened = cv2.addWeighted(smoothed, 1.55, base_blur, -0.55, 0)

    detail = cv2.Laplacian(sharpened, cv2.CV_16S, ksize=3)
    adaptive = cv2.convertScaleAbs(sharpened + np.clip(detail, -20, 20) * 0.25)
    return cv2.resize(adaptive, (1200, 1200), interpolation=cv2.INTER_CUBIC)


def main() -> None:
    """Generate processed portrait image used by ASCII renderer."""
    source = discover_source_image()
    image = cv2.imread(str(source))
    if image is None:
        raise ValueError(f"Could not read source image: {source}")

    foreground = remove_background(image)
    face = detect_face_crop(foreground)
    processed = enhance_for_ascii(face)
    cv2.imwrite(str(OUTPUT_PATH), processed)


if __name__ == "__main__":
    main()
