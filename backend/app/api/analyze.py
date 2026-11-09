"""
CX MIRROR — Analyze API Router
Provides POST /api/analyze and GET /api/analysis/{analysis_id}.
"""

import os
import json
import shutil
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from pydantic import ValidationError

from app.models.schemas import AnalysisResponse
from app.services.analysis_service import run_visual_qa_analysis, get_cached_analysis

router = APIRouter(prefix="/api", tags=["Analysis"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
GOLDEN_PATH_FRONTEND = os.path.join(PROJECT_ROOT, "frontend", "public", "golden_mockup.png")
GOLDEN_GRAPH_FRONTEND = os.path.join(PROJECT_ROOT, "frontend", "public", "golden_mockup.graph.json")
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_design_match(
    mockup: Optional[UploadFile] = File(None),
    target_url: str = Form("http://127.0.0.1:8000/sandbox?preset=clean"),
    preset: str = Form("clean"),
    threshold: float = Form(95.0),
    reference_data: Optional[str] = Form(None),
    viewport_width: int = Form(1440),
    viewport_height: int = Form(1000)
):
    """
    Executes end-to-end visual QA verification between mockup and target URL.
    """
    # Security: restrict target URL access to prevent SSRF
    allowed_hosts = ["localhost", "127.0.0.1", "0.0.0.0", "::1"]
    if not any(h in target_url for h in allowed_hosts):
        raise HTTPException(
            status_code=400, 
            detail="Security restriction: target_url must target local test servers."
        )

    # Resolve mockup image path
    mockup_path = GOLDEN_PATH_FRONTEND
    graph_path = GOLDEN_GRAPH_FRONTEND if os.path.exists(GOLDEN_GRAPH_FRONTEND) else None

    if mockup is not None and mockup.filename:
        # Save uploaded mockup safely
        safe_filename = f"upload_{os.path.basename(mockup.filename)}"
        saved_upload_path = os.path.join(UPLOAD_DIR, safe_filename)
        with open(saved_upload_path, "wb") as buffer:
            shutil.copyfileobj(mockup.file, buffer)
        mockup_path = saved_upload_path
        graph_path = None  # Uploaded file will trigger OpenCV contour segmentation

    if not os.path.exists(mockup_path):
        raise HTTPException(
            status_code=404,
            detail=f"Mockup image not found at {mockup_path}. Please generate golden mockup first."
        )

    # Parse reference data if provided
    custom_ref = None
    if reference_data:
        try:
            custom_ref = json.loads(reference_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid reference_data JSON: {str(e)}")

    try:
        response = await run_visual_qa_analysis(
            mockup_path=mockup_path,
            target_url=target_url,
            preset=preset,
            threshold=threshold,
            custom_reference_data=custom_ref,
            mockup_graph_json_path=graph_path
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis pipeline error: {str(e)}")


@router.get("/analysis/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis_by_id(analysis_id: str):
    cached = get_cached_analysis(analysis_id)
    if not cached:
        raise HTTPException(status_code=404, detail="Analysis ID not found.")
    return cached

