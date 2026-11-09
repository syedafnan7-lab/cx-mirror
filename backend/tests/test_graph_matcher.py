"""
Unit tests for Hungarian graph matching and semantic penalties.
"""

from app.models.graph_models import GraphNode, BoundingBox
from app.core.graph_matcher import match_spatial_graphs, compute_semantic_penalty


def test_semantic_penalty():
    node_price = GraphNode(
        id="m_p",
        element_type="price",
        role="current_price",
        text="$24.99",
        bounding_box=BoundingBox(x=10, y=10, width=50, height=20)
    )
    node_legal = GraphNode(
        id="d_l",
        element_type="legal",
        role="legal_disclaimer",
        text="Terms apply",
        bounding_box=BoundingBox(x=10, y=10, width=50, height=20)
    )
    penalty = compute_semantic_penalty(node_price, node_legal)
    assert penalty >= 0.80  # Strict role mismatch penalty


def test_hungarian_bipartite_matching():
    mockup_nodes = {
        "m_btn": GraphNode(
            id="m_btn",
            element_type="button",
            role="checkout_button",
            text="Checkout",
            bounding_box=BoundingBox(x=100, y=500, width=200, height=50)
        ),
        "m_price": GraphNode(
            id="m_price",
            element_type="price",
            role="current_price",
            text="$24.99",
            bounding_box=BoundingBox(x=100, y=200, width=80, height=30)
        )
    }

    dom_nodes = {
        "d_btn": GraphNode(
            id="d_btn",
            element_type="button",
            role="checkout_button",
            text="Checkout",
            bounding_box=BoundingBox(x=102, y=501, width=200, height=50)
        ),
        "d_price": GraphNode(
            id="d_price",
            element_type="price",
            role="current_price",
            text="$24.99",
            bounding_box=BoundingBox(x=101, y=202, width=80, height=30)
        )
    }

    matches, unmatched_m, unmatched_d = match_spatial_graphs(mockup_nodes, dom_nodes)
    assert len(matches) == 2
    assert len(unmatched_m) == 0
    assert len(unmatched_d) == 0

    match_dict = {p.mockup_node_id: p.dom_node_id for p in matches}
    assert match_dict["m_btn"] == "d_btn"
    assert match_dict["m_price"] == "d_price"

