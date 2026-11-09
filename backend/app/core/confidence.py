"""
CX MIRROR — Confidence and Scoring Engine
Calculates multi-modal visual score S_visual, structural score S_structure,
contract score S_contract, and composite decision S_total.
Never hardcodes confidence scores.
"""

from typing import List, Dict, Any, Tuple
from app.models.graph_models import MatchedPair, ContractResult, Discrepancy, GraphNode
from app.models.schemas import AnalysisScores, AnalysisSummary


def compute_confidence_scores(
    matched_pairs: List[MatchedPair],
    unmatched_mockup: List[str],
    unmatched_dom: List[str],
    mockup_nodes: Dict[str, GraphNode],
    dom_nodes: Dict[str, GraphNode],
    contracts: List[ContractResult],
    threshold: float = 95.0
) -> Tuple[str, float, AnalysisScores, AnalysisSummary, List[Discrepancy]]:
    """
    Computes exact mathematical scores and PASS/FAIL verdict.
    
    Formula:
      S_visual = 100 * sum(a_i * Q_i) / sum(a_i)
      S_structure = 100 * (1 - normalized_penalty)
      S_contract = 100 * (passed_contracts / total_contracts)
      S_total = 0.60 * S_visual + 0.15 * S_structure + 0.25 * S_contract
      
    Verdict: PASS if S_total >= threshold AND all critical contracts pass.
    """
    discrepancies: List[Discrepancy] = []

    # 1. Visual Score Calculation
    total_weighted_quality = 0.0
    total_weights = 0.0

    for pair in matched_pairs:
        a_i = pair.importance
        q_i = pair.quality_score
        total_weighted_quality += a_i * q_i
        total_weights += a_i

        m_node = mockup_nodes.get(pair.mockup_node_id)
        d_node = dom_nodes.get(pair.dom_node_id)

        # Detect Geometry Discrepancy
        if pair.displacement.distance > 8.0 or pair.ciou < 0.65:
            severity = "CRITICAL" if a_i >= 3.0 else ("MAJOR" if a_i >= 2.0 else "MINOR")
            discrepancies.append(Discrepancy(
                node_id=pair.mockup_node_id,
                category="geometry",
                severity=severity,
                expected={"x": m_node.bounding_box.x if m_node else 0, "y": m_node.bounding_box.y if m_node else 0, "w": m_node.bounding_box.width if m_node else 0, "h": m_node.bounding_box.height if m_node else 0},
                actual={"x": d_node.bounding_box.x if d_node else 0, "y": d_node.bounding_box.y if d_node else 0, "w": d_node.bounding_box.width if d_node else 0, "h": d_node.bounding_box.height if d_node else 0},
                difference=f"Displacement: {pair.displacement.distance}px (dx={pair.displacement.dx}px, dy={pair.displacement.dy}px), CIoU={pair.ciou:.3f}",
                confidence=pair.match_confidence,
                explanation=f"Element shifted by {pair.displacement.distance}px from mockup position."
            ))

        # Detect Color Discrepancy
        if pair.delta_e > 6.0:
            severity = "MAJOR" if a_i >= 2.0 else "MINOR"
            discrepancies.append(Discrepancy(
                node_id=pair.mockup_node_id,
                category="color",
                severity=severity,
                expected=m_node.color if m_node else "#000000",
                actual=d_node.color if d_node else "#000000",
                difference=f"CIE LAB Delta E: {pair.delta_e:.1f} (Threshold 6.0)",
                confidence=pair.match_confidence,
                explanation=f"Perceptual color drift exceeds JND (Delta E = {pair.delta_e:.1f})."
            ))

        # Detect Typography Discrepancy
        if m_node and d_node and m_node.font_size and d_node.font_size:
            diff_fs = abs(m_node.font_size - d_node.font_size)
            if diff_fs > 2.0:
                severity = "MAJOR" if a_i >= 2.0 else "MINOR"
                discrepancies.append(Discrepancy(
                    node_id=pair.mockup_node_id,
                    category="typography",
                    severity=severity,
                    expected=f"{m_node.font_size}px",
                    actual=f"{d_node.font_size}px",
                    difference=f"Font size delta: {diff_fs:.1f}px",
                    confidence=pair.match_confidence,
                    explanation=f"Font size altered from mockup {m_node.font_size}px to {d_node.font_size}px."
                ))

        # Detect Text Content Discrepancy
        if pair.text_sim < 0.85 and (m_node and m_node.text):
            severity = "CRITICAL" if a_i >= 3.0 else ("MAJOR" if a_i >= 2.0 else "MINOR")
            discrepancies.append(Discrepancy(
                node_id=pair.mockup_node_id,
                category="text",
                severity=severity,
                expected=m_node.text,
                actual=d_node.text if d_node else "",
                difference=f"Text similarity: {pair.text_sim * 100:.1f}%",
                confidence=pair.match_confidence,
                explanation=f"Content difference in {pair.semantic_role}."
            ))

    # Account for unmatched mockup nodes (missing elements in implementation)
    for m_id in unmatched_mockup:
        m_node = mockup_nodes.get(m_id)
        if m_node:
            total_weights += m_node.importance
            # Q_i for missing element is 0.0
            severity = "CRITICAL" if m_node.importance >= 3.0 else ("MAJOR" if m_node.importance >= 2.0 else "MINOR")
            discrepancies.append(Discrepancy(
                node_id=m_id,
                category="missing_element",
                severity=severity,
                expected=f"Present in design ({m_node.role or m_node.element_type})",
                actual="Missing from live DOM",
                difference="Element not implemented",
                confidence=1.0,
                explanation=f"Mandatory mockup element '{m_id}' not found in rendered DOM."
            ))

    if total_weights > 0:
        s_visual = 100.0 * (total_weighted_quality / total_weights)
    else:
        s_visual = 0.0

    # 2. Structural Score Calculation
    structural_penalties = 0.0
    # Penalty for unmatched nodes
    if mockup_nodes:
        structural_penalties += (len(unmatched_mockup) / len(mockup_nodes)) * 0.50
    # Penalty for large displacements
    displaced_count = sum(1 for p in matched_pairs if p.displacement.distance > 15.0)
    if matched_pairs:
        structural_penalties += (displaced_count / len(matched_pairs)) * 0.50

    s_structure = max(0.0, min(100.0, 100.0 * (1.0 - structural_penalties)))

    # 3. Business Contract Score Calculation
    total_contracts = len(contracts)
    passed_contracts = sum(1 for c in contracts if c.status == "PASS")
    critical_failures = sum(1 for c in contracts if c.status == "FAIL" and c.severity == "CRITICAL")

    # Add contract failures to discrepancies list
    for c in contracts:
        if c.status == "FAIL":
            discrepancies.append(Discrepancy(
                node_id=c.contract_id,
                category="business_contract",
                severity=c.severity,
                expected=c.expected,
                actual=c.actual,
                difference=c.evidence,
                confidence=1.0,
                explanation=c.explanation
            ))

    if total_contracts > 0:
        s_contract = 100.0 * (passed_contracts / total_contracts)
    else:
        s_contract = 100.0

    # 4. Total Composite Score
    s_total = (0.60 * s_visual) + (0.15 * s_structure) + (0.25 * s_contract)
    s_total = max(0.0, min(100.0, s_total))

    # Decision rule: S_total >= threshold AND zero critical contract failures
    verdict = "PASS" if (s_total >= threshold and critical_failures == 0) else "FAIL"

    scores = AnalysisScores(
        visual=round(s_visual, 2),
        structural=round(s_structure, 2),
        contract=round(s_contract, 2),
        total=round(s_total, 2)
    )

    summary = AnalysisSummary(
        total_mockup_nodes=len(mockup_nodes),
        total_dom_nodes=len(dom_nodes),
        matched_nodes=len(matched_pairs),
        unmatched_mockup_nodes=len(unmatched_mockup),
        unmatched_dom_nodes=len(unmatched_dom),
        discrepancies=len(discrepancies),
        critical_failures=critical_failures
    )

    return verdict, round(s_total, 2), scores, summary, discrepancies

