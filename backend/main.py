from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
import database
import models
import scheduler
import auth
import os
from ping3 import ping
from pydantic import BaseModel
from database import get_db
import notifications

from notifications import notification_manager

# Create tables
database.migrate_db()
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Network Monitor API")


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, specify the frontend URL
    allow_credentials=True,
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
    user = auth.User(username=token_data.username)
    return user

@app.post("/token", response_model=auth.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Simple hardcoded admin check for now, can be expanded to DB
    admin_password = os.getenv("ADMIN_PASSWORD", "admin")
    
    # In a real app we would check username too, but here we just check password for "admin"
    if form_data.username != "admin" or not auth.verify_password(form_data.password, auth.get_password_hash(admin_password)):
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
    # Initialize notification manager with DB
    db = database.SessionLocal()
    try:
        notification_manager.load_config(db)
    finally:
        db.close()

@app.post("/hosts/", response_model=models.Host)
def create_host(host: models.HostCreate, db: Session = Depends(get_db), current_user: auth.User = Depends(get_current_user)):
    db_host = models.HostDB(**host.dict())
    db.add(db_host)
    db.commit()
    db.refresh(db_host)
    scheduler.update_jobs()
    return db_host

@app.get("/hosts/", response_model=List[models.Host])
def read_hosts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    hosts = db.query(models.HostDB).offset(skip).limit(limit).all()
    return hosts

@app.get("/hosts/{host_id}", response_model=models.Host)
def read_host(host_id: int, db: Session = Depends(get_db)):
    db_host = db.query(models.HostDB).filter(models.HostDB.id == host_id).first()
    if db_host is None:
        raise HTTPException(status_code=404, detail="Host not found")
    return db_host

@app.put("/hosts/{host_id}", response_model=models.Host)
def update_host(host_id: int, host: models.HostCreate, db: Session = Depends(get_db), current_user: auth.User = Depends(get_current_user)):
    db_host = db.query(models.HostDB).filter(models.HostDB.id == host_id).first()
    if db_host is None:
        raise HTTPException(status_code=404, detail="Host not found")
    
    db_host.name = host.name
    db_host.ip_address = host.ip_address
    db_host.interval = host.interval
    db_host.enabled = host.enabled
    db_host.port = host.port
    
    db.commit()
    db.refresh(db_host)
    scheduler.update_jobs()
    return db_host

@app.delete("/hosts/{host_id}")
def delete_host(host_id: int, db: Session = Depends(get_db), current_user: auth.User = Depends(get_current_user)):
    db_host = db.query(models.HostDB).filter(models.HostDB.id == host_id).first()
    if db_host is None:
        raise HTTPException(status_code=404, detail="Host not found")
    db.delete(db_host)
    db.commit()
    scheduler.update_jobs()
    return {"ok": True}

@app.get("/metrics/{host_id}")
def get_metrics(host_id: int, range: str = "-1h", db: Session = Depends(get_db)):
    """
    Get metrics for a specific host.
    range: Duration string (e.g., -1h, -24h, -7d)
    """
    
    # Calculate cutoff time
    from datetime import datetime
    now = datetime.utcnow()
    
    if range == "-1h":
        cutoff = now - timedelta(hours=1)
    elif range == "-6h":
        cutoff = now - timedelta(hours=6)
    elif range == "-24h":
        cutoff = now - timedelta(hours=24)
    elif range == "-7d":
        cutoff = now - timedelta(days=7)
    elif range == "-30d":
        cutoff = now - timedelta(days=30)
    elif range == "-1y":
        cutoff = now - timedelta(days=365)
    else:
        cutoff = now - timedelta(hours=1) # Default
        
    # Query SQLite
    # Optimize: For long ranges, we might want to sample. 
    # For now, we return raw data but maybe limit query if it's too huge.
    results_db = db.query(models.PingResultDB).filter(
        models.PingResultDB.host_id == host_id,
        models.PingResultDB.timestamp >= cutoff
    ).order_by(models.PingResultDB.timestamp.asc()).all()
    
    results = []
    total_pings = 0
    successful_pings = 0
    total_latency = 0.0
    
    for record in results_db:
        total_pings += 1
        val = record.latency
        
        # In DB, latency is None for timeout. In frontend/influx logic, timeout might be -1 or handled differently.
        # Frontend expects positive value for chart, or maybe -1 for down?
        # Let's standardize: If None, send -1 (so chart shows gap or 0 line depending on frontend).
        # But wait, logic says "if val >= 0: successful".
        
        latency_val = val if val is not None else -1.0
        
        if latency_val >= 0:
            successful_pings += 1
            total_latency += latency_val
        
        results.append({
            "time": record.timestamp.isoformat() + "Z", # Add Z for UTC
            "latency": latency_val
        })
            
    uptime = (successful_pings / total_pings * 100) if total_pings > 0 else 0
    avg_latency = (total_latency / successful_pings) if successful_pings > 0 else 0
    
    return {
        "data": results,
        "uptime": uptime,
        "avg_latency": avg_latency
    }

@app.get("/status")
def get_network_status(db: Session = Depends(get_db)):
    """
    Returns the overall network status.
    If > 50% of enabled hosts are reachable in the last 5 minutes, network is UP.
    """
    # Get all enabled hosts
    hosts = db.query(models.HostDB).filter(models.HostDB.enabled == True).all()
    
    from datetime import datetime
    cutoff = datetime.utcnow() - timedelta(minutes=5)
    
    total_hosts = 0
    reachable_hosts = 0
    total_latency = 0.0
    latency_count = 0
    
    for host in hosts:
        total_hosts += 1
        # Get last ping result
        last_ping = db.query(models.PingResultDB).filter(
            models.PingResultDB.host_id == host.id,
            models.PingResultDB.timestamp >= cutoff
        ).order_by(models.PingResultDB.timestamp.desc()).first()
        
        if last_ping and last_ping.latency is not None:
             # It responded
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
        "global_avg_latency": global_avg
    }

