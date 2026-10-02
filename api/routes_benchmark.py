"""
Benchmark execution and reporting routes.
Runs multi-seed Monte Carlo evaluations, paired significance tests, and exports results.
"""
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field
import io
import csv
from eval.benchmark_runner import BenchmarkRunner
from schedulers import SCHEDULER_REGISTRY

router = APIRouter(prefix="/api/benchmark", tags=["Benchmark"])

# In-memory store of latest benchmark run
LATEST_BENCHMARK_RESULTS: Dict[str, Any] = {}


class BenchmarkRequest(BaseModel):
    scenario_id: str = "periodic_emitters"
    scheduler_ids: List[str] = Field(default_factory=lambda: list(SCHEDULER_REGISTRY.keys()))
    num_seeds: int = Field(default=10, ge=3, le=50)
    base_seed: int = 100


@router.post("/run")
def run_benchmark(req: BenchmarkRequest):
    global LATEST_BENCHMARK_RESULTS
    runner = BenchmarkRunner(num_seeds=req.num_seeds, base_seed=req.base_seed)

    results = runner.run_scenario_benchmark(
        scenario_id=req.scenario_id,
        scheduler_ids=req.scheduler_ids,
        seeds=runner.seeds,
    )
    table_md = runner.generate_markdown_table(results)
    results["markdown_table"] = table_md

    LATEST_BENCHMARK_RESULTS = results
    return results


@router.get("/latest")
def get_latest_benchmark():
    if not LATEST_BENCHMARK_RESULTS:
        # Run a default fast 5-seed benchmark to populate on first load
        runner = BenchmarkRunner(num_seeds=5, base_seed=42)
        results = runner.run_scenario_benchmark(
            scenario_id="periodic_emitters",
            scheduler_ids=["smart_scan", "sequential", "random", "priority_rr"],
        )
        results["markdown_table"] = runner.generate_markdown_table(results)
        return results
    return LATEST_BENCHMARK_RESULTS


@router.get("/export/csv")
def export_benchmark_csv():
    if not LATEST_BENCHMARK_RESULTS:
        raise HTTPException(status_code=404, detail="No benchmark results available to export.")

    summary = LATEST_BENCHMARK_RESULTS["summary"]
    scheds = LATEST_BENCHMARK_RESULTS["schedulers"]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "scenario_id", "algorithm",
        "threat_intercept_rate_mean", "threat_intercept_rate_std",
        "periodic_revisit_rate_mean", "periodic_revisit_rate_std",
        "mean_ttfi_mean", "mean_ttfi_std",
        "dwell_efficiency_mean", "dwell_efficiency_std",
        "total_retune_cost_ms_mean", "total_retune_cost_ms_std",
    ])

    for sid in scheds:
        s = summary[sid]
        writer.writerow([
            LATEST_BENCHMARK_RESULTS["scenario_id"],
            sid,
            s["threat_intercept_rate"]["mean"], s["threat_intercept_rate"]["std"],
            s["periodic_revisit_rate"]["mean"], s["periodic_revisit_rate"]["std"],
            s["mean_ttfi_steps"]["mean"], s["mean_ttfi_steps"]["std"],
            s["dwell_efficiency"]["mean"], s["dwell_efficiency"]["std"],
            s["total_retune_cost_ms"]["mean"], s["total_retune_cost_ms"]["std"],
        ])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=ew_benchmark_results.csv"},
    )
