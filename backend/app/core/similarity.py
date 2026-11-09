"""
CX MIRROR — Similarity Module
Implements windowed Structural Similarity (SSIM) between aligned image regions,
and Unicode/token-aware text similarity metrics.
"""

import unicodedata
import re
from typing import Tuple, Dict, Any, Union
import numpy as np
import cv2

try:
    from skimage.metrics import structural_similarity as skimage_ssim
except ImportError:
    skimage_ssim = None


def normalize_text(text: str) -> str:
    """Normalize text using Unicode NFKC normalization and collapse whitespace."""
    if not text:
        return ""
    text = unicodedata.normalize('NFKC', str(text))
    # Replace multiple whitespace with a single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def calculate_token_similarity(text_a: str, text_b: str) -> float:
    """Calculate token Jaccard similarity between two strings."""
    norm_a = normalize_text(text_a).lower()
    norm_b = normalize_text(text_b).lower()

    if not norm_a and not norm_b:
        return 1.0
    if not norm_a or not norm_b:
        return 0.0

    tokens_a = set(re.findall(r'\b\w+\b', norm_a))
    tokens_b = set(re.findall(r'\b\w+\b', norm_b))

    if not tokens_a and not tokens_b:
        return 1.0 if norm_a == norm_b else 0.0

    intersection = tokens_a.intersection(tokens_b)
    union = tokens_a.union(tokens_b)

    return len(intersection) / max(1, len(union))


def calculate_character_similarity(text_a: str, text_b: str) -> float:
    """Calculate Levenshtein ratio between normalized strings."""
    norm_a = normalize_text(text_a)
    norm_b = normalize_text(text_b)

    if norm_a == norm_b:
        return 1.0
    if not norm_a or not norm_b:
        return 0.0

    len_a, len_b = len(norm_a), len(norm_b)
    # Fast DP Levenshtein distance
    dp = [[0] * (len_b + 1) for _ in range(len_a + 1)]
    for i in range(len_a + 1):
        dp[i][0] = i
    for j in range(len_b + 1):
        dp[0][j] = j

    for i in range(1, len_a + 1):
        for j in range(1, len_b + 1):
            cost = 0 if norm_a[i - 1] == norm_b[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,       # deletion
                dp[i][j - 1] + 1,       # insertion
                dp[i - 1][j - 1] + cost # substitution
            )

    dist = dp[len_a][len_b]
    max_len = max(len_a, len_b)
    return 1.0 - (dist / max_len)


def calculate_text_similarity(text_a: str, text_b: str) -> Tuple[float, float]:
    """
    Combined character and token similarity.
    Returns:
      (similarity_score in [0, 1], c_text in [0, 1])
    """
    if text_a is None and text_b is None:
        return 1.0, 0.0
    if text_a is None or text_b is None:
        return 0.0, 1.0

    char_sim = calculate_character_similarity(text_a, text_b)
    token_sim = calculate_token_similarity(text_a, text_b)

    # 60% character similarity + 40% token similarity
    sim = 0.60 * char_sim + 0.40 * token_sim
    c_text = 1.0 - sim

    return sim, c_text


def calculate_ssim(
    image_a: np.ndarray, 
    image_b: np.ndarray,
    target_size: Tuple[int, int] = (64, 64)
) -> Tuple[float, float]:
    """
    Calculate windowed SSIM on two image regions.
    Normalizes sizes and converts to grayscale.
    
    Formula:
      SSIM = ((2*mu_x*mu_y + C1)*(2*sigma_xy + C2)) / ((mu_x^2 + mu_y^2 + C1)*(sigma_x^2 + sigma_y^2 + C2))
      C_ssim = (1 - clamp(SSIM, -1, 1)) / 2
      
    Returns:
      (raw_ssim, c_ssim)
    """
    if image_a is None or image_b is None or image_a.size == 0 or image_b.size == 0:
        return 0.0, 1.0

    # Convert to grayscale if 3-channel
    if len(image_a.shape) == 3:
        gray_a = cv2.cvtColor(image_a, cv2.COLOR_BGR2GRAY if image_a.shape[2] == 3 else cv2.COLOR_BGRA2GRAY)
    else:
        gray_a = image_a

    if len(image_b.shape) == 3:
        gray_b = cv2.cvtColor(image_b, cv2.COLOR_BGR2GRAY if image_b.shape[2] == 3 else cv2.COLOR_BGRA2GRAY)
    else:
        gray_b = image_b

    # Resize both to standard target size for consistent windowed evaluation
    h, w = target_size
    resized_a = cv2.resize(gray_a, (w, h), interpolation=cv2.INTER_AREA)
    resized_b = cv2.resize(gray_b, (w, h), interpolation=cv2.INTER_AREA)

    if skimage_ssim is not None:
        raw_ssim = float(skimage_ssim(resized_a, resized_b, data_range=255))
    else:
        # Deterministic fallback implementation of Wang et al. SSIM
        img1 = resized_a.astype(np.float64)
        img2 = resized_b.astype(np.float64)
        c1 = (0.01 * 255) ** 2
        c2 = (0.03 * 255) ** 2

        mu1 = cv2.GaussianBlur(img1, (11, 11), 1.5)
        mu2 = cv2.GaussianBlur(img2, (11, 11), 1.5)

        mu1_sq = mu1 ** 2
        mu2_sq = mu2 ** 2
        mu1_mu2 = mu1 * mu2

        sigma1_sq = cv2.GaussianBlur(img1 ** 2, (11, 11), 1.5) - mu1_sq
        sigma2_sq = cv2.GaussianBlur(img2 ** 2, (11, 11), 1.5) - mu2_sq
        sigma12 = cv2.GaussianBlur(img1 * img2, (11, 11), 1.5) - mu1_mu2

        num = (2 * mu1_mu2 + c1) * (2 * sigma12 + c2)
        den = (mu1_sq + mu2_sq + c1) * (sigma1_sq + sigma2_sq + c2)
        ssim_map = num / (den + 1e-7)
        raw_ssim = float(np.mean(ssim_map))

    raw_ssim = max(-1.0, min(1.0, raw_ssim))
    c_ssim = (1.0 - raw_ssim) / 2.0
    c_ssim = max(0.0, min(1.0, c_ssim))

    return raw_ssim, c_ssim

