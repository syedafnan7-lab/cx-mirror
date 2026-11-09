"""
CX MIRROR — Analysis Service
Coordinates DOM extraction, Mockup parsing, Hungarian graph matching,
Contract validation, and multi-modal confidence scoring.
"""

import os
import time
import uuid
import json
from typing import Dict, Any, Optional, Tuple
import cv2
import numpy as np

from app.models.schemas import AnalysisResponse, AnalysisScores, AnalysisSummary
from app.models.graph_models import SpatialGraph, GraphNode
from app.core.dom_extractor import extract_dom_graph_from_url
from app.core.mockup_parser import extract_mockup_graph_from_image
from app.core.graph_matcher import match_spatial_graphs
from app.core.contract_validator import validate_contracts
from app.core.confidence import compute_confidence_scores

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # backend/app
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", "..")) # CX-MIRROR
REF_DATA_PATH = os.path.join(BASE_DIR, "data", "reference_data.json")
ARTIFACTS_DIR = os.path.join(PROJECT_ROOT, "artifacts")

# In-memory analysis cache
ANALYSIS_CACHE: Dict[str, AnalysisResponse] = {}


def load_default_reference_data() -> Dict[str, Any]:
    if os.path.exists(REF_DATA_PATH):
        with open(REF_DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


async def run_visual_qa_analysis(
    mockup_path: str,
    target_url: str,
    preset: str = "clean",
    threshold: float = 95.0,
    custom_reference_data: Optional[Dict[str, Any]] = None,
    mockup_graph_json_path: Optional[str] = None
) -> AnalysisResponse:
    """
    Executes full deterministic verification pipeline.
    """
    start_time = time.time()
    analysis_id = f"analysis_{uuid.uuid4().hex[:8]}"

    os.makedirs(os.path.join(ARTIFACTS_DIR, "screenshots"), exist_ok=True)
    live_screenshot_path = os.path.join(ARTIFACTS_DIR, "screenshots", f"{analysis_id}_live.png")

    # 1. Playwright DOM extraction and live screenshot capture
    dom_graph, live_bytes, rendering_meta = await extract_dom_graph_from_url(
        target_url=target_url,
        screenshot_save_path=live_screenshot_path
    )

    # 2. Mockup Graph extraction
    mockup_graph, mockup_cv_img = extract_mockup_graph_from_image(
        image_path=mockup_path,
        associated_graph_json=mockup_graph_json_path
    )

    # Decode live image for SSIM crop comparisons
    nparr = np.frombuffer(live_bytes, np.uint8)
    live_cv_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # 3. Hungarian Graph Matching with semantic compatibility and refinement
    matched_pairs, unmatched_m, unmatched_d = match_spatial_graphs(
        mockup_nodes=mockup_graph.nodes,
        dom_nodes=dom_graph.nodes,
        mockup_image=mockup_cv_img,
        dom_image=live_cv_img
    )

    # 4. Reference Contract Validation
    ref_data = custom_reference_data or load_default_reference_data()
    contracts = validate_contracts(dom_nodes=dom_graph.nodes, reference_data=ref_data)

    # 5. Confidence Engine and Decision Formula
    verdict, confidence, scores, summary, discrepancies = compute_confidence_scores(
        matched_pairs=matched_pairs,
        unmatched_mockup=unmatched_m,
        unmatched_dom=unmatched_d,
        mockup_nodes=mockup_graph.nodes,
        dom_nodes=dom_graph.nodes,
        contracts=contracts,
        threshold=threshold
    )

    exec_time = round((time.time() - start_time) * 1000, 2)

    response = AnalysisResponse(
        analysis_id=analysis_id,
        status="completed",
        verdict=verdict,
        confidence=confidence,
        threshold=threshold,
        scores=scores,
        summary=summary,
        matches=matched_pairs,
        unmatched_mockup_nodes=[{"id": nid} for nid in unmatched_m],
        unmatched_dom_nodes=[{"id": nid} for nid in unmatched_d],
        discrepancies=discrepancies,
        contracts=contracts,
        graph={
            "mockup_nodes": {k: v.model_dump() for k, v in mockup_graph.nodes.items()},
            "dom_nodes": {k: v.model_dump() for k, v in dom_graph.nodes.items()}
        },
        artifacts={
            "live_screenshot": f"/api/artifacts/{os.path.basename(live_screenshot_path)}",
            "mockup_image": f"/api/artifacts/{os.path.basename(mockup_path)}"
        },
        rendering_metadata=rendering_meta,
        execution_time_ms=exec_time
    )

    ANALYSIS_CACHE[analysis_id] = response
    return response


def get_cached_analysis(analysis_id: str) -> Optional[AnalysisResponse]:
    return ANALYSIS_CACHE.get(analysis_id)

