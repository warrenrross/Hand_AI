# RPS.AI — Rock Paper Scissors Classifier

A two-stage interactive ML demo. Users train a browser-based image classifier
on their own webcam captures, then challenge it to identify stored images.

---

## How It Works

### Stage 1 · Train
1. Select a class (Rock / Paper / Scissors / None)
2. Click **Capture Sample** — the webcam image is:
   - Added to the in-browser KNN classifier (instant, no reload needed)
   - Uploaded to the FastAPI backend and saved to disk by label
3. Capture 10–20 samples per class from varied angles
4. The live prediction display updates in real time as you train
5. Once you have ≥5 samples per class, the Game button unlocks

### Stage 2 · Game
1. The app fetches 15 random labeled images from the server database
2. Each image is shown to your trained classifier
3. The AI's prediction is compared to the stored ground truth label
4. Results are shown one by one (2.2 seconds each) so you can watch it think
5. A final score and grade is displayed with advice on how to improve

---

## Project Structure

```
rps-classifier/
├── backend/
│   ├── main.py          ← FastAPI server
│   ├── pyproject.toml   ← uv project config & dependencies
│   ├── uv.lock          ← generated lockfile (commit this)
│   └── images/          ← created automatically on first run
│       ├── rock/
│       ├── paper/
│       ├── scissors/
│       └── background/
└── frontend/
    └── index.html       ← single-file app, no build step needed
```

---

## Setup

### Install uv (if you don't have it)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Backend

```bash
cd backend

# Create venv + install all dependencies from pyproject.toml
uv sync

# Run the dev server
uv run uvicorn main:app --reload --port 8000
```

The `/images/` folder is created automatically on first run.

**Adding a new dependency:**
```bash
uv add <package>          # runtime dep  → updates pyproject.toml + uv.lock
uv add --dev <package>    # dev-only dep
uv remove <package>       # remove a dep
```

**Running tests:**
```bash
uv run pytest
```

### Frontend

Open `frontend/index.html` in a local server:

```bash
cd frontend
python3 -m http.server 3000
# → http://localhost:3000
```

> **Note:** Chrome blocks webcam access on `file://` URLs. Use `localhost` or HTTPS.

---

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/upload` | Save a labeled training image |
| GET | `/images-for-game?count=15` | Return N random labeled images for the game |
| GET | `/stats` | Image counts per class |
| GET | `/images/{label}/{file}` | Serve a stored image |

---

## Deployment

**Render.com start command:**
```bash
uv sync && uv run uvicorn main:app --host 0.0.0.0 --port $PORT
```

To swap to Supabase storage, replace the file-write logic in `main.py`:
```bash
uv add supabase
```

---

## Improving Your AI

- **More samples = better accuracy** — aim for 20+ per class
- **Varied angles** — train with your hand tilted, closer, farther
- **Background samples** — a few frames with no hand help the classifier know what "nothing" looks like
- **Consistent lighting** between training and game images helps significantly
