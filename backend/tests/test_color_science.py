"""
Unit tests for CIE L*a*b* conversion, Delta E, and WCAG contrast.
"""

import pytest
from app.core.color_science import (
    parse_css_color,
    rgb_to_lab,
    calculate_delta_e,
    calculate_contrast_ratio
)


def test_parse_css_color():
    assert parse_css_color("#FFFFFF") == (255, 255, 255, 1.0)
    assert parse_css_color("#000000") == (0, 0, 0, 1.0)
    assert parse_css_color("rgb(16, 185, 129)") == (16, 185, 129, 1.0)
    assert parse_css_color("rgba(37, 99, 235, 0.5)") == (37, 99, 235, 0.5)


def test_identical_color_delta_e():
    delta_e, cost = calculate_delta_e("#2563EB", "#2563EB")
    assert delta_e == 0.0
    assert cost == 0.0


def test_distinct_color_delta_e():
    # Blue vs Red
    delta_e, cost = calculate_delta_e("#2563EB", "#DC2626")
    assert delta_e > 40.0
    assert cost > 0.40


def test_wcag_contrast_black_on_white():
    contrast = calculate_contrast_ratio("#000000", "#FFFFFF")
    assert abs(contrast - 21.0) < 0.1


def test_wcag_contrast_low():
    # Low contrast: dark grey on black
    contrast = calculate_contrast_ratio("#1E293B", "#0F172A")
    assert contrast < 2.0

