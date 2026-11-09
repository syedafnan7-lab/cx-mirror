"""
CX MIRROR — Core Geometry Module
Implements deterministic bounding box math, Intersection-over-Union (IoU),
and Complete Intersection-over-Union (CIoU) based on Zheng et al.
"""

import math
from typing import Dict, Any, Tuple


def calculate_iou(box_a: Dict[str, float], box_b: Dict[str, float]) -> float:
    """
    Calculate standard Intersection-over-Union between two bounding boxes.
    Boxes are dicts with keys: 'x', 'y', 'width', 'height'.
    """
    x1_a, y1_a = box_a['x'], box_a['y']
    x2_a, y2_a = x1_a + box_a['width'], y1_a + box_a['height']

    x1_b, y1_b = box_b['x'], box_b['y']
    x2_b, y2_b = x1_b + box_b['width'], y1_b + box_b['height']

    # Intersection coordinates
    x1_i = max(x1_a, x1_b)
    y1_i = max(y1_a, y1_b)
    x2_i = min(x2_a, x2_b)
    y2_i = min(y2_a, y2_b)

    inter_w = max(0.0, x2_i - x1_i)
    inter_h = max(0.0, y2_i - y1_i)
    inter_area = inter_w * inter_h

    area_a = max(0.0, box_a['width'] * box_a['height'])
    area_b = max(0.0, box_b['width'] * box_b['height'])
    union_area = area_a + area_b - inter_area

    if union_area <= 1e-7:
        return 0.0

    return inter_area / union_area


def calculate_ciou(box_a: Dict[str, float], box_b: Dict[str, float], eps: float = 1e-7) -> Tuple[float, float]:
    """
    Calculate Complete Intersection-over-Union (CIoU) and normalized geometry cost.
    
    Formula:
      CIoU = IoU - (rho^2 / c^2) - (alpha * v)
      v = (4 / pi^2) * (atan(w_b / h_b) - atan(w_a / h_a))^2
      alpha = v / ((1 - IoU) + v + eps)
      C_geometry = (1 - clamp(CIoU, -1, 1)) / 2

    Returns:
      (ciou, c_geometry)
    """
    w_a = max(1e-4, float(box_a['width']))
    h_a = max(1e-4, float(box_a['height']))
    x1_a, y1_a = float(box_a['x']), float(box_a['y'])
    x2_a, y2_a = x1_a + w_a, y1_a + h_a
    cx_a, cy_a = x1_a + w_a / 2.0, y1_a + h_a / 2.0

    w_b = max(1e-4, float(box_b['width']))
    h_b = max(1e-4, float(box_b['height']))
    x1_b, y1_b = float(box_b['x']), float(box_b['y'])
    x2_b, y2_b = x1_b + w_b, y1_b + h_b
    cx_b, cy_b = x1_b + w_b / 2.0, y1_b + h_b / 2.0

    # IoU
    iou = calculate_iou(box_a, box_b)

    # Center distance rho^2
    rho_sq = (cx_a - cx_b) ** 2 + (cy_a - cy_b) ** 2

    # Enclosing box diagonal c^2
    enc_x1 = min(x1_a, x1_b)
    enc_y1 = min(y1_a, y1_b)
    enc_x2 = max(x2_a, x2_b)
    enc_y2 = max(y2_a, y2_b)
    enc_w = enc_x2 - enc_x1
    enc_h = enc_y2 - enc_y1
    c_sq = enc_w ** 2 + enc_h ** 2 + eps

    # Aspect ratio consistency v and alpha
    arctan_diff = math.atan(w_b / h_b) - math.atan(w_a / h_a)
    v = (4.0 / (math.pi ** 2)) * (arctan_diff ** 2)
    alpha = v / ((1.0 - iou) + v + eps)

    # CIoU
    ciou = iou - (rho_sq / c_sq) - (alpha * v)
    ciou = max(-1.0, min(1.0, ciou))

    # Normalized cost in [0, 1]
    c_geometry = (1.0 - ciou) / 2.0
    c_geometry = max(0.0, min(1.0, c_geometry))

    return ciou, c_geometry


def calculate_displacement(box_a: Dict[str, float], box_b: Dict[str, float]) -> Dict[str, float]:
    """
    Calculate Euclidean center displacement vector between box_a (expected) and box_b (actual).
    """
    cx_a = box_a['x'] + box_a['width'] / 2.0
    cy_a = box_a['y'] + box_a['height'] / 2.0
    cx_b = box_b['x'] + box_b['width'] / 2.0
    cy_b = box_b['y'] + box_b['height'] / 2.0

    dx = cx_b - cx_a
    dy = cy_b - cy_a
    distance = math.sqrt(dx ** 2 + dy ** 2)

    return {
        'dx': round(dx, 2),
        'dy': round(dy, 2),
        'distance': round(distance, 2),
        'width_diff': round(box_b['width'] - box_a['width'], 2),
        'height_diff': round(box_b['height'] - box_a['height'], 2)
    }