@app.get("/public-ip-history")
def get_public_ip_history(db: Session = Depends(get_db)):
    """
    Get the history of public IP addresses for the last 2 years.
    """
    history_db = db.query(models.PublicIPHistoryDB).order_by(models.PublicIPHistoryDB.timestamp.desc()).limit(100).all()
    
    history = []
    for record in history_db:
        history.append({
            "time": record.timestamp.isoformat() + "Z",
            "ip_address": record.ip_address
        })
            
            
    return history

@app.post("/speedtest/run")
def run_speedtest_manual():
    """
    Manually trigger a speed test.
    """
    scheduler.scheduler.add_job(scheduler.run_speedtest)
    return {"message": "Speed test started"}

@app.get("/speedtest/history", response_model=List[models.SpeedTestResultBase])
def get_speedtest_history(db: Session = Depends(get_db)):
    """
    Get the history of speed test results for the last 30 days.
    """
    # Limit to last 50 results to prevent overloaded UI
    results = db.query(models.SpeedTestResultDB).order_by(models.SpeedTestResultDB.timestamp.desc()).limit(50).all()
    
    history = []
    for record in results:
        history.append({
            "timestamp": record.timestamp.isoformat() + "Z",
            "download": record.download,
            "upload": record.upload,
            "ping": record.ping
        })
            
    return history

class QuickPingRequest(BaseModel):
    target: str

@app.post("/tools/ping")
def quick_ping(request: QuickPingRequest):
    """
    Pings a specific host/IP once and returns the latency.
    """
    try:
        latency = ping(request.target, unit='ms', timeout=2)
        if latency is None:
            return {"target": request.target, "reachable": False, "latency": None, "error": "Timeout"}
        return {"target": request.target, "reachable": True, "latency": latency}
    except Exception as e:
        return {"target": request.target, "reachable": False, "latency": None, "error": str(e)}

@app.get("/settings", response_model=List[models.Settings])
def get_settings(db: Session = Depends(get_db), current_user: auth.User = Depends(get_current_user)):
    return db.query(models.SettingsDB).all()

@app.post("/settings/notifications")
def update_notification_settings(settings: models.SettingsBase, db: Session = Depends(get_db), current_user: auth.User = Depends(get_current_user)):
    db_setting = db.query(models.SettingsDB).filter(models.SettingsDB.key == "notification_url").first()
    if not db_setting:
        db_setting = models.SettingsDB(key="notification_url", value=settings.value)
        db.add(db_setting)
    else:
        db_setting.value = settings.value
    
    db.commit()
    
    # Reload config
    notification_manager.load_config(db)
    
    # Test notification
    notification_manager.send_notification("NetworkMonitor", "Notification configuration updated successfully.")
    
    return {"message": "Settings updated"}
