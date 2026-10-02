"""
FastAPI Application Entrypoint for DRDO SIH26055 Electronic Warfare Smart Scan.
Provides REST APIs and real-time WebSocket state streaming.
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .websocket_manager import ws_manager
from .routes_sim import router as sim_router, sim_session
from .routes_benchmark import router as bench_router
from .routes_dataset import router as dataset_router

# Background streaming worker task
streaming_worker_task = None


async def simulation_streaming_worker():
    """Background loop that steps the simulation and streams telemetry when active."""
    while True:
        try:
            if sim_session.is_running:
                step_data = sim_session.step()
                # Broadcast over WebSockets
                if ws_manager.active_count() > 0:
                    await ws_manager.broadcast_json({
                        "type": "sim_step",
                        "data": step_data,
                    })
                if step_data.get("done"):
                    sim_session.is_running = False

            # Sleep interval according to simulation speed
            interval = 1.0 / max(1, sim_session.speed_hz)
            await asyncio.sleep(interval)
        except asyncio.CancelledError:
            break
        except Exception as e:
            await asyncio.sleep(0.1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global streaming_worker_task
    # Initialize default simulation
    sim_session.initialize("periodic_emitters", "smart_scan", 42, 16)
    streaming_worker_task = asyncio.create_task(simulation_streaming_worker())
    yield
    if streaming_worker_task:
        streaming_worker_task.cancel()


app = FastAPI(
    title="DRDO Electronic Warfare Smart Scan API",
    description="Cognitive Surveillance Receiver Scheduling Engine (SIH26055)",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(sim_router)
app.include_router(bench_router)
app.include_router(dataset_router)


@app.get("/")
def root():
    return {
        "project": "DRDO Smart Scan Electronic Support Receiver (SIH26055)",
        "status": "online",
        "active_scenario": sim_session.scenario_id,
        "active_scheduler": sim_session.scheduler_id,
    }


@app.websocket("/ws/live")
async def websocket_live_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        # Send initial state snapshot on connection
        await websocket.send_json({
            "type": "init_state",
            "data": sim_session.get_state(),
        })
        while True:
            # Client can send commands like {"action": "step", "speed": 30}
            msg = await websocket.receive_json()
            action = msg.get("action")
            if action == "step":
                step_data = sim_session.step()
                await websocket.send_json({"type": "sim_step", "data": step_data})
            elif action == "play":
                sim_session.is_running = True
            elif action == "pause":
                sim_session.is_running = False
            elif action == "set_speed":
                sim_session.speed_hz = max(1, min(100, int(msg.get("speed", 20))))
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)
    except Exception:
        await ws_manager.disconnect(websocket)
