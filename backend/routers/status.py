import asyncio
import json
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import case, func
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse

import auth
import database
import models
from auth import get_current_user
from database import get_db
from notifications import notification_manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Status & Events"])




@router.get("/status")
def get_network_status(
    db: Session = Depends(get_db), current_user: auth.User = Depends(get_current_user)
):
    # ⚡ Bolt: Pushed global status aggregations down to the database level.
    # Instead of fetching all host statuses into Python memory (O(N) data transfer),
    # we compute the total count, reachable count, and average latency natively in SQLite.
    stats = db.query(
        func.count(models.HostDB.id).label("total"),
        func.sum(case((models.HostDB.last_status == "UP", 1), else_=0)).label("reachable"),
        func.avg(case((models.HostDB.last_status == "UP", models.HostDB.average_latency), else_=None)).label("avg_latency")
    ).filter(models.HostDB.enabled == True).first()

    total_hosts = stats.total or 0
    reachable_hosts = stats.reachable or 0
    global_avg = stats.avg_latency or 0.0

    if total_hosts == 0:
        return {"status": "UNKNOWN", "details": "No data", "global_avg_latency": 0}

    is_up = (reachable_hosts / total_hosts) > 0.5

    return {
        "status": "UP" if is_up else "DOWN",
        "reachable": int(reachable_hosts),
        "total": int(total_hosts),
        "global_avg_latency": float(global_avg),
    }




def _get_sse_data():
    """Sync helper — runs in executor to avoid blocking event loop."""
    db = database.SessionLocal()
    try:
        # ⚡ Bolt: Fetch only the specific columns needed for the SSE payload
        # This prevents full ORM model instantiation in a high-frequency execution path (called every 5s per client)
        hosts = db.query(
            models.HostDB.id,
            models.HostDB.name,
            models.HostDB.last_status,
            models.HostDB.average_latency,
            models.HostDB.maintenance,
            models.HostDB.enabled,
            models.HostDB.group_name,
            models.HostDB.ip_address,
            models.HostDB.monitor_type,
            models.HostDB.port,
            models.HostDB.ssl_monitor,
            models.HostDB.ssl_expiry_days,
            models.HostDB.latency_threshold_ms,
        ).filter(models.HostDB.enabled == True).all()

        host_list = []
        for h in hosts:
            host_list.append(
                {
                    "id": h.id,
                    "name": h.name,
                    "last_status": h.last_status,
                    "average_latency": h.average_latency,
                    "maintenance": h.maintenance,
                    "enabled": h.enabled,
                    "group_name": h.group_name,
                    "ip_address": h.ip_address,
                    "monitor_type": h.monitor_type,
                    "port": h.port,
                    "ssl_monitor": h.ssl_monitor,
                    "ssl_expiry_days": h.ssl_expiry_days,
                    "latency_threshold_ms": h.latency_threshold_ms,
                }
            )
        return host_list
    finally:
        db.close()


@router.get("/events")
async def event_stream(request: Request):
    async def generate():
        while True:
            if await request.is_disconnected():
                break
            try:
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, _get_sse_data)
                yield {"data": json.dumps(data), "event": "hosts_update"}
            except Exception as e:
                logger.error(f"SSE error: {e}")
            await asyncio.sleep(5)

    return EventSourceResponse(generate())


@router.post("/heartbeat/{slug}")
def receive_heartbeat(slug: str, db: Session = Depends(get_db)):
    host = (
        db.query(models.HostDB)
        .filter(models.HostDB.heartbeat_slug == slug, models.HostDB.enabled == True)
        .first()
    )
    if not host:
        raise HTTPException(status_code=404, detail="Heartbeat slug not found")

    ping_result = models.PingResultDB(host_id=host.id, latency=0.1)
    db.add(ping_result)

    prev_status = host.last_status
    host.last_status = "UP"
    db.commit()

    if prev_status == "DOWN" and not host.maintenance:
        notification_manager.send_notification(
            f"🟢 Host {host.name} is UP",
            f"Host: {host.name}\nHeartbeat received.\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        )
    return {"ok": True, "host": host.name}
