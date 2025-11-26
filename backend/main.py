from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import database
import models
import scheduler
from database import get_db, query_api, INFLUXDB_BUCKET, INFLUXDB_ORG

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

@app.on_event("startup")
def startup_event():
    scheduler.start_scheduler()

@app.post("/hosts/", response_model=models.Host)
def create_host(host: models.HostCreate, db: Session = Depends(get_db)):
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
def update_host(host_id: int, host: models.HostCreate, db: Session = Depends(get_db)):
    db_host = db.query(models.HostDB).filter(models.HostDB.id == host_id).first()
    if db_host is None:
        raise HTTPException(status_code=404, detail="Host not found")
    
    db_host.name = host.name
    db_host.ip_address = host.ip_address
    db_host.interval = host.interval
    db_host.enabled = host.enabled
    
    db.commit()
    db.refresh(db_host)
    scheduler.update_jobs()
    return db_host

@app.delete("/hosts/{host_id}")
def delete_host(host_id: int, db: Session = Depends(get_db)):
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
    query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
      |> range(start: {range})
      |> filter(fn: (r) => r["_measurement"] == "ping_result")
      |> filter(fn: (r) => r["host_id"] == "{host_id}")
      |> filter(fn: (r) => r["_field"] == "latency")
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
    
    for table in result:
        for record in table.records:
            total_hosts += 1
            if record.get_value() >= 0:
                reachable_hosts += 1
                
    if total_hosts == 0:
        return {"status": "UNKNOWN", "details": "No data"}
        
    is_up = (reachable_hosts / total_hosts) > 0.5
    return {
        "status": "UP" if is_up else "DOWN",
        "reachable": reachable_hosts,
        "total": total_hosts
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
