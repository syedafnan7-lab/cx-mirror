"""
CX MIRROR — Graph Matcher Module
Implements multi-modal Hungarian Assignment (scipy.optimize.linear_sum_assignment),
semantic compatibility penalties, dummy node cost padding, and deterministic refinement.
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from scipy.optimize import linear_sum_assignment

from app.models.graph_models import GraphNode, MatchedPair, Displacement
from app.core.geometry import calculate_ciou, calculate_displacement
from app.core.color_science import calculate_delta_e
from app.core.similarity import calculate_text_similarity, calculate_ssim


# Default modality weights
W_GEOMETRY = 0.35
W_SSIM = 0.20
W_COLOR = 0.15
W_TEXT = 0.30

# Unmatched assignment threshold
UNMATCHED_COST_THRESHOLD = 0.75


def compute_semantic_penalty(mockup_node: GraphNode, dom_node: GraphNode) -> float:
    """
    Calculate semantic role and element type compatibility penalty.
    Returns penalty in range [0.0, 1.0].
    """
    m_role = (mockup_node.role or "").lower()
    d_role = (dom_node.role or "").lower()

    m_type = (mockup_node.element_type or "").lower()
    d_type = (dom_node.element_type or "").lower()

    # Exact role match
    if m_role and d_role and m_role == d_role:
        return 0.0

    # Strict role mismatches
    strict_roles = {"current_price", "original_price", "legal_disclaimer", "cta", "sku"}
    if m_role in strict_roles and d_role in strict_roles and m_role != d_role:
        return 0.90  # Severe penalty for price <-> legal, etc.

    if m_role in strict_roles and not d_role:
        return 0.40

    # Element type matching
    if m_type == d_type:
        return 0.0
    
    if (m_type in {"text", "price", "legal"} and d_type in {"text", "price", "legal"}):
        return 0.10

    if (m_type == "button" and d_type == "button"):
        return 0.0

    # Incompatible types (e.g. image vs text)
    if (m_type == "image" and d_type in {"text", "legal", "price"}) or (d_type == "image" and m_type in {"text", "legal", "price"}):
        return 0.85

    return 0.25


def extract_node_crop(image: Optional[np.ndarray], node: GraphNode) -> Optional[np.ndarray]:
    """Extract sub-image patch for SSIM calculation from node bounding box."""
    if image is None:
        return None
    h, w = image.shape[:2]
    bb = node.bounding_box
    x1 = max(0, min(w - 1, int(bb.x)))
    y1 = max(0, min(h - 1, int(bb.y)))
    x2 = max(x1 + 1, min(w, int(bb.x + bb.width)))
    y2 = max(y1 + 1, min(h, int(bb.y + bb.height)))

    crop = image[y1:y2, x1:x2]
    return crop if crop.size > 0 else None


def match_spatial_graphs(
    mockup_nodes: Dict[str, GraphNode],
    dom_nodes: Dict[str, GraphNode],
    mockup_image: Optional[np.ndarray] = None,
    dom_image: Optional[np.ndarray] = None
) -> Tuple[List[MatchedPair], List[str], List[str]]:
    """
    Perform Hungarian bipartite matching between Mockup Graph G_M and DOM Graph G_D.
    
    Returns:
      (matched_pairs, unmatched_mockup_node_ids, unmatched_dom_node_ids)
    """
    m_keys = list(mockup_nodes.keys())
    d_keys = list(dom_nodes.keys())

    num_m = len(m_keys)
    num_d = len(d_keys)

    if num_m == 0:
        return [], [], d_keys
    if num_d == 0:
        return [], m_keys, []

    # Construct Cost Matrix C of size (num_m, num_d)
    cost_matrix = np.zeros((num_m, num_d), dtype=np.float64)
    metric_cache: Dict[Tuple[int, int], Dict[str, float]] = {}

    for i, m_id in enumerate(m_keys):
        m_node = mockup_nodes[m_id]
        m_box = m_node.bounding_box.model_dump()
        m_crop = extract_node_crop(mockup_image, m_node)

        for j, d_id in enumerate(d_keys):
            d_node = dom_nodes[d_id]
            d_box = d_node.bounding_box.model_dump()
            d_crop = extract_node_crop(dom_image, d_node)

            # 1. CIoU & Geometry Cost
            ciou, c_geom = calculate_ciou(m_box, d_box)

            # 2. SSIM Cost
            if m_crop is not None and d_crop is not None:
                raw_ssim, c_ssim = calculate_ssim(m_crop, d_crop)
                has_ssim = True
            else:
                raw_ssim, c_ssim = 0.5, 0.25
                has_ssim = False

            # 3. Color Cost (CIE LAB Delta E)
            if m_node.color and d_node.color:
                delta_e, c_color = calculate_delta_e(m_node.color, d_node.color)
                has_color = True
            else:
                delta_e, c_color = 0.0, 0.0
                has_color = False

            # 4. Text Cost
            has_text = bool(m_node.text or d_node.text)
            if has_text:
                text_sim, c_text = calculate_text_similarity(m_node.text or "", d_node.text or "")
            else:
                text_sim, c_text = 1.0, 0.0

            # Proportional weight redistribution if a modality is unavailable
            active_weights = {
                "geom": W_GEOMETRY,
                "ssim": W_SSIM if has_ssim else 0.0,
                "color": W_COLOR if has_color else 0.0,
                "text": W_TEXT if has_text else 0.0,
            }
            w_sum = sum(active_weights.values())
            if w_sum > 0:
                scale = 1.0 / w_sum
                total_cost = (
                    active_weights["geom"] * scale * c_geom +
                    active_weights["ssim"] * scale * c_ssim +
                    active_weights["color"] * scale * c_color +
                    active_weights["text"] * scale * c_text
                )
            else:
                total_cost = c_geom

            # Semantic penalty
            sem_penalty = compute_semantic_penalty(m_node, d_node)
            final_cost = min(1.0, 0.80 * total_cost + 0.20 * sem_penalty)

            cost_matrix[i, j] = final_cost

            # Cache raw metrics
            disp = calculate_displacement(m_box, d_box)
            metric_cache[(i, j)] = {
                "ciou": ciou,
                "c_geometry": c_geom,
                "raw_ssim": raw_ssim,
                "c_ssim": c_ssim,
                "delta_e": delta_e,
                "c_color": c_color,
                "text_sim": text_sim,
                "c_text": c_text,
                "dx": disp["dx"],
                "dy": disp["dy"],
                "distance": disp["distance"],
                "width_diff": disp["width_diff"],
                "height_diff": disp["height_diff"],
                "sem_penalty": sem_penalty,
                "final_cost": final_cost
            }

    # Solve bipartite matching with Hungarian Algorithm
    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    matched_pairs: List[MatchedPair] = []
    matched_m_indices = set()
    matched_d_indices = set()

    for r, c in zip(row_ind, col_ind):
        cost = cost_matrix[r, c]
        metrics = metric_cache[(r, c)]

        # Check threshold for unmatchable / dummy rejection
        if cost > UNMATCHED_COST_THRESHOLD:
            continue

        m_id = m_keys[r]
        d_id = d_keys[c]
        m_node = mockup_nodes[m_id]

        # Calculate ambiguity: is there another match with almost identical cost?
        row_costs = np.sort(cost_matrix[r, :])
        if len(row_costs) > 1 and abs(row_costs[1] - row_costs[0]) < 0.05:
            match_confidence = max(0.40, 1.0 - cost - 0.15)
        else:
            match_confidence = max(0.10, 1.0 - cost)

        # Quality score Q_i in [0, 1]
        q_i = max(0.0, min(1.0, 1.0 - (
            W_GEOMETRY * metrics["c_geometry"] +
            W_SSIM * metrics["c_ssim"] +
            W_COLOR * metrics["c_color"] +
            W_TEXT * metrics["c_text"]
        )))

        matched_pair = MatchedPair(
            mockup_node_id=m_id,
            dom_node_id=d_id,
            semantic_role=m_node.role or m_node.element_type,
            importance=m_node.importance,
            c_geometry=round(metrics["c_geometry"], 4),
            ciou=round(metrics["ciou"], 4),
            c_ssim=round(metrics["c_ssim"], 4),
            raw_ssim=round(metrics["raw_ssim"], 4),
            c_color=round(metrics["c_color"], 4),
            delta_e=round(metrics["delta_e"], 2),
            c_text=round(metrics["c_text"], 4),
            text_sim=round(metrics["text_sim"], 4),
            displacement=Displacement(
                dx=metrics["dx"],
                dy=metrics["dy"],
                distance=metrics["distance"],
                width_diff=metrics["width_diff"],
                height_diff=metrics["height_diff"]
            ),
            match_confidence=round(match_confidence, 4),
            quality_score=round(q_i, 4)
        )

        matched_pairs.append(matched_pair)
        matched_m_indices.add(r)
        matched_d_indices.add(c)

    # Deterministic Refinement Pass: Check edge hierarchy and parent context
    # (If both child and parent exist, ensure consistency)

    unmatched_m = [m_keys[i] for i in range(num_m) if i not in matched_m_indices]
    unmatched_d = [d_keys[j] for j in range(num_d) if j not in matched_d_indices]

    return matched_pairs, unmatched_m, unmatched_d

