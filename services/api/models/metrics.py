from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, Any

from .base import Base

class Metric(Base):
    """Base metric model."""
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    metric_type = Column(String, nullable=False, index=True)
    value = Column(JSON)
    metadata = Column(JSON)

    __mapper_args__ = {
        "polymorphic_identity": "metric",
        "polymorphic_on": metric_type
    }

class ScreenshotMetric(Metric):
    """Screenshot metric model."""
    __tablename__ = "screenshot_metrics"

    id = Column(Integer, ForeignKey("metrics.id"), primary_key=True)
    file_path = Column(String, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    format = Column(String)
    compression_quality = Column(Integer)

    __mapper_args__ = {
        "polymorphic_identity": "screenshot"
    }

class NetworkMetric(Metric):
    """Network metric model."""
    __tablename__ = "network_metrics"

    id = Column(Integer, ForeignKey("metrics.id"), primary_key=True)
    connections = Column(JSON)  # List of connection info
    bytes_sent = Column(Integer)
    bytes_received = Column(Integer)
    packets_sent = Column(Integer)
    packets_received = Column(Integer)
    bandwidth_mbps = Column(Float)
    interface_data = Column(JSON)  # Network interface information

    __mapper_args__ = {
        "polymorphic_identity": "network"
    }

class ClipboardMetric(Metric):
    """Clipboard metric model."""
    __tablename__ = "clipboard_metrics"

    id = Column(Integer, ForeignKey("metrics.id"), primary_key=True)
    content_hash = Column(String, nullable=False, index=True)
    content_type = Column(String, nullable=False)
    content_length = Column(Integer, nullable=False)
    is_filtered = Column(Boolean, default=False)
    filter_matches = Column(JSON)  # List of filter matches
    filtered_content = Column(String)  # Stored only if content is filtered

    __mapper_args__ = {
        "polymorphic_identity": "clipboard"
    }

# Helper methods for metric creation
def create_screenshot_metric(
    file_path: str,
    width: int,
    height: int,
    file_size: int,
    format: str = "PNG",
    compression_quality: int = 85,
    metadata: Dict[str, Any] = None
) -> ScreenshotMetric:
    """Create a screenshot metric instance."""
    return ScreenshotMetric(
        file_path=file_path,
        width=width,
        height=height,
        file_size=file_size,
        format=format,
        compression_quality=compression_quality,
        metadata=metadata
    )

def create_network_metric(
    bytes_sent: int,
    bytes_received: int,
    packets_sent: int,
    packets_received: int,
    bandwidth_mbps: float,
    connections: list = None,
    interface_data: dict = None,
    metadata: Dict[str, Any] = None
) -> NetworkMetric:
    """Create a network metric instance."""
    return NetworkMetric(
        bytes_sent=bytes_sent,
        bytes_received=bytes_received,
        packets_sent=packets_sent,
        packets_received=packets_received,
        bandwidth_mbps=bandwidth_mbps,
        connections=connections,
        interface_data=interface_data,
        metadata=metadata
    )

def create_clipboard_metric(
    content_hash: str,
    content_type: str,
    content_length: int,
    is_filtered: bool = False,
    filter_matches: list = None,
    filtered_content: str = None,
    metadata: Dict[str, Any] = None
) -> ClipboardMetric:
    """Create a clipboard metric instance."""
    return ClipboardMetric(
        content_hash=content_hash,
        content_type=content_type,
        content_length=content_length,
        is_filtered=is_filtered,
        filter_matches=filter_matches,
        filtered_content=filtered_content,
        metadata=metadata
    ) 