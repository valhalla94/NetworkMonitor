import asyncio
import json
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
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
    # ⚡ Bolt: Fetch only needed columns directly from HostDB to avoid expensive PingResultDB joins
    # HostDB already caches last_status and average_latency via the scheduler.
    hosts = db.query(
        models.HostDB.id,
        models.HostDB.last_status,
        models.HostDB.average_latency
    ).filter(models.HostDB.enabled == True).all()

    total_hosts = 0
    reachable_hosts = 0
    total_latency = 0.0
    latency_count = 0

    for host in hosts:
        total_hosts += 1
        if host.last_status == "UP":
            reachable_hosts += 1
            if host.average_latency is not None:
                total_latency += host.average_latency
                latency_count += 1

    if total_hosts == 0:
        return {"status": "UNKNOWN", "details": "No data", "global_avg_latency": 0}

    is_up = (reachable_hosts / total_hosts) > 0.5
    global_avg = (total_latency / latency_count) if latency_count > 0 else 0

    return {
        "status": "UP" if is_up else "DOWN",
        "reachable": reachable_hosts,
        "total": total_hosts,
        "global_avg_latency": global_avg,
    }


def _get_sse_data():
    """Sync helper — runs in executor to avoid blocking event loop."""
    db = database.SessionLocal()
    try:
        hosts = db.query(models.HostDB).filter(models.HostDB.enabled == True).all()

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
                    "latency_threshold_ms": getattr(h, "latency_threshold_ms", None),
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
