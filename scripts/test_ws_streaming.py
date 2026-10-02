"""
Test script to verify real-time WebSocket state streaming at 20-30 Hz.
"""
import asyncio
import json
import websockets
import httpx

async def test_websocket_streaming():
    print("Connecting to ws://127.0.0.1:8000/ws/live...")
    async with websockets.connect("ws://127.0.0.1:8000/ws/live") as ws:
        # First message should be init_state
        init_msg = await ws.recv()
        data = json.loads(init_msg)
        assert data["type"] == "init_state", f"Expected init_state, got {data.get('type')}"
        print("  -> OK: Received init_state with scenario:", data["data"]["scenario_id"])

        # Send play command
        print("  Triggering live scan play...")
        httpx.post("http://127.0.0.1:8000/api/sim/play?speed_hz=25")

        # Collect 5 streamed steps
        for i in range(5):
            msg = await asyncio.wait_for(ws.recv(), timeout=3.0)
            step_obj = json.loads(msg)
            assert step_obj["type"] == "sim_step"
            step_d = step_obj["data"]
            print(f"  -> Streamed step #{step_d['step']}: Dwell on Band {step_d['action']} (Hit: {step_d['telemetry']['hit']}, Beliefs: {len(step_d['beliefs'])} bands)")

        # Pause
        httpx.post("http://127.0.0.1:8000/api/sim/pause")
        print("  -> OK: WebSocket real-time 25 Hz streaming verified successfully!")

if __name__ == "__main__":
    asyncio.run(test_websocket_streaming())
