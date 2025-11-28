from sqlalchemy import Column, Integer, String, Boolean, Float
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

# Pydantic Models
class HostBase(BaseModel):
    name: str
    ip_address: str
    interval: int = 60
    enabled: bool = True
    average_latency: float | None = None
    port: int | None = None

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

class SpeedTestResultDB(Base):
    __tablename__ = "speedtest_results"

    id = Column(Integer, primary_key=True, index=True)
    download = Column(Float) # Mbps
    upload = Column(Float) # Mbps
    ping = Column(Float) # ms
    timestamp = Column(String)

class SpeedTestResultBase(BaseModel):
    download: float
    upload: float
    ping: float
    timestamp: str

class SpeedTestResult(SpeedTestResultBase):
    id: int

    class Config:
        from_attributes = True
