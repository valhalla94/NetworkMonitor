from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey
from datetime import datetime
from pydantic import BaseModel
from database import Base

# SQLAlchemy Model
class HostDB(Base):
    __tablename__ = "hosts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    ip_address = Column(String, unique=True, index=True)
    interval = Column(Integer, default=60) # Ping interval in seconds
    enabled = Column(Boolean, default=True)
    average_latency = Column(Float, nullable=True)
    port = Column(Integer, nullable=True)
    monitor_type = Column(String, default="icmp") # icmp, tcp, http
    ssl_monitor = Column(Boolean, default=False)
    expected_status_code = Column(Integer, default=200, nullable=True)
    group_name = Column(String, nullable=True, default="General")
    maintenance = Column(Boolean, default=False)
    last_status = Column(String, default="UNKNOWN") # UP, DOWN, UNKNOWN
    ssl_expiry_days = Column(Integer, nullable=True)
    ssl_error = Column(String, nullable=True)

class SettingsDB(Base):
    __tablename__ = "settings"

    key = Column(String, primary_key=True, index=True)
    value = Column(String)

# Pydantic Models
class HostBase(BaseModel):
    name: str
    ip_address: str
    interval: int = 60
    enabled: bool = True
    average_latency: float | None = None
    port: int | None = None
    monitor_type: str = "icmp"
    ssl_monitor: bool = False
    expected_status_code: int | None = 200
    group_name: str | None = "General"
    maintenance: bool = False
    last_status: str | None = "UNKNOWN"
    ssl_expiry_days: int | None = None
    ssl_error: str | None = None

class HostCreate(HostBase):
    pass

class Host(HostBase):
    id: int

    class Config:
        from_attributes = True

class PingResult(BaseModel):
    host_id: int
    latency: float | None # None if timeout
    timestamp: str

class PingResultDB(Base):
    __tablename__ = "ping_results"

    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(Integer, ForeignKey("hosts.id"), index=True)
    latency = Column(Float, nullable=True) # Null for timeout
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class PublicIPHistoryDB(Base):
    __tablename__ = "public_ip_history"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class SpeedTestResultDB(Base):
    __tablename__ = "speedtest_results"

    id = Column(Integer, primary_key=True, index=True)
    download = Column(Float) # Mbps
    upload = Column(Float) # Mbps
    ping = Column(Float) # ms
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    server_id = Column(Integer, nullable=True)
    server_name = Column(String, nullable=True)
    server_country = Column(String, nullable=True)

class SpeedTestResultBase(BaseModel):
    download: float
    upload: float
    ping: float
    timestamp: str

class SpeedTestResult(SpeedTestResultBase):
    id: int

    class Config:
        from_attributes = True

class SettingsBase(BaseModel):
    key: str
    value: str

class Settings(SettingsBase):
    class Config:
        from_attributes = True
