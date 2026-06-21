import os
import re
import json
import asyncio
import logging
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta, datetime
import database
import models
import scheduler
import auth
from ping3 import ping
from pydantic import BaseModel, validator
from database import get_db
import notifications
from notifications import notification_manager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

logger = logging.getLogger(__name__)

# Hash admin password once at startup (bcrypt is slow — avoid rehashing per-request)
_admin_password_raw = os.getenv("ADMIN_PASSWORD")
if not _admin_password_raw:
    logger.warning(
        "⚠️  ADMIN_PASSWORD not set! Using default 'admin'. Set it before production use."
    )
    _admin_password_raw = "admin"
elif _admin_password_raw in ("admin", "password", "123456", "test"):
    logger.warning("⚠️  ADMIN_PASSWORD is too weak. Use a strong password.")
ADMIN_PASSWORD_HASH = auth.get_password_hash(_admin_password_raw)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# DB init
database.migrate_db()
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Network Monitor API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"
        return response


app.add_middleware(SecurityHeadersMiddleware)

# CORS — no credentials needed (Bearer token in Authorization header, not cookies)
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN] if FRONTEND_ORIGIN != "*" else ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = auth.decode_access_token(token)
    if token_data is None:
        raise credentials_exception
    return auth.User(username=token_data.username)


@app.post("/token", response_model=auth.Token)
@limiter.limit("5/minute")
async def login_for_access_token(
    request: Request, form_data: OAuth2PasswordRequestForm = Depends()
):
    if form_data.username != "admin" or not auth.verify_password(
        form_data.password, ADMIN_PASSWORD_HASH
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.on_event("startup")
def startup_event():
    scheduler.start_scheduler()
    db = database.SessionLocal()
    try:
        notification_manager.load_config(db)
    finally:
        db.close()


@app.post("/hosts/", response_model=models.Host)
def create_host(
    host: models.HostCreate,
    db: Session = Depends(get_db),
    current_user: auth.User = Depends(get_current_user),
):
    db_host = models.HostDB(**host.dict())
    db.add(db_host)
    db.commit()
    db.refresh(db_host)
    scheduler.update_jobs()
    return db_host


@app.get("/hosts/", response_model=List[models.Host])
def read_hosts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.HostDB).offset(skip).limit(limit).all()


@app.get("/hosts/{host_id}", response_model=models.Host)
def read_host(host_id: int, db: Session = Depends(get_db)):
    db_host = db.query(models.HostDB).filter(models.HostDB.id == host_id).first()
    if db_host is None:
        raise HTTPException(status_code=404, detail="Host not found")
    return db_host


@app.put("/hosts/{host_id}", response_model=models.Host)
def update_host(
    host_id: int,
    host: models.HostCreate,
    db: Session = Depends(get_db),
    current_user: auth.User = Depends(get_current_user),
):
    db_host = db.query(models.HostDB).filter(models.HostDB.id == host_id).first()
    if db_host is None:
        raise HTTPException(status_code=404, detail="Host not found")
    for field, value in host.dict().items():
        setattr(db_host, field, value)
    db.commit()
    db.refresh(db_host)
    scheduler.update_jobs()
    return db_host


@app.delete("/hosts/{host_id}")
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


# Range → max data points for downsampling
_RANGE_LIMITS = {
    "-1h": 720,
    "-6h": 360,
    "-24h": 1440,
    "-7d": 2016,
    "-30d": 4320,
    "-1y": 8760,
    "-2y": 8760,
}


@app.get("/metrics/{host_id}")
def get_metrics(host_id: int, range: str = "-1h", db: Session = Depends(get_db)):
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
        db.query(models.PingResultDB)
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

    for record in results_db:
        total_pings += 1
        latency_val = record.latency if record.latency is not None else -1.0
        if latency_val >= 0:
            successful_pings += 1
            total_latency += latency_val
        results.append(
            {"time": record.timestamp.isoformat() + "Z", "latency": latency_val}
        )

    uptime = (successful_pings / total_pings * 100) if total_pings > 0 else 0
    avg_latency = (total_latency / successful_pings) if successful_pings > 0 else 0

    return {"data": results, "uptime": uptime, "avg_latency": avg_latency}


@app.get("/uptime/{host_id}")
def get_uptime_history(
    host_id: int, range: str = "-30d", db: Session = Depends(get_db)
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
        db.query(models.PingResultDB)
        .filter(
            models.PingResultDB.host_id == host_id,
            models.PingResultDB.timestamp >= cutoff,
        )
        .order_by(models.PingResultDB.timestamp.asc())
        .all()
    )

    # Group by day
    daily: dict = {}
    for record in results_db:
        day_key = record.timestamp.strftime("%Y-%m-%d")
        if day_key not in daily:
            daily[day_key] = {"total": 0, "up": 0}
        daily[day_key]["total"] += 1
        if record.latency is not None and record.latency >= 0:
            daily[day_key]["up"] += 1

    return [
        {
            "date": day,
            "uptime": round(v["up"] / v["total"] * 100, 2) if v["total"] > 0 else 0,
        }
        for day, v in sorted(daily.items())
    ]


@app.get("/status")
def get_network_status(db: Session = Depends(get_db)):
    hosts = db.query(models.HostDB).filter(models.HostDB.enabled == True).all()
    cutoff = datetime.utcnow() - timedelta(minutes=5)

    host_ids = [h.id for h in hosts]

    if host_ids:
        recent_pings = (
            db.query(models.PingResultDB)
            .filter(
                models.PingResultDB.host_id.in_(host_ids),
                models.PingResultDB.timestamp >= cutoff,
            )
            .order_by(models.PingResultDB.timestamp.desc())
            .all()
        )
    else:
        recent_pings = []

    latest_pings = {}
    for p in recent_pings:
        if p.host_id not in latest_pings:
            latest_pings[p.host_id] = p

    total_hosts = 0
    reachable_hosts = 0
    total_latency = 0.0
    latency_count = 0

    for host in hosts:
        total_hosts += 1
        last_ping = latest_pings.get(host.id)
        if last_ping and last_ping.latency is not None:
            reachable_hosts += 1
            total_latency += last_ping.latency
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


