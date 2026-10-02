"""
Offline 30-Seed Monte Carlo Benchmark Script for DRDO SIH26055.
Runs all 5 scenarios across all 5 schedulers, saving results to docs/RESULTS.md and sample_data/benchmark_results.json.
"""
import json
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eval.benchmark_runner import BenchmarkRunner

SCENARIOS = [
    ("periodic_emitters", "Periodic Scanning Radars"),
    ("cold_start", "Cold Start Discovery"),
    ("frequency_agile", "Frequency Agile Hoppers"),
    ("decoy_heavy", "Decoy-Heavy Electronic Attack"),
    ("congested", "Congested Multi-Emitter Battlefield"),
]

SCHEDULERS = ["smart_scan", "sequential", "random", "priority_rr", "rl_dqn"]


def main():
    num_seeds = 30
    print(f"Starting DRDO SIH26055 Monte Carlo Benchmark ({num_seeds} seeds per scenario)...")
    runner = BenchmarkRunner(num_seeds=num_seeds, base_seed=100)

    all_results = {}
    md_sections = [
        "# Comprehensive Benchmark Results (SIH26055 - DRDO)",
        "",
        f"**Monte Carlo Configuration**: {num_seeds} deterministic seeds (100 to {100 + num_seeds - 1}) per scenario.",
        "**Statistical Hypothesis Tests**: Paired Student's t-test and Wilcoxon signed-rank test against Proposed *SmartScan-BayesianRMAB* (α = 0.05).",
        "",
    ]

    for scen_id, scen_name in SCENARIOS:
        print(f"\n--> Running scenario: {scen_name} ({scen_id})...")
        res = runner.run_scenario_benchmark(
            scenario_id=scen_id,
            scheduler_ids=SCHEDULERS,
        )
        all_results[scen_id] = res

        table_md = runner.generate_markdown_table(res)
        md_sections.append(f"## {scen_name}")
        md_sections.append(table_md)
        md_sections.append("")

        # Add significance notes
        if "significance" in res:
            md_sections.append("### Paired Statistical Significance vs Baselines")
            md_sections.append("| Baseline | Metric | Proposed Mean | Baseline Mean | p-value (t-test) | Cohen's d | Superiority |")
            md_sections.append("| :--- | :--- | :---: | :---: | :---: | :---: | :---: |")
            for base_sid, metrics in res["significance"].items():
                for m_name, comp in metrics.items():
                    if "error" in comp:
                        continue
                    p_val_str = f"{comp.get('p_value_ttest', 1.0):.4e}"
                    sig_label = comp.get("significance_label", "ns")
                    cohen = f"{comp.get('cohens_d', 0.0):.2f}"
                    sup = comp.get("superiority", "tie")
                    md_sections.append(
                        f"| {base_sid} | {m_name} | {comp.get('mean_proposed', 0)} | {comp.get('mean_baseline', 0)} | {p_val_str} ({sig_label}) | {cohen} | **{sup}** |"
                    )
            md_sections.append("")

    # Save to JSON
    os.makedirs("sample_data", exist_ok=True)
    with open("sample_data/benchmark_results.json", "w", encoding="utf-8") as f:
        # Strip non-serializable elements if any
        json.dump(all_results, f, indent=2)

    # Save to docs/RESULTS.md
    os.makedirs("docs", exist_ok=True)
    with open("docs/RESULTS.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md_sections))

    print("\nBenchmark complete! Results written to docs/RESULTS.md and sample_data/benchmark_results.json.")


if __name__ == "__main__":
    main()
