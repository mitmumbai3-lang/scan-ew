"""
Multi-Seed Monte Carlo Benchmark Runner for Electronic Warfare Schedulers.
Executes batch evaluations across 30+ seeds, aggregates mean +/- std, and conducts
paired significance hypothesis testing.
"""
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd
from sim.presets import get_scenario_preset, PRESET_FACTORIES
from schedulers import get_scheduler, SCHEDULER_REGISTRY
from .metrics import EWMetricsCalculator
from .significance import SignificanceTester


class BenchmarkRunner:
    """Executes repeatable multi-seed Monte Carlo benchmarks across algorithms and scenarios."""

    def __init__(self, num_seeds: int = 30, base_seed: int = 100):
        self.num_seeds = num_seeds
        self.base_seed = base_seed
        self.seeds = [base_seed + i for i in range(num_seeds)]

    def run_single_episode(self, scenario_id: str, scheduler_id: str, seed: int) -> Dict[str, Any]:
        """Runs a single simulation episode to completion and computes EW metrics."""
        env = get_scenario_preset(scenario_id, seed=seed)
        num_bands = env.config.num_bands
        max_steps = env.config.max_steps_per_episode

        scheduler = get_scheduler(scheduler_id, num_bands=num_bands, seed=seed)
        scheduler.reset()

        telemetry_history = []
        obs = env.reset(seed=seed)

        for step in range(max_steps):
            action = scheduler.select_band(step)
            obs, telem, info = env.step(action)
            scheduler.observe(obs)
            telemetry_history.append(telem)

        # Extract period estimates if available
        est_periods = None
        if hasattr(scheduler, "periodicity_engine"):
            est_periods = scheduler.periodicity_engine.get_period_estimates()

        metrics = EWMetricsCalculator.compute_episode_metrics(
            telemetry_history=telemetry_history,
            all_emitters=env.emitters,
            num_bands=num_bands,
            estimated_periods=est_periods,
        )
        return metrics

    def run_scenario_benchmark(
        self,
        scenario_id: str,
        scheduler_ids: Optional[List[str]] = None,
        seeds: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """Runs multi-seed benchmark for a specific scenario across all specified algorithms."""
        sched_list = scheduler_ids or list(SCHEDULER_REGISTRY.keys())
        seed_list = seeds or self.seeds

        # Structure: sched_id -> metric_name -> list of values across seeds
        raw_seed_data: Dict[str, Dict[str, List[float]]] = {
            sid: {
                "intercepted_fraction": [],
                "mean_ttfi_steps": [],
                "threat_intercept_rate": [],
                "periodic_revisit_rate": [],
                "dwell_efficiency": [],
                "wasted_dwell_ratio": [],
                "band_coverage_fairness": [],
                "total_retune_cost_ms": [],
            }
            for sid in sched_list
        }

        for sid in sched_list:
            for seed in seed_list:
                res = self.run_single_episode(scenario_id, sid, seed)
                for k in raw_seed_data[sid].keys():
                    raw_seed_data[sid][k].append(res.get(k, 0.0))

        # Compute summary statistics (Mean +/- Std)
        summary: Dict[str, Dict[str, Dict[str, float]]] = {}
        for sid in sched_list:
            summary[sid] = {}
            for k, vals in raw_seed_data[sid].items():
                summary[sid][k] = {
                    "mean": round(float(np.mean(vals)), 4),
                    "std": round(float(np.std(vals, ddof=1)), 4) if len(vals) > 1 else 0.0,
                    "median": round(float(np.median(vals)), 4),
                }

        # Compute Paired Statistical Significance against proposed "smart_scan"
        significance_results = {}
        if "smart_scan" in sched_list:
            proposed_raw = raw_seed_data["smart_scan"]
            for sid in sched_list:
                if sid == "smart_scan":
                    continue
                significance_results[sid] = {}
                for metric in ["threat_intercept_rate", "periodic_revisit_rate", "mean_ttfi_steps", "dwell_efficiency"]:
                    higher_is_better = (metric != "mean_ttfi_steps")
                    comp = SignificanceTester.compare_samples(
                        proposed_raw[metric],
                        raw_seed_data[sid][metric],
                        metric_name=metric,
                        higher_is_better=higher_is_better,
                    )
                    significance_results[sid][metric] = comp

        return {
            "scenario_id": scenario_id,
            "num_seeds": len(seed_list),
            "schedulers": sched_list,
            "summary": summary,
            "significance": significance_results,
            "raw_seed_data": raw_seed_data,
        }

    def generate_markdown_table(self, benchmark_result: Dict[str, Any]) -> str:
        """Converts benchmark results to a formatted GitHub Markdown table."""
        summary = benchmark_result["summary"]
        scheds = benchmark_result["schedulers"]

        lines = [
            f"### Benchmark Evaluation: `{benchmark_result['scenario_id']}` ({benchmark_result['num_seeds']} seeds)",
            "",
            "| Algorithm | Threat Intercept Rate | Periodic Revisit Rate | Mean TTFI (steps) | Dwell Efficiency | Retune Cost (ms) |",
            "| :--- | :---: | :---: | :---: | :---: | :---: |",
        ]

        for sid in scheds:
            s = summary[sid]
            ir = f"{s['threat_intercept_rate']['mean']:.3f} ± {s['threat_intercept_rate']['std']:.3f}"
            pr = f"{s['periodic_revisit_rate']['mean']:.3f} ± {s['periodic_revisit_rate']['std']:.3f}"
            ttfi = f"{s['mean_ttfi_steps']['mean']:.1f} ± {s['mean_ttfi_steps']['std']:.1f}"
            eff = f"{s['dwell_efficiency']['mean']:.3f} ± {s['dwell_efficiency']['std']:.3f}"
            retune = f"{s['total_retune_cost_ms']['mean']:.1f} ± {s['total_retune_cost_ms']['std']:.1f}"
            lines.append(f"| **{sid}** | {ir} | {pr} | {ttfi} | {eff} | {retune} |")

        return "\n".join(lines)
