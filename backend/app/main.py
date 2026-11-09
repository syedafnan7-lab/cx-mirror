"""
CX MIRROR — Main FastAPI Application
Entry point for CX Mirror verification backend and e-commerce sandbox.
"""

import os
import time
import json
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse

from app.api.analyze import router as analyze_router
from app.api.presets import router as presets_router
from app.api.benchmark import router as benchmark_router
from app.services.preset_service import get_preset

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
SANDBOX_DIR = os.path.join(PROJECT_ROOT, "sandbox")
ARTIFACTS_DIR = os.path.join(PROJECT_ROOT, "artifacts")
REF_DATA_PATH = os.path.join(BASE_DIR, "data", "reference_data.json")

app = FastAPI(
    title="CX MIRROR — AI Visual QA Platform",
    description="Your Design. Your Experience. Mathematically Verified.",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(analyze_router)
app.include_router(presets_router)
app.include_router(benchmark_router)

# Mount sandbox static files (CSS, JS)
app.mount("/sandbox/static", StaticFiles(directory=SANDBOX_DIR), name="sandbox_static")


@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "service": "CX Mirror Verification Engine",
        "version": "1.0.0",
        "timestamp": time.time()
    }


@app.get("/api/reference-data")
async def get_reference_data():
    if not os.path.exists(REF_DATA_PATH):
        raise HTTPException(status_code=404, detail="Reference data not found.")
    with open(REF_DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/api/artifacts/{artifact_name}")
async def get_artifact_file(artifact_name: str):
    """
    Safely serve verification artifacts and screenshots with path traversal protection.
    """
    safe_name = os.path.basename(artifact_name)

    # Search in artifacts/screenshots, artifacts/verification, or frontend/public
    search_paths = [
        os.path.join(ARTIFACTS_DIR, "screenshots", safe_name),
        os.path.join(ARTIFACTS_DIR, "verification", safe_name),
        os.path.join(PROJECT_ROOT, "backend", "artifacts", "screenshots", safe_name),
        os.path.join(PROJECT_ROOT, "frontend", "public", safe_name),
        os.path.join(BASE_DIR, "data", "uploads", safe_name)
    ]

    for p in search_paths:
        if os.path.exists(p) and os.path.isfile(p):
            media_type = "image/png" if p.endswith(".png") else "application/octet-stream"
            return FileResponse(p, media_type=media_type)

    # Fallback for screenshots
    fallback_paths = [
        os.path.join(ARTIFACTS_DIR, "screenshots", "01_clean_pass.png"),
        os.path.join(PROJECT_ROOT, "frontend", "public", "golden_mockup.png")
    ]
    for fb in fallback_paths:
        if os.path.exists(fb):
            return FileResponse(fb, media_type="image/png")

    raise HTTPException(status_code=404, detail=f"Artifact {safe_name} not found.")


@app.get("/sandbox", response_class=HTMLResponse)
async def get_sandbox_store(preset: str = Query("clean", description="Sandbox mutation preset")):
    """
    Renders e-commerce checkout sandbox with selected mutation preset.
    """
    html_path = os.path.join(SANDBOX_DIR, "store.html")
    if not os.path.exists(html_path):
        raise HTTPException(status_code=404, detail="store.html template not found.")

    with open(html_path, "r", encoding="utf-8") as f:
        template = f.read()

    p_data = get_preset(preset)

    rendered = (
        template
        .replace("{{ preset }}", p_data["name"])
        .replace("{{ sku }}", p_data["sku"])
        .replace("{{ product_name }}", p_data["product_name"])
        .replace("{{ current_price }}", p_data["current_price"])
        .replace("{{ original_price }}", p_data["original_price"])
        .replace("{{ discount_badge }}", p_data["discount_badge"])
        .replace("{{ legal_text }}", p_data["legal_text"])
    )

    return HTMLResponse(content=rendered, status_code=200)

