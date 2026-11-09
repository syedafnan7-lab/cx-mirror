"""
CX MIRROR — ROC Benchmark API Router
Provides GET /api/roc-benchmark executing honest 60-scenario evaluation.
"""

from fastapi import APIRouter, Query
from app.models.schemas import ROCBenchmarkResponse
from app.benchmark.roc_engine import run_roc_benchmark

router = APIRouter(prefix="/api", tags=["Benchmark"])


@router.get("/roc-benchmark", response_model=ROCBenchmarkResponse)
async def get_roc_benchmark_results(seed: int = Query(42, description="Random seed for scenario generation")):
    """
    Executes honest comparison between CX Mirror and Traditional Pixel Diff
    across 60 reproducible scenarios.
    """
    results = run_roc_benchmark(seed=seed)
    return results

