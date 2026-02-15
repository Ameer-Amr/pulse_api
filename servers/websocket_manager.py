from fastapi import WebSocket
from typing import Dict, List

class ConnectionManager:
    def __init__(self):
        # Dictionary mapping server_id to a list of active WebSockets
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, server_id: int):
        await websocket.accept()
        if server_id not in self.active_connections:
            self.active_connections[server_id] = []
        self.active_connections[server_id].append(websocket)

    def disconnect(self, websocket: WebSocket, server_id: int):
        if server_id in self.active_connections:
            self.active_connections[server_id].remove(websocket)

    async def broadcast_to_server(self, server_id: int, message: dict):
        """Sends a message only to clients watching a specific server."""
        if server_id in self.active_connections:
            for connection in self.active_connections[server_id]:
                await connection.send_json(message)

manager = ConnectionManager()
