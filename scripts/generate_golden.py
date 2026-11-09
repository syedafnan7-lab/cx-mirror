"""
CX MIRROR — Golden Mockup Generator
Reproducibly renders the baseline clean checkout sandbox under strict rendering_config.json
and generates:
- frontend/public/golden_mockup.png
- frontend/public/golden_mockup.graph.json
- artifacts/verification/golden_rendering_metadata.json
"""

import os
import sys
import json
import time
import asyncio
import threading
import uvicorn

# Add backend directory to sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
sys.path.insert(0, BACKEND_DIR)

from app.main import app
from app.core.dom_extractor import extract_dom_graph_from_url


def run_temp_server():
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="warning")


async def generate_golden():
    print("[1/5] Starting temporary verification server on port 8001...")
    server_thread = threading.Thread(target=run_temp_server, daemon=True)
    server_thread.start()
    time.sleep(2.0)  # Wait for uvicorn to bind

    frontend_public = os.path.join(PROJECT_ROOT, "frontend", "public")
    os.makedirs(frontend_public, exist_ok=True)
    golden_img_path = os.path.join(frontend_public, "golden_mockup.png")
    golden_graph_path = os.path.join(frontend_public, "golden_mockup.graph.json")
    meta_path = os.path.join(PROJECT_ROOT, "artifacts", "verification", "golden_rendering_metadata.json")
    os.makedirs(os.path.dirname(meta_path), exist_ok=True)

    print("[2/5] Capturing baseline clean sandbox under rendering_config.json...")
    clean_url = "http://127.0.0.1:8001/sandbox?preset=clean"

    graph, screenshot_bytes, meta = await extract_dom_graph_from_url(
        target_url=clean_url,
        screenshot_save_path=golden_img_path
    )

    print(f"[3/5] Golden mockup saved to: {golden_img_path} ({len(screenshot_bytes)} bytes)")

    # Save spatial graph
    graph_dict = {
        "viewport": graph.viewport,
        "nodes": {k: v.model_dump() for k, v in graph.nodes.items()}
    }
    with open(golden_graph_path, "w", encoding="utf-8") as f:
        json.dump(graph_dict, f, indent=2)
    print(f"[4/5] Golden spatial graph saved to: {golden_graph_path} ({len(graph.nodes)} nodes)")

    # Save metadata
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print(f"[5/5] Golden rendering metadata saved to: {meta_path}")

    print("\nSUCCESS: Golden Mockup Baseline Generated Reproducibly!")


if __name__ == "__main__":
    asyncio.run(generate_golden())

