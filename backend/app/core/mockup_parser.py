"""
CX MIRROR — Mockup Parser Module
Extracts Mockup Spatial Graph G_M from design mockup images using deterministic
OpenCV contour analysis, morphological operators, color sampling, and design metadata.
"""

import os
import json
from typing import Dict, Any, Tuple, Optional, List
import cv2
import numpy as np

from app.models.graph_models import GraphNode, BoundingBox, SpatialGraph


def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"


def extract_mockup_graph_from_image(
    image_path: str,
    associated_graph_json: Optional[str] = None
) -> Tuple[SpatialGraph, np.ndarray]:
    """
    Parses design mockup image into a SpatialGraph G_M.
    Uses golden design metadata if available, otherwise executes deterministic
    OpenCV contour hierarchy segmentation and color sampling.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Mockup image not found at: {image_path}")

    # Read image using OpenCV
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Failed to decode image from: {image_path}")

    img_h, img_w = image.shape[:2]

    # If associated graph metadata file exists (e.g. golden_mockup.graph.json), load it directly
    if associated_graph_json and os.path.exists(associated_graph_json):
        with open(associated_graph_json, "r", encoding="utf-8") as f:
            data = json.load(f)
            nodes = {k: GraphNode(**v) for k, v in data.get("nodes", {}).items()}
            return SpatialGraph(nodes=nodes, viewport=data.get("viewport", {"width": img_w, "height": img_h})), image

    # Automatic OpenCV Contour and Morphological Segmentation
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Adaptive threshold / Canny edges
    edges = cv2.Canny(blurred, 30, 120)

    # Morphological close to merge nearby text lines and buttons
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 5))
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    # Find external and structural contours
    contours, _ = cv2.findContours(closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    nodes: Dict[str, GraphNode] = {}
    counter = 0

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h

        # Filter microscopic noise or entire canvas contour
        if area < 400 or (w >= img_w - 10 and h >= img_h - 10):
            continue

        # Extract median color inside box
        roi = image[y:y+h, x:x+w]
        if roi.size == 0:
            continue

        median_bgr = np.median(roi.reshape(-1, 3), axis=0)
        color_hex = rgb_to_hex(median_bgr[2], median_bgr[1], median_bgr[0])

        # Heuristic element classification based on aspect ratio and geometry
        aspect_ratio = w / float(h)
        element_type = "container"
        importance = 1.0

        if 2.0 <= aspect_ratio <= 8.0 and 24 <= h <= 65:
            element_type = "button"
            importance = 2.0
        elif aspect_ratio > 3.0 and h <= 30:
            element_type = "text"
            importance = 1.0
        elif 0.8 <= aspect_ratio <= 1.8 and w > 150:
            element_type = "image"
            importance = 1.5

        node_id = f"mockup_box_{counter}"
        counter += 1

        nodes[node_id] = GraphNode(
            id=node_id,
            element_type=element_type,
            role=None,
            text="",
            bounding_box=BoundingBox(x=float(x), y=float(y), width=float(w), height=float(h)),
            font_size=14.0 if element_type == "text" else None,
            color=color_hex,
            background_color=color_hex,
            importance=importance,
            visibility=True
        )

    return SpatialGraph(nodes=nodes, viewport={"width": img_w, "height": img_h}), image

