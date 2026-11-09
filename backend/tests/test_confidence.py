"""
Unit tests for confidence calculation and critical contract overrides.
"""

from app.models.graph_models import MatchedPair, Displacement, ContractResult, GraphNode, BoundingBox
from app.core.confidence import compute_confidence_scores


def test_confidence_clean_pass():
    matched_pairs = [
        MatchedPair(
            mockup_node_id="m1",
            dom_node_id="d1",
            semantic_role="checkout_button",
            importance=2.0,
            c_geometry=0.01,
            ciou=0.98,
            c_ssim=0.02,
            raw_ssim=0.96,
            c_color=0.01,
            delta_e=1.0,
            c_text=0.0,
            text_sim=1.0,
            displacement=Displacement(dx=1.0, dy=1.0, distance=1.41),
            match_confidence=0.98,
            quality_score=0.98
        )
    ]
    contracts = [
        ContractResult(
            contract_id="C1",
            name="Price Check",
            status="PASS",
            severity="CRITICAL",
            expected="$24.99",
            actual="$24.99",
            evidence="OK",
            explanation="Matches"
        )
    ]
    nodes = {
        "m1": GraphNode(
            id="m1",
            element_type="button",
            bounding_box=BoundingBox(x=10, y=10, width=100, height=40)
        )
    }

    verdict, conf, scores, summary, discrepancies = compute_confidence_scores(
        matched_pairs=matched_pairs,
        unmatched_mockup=[],
        unmatched_dom=[],
        mockup_nodes=nodes,
        dom_nodes=nodes,
        contracts=contracts,
        threshold=95.0
    )

    assert verdict == "PASS"
    assert conf >= 95.0
    assert summary.critical_failures == 0


def test_critical_contract_forces_fail():
    matched_pairs = [
        MatchedPair(
            mockup_node_id="m1",
            dom_node_id="d1",
            semantic_role="price",
            importance=3.0,
            c_geometry=0.0,
            ciou=1.0,
            c_ssim=0.0,
            raw_ssim=1.0,
            c_color=0.0,
            delta_e=0.0,
            c_text=0.0,
            text_sim=1.0,
            displacement=Displacement(dx=0.0, dy=0.0, distance=0.0),
            match_confidence=1.0,
            quality_score=1.0
        )
    ]
    contracts = [
        ContractResult(
            contract_id="C1",
            name="Price Check",
            status="FAIL",
            severity="CRITICAL",  # CRITICAL FAILURE
            expected="$24.99",
            actual="$19.99",
            evidence="Mismatch",
            explanation="Business price violation"
        )
    ]
    nodes = {
        "m1": GraphNode(
            id="m1",
            element_type="price",
            bounding_box=BoundingBox(x=10, y=10, width=50, height=20)
        )
    }

    verdict, conf, scores, summary, discrepancies = compute_confidence_scores(
        matched_pairs=matched_pairs,
        unmatched_mockup=[],
        unmatched_dom=[],
        mockup_nodes=nodes,
        dom_nodes=nodes,
        contracts=contracts,
        threshold=50.0  # Even with very low threshold, must FAIL!
    )

    assert verdict == "FAIL"
    assert summary.critical_failures == 1

