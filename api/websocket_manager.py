"""
WebSocket Connection Manager for live real-time simulation streaming.
Broadcasts 20-50 Hz spectrum telemetry, beliefs, and explainability updates to connected clients.
"""
from typing import List, Dict, Any
import json
import asyncio
from fastapi import WebSocket, WebSocketDisconnect


class WebSocketManager:
    """Manages active WebSocket connections and thread-safe broadcasting."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

    async def broadcast_json(self, data: Dict[str, Any]):
        """Broadcasts data dictionary as JSON to all connected clients."""
        async with self._lock:
            stale = []
            for connection in self.active_connections:
                try:
                    await connection.send_json(data)
                except Exception:
                    stale.append(connection)
            for s in stale:
                if s in self.active_connections:
                    self.active_connections.remove(s)

    def active_count(self) -> int:
        return len(self.active_connections)


ws_manager = WebSocketManager()
