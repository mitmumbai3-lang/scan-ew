"""
Unit tests for evaluation metrics, significance testing, and benchmark runner.
"""
import pytest
from sim.receiver import ReceiverTelemetry
from sim.emitter import FixedEmitter, PeriodicRadarEmitter
from eval.metrics import EWMetricsCalculator
from eval.significance import SignificanceTester
from eval.benchmark_runner import BenchmarkRunner


def test_metrics_calculator():
    e1 = FixedEmitter(id="EM1", name="Fixed 1", band=1)
    e2 = PeriodicRadarEmitter(id="RADAR1", name="Radar 1", band=3, scan_period=20)
    all_emitters = [e1, e2]

    # Create dummy telemetry
    telemetry = [
        ReceiverTelemetry(
            step=0, dwell_band=1, hit=True, measured_snr_db=18.0, pulse_count=4,
            retune_cost_ms=0.0, cumulative_time_ms=2.0, intercepted_emitter_ids=["EM1"]
        ),
        ReceiverTelemetry(
            step=1, dwell_band=5, hit=False, measured_snr_db=0.0, pulse_count=0,
            retune_cost_ms=0.3, cumulative_time_ms=4.3, intercepted_emitter_ids=[]
        ),
        ReceiverTelemetry(
            step=2, dwell_band=3, hit=True, measured_snr_db=22.0, pulse_count=5,
            retune_cost_ms=0.2, cumulative_time_ms=6.5, intercepted_emitter_ids=["RADAR1"]
        ),
    ]

    metrics = EWMetricsCalculator.compute_episode_metrics(
        telemetry_history=telemetry,
        all_emitters=all_emitters,
        num_bands=8,
    )

    assert metrics["distinct_emitters_intercepted"] == 2
    assert metrics["intercepted_fraction"] == 1.0
    assert metrics["mean_ttfi_steps"] == 1.0  # (0 + 2) / 2
    assert 0.0 <= metrics["dwell_efficiency"] <= 1.0
    assert 0.0 <= metrics["band_coverage_fairness"] <= 1.0


def test_significance_tester():
    sample_a = [0.85, 0.88, 0.91, 0.84, 0.89, 0.92, 0.87, 0.90]
    sample_b = [0.45, 0.42, 0.50, 0.43, 0.47, 0.49, 0.44, 0.46]

    res = SignificanceTester.compare_samples(sample_a, sample_b, metric_name="intercept_rate")
    assert res["statistically_significant"] is True
    assert res["p_value_ttest"] < 0.01
    assert res["superiority"] == "proposed"
    assert res["cohens_d"] > 2.0


def test_benchmark_runner_mini():
    runner = BenchmarkRunner(num_seeds=3, base_seed=42)
    # Test a mini benchmark across 2 schedulers on periodic scenario
    results = runner.run_scenario_benchmark(
        scenario_id="periodic_emitters",
        scheduler_ids=["smart_scan", "sequential"],
        seeds=[42, 43, 44],
    )

    assert "summary" in results
    assert "smart_scan" in results["summary"]
    assert "sequential" in results["summary"]
    assert "significance" in results
    assert "sequential" in results["significance"]

    table_md = runner.generate_markdown_table(results)
    assert "| **smart_scan** |" in table_md
    assert "| **sequential** |" in table_md
