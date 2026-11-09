"""
Unit tests for 60-scenario ROC benchmark engine.
"""

from app.benchmark.roc_engine import generate_benchmark_scenarios, run_roc_benchmark


def test_scenario_counts():
    scenarios = generate_benchmark_scenarios(seed=42)
    assert len(scenarios) == 60

    # Count categories
    cats = {}
    for s in scenarios:
        cats[s["category"]] = cats.get(s["category"], 0) + 1

    assert cats["legitimate_dynamic_variation"] == 15
    assert cats["geometry_defect"] == 15
    assert cats["typography_color_defect"] == 10
    assert cats["price_defect"] == 10
    assert cats["legal_defect"] == 10


def test_roc_benchmark_execution():
    res = run_roc_benchmark(seed=42)
    assert res["total_scenarios"] == 60
    assert res["cx_mirror_auc"] >= 0.95
    assert res["pixel_diff_auc"] < res["cx_mirror_auc"]
    assert len(res["cx_roc_curve"]) > 0
    assert len(res["pixel_roc_curve"]) > 0

