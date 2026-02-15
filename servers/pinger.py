import httpx
import time
from servers.websocket_manager import manager
from servers.models import ServerAnalytics, ServerStatus

async def perform_ping(db, server):
    start_time = time.time()

    # Perform the HTTP request to check server status
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(server.server_url, timeout=10.0)
            status = response.status_code
    except Exception:
        status = 0 # Down
    
    latency = round((time.time() - start_time) * 1000, 2)

    # 1. Update Server Status in Database
    server.status = ServerStatus.ACTIVE.value if status == 200 else ServerStatus.INACTIVE.value
    server.updated_at = time.strftime("%Y-%m-%d %H:%M:%S")
    db.add(server)

    # 2. Save Analytics to Database
    new_check = ServerAnalytics(server_id=server.id, status_code=status, latency_ms=latency)
    db.add(new_check)
    db.commit()
    

    # 3. Broadcast Live to WebSockets
    await manager.broadcast_to_server(server.id, {
        "status": status,
        "latency": latency,
        "timestamp": time.strftime("%H:%M:%S")
    })
