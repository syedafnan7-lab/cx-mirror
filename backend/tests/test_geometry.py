"""
Unit tests for CIoU, IoU, and bounding box geometry.
"""

import pytest
import math
from app.core.geometry import calculate_iou, calculate_ciou, calculate_displacement


def test_perfect_overlap_iou():
    box_a = {"x": 100, "y": 100, "width": 200, "height": 100}
    box_b = {"x": 100, "y": 100, "width": 200, "height": 100}
    iou = calculate_iou(box_a, box_b)
    assert abs(iou - 1.0) < 1e-5


def test_disjoint_boxes_iou():
    box_a = {"x": 0, "y": 0, "width": 50, "height": 50}
    box_b = {"x": 100, "y": 100, "width": 50, "height": 50}
    iou = calculate_iou(box_a, box_b)
    assert iou == 0.0


def test_perfect_overlap_ciou():
    box_a = {"x": 100, "y": 100, "width": 200, "height": 100}
    box_b = {"x": 100, "y": 100, "width": 200, "height": 100}
    ciou, cost = calculate_ciou(box_a, box_b)
    assert abs(ciou - 1.0) < 1e-4
    assert abs(cost - 0.0) < 1e-4


def test_shifted_box_ciou():
    box_a = {"x": 100, "y": 100, "width": 100, "height": 100}
    box_b = {"x": 120, "y": 100, "width": 100, "height": 100}
    ciou, cost = calculate_ciou(box_a, box_b)
    assert ciou < 1.0
    assert cost > 0.0
    assert 0.0 <= cost <= 1.0


def test_displacement_calculation():
    box_a = {"x": 100, "y": 100, "width": 100, "height": 50}
    box_b = {"x": 130, "y": 140, "width": 100, "height": 50}
    disp = calculate_displacement(box_a, box_b)
    assert disp["dx"] == 30.0
    assert disp["dy"] == 40.0
    assert disp["distance"] == 50.0

