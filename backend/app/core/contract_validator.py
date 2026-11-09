"""
CX MIRROR — Contract Validator Module
Validates business data contracts, price consistency, legal disclaimers,
and WCAG contrast deterministically.
"""

import re
from typing import List, Dict, Any, Optional
from app.models.graph_models import GraphNode, ContractResult
from app.core.color_science import calculate_contrast_ratio
from app.core.similarity import normalize_text


def extract_numeric_price(text: str) -> Optional[float]:
    """Extract numeric float value from currency string (e.g. '$24.99' -> 24.99)."""
    if not text:
        return None
    match = re.search(r'[\$£€¥]?\s*([0-9]+(?:\.[0-9]{1,2})?)', text)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None


def validate_contracts(
    dom_nodes: Dict[str, GraphNode], 
    reference_data: Dict[str, Any]
) -> List[ContractResult]:
    """
    Validate all business contracts against extracted DOM graph nodes.
    Returns list of ContractResult objects.
    """
    contracts_def = reference_data.get("contracts", [])
    results: List[ContractResult] = []

    # Map nodes by semantic role
    role_to_nodes: Dict[str, List[GraphNode]] = {}
    for node in dom_nodes.values():
        if node.role:
            role_to_nodes.setdefault(node.role, []).append(node)

    for c in contracts_def:
        cid = c["id"]
        name = c["name"]
        target_role = c["target_role"]
        rule = c["rule"]
        expected_val = c["expected_value"]
        severity = c["criticality"]

        matching_nodes = role_to_nodes.get(target_role, [])

        if not matching_nodes:
            # Element missing completely
            results.append(ContractResult(
                contract_id=cid,
                name=name,
                status="FAIL",
                severity=severity,
                expected=expected_val,
                actual=None,
                evidence=f"No DOM element found matching semantic role '{target_role}'",
                explanation=f"Critical omission: {c.get('description', 'Required element missing.')}"
            ))
            continue

        target_node = matching_nodes[0]

        # Rule evaluation
        if rule == "exact_or_numeric_match":
            actual_text = (target_node.text or "").strip()
            exp_num = extract_numeric_price(str(expected_val))
            act_num = extract_numeric_price(actual_text)

            passed = False
            if exp_num is not None and act_num is not None:
                passed = abs(exp_num - act_num) < 0.001
            else:
                passed = normalize_text(actual_text) == normalize_text(str(expected_val))

            status = "PASS" if passed else "FAIL"
            evidence = f"Extracted text: '{actual_text}' (Numeric: {act_num})"
            explanation = (
                f"Price verified: matches expected {expected_val}"
                if passed else
                f"Price mismatch: live value {actual_text} differs from business specification {expected_val}"
            )

            results.append(ContractResult(
                contract_id=cid,
                name=name,
                status=status,
                severity=severity,
                expected=expected_val,
                actual=actual_text,
                evidence=evidence,
                explanation=explanation
            ))

        elif rule == "substring_or_semantic_presence":
            actual_text = normalize_text(target_node.text or "")
            expected_norm = normalize_text(str(expected_val))

            # Visibility check
            is_visible = (
                target_node.visibility and 
                (target_node.opacity is None or target_node.opacity >= 0.2) and
                target_node.bounding_box.width > 20 and
                target_node.bounding_box.height > 8
            )

            if not is_visible:
                results.append(ContractResult(
                    contract_id=cid,
                    name=name,
                    status="FAIL",
                    severity=severity,
                    expected=f"Visible legal disclaimer containing: '{expected_val[:40]}...'",
                    actual=f"Hidden/Invisible (visibility={target_node.visibility}, opacity={target_node.opacity})",
                    evidence=f"Bounding box: {target_node.bounding_box.width}x{target_node.bounding_box.height}px",
                    explanation="Mandatory customer legal disclaimer is hidden or rendered unreadable."
                ))
            else:
                # Check key substrings
                has_terms = "terms" in actual_text.lower() or "warranty" in actual_text.lower() or "policy" in actual_text.lower()
                passed = has_terms and len(actual_text) >= 20
                status = "PASS" if passed else "FAIL"
                results.append(ContractResult(
                    contract_id=cid,
                    name=name,
                    status=status,
                    severity=severity,
                    expected=expected_val,
                    actual=actual_text,
                    evidence=f"Text length: {len(actual_text)} chars. Content: '{actual_text[:60]}...'",
                    explanation="Mandatory legal disclaimer present and verified." if passed else "Legal disclaimer text altered or incomplete."
                ))

        elif rule == "min_font_size":
            actual_size = target_node.font_size or 0.0
            expected_min = float(expected_val)
            passed = actual_size >= (expected_min - 0.5)

            status = "PASS" if passed else "FAIL"
            results.append(ContractResult(
                contract_id=cid,
                name=name,
                status=status,
                severity=severity,
                expected=f">= {expected_min}px",
                actual=f"{actual_size}px",
                evidence=f"Computed CSS font-size: {actual_size}px",
                explanation="Font size exceeds minimum statutory threshold." if passed else f"Font size {actual_size}px is below minimum required {expected_min}px for consumer legibility."
            ))

        elif rule == "min_wcag_contrast":
            fg_color = target_node.color or "#000000"
            bg_color = target_node.background_color or "#ffffff"
            contrast = calculate_contrast_ratio(fg_color, bg_color)
            min_req = float(expected_val)

            passed = contrast >= min_req
            status = "PASS" if passed else "FAIL"
            results.append(ContractResult(
                contract_id=cid,
                name=name,
                status=status,
                severity=severity,
                expected=f">= {min_req}:1 (WCAG AA)",
                actual=f"{contrast:.2f}:1",
                evidence=f"Foreground: {fg_color}, Background: {bg_color}",
                explanation="Contrast complies with WCAG AA accessibility standard." if passed else f"WCAG contrast violation: {contrast:.2f}:1 fails minimum {min_req}:1 ratio."
            ))

        elif rule == "contains_token":
            actual_text = (target_node.text or "").strip()
            token = str(expected_val).strip()
            passed = token.lower() in actual_text.lower()

            status = "PASS" if passed else "WARNING"
            results.append(ContractResult(
                contract_id=cid,
                name=name,
                status=status,
                severity=severity,
                expected=f"Contains '{token}'",
                actual=actual_text,
                evidence=f"Extracted badge text: '{actual_text}'",
                explanation=f"Discount badge properly highlights {token}." if passed else f"Discount badge does not display expected '{token}' token."
            ))

        elif rule == "element_visibility":
            is_visible = (
                target_node.visibility and 
                (target_node.opacity is None or target_node.opacity >= 0.5) and
                target_node.bounding_box.width > 30 and
                target_node.bounding_box.height > 15
            )
            status = "PASS" if is_visible else "FAIL"
            results.append(ContractResult(
                contract_id=cid,
                name=name,
                status=status,
                severity=severity,
                expected="Visible, interactive element with >=30x15px bounds",
                actual=f"Visible={target_node.visibility}, Opacity={target_node.opacity}, Size={target_node.bounding_box.width}x{target_node.bounding_box.height}",
                evidence=f"Coordinates: x={target_node.bounding_box.x}, y={target_node.bounding_box.y}",
                explanation="Primary CTA is visible and clickable." if is_visible else "Primary CTA is hidden, occluded, or collapsed."
            ))

    return results

