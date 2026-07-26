import asyncio
import logging
import re

from fastapi import APIRouter, Depends, Request
from ping3 import ping
from pydantic import BaseModel, field_validator
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

import auth
import models
import scheduler
from auth import get_current_user
from database import get_db

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(tags=["Tools & Diagnostics"])


class QuickPingRequest(BaseModel):
    target: str

    @field_validator("target")
    @classmethod
    def validate_target(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9.\-_:\/]{1,253}$", v):
            raise ValueError("Invalid target: use IP address or hostname only")
        return v


@router.post("/tools/ping")
@limiter.limit("10/minute")
async def quick_ping(request: Request, body: QuickPingRequest):
    try:
        latency = await asyncio.to_thread(ping, body.target, unit="ms", timeout=2)
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


@router.get("/public-ip-history")
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


@router.post("/speedtest/run")
def run_speedtest_manual(current_user: auth.User = Depends(get_current_user)):
    scheduler.scheduler.add_job(scheduler.run_speedtest)
    return {"message": "Speed test started"}


@router.get("/speedtest/history", response_model=list[models.SpeedTestResultBase])
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


@router.get("/audit-log")
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

