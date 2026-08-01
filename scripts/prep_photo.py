#!/usr/bin/env python3
"""Prepare source photo for ASCII conversion with background removal and CLAHE."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data" / "profile-photo.jpg"
OUTPUT_PATH = ROOT / "data" / "profile-processed.png"


def remove_background(image: np.ndarray) -> np.ndarray:
    """Remove background using GrabCut segmentation."""
    mask = np.zeros(image.shape[:2], np.uint8)
    bg = np.zeros((1, 65), np.float64)
    fg = np.zeros((1, 65), np.float64)
    rect = (20, 20, image.shape[1] - 40, image.shape[0] - 40)
    cv2.grabCut(image, mask, rect, bg, fg, 5, cv2.GC_INIT_WITH_RECT)
    subject = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 1, 0).astype(np.uint8)
    result = image.copy()
    result[subject == 0] = (0, 0, 0)
    return result


def apply_clahe_grayscale(image: np.ndarray) -> np.ndarray:
    """Convert to grayscale and apply CLAHE enhancement."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8))
    return clahe.apply(gray)


def main() -> None:
    """Generate processed photo used by ASCII renderer."""
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Missing source image: {INPUT_PATH}")
    img = cv2.imread(str(INPUT_PATH))
    if img is None:
        raise ValueError("Could not read source image")
    cleaned = remove_background(img)
    enhanced = apply_clahe_grayscale(cleaned)
    cv2.imwrite(str(OUTPUT_PATH), enhanced)


if __name__ == "__main__":
    main()
