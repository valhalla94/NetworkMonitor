import csv
import io
import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import case, func
from sqlalchemy.orm import Session

import auth
import models
import scheduler
from auth import get_current_user
from database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Hosts & Telemetry"])

_RANGE_LIMITS = {
    "-1h": 720,
    "-6h": 360,
    "-24h": 1440,
    "-7d": 2016,
    "-30d": 4320,
    "-1y": 8760,
    "-2y": 8760,
}


@router.post("/hosts/", response_model=models.Host)
def create_host(
    host: models.HostCreate,
    db: Session = Depends(get_db),
    current_user: auth.User = Depends(get_current_user),
):
    db_host = models.HostDB(**host.model_dump())
    db.add(db_host)
    db.commit()
    db.refresh(db_host)
    scheduler.update_jobs()
    return db_host


@router.get("/hosts/", response_model=list[models.Host])
def read_hosts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: auth.User = Depends(get_current_user),
):
    return db.query(models.HostDB).offset(skip).limit(limit).all()


@router.get("/hosts/{host_id}", response_model=models.Host)
def read_host(
    host_id: int,
    db: Session = Depends(get_db),
    current_user: auth.User = Depends(get_current_user),
):
    db_host = db.query(models.HostDB).filter(models.HostDB.id == host_id).first()
    if db_host is None:
        raise HTTPException(status_code=404, detail="Host not found")
    return db_host


@router.put("/hosts/{host_id}", response_model=models.Host)
def update_host(
    host_id: int,
    host: models.HostCreate,
    db: Session = Depends(get_db),
    current_user: auth.User = Depends(get_current_user),
):
    db_host = db.query(models.HostDB).filter(models.HostDB.id == host_id).first()
    if db_host is None:
        raise HTTPException(status_code=404, detail="Host not found")
    for field, value in host.model_dump().items():
        setattr(db_host, field, value)
    db.commit()
    db.refresh(db_host)
    scheduler.update_jobs()
    return db_host


@router.delete("/hosts/{host_id}")
def delete_host(
    host_id: int,
    db: Session = Depends(get_db),
    current_user: auth.User = Depends(get_current_user),
):
    db_host = db.query(models.HostDB).filter(models.HostDB.id == host_id).first()
    if db_host is None:
        raise HTTPException(status_code=404, detail="Host not found")
    db.delete(db_host)
    db.commit()
    scheduler.update_jobs()
    return {"ok": True}


@router.get("/metrics/{host_id}")
def get_metrics(
    host_id: int,
    range: str = "-1h",
    db: Session = Depends(get_db),
    current_user: auth.User = Depends(get_current_user),
):
    now = datetime.utcnow()
    range_map = {
        "-1h": timedelta(hours=1),
        "-6h": timedelta(hours=6),
        "-24h": timedelta(hours=24),
        "-7d": timedelta(days=7),
        "-30d": timedelta(days=30),
        "-1y": timedelta(days=365),
        "-2y": timedelta(days=730),
    }
    delta = range_map.get(range, timedelta(hours=1))
    cutoff = now - delta

    limit = _RANGE_LIMITS.get(range, 1440)
    results_db = (
        db.query(models.PingResultDB.timestamp, models.PingResultDB.latency)
        .filter(
            models.PingResultDB.host_id == host_id,
            models.PingResultDB.timestamp >= cutoff,
        )
        .order_by(models.PingResultDB.timestamp.asc())
        .limit(limit)
        .all()
    )

    results = []
    total_pings = 0
    successful_pings = 0
    total_latency = 0.0

    for timestamp, latency in results_db:
        total_pings += 1
        latency_val = latency if latency is not None else -1.0
        if latency_val >= 0:
            successful_pings += 1
            total_latency += latency_val
        results.append({"time": timestamp.isoformat() + "Z", "latency": latency_val})

    uptime = (successful_pings / total_pings * 100) if total_pings > 0 else 0
    avg_latency = (total_latency / successful_pings) if successful_pings > 0 else 0

    return {"data": results, "uptime": uptime, "avg_latency": avg_latency}


@router.get("/uptime/{host_id}")
def get_uptime_history(
    host_id: int,
    range: str = "-30d",
    db: Session = Depends(get_db),
    current_user: auth.User = Depends(get_current_user),
):
    """Daily uptime percentage for the given host."""
    now = datetime.utcnow()
    range_map = {
        "-7d": timedelta(days=7),
        "-30d": timedelta(days=30),
        "-90d": timedelta(days=90),
    }
    delta = range_map.get(range, timedelta(days=30))
    cutoff = now - delta

    results_db = (
        db.query(
            func.strftime("%Y-%m-%d", models.PingResultDB.timestamp).label("day_key"),
            func.count(models.PingResultDB.id).label("total"),
            func.sum(case((models.PingResultDB.latency >= 0, 1), else_=0)).label("up"),
        )
        .filter(
            models.PingResultDB.host_id == host_id,
            models.PingResultDB.timestamp >= cutoff,
        )
        .group_by("day_key")
        .order_by("day_key")
        .all()
    )

    daily = []
    for day_key, total, up in results_db:
        up_count = up if up is not None else 0
        pct = round((up_count / total * 100), 1) if total > 0 else 0.0
        daily.append({"date": day_key, "uptime": pct, "total": total, "up": up_count})

    return daily


@router.get("/export/metrics/{host_id}")
def export_metrics_csv(
    host_id: int,
    range: str = "-30d",
    db: Session = Depends(get_db),
    current_user: auth.User = Depends(get_current_user),
):
    now = datetime.utcnow()
    range_map = {
        "-1h": timedelta(hours=1),
        "-24h": timedelta(hours=24),
        "-7d": timedelta(days=7),
        "-30d": timedelta(days=30),
        "-1y": timedelta(days=365),
    }
    delta = range_map.get(range, timedelta(days=30))
    cutoff = now - delta

    # ⚡ Bolt: Use yield_per and generator to stream large CSV exports directly.
    # This prevents loading the entire dataset into memory for processing, significantly
    # reducing memory usage and O(n) processing overhead on the API server for large time ranges.
    query = (
        db.query(models.PingResultDB.timestamp, models.PingResultDB.latency)
        .filter(
            models.PingResultDB.host_id == host_id,
            models.PingResultDB.timestamp >= cutoff,
        )
        .order_by(models.PingResultDB.timestamp.asc())
    )

    def iter_csv():
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["timestamp", "latency_ms", "status"])

        # Yield the header immediately so empty datasets still return a valid CSV structure
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)

        # Buffer rows to avoid massive thread pool thrashing in StreamingResponse
        # with synchronous generators yielding line-by-line
        buffer_count = 0

        for timestamp, latency in query.yield_per(1000):
            writer.writerow(
                [
                    timestamp.isoformat(),
                    latency if latency is not None else "",
                    "UP" if latency is not None else "DOWN",
                ]
            )
            buffer_count += 1
            if buffer_count >= 1000:
                yield output.getvalue()
                output.seek(0)
                output.truncate(0)
                buffer_count = 0

        # Yield remaining rows
        if buffer_count > 0:
            yield output.getvalue()

    return StreamingResponse(
        iter_csv(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=metrics_host_{host_id}_{range}.csv"
        },
    )
