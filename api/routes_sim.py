"""
Simulation control routes for Electronic Warfare Smart Scan dashboard.
Provides session initialization, stepping, streaming playback controls, and state queries.
"""
from typing import Dict, Any, Optional, List
import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from sim.presets import get_scenario_preset, list_available_presets
from sim.rf_environment import RFEnvironment
from schedulers import get_scheduler, list_schedulers
from eval.metrics import EWMetricsCalculator
from .websocket_manager import ws_manager

router = APIRouter(prefix="/api/sim", tags=["Simulation"])


class SimInitRequest(BaseModel):
    scenario_id: str = "periodic_emitters"
    scheduler_id: str = "smart_scan"
    seed: int = 42
    num_bands: int = 16
    speed_hz: int = Field(default=20, ge=1, le=100)


class SimStepRequest(BaseModel):
    steps: int = Field(default=1, ge=1, le=50)


class SimulationSession:
    """Singleton/Active simulation session state."""

    def __init__(self):
        self.scenario_id = "periodic_emitters"
        self.scheduler_id = "smart_scan"
        self.seed = 42
        self.num_bands = 16
        self.speed_hz = 20
        self.is_running = False

        self.env: Optional[RFEnvironment] = None
        self.scheduler = None
        self.telemetry_history = []
        self.last_observation = None
        self.last_telemetry = None
        self.last_info = None
        self.stream_task: Optional[asyncio.Task] = None

    def initialize(self, scenario_id: str, scheduler_id: str, seed: int, num_bands: int = 16):
        self.scenario_id = scenario_id
        self.scheduler_id = scheduler_id
        self.seed = seed
        self.num_bands = num_bands
        self.is_running = False

        self.env = get_scenario_preset(scenario_id, num_bands=num_bands, seed=seed)
        self.scheduler = get_scheduler(scheduler_id, num_bands=num_bands, seed=seed)
        self.telemetry_history = []

        obs = self.env.reset(seed=seed)
        self.scheduler.reset()
        self.last_observation = obs
        self.last_telemetry = None
        self.last_info = {"step": 0, "spectrum_ground_truth": {}}

    def step(self) -> Dict[str, Any]:
        """Executes a single simulation step."""
        if not self.env or not self.scheduler:
            self.initialize(self.scenario_id, self.scheduler_id, self.seed, self.num_bands)

        step_idx = self.env.current_step
        action = self.scheduler.select_band(step_idx)
        obs, telem, info = self.env.step(action)
        self.scheduler.observe(obs)

        self.telemetry_history.append(telem)
        self.last_observation = obs
        self.last_telemetry = telem
        self.last_info = info

        # Extract explainability info
        explain_info = self.scheduler.get_explainability_info(step_idx)
        beliefs = self.scheduler.get_belief_state()

        # Compute rolling metrics
        est_periods = None
        if hasattr(self.scheduler, "periodicity_engine"):
            est_periods = self.scheduler.periodicity_engine.get_period_estimates()

        metrics = EWMetricsCalculator.compute_episode_metrics(
            telemetry_history=self.telemetry_history,
            all_emitters=self.env.emitters,
            num_bands=self.num_bands,
            estimated_periods=est_periods,
        )

        return {
            "step": step_idx,
            "action": action,
            "observation": obs.to_dict(),
            "telemetry": {
                "step": telem.step,
                "dwell_band": telem.dwell_band,
                "hit": telem.hit,
                "measured_snr_db": telem.measured_snr_db,
                "pulse_count": telem.pulse_count,
                "retune_cost_ms": telem.retune_cost_ms,
                "cumulative_time_ms": round(telem.cumulative_time_ms, 2),
                "intercepted_emitter_ids": telem.intercepted_emitter_ids,
                "is_decoy": telem.is_decoy,
                "is_false_alarm": telem.is_false_alarm,
            },
            "ground_truth_active": info.get("spectrum_ground_truth", {}),
            "beliefs": beliefs,
            "explainability": explain_info,
            "metrics": metrics,
            "done": info.get("done", False),
        }

    def get_state(self) -> Dict[str, Any]:
        if not self.env:
            self.initialize(self.scenario_id, self.scheduler_id, self.seed, self.num_bands)

        beliefs = self.scheduler.get_belief_state() if self.scheduler else [0.5] * self.num_bands
        explain_info = self.scheduler.get_explainability_info(self.env.current_step) if self.scheduler else {}

        est_periods = None
        if self.scheduler and hasattr(self.scheduler, "periodicity_engine"):
            est_periods = self.scheduler.periodicity_engine.get_period_estimates()

        metrics = EWMetricsCalculator.compute_episode_metrics(
            telemetry_history=self.telemetry_history,
            all_emitters=self.env.emitters if self.env else [],
            num_bands=self.num_bands,
            estimated_periods=est_periods,
        )

        return {
            "scenario_id": self.scenario_id,
            "scheduler_id": self.scheduler_id,
            "seed": self.seed,
            "num_bands": self.num_bands,
            "current_step": self.env.current_step if self.env else 0,
            "is_running": self.is_running,
            "speed_hz": self.speed_hz,
            "beliefs": beliefs,
            "explainability": explain_info,
            "metrics": metrics,
            "emitters": [
                {
                    "id": e.id,
                    "name": e.name,
                    "type": e.emitter_type,
                    "priority": e.priority,
                    "base_snr_db": e.base_snr_db,
                }
                for e in self.env.emitters
            ] if self.env else [],
        }


sim_session = SimulationSession()


@router.get("/presets")
def get_presets():
    return list_available_presets()


@router.get("/schedulers")
def get_schedulers_list():
    return list_schedulers()


@router.post("/init")
def init_simulation(req: SimInitRequest):
    sim_session.initialize(
        scenario_id=req.scenario_id,
        scheduler_id=req.scheduler_id,
        seed=req.seed,
        num_bands=req.num_bands,
    )
    sim_session.speed_hz = req.speed_hz
    return {"status": "initialized", "state": sim_session.get_state()}


@router.post("/step")
def step_simulation(req: SimStepRequest):
    results = []
    for _ in range(req.steps):
        res = sim_session.step()
        results.append(res)
        if res.get("done"):
            sim_session.is_running = False
            break

    # Return latest step data
    latest = results[-1] if results else {}
    return {"status": "stepped", "step_count": len(results), "latest": latest}


@router.post("/reset")
def reset_simulation():
    sim_session.initialize(
        scenario_id=sim_session.scenario_id,
        scheduler_id=sim_session.scheduler_id,
        seed=sim_session.seed,
        num_bands=sim_session.num_bands,
    )
    return {"status": "reset", "state": sim_session.get_state()}


@router.post("/play")
def play_simulation(speed_hz: Optional[int] = None):
    if speed_hz:
        sim_session.speed_hz = max(1, min(100, speed_hz))
    sim_session.is_running = True
    return {"status": "playing", "speed_hz": sim_session.speed_hz}


@router.post("/pause")
def pause_simulation():
    sim_session.is_running = False
    return {"status": "paused"}


@router.get("/state")
def get_current_state():
    return sim_session.get_state()
