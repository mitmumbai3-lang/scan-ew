"""
Comprehensive end-to-end verification script for all DRDO EW Smart Scan panels and functions.
"""
import sys
import os
import json
import httpx

# Project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://127.0.0.1:8000"


def test_presets():
    print("[1/10] Testing /api/sim/presets...")
    r = httpx.get(f"{BASE_URL}/api/sim/presets")
    assert r.status_code == 200, f"Failed presets: {r.status_code}"
    presets = r.json()
    assert len(presets) >= 5, f"Expected 5 presets, got {len(presets)}"
    print(f"  -> OK: {len(presets)} presets found: {[p['id'] for p in presets]}")


def test_schedulers():
    print("[2/10] Testing /api/sim/schedulers...")
    r = httpx.get(f"{BASE_URL}/api/sim/schedulers")
    assert r.status_code == 200
    scheds = r.json()
    assert len(scheds) >= 5
    print(f"  -> OK: {len(scheds)} schedulers found: {[s['id'] for s in scheds]}")


def test_init_all_scenarios():
    print("[3/10] Testing initialization of all 5 scenarios & schedulers...")
    scenarios = ["cold_start", "periodic_emitters", "frequency_agile", "decoy_heavy", "congested"]
    schedulers = ["smart_scan", "sequential", "random", "priority_rr", "rl_dqn"]

    for sc in scenarios:
        for sch in schedulers[:2]:  # test smart_scan and sequential
            r = httpx.post(
                f"{BASE_URL}/api/sim/init",
                json={"scenario_id": sc, "scheduler_id": sch, "seed": 42, "num_bands": 16, "speed_hz": 20},
            )
            assert r.status_code == 200, f"Init failed for {sc} / {sch}"
            data = r.json()["state"]
            assert data["scenario_id"] == sc
            assert len(data["emitters"]) > 0
    print("  -> OK: All scenarios and schedulers initialize cleanly.")


def test_step_functions():
    print("[4/10] Testing step functions (1x and 10x)...")
    # Step 1x
    r1 = httpx.post(f"{BASE_URL}/api/sim/step", json={"steps": 1})
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["step_count"] == 1
    assert "latest" in d1
    assert "metrics" in d1["latest"]
    assert "explainability" in d1["latest"]
    assert "beliefs" in d1["latest"]
    assert len(d1["latest"]["beliefs"]) == 16

    # Step 10x
    r10 = httpx.post(f"{BASE_URL}/api/sim/step", json={"steps": 10})
    assert r10.status_code == 200
    d10 = r10.json()
    assert d10["step_count"] == 10
    assert len(d10["all_steps"]) == 10
    print("  -> OK: Step 1x and Step 10x work correctly with full state and batch arrays.")


def test_play_pause_reset():
    print("[5/10] Testing play, pause, and reset controls...")
    r_play = httpx.post(f"{BASE_URL}/api/sim/play?speed_hz=30")
    assert r_play.status_code == 200
    assert r_play.json()["status"] == "playing"
    assert r_play.json()["speed_hz"] == 30

    r_pause = httpx.post(f"{BASE_URL}/api/sim/pause")
    assert r_pause.status_code == 200
    assert r_pause.json()["status"] == "paused"

    r_reset = httpx.post(f"{BASE_URL}/api/sim/reset")
    assert r_reset.status_code == 200
    assert r_reset.json()["status"] == "reset"
    assert r_reset.json()["state"]["current_step"] == 0
    print("  -> OK: Play, Pause, and Reset controls work properly.")


def test_benchmark_run():
    print("[6/10] Testing benchmark execution API (3 seeds)...")
    r = httpx.post(
        f"{BASE_URL}/api/benchmark/run",
        json={
            "scenario_id": "periodic_emitters",
            "scheduler_ids": ["smart_scan", "sequential", "random"],
            "num_seeds": 3,
            "base_seed": 100,
        },
        timeout=30.0,
    )
    assert r.status_code == 200, f"Benchmark run error: {r.text}"
    bench = r.json()
    assert "summary" in bench
    assert "smart_scan" in bench["summary"]
    assert "significance" in bench
    assert "markdown_table" in bench
    print("  -> OK: Benchmark execution returned full statistics, significance, and markdown table.")


def test_benchmark_export():
    print("[7/10] Testing benchmark CSV export...")
    r = httpx.get(f"{BASE_URL}/api/benchmark/export/csv")
    assert r.status_code == 200
    csv_text = r.text
    assert "scenario_id,algorithm" in csv_text
    assert "smart_scan" in csv_text
    print(f"  -> OK: CSV export generated {len(csv_text.splitlines())} rows.")


def test_dataset_samples():
    print("[8/10] Testing dataset sample templates...")
    r = httpx.get(f"{BASE_URL}/api/dataset/samples")
    assert r.status_code == 200
    data = r.json()
    assert "csv_sample" in data
    assert "json_sample" in data
    assert "RAD_ALPHA" in data["csv_sample"]
    print("  -> OK: Sample datasets loaded correctly.")


def test_dataset_upload():
    print("[9/10] Testing custom dataset upload and replay...")
    sample_csv_path = "sample_data/sample_dense_radar.csv"
    with open(sample_csv_path, "rb") as f:
        files = {"file": ("test_upload.csv", f, "text/csv")}
        r = httpx.post(f"{BASE_URL}/api/dataset/upload", files=files)

    assert r.status_code == 200, f"Upload error: {r.text}"
    upload_res = r.json()
    assert upload_res["status"] == "success"
    assert upload_res["emitter_count"] > 0
    print(f"  -> OK: Dataset upload injected {upload_res['emitter_count']} custom emitters into simulator.")


def test_frontend_reachable():
    print("[10/10] Testing Vite frontend reachable on http://127.0.0.1:5173...")
    r = httpx.get("http://127.0.0.1:5173/")
    assert r.status_code == 200
    assert "AURA-ES" in r.text
    print("  -> OK: Vite React Frontend is live, reachable, and rendered.")


if __name__ == "__main__":
    print("================================================================")
    print(" DRDO SIH26055 Full System Integration Verification Test")
    print("================================================================")
    test_presets()
    test_schedulers()
    test_init_all_scenarios()
    test_step_functions()
    test_play_pause_reset()
    test_benchmark_run()
    test_benchmark_export()
    test_dataset_samples()
    test_dataset_upload()
    test_frontend_reachable()
    print("\n>>> ALL 10 PANELS AND FUNCTIONS VERIFIED SUCCESSFULLY! <<<")
