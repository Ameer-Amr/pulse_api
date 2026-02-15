# app/core/worker.py
import asyncio
from sqlalchemy.orm import Session
from app.database import SessionLocal
from servers.models import UserServer
from servers.pinger import perform_ping 

async def monitoring_loop():
    """
    Create a dedicated asyncio.Task per server so each one runs at its own interval_seconds.
    The main loop refreshes the server list periodically, starting monitors for new servers
    and cancelling monitors for removed servers.
    """
    tasks = {}  # server_id -> asyncio.Task

    async def monitor_server(server_id):
        while True:
            # open a fresh session for each ping
            with SessionLocal() as db:
                try:
                    server = db.query(UserServer).filter(UserServer.id == server_id).first()
                    if server is None:
                        return

                    # perform the ping with a fresh session and server instance
                    await perform_ping(db, server)

                    # read interval (fallback to 60s if missing/invalid)
                    interval = getattr(server, "interval_seconds", None) or 60
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    interval = 60

            await asyncio.sleep(interval)

    try:
        while True:
            # refresh server list
            with SessionLocal() as db:
                try:
                    servers = db.query(UserServer).all()
                except Exception as e:
                    servers = []

            current_ids = {s.id for s in servers}

            # start monitors for new servers
            for s in servers:
                if s.id not in tasks:
                    tasks[s.id] = asyncio.create_task(monitor_server(s.id))

            # cancel monitors for removed servers
            removed = [sid for sid in tasks.keys() if sid not in current_ids]
            for sid in removed:
                task = tasks.pop(sid)
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    pass

            # main loop refresh interval: small so new/removed servers are picked up quickly
            await asyncio.sleep(5)
    except asyncio.CancelledError:
        # cancel all child tasks on shutdown
        for t in tasks.values():
            t.cancel()
        raise
