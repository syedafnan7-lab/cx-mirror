"""
CX MIRROR — Preset Service
Defines metadata, HTML templates, and mutation logic for the five sandbox presets.
"""

from typing import Dict, Any, List
from app.models.schemas import PresetResponse

PRESETS: Dict[str, Dict[str, Any]] = {
    "clean": {
        "name": "clean",
        "title": "Baseline Golden Standard",
        "description": "Pixel-perfect implementation matching design geometry, typography, and active $24.99 SKU contract.",
        "defects_introduced": [],
        "expected_verdict": "PASS",
        "sku": "SKU-AURORA-PRO-X",
        "product_name": "Aurora Pro Wireless Noise-Cancelling Headphones",
        "current_price": "$24.99",
        "original_price": "$39.99",
        "discount_badge": "38% OFF",
        "legal_text": "Terms apply. All sales final on promotional bundles. 30-day limited warranty included. See return policy for details."
    },
    "drifted": {
        "name": "drifted",
        "title": "Geometric Layout & Color Drift",
        "description": "Summary card shifted right (+28px, +22px), CTA button changed to Purple (#9333EA), font size reduced to 20px.",
        "defects_introduced": [
            "Order summary card translated 28px X, 22px Y",
            "Checkout button background color shifted to #9333EA (Delta E ~38)",
            "Checkout button height collapsed to 40px",
            "Product title font size decreased from 28px to 20px",
            "Current price shifted color to amber (#F59E0B)"
        ],
        "expected_verdict": "FAIL",
        "sku": "SKU-AURORA-PRO-X",
        "product_name": "Aurora Pro Wireless Noise-Cancelling Headphones",
        "current_price": "$24.99",
        "original_price": "$39.99",
        "discount_badge": "38% OFF",
        "legal_text": "Terms apply. All sales final on promotional bundles. 30-day limited warranty included. See return policy for details."
    },
    "price_bug": {
        "name": "price_bug",
        "title": "Critical Business Contract Failure (Wrong Price)",
        "description": "Live checkout charges $19.99 instead of contracted $24.99. Visually attractive but critical revenue/contract defect.",
        "defects_introduced": [
            "Checkout unit price rendered as $19.99 instead of $24.99 catalog contract",
            "Subtotal and total reflect incorrect $19.99 price",
            "Breaches CONTRACT-PRICE-001 (CRITICAL)"
        ],
        "expected_verdict": "FAIL",
        "sku": "SKU-AURORA-PRO-X",
        "product_name": "Aurora Pro Wireless Noise-Cancelling Headphones",
        "current_price": "$19.99",
        "original_price": "$39.99",
        "discount_badge": "38% OFF",
        "legal_text": "Terms apply. All sales final on promotional bundles. 30-day limited warranty included. See return policy for details."
    },
    "legal_hidden": {
        "name": "legal_hidden",
        "title": "Statutory Disclaimer Hidden / Illegible",
        "description": "Mandatory 30-day warranty and terms disclaimer rendered at 5px font size with 0.05 opacity (fails WCAG AA 1.1:1).",
        "defects_introduced": [
            "Legal disclaimer font-size reduced to 5px (below 11px statutory limit)",
            "Disclaimer opacity reduced to 0.05 (invisible to consumer)",
            "WCAG AA contrast ratio collapsed to 1.1:1 (breaches 4.5:1 requirement)",
            "Breaches CONTRACT-LEGAL-001, CONTRACT-LEGAL-002, CONTRACT-CONTRAST-001"
        ],
        "expected_verdict": "FAIL",
        "sku": "SKU-AURORA-PRO-X",
        "product_name": "Aurora Pro Wireless Noise-Cancelling Headphones",
        "current_price": "$24.99",
        "original_price": "$39.99",
        "discount_badge": "38% OFF",
        "legal_text": "Terms apply. All sales final on promotional bundles. 30-day limited warranty included. See return policy for details."
    },
    "all_bugs": {
        "name": "all_bugs",
        "title": "Compounded Defect Chaos",
        "description": "Combines geometric translation (+34px, +26px), altered CTA button, incorrect $18.50 price, and hidden disclaimer.",
        "defects_introduced": [
            "Severe geometric layout shift",
            "CTA button color shifted to Crimson (#DC2626) and height collapsed",
            "Price altered to $18.50",
            "Legal disclaimer rendered transparent at 5px",
            "Multiple simultaneous contract and visual regressions"
        ],
        "expected_verdict": "FAIL",
        "sku": "SKU-AURORA-PRO-X",
        "product_name": "Aurora Pro Wireless Noise-Cancelling Headphones",
        "current_price": "$18.50",
        "original_price": "$39.99",
        "discount_badge": "38% OFF",
        "legal_text": "Terms apply. All sales final on promotional bundles. 30-day limited warranty included. See return policy for details."
    }
}


def get_all_presets() -> List[PresetResponse]:
    return [
        PresetResponse(
            name=p["name"],
            title=p["title"],
            description=p["description"],
            defects_introduced=p["defects_introduced"],
            expected_verdict=p["expected_verdict"]
        )
        for p in PRESETS.values()
    ]


def get_preset(name: str) -> Dict[str, Any]:
    return PRESETS.get(name.lower(), PRESETS["clean"])

