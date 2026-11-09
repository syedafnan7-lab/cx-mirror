"""
CX MIRROR — Presets API Router
Provides GET /api/presets and GET /api/presets/{name}.
"""

from typing import List
from fastapi import APIRouter, HTTPException
from app.models.schemas import PresetResponse
from app.services.preset_service import get_all_presets, get_preset

router = APIRouter(prefix="/api/presets", tags=["Presets"])


@router.get("", response_model=List[PresetResponse])
async def list_presets():
    return get_all_presets()


@router.get("/{name}", response_model=PresetResponse)
async def get_single_preset(name: str):
    p = get_preset(name)
    if not p:
        raise HTTPException(status_code=404, detail="Preset not found.")
    return PresetResponse(
        name=p["name"],
        title=p["title"],
        description=p["description"],
        defects_introduced=p["defects_introduced"],
        expected_verdict=p["expected_verdict"]
    )

