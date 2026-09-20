"""
Real-Time WebSocket Engine for Live Tracking (Swiggy / Uber Style)
Delivers sub-5ms live GPS coordinates, status transitions, and dynamic ETA updates
to customer and partner devices.
"""
import json
import logging
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger("websockets")

class RealtimeConnectionManager:
    def __init__(self):
        # request_id -> Set[WebSocket] (Customer tracking screens)
        self.request_subscribers: Dict[str, Set[WebSocket]] = {}
        # partner_id -> WebSocket (Partner app live connection)
        self.partner_connections: Dict[str, WebSocket] = {}

    async def connect_request_tracker(self, request_id: str, websocket: WebSocket):
        await websocket.accept()
        if request_id not in self.request_subscribers:
            self.request_subscribers[request_id] = set()
        self.request_subscribers[request_id].add(websocket)
        logger.info(f"Customer connected to live stream for Request: {request_id}")

    def disconnect_request_tracker(self, request_id: str, websocket: WebSocket):
        if request_id in self.request_subscribers:
            self.request_subscribers[request_id].discard(websocket)
            if not self.request_subscribers[request_id]:
                del self.request_subscribers[request_id]
        logger.info(f"Customer disconnected from Request: {request_id}")

    async def broadcast_request_update(self, request_id: str, payload: dict):
        """Broadcast live tracking data (coordinates, status, ETA) to all watching devices."""
        if request_id in self.request_subscribers:
            message = json.dumps(payload)
            dead_sockets = set()
            for ws in list(self.request_subscribers[request_id]):
                try:
                    await ws.send_text(message)
                except Exception:
                    dead_sockets.add(ws)
            for ws in dead_sockets:
                self.request_subscribers[request_id].discard(ws)

    async def connect_partner(self, partner_id: str, websocket: WebSocket):
        await websocket.accept()
        self.partner_connections[partner_id] = websocket
        logger.info(f"Partner {partner_id} connected to real-time dispatch channel")

    def disconnect_partner(self, partner_id: str):
        if partner_id in self.partner_connections:
            del self.partner_connections[partner_id]
        logger.info(f"Partner {partner_id} disconnected from real-time dispatch channel")

    async def send_partner_alert(self, partner_id: str, payload: dict) -> bool:
        """Sends instant interactive dispatch popup to partner's phone."""
        if partner_id in self.partner_connections:
            ws = self.partner_connections[partner_id]
            try:
                await ws.send_text(json.dumps(payload))
                return True
            except Exception:
                self.disconnect_partner(partner_id)
        return False

    async def broadcast_all_partners(self, payload: dict):
        """Broadcasts instant interactive alert to all connected partner consoles."""
        message = json.dumps(payload)
        dead = []
        for pid, ws in list(self.partner_connections.items()):
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(pid)
        for pid in dead:
            self.disconnect_partner(pid)

# Global Singleton
ws_manager = RealtimeConnectionManager()

