"""
CX MIRROR — Graph and Data Models
Defines internal spatial graphs, nodes, matched pairs, discrepancies, and contracts.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    x: float
    y: float
    width: float
    height: float


class Displacement(BaseModel):
    dx: float
    dy: float
    distance: float
    width_diff: float = 0.0
    height_diff: float = 0.0


class GraphNode(BaseModel):
    id: str
    element_type: str  # text, price, legal, button, image, container, badge
    role: Optional[str] = None  # sku, current_price, original_price, discount, title, legal_disclaimer, cta
    text: Optional[str] = ""
    bounding_box: BoundingBox
    font_size: Optional[float] = None
    font_weight: Optional[str] = None
    color: Optional[str] = None
    background_color: Optional[str] = None
    z_index: Optional[int] = 0
    opacity: Optional[float] = 1.0
    visibility: bool = True
    parent_id: Optional[str] = None
    children_ids: List[str] = Field(default_factory=list)
    importance: float = 1.0  # 3.0 for price/legal, 2.0 for CTA, 1.5 for product info, 1.0 ordinary, 0.5 decorative


class SpatialGraph(BaseModel):
    nodes: Dict[str, GraphNode] = Field(default_factory=dict)
    viewport: Dict[str, int] = Field(default_factory=lambda: {"width": 1440, "height": 1000})


class MatchedPair(BaseModel):
    mockup_node_id: str
    dom_node_id: str
    semantic_role: str
    importance: float = 1.0
    c_geometry: float
    ciou: float
    c_ssim: float
    raw_ssim: float
    c_color: float
    delta_e: float
    c_text: float
    text_sim: float
    displacement: Displacement
    match_confidence: float
    quality_score: float  # Q_i in [0, 1]


class Discrepancy(BaseModel):
    node_id: str
    category: str  # geometry, typography, color, text, business_contract, missing_element
    severity: str  # CRITICAL, MAJOR, MINOR, WARNING
    expected: Any
    actual: Any
    difference: str
    confidence: float
    explanation: str


class ContractResult(BaseModel):
    contract_id: str
    name: str
    status: str  # PASS, FAIL, WARNING
    severity: str  # CRITICAL, MAJOR, MINOR
    expected: Any
    actual: Any
    evidence: str
    explanation: str

