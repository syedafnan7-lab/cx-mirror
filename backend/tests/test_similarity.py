"""
Unit tests for text similarity and windowed SSIM.
"""

import numpy as np
import pytest
from app.core.similarity import (
    normalize_text,
    calculate_token_similarity,
    calculate_character_similarity,
    calculate_text_similarity,
    calculate_ssim
)


def test_normalize_text():
    raw = "  Order \t\n Summary   "
    assert normalize_text(raw) == "Order Summary"


def test_token_similarity_exact():
    assert calculate_token_similarity("Terms apply. All sales final.", "Terms apply. All sales final.") == 1.0


def test_token_similarity_partial():
    sim = calculate_token_similarity("Proceed to Express Checkout", "Proceed to Checkout")
    assert 0.6 <= sim < 1.0


def test_ssim_identical_images():
    img1 = np.ones((64, 64, 3), dtype=np.uint8) * 128
    img2 = np.ones((64, 64, 3), dtype=np.uint8) * 128
    raw_ssim, cost = calculate_ssim(img1, img2)
    assert abs(raw_ssim - 1.0) < 1e-4
    assert cost == 0.0


def test_ssim_different_images():
    img1 = np.zeros((64, 64, 3), dtype=np.uint8)
    img2 = np.ones((64, 64, 3), dtype=np.uint8) * 255
    raw_ssim, cost = calculate_ssim(img1, img2)
    assert raw_ssim < 0.2
    assert cost > 0.4

