"""
CX MIRROR — API Schemas
Pydantic schemas for all public REST API endpoints.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.models.graph_models import MatchedPair, Discrepancy, ContractResult


class AnalysisScores(BaseModel):
    visual: float
    structural: float
    contract: float
    total: float


class AnalysisSummary(BaseModel):
    total_mockup_nodes: int
    total_dom_nodes: int
    matched_nodes: int
    unmatched_mockup_nodes: int
    unmatched_dom_nodes: int
    discrepancies: int
    critical_failures: int


class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    verdict: str  # PASS / FAIL
    confidence: float
    threshold: float
    scores: AnalysisScores
    summary: AnalysisSummary
    matches: List[MatchedPair]
    unmatched_mockup_nodes: List[Dict[str, Any]] = Field(default_factory=list)
    unmatched_dom_nodes: List[Dict[str, Any]] = Field(default_factory=list)
    discrepancies: List[Discrepancy]
    contracts: List[ContractResult]
    graph: Dict[str, Any] = Field(default_factory=dict)
    artifacts: Dict[str, str] = Field(default_factory=dict)
    rendering_metadata: Dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: float


class PresetResponse(BaseModel):
    name: str
    title: str
    description: str
    defects_introduced: List[str]
    expected_verdict: str


class ROCPoint(BaseModel):
    fpr: float
    tpr: float
    threshold: float


class ConfusionMatrix(BaseModel):
    true_positive: int
    false_positive: int
    true_negative: int
    false_negative: int


class ROCBenchmarkResponse(BaseModel):
    seed: int
    total_scenarios: int
    categories: Dict[str, int]
    cx_mirror_auc: float
    pixel_diff_auc: float
    cx_roc_curve: List[ROCPoint]
    pixel_roc_curve: List[ROCPoint]
    cx_confusion_matrix: ConfusionMatrix
    pixel_confusion_matrix: ConfusionMatrix
    precision: float
    recall: float
    accuracy: float
    scenarios_sample: List[Dict[str, Any]]

