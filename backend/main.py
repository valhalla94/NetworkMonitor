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
from database import get_db, query_api, INFLUXDB_BUCKET, INFLUXDB_ORG
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
def get_metrics(host_id: int, range: str = "-1h"):
    """
    Get metrics for a specific host.
    range: Flux duration string (e.g., -1h, -24h, -7d)
    """
    
    # Determine aggregation window based on range
    window = "1m" # Default
    if range == "-6h":
        window = "5m"
    elif range == "-24h":
        window = "10m"
    elif range == "-7d":
        window = "1h"
    elif range == "-30d":
        window = "4h"
    elif range == "-1y":
        window = "1d"
    elif range == "-2y":
        window = "1d"
        
    # If range is small (-1h), we might not need aggregation, or use a very small one.
    # But for consistency and to prevent over-fetching, we can stick to a small window or raw data.
    # For -1h, raw data is usually fine (60*60/30 = 120 points).
    
    aggregate_logic = ""
    if range != "-1h":
        aggregate_logic = f'|> aggregateWindow(every: {window}, fn: mean, createEmpty: false)'

    query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
      |> range(start: {range})
      |> filter(fn: (r) => r["_measurement"] == "ping_result")
      |> filter(fn: (r) => r["host_id"] == "{host_id}")
      |> filter(fn: (r) => r["_field"] == "latency")
      {aggregate_logic}
      |> yield(name: "mean")
    '''
    result = query_api.query(org=INFLUXDB_ORG, query=query)
    results = []
    total_pings = 0
    successful_pings = 0
    total_latency = 0.0
    
    for table in result:
        for record in table.records:
            val = record.get_value()
            total_pings += 1
            if val >= 0:
                successful_pings += 1
                total_latency += val
            
            results.append({
                "time": record.get_time(),
                "latency": val
            })
            
    # Note: Uptime calculation on aggregated data is an approximation.
    # Ideally, we should calculate uptime on raw data or use a separate query.
    # For now, this approximation is acceptable for the dashboard view.
    uptime = (successful_pings / total_pings * 100) if total_pings > 0 else 0
    avg_latency = (total_latency / successful_pings) if successful_pings > 0 else 0
    
    return {
        "data": results,
        "uptime": uptime,
        "avg_latency": avg_latency
    }

@app.get("/status")
def get_network_status():
    """
    Returns the overall network status.
    If > 50% of enabled hosts are reachable in the last 5 minutes, network is UP.
    """
    # Query last 5 minutes for all hosts
    query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
      |> range(start: -5m)
      |> filter(fn: (r) => r["_measurement"] == "ping_result")
      |> filter(fn: (r) => r["_field"] == "latency")
      |> last()
    '''
    result = query_api.query(org=INFLUXDB_ORG, query=query)
    
    total_hosts = 0
    reachable_hosts = 0
    total_latency = 0.0
    latency_count = 0
    
    for table in result:
        for record in table.records:
            total_hosts += 1
            val = record.get_value()
            if val >= 0:
                reachable_hosts += 1
                total_latency += val
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
def get_public_ip_history():
    """
    Get the history of public IP addresses for the last 2 years.
    """
    query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
      |> range(start: -2y)
      |> filter(fn: (r) => r["_measurement"] == "public_ip_history")
      |> filter(fn: (r) => r["_field"] == "ip_address")
      |> sort(columns: ["_time"], desc: true)
    '''
    result = query_api.query(org=INFLUXDB_ORG, query=query)
    
    history = []
    for table in result:
        for record in table.records:
            history.append({
                "time": record.get_time(),
                "ip_address": record.get_value()
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
def get_speedtest_history():
    """
    Get the history of speed test results for the last 30 days.
    """
    query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
      |> range(start: -30d)
      |> filter(fn: (r) => r["_measurement"] == "speedtest_result")
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
      |> sort(columns: ["_time"], desc: true)
    '''
    result = query_api.query(org=INFLUXDB_ORG, query=query)
    
    history = []
    for table in result:
        for record in table.records:
            history.append({
                "timestamp": record.get_time().isoformat(),
                "download": record.values.get("download", 0),
                "upload": record.values.get("upload", 0),
                "ping": record.values.get("ping", 0)
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
