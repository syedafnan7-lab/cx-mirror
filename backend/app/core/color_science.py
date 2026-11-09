"""
CX MIRROR — Color Science Module
Implements sRGB to CIE L*a*b* conversion (D65 illuminant), Delta E (CIE76),
and WCAG 2.1 contrast ratio calculations without approximations.
"""

import math
import re
from typing import Tuple, Dict, Any, Union


def parse_css_color(color_str: str) -> Tuple[int, int, int, float]:
    """
    Parse CSS color strings (hex, rgb, rgba) into (R, G, B, Alpha).
    Returns (0-255, 0-255, 0-255, 0.0-1.0).
    """
    color_str = color_str.strip().lower()

    # Hex formats: #RGB, #RGBA, #RRGGBB, #RRGGBBAA
    if color_str.startswith('#'):
        hex_val = color_str[1:]
        if len(hex_val) == 3:
            r = int(hex_val[0] * 2, 16)
            g = int(hex_val[1] * 2, 16)
            b = int(hex_val[2] * 2, 16)
            return r, g, b, 1.0
        elif len(hex_val) == 4:
            r = int(hex_val[0] * 2, 16)
            g = int(hex_val[1] * 2, 16)
            b = int(hex_val[2] * 2, 16)
            a = int(hex_val[3] * 2, 16) / 255.0
            return r, g, b, a
        elif len(hex_val) == 6:
            r = int(hex_val[0:2], 16)
            g = int(hex_val[2:4], 16)
            b = int(hex_val[4:6], 16)
            return r, g, b, 1.0
        elif len(hex_val) == 8:
            r = int(hex_val[0:2], 16)
            g = int(hex_val[2:4], 16)
            b = int(hex_val[4:6], 16)
            a = int(hex_val[6:8], 16) / 255.0
            return r, g, b, a

    # rgb(...) or rgba(...)
    rgba_match = re.match(r'rgba?\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(?:\s*,\s*([\d.]+))?\s*\)', color_str)
    if rgba_match:
        r = int(rgba_match.group(1))
        g = int(rgba_match.group(2))
        b = int(rgba_match.group(3))
        a = float(rgba_match.group(4)) if rgba_match.group(4) is not None else 1.0
        return r, g, b, a

    # Common named colors fallback
    named_colors = {
        'black': (0, 0, 0, 1.0),
        'white': (255, 255, 255, 1.0),
        'transparent': (0, 0, 0, 0.0),
        'red': (255, 0, 0, 1.0),
        'green': (0, 128, 0, 1.0),
        'blue': (0, 0, 255, 1.0),
    }
    return named_colors.get(color_str, (0, 0, 0, 1.0))


def srgb_to_linear(c_srgb: float) -> float:
    """Convert an 8-bit channel (0-1) from sRGB gamma to linear RGB."""
    if c_srgb <= 0.04045:
        return c_srgb / 12.92
    return ((c_srgb + 0.055) / 1.055) ** 2.4


def rgb_to_xyz(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """Convert 8-bit sRGB to CIE XYZ under standard illuminant D65."""
    r_lin = srgb_to_linear(r / 255.0)
    g_lin = srgb_to_linear(g / 255.0)
    b_lin = srgb_to_linear(b / 255.0)

    # Standard sRGB to XYZ (D65) transformation matrix
    x = r_lin * 0.4124564 + g_lin * 0.3575761 + b_lin * 0.1804375
    y = r_lin * 0.2126729 + g_lin * 0.7151522 + b_lin * 0.0721750
    z = r_lin * 0.0193339 + g_lin * 0.1191920 + b_lin * 0.9503041

    return x, y, z


def xyz_to_lab(x: float, y: float, z: float) -> Tuple[float, float, float]:
    """
    Convert CIE XYZ to CIE L*a*b* using standard D65 reference white point:
    X_n = 0.95047, Y_n = 1.00000, Z_n = 1.08883.
    """
    xn, yn, zn = 0.95047, 1.00000, 1.08883

    def f(t: float) -> float:
        delta = 6.0 / 29.0
        if t > delta ** 3:
            return t ** (1.0 / 3.0)
        return (t / (3.0 * delta ** 2)) + (4.0 / 29.0)

    fx = f(x / xn)
    fy = f(y / yn)
    fz = f(z / zn)

    l_star = 116.0 * fy - 16.0
    a_star = 500.0 * (fx - fy)
    b_star = 200.0 * (fy - fz)

    return l_star, a_star, b_star


def rgb_to_lab(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """Convenience helper: 8-bit sRGB directly to CIE L*a*b*."""
    x, y, z = rgb_to_xyz(r, g, b)
    return xyz_to_lab(x, y, z)


def calculate_delta_e(
    color_a: Union[str, Tuple[int, int, int]], 
    color_b: Union[str, Tuple[int, int, int]]
) -> Tuple[float, float]:
    """
    Calculate CIE76 Delta E between two colors and normalized cost.
    Input colors can be CSS strings (#hex, rgb) or (r, g, b) tuples.
    
    Formula:
      Delta E_ab = sqrt((L1 - L2)^2 + (a1 - a2)^2 + (b1 - b2)^2)
      C_color = min(Delta E_ab / 100.0, 1.0)
      
    Returns:
      (delta_e, c_color)
    """
    if isinstance(color_a, str):
        ra, ga, ba, _ = parse_css_color(color_a)
    else:
        ra, ga, ba = color_a[:3]

    if isinstance(color_b, str):
        rb, gb, bb, _ = parse_css_color(color_b)
    else:
        rb, gb, bb = color_b[:3]

    l1, a1, b1 = rgb_to_lab(ra, ga, ba)
    l2, a2, b2 = rgb_to_lab(rb, gb, bb)

    delta_e = math.sqrt((l1 - l2) ** 2 + (a1 - a2) ** 2 + (b1 - b2) ** 2)
    c_color = min(delta_e / 100.0, 1.0)

    return delta_e, c_color


def calculate_relative_luminance(r: int, g: int, b: int) -> float:
    """Calculate WCAG 2.1 relative luminance for an 8-bit sRGB color."""
    r_lin = srgb_to_linear(r / 255.0)
    g_lin = srgb_to_linear(g / 255.0)
    b_lin = srgb_to_linear(b / 255.0)
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def calculate_contrast_ratio(
    foreground: Union[str, Tuple[int, int, int]], 
    background: Union[str, Tuple[int, int, int]]
) -> float:
    """
    Calculate WCAG 2.1 contrast ratio:
      (L1 + 0.05) / (L2 + 0.05) where L1 >= L2
    Returns value in range [1.0, 21.0].
    """
    if isinstance(foreground, str):
        rf, gf, bf, _ = parse_css_color(foreground)
    else:
        rf, gf, bf = foreground[:3]

    if isinstance(background, str):
        rb, gb, bb, _ = parse_css_color(background)
    else:
        rb, gb, bb = background[:3]

    lum_f = calculate_relative_luminance(rf, gf, bf)
    lum_b = calculate_relative_luminance(rb, gb, bb)

    l1 = max(lum_f, lum_b)
    l2 = min(lum_f, lum_b)

    return (l1 + 0.05) / (l2 + 0.05)

