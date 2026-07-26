from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Index
from datetime import datetime
from pydantic import BaseModel
from database import Base


class HostDB(Base):
    __tablename__ = "hosts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    ip_address = Column(String, unique=True, index=True)
    interval = Column(Integer, default=60)
    enabled = Column(Boolean, default=True)
    average_latency = Column(Float, nullable=True)
    port = Column(Integer, nullable=True)
    monitor_type = Column(String, default="icmp")  # icmp, tcp, http, heartbeat
    ssl_monitor = Column(Boolean, default=False)
    expected_status_code = Column(Integer, default=200, nullable=True)
    group_name = Column(String, nullable=True, default="General")
    maintenance = Column(Boolean, default=False)
    last_status = Column(String, default="UNKNOWN")
    ssl_expiry_days = Column(Integer, nullable=True)
    ssl_error = Column(String, nullable=True)
    latency_threshold_ms = Column(Float, nullable=True)  # Alert if avg latency exceeds this
    heartbeat_slug = Column(String, nullable=True, unique=True, index=True)  # For heartbeat monitors
    heartbeat_interval = Column(Integer, nullable=True)  # Expected interval in seconds
    maintenance_start = Column(DateTime, nullable=True)  # Scheduled maintenance window start
    maintenance_end = Column(DateTime, nullable=True)    # Scheduled maintenance window end


class SettingsDB(Base):
    __tablename__ = "settings"

    key = Column(String, primary_key=True, index=True)
    value = Column(String)


class AuditLogDB(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    user = Column(String, default="admin")
    action = Column(String)  # LOGIN, CREATE_HOST, DELETE_HOST, etc.
    target = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    details = Column(String, nullable=True)


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
    latency_threshold_ms: float | None = None
    heartbeat_slug: str | None = None
    heartbeat_interval: int | None = None
    maintenance_start: datetime | None = None
    maintenance_end: datetime | None = None


class HostCreate(HostBase):
    pass


class Host(HostBase):
    id: int

    class Config:
        from_attributes = True


class PingResult(BaseModel):
    host_id: int
    latency: float | None
    timestamp: str


class PingResultDB(Base):
    __tablename__ = "ping_results"

    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(Integer, ForeignKey("hosts.id"), index=True)
    latency = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # ⚡ Bolt: Added composite index on (host_id, timestamp)
    # This prevents full table scans when filtering metrics by host and ordering by time.
    # Impact: Reduces query time significantly for `/metrics` and `/uptime` endpoints on large datasets.
    __table_args__ = (
        Index("ix_ping_results_host_id_timestamp", "host_id", "timestamp"),
    )


class PublicIPHistoryDB(Base):
    __tablename__ = "public_ip_history"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class SpeedTestResultDB(Base):
    __tablename__ = "speedtest_results"

    id = Column(Integer, primary_key=True, index=True)
    download = Column(Float)
    upload = Column(Float)
    ping = Column(Float)
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
