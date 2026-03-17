"""
Rock Paper Scissors Classifier Backend
FastAPI server that stores training images and serves them for the game phase.
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import uuid
import json
import random
from datetime import datetime
from pathlib import Path

app = FastAPI(title="RPS Classifier API")

# Allow all origins for local dev — tighten this for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------------------------------
# Storage setup
# In production, swap this for Supabase Storage or S3.
# For now, images are saved to disk under /images/<label>/
# --------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
IMAGE_DIR = BASE_DIR / "images"
LABELS = ["rock", "paper", "scissors", "background"]

for label in LABELS:
    (IMAGE_DIR / label).mkdir(parents=True, exist_ok=True)

# Serve stored images as static files
app.mount("/images", StaticFiles(directory=str(IMAGE_DIR)), name="images")


# --------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------

@app.get("/")
def root():
    return {"status": "ok", "message": "RPS Classifier API running"}


@app.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    label: str = Form(...),
):
    """
    Receives a webcam snapshot (JPEG/PNG) and a label (rock/paper/scissors/background).
    Saves it to disk and returns the file path.
    """
    if label not in LABELS:
        raise HTTPException(status_code=400, detail=f"Invalid label. Must be one of: {LABELS}")

    ext = "jpg"
    filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.{ext}"
    save_path = IMAGE_DIR / label / filename

    contents = await file.read()
    with open(save_path, "wb") as f:
        f.write(contents)

    return {
        "status": "saved",
        "label": label,
        "filename": filename,
        "url": f"/images/{label}/{filename}",
    }


@app.get("/images-for-game")
def get_game_images(count: int = 15):
    """
    Returns a random selection of labeled images for the game phase.
    Tries to balance across labels. Returns URL + correct label for grading.
    """
    pool = []
    for label in LABELS:
        label_dir = IMAGE_DIR / label
        files = list(label_dir.glob("*.jpg")) + list(label_dir.glob("*.png"))
        for f in files:
            pool.append({"url": f"/images/{label}/{f.name}", "label": label})

    if len(pool) == 0:
        raise HTTPException(status_code=404, detail="No images stored yet. Train first!")

    selected = random.sample(pool, min(count, len(pool)))
    random.shuffle(selected)
    return {"images": selected, "total_available": len(pool)}


@app.get("/stats")
def get_stats():
    """Returns count of stored images per label."""
    stats = {}
    for label in LABELS:
        label_dir = IMAGE_DIR / label
        files = list(label_dir.glob("*.jpg")) + list(label_dir.glob("*.png"))
        stats[label] = len(files)
    stats["total"] = sum(stats.values())
    return stats
