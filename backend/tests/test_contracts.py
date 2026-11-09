"""
Unit tests for reference contracts validation.
"""

from app.models.graph_models import GraphNode, BoundingBox
from app.core.contract_validator import validate_contracts


def test_contract_price_pass():
    dom_nodes = {
        "price_el": GraphNode(
            id="price_el",
            element_type="price",
            role="current_price",
            text="$24.99",
            bounding_box=BoundingBox(x=100, y=100, width=80, height=30)
        )
    }
    ref_data = {
        "contracts": [
            {
                "id": "CONTRACT-PRICE-001",
                "name": "Price Check",
                "target_role": "current_price",
                "rule": "exact_or_numeric_match",
                "expected_value": "$24.99",
                "criticality": "CRITICAL"
            }
        ]
    }
    results = validate_contracts(dom_nodes, ref_data)
    assert len(results) == 1
    assert results[0].status == "PASS"


def test_contract_price_fail():
    dom_nodes = {
        "price_el": GraphNode(
            id="price_el",
            element_type="price",
            role="current_price",
            text="$19.99",  # Buggy price
            bounding_box=BoundingBox(x=100, y=100, width=80, height=30)
        )
    }
    ref_data = {
        "contracts": [
            {
                "id": "CONTRACT-PRICE-001",
                "name": "Price Check",
                "target_role": "current_price",
                "rule": "exact_or_numeric_match",
                "expected_value": "$24.99",
                "criticality": "CRITICAL"
            }
        ]
    }
    results = validate_contracts(dom_nodes, ref_data)
    assert len(results) == 1
    assert results[0].status == "FAIL"
    assert results[0].severity == "CRITICAL"

