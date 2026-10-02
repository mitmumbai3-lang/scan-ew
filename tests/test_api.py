"""
Unit tests for FastAPI REST endpoints and WebSocket handshakes.
"""
import pytest
from fastapi.testclient import TestClient
from api.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_root_endpoint(client):
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert "project" in data
    assert data["status"] == "online"


def test_presets_endpoint(client):
    res = client.get("/api/sim/presets")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 5
    ids = [p["id"] for p in data]
    assert "cold_start" in ids
    assert "periodic_emitters" in ids


def test_schedulers_endpoint(client):
    res = client.get("/api/sim/schedulers")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 5


def test_sim_init_and_step(client):
    # Initialize simulation
    init_res = client.post(
        "/api/sim/init",
        json={"scenario_id": "periodic_emitters", "scheduler_id": "smart_scan", "seed": 42, "num_bands": 16},
    )
    assert init_res.status_code == 200
    state = init_res.json()["state"]
    assert state["scenario_id"] == "periodic_emitters"

    # Step simulation
    step_res = client.post("/api/sim/step", json={"steps": 3})
    assert step_res.status_code == 200
    step_data = step_res.json()
    assert step_data["step_count"] == 3
    assert "latest" in step_data
    assert "metrics" in step_data["latest"]
    assert "explainability" in step_data["latest"]


def test_benchmark_run_api(client):
    bench_res = client.post(
        "/api/benchmark/run",
        json={
            "scenario_id": "periodic_emitters",
            "scheduler_ids": ["smart_scan", "sequential"],
            "num_seeds": 3,
            "base_seed": 42,
        },
    )
    assert bench_res.status_code == 200
    data = bench_res.json()
    assert "summary" in data
    assert "smart_scan" in data["summary"]
    assert "markdown_table" in data


def test_dataset_sample_api(client):
    res = client.get("/api/dataset/samples")
    assert res.status_code == 200
    data = res.json()
    assert "csv_sample" in data
    assert "json_sample" in data
