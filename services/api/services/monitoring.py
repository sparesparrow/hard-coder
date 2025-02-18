from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.metrics import (
    create_metric_repository,
    MetricRepository,
    ScreenshotMetricRepository,
    NetworkMetricRepository,
    ClipboardMetricRepository
)
from ..models.metrics import (
    Metric,
    ScreenshotMetric,
    NetworkMetric,
    ClipboardMetric,
    create_screenshot_metric,
    create_network_metric,
    create_clipboard_metric
)

logger = logging.getLogger(__name__)

class MonitoringService:
    """Service for handling monitoring operations."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
        self._screenshot_repo = ScreenshotMetricRepository(session)
        self._network_repo = NetworkMetricRepository(session)
        self._clipboard_repo = ClipboardMetricRepository(session)
    
    async def create_metric(self, metric_type: str, data: Dict[str, Any]) -> Metric:
        """Create a new metric of the specified type."""
        try:
            if metric_type == "screenshot":
                metric = create_screenshot_metric(
                    file_path=data["file_path"],
                    width=data["width"],
                    height=data["height"],
                    file_size=data["file_size"],
                    format=data.get("format", "PNG"),
                    compression_quality=data.get("compression_quality", 85),
                    metadata=data.get("metadata")
                )
                return await self._screenshot_repo.create(metric)
                
            elif metric_type == "network":
                metric = create_network_metric(
                    bytes_sent=data["bytes_sent"],
                    bytes_received=data["bytes_received"],
                    packets_sent=data["packets_sent"],
                    packets_received=data["packets_received"],
                    bandwidth_mbps=data["bandwidth_mbps"],
                    connections=data.get("connections"),
                    interface_data=data.get("interface_data"),
                    metadata=data.get("metadata")
                )
                return await self._network_repo.create(metric)
                
            elif metric_type == "clipboard":
                metric = create_clipboard_metric(
                    content_hash=data["content_hash"],
                    content_type=data["content_type"],
                    content_length=data["content_length"],
                    is_filtered=data.get("is_filtered", False),
                    filter_matches=data.get("filter_matches"),
                    filtered_content=data.get("filtered_content"),
                    metadata=data.get("metadata")
                )
                return await self._clipboard_repo.create(metric)
                
            else:
                raise ValueError(f"Unknown metric type: {metric_type}")
                
        except Exception as e:
            logger.error(f"Error creating {metric_type} metric: {str(e)}")
            raise
    
    async def get_metrics(
        self,
        metric_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Metric]:
        """Get metrics with optional filtering."""
        try:
            if metric_type:
                repo = create_metric_repository(self._session, metric_type)
                return await repo.get_all(start_time, end_time, limit, offset)
            
            # If no specific type, get all types
            results = []
            for repo in [self._screenshot_repo, self._network_repo, self._clipboard_repo]:
                metrics = await repo.get_all(start_time, end_time, limit, offset)
                results.extend(metrics)
            
            # Sort combined results by timestamp
            results.sort(key=lambda x: x.timestamp, reverse=True)
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Error getting metrics: {str(e)}")
            raise
    
    async def cleanup_old_metrics(self, retention_hours: int = 24) -> Dict[str, int]:
        """Clean up metrics older than the specified retention period."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(hours=retention_hours)
            cleanup_results = {}
            
            # Clean up each metric type
            for metric_type, repo in [
                ("screenshot", self._screenshot_repo),
                ("network", self._network_repo),
                ("clipboard", self._clipboard_repo)
            ]:
                deleted_count = await repo.cleanup_old_metrics(cutoff_date)
                cleanup_results[metric_type] = deleted_count
                
            logger.info(f"Cleaned up old metrics: {cleanup_results}")
            return cleanup_results
            
        except Exception as e:
            logger.error(f"Error cleaning up old metrics: {str(e)}")
            raise
    
    # Screenshot-specific methods
    async def get_screenshots_by_dimensions(
        self,
        min_width: Optional[int] = None,
        min_height: Optional[int] = None,
        limit: int = 100
    ) -> List[ScreenshotMetric]:
        """Get screenshots filtered by dimensions."""
        try:
            return await self._screenshot_repo.get_by_dimensions(
                min_width,
                min_height,
                limit
            )
        except Exception as e:
            logger.error(f"Error getting screenshots by dimensions: {str(e)}")
            raise
    
    # Network-specific methods
    async def get_network_by_bandwidth(
        self,
        min_bandwidth: float,
        limit: int = 100
    ) -> List[NetworkMetric]:
        """Get network metrics filtered by minimum bandwidth."""
        try:
            return await self._network_repo.get_by_bandwidth(
                min_bandwidth,
                limit
            )
        except Exception as e:
            logger.error(f"Error getting network metrics by bandwidth: {str(e)}")
            raise
    
    # Clipboard-specific methods
    async def get_clipboard_by_content_type(
        self,
        content_type: str,
        limit: int = 100
    ) -> List[ClipboardMetric]:
        """Get clipboard metrics filtered by content type."""
        try:
            return await self._clipboard_repo.get_by_content_type(
                content_type,
                limit
            )
        except Exception as e:
            logger.error(f"Error getting clipboard metrics by content type: {str(e)}")
            raise
    
    async def get_filtered_clipboard_content(
        self,
        limit: int = 100
    ) -> List[ClipboardMetric]:
        """Get clipboard metrics that have been filtered."""
        try:
            return await self._clipboard_repo.get_filtered_content(limit)
        except Exception as e:
            logger.error(f"Error getting filtered clipboard content: {str(e)}")
            raise 