@app.get("/public-ip-history")
def get_public_ip_history(db: Session = Depends(get_db)):
    history_db = (
        db.query(models.PublicIPHistoryDB)
        .order_by(models.PublicIPHistoryDB.timestamp.desc())
        .limit(100)
        .all()
    )
    return [
        {"time": r.timestamp.isoformat() + "Z", "ip_address": r.ip_address}
        for r in history_db
    ]


@app.post("/speedtest/run")
def run_speedtest_manual(current_user: auth.User = Depends(get_current_user)):
    scheduler.scheduler.add_job(scheduler.run_speedtest)
    return {"message": "Speed test started"}


@app.get("/speedtest/history", response_model=List[models.SpeedTestResultBase])
def get_speedtest_history(db: Session = Depends(get_db)):
    results = (
        db.query(models.SpeedTestResultDB)
        .order_by(models.SpeedTestResultDB.timestamp.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "timestamp": r.timestamp.isoformat() + "Z",
            "download": r.download,
            "upload": r.upload,
            "ping": r.ping,
        }
        for r in results
    ]


class QuickPingRequest(BaseModel):
    target: str

    @validator("target")
    def validate_target(cls, v):
        if not re.match(r"^[a-zA-Z0-9.\-_:\/]{1,253}$", v):
            raise ValueError("Invalid target: use IP address or hostname only")
        return v


@app.post("/tools/ping")
@limiter.limit("10/minute")
async def quick_ping(request: Request, body: QuickPingRequest):
    try:
        latency = ping(body.target, unit="ms", timeout=2)
        if latency is None:
            return {
                "target": body.target,
                "reachable": False,
                "latency": None,
                "error": "Timeout",
            }
        return {"target": body.target, "reachable": True, "latency": latency}
    except Exception as e:
        return {
            "target": body.target,
            "reachable": False,
            "latency": None,
            "error": str(e),
        }


@app.get("/settings", response_model=List[models.Settings])
def get_settings(
    db: Session = Depends(get_db), current_user: auth.User = Depends(get_current_user)
):
    return db.query(models.SettingsDB).all()


@app.post("/settings/notifications")
def update_notification_settings(
    settings: models.SettingsBase,
    db: Session = Depends(get_db),
    current_user: auth.User = Depends(get_current_user),
):
    db_setting = (
        db.query(models.SettingsDB)
        .filter(models.SettingsDB.key == "notification_url")
        .first()
    )
    if not db_setting:
        db_setting = models.SettingsDB(key="notification_url", value=settings.value)
        db.add(db_setting)
    else:
        db_setting.value = settings.value
    db.commit()
    notification_manager.load_config(db)
    notification_manager.send_notification(
        "NetworkMonitor", "Notification configuration updated successfully."
    )
    return {"message": "Settings updated"}


# SSE — real-time host status stream
from sse_starlette.sse import EventSourceResponse


def _get_sse_data():
    """Sync helper — runs in executor to avoid blocking event loop."""
    db = database.SessionLocal()
    try:
        hosts = db.query(models.HostDB).filter(models.HostDB.enabled == True).all()
        cutoff = datetime.utcnow() - timedelta(minutes=5)

        host_ids = [h.id for h in hosts]
        if host_ids:
            recent_pings = (
                db.query(models.PingResultDB)
                .filter(
                    models.PingResultDB.host_id.in_(host_ids),
                    models.PingResultDB.timestamp >= cutoff,
                )
                .order_by(models.PingResultDB.timestamp.desc())
                .all()
            )
        else:
            recent_pings = []

        latest_pings = {}
        for p in recent_pings:
            if p.host_id not in latest_pings:
                latest_pings[p.host_id] = p

        host_list = []
        for h in hosts:
            last_ping = latest_pings.get(h.id)
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


@app.get("/events")
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


# Heartbeat endpoint — for push-based monitors (cron jobs, scripts, services)
@app.post("/heartbeat/{slug}")
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


# CSV export
import csv
import io
from fastapi.responses import StreamingResponse


@app.get("/export/metrics/{host_id}")
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

    results = (
        db.query(models.PingResultDB)
        .filter(
            models.PingResultDB.host_id == host_id,
            models.PingResultDB.timestamp >= cutoff,
        )
        .order_by(models.PingResultDB.timestamp.asc())
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["timestamp", "latency_ms", "status"])
    for r in results:
        writer.writerow(
            [
                r.timestamp.isoformat(),
                r.latency if r.latency is not None else "",
                "UP" if r.latency is not None else "DOWN",
            ]
        )

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=metrics_host_{host_id}_{range}.csv"
        },
    )


# Audit log
@app.get("/audit-log")
def get_audit_log(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: auth.User = Depends(get_current_user),
):
    logs = (
        db.query(models.AuditLogDB)
        .order_by(models.AuditLogDB.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": log.id,
            "user": log.user,
            "action": log.action,
            "target": log.target,
            "timestamp": log.timestamp.isoformat() + "Z",
            "details": log.details,
        }
        for log in logs
    ]


def _audit(db: Session, user: str, action: str, target: str, details: str = ""):
    log = models.AuditLogDB(user=user, action=action, target=target, details=details)
    db.add(log)
    db.commit()
