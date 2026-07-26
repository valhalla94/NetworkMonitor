import logging
import os
import secrets
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

import auth
import models
from auth import get_current_user
from database import get_db
from notifications import notification_manager

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(tags=["Authentication & Settings"])

# Hash admin password once at startup
_admin_password_raw = os.getenv("ADMIN_PASSWORD")
if not _admin_password_raw:
    _admin_password_raw = secrets.token_urlsafe(16)
    logger.warning(
        f"⚠️  ADMIN_PASSWORD not set! Generated random admin password: {_admin_password_raw}\n"
        "Please set the ADMIN_PASSWORD environment variable before production use."
    )
elif _admin_password_raw in ("admin", "password", "123456", "test"):
    logger.warning("⚠️  ADMIN_PASSWORD is too weak. Use a strong password.")

ADMIN_PASSWORD_HASH = auth.get_password_hash(_admin_password_raw)


@router.post("/token", response_model=auth.Token)
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


@router.get("/settings")
def get_settings(
    db: Session = Depends(get_db), current_user: auth.User = Depends(get_current_user)
):
    settings = db.query(models.SettingsDB).all()
    return {s.key: s.value for s in settings}


@router.post("/settings/notifications")
def update_notification_settings(
    setting: models.SettingsBase,
    db: Session = Depends(get_db),
    current_user: auth.User = Depends(get_current_user),
):
    db_setting = (
        db.query(models.SettingsDB)
        .filter(models.SettingsDB.key == setting.key)
        .first()
    )
    if db_setting:
        db_setting.value = setting.value
    else:
        db_setting = models.SettingsDB(key=setting.key, value=setting.value)
        db.add(db_setting)
    db.commit()
    notification_manager.load_config(db)
    notification_manager.send_notification("Test Notification", "Configuration updated successfully!")
    return {"ok": True}
