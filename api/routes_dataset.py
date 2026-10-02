"""
Dataset management, upload, inspection, and sample generation routes.
Allows custom CSV and JSON emitter scenario configurations to be imported into the simulator.
"""
from typing import Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import json
from sim.dataset_adapter import DatasetAdapter
from .routes_sim import sim_session

router = APIRouter(prefix="/api/dataset", tags=["Dataset"])


@router.get("/samples")
def get_sample_datasets():
    """Returns sample CSV and JSON dataset templates."""
    with open("sample_data/sample_dense_radar.csv", "r", encoding="utf-8") as f:
        csv_sample = f.read()

    with open("sample_data/sample_agile_scenario.json", "r", encoding="utf-8") as f:
        json_sample = json.load(f)

    return {
        "csv_sample": csv_sample,
        "json_sample": json_sample,
    }


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """Uploads a CSV or JSON dataset and immediately loads it into the simulator session."""
    filename = file.filename or "dataset"
    content = await file.read()
    text = content.decode("utf-8")

    try:
        if filename.endswith(".json") or text.strip().startswith("{"):
            env = DatasetAdapter.load_from_json(text)
        else:
            env = DatasetAdapter.load_from_csv(text)

        # Inject into simulation session as a custom scenario
        sim_session.env = env
        sim_session.scenario_id = f"custom_{filename}"
        sim_session.num_bands = env.config.num_bands
        sim_session.initialize(
            scenario_id="custom",
            scheduler_id=sim_session.scheduler_id,
            seed=42,
            num_bands=env.config.num_bands,
        )
        sim_session.env = env  # preserve custom loaded environment

        return {
            "status": "success",
            "message": f"Successfully loaded scenario from {filename}",
            "num_bands": env.config.num_bands,
            "emitter_count": len(env.emitters),
            "emitters": [
                {
                    "id": e.id,
                    "name": e.name,
                    "type": e.emitter_type,
                    "priority": e.priority,
                    "base_snr_db": e.base_snr_db,
                }
                for e in env.emitters
            ],
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to parse dataset: {str(exc)}")
